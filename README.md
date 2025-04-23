## EHenatai Gallery

> 本项目使用 Fastapi+Vue3 前后端分离的方式运行

### 环境准备

#### 后端安装

API 默认端口：8000

```bash
uv sync
cd backend
uvicorn main:app --reload
```
#### 前端安装

UI 默认端口：5173

```bash
cd frontend
pnpm i
pnpm run dev
```

### 使用方式

运行前请在 `backend` 目录下创建 `config.toml` 文件用于记录 cookie，格式如下：

```toml
[cookies]
ipb_member_id = 
ipb_pass_hash = "xxx"
```