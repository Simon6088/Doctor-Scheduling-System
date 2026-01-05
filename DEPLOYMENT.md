# 部署指南 (Deployment Guide)

本项目分为三部分：后端 (Python/FastAPI)、Web 管理端 (Vue3)、移动端 (UniApp/H5)。
为了实现 "部署到 Supabase" 的目标，推荐采用以下现代云架构：

1.  **数据库 (Database)**: 使用 **Supabase** (PostgreSQL)。
2.  **后端服务 (Backend)**: 由于 Supabase 原生不托管 Python 容器，推荐部署到 **Render**, **Railway** 或 **Fly.io** (均支持 Docker 且有免费/廉价层，可直连 Supabase)。
3.  **前端服务 (Web & Mobile H5)**: 部署到 **Vercel** 或 **Netlify**。

---

## 1. 数据库配置 (Supabase)

1.  登录 [Supabase](https://supabase.com) 并创建一个新项目。
2.  获取 **Database URL** (Connection String):
    *   Settings -> Database -> Connection string -> URI.
    *   格式: `postgresql://postgres:[PASSWORD]@db.[REF].supabase.co:5432/postgres`
    postgresql://postgres:f3vI2Th583n5usPF@db.chfdfarbajbwncourwzk.supabase.co:5432/postgres

## 2. 后端部署 (Render 示例)

1.  将代码推送到 GitHub。
2.  在 [Render](https://render.com) 创建 **Web Service**。
3.  连接你的 GitHub 仓库。
4.  **Runtime**: 选择 `Docker` (我们已创建 `backend/Dockerfile`)。
    *   **Root Directory**: `backend` (重要！)。
5.  **Environment Variables**:
    *   `DATABASE_URL`: 填入 Supabase 的连接字符串 (注意替换 [PASSWORD])。
    *   `SECRET_KEY`: 生成一个随机密钥。
    *   `ALGORITHM`: `HS256`.
    *   `ACCESS_TOKEN_EXPIRE_MINUTES`: `30`.
6.  Deploy。

## 3. 前端部署 (Vercel 示例)

### Web 管理端 (`frontend-admin`)
1.  在 Vercel 导入仓库。
2.  **Root Directory**: `frontend-admin`.
3.  **Framework Preset**: Vite.
4.  **Environment Variables**:
    *   `VITE_API_BASE_URL`: 填入部署好的后端 URL (例如 `https://your-backend.onrender.com`).
5.  Deploy.

### 移动端 H5 (`mobile-app`)
1.  在 Vercel 导入仓库 (或添加新Project)。
2.  **Root Directory**: `mobile-app`.
3.  **Build Command**: `npm run build:h5`.
4.  **Output Directory**: `dist/build/h5`.
5.  **Environment Variables**:
    *   `VITE_API_BASE_URL`: 同上 (注意: UniApp 需要在代码中读取环境变变量，可能需要修改 request.js 适配 Vercel env 注入方式，通常使用 `import.meta.env`).
6.  Deploy.

## 4. 常见问题 (Troubleshooting)

### 无法连接数据库 (Network is unreachable / IPv6)
如果 Render 报错 `psycopg2.OperationalError ... Network is unreachable` (且显示 IPv6 地址)，这是因为 Supabase 直连地址 (`db.xxx.supabase.co`) 解析到了 IPv6，而 Render 容器网络对此支持不佳。

**解决方法**: 改用 Supabase **Connection Pooler (IPv4)** 地址。
1.  进入 Supabase Dashboard -> **Settings** -> **Database**.
2.  找到 **Connection Pooling** (或直接看 Connection String -> URI -> 把 Port 改为 **6543**，或者勾选 "Use connection pooling")。
3.  通常 Connection String 格式类似: `postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres?pgbouncer=true`.
    *   关键是 **Port 6543** 和域名 (可能是 pooler 域名或原域名但走 Pooler)。
4.  更新 Render 的 `DATABASE_URL` 环境变量为这个新地址。

---

## 特别说明
*   **迁移**: 部署后，后端的 `models.Base.metadata.create_all` 会自动在 Supabase 数据库创建表结构。
*   **数据**: 这是一个新数据库，初始为空。你可能需要重新创建管理员账号或导入数据。
