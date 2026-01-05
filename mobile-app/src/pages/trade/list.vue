<template>
  <view class="container">
    <view class="tabs">
      <view 
        class="tab" 
        :class="{ active: activeTab === 'incoming' }" 
        @click="activeTab = 'incoming'"
      >
        收到的请求 ({{ incomingTrades.length }})
      </view>
      <view 
        class="tab" 
        :class="{ active: activeTab === 'outgoing' }" 
        @click="activeTab = 'outgoing'"
      >
        发出的请求 ({{ outgoingTrades.length }})
      </view>
    </view>

    <view class="trade-list">
      <!-- 收到的请求 -->
      <view v-if="activeTab === 'incoming'">
        <view v-if="incomingTrades.length === 0" class="empty">
          <text>暂无收到的换班请求</text>
        </view>
        <view v-for="trade in incomingTrades" :key="trade.id" class="trade-item incoming">
          <view class="trade-header">
            <text class="requester">{{ trade.requester_name }}</text>
            <text class="status" :class="'status-' + trade.status">{{ getStatusText(trade.status) }}</text>
          </view>
          <view class="trade-info">
            <text>排班日期: {{ trade.shift_date }}</text>
            <text>班次: {{ trade.shift_name }}</text>
          </view>
          <view v-if="trade.reason" class="trade-reason">
            <text>原因: {{ trade.reason }}</text>
          </view>
      <view v-if="trade.status === 'pending'" class="trade-actions">
            <button class="btn-accept" @click="respondTrade(trade.id, 'accept')">接受</button>
            <button class="btn-reject" @click="respondTrade(trade.id, 'reject')">拒绝</button>
          </view>
        </view>
      </view>

      <!-- 发出的请求 -->
      <view v-if="activeTab === 'outgoing'">
        <view v-if="outgoingTrades.length === 0" class="empty">
          <text>暂无发出的换班请求</text>
        </view>
        <view v-for="trade in outgoingTrades" :key="trade.id" class="trade-item outgoing">
          <view class="trade-header">
            <text class="target">发给: {{ trade.target_name }}</text>
            <text class="status" :class="'status-' + trade.status">{{ getStatusText(trade.status) }}</text>
          </view>
          <view class="trade-info">
            <text>排班日期: {{ trade.shift_date }}</text>
            <text>班次: {{ trade.shift_name }}</text>
          </view>
          <view v-if="trade.reason" class="trade-reason">
            <text>原因: {{ trade.reason }}</text>
          </view>
        </view>
      </view>
    </view>
    <FeedbackBtn />
  </view>
</template>

<script>
import { request } from '../../utils/request';
import FeedbackBtn from '../../components/FeedbackBtn.vue';

