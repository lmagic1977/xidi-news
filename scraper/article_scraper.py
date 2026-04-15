#!/usr/bin/env python3
"""
西地新闻 - 新闻爬虫系统 v2
抓取多个海外华人新闻网站的完整文章内容
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime
import os
import sys
from typing import List, Dict, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ArticleScraper:
    """单篇文章爬取器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })

    def fetch_page(self, url: str, timeout: int = 20) -> Optional[str]:
        """获取网页内容"""
        try:
            response = self.session.get(url, timeout=timeout)
            response.encoding = response.apparent_encoding or 'utf-8'
            return response.text
        except Exception as e:
            print(f"  ⚠️ 获取失败 {url}: {e}")
            return None

    def extract_article_content(self, url: str, source: str) -> Dict:
        """提取单篇文章的完整内容"""
        content = self.fetch_page(url)
        if not content:
            return {'title': '', 'content': '', 'images': [], 'author': '', 'publish_date': ''}

        soup = BeautifulSoup(content, 'html.parser')

        # 根据不同网站使用不同的提取策略
        if 'backchina.com' in url:
            return self.extract_backchina_article(soup, url)
        elif 'secretchina.com' in url:
            return self.extract_secrechina_article(soup, url)
        elif 'bbc.com' in url or 'bbc.co.uk' in url:
            return self.extract_bbc_article(soup, url)
        elif 'voachinese.com' in url:
            return self.extract_voa_article(soup, url)
        else:
            return self.extract_generic_article(soup, url)

    def extract_backchina_article(self, soup: BeautifulSoup, url: str) -> Dict:
        """提取倍可亲文章"""
        # 标题
        title = ''
        title_elem = soup.select_one('h1.article-title, h1.title, .article-header h1, h1')
        if title_elem:
            title = title_elem.get_text(strip=True)

        # 作者
        author = ''
        author_elem = soup.select_one('.author, .article-author, .byline')
        if author_elem:
            author = author_elem.get_text(strip=True)

        # 发布时间
        publish_date = ''
        date_elem = soup.select_one('.publish-date, .article-date, .time, time')
        if date_elem:
            publish_date = date_elem.get_text(strip=True)

        # 正文内容
        content = ''
        content_elem = soup.select_one('.article-content, .article-body, .content-body, .post-content, article')
        if content_elem:
            # 移除脚本和样式
            for tag in content_elem.find_all(['script', 'style', 'iframe', 'nav']):
                tag.decompose()
            content = content_elem.get_text(separator='\n', strip=True)

        # 图片
        images = []
        for img in soup.select('.article-content img, .article-body img, article img'):
            src = img.get('src') or img.get('data-src')
            if src and src.startswith('http'):
                alt = img.get('alt', '')
                images.append({'url': src, 'alt': alt})

        return {
            'title': title,
            'content': content[:3000] if content else '',  # 限制内容长度
            'images': images[:5],  # 最多5张图片
            'author': author,
            'publish_date': publish_date
        }

    def extract_secrechina_article(self, soup: BeautifulSoup, url: str) -> Dict:
        """提取看中国文章"""
        title = soup.select_one('h1.article-title, h1.title, h1')
        author = soup.select_one('.author, .article-author')
        date_elem = soup.select_one('.publish-date, .time')
        content_elem = soup.select_one('.article-content, .article-body, .content, article')

        content = ''
        if content_elem:
            for tag in content_elem.find_all(['script', 'style', 'iframe', 'nav']):
                tag.decompose()
            content = content_elem.get_text(separator='\n', strip=True)

        images = [{'url': img.get('src', ''), 'alt': img.get('alt', '')}
                   for img in soup.select('.article-content img, article img') if img.get('src')]

        return {
            'title': title.get_text(strip=True) if title else '',
            'content': content[:3000] if content else '',
            'images': images[:5],
            'author': author.get_text(strip=True) if author else '',
            'publish_date': date_elem.get_text(strip=True) if date_elem else ''
        }

    def extract_bbc_article(self, soup: BeautifulSoup, url: str) -> Dict:
        """提取BBC中文文章"""
        title = soup.select_one('h1.article-headline, h1')
        author = soup.select_one('.byline-name, .author')
        date_elem = soup.select_one('time, .publish-date')
        content_elem = soup.select_one('article .article-body, .story-body, article')

        content = ''
        if content_elem:
            for tag in content_elem.find_all(['script', 'style', 'aside', 'nav']):
                tag.decompose()
            content = content_elem.get_text(separator='\n', strip=True)

        images = [{'url': img.get('src', ''), 'alt': img.get('alt', '')}
                   for img in soup.select('article img') if img.get('src')]

        return {
            'title': title.get_text(strip=True) if title else '',
            'content': content[:3000] if content else '',
            'images': images[:5],
            'author': author.get_text(strip=True) if author else 'BBC中文',
            'publish_date': date_elem.get_text(strip=True) if date_elem else ''
        }

    def extract_voa_article(self, soup: BeautifulSoup, url: str) -> Dict:
        """提取美国之音文章"""
        title = soup.select_one('h1.article-title, h1')
        author = soup.select_one('.author-name, .byline')
        date_elem = soup.select_one('.article-date, time')
        content_elem = soup.select_one('.article-body, .story-body, article')

        content = ''
        if content_elem:
            for tag in content_elem.find_all(['script', 'style', 'aside']):
                tag.decompose()
            content = content_elem.get_text(separator='\n', strip=True)

        images = [{'url': img.get('src', ''), 'alt': img.get('alt', '')}
                   for img in soup.select('.article-body img, article img') if img.get('src')]

        return {
            'title': title.get_text(strip=True) if title else '',
            'content': content[:3000] if content else '',
            'images': images[:5],
            'author': author.get_text(strip=True) if author else '美国之音',
            'publish_date': date_elem.get_text(strip=True) if date_elem else ''
        }

    def extract_generic_article(self, soup: BeautifulSoup, url: str) -> Dict:
        """通用文章提取"""
        title = soup.select_one('h1, .article-title, .post-title')
        content_elem = soup.select_one('article, .article-content, .post-content, .entry-content')

        content = ''
        if content_elem:
            for tag in content_elem.find_all(['script', 'style', 'nav', 'header', 'footer']):
                tag.decompose()
            content = content_elem.get_text(separator='\n', strip=True)

        images = [{'url': img.get('src', ''), 'alt': img.get('alt', '')}
                   for img in soup.select('article img, .content img') if img.get('src')]

        return {
            'title': title.get_text(strip=True) if title else '',
            'content': content[:3000] if content else '',
            'images': images[:5],
            'author': '',
            'publish_date': ''
        }


