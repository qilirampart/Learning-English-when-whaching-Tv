"""
iFlow API 正确配置测试
根据官方文档: https://platform.iflow.cn/docs/api-reference
"""
from openai import OpenAI
import sys
import io

# 设置输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# iFlow API 配置（根据官方文档）
API_KEY = "sk-765f4fdc95a1fcc249b3008091825e42"
BASE_URL = "https://apis.iflow.cn/v1"
ENDPOINT = "https://apis.iflow.cn/v1/chat/completions"

# 尝试不同的模型（从官方文档示例中提取）
# 常见的可能支持的模型
MODELS_TO_TEST = [
    "gpt-3.5-turbo",
    "gpt-4",
    "gpt-4-turbo",
    "claude-3-sonnet",
    "claude-3.5-sonnet",
    "TBStars2-200B-A13B",
    "deepseek-chat",
    "qwen-plus",
]

MODEL = "gpt-3.5-turbo"  # 默认模型

def test_with_openai_sdk():
    """使用 OpenAI SDK 测试（官方推荐方式）"""

    print("=" * 70)
    print("🚀 使用 OpenAI SDK 测试 iFlow API")
    print("=" * 70)
    print(f"Base URL: {BASE_URL}")
    print(f"Model: {MODEL}")
    print(f"API Key: {API_KEY[:20]}...{API_KEY[-15:]}")
    print("=" * 70)

    try:
        # 创建 OpenAI 客户端
        client = OpenAI(
            base_url=BASE_URL,
            api_key=API_KEY,
        )

        print("\n📤 发送测试消息...")

        # 发送请求
        completion = client.chat.completions.create(
            extra_body={},
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": "你好，请用一句话介绍你自己"
                }
            ]
        )

        # 获取响应
        ai_response = completion.choices[0].message.content

        print("\n✅ 成功！")
        print("=" * 70)
        print(f"🤖 AI 回复: {ai_response}")
        print("=" * 70)

        # 显示使用信息
        if hasattr(completion, 'usage'):
            print(f"\n📊 使用统计:")
            print(f"   - Prompt tokens: {completion.usage.prompt_tokens}")
            print(f"   - Completion tokens: {completion.usage.completion_tokens}")
            print(f"   - Total tokens: {completion.usage.total_tokens}")

        print("\n💾 保存配置...")
        save_config()

        return True

    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        print("\n建议:")
        print("1. 检查 API Key 是否有效")
        print("2. 确认账户是否有可用额度")
        print("3. 检查网络连接")
        return False

def test_with_requests():
    """使用 requests 直接测试"""
    import requests
    import json

    print("\n" + "=" * 70)
    print("🔧 使用 Requests 库测试")
    print("=" * 70)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": "请回复：测试成功"
            }
        ]
    }

    try:
        print(f"\n📤 POST {ENDPOINT}")
        response = requests.post(
            ENDPOINT,
            headers=headers,
            json=payload,
            timeout=30
        )

        print(f"📥 状态码: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("\n✅ 成功！")
            print("\n📄 完整响应:")
            print(json.dumps(result, indent=2, ensure_ascii=False))

            ai_response = result['choices'][0]['message']['content']
            print(f"\n🤖 AI 回复: {ai_response}")
            return True
        else:
            print(f"\n❌ 失败")
            print(f"错误信息: {response.text}")
            return False

    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        return False

def save_config():
    """保存成功的配置"""
    import json

    config = {
        "provider": "iFlow",
        "base_url": BASE_URL,
        "api_key": API_KEY,
        "model": MODEL,
        "endpoint": ENDPOINT
    }

    with open("ai_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"✅ 配置已保存到: ai_config.json")

def test_all_models():
    """测试所有可能的模型"""
    import requests
    import json

    print("\n" + "=" * 70)
    print("🔍 测试所有可能支持的模型")
    print("=" * 70)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    for model in MODELS_TO_TEST:
        print(f"\n📦 测试模型: {model}")
        print("-" * 70)

        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": "你好"}
            ],
            "max_tokens": 20
        }

        try:
            response = requests.post(
                ENDPOINT,
                headers=headers,
                json=payload,
                timeout=15
            )

            if response.status_code == 200:
                result = response.json()

                # 检查是否成功
                if 'choices' in result and result.get('status') != '435':
                    ai_response = result['choices'][0]['message']['content']
                    print(f"✅ 支持！AI 回复: {ai_response}")

                    # 保存成功的配置
                    global MODEL
                    MODEL = model
                    save_config()
                    return model
                else:
                    print(f"❌ 不支持 - {result.get('msg', '未知错误')}")
            else:
                print(f"❌ HTTP {response.status_code}")

        except Exception as e:
            print(f"⚠️ 错误: {str(e)}")

    return None

def main():
    print("\n🎯 iFlow API 测试工具")
    print("根据官方文档配置\n")

    # 测试所有模型找到可用的
    print("\n🔍 自动检测支持的模型...")
    working_model = test_all_models()

    if working_model:
        print("\n" + "=" * 70)
        print(f"🎉 找到可用模型: {working_model}")
        print("🎉 iFlow API 测试成功！可以开始开发 AI 功能了！")
        print("=" * 70)
        print(f"\n✅ 配置已保存到 ai_config.json")
    else:
        print("\n" + "=" * 70)
        print("❌ 未找到可用的模型")
        print("=" * 70)
        print("\n建议:")
        print("1. 访问 iFlow 控制台查看支持的模型列表")
        print("2. 检查账户是否有可用额度")
        print("3. 联系 iFlow 技术支持")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
