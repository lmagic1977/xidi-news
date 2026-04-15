#!/usr/bin/env python3
"""
西地新闻 - 主自动化脚本
爬取 -> AI改写 -> 生成网站
"""

import os
import sys
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_full_pipeline():
    """运行完整流程"""
    print("=" * 60)
    print("🚀 西地新闻自动化系统")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Step 1: 爬取完整文章
    print("\n📥 Step 1: 爬取新闻...")
    print("-" * 40)
    try:
        from scraper.article_scraper import NewsScraper
        scraper = NewsScraper()
        articles = scraper.scrape_all()

        if not articles:
            print("⚠️ 没有爬取到文章")
            articles = []
    except Exception as e:
        print(f"❌ 爬取出错: {e}")
        articles = []

    # 保存原始文章
    storage_dir = os.path.join(os.path.dirname(__file__), 'storage', 'raw')
    os.makedirs(storage_dir, exist_ok=True)
    raw_path = os.path.join(storage_dir, 'articles_latest.json')
    with open(raw_path, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"💾 原始文章已保存: {len(articles)} 篇")

    # Step 2: AI改写
    print("\n✍️ Step 2: AI改写...")
    print("-" * 40)
    try:
        from rewriter.article_rewriter import ArticleRewriter
        rewriter = ArticleRewriter()
        rewritten = rewriter.rewrite_articles_batch(articles, target_count=20)
    except Exception as e:
        print(f"⚠️ AI改写出错: {e}")
        rewritten = articles

    # 保存改写后文章
    rewritten_dir = os.path.join(os.path.dirname(__file__), 'storage', 'rewritten')
    os.makedirs(rewritten_dir, exist_ok=True)
    rewritten_path = os.path.join(rewritten_dir, 'latest.json')
    with open(rewritten_path, 'w', encoding='utf-8') as f:
        json.dump(rewritten, f, ensure_ascii=False, indent=2)
    print(f"💾 改写文章已保存: {len(rewritten)} 篇")

    # Step 3: 生成网站
    print("\n🌐 Step 3: 生成网站...")
    print("-" * 40)
    try:
        from website.news_generator import generate_website
        output_dir = os.path.join(os.path.dirname(__file__), 'website', 'output')
        website_path = generate_website(rewritten, output_dir)
        print(f"✅ 网站已生成: {website_path}")
    except Exception as e:
        print(f"❌ 网站生成出错: {e}")

    print("\n" + "=" * 60)
    print("🎉 完成!")
    print(f"📊 处理: 爬取 {len(articles)} 篇, 改写 {len(rewritten)} 篇")
    print("=" * 60)

    return True


if __name__ == '__main__':
    run_full_pipeline()
