"""
iFlow API 测试脚本（根据官方文档）
官方文档: https://platform.iflow.cn/docs/api-reference
"""
import requests
import json
import sys
import io

# 设置输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# iFlow API 配置
API_KEY = "sk-765f4fdc95a1fcc249b3008091825e42"

# 根据 iFlow 平台的常见配置，可能的 endpoint
POSSIBLE_ENDPOINTS = [
    "https://api.iflow.cn/v1/chat/completions",
    "https://platform.iflow.cn/v1/chat/completions",
    "https://api.platform.iflow.cn/v1/chat/completions",
]

# 常见的模型名称
MODELS_TO_TEST = [
    "gpt-3.5-turbo",
    "gpt-4",
    "gpt-4-turbo-preview",
    "claude-3-sonnet",
]

def test_single_request(endpoint, model, api_key):
    """测试单个请求"""

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "你好，请回复：测试成功"
            }
        ],
        "max_tokens": 50,
        "temperature": 0.7
    }

    try:
        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=30
        )

        return response.status_code, response

    except requests.exceptions.Timeout:
        return None, "超时"
    except requests.exceptions.ConnectionError:
        return None, "连接失败"
    except Exception as e:
        return None, str(e)

def main():
    print("=" * 70)
    print("🚀 iFlow API 完整测试")
    print("=" * 70)
    print(f"\nAPI Key: {API_KEY[:20]}...{API_KEY[-15:]}")
    print(f"\n提示：如果你知道正确的 endpoint，请访问官网文档确认")
    print(f"文档地址: https://platform.iflow.cn/docs/api-reference\n")

    # 询问用户是否知道正确的 endpoint
    custom_endpoint = input("如果你知道正确的 endpoint，请输入（直接回车使用默认测试）: ").strip()

    if custom_endpoint:
        endpoints = [custom_endpoint]
    else:
        endpoints = POSSIBLE_ENDPOINTS

    # 询问模型
    custom_model = input("请输入要测试的模型名称（直接回车测试多个常见模型）: ").strip()

    if custom_model:
        models = [custom_model]
    else:
        models = MODELS_TO_TEST

    print("\n" + "=" * 70)
    print("开始测试...")
    print("=" * 70)

    success = False

    # 测试每个 endpoint 和模型组合
    for endpoint in endpoints:
        for model in models:
            print(f"\n📡 测试: {endpoint}")
            print(f"📦 模型: {model}")
            print("-" * 70)

            status_code, response = test_single_request(endpoint, model, API_KEY)

            if status_code == 200:
                print(f"✅ 成功！状态码: {status_code}")

                try:
                    result = response.json()

                    # 打印完整响应
                    print("\n📄 完整响应:")
                    print(json.dumps(result, indent=2, ensure_ascii=False))

                    # 提取 AI 回复
                    if 'choices' in result and len(result['choices']) > 0:
                        ai_message = result['choices'][0]['message']['content']
                        print(f"\n🤖 AI 回复: {ai_message}")
                        print(f"\n✨ 成功配置:")
                        print(f"   - Endpoint: {endpoint}")
                        print(f"   - Model: {model}")
                        print(f"   - API Key: {API_KEY}")
                        success = True

                        # 保存成功的配置
                        save_config(endpoint, model)

                        return True

                except Exception as e:
                    print(f"⚠️ 解析响应失败: {e}")

            elif status_code:
                print(f"❌ 失败！状态码: {status_code}")
                print(f"错误信息: {response.text[:200]}")
            else:
                print(f"❌ 请求失败: {response}")

    if not success:
        print("\n" + "=" * 70)
        print("❌ 所有测试均失败")
        print("=" * 70)
        print("\n建议:")
        print("1. 访问官方文档确认正确的 endpoint 和模型名称")
        print("2. 检查 API Key 是否有效")
        print("3. 确认账户是否有可用额度")
        print("4. 检查网络连接")

    return False

def save_config(endpoint, model):
    """保存成功的配置"""
    config = {
        "endpoint": endpoint,
        "model": model,
        "api_key": API_KEY
    }

    with open("iflow_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    print(f"\n💾 配置已保存到: iflow_config.json")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
