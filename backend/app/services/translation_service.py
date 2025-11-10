"""翻译服务"""
import requests
import hashlib
import time
import uuid
from flask import current_app


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
        
        if app_key and app_secret:
            result = self._translate_with_youdao(word, app_key, app_secret)
            if result:
                return result
        
        # 如果API不可用，返回模拟数据（用于开发测试）
        return self._get_mock_translation(word)
    
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
            
            # 发送请求
            response = requests.get(self.youdao_url, params=params, timeout=5)
            data = response.json()
            
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
            
            return None
        
        except Exception as e:
            print(f"翻译API错误: {str(e)}")
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

