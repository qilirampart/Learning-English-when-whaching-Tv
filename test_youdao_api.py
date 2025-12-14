"""测试有道翻译API"""
import requests
import hashlib
import time
import uuid
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv('backend/.env')

app_key = os.getenv('YOUDAO_APP_KEY')
app_secret = os.getenv('YOUDAO_APP_SECRET')

print(f"APP_KEY: {app_key}")
print(f"APP_SECRET: {app_secret}")
print()

if not app_key or not app_secret:
    print("❌ 有道API配置未找到！")
    exit(1)

# 测试单词
word = "fantastic"

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

print(f"正在查询单词: {word}")
print(f"请求参数: {params}")
print()

# 发送请求
try:
    response = requests.get('https://openapi.youdao.com/api', params=params, timeout=10)
    data = response.json()

    print(f"响应状态码: {response.status_code}")
    print(f"响应数据: {data}")
    print()

    if data.get('errorCode') == '0':
        print("✓ 有道API调用成功！")
        print(f"  音标: {data.get('basic', {}).get('phonetic', 'N/A')}")
        print(f"  翻译: {'; '.join(data.get('translation', []))}")
        print(f"  英文释义: {'; '.join(data.get('basic', {}).get('explains', []))}")
    else:
        print(f"✗ 有道API返回错误！")
        print(f"  错误代码: {data.get('errorCode')}")
        print(f"  错误信息: {data.get('msg', 'N/A')}")

        # 常见错误代码说明
        error_codes = {
            '101': '缺少必填的参数',
            '102': '不支持的语言类型',
            '103': '翻译文本过长',
            '104': '不支持的API类型',
            '105': '不支持的签名类型',
            '106': '不支持的响应类型',
            '107': '不支持的传输加密类型',
            '108': 'appKey无效',
            '109': 'batchLog格式不正确',
            '110': '无相关服务的有效实例',
            '111': '开发者账号无效',
            '201': '解密失败',
            '202': '签名检验失败',
            '203': '访问IP地址不在可访问IP列表',
            '301': '辞典查询失败',
            '302': '翻译查询失败',
            '303': '服务端的其它异常',
            '401': '账户已经欠费停',
            '411': '访问频率受限'
        }
        if data.get('errorCode') in error_codes:
            print(f"  说明: {error_codes[data.get('errorCode')]}")

except Exception as e:
    print(f"✗ 请求失败: {e}")
    import traceback
    traceback.print_exc()
