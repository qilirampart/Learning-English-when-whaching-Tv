"""
测试 iFlow 实际支持的模型
根据官网模型库页面
"""
import requests
import json
import sys
import io

# 设置输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# iFlow API 配置
API_KEY = "sk-765f4fdc95a1fcc249b3008091825e42"
BASE_URL = "https://apis.iflow.cn/v1"
ENDPOINT = "https://apis.iflow.cn/v1/chat/completions"

# 从官网模型库看到的实际支持的模型
SUPPORTED_MODELS = [
    # 通义千问系列
    "Qwen3-Coder-Plus",
    "Qwen3-Coder-480B-A35B",
    "Qwen3-Max",
    "Qwen3-VL-Plus",
    "Qwen3-Max-Preview",
    "Qwen3-32B",

    # 智谱清言
    "GLM-4.6",

    # DeepSeek 系列
    "DeepSeek-V3.2-Exp",
    "DeepSeek-V3.1-Terminus",
    "DeepSeek-R1",
    "DeepSeek-V3-671B",

    # Kimi
    "Kimi-K2-Instruct-0905",

    # TStars
    "TStars-2.0",
]

def test_model(model_name):
    """测试单个模型"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    payload = {
        "model": model_name,
        "messages": [
            {"role": "user", "content": "你好，请简单介绍一下你自己"}
        ],
        "max_tokens": 100
    }

    try:
        response = requests.post(
            ENDPOINT,
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()

            # 检查是否成功
            if 'choices' in result and result.get('status') != '435':
                ai_response = result['choices'][0]['message']['content']
                return True, ai_response, result
            else:
                return False, result.get('msg', '未知错误'), result
        else:
            return False, f"HTTP {response.status_code}", response.text

    except Exception as e:
        return False, str(e), None

def main():
    print("=" * 80)
    print("🚀 测试 iFlow 平台实际支持的模型")
    print("=" * 80)
    print(f"API Key: {API_KEY[:20]}...{API_KEY[-15:]}")
    print(f"Endpoint: {ENDPOINT}")
    print("=" * 80)

    working_models = []
    failed_models = []

    for i, model in enumerate(SUPPORTED_MODELS, 1):
        print(f"\n[{i}/{len(SUPPORTED_MODELS)}] 测试模型: {model}")
        print("-" * 80)

        success, message, result = test_model(model)

        if success:
            print(f"✅ 成功！")
            print(f"🤖 AI 回复: {message[:100]}...")
            working_models.append(model)

            # 保存第一个成功的模型配置
            if len(working_models) == 1:
                save_config(model, message)
        else:
            print(f"❌ 失败: {message}")
            failed_models.append(model)

    # 总结
    print("\n" + "=" * 80)
    print("📊 测试总结")
    print("=" * 80)
    print(f"\n✅ 可用模型 ({len(working_models)} 个):")
    for model in working_models:
        print(f"   - {model}")

    if failed_models:
        print(f"\n❌ 不可用模型 ({len(failed_models)} 个):")
        for model in failed_models:
            print(f"   - {model}")

    if working_models:
        print("\n" + "=" * 80)
        print(f"🎉 成功！找到 {len(working_models)} 个可用模型！")
        print("=" * 80)
        print(f"\n💡 推荐使用: {working_models[0]}")
        print(f"📁 配置已保存到: ai_config.json")
        print("\n✨ 现在可以开始开发 AI 智能助手功能了！")
        return True
    else:
        print("\n" + "=" * 80)
        print("❌ 未找到可用模型")
        print("=" * 80)
        print("\n可能原因:")
        print("1. 账户没有可用额度")
        print("2. 需要在控制台激活模型")
        print("3. API Key 权限不足")
        return False

def save_config(model, sample_response):
    """保存成功的配置"""
    config = {
        "provider": "iFlow",
        "base_url": BASE_URL,
        "endpoint": ENDPOINT,
        "api_key": API_KEY,
        "model": model,
        "sample_response": sample_response[:200],
        "notes": "iFlow 平台配置 - 可随时切换其他模型"
    }

    with open("ai_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"\n💾 配置已保存")

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n" + "=" * 80)
            print("🎯 下一步: 开始实现 AI 智能助手功能")
            print("=" * 80)
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
