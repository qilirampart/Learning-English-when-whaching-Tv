"""翻译服务"""
import requests
import hashlib
import time
import uuid
import urllib3
from flask import current_app

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class TranslationService:
    """翻译服务类"""

    def __init__(self):
        self.youdao_url = 'https://openapi.youdao.com/api'

    def translate(self, word):
        """
        翻译单词
        :param word: 要翻译的单词
        :return: 翻译结果字典
        """
        # 尝试使用有道翻译API
        app_key = current_app.config.get('YOUDAO_APP_KEY')
        app_secret = current_app.config.get('YOUDAO_APP_SECRET')

        import sys
        print(f"[翻译服务] 查询单词: {word}", flush=True)
        print(f"[翻译服务] APP_KEY: {app_key[:10] if app_key else 'None'}...", flush=True)
        print(f"[翻译服务] APP_SECRET: {'已配置' if app_secret else '未配置'}", flush=True)
        sys.stdout.flush()

        if app_key and app_secret:
            print(f"[翻译服务] 尝试调用有道API...")
            result = self._translate_with_youdao(word, app_key, app_secret)
            if result:
                print(f"[翻译服务] API调用成功")

                # 检查翻译结果是否完整
                if self._is_incomplete_translation(result):
                    print(f"[翻译服务] 检测到翻译不完整，使用AI增强...")
                    result = self._enhance_with_ai(word, result)

                return result
            else:
                print(f"[翻译服务] API调用失败，使用模拟数据")
        else:
            print(f"[翻译服务] API未配置，使用模拟数据")

        # 如果API不可用，返回模拟数据（用于开发测试）
        return self._get_mock_translation(word)

    def _is_incomplete_translation(self, result):
        """检查翻译结果是否不完整"""
        # 如果definition为空或只有一个简单翻译，认为不完整
        definition = result.get('definition', '').strip()

        # 检查是否包含词性标注（如 n., v., adj. 等）
        has_part_of_speech = any(marker in definition for marker in ['n.', 'v.', 'adj.', 'adv.', 'prep.', 'conj.', 'pron.', 'num.'])

        # 如果没有词性标注或释义为空，认为不完整
        if not definition or not has_part_of_speech:
            return True

        # 如果只有一个释义（没有分号或换行），也认为可能不完整
        if ';' not in definition and '\n' not in definition and len(definition) < 30:
            return True

        return False

    def _enhance_with_ai(self, word, original_result):
        """使用AI增强翻译结果"""
        try:
            # 导入AI服务（避免循环导入）
            from app.services.ai_service import ai_service

            # 使用AI生成详细释义
            prompt = f"""请为英文单词 "{word}" 提供详细的中文释义。

要求：
1. 列出所有常见词性（如 n., v., adj., adv. 等）
2. 每个词性下列出2-3个主要释义
3. 用分号分隔不同释义
4. 格式示例：
   n. 释义1；释义2；释义3
   v. 释义1；释义2
   adj. 释义1；释义2

只返回释义内容，不要有任何其他文字或解释。"""

            messages = [
                {
                    "role": "system",
                    "content": "你是一位专业的英语词典编纂专家。请严格按照要求的格式返回单词释义。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]

            # 调用AI API
            ai_definition = ai_service._call_api(messages, temperature=0.3, max_tokens=500)

            if ai_definition:
                print(f"[翻译服务] AI增强成功")
                # 使用AI生成的释义替换原有的definition
                original_result['definition'] = ai_definition.strip()
                original_result['ai_enhanced'] = True  # 标记为AI增强
            else:
                print(f"[翻译服务] AI增强失败，保持原有结果")

        except Exception as e:
            print(f"[翻译服务] AI增强异常: {str(e)}")
            import traceback
            traceback.print_exc()

        return original_result
    
    def _translate_with_youdao(self, word, app_key, app_secret):
        """使用有道翻译API"""
        try:
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

            print(f"[有道API] 请求URL: {self.youdao_url}")
            print(f"[有道API] 请求参数: q={word}, from=en, to=zh-CHS")

            # 创建 session 并禁用代理
            session = requests.Session()
            session.trust_env = False  # 不使用环境变量中的代理设置

            # 发送请求（禁用代理和SSL验证）
            response = session.get(
                self.youdao_url,
                params=params,
                timeout=10,
                verify=False,  # 禁用 SSL 验证以避免代理问题
                proxies={}  # 显式禁用代理
            )
            data = response.json()

            print(f"[有道API] 响应状态码: {response.status_code}")
            print(f"[有道API] 响应数据: {data}")

            if data.get('errorCode') == '0':
                # 解析结果
                basic = data.get('basic', {})
                translation = data.get('translation', [])

                return {
                    'phonetic': basic.get('phonetic', ''),
                    'translation': '; '.join(translation) if translation else '',
                    'definition': '; '.join(basic.get('explains', [])) if basic.get('explains') else '',
                    'examples': self._extract_examples(data.get('web', []))
                }
            else:
                print(f"[有道API] 错误代码: {data.get('errorCode')}")

            return None

        except Exception as e:
            print(f"[有道API] 异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _extract_examples(self, web_data):
        """提取例句"""
        examples = []
        for item in web_data[:3]:  # 最多取3个
            key = item.get('key', '')
            value = '; '.join(item.get('value', []))
            if key and value:
                examples.append(f"{key}: {value}")
        return examples
    
    def _get_mock_translation(self, word):
        """
        获取模拟翻译数据（用于开发测试）
        实际部署时应该配置真实的翻译API
        """
        # 一些常见单词的模拟数据
        mock_data = {
            'hello': {
                'phonetic': '/həˈləʊ/',
                'translation': '你好；哈喽',
                'definition': 'used as a greeting or to begin a phone conversation',
                'examples': [
                    'Hello, how are you?',
                    'Say hello to your parents for me.'
                ]
            },
            'sarcastic': {
                'phonetic': '/sɑːrˈkæstɪk/',
                'translation': '讽刺的；挖苦的',
                'definition': 'using or characterized by irony in order to mock or convey contempt',
                'examples': [
                    'She made a sarcastic comment about his cooking.',
                    'Don\'t be so sarcastic!'
                ]
            },
            'awesome': {
                'phonetic': '/ˈɔːsəm/',
                'translation': '令人敬畏的；很棒的',
                'definition': 'extremely impressive or daunting; inspiring great admiration',
                'examples': [
                    'The view from the top was awesome.',
                    'That\'s an awesome idea!'
                ]
            }
        }
        
        # 返回模拟数据或默认数据
        if word.lower() in mock_data:
            return mock_data[word.lower()]
        else:
            return {
                'phonetic': f'/{word}/',
                'translation': f'{word}的中文翻译',
                'definition': f'Definition of {word}',
                'examples': [
                    f'Example sentence with {word}.',
                    f'Another example using {word}.'
                ]
            }