class NewsScraper:
    """新闻爬虫主类"""

    def __init__(self):
        self.article_scraper = ArticleScraper()
        self.news_sources = [
            {
                'name': '倍可亲',
                'url': 'https://www.backchina.com',
                'list_selector': 'h3 a, h2 a, .article-title a, .news-title a',
                'target_count': 15
            },
            {
                'name': '看中国',
                'url': 'https://www.secretchina.com',
                'list_selector': 'h3 a, h2 a, .news-title a, .title a',
                'target_count': 10
            },
            {
                'name': 'BBC中文',
                'url': 'https://www.bbc.com/zhongwen/simp',
                'list_selector': '.bbc-uk8gs8 a, .bbc-1o0lr9v a, h3 a, .media__title a',
                'target_count': 5
            },
            {
                'name': '美国之音中文',
                'url': 'https://www.voachinese.com',
                'list_selector': 'h2 a, h3 a, .title a, .news-headline a',
                'target_count': 5
            },
            {
                'name': '侨报网',
                'url': 'https://www.qiaobaous.com',
                'list_selector': 'h3 a, h2 a, .news-title a',
                'target_count': 8
            },
            {
                'name': '华文日报',
                'url': 'https://zhdaily.com',
                'list_selector': 'h2 a, h3 a, .news-title a',
                'target_count': 7
            }
        ]

    def fetch_page(self, url: str, timeout: int = 15) -> Optional[str]:
        """获取网页内容"""
        try:
            response = self.article_scraper.session.get(url, timeout=timeout)
            response.encoding = 'utf-8'
            return response.text
        except Exception as e:
            print(f"  ⚠️ 获取失败 {url}: {e}")
            return None

    def scrape_news_list(self, source_info: Dict) -> List[Dict]:
        """爬取新闻列表"""
        print(f"  正在爬取 {source_info['name']}...")

        news_list = []
        content = self.fetch_page(source_info['url'])

        if not content:
            print(f"  ⚠️ 无法获取页面")
            return news_list

        soup = BeautifulSoup(content, 'html.parser')
        articles = soup.select(source_info.get('list_selector', 'h3 a, h2 a'))[:source_info['target_count'] * 2]

        base_url = source_info['url']
        for article in articles:
            if len(news_list) >= source_info['target_count']:
                break

            title = article.get_text(strip=True)
            link = article.get('href', '')

            # 跳过无效链接
            if not title or len(title) < 10:
                continue
            if not link:
                continue

            # 完善链接
            if not link.startswith('http'):
                if link.startswith('/'):
                    base = '/'.join(base_url.split('/')[:3])
                    link = base + link
                else:
                    link = base_url.rstrip('/') + '/' + link

            # 跳过非文章链接
            if any(x in link.lower() for x in ['javascript:', '#', 'login', 'register', 'subscribe']):
                continue

            news_list.append({
                'title': title,
                'url': link,
                'source': source_info['name']
            })

        print(f"  ✓ 获取 {len(news_list)} 条文章链接")
        return news_list

    def scrape_full_article(self, news_item: Dict) -> Dict:
        """爬取单篇文章完整内容"""
        try:
            article_data = self.article_scraper.extract_article_content(
                news_item['url'],
                news_item['source']
            )
            return {
                **news_item,
                'content': article_data.get('content', ''),
                'images': article_data.get('images', []),
                'author': article_data.get('author', ''),
                'publish_date': article_data.get('publish_date', ''),
                'scraped_at': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"  ⚠️ 提取内容失败: {news_item.get('url', '')} - {e}")
            return {
                **news_item,
                'content': '',
                'images': [],
                'author': '',
                'publish_date': '',
                'scraped_at': datetime.now().isoformat()
            }

    def scrape_all(self) -> List[Dict]:
        """爬取所有来源的新闻完整内容"""
        print("=" * 50)
        print("🚀 开始爬取新闻完整内容...")
        print("=" * 50)

        all_articles = []

        for source in self.news_sources:
            print(f"\n📰 正在处理: {source['name']}")

            # 1. 获取文章列表
            news_list = self.scrape_news_list(source)

            if not news_list:
                continue

            # 2. 逐个爬取完整内容
            for i, news in enumerate(news_list[:source['target_count']]):
                print(f"  [{i+1}/{min(len(news_list), source['target_count'])}] {news['title'][:30]}...")
                article = self.scrape_full_article(news)
                all_articles.append(article)

                # 添加延时，避免被封
                time.sleep(1)

        # 去重
        seen = set()
        unique_articles = []
        for article in all_articles:
            if article['url'] not in seen and article['content']:
                seen.add(article['url'])
                unique_articles.append(article)

        print("\n" + "=" * 50)
        print(f"📊 共获取 {len(unique_articles)} 篇完整文章 (去重后)")
        print("=" * 50)

        return unique_articles

    def save_to_json(self, articles: List[Dict], filepath: str):
        """保存到JSON文件"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        print(f"💾 已保存到 {filepath}")


def main():
    scraper = NewsScraper()
    articles = scraper.scrape_all()

    if not articles:
        print("❌ 没有爬取到任何文章")
        return []

    # 保存
    storage_dir = os.path.join(os.path.dirname(__file__), '..', 'storage', 'raw')
    os.makedirs(storage_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = os.path.join(storage_dir, f'articles_{timestamp}.json')
    scraper.save_to_json(articles, filepath)

    # 保存最新版本
    latest_filepath = os.path.join(storage_dir, 'articles_latest.json')
    scraper.save_to_json(articles, latest_filepath)

    return articles


if __name__ == '__main__':
    main()
