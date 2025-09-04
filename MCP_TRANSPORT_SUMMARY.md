# MCP 通信方式总结

## 📡 MCP支持的通信方式

Model Context Protocol (MCP) 协议支持以下几种传输方式：

### 1. Stdio（标准输入输出）
- **原理**: 通过进程的标准输入和输出进行通信
- **适用场景**: 本地进程间通信，如Claude Desktop集成
- **优点**: 性能高，延迟低，实现简单
- **缺点**: 仅限本地通信，不支持网络访问

### 2. SSE（服务器发送事件）
- **原理**: 基于HTTP的单向数据传输，服务器主动推送数据
- **适用场景**: 实时数据更新，如日志流、状态监控
- **优点**: 实时性好，基于标准HTTP
- **缺点**: 单向通信，需要配合其他方式实现双向

### 3. Streamable HTTP（流式HTTP）
- **原理**: 使用单一HTTP端点进行双向通信，可选升级到SSE
- **适用场景**: 网络服务，API集成，微服务架构
- **优点**: 网络友好，标准HTTP协议，易于调试和集成
- **缺点**: 网络延迟，相比stdio性能略低

## 🔄 你的改造成果

### 原始配置（Stdio方式）
```python
# word2img_mcp/mcp_app.py
from mcp.server.stdio import stdio_server

async def run_server():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())
```

### 新增配置（HTTP方式）
```python
# http_server.py  
from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    # 处理MCP JSON-RPC请求
    return await handler.handle_request(request_data)
```

## 📊 两种方式对比

| 特性 | Stdio模式 | HTTP模式 |
|------|-----------|----------|
| **通信方式** | 进程间通信 | HTTP网络通信 |
| **网络支持** | ❌ 仅本地 | ✅ 支持远程 |
| **性能** | 🚀 高性能 | ⚡ 中等性能 |
| **调试难度** | 🔧 中等 | 🛠️ 简单 |
| **集成难度** | 📚 需要MCP客户端 | 🌐 标准HTTP API |
| **实时性** | ✅ 极佳 | ✅ 良好 |
| **扩展性** | ❌ 有限 | ✅ 易扩展 |
| **监控** | ❌ 困难 | ✅ 容易 |

## 🎯 使用建议

### 选择Stdio模式，如果你：
- 主要在Claude Desktop中使用
- 需要最佳性能
- 只需要本地通信
- 已有MCP客户端集成

### 选择HTTP模式，如果你：
- 需要网络访问服务
- 要集成到Web应用
- 需要多客户端访问
- 希望使用标准API调试工具
- 计划构建分布式系统

## 🛠️ 实现细节

### Stdio模式启动
```bash
# 使用原始方式
python start_mcp_server.py

# 或使用新脚本的stdio选项
python start_http_server.py --stdio
```

### HTTP模式启动
```bash
# 默认配置（localhost:8000）
python start_http_server.py

# 自定义配置
python start_http_server.py --host 0.0.0.0 --port 8080 --log-level debug
```

## 🔧 技术实现

### HTTP服务器架构
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   HTTP Client   │───▶│   FastAPI App    │───▶│   MCP Server    │
│                 │    │                  │    │                 │
│ - curl          │    │ - /mcp (JSON-RPC)│    │ - Tools Handler │
│ - Browser       │    │ - /health        │    │ - Image Store   │
│ - Python Client │    │ - /tools         │    │ - Renderer      │
│ - JavaScript    │    │ - /sse           │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### 请求流程
```
1. Client ──[HTTP POST]──▶ FastAPI (/mcp)
2. FastAPI ──[Parse JSON-RPC]──▶ MCPHTTPHandler  
3. MCPHTTPHandler ──[Route Method]──▶ MCP Server
4. MCP Server ──[Execute Tool]──▶ Tool Handler
5. Tool Handler ──[Generate Image]──▶ Renderer
6. Renderer ──[Return Result]──▶ Client
```

## 📈 扩展可能性

### 当前实现的端点
- `POST /mcp` - 主要MCP JSON-RPC端点
- `GET /health` - 健康检查
- `GET /tools` - 工具列表
- `GET /sse` - SSE流式连接
- `GET /` - 服务器信息

### 未来可扩展的功能
- 🔐 **认证授权**: JWT token验证
- 📊 **监控指标**: Prometheus metrics
- 🗄️ **数据持久化**: Redis/PostgreSQL集成
- 🔄 **负载均衡**: 多实例部署
- 📝 **API文档**: Swagger/OpenAPI集成
- 🧪 **测试框架**: 自动化测试套件

## 🎉 总结

通过这次改造，你的word2img-mcp服务现在支持两种通信方式：

1. **保持兼容**: 原有的stdio方式继续可用
2. **增加选择**: 新的HTTP方式提供更多可能性
3. **灵活部署**: 可根据不同场景选择合适的方式
4. **易于集成**: HTTP API让第三方集成变得简单

你现在可以：
- ✅ 在Claude Desktop中继续使用stdio方式
- ✅ 通过HTTP API在网络中访问服务
- ✅ 使用curl、Postman等工具调试
- ✅ 集成到Web应用或移动应用中
- ✅ 部署为微服务或容器化应用

这为你的MCP服务提供了更广阔的使用场景和集成可能性！
