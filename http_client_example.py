#!/usr/bin/env python3
"""
word2img-mcp HTTP 客户端示例
演示如何通过HTTP方式与MCP服务器通信
"""

import asyncio
import json
import aiohttp
import base64
from typing import Dict, Any, Optional

class MCPHTTPClient:
    """MCP HTTP客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.mcp_url = f"{base_url}/mcp"
        self.request_id = 0
        self.session: Optional[aiohttp.ClientSession] = None
        self.initialized = False
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def get_next_request_id(self) -> int:
        """获取下一个请求ID"""
        self.request_id += 1
        return self.request_id
    
    async def send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """发送MCP请求"""
        if not self.session:
            raise RuntimeError("客户端未初始化，请使用async with语句")
        
        request_data = {
            "jsonrpc": "2.0",
            "method": method,
            "id": self.get_next_request_id()
        }
        
        if params:
            request_data["params"] = params
        
        print(f"发送请求: {method}")
        
        try:
            async with self.session.post(self.mcp_url, json=request_data) as response:
                response_data = await response.json()
                
                if "error" in response_data:
                    raise Exception(f"服务器错误: {response_data['error']}")
                
                return response_data
        except Exception as e:
            print(f"请求失败: {e}")
            raise
    
    async def initialize(self) -> Dict[str, Any]:
        """初始化MCP连接"""
        params = {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "clientInfo": {
                "name": "word2img-mcp-http-client",
                "version": "1.0.0"
            }
        }
        
        response = await self.send_request("initialize", params)
        
        # 发送initialized通知
        await self.send_request("initialized")
        
        self.initialized = True
        print("MCP连接初始化成功")
        return response
    
    async def list_tools(self) -> Dict[str, Any]:
        """获取可用工具列表"""
        if not self.initialized:
            await self.initialize()
        
        response = await self.send_request("tools/list")
        return response.get("result", {})
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """调用工具"""
        if not self.initialized:
            await self.initialize()
        
        params = {
            "name": tool_name,
            "arguments": arguments
        }
        
        response = await self.send_request("tools/call", params)
        return response.get("result", {})
    
    async def check_health(self) -> Dict[str, Any]:
        """检查服务器健康状态"""
        if not self.session:
            raise RuntimeError("客户端未初始化")
        
        health_url = f"{self.base_url}/health"
        async with self.session.get(health_url) as response:
            return await response.json()

async def demo_client():
    """演示客户端使用"""
    print("word2img-mcp HTTP客户端演示")
    print("=" * 50)
    
    async with MCPHTTPClient() as client:
        try:
            # 检查服务器健康状态
            print("1. 检查服务器状态...")
            health = await client.check_health()
            print(f"   服务器状态: {health['status']}")
            print(f"   初始化状态: {health['server_initialized']}")
            print()
            
            # 初始化连接
            print("2. 初始化MCP连接...")
            init_response = await client.initialize()
            server_info = init_response.get("result", {}).get("serverInfo", {})
            print(f"   服务器: {server_info.get('name', 'unknown')}")
            print(f"   版本: {server_info.get('version', 'unknown')}")
            print()
            
            # 获取工具列表
            print("3. 获取可用工具...")
            tools_response = await client.list_tools()
            tools = tools_response.get("tools", [])
            print(f"   发现 {len(tools)} 个工具:")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description']}")
            print()
            
            # 演示调用工具
            print("4. 演示工具调用...")
            
            # 调用submit_markdown工具
            markdown_text = """# 测试标题

这是一个**测试文档**，用于演示word2img-mcp的HTTP传输功能。

## 功能特点

- 支持Markdown渲染
- 高质量图片输出
- 多种样式选项
- HTTP传输方式

> 这是一个引用块示例

```python
print("Hello, MCP HTTP!")
```

---

*生成时间: 2024年*
"""
            
            print("   调用submit_markdown工具...")
            submit_result = await client.call_tool("submit_markdown", {
                "markdown_text": markdown_text,
                "width": 800,
                "height": 1067,  # 3:4比例
                "background_color": "#2c3e50",  # 使用用户偏好的深蓝色背景 [[memory:7903413]]
                "text_color": "#ffffff",
                "theme": "dark"
            })
            
            content = submit_result.get("content", [])
            if content:
                task_info = json.loads(content[0]["text"])
                task_id = task_info["task_id"]
                print(f"   任务创建成功，ID: {task_id}")
                print(f"   图片尺寸: {task_info['image_size']}")
                print(f"   格式: {task_info['format']}")
                print()
                
                # 获取生成的图片
                print("   获取生成的图片...")
                image_result = await client.call_tool("get_image", {
                    "task_id": task_id,
                    "as_base64": True,
                    "show_in_chat": False,  # 在演示中不显示图片
                    "include_full_base64": True
                })
                
                image_content = image_result.get("content", [])
                if image_content:
                    image_data = json.loads(image_content[0]["text"])
                    print(f"   图片文件大小: {image_data['file_size']} 字节")
                    print(f"   Base64数据长度: {len(image_data.get('image_data', ''))} 字符")
                    print(f"   文件路径: {image_data['file_path']}")
                    print("   ✅ 图片生成成功！")
                else:
                    print("   ❌ 未能获取图片数据")
            else:
                print("   ❌ 工具调用失败")
            
            print()
            print("演示完成！")
            
        except Exception as e:
            print(f"❌ 演示过程中发生错误: {e}")
            return False
    
    return True

async def main():
    """主函数"""
    try:
        success = await demo_client()
        if success:
            print("\n🎉 HTTP传输方式测试成功！")
        else:
            print("\n❌ HTTP传输方式测试失败！")
            return 1
    except Exception as e:
        print(f"\n❌ 客户端运行失败: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(asyncio.run(main()))
