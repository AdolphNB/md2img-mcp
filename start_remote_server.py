#!/usr/bin/env python3
"""
word2img-mcp 远程访问启动脚本
配置为可远程访问的HTTP服务器
"""

import argparse
import sys
import os
import subprocess
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def get_public_ip():
    """获取公网IP地址"""
    try:
        import requests
        response = requests.get('http://ifconfig.me', timeout=5)
        return response.text.strip()
    except:
        try:
            import requests
            response = requests.get('http://ipinfo.io/ip', timeout=5)
            return response.text.strip()
        except:
            return "无法获取公网IP"

def check_port_available(port):
    """检查端口是否可用"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('0.0.0.0', port))
            return True
        except OSError:
            return False

def main():
    """启动远程访问MCP服务"""
    parser = argparse.ArgumentParser(description="word2img-mcp 远程访问服务器")
    parser.add_argument("--port", type=int, default=8000, help="监听端口 (默认: 8000)")
    parser.add_argument("--log-level", default="info", choices=["debug", "info", "warning", "error"], help="日志级别")
    parser.add_argument("--check-firewall", action="store_true", help="检查防火墙配置")
    
    args = parser.parse_args()
    
    print("🌐 word2img-mcp 远程访问服务器")
    print("=" * 60)
    
    # 检查端口可用性
    if not check_port_available(args.port):
        print(f"❌ 端口 {args.port} 已被占用，请使用其他端口")
        print(f"   尝试使用: python start_remote_server.py --port {args.port + 1}")
        sys.exit(1)
    
    # 获取IP信息
    print("📡 网络信息:")
    public_ip = get_public_ip()
    print(f"   公网IP: {public_ip}")
    print(f"   监听端口: {args.port}")
    print()
    
    # 显示访问URL
    print("🔗 访问URL:")
    print(f"   本地访问: http://localhost:{args.port}")
    if public_ip != "无法获取公网IP":
        print(f"   远程访问: http://{public_ip}:{args.port}")
    print()
    
    # 显示API端点
    print("📋 API端点:")
    base_url = f"http://{public_ip}:{args.port}" if public_ip != "无法获取公网IP" else f"http://localhost:{args.port}"
    print(f"   健康检查: {base_url}/health")
    print(f"   工具列表: {base_url}/tools") 
    print(f"   MCP端点: {base_url}/mcp")
    print(f"   SSE流式: {base_url}/sse")
    print()
    
    # 防火墙检查提示
    if args.check_firewall:
        print("🔥 防火墙配置检查:")
        print("   请确保以下端口已开放:")
        print(f"   - TCP {args.port}")
        print()
        print("   Ubuntu/Debian 配置命令:")
        print(f"   sudo ufw allow {args.port}/tcp")
        print(f"   sudo ufw enable")
        print()
        print("   CentOS/RHEL 配置命令:")
        print(f"   sudo firewall-cmd --permanent --add-port={args.port}/tcp")
        print(f"   sudo firewall-cmd --reload")
        print()
    
    # 安全提醒
    print("⚠️  安全提醒:")
    print("   - 此服务将监听所有网络接口 (0.0.0.0)")
    print("   - 任何人都可以访问此服务")
    print("   - 生产环境请配置认证和HTTPS")
    print("   - 建议限制访问来源IP")
    print()
    
    # 启动服务
    print("🚀 正在启动服务...")
    print("   按 Ctrl+C 停止服务")
    print("=" * 60)
    
    try:
        # 确保输出目录存在
        os.makedirs("outputs", exist_ok=True)
        
        # 启动HTTP服务器
        from http_server import run_http_server
        run_http_server(host="0.0.0.0", port=args.port, log_level=args.log_level)
        
    except KeyboardInterrupt:
        print("\n🛑 服务已停止")
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保依赖已正确安装:")
        print("   uv sync")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 服务启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
