# word2img-mcp 使用指南

## 目录
- [简介](#简介)
- [安装与配置](#安装与配置)
- [传输方式选择](#传输方式选择)
- [Stdio模式使用](#stdio模式使用)
- [HTTP模式使用](#http模式使用)
- [工具详解](#工具详解)
- [样式配置](#样式配置)
- [常见问题](#常见问题)
- [高级用法](#高级用法)

## 简介

word2img-mcp 是一个基于 MCP（Model Context Protocol）的服务，能够将 Markdown 文本转换为高质量的图片。支持多种渲染后端和丰富的样式配置选项。

### 主要特性

- 📝 **Markdown 渲染**: 支持完整的 Markdown 语法
- 🎨 **丰富样式**: 多种主题、字体、颜色配置
- 🖼️ **高质量输出**: 支持多种图片格式（PNG、JPG、WebP）
- 🔧 **多种后端**: imgkit/wkhtmltopdf、markdown-pdf、PIL 等
- 🌐 **双重传输**: 支持 stdio 和 HTTP 两种通信方式
- 📐 **3:4 比例**: 默认适合社交媒体的图片比例

## 安装与配置

### 1. 环境要求

- Python 3.13+
- uv 包管理器 [[memory:7894195]]

### 2. 安装依赖

```bash
# 进入项目目录
cd /root/word2img-mcp

# 如果网络较慢，增加超时时间
UV_HTTP_TIMEOUT=120 uv sync

# 或者分步安装
uv add fastapi uvicorn aiohttp
```

### 3. 验证安装

```bash
# 检查项目结构
ls -la

# 验证 Python 环境
python -c "import word2img_mcp; print('✅ 安装成功')"
```

## 传输方式选择

word2img-mcp 支持两种通信方式：

### Stdio 模式（原有方式）
- ✅ 适合本地进程间通信
- ✅ 性能更高
- ✅ 适合 Claude Desktop 等客户端
- ❌ 不支持网络访问

### HTTP 模式（新增方式）
- ✅ 支持网络访问
- ✅ 易于调试和集成
- ✅ 提供 RESTful API
- ✅ 支持 SSE 流式通信
- ❌ 性能略低于 stdio

## Stdio模式使用

### 1. 启动服务

```bash
# 方式1：使用原始启动脚本
uv run python start_mcp_server.py

# 方式2：使用新启动脚本的stdio模式
uv run python start_http_server.py --stdio
```

### 2. 配置 Claude Desktop

在 `claude_desktop_config.json` 中添加：

```json
{
  "mcpServers": {
    "word2img-mcp": {
      "command": "python",
      "args": ["/root/word2img-mcp/start_mcp_server.py"],
      "env": {}
    }
  }
}
```

### 3. 在 Claude 中使用

直接在 Claude 对话中使用：

```
请将以下 Markdown 转换为图片：

# 我的项目计划

## 第一阶段：准备工作
- [x] 需求分析
- [x] 技术选型
- [ ] 原型设计

## 第二阶段：开发实施
- [ ] 核心功能开发
- [ ] 测试验证
- [ ] 部署上线

> 预计完成时间：2024年2月

请使用深蓝色背景，白色文字。
```

## HTTP模式使用

### 1. 启动HTTP服务器

```bash
# 默认配置（localhost:8000）
uv run python start_http_server.py

# 自定义配置
uv run python start_http_server.py --host 0.0.0.0 --port 8080 --log-level debug

# 远程访问配置（推荐）
uv run python start_remote_server.py

# 直接启动
uv run python http_server.py
```

### 2. 服务器端点

启动后可访问以下端点：

- `http://localhost:8000/` - 服务器信息
- `http://localhost:8000/health` - 健康检查
- `http://localhost:8000/tools` - 工具列表
- `http://localhost:8000/mcp` - MCP JSON-RPC 端点
- `http://localhost:8000/sse` - SSE 流式连接

### 3. 使用客户端示例

```bash
# 运行完整示例
uv run python http_client_example.py
```

### 4. 手动API调用

#### 健康检查

```bash
curl http://localhost:8000/health
```

响应：
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000000",
  "server_initialized": false
}
```

#### 获取工具列表

```bash
curl http://localhost:8000/tools
```

#### MCP初始化

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "initialize",
    "id": 1,
    "params": {
      "protocolVersion": "2024-11-05",
      "capabilities": {"tools": {}},
      "clientInfo": {"name": "my-client", "version": "1.0.0"}
    }
  }'
```

#### 生成图片

```bash
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "id": 2,
    "params": {
      "name": "submit_markdown",
      "arguments": {
        "markdown_text": "# Hello World\n\n这是一个**测试文档**。\n\n- 项目1\n- 项目2\n- 项目3",
        "width": 800,
        "height": 1067,
        "background_color": "#2c3e50",
        "text_color": "#ffffff",
        "theme": "dark"
      }
    }
  }'
```

## 工具详解

### 1. submit_markdown

将 Markdown 文本转换为图片。

**参数说明：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `markdown_text` | string | 必填 | 要渲染的 Markdown 文本 |
| `width` | integer | 1200 | 图片宽度（像素） |
| `height` | integer | 1600 | 图片高度（像素） |
| `background_color` | string | "#FFFFFF" | 背景颜色 |
| `text_color` | string | "#000000" | 文字颜色 |
| `accent_color` | string | "#4682B4" | 强调色 |
| `font_family` | string | "Microsoft YaHei, ..." | 字体族 |
| `font_size` | integer | 20 | 基础字体大小 |
| `line_height` | number | 1.6 | 行高倍数 |
| `theme` | string | "default" | 主题样式 |
| `output_format` | string | "png" | 输出格式 |

**使用示例：**

```python
{
  "name": "submit_markdown",
  "arguments": {
    "markdown_text": """# 项目报告

## 执行摘要
本项目已顺利完成第一阶段的开发工作。

### 主要成果
- ✅ 完成核心功能开发
- ✅ 通过所有测试用例
- ⏳ 准备部署上线

### 下一步计划
1. 用户验收测试
2. 性能优化
3. 正式发布

---

**项目团队** | 2024年1月
""",
    "width": 1080,
    "height": 1440,
    "background_color": "#1e3a8a",
    "text_color": "#f8fafc",
    "accent_color": "#60a5fa",
    "theme": "professional",
    "font_size": 22,
    "line_height": 1.8
  }
}
```

### 2. get_image

获取生成的图片数据。

**参数说明：**

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `task_id` | string | 必填 | 任务ID |
| `as_base64` | boolean | true | 是否返回base64编码 |
| `show_in_chat` | boolean | true | 是否在聊天中显示图片 |
| `include_full_base64` | boolean | false | 是否包含完整base64数据 |
| `include_metadata` | boolean | false | 是否包含图片元数据 |

### 3. get_render_info

获取渲染器状态和可用后端信息。

### 4. list_tasks

列出任务历史和统计信息。

## 样式配置

### 主题选项

- `default` - 默认主题
- `dark` - 深色主题
- `light` - 浅色主题  
- `professional` - 专业主题
- `casual` - 休闲主题

### 颜色配置

支持多种颜色格式：

```python
# HEX 格式
"background_color": "#2c3e50"

# RGB 格式
"background_color": "rgb(44, 62, 80)"

# RGBA 格式  
"background_color": "rgba(44, 62, 80, 0.9)"

# CSS 颜色名
"background_color": "navy"
```

### 推荐配色方案

#### 1. 深蓝商务风 [[memory:7903413]]
```python
{
  "background_color": "#1e3a8a",
  "text_color": "#f8fafc", 
  "accent_color": "#60a5fa"
}
```

#### 2. 温暖橙色
```python
{
  "background_color": "#ea580c",
  "text_color": "#fffbeb",
  "accent_color": "#fed7aa"
}
```

#### 3. 优雅紫色
```python
{
  "background_color": "#7c3aed", 
  "text_color": "#f5f3ff",
  "accent_color": "#c4b5fd"
}
```

#### 4. 清新绿色
```python
{
  "background_color": "#059669",
  "text_color": "#ecfdf5", 
  "accent_color": "#a7f3d0"
}
```

### 字体配置

```python
# 中文优先
"font_family": "Microsoft YaHei, PingFang SC, Helvetica Neue, Arial, sans-serif"

# 英文优先  
"font_family": "Helvetica Neue, Arial, Microsoft YaHei, sans-serif"

# 等宽字体
"font_family": "Monaco, Consolas, Microsoft YaHei, monospace"
```

## 常见问题

### 1. 依赖安装失败

**问题：** `more-itertools` 下载超时

**解决：**
```bash
# 增加超时时间
UV_HTTP_TIMEOUT=120 uv sync

# 或使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt
```

### 2. HTTP服务启动失败

**问题：** 端口被占用

**解决：**
```bash
# 检查端口占用
lsof -i :8000

# 使用其他端口
python start_http_server.py --port 8001
```

### 3. 图片质量不佳

**解决：**
- 增加图片尺寸：`width=1600, height=2133`
- 使用 imgkit 后端：`backend_preference="imgkit"`
- 调整字体大小：`font_size=24`

### 4. 中文显示异常

**解决：**
- 确保字体支持中文：`font_family="Microsoft YaHei, ..."`
- 检查系统字体安装
- 使用 UTF-8 编码

### 5. 内存占用过高

**解决：**
- 降低图片尺寸
- 定期清理输出目录：`rm -rf outputs/*`
- 限制并发任务数

## 高级用法

### 1. 批量处理

```python
import asyncio
from http_client_example import MCPHTTPClient

async def batch_generate():
    async with MCPHTTPClient() as client:
        await client.initialize()
        
        texts = [
            "# 文档1\n内容1...",
            "# 文档2\n内容2...", 
            "# 文档3\n内容3..."
        ]
        
        tasks = []
        for i, text in enumerate(texts):
            task = client.call_tool("submit_markdown", {
                "markdown_text": text,
                "width": 800,
                "height": 1067
            })
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        return results

# 运行批量处理
results = asyncio.run(batch_generate())
```

### 2. 自定义样式模板

```python
# 创建样式模板
STYLE_TEMPLATES = {
    "report": {
        "background_color": "#1e293b",
        "text_color": "#f1f5f9", 
        "accent_color": "#3b82f6",
        "font_size": 22,
        "line_height": 1.8,
        "theme": "professional"
    },
    "social": {
        "background_color": "#be185d",
        "text_color": "#fdf2f8",
        "accent_color": "#f9a8d4", 
        "font_size": 20,
        "line_height": 1.6,
        "theme": "casual"
    }
}

# 使用模板
def generate_with_template(text, template_name):
    style = STYLE_TEMPLATES[template_name]
    return {
        "name": "submit_markdown",
        "arguments": {
            "markdown_text": text,
            **style
        }
    }
```

### 3. 监控和日志

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('word2img-mcp.log'),
        logging.StreamHandler()
    ]
)

# 启动服务时启用详细日志
python start_http_server.py --log-level debug
```

### 4. 性能优化

```python
# 预加载常用样式
PRELOAD_STYLES = [
    {"background_color": "#1e3a8a", "text_color": "#f8fafc"},
    {"background_color": "#059669", "text_color": "#ecfdf5"}
]

# 缓存渲染结果
import hashlib

def get_cache_key(text, options):
    content = f"{text}_{str(sorted(options.items()))}"
    return hashlib.md5(content.encode()).hexdigest()
```

### 5. 集成到其他应用

```python
# Flask 集成示例
from flask import Flask, request, jsonify
import asyncio

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
async def generate_image():
    data = request.json
    
    async with MCPHTTPClient() as client:
        await client.initialize()
        result = await client.call_tool("submit_markdown", data)
        return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## 结语

word2img-mcp 提供了灵活而强大的 Markdown 到图片转换功能。通过选择合适的传输方式和配置参数，你可以轻松地将其集成到各种应用场景中。

如果遇到问题，请检查：
1. 依赖是否正确安装
2. 服务是否正常启动  
3. 网络连接是否正常
4. 参数配置是否正确

更多高级功能和最新更新，请参考项目文档和源码。
