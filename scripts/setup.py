#!/usr/bin/env python3
"""
一键配置脚本：引导用户完成环境配置和依赖安装
"""

import os
import sys
import subprocess
import platform

def print_step(step: str, message: str):
    """打印步骤信息"""
    print(f"\n{'='*50}")
    print(f"步骤 {step}: {message}")
    print('='*50)

def print_success(message: str):
    """打印成功信息"""
    print(f"✅ {message}")

def print_error(message: str):
    """打印错误信息"""
    print(f"❌ {message}")

def print_warning(message: str):
    """打印警告信息"""
    print(f"⚠️  {message}")

def check_python_version() -> bool:
    """检查Python版本"""
    print_step("1/5", "检查Python版本")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python版本符合要求: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python版本过低: {version.major}.{version.minor}.{version.micro}，需要Python 3.8+")
        return False

def install_dependencies() -> bool:
    """安装依赖包"""
    print_step("2/5", "安装Python依赖")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print_success("依赖安装完成")
        return True
    except subprocess.CalledProcessError:
        print_error("依赖安装失败，请手动运行: pip install -r requirements.txt")
        return False

def configure_env() -> bool:
    """配置环境变量"""
    print_step("3/5", "配置环境变量")
    
    env_file = ".env"
    if os.path.exists(env_file):
        overwrite = input("检测到已存在.env文件，是否覆盖？(y/N): ").strip().lower()
        if overwrite != 'y':
            print_success("跳过环境变量配置，使用现有.env文件")
            return True
    
    print("请准备好以下配置信息：")
    print("1. Tavily API Key (https://tavily.com/) - 用于搜索热点和图片")
    print("2. 微信公众号APPID - 在微信公众平台后台获取：开发 -> 基本配置")
    print("3. 微信公众号APPSECRET - 在微信公众平台后台获取：开发 -> 基本配置")
    print()
    print("⚠️  重要提示：请先在微信公众平台后台配置IP白名单")
    print("   路径：开发 -> 基本配置 -> IP白名单，添加你服务器的公网IP")
    print()
    
    tavily_key = input("请输入Tavily API Key: ").strip()
    while not tavily_key:
        tavily_key = input("Tavily API Key不能为空，请重新输入: ").strip()
    
    wechat_appid = input("请输入微信公众号APPID: ").strip()
    while not wechat_appid:
        wechat_appid = input("微信公众号APPID不能为空，请重新输入: ").strip()
    
    wechat_appsecret = input("请输入微信公众号APPSECRET: ").strip()
    while not wechat_appsecret:
        wechat_appsecret = input("微信公众号APPSECRET不能为空，请重新输入: ").strip()
    
    # 生成.env文件
    env_content = f"""# 微信公众号发布套件环境变量配置
# 配置时间: {os.popen('date').read().strip()}

# Tavily API Key - 用于搜索热点和图片
# 申请地址: https://tavily.com/
export TAVILY_API_KEY="{tavily_key}"

# 微信公众号配置
# 在微信公众平台后台获取：开发 -> 基本配置
export WECHAT_APPID="{wechat_appid}"
export WECHAT_APPSECRET="{wechat_appsecret}"

# ⚠️ 重要提示：必须在微信公众平台后台配置IP白名单
# 路径：开发 -> 基本配置 -> IP白名单，添加你服务器的公网IP
"""
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print_success(f"环境变量已保存到 {env_file}")
    
    # 加载环境变量
    if platform.system() != 'Windows':
        print("\n💡 提示：请运行以下命令加载环境变量：")
        print(f"  source {env_file}")
    else:
        print("\n💡 提示：请运行以下命令加载环境变量：")
        print(f"  .\\{env_file}")
    
    return True

def test_configuration() -> bool:
    """测试配置是否有效"""
    print_step("4/5", "测试配置有效性")
    
    # 加载环境变量
    if os.path.exists('.env'):
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.replace('export ', '').strip()
                    value = value.strip().strip('"\'')
                    os.environ[key] = value
    
    # 测试Tavily API
    try:
        from scripts.image_processor import ImageProcessor
        processor = ImageProcessor()
        test_images = processor.search_images("人工智能", 1)
        if test_images:
            print_success("Tavily API 配置有效")
        else:
            print_warning("Tavily API 测试返回空结果，可能是配额不足")
    except Exception as e:
        print_error(f"Tavily API 测试失败: {e}")
        print_warning("请检查Tavily API Key是否正确")
    
    # 测试微信API
    try:
        from scripts.wechat_api import WeChatAPI
        api = WeChatAPI()
        token = api.get_access_token()
        if token:
            print_success("微信API 配置有效")
            print(f"📋 公众号APPID: {wechat_appid}")
            print("✅ access_token 获取成功")
        else:
            print_warning("微信API 测试失败，请检查APPID和APPSECRET是否正确")
    except Exception as e:
        print_error(f"微信API 测试失败: {e}")
        print_warning("请检查：")
        print("  1. APPID和APPSECRET是否正确")
        print("  2. 公众号后台是否配置了IP白名单")
        print("  3. 公众号是否是认证的服务号/订阅号")
    
    return True

def show_usage() -> bool:
    """显示使用说明"""
    print_step("5/5", "配置完成！使用说明")
    
    print("\n🎯 基础使用：")
    print("  # 自动搜索热点并生成文章发布到草稿箱")
    print("  python scripts/publish.py")
    print()
    print("  # 指定主题生成技术文章")
    print("  python scripts/publish.py --topic \"智能座舱大模型应用\" --type tech")
    print()
    print("  # 指定主题生成热点文章，仅保存到文件")
    print("  python scripts/publish.py --topic \"AI大模型最新进展\" --type hot --output ./article.html")
    print()
    print("  # 指定公众号APPID发布")
    print("  python scripts/publish.py --topic \"自动驾驶技术\" --appid wx1234567890")
    print()
    
    print("📚 更多帮助：")
    print("  查看完整文档：README.md")
    print("  查看参数说明：python scripts/publish.py --help")
    print()
    
    print("🎉 配置完成！现在可以开始使用微信公众号发布套件了~")
    return True

def main():
    print("""
╔══════════════════════════════════════════════════╗
║               微信公众号发布套件                 ║
║             一键配置向导 v1.0.0                  ║
╚══════════════════════════════════════════════════╝
    """)
    
    steps = [
        check_python_version,
        install_dependencies,
        configure_env,
        test_configuration,
        show_usage
    ]
    
    for step in steps:
        if not step():
            print_error("配置流程中断，请解决问题后重新运行")
            sys.exit(1)
    
    print("\n" + "="*50)
    print("✅ 全部配置完成！")
    print("="*50)

if __name__ == "__main__":
    main()
