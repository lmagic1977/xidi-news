#!/usr/bin/env python3
"""
西地新闻 - AI 文章改写模块
使用 MiniMax API 重写完整文章内容
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import List, Dict
import re

# 读取环境变量中的 API Key
def get_minimax_key():
    """获取 MiniMax API Key"""
    env_path = os.path.expanduser('~/.hermes/.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                if line.strip().startswith('MINIMAX_API_KEY='):
                    key = line.split('=', 1)[1].strip()
                    key = key.strip('"\'')
                    return key
    return None

MINIMAX_API_KEY = get_minimax_key()

class ArticleRewriter:
    """文章AI改写器"""

    def __init__(self, api_key=None):
        self.api_key = api_key or MINIMAX_API_KEY
        self.retry_times = 3
        self.retry_delay = 5

    def call_api(self, prompt: str, max_tokens: int = 2000) -> str:
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
            'model': 'MiniMax-M2.7',
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
                    'https://api.minimax.io/anthropic/v1/messages',
                    headers=headers,
                    json=payload,
                    timeout=120
                )

                if response.status_code == 200:
                    data = response.json()
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
                    print(f"  ⚠️ API 超出限额，等待重试...")
                    time.sleep(self.retry_delay * (attempt + 2))
                else:
                    print(f"  ⚠️ API 返回错误: {response.status_code}")

            except Exception as e:
                print(f"  ⚠️ 调用失败: {e}")
                time.sleep(self.retry_delay)

        return None

    def rewrite_title(self, title: str) -> str:
        """改写标题"""
        if not title or len(title) < 5:
            return title

        prompt = f"""请将以下新闻标题进行改写，保持原意但使用不同的表达方式。
要求：
1. 不改变原意
2. 标题更加吸引人
3. 字数相近（15-30字）
4. 不要添加虚假信息
5. 只输出改写后的标题，不要其他内容

原文标题：
{title}

改写后的标题："""

        response = self.call_api(prompt, max_tokens=100)
        if response:
            cleaned = response.strip()
            # 移除可能的引号
            cleaned = cleaned.strip('"\'"')
            if 5 < len(cleaned) < 50:
                return cleaned
        return title

    def rewrite_content(self, article: Dict) -> Dict:
        """改写整篇文章"""
        original_title = article.get('title', '')
        original_content = article.get('content', '')
        source = article.get('source', '')

        if not original_content or len(original_content) < 50:
            # 内容太少，只改写标题
            new_title = self.rewrite_title(original_title)
            return {
                **article,
                'title': new_title,
                'rewritten_content': original_content,
                'rewrite_status': 'title_only' if new_title != original_title else 'unchanged'
            }

        # 准备内容片段（避免太长）
        content_to_rewrite = original_content[:2500]

        prompt = f"""你是一位资深新闻编辑，请将以下新闻文章进行改写，要求：
1. 保持原意和核心信息
2. 语言更加流畅、地道
3. 适当调整文章结构
4. 不添加虚假信息
5. 长度与原文相近
6. 只输出改写后的文章内容，不要其他说明

信息来源：{source}

原文标题：{original_title}

原文内容：
{content_to_rewrite}

改写后的文章："""

        print(f"    ✍️ 正在改写文章...")
        response = self.call_api(prompt, max_tokens=3000)

        new_title = self.rewrite_title(original_title)

        if response and len(response) > 50:
            print(f"    ✓ 改写成功 ({len(response)} 字)")
            return {
                **article,
                'title': new_title,
                'rewritten_content': response.strip(),
                'rewrite_status': 'full'
            }
        else:
            print(f"    ⚠️ 改写失败，保持原样")
            return {
                **article,
                'title': new_title,
                'rewritten_content': original_content,
                'rewrite_status': 'failed'
            }

    def rewrite_articles_batch(self, articles: List[Dict], target_count: int = 30) -> List[Dict]:
        """批量改写文章"""
        print("=" * 50)
        print("✍️ 开始AI改写文章...")
        print("=" * 50)

        rewritten = []
        success_count = 0

        articles_to_process = [a for a in articles if a.get('content')][:target_count]

        for i, article in enumerate(articles_to_process):
            title = article.get('title', '')[:40]
            print(f"\n  [{i+1}/{len(articles_to_process)}] {title}...")

            result = self.rewrite_content(article)
            rewritten.append(result)

            if result['rewrite_status'] in ['full', 'title_only']:
                success_count += 1

            # API 限流等待
            time.sleep(2)

        # 添加没有内容的文章（直接保留）
        articles_without_content = [a for a in articles if not a.get('content') and a not in rewritten]
        rewritten.extend(articles_without_content)

        print("\n" + "=" * 50)
        print(f"📊 改写完成: 成功 {success_count}/{len(articles_to_process)} 篇")
        print("=" * 50)

        return rewritten

    def save_to_json(self, articles: List[Dict], filepath: str):
        """保存到JSON文件"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        print(f"💾 已保存到 {filepath}")


def main():
    # 从存储目录读取爬取的文章
    storage_dir = os.path.join(os.path.dirname(__file__), '..', 'storage', 'raw')
    latest_file = os.path.join(storage_dir, 'articles_latest.json')

    if not os.path.exists(latest_file):
        print("❌ 未找到爬取的文章文件，请先运行爬虫")
        return

    with open(latest_file, 'r', encoding='utf-8') as f:
        articles = json.load(f)

    print(f"📰 从 {latest_file} 读取了 {len(articles)} 篇待改写文章")

    # 改写文章
    rewriter = ArticleRewriter()
    rewritten = rewriter.rewrite_articles_batch(articles, target_count=30)

    # 保存改写后的文章
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'storage', 'rewritten')
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(output_dir, f'rewritten_{timestamp}.json')
    latest_output = os.path.join(output_dir, 'latest.json')

    rewriter.save_to_json(rewritten, output_file)
    rewriter.save_to_json(rewritten, latest_output)

    return rewritten


if __name__ == '__main__':
    main()
