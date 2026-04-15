#!/usr/bin/env python3
"""
西地新闻 - 新闻爬虫系统
从多个海外华人新闻网站抓取新闻
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
from datetime import datetime
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class NewsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        })
        self.news_sources = [
            {
                'name': '倍可亲',
                'url': 'https://www.backchina.com',
                'rss_url': 'https://www.backchina.com/rss.xml',
                'target_count': 15
            },
            {
                'name': '看中国',
                'url': 'https://www.secretchina.com',
                'target_count': 10
            },
            {
                'name': '侨报网',
                'url': 'https://www.qiaobaous.com',
                'target_count': 8
            },
            {
                'name': 'BBC中文',
                'url': 'https://www.bbc.com/zhongwen/simp',
                'target_count': 5
            },
            {
                'name': '美国之音中文',
                'url': 'https://www.voachinese.com',
                'target_count': 5
            },
            {
                'name': '华文日报',
                'url': 'https://zhdaily.com',
                'target_count': 7
            }
        ]

    def fetch_page(self, url, timeout=15):
        """获取网页内容"""
        try:
            response = self.session.get(url, timeout=timeout)
            response.encoding = 'utf-8'
            return response.text
        except Exception as e:
            print(f"  ⚠️ 获取失败 {url}: {e}")
            return None

    def scrape_backchina(self, target_count=15):
        """爬取倍可亲新闻"""
        print("  正在爬取倍可亲...")
        news_list = []

        # 方法1: 尝试获取RSS
        try:
            rss_url = 'https://www.backchina.com/rss.xml'
            content = self.fetch_page(rss_url)
            if content:
                soup = BeautifulSoup(content, 'xml')
                items = soup.find_all('item')[:target_count]
                for item in items:
                    title = item.find('title')
                    link = item.find('link')
                    description = item.find('description')
                    pubdate = item.find('pubDate')

                    if title and link:
                        news_list.append({
                            'title': self.clean_text(title.text) if title else '',
                            'url': link.text.strip() if link else '',
                            'source': '倍可亲',
                            'summary': self.clean_text(description.text[:200]) if description and description.text else '',
                            'pubdate': pubdate.text if pubdate else '',
                            'scraped_at': datetime.now().isoformat()
                        })
                print(f"  ✓ 从RSS获取 {len(news_list)} 条")
        except Exception as e:
            print(f"  ⚠️ RSS获取失败: {e}")

        # 方法2: 从首页获取
        if len(news_list) < target_count:
            content = self.fetch_page('https://www.backchina.com')
            if content:
                soup = BeautifulSoup(content, 'html.parser')
                # 查找新闻链接
                articles = soup.select('h3 a, h2 a, .article-title a, .news-title a')[:target_count*2]
                for article in articles:
                    if len(news_list) >= target_count:
                        break
                    title = article.get_text(strip=True)
                    link = article.get('href', '')

                    if title and len(title) > 5 and link:
                        if not link.startswith('http'):
                            link = 'https://www.backchina.com' + link
                        news_list.append({
                            'title': title,
                            'url': link,
                            'source': '倍可亲',
                            'summary': '',
                            'pubdate': '',
                            'scraped_at': datetime.now().isoformat()
                        })

        print(f"  ✓ 倍可亲共获取 {len(news_list)} 条")
        return news_list[:target_count]

    def scrape_secrechina(self, target_count=10):
        """爬取看中国新闻"""
        print("  正在爬取看中国...")
        news_list = []
        content = self.fetch_page('https://www.secretchina.com')
        
        if content:
            soup = BeautifulSoup(content, 'html.parser')
            articles = soup.select('.news-title, .article-title, h3 a, h2 a, .title a')[:target_count*2]
            
            for article in articles:
                if len(news_list) >= target_count:
                    break
                title_elem = article if article.name in ['h3', 'h2'] else article
                title = title_elem.get_text(strip=True) if title_elem else ''
                link = article.get('href', '') if hasattr(article, 'get') else ''
                
                if title and len(title) > 5:
                    if link and not link.startswith('http'):
                        link = 'https://www.secretchina.com' + link
                    news_list.append({
                        'title': title,
                        'url': link,
                        'source': '看中国',
                        'summary': '',
                        'pubdate': '',
                        'scraped_at': datetime.now().isoformat()
                    })
        
        print(f"  ✓ 看中国获取 {len(news_list)} 条")
        return news_list[:target_count]

    def scrape_qiaobao(self, target_count=8):
        """爬取侨报网新闻"""
        print("  正在爬取侨报网...")
        news_list = []
        content = self.fetch_page('https://www.qiaobaous.com')
        
        if content:
            soup = BeautifulSoup(content, 'html.parser')
            articles = soup.select('h3 a, h2 a, .news-title a, .article-title a')[:target_count*2]
            
            for article in articles:
                if len(news_list) >= target_count:
                    break
                title = article.get_text(strip=True)
                link = article.get('href', '')
                
                if title and len(title) > 5:
                    if link and not link.startswith('http'):
                        link = 'https://www.qiaobaous.com' + link
                    news_list.append({
                        'title': title,
                        'url': link,
                        'source': '侨报网',
                        'summary': '',
                        'pubdate': '',
                        'scraped_at': datetime.now().isoformat()
                    })
        
        print(f"  ✓ 侨报网获取 {len(news_list)} 条")
        return news_list[:target_count]

    def scrape_bbc(self, target_count=5):
        """爬取BBC中文新闻"""
        print("  正在爬取BBC中文...")
        news_list = []
        content = self.fetch_page('https://www.bbc.com/zhongwen/simp')
        
        if content:
            soup = BeautifulSoup(content, 'html.parser')
            articles = soup.select('.bbc-uk8gs8, .bbc-1o0lr9v, h3 a, .media__title a')[:target_count*2]
            
            for article in articles:
                if len(news_list) >= target_count:
                    break
                title = article.get_text(strip=True) if hasattr(article, 'get_text') else ''
                link = article.get('href', '') if hasattr(article, 'get') else ''
                
                if not title and hasattr(article, 'select_one'):
                    title_elem = article.select_one('a')
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        link = title_elem.get('href', '')
                
                if title and len(title) > 5:
                    if link and not link.startswith('http'):
                        link = 'https://www.bbc.com' + link
                    news_list.append({
                        'title': title,
                        'url': link,
                        'source': 'BBC中文',
                        'summary': '',
                        'pubdate': '',
                        'scraped_at': datetime.now().isoformat()
                    })
        
        print(f"  ✓ BBC中文获取 {len(news_list)} 条")
        return news_list[:target_count]

    def scrape_voa(self, target_count=5):
        """爬取美国之音中文新闻"""
        print("  正在爬取美国之音...")
        news_list = []
        content = self.fetch_page('https://www.voachinese.com')
        
        if content:
            soup = BeautifulSoup(content, 'html.parser')
            articles = soup.select('h2 a, h3 a, .title a, .news-headline a')[:target_count*2]
            
            for article in articles:
                if len(news_list) >= target_count:
                    break
                title = article.get_text(strip=True)
                link = article.get('href', '')
                
                if title and len(title) > 5:
                    if link and not link.startswith('http'):
                        link = 'https://www.voachinese.com' + link
                    news_list.append({
                        'title': title,
                        'url': link,
                        'source': '美国之音',
                        'summary': '',
                        'pubdate': '',
                        'scraped_at': datetime.now().isoformat()
                    })
        
        print(f"  ✓ 美国之音获取 {len(news_list)} 条")
        return news_list[:target_count]

    def scrape_zhdaily(self, target_count=7):
        """爬取华文日报新闻"""
        print("  正在爬取华文日报...")
        news_list = []
        content = self.fetch_page('https://zhdaily.com')
        
        if content:
            soup = BeautifulSoup(content, 'html.parser')
            articles = soup.select('h2 a, h3 a, .news-title a, .article-title a')[:target_count*2]
            
            for article in articles:
                if len(news_list) >= target_count:
                    break
                title = article.get_text(strip=True)
                link = article.get('href', '')
                
                if title and len(title) > 5:
                    if link and not link.startswith('http'):
                        link = 'https://zhdaily.com' + link
                    news_list.append({
                        'title': title,
                        'url': link,
                        'source': '华文日报',
                        'summary': '',
                        'pubdate': '',
                        'scraped_at': datetime.now().isoformat()
                    })
        
        print(f"  ✓ 华文日报获取 {len(news_list)} 条")
        return news_list[:target_count]

    def clean_text(self, text):
        """清理文本"""
        if not text:
            return ''
        # 移除多余空白
        text = re.sub(r'\s+', ' ', text)
        # 移除特殊字符
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        return text.strip()

    def scrape_all(self):
        """爬取所有来源的新闻"""
        print("=" * 50)
        print("🚀 开始爬取新闻...")
        print("=" * 50)
        
        all_news = []
        
        # 爬取各个网站
        all_news.extend(self.scrape_backchina(15))
        time.sleep(1)
        
        all_news.extend(self.scrape_secrechina(10))
        time.sleep(1)
        
        all_news.extend(self.scrape_qiaobao(8))
        time.sleep(1)
        
        all_news.extend(self.scrape_bbc(5))
        time.sleep(1)
        
        all_news.extend(self.scrape_voa(5))
        time.sleep(1)
        
        all_news.extend(self.scrape_zhdaily(7))
        
        # 去重
        seen = set()
        unique_news = []
        for news in all_news:
            if news['title'] not in seen:
                seen.add(news['title'])
                unique_news.append(news)
        
        print("=" * 50)
        print(f"📊 共获取 {len(unique_news)} 条新闻 (去重后)")
        print("=" * 50)
        
        return unique_news

    def save_to_json(self, news_list, filepath):
        """保存到JSON文件"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(news_list, f, ensure_ascii=False, indent=2)
        print(f"💾 已保存到 {filepath}")

def main():
    scraper = NewsScraper()
    news_list = scraper.scrape_all()
    
    # 保存原始爬取数据
    storage_dir = os.path.join(os.path.dirname(__file__), '..', 'storage', 'raw')
    os.makedirs(storage_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = os.path.join(storage_dir, f'raw_news_{timestamp}.json')
    
    scraper.save_to_json(news_list, filepath)
    
    # 同时保存一份到 latest.json
    latest_filepath = os.path.join(storage_dir, 'latest.json')
    scraper.save_to_json(news_list, latest_filepath)
    
    return news_list

if __name__ == '__main__':
    main()
