"""
测试 iFlow API 连接
"""
import requests
import json
import sys
import io

# 设置输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# iFlow API 配置
API_KEY = "sk-765f4fdc95a1fcc249b3008091825e42"

# 尝试多个可能的 endpoint
ENDPOINTS = [
    "https://api.openai-proxy.org/v1/chat/completions",
    "https://api.gptsapi.net/v1/chat/completions",
    "https://aigptx.top/v1/chat/completions",
    "https://iflow.work/api/v1/chat/completions",
    "http://api.iflow.cn/v1/chat/completions",
    "https://api.iflow.cn/v1/chat/completions",
]

def test_iflow_api():
    """测试 iFlow API"""

    # 测试消息
    test_message = {
        "model": "gpt-3.5-turbo",  # 尝试不同模型
        "messages": [
            {
                "role": "user",
                "content": "请用一句话介绍自己"
            }
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    print("=" * 60)
    print("🔍 开始测试 iFlow API")
    print("=" * 60)

    # 尝试每个 endpoint
    for i, endpoint in enumerate(ENDPOINTS, 1):
        print(f"\n📡 测试 Endpoint {i}: {endpoint}")
        print("-" * 60)

        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=test_message,
                timeout=30
            )

            print(f"状态码: {response.status_code}")

            if response.status_code == 200:
                print("✅ 连接成功！")
                result = response.json()
                print("\n📄 返回数据:")
                print(json.dumps(result, indent=2, ensure_ascii=False))

                if 'choices' in result and len(result['choices']) > 0:
                    ai_response = result['choices'][0]['message']['content']
                    print(f"\n🤖 AI 回复: {ai_response}")
                    print("\n🎉 iFlow API 测试成功！可以正常使用！")
                    return True
            else:
                print(f"❌ 请求失败")
                print(f"响应内容: {response.text}")

        except requests.exceptions.Timeout:
            print("⏱️ 请求超时")
        except requests.exceptions.ConnectionError:
            print("🔌 连接错误，可能是网络问题或 endpoint 不正确")
        except Exception as e:
            print(f"❌ 错误: {str(e)}")

    print("\n" + "=" * 60)
    print("❌ 所有 endpoint 测试失败")
    print("=" * 60)
    return False

def test_different_models():
    """测试不同的模型"""
    models = [
        "gpt-3.5-turbo",
        "gpt-4",
        "gpt-4-turbo",
        "claude-3-sonnet",
        "claude-3.5-sonnet"
    ]

    # 使用第一个 endpoint
    endpoint = ENDPOINTS[0]

    print("\n" + "=" * 60)
    print("🔍 测试支持的模型")
    print("=" * 60)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    for model in models:
        print(f"\n📦 测试模型: {model}")

        test_message = {
            "model": model,
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 10
        }

        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=test_message,
                timeout=10
            )

            if response.status_code == 200:
                print(f"  ✅ {model} - 支持")
            else:
                print(f"  ❌ {model} - 不支持或错误")
        except:
            print(f"  ⚠️ {model} - 请求失败")

if __name__ == "__main__":
    print("\n🚀 iFlow API 测试工具")
    print("API Key:", API_KEY[:20] + "..." + API_KEY[-10:])

    # 先测试基本连接
    if test_iflow_api():
        # 如果基本连接成功，测试支持的模型
        response = input("\n是否测试支持的模型列表？(y/n): ")
        if response.lower() == 'y':
            test_different_models()

    print("\n✅ 测试完成！")
