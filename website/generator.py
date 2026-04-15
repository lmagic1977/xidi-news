#!/usr/bin/env python3
"""
西地新闻 - 网站生成器
将改写后的新闻更新到网站
"""

import os
import json
from datetime import datetime
from typing import List, Dict

def generate_news_cards(news_list: List[Dict]) -> str:
    """生成新闻卡片HTML"""
    cards_html = ''

    for news in news_list:
        category = get_category_for_source(news.get('source', ''))
        time_ago = get_time_ago(news.get('rewritten_at', ''))
        news_url = news.get('url', '#') or '#'
        title = news.get('title', '')
        summary = news.get('summary', '点击阅读更多最新新闻资讯')

        cards_html += f'''
        <article class="news-card">
          <a href="{news_url}" target="_blank" rel="noopener noreferrer" class="news-card-link">
            <img class="news-card-img" src="{get_placeholder_image(category)}" alt="{category}">
            <div class="news-card-body">
              <span class="category {category}">{get_source_display_name(news.get('source', ''))}</span>
              <h3>{title}</h3>
              <p class="excerpt">{summary}</p>
              <div class="meta">
                <span>📅 {time_ago}</span>
                <span>👁 {news.get('source', '西地新闻')}</span>
              </div>
            </div>
          </a>
        </article>
        '''
    return cards_html

def generate_trending_list(news_list: List[Dict]) -> str:
    """生成热门文章列表HTML"""
    trending_html = ''
    for i, news in enumerate(news_list[:5]):
        news_url = news.get('url', '#') or '#'
        title = news.get('title', '')[:40]
        source = news.get('source', '西地新闻')
        time_ago = get_time_ago(news.get('rewritten_at', ''))
        trending_html += f'''
            <li class="trending-item">
              <span class="trending-num">{i+1}</span>
              <div>
                <a href="{news_url}" target="_blank" rel="noopener noreferrer" style="text-decoration:none;color:inherit;">
                  <h4>{title}...</h4>
                </a>
                <p class="meta">{source} · {time_ago}</p>
              </div>
            </li>
        '''
    return trending_html

def get_category_for_source(source: str) -> str:
    """根据来源映射分类"""
    mapping = {
        '倍可亲': 'world',
        '看中国': 'world',
        '侨报网': 'world',
        'BBC中文': 'world',
        '美国之音': 'world',
        '华文日报': 'world',
        '华人网': 'culture',
        '新华网': 'world',
        '凤凰网': 'tech',
        '52hrtt': 'culture',
    }
    return mapping.get(source, 'world')

def get_source_display_name(source: str) -> str:
    """获取来源显示名称"""
    display = {
        '倍可亲': '国际',
        '看中国': '深度',
        '侨报网': '侨报',
        'BBC中文': 'BBC',
        '美国之音': '美国之音',
        '华文日报': '日报',
        '华人网': '社区',
        'secretchina': '看中国',
        'qiaobaous': '侨报',
        'voachinese': '美国之音',
    }
    if source in display:
        return display[source]
    return source[:4] if source else '新闻'

