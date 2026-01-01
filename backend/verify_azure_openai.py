#!/usr/bin/env python3
"""
验证是否正在使用 Azure OpenAI Service
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

print("=" * 60)
print("Azure OpenAI 配置验证")
print("=" * 60)
print()

# Check Azure OpenAI variables
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION")

# Check old OpenAI variables (should NOT be used)
old_openai_key = os.getenv("OPENAI_API_KEY")

print("✅ Azure OpenAI 配置:")
print(f"  AZURE_OPENAI_ENDPOINT: {'✅ 已设置' if azure_endpoint else '❌ 未设置'}")
if azure_endpoint:
    # Show partial endpoint for verification
    endpoint_display = azure_endpoint[:30] + "..." if len(azure_endpoint) > 30 else azure_endpoint
    print(f"    值: {endpoint_display}")
    
print(f"  AZURE_OPENAI_API_KEY: {'✅ 已设置' if azure_api_key else '❌ 未设置'}")
if azure_api_key:
    key_display = azure_api_key[:10] + "..." + azure_api_key[-5:] if len(azure_api_key) > 15 else "***"
    print(f"    值: {key_display}")

print(f"  AZURE_OPENAI_DEPLOYMENT_NAME: {'✅ 已设置' if azure_deployment else '❌ 未设置'}")
if azure_deployment:
    print(f"    值: {azure_deployment}")

print(f"  AZURE_OPENAI_API_VERSION: {'✅ 已设置' if azure_api_version else '⚠️  使用默认值'}")
if azure_api_version:
    print(f"    值: {azure_api_version}")

print()
print("旧 OpenAI 配置 (不应使用):")
print(f"  OPENAI_API_KEY: {'⚠️  已设置 (应该移除)' if old_openai_key else '✅ 未设置 (正确)'}")

print()
print("=" * 60)
print("结论:")
print("=" * 60)

if azure_endpoint and azure_api_key and azure_deployment:
    print("✅ 你正在使用 Azure OpenAI Service！")
    print("✅ 代码会使用 Azure OpenAI API 生成故事")
    print()
    print("🎉 符合 Imagine Cup 要求 - 使用了 Microsoft AI 服务！")
else:
    missing = []
    if not azure_endpoint:
        missing.append("AZURE_OPENAI_ENDPOINT")
    if not azure_api_key:
        missing.append("AZURE_OPENAI_API_KEY")
    if not azure_deployment:
        missing.append("AZURE_OPENAI_DEPLOYMENT_NAME")
    
    print(f"❌ Azure OpenAI 配置不完整！")
    print(f"缺少: {', '.join(missing)}")
    print()
    print("请检查 .env 文件并添加缺失的配置。")

if old_openai_key:
    print()
    print("⚠️  警告: 发现旧的 OPENAI_API_KEY")
    print("   建议从 .env 文件中移除，因为现在使用的是 Azure OpenAI")

print()

