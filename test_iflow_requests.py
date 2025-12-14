"""测试 iFlow API 使用 requests 库"""
import json
import requests
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 加载配置
with open('ai_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

print("配置信息:")
print(f"  API Key: {config['api_key'][:20]}...")
print(f"  Endpoint: {config['endpoint']}")
print(f"  Model: {config['model']}")
print()

# 构建请求
headers = {
    "Authorization": f"Bearer {config['api_key']}",
    "Content-Type": "application/json"
}

payload = {
    "model": config['model'],
    "messages": [
        {"role": "system", "content": "你是一位专业的英语教学助手。"},
        {"role": "user", "content": "请用一句话解释单词 hello 的含义。"}
    ],
    "temperature": 0.7,
    "max_tokens": 100
}

print("开始调用 API...")
try:
    response = requests.post(
        config['endpoint'],
        headers=headers,
        json=payload,
        timeout=30,
        verify=False  # 禁用 SSL 验证
    )

    print(f"✓ 响应状态码: {response.status_code}")
    print(f"✓ 响应头: {dict(response.headers)}")
    print()

    if response.status_code == 200:
        data = response.json()
        print(f"✓ 响应 JSON:")
        print(json.dumps(data, indent=2, ensure_ascii=False))

        if data.get('choices'):
            content = data['choices'][0]['message']['content']
            print(f"\n✓ 内容: {content}")
    else:
        print(f"✗ 错误响应:")
        print(response.text)

except Exception as e:
    print(f"✗ 请求失败: {e}")
    import traceback
    traceback.print_exc()
