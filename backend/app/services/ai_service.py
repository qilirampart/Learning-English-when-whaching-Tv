"""
AI 服务模块
使用 iFlow API 提供智能助手功能
"""
import json
import requests
import os
import urllib3

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class AIService:
    """AI 服务类，支持主备 API 自动切换"""

    def __init__(self):
        """初始化 AI 服务"""
        # 从配置文件加载主备配置
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'ai_config.json')

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

                # 加载主 API 配置
                primary_config = config.get('primary', {})
                self.primary_api = {
                    'provider': primary_config.get('provider', 'anyrouter'),
                    'api_key': primary_config.get('api_key', ''),
                    'base_url': primary_config.get('base_url', 'https://c.cspok.cn/v1'),
                    'endpoint': primary_config.get('endpoint', 'https://c.cspok.cn/v1/chat/completions'),
                    'model': primary_config.get('model', 'claude-3-5-sonnet-20241022')
                }

                # 加载备用 API 配置
                backup_config = config.get('backup', {})
                self.backup_api = {
                    'provider': backup_config.get('provider', 'iFlow'),
                    'api_key': backup_config.get('api_key', ''),
                    'base_url': backup_config.get('base_url', 'https://apis.iflow.cn/v1'),
                    'endpoint': backup_config.get('endpoint', 'https://apis.iflow.cn/v1/chat/completions'),
                    'model': backup_config.get('model', 'Qwen3-Coder-Plus')
                }

                # 故障转移配置
                self.failover_enabled = config.get('failover_enabled', True)
                self.retry_attempts = config.get('retry_attempts', 3)
                self.timeout = config.get('timeout', 30)

        except FileNotFoundError:
            print("[AI Service] 配置文件不存在，使用默认配置")
            # 默认主 API 配置
            self.primary_api = {
                'provider': 'anyrouter',
                'api_key': 'sk-IxAvh52Ug0PgQLRdok4TmaJcLV3M5Qdcyp98xMf4aXBAFegC',
                'base_url': 'https://c.cspok.cn/v1',
                'endpoint': 'https://c.cspok.cn/v1/chat/completions',
                'model': 'claude-3-5-sonnet-20241022'
            }
            # 默认备用 API 配置
            self.backup_api = {
                'provider': 'iFlow',
                'api_key': 'sk-17b2eca4e3459195d34f162353b5cd33',
                'base_url': 'https://apis.iflow.cn/v1',
                'endpoint': 'https://apis.iflow.cn/v1/chat/completions',
                'model': 'Qwen3-Coder-Plus'
            }
            self.failover_enabled = True
            self.retry_attempts = 3
            self.timeout = 30

        # 当前使用的 API（初始为主 API）
        self.current_api = 'primary'

        print(f"[AI Service] 初始化完成")
        print(f"[AI Service] 主 API: {self.primary_api['provider']} ({self.primary_api['model']})")
        print(f"[AI Service] 备用 API: {self.backup_api['provider']} ({self.backup_api['model']})")
        print(f"[AI Service] 故障转移: {'启用' if self.failover_enabled else '禁用'}")

    def _call_api(self, messages, temperature=0.7, max_tokens=2000):
        """
        调用 AI API，支持主备自动切换

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            API 响应内容
        """
        # 先尝试主 API
        if self.current_api == 'primary' or not self.failover_enabled:
            result = self._try_api_call(
                self.primary_api,
                messages,
                temperature,
                max_tokens,
                api_type='primary'
            )
            if result:
                return result
            elif not self.failover_enabled:
                return None

        # 主 API 失败，尝试备用 API
        if self.failover_enabled:
            print(f"[AI Service] 主 API 失败，切换到备用 API...")
            result = self._try_api_call(
                self.backup_api,
                messages,
                temperature,
                max_tokens,
                api_type='backup'
            )
            if result:
                self.current_api = 'backup'
                return result

        print(f"[AI Service] 所有 API 都失败了")
        return None

    def _try_api_call(self, api_config, messages, temperature, max_tokens, api_type='primary'):
        """
        尝试调用指定的 API

        Args:
            api_config: API 配置字典
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            api_type: API 类型（primary 或 backup）

        Returns:
            API 响应内容或 None
        """
        try:
            print(f"[AI Service] 尝试调用 {api_type} API: {api_config['provider']}")

            payload = {
                "model": api_config['model'],
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }

            headers = {
                "Authorization": f"Bearer {api_config['api_key']}",
                "Content-Type": "application/json"
            }

            # 使用 requests 发送请求，禁用代理
            session = requests.Session()
            session.trust_env = False

            response = session.post(
                api_config['endpoint'],
                headers=headers,
                json=payload,
                timeout=self.timeout,
                verify=False,
                proxies={}
            )

            # 检查响应状态
            if response.status_code != 200:
                print(f"[AI Service] {api_type} API 返回错误状态码: {response.status_code}")
                print(f"[AI Service] 响应内容: {response.text}")
                return None

            # 解析响应
            data = response.json()

            # 提取内容
            if data.get('choices') and len(data['choices']) > 0:
                content = data['choices'][0].get('message', {}).get('content')
                print(f"[AI Service] {api_type} API 调用成功 ({api_config['provider']})")
                return content
            else:
                print(f"[AI Service] {api_type} API 响应格式异常: {data}")
                return None

        except Exception as e:
            print(f"[AI Service] {api_type} API 调用异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def generate_word_usage(self, word: str, tv_show: str = None) -> dict:
        """
        生成单词的详细用法解析

        Args:
            word: 要查询的单词
            tv_show: 剧集名称（可选）

        Returns:
            dict: 包含用法解析的字典
        """
        # 构建 prompt
        if tv_show:
            prompt = f"""请详细分析单词 "{word}" 在美剧《{tv_show}》或类似剧集中的用法。

要求：
1. 开头用一句话概括这个单词的核心含义和使用场景
2. 列出至少4个不同场景下的用法，每个用法包括：
   - 场景标题（如：Ted 的经典台词中使用）
   - 场景描述
   - 英文例句（尽量贴近剧集风格）
   - 中文翻译
   - 用法解释
3. 在最后添加一个"小结"部分，总结核心用法和注意事项
4. 提供2-3个相关延伸问题

请用中文回答，但例句要用英文。格式要清晰，易于理解。"""
        else:
            prompt = f"""请详细分析单词 "{word}" 的常见用法。

要求：
1. 开头用一句话概括这个单词的核心含义和使用场景
2. 列出至少4个不同场景下的用法，每个用法包括：
   - 场景标题（如：日常对话中、正式场合中等）
   - 场景描述
   - 英文例句
   - 中文翻译
   - 用法解释
3. 在最后添加一个"小结"部分，总结核心用法和注意事项
4. 提供2-3个相关延伸问题

请用中文回答，但例句要用英文。格式要清晰，易于理解。"""

        try:
            print(f"[AI Service] 开始调用 AI API，单词: {word}, 剧名: {tv_show}")

            # 构建消息
            messages = [
                {
                    "role": "system",
                    "content": "你是一位专业的英语教学助手，擅长通过美剧场景帮助学生理解和记忆单词用法。你的解释要生动、具体、易于理解。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]

            # 调用 API
            content = self._call_api(messages, temperature=0.7, max_tokens=2000)

            print(f"[AI Service] AI API 调用完成")
            print(f"[AI Service] 返回内容长度: {len(content) if content else 0}")
            if content:
                print(f"[AI Service] 内容预览: {content[:100]}...")
            else:
                print(f"[AI Service] ⚠️ 警告：AI 返回的 content 为空")

            if not content:
                return {
                    "success": False,
                    "error": "AI 返回内容为空",
                    "message": "AI 服务调用失败"
                }

            return {
                "success": True,
                "word": word,
                "tv_show": tv_show,
                "content": content,
                "model": self.primary_api['model'] if self.current_api == 'primary' else self.backup_api['model'],
                "provider": self.primary_api['provider'] if self.current_api == 'primary' else self.backup_api['provider'],
                "api_used": self.current_api
            }

        except Exception as e:
            print(f"[AI Service] ❌ AI API 调用失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "message": "AI 服务调用失败"
            }

    def generate_examples(self, word: str, count: int = 5) -> dict:
        """
        生成单词的例句

        Args:
            word: 要生成例句的单词
            count: 例句数量

        Returns:
            dict: 包含例句列表的字典
        """
        prompt = f"""为单词 "{word}" 生成 {count} 个英语例句。

要求：
1. 例句涵盖不同难度（从简单到复杂）
2. 包含不同使用场景（日常对话、正式场合、俚语等）
3. 每个例句提供中文翻译
4. 说明使用场景

请严格按照以下 JSON 格式返回，不要有任何额外的文字：
{{
    "examples": [
        {{
            "sentence": "英文例句",
            "translation": "中文翻译",
            "scenario": "使用场景",
            "level": "beginner"
        }}
    ]
}}

只返回 JSON，不要有任何解释文字或 markdown 标记。"""

        try:
            print(f"[AI Service] 开始生成例句，单词: {word}, 数量: {count}")

            messages = [
                {
                    "role": "system",
                    "content": "你是一位英语例句生成专家。请严格按照 JSON 格式返回结果，不要有任何额外的文字或 markdown 标记。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]

            content = self._call_api(messages, temperature=0.7, max_tokens=1500)

            if not content:
                print("[AI Service] AI 返回内容为空")
                raise Exception("AI 返回内容为空")

            print(f"[AI Service] AI 返回内容长度: {len(content)}")
            print(f"[AI Service] 内容预览: {content[:200]}...")

            # 尝试多种方式提取 JSON
            json_content = self._extract_json(content)

            if not json_content:
                print(f"[AI Service] 无法提取 JSON，原始内容: {content}")
                raise Exception("无法从 AI 响应中提取有效的 JSON")

            try:
                result = json.loads(json_content)

                # 验证返回的 JSON 格式
                if not isinstance(result, dict):
                    raise ValueError("JSON 必须是对象格式")

                if "examples" not in result:
                    raise ValueError("JSON 中缺少 examples 字段")

                if not isinstance(result["examples"], list):
                    raise ValueError("examples 必须是数组")

                # 验证每个例句的格式
                for i, example in enumerate(result["examples"]):
                    if not isinstance(example, dict):
                        raise ValueError(f"第 {i+1} 个例句格式错误")
                    if "sentence" not in example or "translation" not in example:
                        raise ValueError(f"第 {i+1} 个例句缺少必要字段")

                print(f"[AI Service] 成功解析 JSON，包含 {len(result['examples'])} 个例句")

                result["success"] = True
                result["word"] = word
                result["model"] = self.primary_api['model'] if self.current_api == 'primary' else self.backup_api['model']
                result["provider"] = self.primary_api['provider'] if self.current_api == 'primary' else self.backup_api['provider']
                result["api_used"] = self.current_api
                return result

            except (json.JSONDecodeError, ValueError) as e:
                print(f"[AI Service] JSON 解析或验证失败: {str(e)}")
                print(f"[AI Service] 提取的内容: {json_content[:500]}")
                raise Exception(f"JSON 格式错误: {str(e)}")

        except Exception as e:
            print(f"[AI Service] 生成例句失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "message": "AI 服务调用失败",
                "word": word
            }

    def _extract_json(self, content: str) -> str:
        """
        从 AI 响应中提取 JSON 内容

        Args:
            content: AI 返回的原始内容

        Returns:
            提取的 JSON 字符串，如果提取失败返回 None
        """
        import re

        # 方法 1: 查找 ```json 标记
        if "```json" in content:
            match = re.search(r'```json\s*\n(.*?)\n```', content, re.DOTALL)
            if match:
                return match.group(1).strip()

        # 方法 2: 查找普通 ``` 标记
        if "```" in content:
            match = re.search(r'```\s*\n(.*?)\n```', content, re.DOTALL)
            if match:
                return match.group(1).strip()

        # 方法 3: 查找 JSON 对象（以 { 开始，以 } 结束）
        match = re.search(r'\{.*\}', content, re.DOTALL)
        if match:
            return match.group(0).strip()

        # 方法 4: 查找 JSON 数组（以 [ 开始，以 ] 结束）
        match = re.search(r'\[.*\]', content, re.DOTALL)
        if match:
            # 如果是数组，包装成对象
            return '{"examples": ' + match.group(0).strip() + '}'

        # 如果都失败了，尝试直接返回原内容
        content = content.strip()
        if content.startswith('{') or content.startswith('['):
            return content

        return None

    def explain_difference(self, words: list) -> dict:
        """
        解释多个近义词的用法差异

        Args:
            words: 近义词列表

        Returns:
            dict: 包含差异解释的字典
        """
        words_str = "、".join(words)
        prompt = f"""请详细解释以下近义词的用法差异：{words_str}

要求：
1. 首先概括性说明这些词的共同点
2. 详细解释每个词的：
   - 核心含义
   - 使用场景
   - 语气/正式程度
   - 常见搭配
3. 为每个词提供 2-3 个例句（英文+中文翻译）
4. 总结使用建议

请用中文解释，但例句用英文。"""

        try:
            messages = [
                {
                    "role": "system",
                    "content": "你是一位英语词汇辨析专家，擅长解释近义词之间的细微差别。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]

            content = self._call_api(messages, temperature=0.7, max_tokens=2000)

            if not content:
                raise Exception("AI 返回内容为空")

            return {
                "success": True,
                "words": words,
                "content": content,
                "model": self.primary_api['model'] if self.current_api == 'primary' else self.backup_api['model'],
                "provider": self.primary_api['provider'] if self.current_api == 'primary' else self.backup_api['provider'],
                "api_used": self.current_api
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "AI 服务调用失败"
            }

    def generate_memory_tips(self, word: str) -> dict:
        """
        生成单词记忆口诀

        Args:
            word: 要生成记忆口诀的单词

        Returns:
            dict: 包含记忆技巧的字典
        """
        prompt = f"""请为单词 "{word}" 提供创意记忆方法。

要求：
1. 词根词缀分析（如果适用）
2. 联想记忆法（通过发音、形状等联想）
3. 谐音记忆（中文谐音）
4. 场景记忆（通过具体场景记忆）
5. 顺口溜或口诀

请提供至少 3 种不同的记忆方法，越有创意越好！"""

        try:
            messages = [
                {
                    "role": "system",
                    "content": "你是一位创意英语记忆法专家，擅长用有趣的方法帮助学生记忆单词。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]

            content = self._call_api(messages, temperature=0.9, max_tokens=1000)

            if not content:
                raise Exception("AI 返回内容为空")

            return {
                "success": True,
                "word": word,
                "content": content,
                "model": self.primary_api['model'] if self.current_api == 'primary' else self.backup_api['model'],
                "provider": self.primary_api['provider'] if self.current_api == 'primary' else self.backup_api['provider'],
                "api_used": self.current_api
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "AI 服务调用失败"
            }


# 创建全局 AI 服务实例
ai_service = AIService()
