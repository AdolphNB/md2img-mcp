# word2img-mcp 快速开始指南

## 🚀 5分钟上手指南

### 第一步：解决依赖安装问题

如果你遇到网络超时问题，使用以下命令：

```bash
# 进入项目目录
cd /root/word2img-mcp

# 设置更长的超时时间重新安装
UV_HTTP_TIMEOUT=120 uv sync

# 如果仍然失败，尝试分步安装关键依赖
uv add fastapi uvicorn aiohttp
```

### 第二步：选择使用方式

#### 方式A：Stdio模式（适合Claude Desktop）

```bash
# 启动stdio服务
python start_mcp_server.py
```

在Claude Desktop配置文件中添加：
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

#### 方式B：HTTP模式（适合网络访问）

```bash
# 启动HTTP服务（推荐用于测试）
python start_http_server.py

# 或指定端口
python start_http_server.py --port 8080
```

### 第三步：测试功能

#### 如果使用HTTP模式，运行测试：

```bash
# 运行完整的客户端示例
python http_client_example.py
```

#### 如果使用Stdio模式，在Claude中测试：

```
请将以下内容转换为图片：

# 🎯 今日任务清单

## ✅ 已完成
- [x] 晨会讨论
- [x] 代码审查
- [x] 文档更新

## 📋 进行中  
- [ ] 功能开发
- [ ] 测试用例编写

## 🔄 计划中
- [ ] 部署准备
- [ ] 用户培训

---
**更新时间：** 2024年1月  
**负责人：** 开发团队

请使用深蓝色背景，白色文字。
```

## 🎨 常用样式配置

### 1. 商务深蓝风（推荐）
```python
{
  "background_color": "#1e3a8a",
  "text_color": "#f8fafc",
  "accent_color": "#60a5fa",
  "theme": "professional"
}
```

### 2. 温暖橙色风
```python
{
  "background_color": "#ea580c", 
  "text_color": "#fffbeb",
  "accent_color": "#fed7aa",
  "theme": "casual"
}
```

### 3. 清新绿色风
```python
{
  "background_color": "#059669",
  "text_color": "#ecfdf5", 
  "accent_color": "#a7f3d0",
  "theme": "default"
}
```

## 🛠️ 常见问题快速解决

### Q1: 依赖安装失败
```bash
# 解决方案1：增加超时
UV_HTTP_TIMEOUT=120 uv sync

# 解决方案2：手动安装核心依赖
pip install fastapi uvicorn aiohttp pillow mcp

# 解决方案3：使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/ fastapi uvicorn aiohttp
```

### Q2: 端口被占用
```bash
# 检查占用
lsof -i :8000

# 使用其他端口
python start_http_server.py --port 8001
```

### Q3: 图片质量不好
- 增加尺寸：`width=1600, height=2133`
- 提高字体大小：`font_size=24`
- 使用PNG格式：`output_format="png"`

## 📝 快速API参考

### HTTP模式API调用示例

```bash
# 1. 健康检查
curl http://localhost:8000/health

# 2. 生成图片（简化版）
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call", 
    "id": 1,
    "params": {
      "name": "submit_markdown",
      "arguments": {
        "markdown_text": "# Hello World\n\n这是一个测试文档。",
        "background_color": "#1e3a8a",
        "text_color": "#ffffff"
      }
    }
  }'
```

## 🎯 实际使用场景

### 1. 制作社交媒体图片
```markdown
# 📢 重要公告

## 🚀 新功能上线
我们很高兴地宣布，新版本已正式发布！

### ✨ 主要更新
- 界面全新设计
- 性能提升50%  
- 新增智能推荐

### 📅 上线时间
**2024年1月15日**

---
关注我们获取更多更新 🔔
```

### 2. 制作工作报告
```markdown
# 📊 月度工作报告

## 📈 关键指标
- **用户增长**: +25%
- **收入增长**: +18% 
- **客户满意度**: 4.8/5.0

## 🎯 主要成就
1. ✅ 完成Q1目标的120%
2. ✅ 新产品成功发布
3. ✅ 团队扩展至15人

## 📋 下月计划
- 🔄 优化用户体验
- 🚀 拓展新市场
- 📚 团队培训计划

---
**报告人**: 项目经理 | **日期**: 2024年1月
```

### 3. 制作学习笔记
```markdown
# 📚 Python学习笔记

## 🐍 基础语法
```python
# 变量定义
name = "Alice"
age = 25

# 函数定义
def greet(name):
    return f"Hello, {name}!"
```

## 📝 重要概念
- **变量**: 存储数据的容器
- **函数**: 可重用的代码块  
- **类**: 对象的蓝图

## 💡 学习心得
> 编程是一门艺术，需要不断练习和思考。

---
**学习进度**: 60% | **下次复习**: 明天
```

## 🚀 下一步

1. **熟悉工具**: 多试试不同的Markdown语法和样式配置
2. **自定义样式**: 根据你的品牌或喜好调整颜色和字体
3. **批量处理**: 学习使用HTTP API进行批量图片生成
4. **集成应用**: 将服务集成到你的工作流程中

## 📖 更多资源

- 📄 [完整使用指南](USAGE_GUIDE.md) - 详细的功能说明
- 🌐 [HTTP传输指南](HTTP_TRANSPORT_GUIDE.md) - HTTP模式详解
- 💻 [客户端示例](http_client_example.py) - 完整的API调用示例

---

**开始使用吧！** 如果遇到问题，请查看完整的使用指南或检查常见问题解决方案。
