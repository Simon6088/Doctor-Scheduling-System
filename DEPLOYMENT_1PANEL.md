# 1Panel 部署指南 (ECS Lightweight Server)

本项目已适配 Docker Compose 部署，适合在 1Panel 或任何支持 Docker 的 Linux 服务器上运行。

## 1. 准备工作

1.  **上传代码**: 将整个 `Doctor-Scheduling-System` 文件夹上传到服务器（例如 `/opt/doctor-scheduling`），或者在服务器上 `git clone`。
2.  **端口开放**: 在火山引擎 ECS 实例的安全组中，开放以下端口（TCP）:
    *   `8000`: 后端 API
    *   `8001`: 管理后台 Web
    *   `8002`: 移动端 H5

## 2. 1Panel 部署步骤

### 方式一：使用“应用编排” (推荐)

1.  登录 1Panel 面板。
2.  进入 **容器** -> **编排** -> **创建编排**。
3.  **名称**: `doctor-scheduling`
4.  **路径**: 选择上传代码的目录 (例如 `/opt/doctor-scheduling`)。
5.  **内容**: 1Panel 会自动读取该目录下的 `docker-compose.yml`。如果没读取，请手动复制 `docker-compose.yml` 的内容粘贴进去。
6.  点击 **确定/创建**。
    *   系统会自动拉取镜像并构建 (`npm install` 和 `npm run build` 会在构建过程中执行，可能需要几分钟，请耐心等待)。

### 方式二：命令行部署

1.  SSH 登录服务器。
2.  进入项目目录: `cd /opt/doctor-scheduling`
3.  运行: `docker-compose up -d --build`

## 3. 验证部署

部署完成后，通过浏览器访问：

*   **管理后台**: `http://<服务器IP>:8001/`
    *   账号: `admin` / `admin123` (首次运行需自行创建或导入数据，因为是新数据库)
*   **移动端**: `http://<服务器IP>:8002/`
*   **后端 API**: `http://<服务器IP>:8000/docs`

## 4. 关于数据与本地共存

*   **本地开发**: 您依然可以在本地 Windows 电脑上运行 `.\run_backend.ps1` 和 `npm run dev`。本地默认使用 `db.sqlite3` (SQLite) 数据库，数据保存在本地文件。
*   **线上环境**: Docker 部署默认使用 **PostgreSQL** 数据库 (在 `docker-compose.yml` 中定义)，数据保存在 Docker Volume (`db_data`) 中，**两者数据不互通**。
*   **数据持久化**: 如果删除容器，Postgres 数据会保留在 Volume 中；如果删除 Volume，数据将丢失。建议定期备份。

## 5. 故障排查

*   **构建失败**: 检查服务器内存是否足够（构建 Node 项目需要较多内存）。
*   **API 404**: 检查 Nginx 配置 (`frontend-admin/nginx.conf`) 是否正确反向代理了 `/api/`。
