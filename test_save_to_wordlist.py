"""
测试 AI 助手保存到单词本功能
"""
import requests
import json
import time
import sys
import io

# 设置标准输出编码为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:5000"

def test_save_workflow():
    """测试完整的 AI 生成 -> 保存到单词本流程"""

    print("=" * 60)
    print("测试 AI 助手保存到单词本功能")
    print("=" * 60)

    # 步骤 1: 生成 AI 用法解析
    print("\n[步骤 1] 调用 AI 用法解析...")
    usage_data = {
        "word": "awesome",
        "tv_show": "Friends"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/ai/usage",
            json=usage_data,
            timeout=70
        )

        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                ai_data = result.get('data', {})
                print(f"✅ AI 生成成功!")
                print(f"单词: {ai_data.get('word')}")
                print(f"剧名: {ai_data.get('tv_show')}")

                content = ai_data.get('content', '')
                print(f"\n生成内容长度: {len(content)} 字符")

                # 步骤 2: 提取例句
                print("[步骤 2] 提取例句...")
                examples = extract_examples(content)
                print(f"✅ 提取到 {len(examples)} 个例句:")
                for i, example in enumerate(examples, 1):
                    print(f"  {i}. 英文: {example['english']}")
                    print(f"     中文: {example['chinese']}")

                if len(examples) > 0:
                    # 步骤 3: 保存到单词本
                    print("\n[步骤 3] 保存到单词本...")

                    # 格式化例句文本（与图片格式一致）
                    context_note = 'AI 助手生成的例句：  '
                    for idx, example in enumerate(examples):
                        context_note += f'{idx + 1}. 英文例句："{example["english"]}"  中文翻译："{example["chinese"]}"  '

                    print(f"\n保存的格式预览：\n{context_note.strip()}\n")

                    save_data = {
                        "word": ai_data.get('word'),
                        "tv_show": ai_data.get('tv_show', ''),
                        "context_note": context_note.strip()
                    }

                    save_response = requests.post(
                        f"{BASE_URL}/api/words/query",
                        json=save_data,
                        timeout=10
                    )

                    if save_response.status_code == 200:
                        save_result = save_response.json()
                        if save_result.get('code') == 200:
                            print(f"✅ 保存成功!")
                            word_data = save_result.get('data', {})
                            print(f"单词 ID: {word_data.get('id')}")
                            print(f"保存的例句:\n{word_data.get('context_note')}")
                        else:
                            print(f"❌ 保存失败: {save_result.get('message')}")
                    else:
                        print(f"❌ 保存请求失败: {save_response.status_code}")
                else:
                    print("❌ 未提取到例句，无法保存")

            else:
                print(f"❌ AI 生成失败: {result.get('message')}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")

    except requests.exceptions.Timeout:
        print("❌ 请求超时（超过70秒）")
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")

def extract_examples(content):
    """提取例句（与前端逻辑相同，带中文翻译）"""
    import re

    if not content:
        return []

    examples = []
    lines = content.split('\n')

    current_english = None
    current_chinese = None

    # 查找英文例句和对应的中文翻译
    for i, line in enumerate(lines):
        # 匹配英文例句行
        if '英文例句' in line or '**英文' in line:
            match = re.search(r'"([^"]+)"', line)
            if match and match.group(1):
                sentence = match.group(1).strip()
                english_chars = len(re.findall(r'[a-zA-Z]', sentence))

                # 确保是英文句子
                if english_chars > 10:
                    current_english = sentence

        # 匹配中文翻译行
        elif current_english and ('中文翻译' in line or '**中文' in line):
            match = re.search(r'"([^"]+)"', line)
            if match and match.group(1):
                current_chinese = match.group(1).strip()

                # 保存英文和中文配对
                examples.append({
                    'english': current_english,
                    'chinese': current_chinese
                })

                current_english = None
                current_chinese = None

                if len(examples) >= 2:  # 只取前两个
                    break

    return examples

if __name__ == "__main__":
    test_save_workflow()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
