"""
简单的 API 测试脚本
使用方法：python test_api_simple.py <endpoint> <api_key>
"""
import requests
import json
import sys

def test_api(endpoint, api_key):
    """测试任何兼容 OpenAI 格式的 API"""

    print(f"\n测试 Endpoint: {endpoint}")
    print(f"API Key: {api_key[:15]}...{api_key[-10:]}")
    print("=" * 60)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    # 简单的测试消息
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "Say 'Hello, I am working!'"}
        ],
        "max_tokens": 50
    }

    try:
        print("\n发送请求...")
        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=30
        )

        print(f"状态码: {response.status_code}")

        if response.status_code == 200:
            print("\n成功！API 可用！")
            result = response.json()
            print(json.dumps(result, indent=2, ensure_ascii=False))

            if 'choices' in result:
                content = result['choices'][0]['message']['content']
                print(f"\nAI 回复: {content}")
            return True
        else:
            print(f"\n失败！错误信息:")
            print(response.text)
            return False

    except Exception as e:
        print(f"\n错误: {str(e)}")
        return False

if __name__ == "__main__":
    # 默认使用 iFlow API Key
    api_key = "sk-765f4fdc95a1fcc249b3008091825e42"

    # 如果命令行提供了参数
    if len(sys.argv) > 1:
        endpoint = sys.argv[1]
        if len(sys.argv) > 2:
            api_key = sys.argv[2]
    else:
        # 让用户输入 endpoint
        print("请输入 iFlow API Endpoint (例如: https://api.iflow.cn/v1/chat/completions)")
        endpoint = input("Endpoint: ").strip()

        if not endpoint:
            print("\n使用默认 endpoint 测试...")
            endpoints_to_test = [
                "https://api.iflow.cn/v1/chat/completions",
                "https://iflow.work/v1/chat/completions",
            ]

            for ep in endpoints_to_test:
                test_api(ep, api_key)
                print("\n" + "=" * 60 + "\n")
        else:
            test_api(endpoint, api_key)
