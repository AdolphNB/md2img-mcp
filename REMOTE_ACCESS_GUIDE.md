# MCP服务远程访问配置指南

## 🌐 概述

本指南将帮你配置word2img-mcp服务，使其可以通过URL远程访问。

## 🚀 快速配置

### 1. 启动服务监听所有接口

```bash
# 启动HTTP服务器，监听所有网络接口
cd /root/word2img-mcp
uv run python start_http_server.py --host 0.0.0.0 --port 8000
```

### 2. 检查服务状态

```bash
# 本地测试
curl http://localhost:8000/health

# 如果有公网IP，测试外部访问（替换为你的实际IP）
curl http://YOUR_PUBLIC_IP:8000/health
```

## 🔧 详细配置步骤

### 步骤1：配置防火墙

#### Ubuntu/Debian系统：
```bash
# 安装ufw（如果未安装）
sudo apt update
sudo apt install ufw

# 允许8000端口
sudo ufw allow 8000/tcp

# 启用防火墙
sudo ufw enable

# 检查状态
sudo ufw status
```

#### CentOS/RHEL系统：
```bash
# 允许8000端口
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload

# 检查状态
sudo firewall-cmd --list-ports
```

### 步骤2：配置云服务器安全组

如果你使用的是云服务器（阿里云、腾讯云、AWS等），需要在控制台配置安全组：

#### 阿里云ECS：
1. 登录阿里云控制台
2. 进入ECS实例管理
3. 点击"安全组" → "配置规则"
4. 添加入方向规则：
   - 端口范围：8000/8000
   - 授权对象：0.0.0.0/0（或指定IP段）
   - 协议：TCP

#### 腾讯云CVM：
1. 登录腾讯云控制台
2. 进入云服务器管理
3. 点击"安全组" → "编辑规则"
4. 添加入站规则：
   - 类型：自定义TCP
   - 端口：8000
   - 源：0.0.0.0/0

### 步骤3：获取访问URL

```bash
# 获取公网IP
curl ifconfig.me

# 或者使用
curl ipinfo.io/ip
```

你的MCP服务URL将是：`http://YOUR_PUBLIC_IP:8000`

## 🔒 安全配置（推荐）

### 1. 添加基础认证

创建一个带认证的版本：

```python
# 创建 secure_http_server.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

app = FastAPI()
security = HTTPBasic()

# 配置用户名和密码
USERNAME = "admin"
PASSWORD = "your_secure_password_here"

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    is_correct_username = secrets.compare_digest(credentials.username, USERNAME)
    is_correct_password = secrets.compare_digest(credentials.password, PASSWORD)
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# 在需要认证的端点上添加依赖
@app.post("/mcp")
async def mcp_endpoint(request: Request, username: str = Depends(authenticate)):
    # 原有的MCP处理逻辑
    pass
```

### 2. 使用HTTPS（生产环境推荐）

#### 获取SSL证书

```bash
# 安装certbot
sudo apt install certbot

# 获取证书（需要域名）
sudo certbot certonly --standalone -d your-domain.com
```

#### 配置HTTPS启动

```python
# 修改启动命令
def run_http_server(host: str = "0.0.0.0", port: int = 8000, 
                   ssl_keyfile: str = None, ssl_certfile: str = None):
    uvicorn.run(
        app,
        host=host,
        port=port,
        ssl_keyfile=ssl_keyfile,
        ssl_certfile=ssl_certfile
    )

# 启动HTTPS服务
run_http_server(
    ssl_keyfile="/etc/letsencrypt/live/your-domain.com/privkey.pem",
    ssl_certfile="/etc/letsencrypt/live/your-domain.com/fullchain.pem"
)
```

## 🌍 域名配置（可选）

### 1. 购买域名并配置DNS

在域名管理面板中添加A记录：
- 主机记录：`mcp`（或`@`用于根域名）
- 记录类型：`A`
- 记录值：你的服务器公网IP

### 2. 使用Nginx反向代理

```nginx
# /etc/nginx/sites-available/word2img-mcp
server {
    listen 80;
    server_name mcp.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /sse {
        proxy_pass http://127.0.0.1:8000/sse;
        proxy_set_header Host $host;
        proxy_set_header Cache-Control no-cache;
        proxy_buffering off;
        proxy_read_timeout 24h;
    }
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/word2img-mcp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 📱 客户端配置

### 1. 更新客户端URL

修改客户端代码中的URL：

```python
# 原来的本地URL
# client = MCPHTTPClient("http://localhost:8000")

