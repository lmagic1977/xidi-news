#!/usr/bin/env python3
"""
西地新闻 - 主自动化脚本
每天定时运行：爬取 -> AI改写 -> 更新网站
"""

import os
import sys
import json
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_full_pipeline():
    """运行完整的自动化流程"""
    print("=" * 60)
    print("🚀 西地新闻自动化系统启动")
    print(f"⏰ 运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Step 1: 爬取新闻
    print("\n📥 Step 1: 爬取新闻...")
    print("-" * 40)
    from scraper.news_scraper import NewsScraper
    scraper = NewsScraper()
    raw_news = scraper.scrape_all()

    if not raw_news:
        print("❌ 爬取失败，退出")
        return False

    # 保存原始新闻
    from storage import save_raw_news
    raw_path = save_raw_news(raw_news)
    print(f"💾 原始新闻已保存: {len(raw_news)} 条")

    # Step 2: AI改写
    print("\n✍️ Step 2: AI改写新闻...")
    print("-" * 40)
    from rewriter.ai_rewriter import NewsRewriter

    rewriter = NewsRewriter()
    rewritten_news = rewriter.rewrite_news_batch(raw_news, target_count=50)

    if not rewritten_news:
        print("⚠️ AI改写失败，使用原始标题")
        # 使用原始数据但添加ID
        rewritten_news = []
        for i, news in enumerate(raw_news[:50]):
            rewritten_news.append({
                'id': f"news_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}",
                'original_title': news.get('title', ''),
                'title': news.get('title', ''),
                'url': news.get('url', ''),
                'source': news.get('source', '未知'),
                'summary': news.get('summary', ''),
                'rewritten_at': datetime.now().isoformat(),
                'status': 'original'
            })

    # 保存改写后的新闻
    from storage import save_rewritten_news
    rewritten_path = save_rewritten_news(rewritten_news)
    print(f"💾 改写新闻已保存: {len(rewritten_news)} 条")

    # Step 3: 更新网站
    print("\n🌐 Step 3: 更新网站...")
    print("-" * 40)
    from website.generator import generate_website
    website_path = generate_website(rewritten_news)
    print(f"✅ 网站已更新: {website_path}")

    # Step 4: 清理旧文件
    print("\n🧹 Step 4: 清理旧文件...")
    print("-" * 40)
    from storage import archive_old_news
    archive_old_news(days=7)
    print("✅ 清理完成")

    print("\n" + "=" * 60)
    print("🎉 全部完成!")
    print(f"📊 本次处理: 爬取 {len(raw_news)} 条, 改写 {len(rewritten_news)} 条")
    print("=" * 60)

    return True

def run_scrape_only():
    """仅运行爬取"""
    print("=" * 60)
    print("📥 仅运行爬取模式")
    print("=" * 60)

    from scraper.news_scraper import NewsScraper
    scraper = NewsScraper()
    raw_news = scraper.scrape_all()

    if raw_news:
        from storage import save_raw_news
        save_raw_news(raw_news)
        print(f"✅ 已保存 {len(raw_news)} 条原始新闻")

    return True

def run_rewrite_only():
    """仅运行改写"""
    print("=" * 60)
    print("✍️ 仅运行改写模式")
    print("=" * 60)

    from storage import get_latest_raw_news, save_rewritten_news
    from rewriter.ai_rewriter import NewsRewriter

    raw_news = get_latest_raw_news()
    if not raw_news:
        print("❌ 未找到原始新闻，请先运行爬取")
        return False

    print(f"📰 读取到 {len(raw_news)} 条原始新闻")

    rewriter = NewsRewriter()
    rewritten_news = rewriter.rewrite_news_batch(raw_news, target_count=50)

    if rewritten_news:
        save_rewritten_news(rewritten_news)
        print(f"✅ 已保存 {len(rewritten_news)} 条改写新闻")

    return True

def show_status():
    """显示状态"""
    from storage import get_stats, get_latest_rewritten_news

    print("=" * 60)
    print("📊 西地新闻系统状态")
    print("=" * 60)

    stats = get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print()
    news = get_latest_rewritten_news()
    if news:
        print(f"✅ 最新改写新闻: {len(news)} 条")
        print("\n最新5条新闻:")
        for i, n in enumerate(news[:5]):
            print(f"  {i+1}. [{n.get('source', '未知')}] {n.get('title', '')[:40]}...")
    else:
        print("❌ 暂无改写新闻")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == 'scrape':
            run_scrape_only()
        elif command == 'rewrite':
            run_rewrite_only()
        elif command == 'status':
            show_status()
        else:
            run_full_pipeline()
    else:
        run_full_pipeline()
