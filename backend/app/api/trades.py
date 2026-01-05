from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, models
from .deps import get_db, get_current_user, get_current_admin_user
from .audit import log_action

router = APIRouter()

@router.get("/trades/", response_model=List[schemas.TradeResponse])
def get_all_trades(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    """获取所有换班请求 - 仅管理员"""
    return db.query(models.ShiftTrade).all()

@router.post("/trades/", response_model=schemas.TradeResponse)
def create_trade(
    trade: schemas.TradeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verify ownership of shift
    shift = db.query(models.Schedule).filter(models.Schedule.id == trade.request_shift_id).first()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    if shift.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only trade your own shifts")
        
    new_trade = models.ShiftTrade(
        requester_id=current_user.id,
        request_shift_id=trade.request_shift_id,
        target_doctor_id=trade.target_doctor_id,
        reason=trade.reason
    )
    db.add(new_trade)
    
    # Notify Target Doctor
    notif = models.Notification(
        user_id=trade.target_doctor_id,
        content=f"您收到来自 {current_user.full_name} 的换班请求",
        type=models.NotificationType.TRADE_REQUEST
    )
    db.add(notif)
    
    db.commit()
    db.refresh(new_trade)
    return new_trade

@router.get("/trades/incoming", response_model=List[schemas.TradeResponse])
def get_incoming_trades(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.ShiftTrade).filter(
        models.ShiftTrade.target_doctor_id == current_user.id,
        models.ShiftTrade.status == models.TradeStatus.PENDING
    ).all()

@router.get("/trades/outgoing", response_model=List[schemas.TradeResponse])
def get_outgoing_trades(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return db.query(models.ShiftTrade).filter(
        models.ShiftTrade.requester_id == current_user.id
    ).all()

@router.put("/trades/{trade_id}/respond", response_model=schemas.TradeResponse)
def respond_to_trade(
    trade_id: int,
    response: schemas.TradeRespond,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    trade = db.query(models.ShiftTrade).filter(models.ShiftTrade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade request not found")
        
    if trade.target_doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to respond to this trade")
        
    if trade.status != models.TradeStatus.PENDING:
        raise HTTPException(status_code=400, detail="Trade is not pending")
        
    action = response.action
    if action == "accept":
        trade.status = models.TradeStatus.ACCEPTED
        # Notify Requester
        requester = db.query(models.User).get(trade.requester_id)
        notif = models.Notification(
            user_id=trade.requester_id,
            content=f"{current_user.full_name} 已同意您的换班请求，等待管理员审批",
            type=models.NotificationType.TRADE_RESULT
        )
        db.add(notif)
    elif action == "reject":
        trade.status = models.TradeStatus.REJECTED
        # Notify Requester
        notif = models.Notification(
            user_id=trade.requester_id,
            content=f"{current_user.full_name} 拒绝了您的换班请求",
            type=models.NotificationType.TRADE_RESULT
        )
        db.add(notif)
    else:
        raise HTTPException(status_code=400, detail="Invalid action")
        
    db.commit()
    db.refresh(trade)
    return trade
    
@router.post("/trades/{trade_id}/approve", response_model=schemas.TradeResponse)
def admin_approve_trade(
    trade_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_admin_user)
):
    """管理员批准换班并执行"""
    trade = db.query(models.ShiftTrade).filter(models.ShiftTrade.id == trade_id).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade request not found")
    
    if trade.status != models.TradeStatus.ACCEPTED:
        raise HTTPException(status_code=400, detail="Trade must be accepted by target doctor first")
        
    # 执行换班 (Swap / Transfer)
    schedule = db.query(models.Schedule).filter(models.Schedule.id == trade.request_shift_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Referenced schedule not found")
        
    # 将排班的医生改为目标医生
    schedule.doctor_id = trade.target_doctor_id
    
    trade.status = models.TradeStatus.APPROVED
    
    # Notify Both
    target = db.query(models.User).get(trade.target_doctor_id)
    requester = db.query(models.User).get(trade.requester_id)
    
    notif1 = models.Notification(
        user_id=trade.requester_id,
        content=f"您与 {target.full_name} 的换班请求已获管理员批准",
        type=models.NotificationType.TRADE_RESULT
    )
    notif2 = models.Notification(
        user_id=trade.target_doctor_id,
        content=f"您与 {requester.full_name} 的换班请求已获管理员批准",
        type=models.NotificationType.TRADE_RESULT
    )
    db.add(notif1)
    db.add(notif2)
    
    db.commit()
    db.refresh(trade)
    
    log_action(db, current_user.id, "APPROVE", "trade", str(trade.id), f"Approved trade {trade.id} between {requester.full_name} and {target.full_name}")
    
    return trade