def get_placeholder_image(category: str) -> str:
    """获取占位图"""
    images = {
        'world': 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=600&q=80',
        'tech': 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=600&q=80',
        'business': 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=600&q=80',
        'culture': 'https://images.unsplash.com/photo-1467269204594-9661b134dd2b?w=600&q=80',
        'sports': 'https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=600&q=80',
    }
    return images.get(category, 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=600&q=80')

def get_time_ago(timestamp: str) -> str:
    """获取相对时间"""
    if not timestamp:
        return '刚刚'
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        now = datetime.now()
        diff = now - dt

        if diff.days > 0:
            return f'{diff.days}天前'
        elif diff.seconds > 3600:
            return f'{diff.seconds // 3600}小时前'
        elif diff.seconds > 60:
            return f'{diff.seconds // 60}分钟前'
        else:
            return '刚刚'
    except:
        return '刚刚'

def generate_website(news_list: List[Dict]) -> str:
    """生成完整的网站HTML"""

    # 更新时间为当前时间
    updated_at = datetime.now().strftime('%Y年%m月%d日 %H:%M')

    # 生成新闻卡片
    news_cards = generate_news_cards(news_list)

    # 生成热门文章
    trending_list = generate_trending_list(news_list)

    # 按来源分组统计
    source_stats = {}
    for news in news_list:
        source = news.get('source', '未知')
        source_stats[source] = source_stats.get(source, 0) + 1

    stats_html = ' · '.join([f"{k}: {v}条" for k, v in source_stats.items()])

    # Hero section links
    hero_url = news_list[0].get('url', '#') if news_list else '#'
    hero2_url = news_list[1].get('url', '#') if len(news_list) > 1 else '#'
    hero3_url = news_list[2].get('url', '#') if len(news_list) > 2 else '#'
    hero_title = news_list[0]['title'] if news_list else '西地新闻 - 您的资讯管家'
    hero2_title = news_list[1]['title'][:40] if len(news_list) > 1 else 'AI技术最新发展动态'
    hero3_title = news_list[2]['title'][:40] if len(news_list) > 2 else '全球市场最新资讯'
    hero_source = news_list[0].get('source', '西地新闻') if news_list else ''

    # 来源标签
    source_tags = ''.join([f'<span style="background: var(--color-bg-warm); padding: 6px 14px; border-radius: var(--radius-pill); font-size: 13px;">{k}</span>' for k in source_stats.keys()])

    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>西地新闻 - 海外华人新闻门户</title>
  <meta name="description" content="西地新闻是服务全球华人的新闻平台，聚合海外华人关心的国际、财经、科技、文化等资讯。">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --color-bg: #ffffff;
      --color-bg-warm: #f6f5f4;
      --color-text: rgba(0,0,0,0.95);
      --color-text-secondary: #615d59;
      --color-text-muted: #a39e98;
      --color-accent: #0075de;
      --color-accent-dark: #005bab;
      --color-border: rgba(0,0,0,0.1);
      --shadow-card: rgba(0,0,0,0.04) 0px 4px 18px, rgba(0,0,0,0.027) 0px 2.025px 7.84688px, rgba(0,0,0,0.02) 0px 0.8px 2.925px, rgba(0,0,0,0.01) 0px 0.175px 1.04062px;
      --radius-sm: 4px;
      --radius-md: 8px;
      --radius-lg: 12px;
      --radius-pill: 9999px;
    }}

    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }}

    body {{
      font-family: 'Noto Sans SC', 'Inter', -apple-system, system-ui, sans-serif;
      color: var(--color-text);
      background: var(--color-bg);
      line-height: 1.5;
    }}

    .container {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 0 24px;
    }}

    .update-info {{
      background: var(--color-bg-warm);
      padding: 12px 24px;
      text-align: center;
      font-size: 13px;
      color: var(--color-text-secondary);
    }}

    .header {{
      background: var(--color-bg);
      border-bottom: 1px solid var(--color-border);
      position: sticky;
      top: 0;
      z-index: 100;
    }}

    .header-inner {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      height: 64px;
    }}

    .logo {{
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 22px;
      font-weight: 700;
      color: var(--color-text);
      text-decoration: none;
    }}

    .logo-icon {{
      width: 36px;
      height: 36px;
      background: linear-gradient(135deg, #ff6b6b, #ee5a24);
      border-radius: var(--radius-md);
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 18px;
    }}

    .nav {{
      display: flex;
      align-items: center;
      gap: 32px;
    }}

    .nav a {{
      font-size: 15px;
      font-weight: 500;
      color: var(--color-text);
      text-decoration: none;
      padding: 8px 0;
      transition: color 0.2s;
    }}

    .nav a:hover {{
      color: var(--color-accent);
    }}

    .header-actions {{
      display: flex;
      align-items: center;
      gap: 16px;
    }}

    .search-box {{
      display: flex;
      align-items: center;
      background: var(--color-bg-warm);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-pill);
      padding: 8px 16px;
      gap: 8px;
      width: 240px;
    }}

    .search-box input {{
      border: none;
      background: transparent;
      outline: none;
      font-size: 14px;
      width: 100%;
      font-family: inherit;
    }}

    .btn-subscribe {{
      background: var(--color-accent);
      color: white;
      border: none;
      padding: 8px 20px;
      border-radius: var(--radius-pill);
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.2s;
    }}

    .btn-subscribe:hover {{
      background: var(--color-accent-dark);
    }}

    .breaking-news {{
      background: #ee5a24;
      color: white;
      padding: 10px 0;
      overflow: hidden;
    }}

    .breaking-news-inner {{
      display: flex;
      align-items: center;
      gap: 16px;
    }}

    .breaking-label {{
      background: rgba(255,255,255,0.2);
      padding: 4px 12px;
      border-radius: var(--radius-pill);
      font-size: 12px;
      font-weight: 600;
      white-space: nowrap;
    }}

    .ticker {{
      flex: 1;
      overflow: hidden;
    }}

    .ticker-content {{
      display: flex;
      gap: 48px;
      animation: ticker 30s linear infinite;
    }}

    .ticker-content:hover {{
      animation-play-state: paused;
    }}

    .ticker-item {{
      white-space: nowrap;
      font-size: 14px;
    }}

    @keyframes ticker {{
      0% {{ transform: translateX(0); }}
      100% {{ transform: translateX(-50%); }}
    }}

    .hero {{
      padding: 48px 0;
    }}

    .hero-grid {{
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 24px;
    }}

    .hero-main {{
      position: relative;
      border-radius: var(--radius-lg);
      overflow: hidden;
      height: 420px;
      cursor: pointer;
    }}

    .hero-main img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
    }}

    .hero-main-overlay {{
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      padding: 32px;
      background: linear-gradient(transparent, rgba(0,0,0,0.8));
      color: white;
    }}

    .hero-main-overlay .category {{
      display: inline-block;
      background: var(--color-accent);
      padding: 4px 12px;
      border-radius: var(--radius-pill);
      font-size: 12px;
      font-weight: 600;
      margin-bottom: 12px;
    }}

    .hero-main-overlay h1 {{
      font-size: 28px;
      font-weight: 700;
      line-height: 1.3;
      margin-bottom: 12px;
    }}

    .hero-main-overlay .meta {{
      font-size: 13px;
      color: rgba(255,255,255,0.8);
    }}

    .hero-main-overlay a {{
      color: inherit;
      text-decoration: none;
    }}

    .hero-main:hover .hero-main-overlay h1 {{
      text-decoration: underline;
    }}

    .hero-side {{
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}

    .hero-side-item {{
      position: relative;
      border-radius: var(--radius-lg);
      overflow: hidden;
      height: calc(50% - 8px);
      cursor: pointer;
    }}

    .hero-side-item img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
    }}

    .hero-side-overlay {{
      position: absolute;
      bottom: 0;
      left: 0;
      right: 0;
      padding: 20px;
      background: linear-gradient(transparent, rgba(0,0,0,0.85));
      color: white;
    }}

    .hero-side-overlay .category {{
      display: inline-block;
      background: #2a9d99;
      padding: 3px 10px;
      border-radius: var(--radius-pill);
      font-size: 11px;
      font-weight: 600;
      margin-bottom: 8px;
    }}

    .hero-side-overlay h3 {{
      font-size: 16px;
      font-weight: 600;
      line-height: 1.4;
    }}

    .section-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 24px 0 16px;
      border-bottom: 1px solid var(--color-border);
      margin-bottom: 24px;
    }}

    .section-title {{
      font-size: 20px;
      font-weight: 700;
    }}

    .category-tabs {{
      display: flex;
      gap: 8px;
    }}

    .category-tab {{
      padding: 8px 20px;
      border-radius: var(--radius-pill);
      font-size: 14px;
      font-weight: 500;
      background: transparent;
      border: 1px solid var(--color-border);
      cursor: pointer;
      transition: all 0.2s;
    }}

    .category-tab:hover {{
      border-color: var(--color-accent);
      color: var(--color-accent);
    }}

    .category-tab.active {{
      background: var(--color-accent);
      color: white;
      border-color: var(--color-accent);
    }}

    .news-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 24px;
    }}

    .news-card {{
      background: var(--color-bg);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-lg);
      overflow: hidden;
      transition: box-shadow 0.2s;
    }}

    .news-card:hover {{
      box-shadow: var(--shadow-card);
    }}

    .news-card-link {{
      text-decoration: none;
      color: inherit;
      display: block;
    }}

    .news-card:hover h3 {{
      color: var(--color-accent);
    }}

    .news-card-img {{
      width: 100%;
      height: 180px;
      object-fit: cover;
    }}

    .news-card-body {{
      padding: 20px;
    }}

    .news-card .category {{
      display: inline-block;
      background: var(--color-bg-warm);
      color: var(--color-text-secondary);
      padding: 4px 10px;
      border-radius: var(--radius-pill);
      font-size: 11px;
      font-weight: 600;
      margin-bottom: 12px;
    }}

    .news-card .category.world {{ background: #e8f4ea; color: #1aae39; }}
    .news-card .category.tech {{ background: #e8f0fd; color: #0075de; }}
    .news-card .category.business {{ background: #fef3e2; color: #dd5b00; }}
    .news-card .category.culture {{ background: #f5e8fd; color: #7c3aed; }}
    .news-card .category.sports {{ background: #fce8e8; color: #ef4444; }}

    .news-card h3 {{
      font-size: 17px;
      font-weight: 600;
      line-height: 1.5;
      margin-bottom: 12px;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }}

    .news-card .excerpt {{
      font-size: 14px;
      color: var(--color-text-secondary);
      line-height: 1.6;
      margin-bottom: 16px;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }}

    .news-card .meta {{
      display: flex;
      align-items: center;
      gap: 16px;
      font-size: 13px;
      color: var(--color-text-muted);
    }}

    .main-with-sidebar {{
      display: grid;
      grid-template-columns: 1fr 320px;
      gap: 48px;
      padding: 48px 0;
    }}

    .sidebar {{
      position: sticky;
      top: 88px;
      height: fit-content;
    }}

    .sidebar-section {{
      background: var(--color-bg);
      border: 1px solid var(--color-border);
      border-radius: var(--radius-lg);
      padding: 24px;
      margin-bottom: 24px;
    }}

    .sidebar-section h2 {{
      font-size: 18px;
      font-weight: 700;
      margin-bottom: 20px;
      padding-bottom: 12px;
      border-bottom: 2px solid var(--color-accent);
      display: inline-block;
    }}

    .trending-list {{
      list-style: none;
    }}

    .trending-item {{
      display: flex;
      gap: 16px;
      padding: 16px 0;
      border-bottom: 1px solid var(--color-border);
    }}

    .trending-item:last-child {{
      border-bottom: none;
      padding-bottom: 0;
    }}

    .trending-num {{
      font-size: 28px;
      font-weight: 700;
      color: var(--color-text-muted);
      line-height: 1;
      min-width: 32px;
    }}

    .trending-item h4 {{
      font-size: 15px;
      font-weight: 600;
      line-height: 1.4;
      margin-bottom: 6px;
    }}

    .trending-item:hover h4 {{
      color: var(--color-accent);
    }}

    .newsletter-box {{
      background: linear-gradient(135deg, #0075de, #005bab);
      border: none;
      color: white;
    }}

    .newsletter-box h2 {{
      border-bottom-color: rgba(255,255,255,0.3);
      color: white;
    }}

    .newsletter-box p {{
      font-size: 14px;
      opacity: 0.9;
      margin-bottom: 16px;
      line-height: 1.6;
    }}

    .newsletter-box input {{
      width: 100%;
      padding: 12px 16px;
      border: none;
      border-radius: var(--radius-md);
      font-size: 14px;
      margin-bottom: 12px;
      font-family: inherit;
    }}

    .newsletter-box button {{
      width: 100%;
      padding: 12px;
      background: white;
      color: var(--color-accent);
      border: none;
      border-radius: var(--radius-md);
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      transition: transform 0.2s;
    }}

    .newsletter-box button:hover {{
      transform: scale(1.02);
    }}

    .footer {{
      background: #1a1a1a;
      color: white;
      padding: 64px 0 32px;
    }}

    .footer-grid {{
      display: grid;
      grid-template-columns: 2fr 1fr 1fr 1fr;
      gap: 48px;
      margin-bottom: 48px;
    }}

    .footer-brand {{
      max-width: 280px;
    }}

    .footer-brand .logo {{
      color: white;
      margin-bottom: 16px;
    }}

    .footer-brand p {{
      font-size: 14px;
      color: rgba(255,255,255,0.7);
      line-height: 1.7;
    }}

    .footer-col h4 {{
      font-size: 14px;
      font-weight: 600;
      margin-bottom: 20px;
      color: white;
    }}

    .footer-col ul {{
      list-style: none;
    }}

    .footer-col li {{
      margin-bottom: 12px;
    }}

    .footer-col a {{
      font-size: 14px;
      color: rgba(255,255,255,0.7);
      text-decoration: none;
      transition: color 0.2s;
    }}

    .footer-col a:hover {{
      color: white;
    }}

    .footer-bottom {{
      padding-top: 32px;
      border-top: 1px solid rgba(255,255,255,0.1);
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 13px;
      color: rgba(255,255,255,0.5);
    }}

    .footer-social {{
      display: flex;
      gap: 16px;
    }}

    .footer-social a {{
      width: 36px;
      height: 36px;
      background: rgba(255,255,255,0.1);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      text-decoration: none;
      transition: background 0.2s;
    }}

    .footer-social a:hover {{
      background: rgba(255,255,255,0.2);
    }}

    @media (max-width: 1024px) {{
      .hero-grid {{
        grid-template-columns: 1fr;
      }}
      .news-grid {{
        grid-template-columns: repeat(2, 1fr);
      }}
      .main-with-sidebar {{
        grid-template-columns: 1fr;
      }}
      .footer-grid {{
        grid-template-columns: repeat(2, 1fr);
      }}
    }}

    @media (max-width: 768px) {{
      .nav, .search-box {{
        display: none;
      }}
      .news-grid {{
        grid-template-columns: 1fr;
      }}
      .footer-grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <!-- 更新信息 -->
  <div class="update-info">
    🔄 内容更新于 {updated_at} · {stats_html}
  </div>

  <!-- Header -->
  <header class="header">
    <div class="container header-inner">
      <a href="#" class="logo">
        <div class="logo-icon">西</div>
        西地新闻
      </a>
      <nav class="nav">
        <a href="#" class="active">首页</a>
        <a href="#">国际</a>
        <a href="#">财经</a>
        <a href="#">科技</a>
        <a href="#">文化</a>
        <a href="#">体育</a>
      </nav>
      <div class="header-actions">
        <div class="search-box">
          <span>🔍</span>
          <input type="text" placeholder="搜索新闻...">
        </div>
        <button class="btn-subscribe">订阅</button>
      </div>
    </div>
  </header>

  <!-- Breaking News -->
  <div class="breaking-news">
    <div class="container">
      <div class="breaking-news-inner">
        <span class="breaking-label">热点</span>
        <div class="ticker">
          <div class="ticker-content">
            <span class="ticker-item">西地新闻为您聚合全球华人关心的热点资讯</span>
            <span class="ticker-item">海外华人社区动态，国际形势深度分析</span>
            <span class="ticker-item">财经、科技、文化、教育 - 多元内容一网打尽</span>
            <span class="ticker-item">西地新闻为您聚合全球华人关心的热点资讯</span>
            <span class="ticker-item">海外华人社区动态，国际形势深度分析</span>
            <span class="ticker-item">财经、科技、文化、教育 - 多元内容一网打尽</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Hero Section -->
  <section class="hero">
    <div class="container">
      <div class="hero-grid">
        <a href="{hero_url}" target="_blank" rel="noopener noreferrer" class="hero-main" style="display:block;color:inherit;text-decoration:none;">
          <img src="https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=800&q=80" alt="Featured">
          <div class="hero-main-overlay">
            <span class="category">热门</span>
            <h1>{hero_title}</h1>
            <p class="meta">来源: {hero_source} · 点击阅读原文</p>
          </div>
        </a>
        <div class="hero-side">
          <a href="{hero2_url}" target="_blank" rel="noopener noreferrer" class="hero-side-item" style="display:block;color:inherit;text-decoration:none;">
            <img src="https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=600&q=80" alt="Tech">
            <div class="hero-side-overlay">
              <span class="category">科技</span>
              <h3>{hero2_title}...</h3>
            </div>
          </a>
          <a href="{hero3_url}" target="_blank" rel="noopener noreferrer" class="hero-side-item" style="display:block;color:inherit;text-decoration:none;">
            <img src="https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=600&q=80" alt="Business">
            <div class="hero-side-overlay">
              <span class="category">财经</span>
              <h3>{hero3_title}...</h3>
            </div>
          </a>
        </div>
      </div>
    </div>
  </section>

  <!-- Main Content -->
  <div class="container">
    <div class="main-with-sidebar">
      <main>
        <div class="section-header">
          <h2 class="section-title">最新资讯</h2>
          <div class="category-tabs">
            <button class="category-tab active">全部</button>
            <button class="category-tab">国际</button>
            <button class="category-tab">财经</button>
            <button class="category-tab">科技</button>
            <button class="category-tab">文化</button>
          </div>
        </div>

        <div class="news-grid">
          {news_cards}
        </div>
      </main>

      <!-- Sidebar -->
      <aside class="sidebar">
        <div class="sidebar-section newsletter-box">
          <h2>📬 订阅通讯</h2>
          <p>每天早上收到最重要的海外华人资讯</p>
          <input type="email" placeholder="输入您的邮箱">
          <button>立即订阅</button>
        </div>

        <div class="sidebar-section">
          <h2>🔥 热门文章</h2>
          <ul class="trending-list">
            {trending_list}
          </ul>
        </div>

        <div class="sidebar-section">
          <h2>📊 新闻来源</h2>
          <div style="display: flex; flex-wrap: wrap; gap: 8px;">
            {source_tags}
          </div>
        </div>
      </aside>
    </div>
  </div>

  <!-- Footer -->
  <footer class="footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-brand">
          <a href="#" class="logo">
            <div class="logo-icon">西</div>
            西地新闻
          </a>
          <p>服务全球华人的新闻资讯平台，聚合多元声音，连接世界华人。</p>
        </div>
        <div class="footer-col">
          <h4>栏目</h4>
          <ul>
            <li><a href="#">国际新闻</a></li>
            <li><a href="#">财经动态</a></li>
            <li><a href="#">科技前沿</a></li>
            <li><a href="#">文化教育</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h4>关于</h4>
          <ul>
            <li><a href="#">关于我们</a></li>
            <li><a href="#">联系我们</a></li>
            <li><a href="#">隐私政策</a></li>
          </ul>
        </div>
        <div class="footer-col">
          <h4>关注</h4>
          <ul>
            <li><a href="#">微信公众号</a></li>
            <li><a href="#">微博</a></li>
            <li><a href="#">Twitter</a></li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom">
        <p>© 2024 西地新闻. 保留所有权利.</p>
      </div>
    </div>
  </footer>

  <script>
    document.querySelectorAll('.category-tab').forEach(tab => {{
      tab.addEventListener('click', function() {{
        document.querySelectorAll('.category-tab').forEach(t => t.classList.remove('active'));
        this.classList.add('active');
      }});
    }});
  </script>
</body>
</html>'''

    # 保存网站
    output_dir = os.path.dirname(__file__)
    output_path = os.path.join(output_dir, 'index.html')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    # 同时保存到项目根目录
    root_output = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'xidi-news-website.html')
    with open(root_output, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return output_path
