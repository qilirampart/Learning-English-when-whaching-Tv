"""测试有道API返回的 initiative 数据结构"""
import requests
import hashlib
import time
import uuid
import json
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

word = "initiative"
app_key = "3ae3f392772d7fba"
app_secret = "JaThett8QfjkGDhA2Cobvq0jVvUh85un"
youdao_url = 'https://openapi.youdao.com/api'

# 生成签名
salt = str(uuid.uuid1())
curtime = str(int(time.time()))
sign_str = app_key + word + salt + curtime + app_secret
sign = hashlib.sha256(sign_str.encode('utf-8')).hexdigest()

# 请求参数
params = {
    'q': word,
    'from': 'en',
    'to': 'zh-CHS',
    'appKey': app_key,
    'salt': salt,
    'sign': sign,
    'signType': 'v3',
    'curtime': curtime
}

print(f"查询单词: {word}")
print("="*80)

# 发送请求
session = requests.Session()
session.trust_env = False

response = session.get(
    youdao_url,
    params=params,
    timeout=10,
    verify=False,
    proxies={}
)

if response.status_code == 200:
    data = response.json()
    print("\n完整响应数据:")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    print("\n"+"="*80)
    print("\n关键字段解析:")
    print(f"\n1. translation (简单翻译): {data.get('translation', [])}")

    basic = data.get('basic', {})
    print(f"\n2. basic.phonetic (音标): {basic.get('phonetic', '')}")
    print(f"\n3. basic.explains (详细释义):")
    for i, explain in enumerate(basic.get('explains', []), 1):
        print(f"   {i}. {explain}")

    print(f"\n4. web (网络释义): {data.get('web', [])[:3]}")

else:
    print(f"请求失败: {response.status_code}")
    print(response.text)