# 更改为远程URL
client = MCPHTTPClient("http://YOUR_PUBLIC_IP:8000")

# 或使用域名
client = MCPHTTPClient("http://mcp.your-domain.com")
```

### 2. 测试远程连接

```python
import asyncio
import aiohttp

async def test_remote_connection():
    url = "http://YOUR_PUBLIC_IP:8000/health"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                data = await response.json()
                print(f"✅ 远程连接成功: {data}")
        except Exception as e:
            print(f"❌ 远程连接失败: {e}")

asyncio.run(test_remote_connection())
```

## 🐳 Docker部署（推荐）

### 1. 创建Dockerfile

```dockerfile
FROM python:3.13-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . .

# 安装Python依赖
RUN pip install uv && uv sync

# 创建输出目录
RUN mkdir -p outputs

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uv", "run", "python", "start_http_server.py", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. 构建和运行

```bash
# 构建镜像
docker build -t word2img-mcp .

# 运行容器
docker run -d \
  --name word2img-mcp \
  -p 8000:8000 \
  -v $(pwd)/outputs:/app/outputs \
  word2img-mcp

# 检查状态
docker logs word2img-mcp
```

### 3. 使用docker-compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  word2img-mcp:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./outputs:/app/outputs
    environment:
      - LOG_LEVEL=info
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - word2img-mcp
    restart: unless-stopped
```

启动：
```bash
docker-compose up -d
```

## 🔍 监控和维护

### 1. 服务监控

```bash
# 检查服务状态
curl -f http://YOUR_PUBLIC_IP:8000/health || echo "Service is down"

# 查看日志
tail -f /var/log/word2img-mcp.log
```

### 2. 性能监控

```python
# 添加到http_server.py
import psutil
import time

@app.get("/metrics")
async def metrics():
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage('/').percent,
        "uptime": time.time() - start_time
    }
```

### 3. 自动重启脚本

```bash
#!/bin/bash
# restart_service.sh

SERVICE_URL="http://localhost:8000/health"
LOG_FILE="/var/log/word2img-mcp-monitor.log"

while true; do
    if ! curl -f $SERVICE_URL > /dev/null 2>&1; then
        echo "$(date): Service is down, restarting..." >> $LOG_FILE
        pkill -f "start_http_server.py"
        sleep 5
        cd /root/word2img-mcp
        nohup uv run python start_http_server.py --host 0.0.0.0 --port 8000 > /dev/null 2>&1 &
    fi
    sleep 60
done
```

## 🎯 使用示例

### 远程API调用

```bash
# 健康检查
curl http://YOUR_PUBLIC_IP:8000/health

# 生成图片
curl -X POST http://YOUR_PUBLIC_IP:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "id": 1,
    "params": {
      "name": "submit_markdown",
      "arguments": {
        "markdown_text": "# 远程测试\n\n这是通过远程API生成的图片！\n\n- ✅ 网络连接正常\n- ✅ 服务运行正常\n- ✅ 图片生成成功",
        "background_color": "#1e3a8a",
        "text_color": "#ffffff"
      }
    }
  }'
```

### JavaScript客户端

```javascript
// 远程调用示例
const MCP_URL = 'http://YOUR_PUBLIC_IP:8000/mcp';

async function generateImage(markdownText) {
    const response = await fetch(MCP_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            jsonrpc: '2.0',
            method: 'tools/call',
            id: 1,
            params: {
                name: 'submit_markdown',
                arguments: {
                    markdown_text: markdownText,
                    background_color: '#1e3a8a',
                    text_color: '#ffffff'
                }
            }
        })
    });
    
    return await response.json();
}
```

## ⚠️ 注意事项

1. **安全性**: 
   - 生产环境请使用HTTPS
   - 添加认证机制
   - 限制访问来源IP

2. **性能**:
   - 监控服务器资源使用
   - 设置合理的并发限制
   - 定期清理生成的图片文件

3. **稳定性**:
   - 使用进程管理器（如systemd）
   - 配置自动重启
   - 设置日志轮转

4. **网络**:
   - 确保网络稳定
   - 配置CDN加速（如需要）
   - 设置合理的超时时间

现在你可以通过URL远程访问你的MCP服务了！🎉
