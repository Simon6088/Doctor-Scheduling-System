# 医院排班系统 (Doctor Scheduling System)

这是一个基于 FastAPI (后端) + Vue 3 (管理后台) + UniApp (移动端 H5) 的医院排班系统。

## 功能特性

- **排班管理**: 自动生成排班、手动调整、班次管理
- **人员管理**: 医生、科室、诊室管理
- **换班申请**: 医生发起换班，管理员审批
- **移动端**: 医生查看个人排班、发起换班

## 项目结构

- `backend/`: Python FastAPI 后端
- `frontend-admin/`: Vue 3 + Element Plus 管理后台
- `mobile-app/`: UniApp 移动端 H5

## 快速开始

### 1. 启动后端

```bash
cd backend
./run_backend.ps1
```

后端服务地址: http://127.0.0.1:8000
API 文档: http://127.0.0.1:8000/docs

### 2. 启动管理后台

```bash
cd frontend-admin
npm run dev
```

管理后台地址: http://localhost:5173
管理员账号: admin / admin123

### 3. 启动移动端

```bash
cd mobile-app
npm run dev:h5
```

移动端地址: http://localhost:5175
测试账号: R001 / 123456

## 详细文档

- [PRD.md](PRD.md): 产品需求文档
- [USER_GUIDE.md](USER_GUIDE.md): 用户使用指南
