"""测试 iFlow API 直接调用"""
import json
from openai import OpenAI

# 加载配置
with open('ai_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

print("配置信息:")
print(f"  API Key: {config['api_key'][:20]}...")
print(f"  Base URL: {config['base_url']}")
print(f"  Model: {config['model']}")
print()

# 初始化客户端
client = OpenAI(
    base_url=config['base_url'],
    api_key=config['api_key']
)

print("开始调用 API...")
try:
    response = client.chat.completions.create(
        model=config['model'],
        messages=[
            {"role": "system", "content": "你是一位专业的英语教学助手。"},
            {"role": "user", "content": "请用一句话解释单词 hello 的含义。"}
        ],
        temperature=0.7,
        max_tokens=100
    )

    print("\n✓ API 调用成功！")
    print(f"Response type: {type(response)}")
    print(f"Response: {response}")
    print()

    # 检查响应结构
    if hasattr(response, 'choices'):
        print(f"Choices: {response.choices}")
        print(f"Choices type: {type(response.choices)}")
        print(f"Choices length: {len(response.choices) if response.choices else 0}")

        if response.choices and len(response.choices) > 0:
            choice = response.choices[0]
            print(f"\nFirst choice: {choice}")
            print(f"Choice type: {type(choice)}")

            if hasattr(choice, 'message'):
                print(f"Message: {choice.message}")
                print(f"Message type: {type(choice.message)}")

                if hasattr(choice.message, 'content'):
                    print(f"\n内容: {choice.message.content}")
                else:
                    print("⚠️ message 没有 content 属性")
            else:
                print("⚠️ choice 没有 message 属性")
        else:
            print("⚠️ choices 为空")
    else:
        print("⚠️ response 没有 choices 属性")

except Exception as e:
    print(f"\n✗ API 调用失败: {e}")
    print(f"错误类型: {type(e)}")
    import traceback
    traceback.print_exc()
