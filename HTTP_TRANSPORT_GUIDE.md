# word2img-mcp HTTP传输方式使用指南

## 概述

本指南介绍如何使用word2img-mcp服务的HTTP传输方式，这是对原有stdio传输方式的扩展。

## MCP支持的传输方式

MCP（Model Context Protocol）协议支持以下几种传输方式：

1. **Stdio（标准输入输出）** - 原有方式，适用于本地进程间通信
2. **SSE（服务器发送事件）** - 基于HTTP的单向数据传输
3. **Streamable HTTP** - 新的HTTP双向通信方式，支持无状态连接

## HTTP传输方式的优势

- **网络友好**: 可以通过网络访问MCP服务
- **标准HTTP**: 使用标准HTTP协议，易于集成
- **状态检查**: 提供健康检查和状态查询端点
- **流式支持**: 支持SSE进行实时数据推送
- **调试友好**: 可以使用标准HTTP工具进行调试

## 安装依赖

使用uv安装新增的依赖：

```bash
uv sync
```

新增的依赖包括：
- `fastapi>=0.104.0` - Web框架
- `uvicorn[standard]>=0.24.0` - ASGI服务器
- `aiohttp>=3.9.0` - HTTP客户端库

## 启动HTTP服务器

### 方式1：使用新的启动脚本

```bash
# 启动HTTP模式（默认）
python start_http_server.py

# 指定端口和主机
python start_http_server.py --host 0.0.0.0 --port 8080

# 设置日志级别
python start_http_server.py --log-level debug

# 仍然使用stdio模式
python start_http_server.py --stdio
```

### 方式2：直接运行HTTP服务器

```bash
python http_server.py
```

## 服务器端点

HTTP服务器提供以下端点：

### 主要端点

- `POST /mcp` - 主要的MCP JSON-RPC端点
- `GET /health` - 健康检查
- `GET /tools` - 获取工具列表（便捷端点）
- `GET /sse` - SSE流式连接端点
- `GET /` - 服务器信息

### 使用示例

#### 1. 检查服务器状态

```bash
curl http://localhost:8000/health
```

响应：
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "server_initialized": true
}
```

#### 2. 获取工具列表

```bash
curl http://localhost:8000/tools
```

#### 3. MCP JSON-RPC调用

```bash
# 初始化连接
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "initialize",
    "id": 1,
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {"tools": {}},
      "clientInfo": {"name": "test-client", "version": "1.0.0"}
    }
  }'

# 获取工具列表
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "id": 2
  }'
```

## 客户端使用

### Python客户端示例

运行提供的客户端示例：

```bash
python http_client_example.py
```

该示例演示了：
1. 连接健康检查
2. MCP连接初始化
3. 获取工具列表
4. 调用submit_markdown工具
5. 获取生成的图片

### 自定义客户端

```python
import aiohttp
import json

async def call_mcp_tool():
    async with aiohttp.ClientSession() as session:
        # 初始化
        init_data = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "id": 1,
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "my-client", "version": "1.0.0"}
            }
        }
        
        async with session.post("http://localhost:8000/mcp", json=init_data) as resp:
            init_result = await resp.json()
        
        # 调用工具
        tool_data = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "id": 2,
            "params": {
                "name": "submit_markdown",
                "arguments": {
                    "markdown_text": "# Hello World\n\nThis is a test.",
                    "width": 800,
                    "height": 1067
                }
            }
        }
        
        async with session.post("http://localhost:8000/mcp", json=tool_data) as resp:
            tool_result = await resp.json()
            return tool_result
```

## SSE流式连接

服务器支持SSE（Server-Sent Events）用于实时通信：

```bash
curl -N http://localhost:8000/sse
```

或在JavaScript中：

```javascript
const eventSource = new EventSource('http://localhost:8000/sse');

eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('收到事件:', data);
};
```

## 配置选项

### 服务器配置

可以通过命令行参数配置服务器：

- `--host`: 监听主机（默认：0.0.0.0）
- `--port`: 监听端口（默认：8000）
- `--log-level`: 日志级别（debug/info/warning/error）

### 环境变量

可以通过环境变量配置：

```bash
export MCP_HTTP_HOST=0.0.0.0
export MCP_HTTP_PORT=8000
export MCP_LOG_LEVEL=info
```

## 与stdio方式的对比

| 特性 | Stdio | HTTP |
|------|-------|------|
| 本地通信 | ✅ | ✅ |
| 网络通信 | ❌ | ✅ |
| 调试工具 | 有限 | 丰富 |
| 状态检查 | ❌ | ✅ |
| 流式支持 | 基础 | 高级(SSE) |
| 集成难度 | 中等 | 简单 |
| 性能 | 高 | 中等 |

## 故障排除

### 常见问题

1. **端口被占用**
   ```bash
   # 检查端口占用
   lsof -i :8000
   
   # 使用不同端口
   python start_http_server.py --port 8001
   ```

2. **依赖缺失**
   ```bash
   # 重新安装依赖
   uv sync
   ```

3. **连接超时**
   - 检查防火墙设置
   - 确认服务器正在运行
   - 验证网络连接

### 调试技巧

1. **启用调试日志**
   ```bash
   python start_http_server.py --log-level debug
   ```

2. **使用curl测试**
   ```bash
   # 测试健康检查
   curl -v http://localhost:8000/health
   ```

3. **查看服务器日志**
   HTTP服务器会输出详细的请求日志

## 生产部署

### 使用反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    location /sse {
        proxy_pass http://localhost:8000/sse;
        proxy_set_header Host $host;
        proxy_set_header Cache-Control no-cache;
        proxy_buffering off;
    }
}
```

### Docker部署

```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY . .

RUN pip install uv && uv sync

EXPOSE 8000

CMD ["python", "start_http_server.py", "--host", "0.0.0.0"]
```

## 总结

HTTP传输方式为word2img-mcp提供了更灵活的部署和集成选项，同时保持了与原有stdio方式的兼容性。选择合适的传输方式取决于你的具体使用场景和需求。