export default {
  components: { FeedbackBtn },
  data() {
    return {
      activeTab: 'incoming',
      incomingTrades: [],
      outgoingTrades: []
    }
  },
  onShow() {
    this.fetchTrades();
  },
  methods: {
    async fetchTrades() {
      try {
        console.log('开始获取换班请求...');
        
        // 获取收到的请求
        const incoming = await request({ url: '/trades/incoming' });
        console.log('收到的请求原始数据:', incoming);
        this.incomingTrades = await this.enrichTradeData(incoming);
        console.log('收到的请求处理后:', this.incomingTrades);

        // 获取发出的请求
        const outgoing = await request({ url: '/trades/outgoing' });
        console.log('发出的请求原始数据:', outgoing);
        this.outgoingTrades = await this.enrichTradeData(outgoing);
        console.log('发出的请求处理后:', this.outgoingTrades);
        
      } catch (e) {
        console.error('获取换班请求失败:', e);
        uni.showToast({ title: '获取换班请求失败', icon: 'none' });
      }
    },
    async enrichTradeData(trades) {
      console.log('开始丰富换班数据，数量:', trades.length);
      
      // 获取用户和排班信息
      const users = await request({ url: '/users/' });
      console.log('获取到用户数量:', users.length);
      
      const schedules = await request({ url: '/schedules/' });
      console.log('获取到排班数量:', schedules.length);
      
      const shiftTypes = await request({ url: '/shift-types/' });
      console.log('获取到班次类型数量:', shiftTypes.length);
      
      return trades.map(trade => {
        const requester = users.find(u => u.id === trade.requester_id);
        const target = users.find(u => u.id === trade.target_doctor_id);
        const schedule = schedules.find(s => s.id === trade.request_shift_id);
        const shiftType = schedule ? shiftTypes.find(st => st.id === schedule.shift_type_id) : null;
        
        console.log(`处理换班 ID ${trade.id}:`, {
          requester: requester?.full_name,
          target: target?.full_name,
          schedule: schedule?.date,
          shiftType: shiftType?.name
        });
        
        return {
          ...trade,
          requester_name: requester?.full_name || '未知',
          target_name: target?.full_name || '未知',
          shift_date: schedule?.date || '未知',
          shift_name: shiftType?.name || '未知班次'
        };
      });
    },
    getStatusText(status) {
      const texts = {
        'pending': '待处理',
        'accepted': '已同意 (待批准)',
        'approved': '已完成',
        'rejected': '已拒绝'
      };
      return texts[status] || status;
    },
    async respondTrade(tradeId, actionInput) {
      // Map frontend 'approved'/'rejected' to backend 'accept'/'reject'
      const actionMap = {
        'approved': 'accept',
        'rejected': 'reject',
        'accept': 'accept',
        'reject': 'reject'
      };
      const apiAction = actionMap[actionInput] || actionInput;

      try {
        await uni.showModal({
          title: '确认操作',
          content: `确定要${apiAction === 'accept' ? '接受' : '拒绝'}这个换班请求吗？`
        });
      } catch {
        return; // 用户取消
      }

      try {
        await request({
          url: `/trades/${tradeId}/respond`,
          method: 'PUT',
          data: { action: apiAction }
        });
        
        uni.showToast({ 
          title: apiAction === 'accept' ? '已接受换班' : '已拒绝换班', 
          icon: 'success' 
        });
        
        this.fetchTrades();
      } catch (e) {
        console.error('响应换班请求失败:', e);
        uni.showToast({ title: '操作失败，请重试', icon: 'none' });
      }
    }
  }
}
</script>

<style>
.container {
  min-height: 100vh;
  background-color: #f5f5f5;
}
.tabs {
  display: flex;
  background-color: white;
  border-bottom: 1px solid #eee;
}
.tab {
  flex: 1;
  text-align: center;
  padding: 15px;
  font-size: 14px;
  color: #666;
}
.tab.active {
  color: #007aff;
  border-bottom: 2px solid #007aff;
  font-weight: bold;
}
.trade-list {
  padding: 10px;
}
.empty {
  text-align: center;
  padding: 40px;
  color: #999;
}
.trade-item {
  background-color: white;
  border-radius: 8px;
  padding: 15px;
  margin-bottom: 10px;
  border-left: 4px solid #007aff;
}
.trade-item.outgoing {
  border-left-color: #28a745;
}
.trade-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.requester, .target {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}
.status {
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
}
.status-pending {
  background-color: #fff3cd;
  color: #856404;
}
.status-approved {
  background-color: #d4edda;
  color: #155724;
}
.status-rejected {
  background-color: #f8d7da;
  color: #721c24;
}
.trade-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-bottom: 10px;
}
.trade-info text {
  font-size: 14px;
  color: #666;
}
.trade-reason {
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
  margin-bottom: 10px;
}
.trade-reason text {
  font-size: 13px;
  color: #666;
}
.trade-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}
.btn-accept, .btn-reject {
  flex: 1;
  padding: 8px;
  font-size: 14px;
}
.btn-accept {
  background-color: #28a745;
  color: white;
}
.btn-reject {
  background-color: #dc3545;
  color: white;
}
</style>
