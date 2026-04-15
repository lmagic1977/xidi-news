#!/usr/bin/env python3
"""
西地新闻 - AI 改写模块
使用 MiniMax API 改写新闻标题和内容
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import List, Dict

# 读取环境变量中的 API Key
def get_minimax_key():
    """获取 MiniMax API Key"""
    # 从 .env 文件读取
    env_path = os.path.expanduser('~/.hermes/.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.strip().startswith('MINIMAX_API_KEY='):
                    key = line.split('=', 1)[1].strip()
                    # 移除可能的引号
                    key = key.strip('"\'')
                    return key
    return None

MINIMAX_API_KEY = get_minimax_key()
MINIMAX_BASE_URL = 'https://api.minimax.io/anthropic/v1/messages'

class NewsRewriter:
    def __init__(self, api_key=None):
        self.api_key = api_key or MINIMAX_API_KEY
        self.base_url = MINIMAX_BASE_URL
        self.model = 'MiniMax-M2.7'
        self.retry_times = 3
        self.retry_delay = 5

    def rewrite_title(self, title: str) -> str:
        """使用AI改写标题"""
        if not title or len(title) < 5:
            return title

        prompt = f"""请将以下新闻标题进行改写，保持原意但使用不同的表达方式。
要求：
1. 不改变原意
2. 标题更加吸引人
3. 字数相近
4. 不要添加虚假信息

原文标题：
{title}

改写后的标题："""

        response = self.call_minimax(prompt)
        if response:
            # 提取AI回复
            rewritten = response.strip()
            if rewritten and len(rewritten) > 5:
                return rewritten
        return title

    def rewrite_content(self, title: str, content: str = '') -> Dict[str, str]:
        """使用AI改写新闻内容"""
        if not content:
            content = ''

        prompt = f"""请将以下新闻进行改写，保持原意但使用不同的表达方式。
要求：
1. 不改变原意，只调整表达
2. 语言更加流畅自然
3. 可以适当调整结构
4. 不要添加虚假信息

新闻标题：{title}

新闻内容：
{content[:500] if content else '无详细内容'}

改写后的版本："""

        response = self.call_minimax(prompt)
        if response:
            return {
                'rewritten_title': self.extract_title(response) or title,
                'rewritten_content': response.strip(),
                'success': True
            }
        return {
            'rewritten_title': title,
            'rewritten_content': content,
            'success': False
        }

    def extract_title(self, text: str) -> str:
        """从AI回复中提取标题"""
        lines = text.strip().split('\n')
        for line in lines[:3]:
            line = line.strip()
            # 如果这一行像标题（不太长，不太短）
            if 5 < len(line) < 50 and not line.startswith('#') and not line.startswith('-'):
                return line
        return ''

    def call_minimax(self, prompt: str, max_tokens: int = 500) -> str:
        """调用 MiniMax API"""
        if not self.api_key:
            print("  ⚠️ 未找到 MiniMax API Key")
            return None

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01'
        }

        payload = {
            'model': self.model,
            'max_tokens': max_tokens,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        }

        for attempt in range(self.retry_times):
            try:
                import requests
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=60
                )

                if response.status_code == 200:
                    data = response.json()
                    # MiniMax 兼容 Anthropic 格式
                    if 'content' in data:
                        for block in data['content']:
                            if block.get('type') == 'text':
                                return block.get('text', '')
                    elif 'completion' in data:
                        return data['completion']
                elif response.status_code == 401:
                    print("  ⚠️ API Key 无效或已过期")
                    return None
                elif response.status_code == 429:
                    print(f"  ⚠️ API 超出限额，尝试重试...")
                    time.sleep(self.retry_delay * (attempt + 1))
                else:
                    print(f"  ⚠️ API 返回错误: {response.status_code} - {response.text[:200]}")

            except Exception as e:
                print(f"  ⚠️ 调用失败: {e}")
                time.sleep(self.retry_delay)

        return None

    def rewrite_news_batch(self, news_list: List[Dict], target_count: int = 50) -> List[Dict]:
        """批量改写新闻"""
        print("=" * 50)
        print("✍️ 开始AI改写新闻...")
        print("=" * 50)

        rewritten_news = []
        success_count = 0
        fail_count = 0

        for i, news in enumerate(news_list[:target_count]):
            print(f"  改写 [{i+1}/{min(len(news_list), target_count)}]: {news['title'][:30]}...")

            # 只改写标题
            original_title = news.get('title', '')
            rewritten_title = self.rewrite_title(original_title)

            if rewritten_title and rewritten_title != original_title:
                success_count += 1
                print(f"    ✓ 改写成功")
            else:
                fail_count += 1
                rewritten_title = original_title
                print(f"    ⚠️ 保持原样")

            rewritten_news.append({
                'id': f"news_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}",
                'original_title': original_title,
                'title': rewritten_title,
                'url': news.get('url', ''),
                'source': news.get('source', '未知'),
                'summary': news.get('summary', ''),
                'rewritten_at': datetime.now().isoformat(),
                'status': 'success' if rewritten_title != original_title else 'unchanged'
            })

            # API 调用间隔，避免超出限额
            time.sleep(1)

        print("=" * 50)
        print(f"📊 改写完成: 成功 {success_count} 条, 保持原样 {fail_count} 条")
        print("=" * 50)

        return rewritten_news

def main():
    # 从存储目录读取爬取的新闻
    storage_dir = os.path.join(os.path.dirname(__file__), '..', 'storage', 'raw')
    latest_file = os.path.join(storage_dir, 'latest.json')

    if not os.path.exists(latest_file):
        print("❌ 未找到爬取的新闻文件，请先运行爬虫")
        return

    with open(latest_file, 'r', encoding='utf-8') as f:
        news_list = json.load(f)

    print(f"📰 从 {latest_file} 读取了 {len(news_list)} 条新闻")

    # 改写新闻
    rewriter = NewsRewriter()
    rewritten_news = rewriter.rewrite_news_batch(news_list, target_count=50)

    # 保存改写后的新闻
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'storage', 'rewritten')
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(output_dir, f'rewritten_news_{timestamp}.json')
    latest_output = os.path.join(output_dir, 'latest.json')

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(rewritten_news, f, ensure_ascii=False, indent=2)

    with open(latest_output, 'w', encoding='utf-8') as f:
        json.dump(rewritten_news, f, ensure_ascii=False, indent=2)

    print(f"💾 已保存改写后的新闻到 {output_file}")
    print(f"💾 最新版本保存到 {latest_output}")

    return rewritten_news

if __name__ == '__main__':
    main()
