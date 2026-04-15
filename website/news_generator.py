#!/usr/bin/env python3
"""
西地新闻 - 网站生成器 v2
生成完整的新闻网站：首页 + 文章详情页
"""

import os
import json
import re
from datetime import datetime
from typing import List, Dict

def clean_text(text: str) -> str:
    """清理文本"""
    if not text:
        return ''
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

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
        return '刚刚'
    except:
        return '刚刚'

def get_category_for_source(source: str) -> str:
    """根据来源映射分类"""
    mapping = {
        '倍可亲': '国际',
        '看中国': '深度',
        '侨报网': '侨报',
        'BBC中文': '国际',
        '美国之音': '国际',
        '华文日报': '日报',
        '华人网': '社区',
        'secretchina': '看中国',
        'qiaobaous': '侨报',
        'voachinese': '美国之音',
    }
    return mapping.get(source, '综合')

def slugify(text: str) -> str:
    """将文本转换为URL友好的slug"""
    text = text[:30]  # 限制长度
    text = re.sub(r'[^\w\s\u4e00-\u9fff]', '', text)  # 保留中文
    text = text.replace(' ', '-')
    return text.lower()

def generate_article_page(article: Dict, index: int, base_url: str = '') -> str:
    """生成单篇文章详情页HTML"""

    title = clean_text(article.get('title', '无标题'))
    content = article.get('rewritten_content', '') or article.get('content', '')
    source = article.get('source', '西地新闻')
    author = article.get('author', '')
    publish_date = article.get('publish_date', '')
    scraped_at = article.get('scraped_at', '')
    time_ago = get_time_ago(scraped_at)
    category = get_category_for_source(source)

    # 处理内容，保留段落格式
    paragraphs = []
    if content:
        # 按换行分割
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 20:  # 只保留有意义的段落
                paragraphs.append(f'<p>{line}</p>')
            elif len(line) > 5:
                paragraphs.append(f'<p class="short">{line}</p>')

    content_html = '\n'.join(paragraphs[:20])  # 最多20段

    # 文章图片
    images = article.get('images', [])
    hero_image = images[0].get('url', 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1200&q=80') if images else 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1200&q=80'

    article_id = f"article-{index + 1}"

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} - 西地新闻</title>
  <meta name="description" content="{title}">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: 'Noto Sans SC', 'Inter', -apple-system, system-ui, sans-serif;
      color: #1a1a1a;
      background: #f8f8f8;
      line-height: 1.8;
    }}
    .header {{
      background: white;
      border-bottom: 1px solid rgba(0,0,0,0.1);
      position: sticky;
      top: 0;
      z-index: 100;
    }}
    .header-inner {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 0 24px;
      height: 64px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .logo {{
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 22px;
      font-weight: 700;
      color: #1a1a1a;
      text-decoration: none;
    }}
    .logo-icon {{
      width: 36px;
      height: 36px;
      background: linear-gradient(135deg, #ff6b6b, #ee5a24);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 18px;
    }}
    .nav {{
      display: flex;
      gap: 32px;
    }}
    .nav a {{
      font-size: 15px;
      font-weight: 500;
      color: #666;
      text-decoration: none;
      transition: color 0.2s;
    }}
    .nav a:hover, .nav a.active {{ color: #0075de; }}
    .back-btn {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
      background: #f0f0f0;
      border-radius: 8px;
      color: #666;
      text-decoration: none;
      font-size: 14px;
      transition: all 0.2s;
    }}
    .back-btn:hover {{ background: #e0e0e0; color: #333; }}

    .article-container {{
      max-width: 800px;
      margin: 40px auto;
      padding: 0 24px;
    }}
    .article-header {{
      background: white;
      border-radius: 16px;
      padding: 40px;
      margin-bottom: 24px;
      box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }}
    .article-category {{
      display: inline-block;
      background: #0075de;
      color: white;
      padding: 4px 16px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 600;
      margin-bottom: 16px;
    }}
    .article-title {{
      font-size: 32px;
      font-weight: 700;
      line-height: 1.4;
      margin-bottom: 20px;
      color: #1a1a1a;
    }}
    .article-meta {{
      display: flex;
      flex-wrap: wrap;
      gap: 24px;
      font-size: 14px;
      color: #888;
      padding-bottom: 20px;
      border-bottom: 1px solid #eee;
    }}
    .article-meta span {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .article-source {{
      color: #0075de;
      font-weight: 500;
    }}

    .article-hero-image {{
      width: 100%;
      height: 400px;
      object-fit: cover;
      border-radius: 12px;
      margin-bottom: 32px;
    }}

    .article-content {{
      background: white;
      border-radius: 16px;
      padding: 40px;
      box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }}
    .article-content p {{
      font-size: 17px;
      line-height: 1.9;
      margin-bottom: 20px;
      color: #333;
    }}
    .article-content p.short {{
      font-size: 14px;
      color: #666;
      margin-bottom: 12px;
    }}
    .article-content h2 {{
      font-size: 24px;
      font-weight: 600;
      margin: 32px 0 16px;
      color: #1a1a1a;
    }}
    .article-content blockquote {{
      border-left: 4px solid #0075de;
      padding: 16px 20px;
      margin: 24px 0;
      background: #f8f9fa;
      border-radius: 0 8px 8px 0;
      font-style: italic;
    }}

    .article-footer {{
      margin-top: 32px;
      padding-top: 24px;
      border-top: 1px solid #eee;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .article-tags {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .article-tag {{
      background: #f0f0f0;
      padding: 4px 12px;
      border-radius: 16px;
      font-size: 12px;
      color: #666;
    }}
    .share-section {{
      display: flex;
      gap: 12px;
    }}
    .share-btn {{
      padding: 8px 16px;
      border: 1px solid #ddd;
      border-radius: 8px;
      font-size: 13px;
      color: #666;
      text-decoration: none;
      transition: all 0.2s;
    }}
    .share-btn:hover {{
      background: #0075de;
      color: white;
      border-color: #0075de;
    }}

    .related-articles {{
      max-width: 800px;
      margin: 40px auto;
      padding: 0 24px;
    }}
    .related-title {{
      font-size: 20px;
      font-weight: 600;
      margin-bottom: 20px;
      color: #1a1a1a;
    }}
    .related-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 20px;
    }}
    .related-card {{
      background: white;
      border-radius: 12px;
      overflow: hidden;
      text-decoration: none;
      color: inherit;
      transition: transform 0.2s, box-shadow 0.2s;
    }}
    .related-card:hover {{
      transform: translateY(-4px);
      box-shadow: 0 8px 24px rgba(0,0,0,0.1);
    }}
    .related-card img {{
      width: 100%;
      height: 120px;
      object-fit: cover;
    }}
    .related-card-content {{
      padding: 16px;
    }}
    .related-card h4 {{
      font-size: 14px;
      font-weight: 600;
      line-height: 1.4;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }}

    .footer {{
      background: #1a1a1a;
      color: white;
      padding: 48px 24px;
      margin-top: 60px;
      text-align: center;
    }}
    .footer p {{
      font-size: 14px;
      color: rgba(255,255,255,0.6);
    }}

    @media (max-width: 768px) {{
      .nav {{ display: none; }}
      .article-title {{ font-size: 24px; }}
      .article-header, .article-content {{ padding: 24px; }}
      .related-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <!-- Header -->
  <header class="header">
    <div class="header-inner">
      <a href="index.html" class="logo">
        <div class="logo-icon">西</div>
        西地新闻
      </a>
      <nav class="nav">
        <a href="index.html" class="active">首页</a>
        <a href="#">国际</a>
        <a href="#">财经</a>
        <a href="#">科技</a>
        <a href="#">文化</a>
      </nav>
      <a href="index.html" class="back-btn">← 返回首页</a>
    </div>
  </header>

  <!-- Article -->
  <main class="article-container">
    <article>
      <header class="article-header">
        <span class="article-category">{category}</span>
        <h1 class="article-title">{title}</h1>
        <div class="article-meta">
          <span class="article-source">📰 {source}</span>
          <span>👤 {author if author else '编辑整理'}</span>
          <span>🕐 {publish_date if publish_date else time_ago}</span>
        </div>
      </header>

      <img src="{hero_image}" alt="{title}" class="article-hero-image">

      <div class="article-content">
        {content_html if content_html else '<p>暂无详细内容</p>'}

        <div class="article-footer">
          <div class="article-tags">
            <span class="article-tag">{source}</span>
            <span class="article-tag">{category}</span>
            <span class="article-tag">海外华人</span>
          </div>
          <div class="share-section">
            <a href="#" class="share-btn" onclick="navigator.share({{title:'{title}',url:location.href}});return false;">分享</a>
          </div>
        </div>
      </div>
    </article>
  </main>

  <!-- Related -->
  <section class="related-articles">
    <h2 class="related-title">相关推荐</h2>
    <div class="related-grid">
      <a href="#" class="related-card">
        <img src="https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=400&q=80" alt="">
        <div class="related-card-content">
          <h4>更多国际新闻资讯</h4>
        </div>
      </a>
      <a href="#" class="related-card">
        <img src="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=400&q=80" alt="">
        <div class="related-card-content">
          <h4>财经动态实时更新</h4>
        </div>
      </a>
      <a href="#" class="related-card">
        <img src="https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=400&q=80" alt="">
        <div class="related-card-content">
          <h4>科技前沿持续关注</h4>
        </div>
      </a>
    </div>
  </section>

  <!-- Footer -->
  <footer class="footer">
    <p>© 2024 西地新闻 - 服务全球华人社区</p>
  </footer>
</body>
</html>'''

    return html


def generate_homepage(articles: List[Dict]) -> str:
    """生成首页HTML"""

    updated_at = datetime.now().strftime('%Y年%m月%d日 %H:%M')

    # 分类统计
    categories = {}
    for article in articles:
        cat = get_category_for_source(article.get('source', ''))
        categories[cat] = categories.get(cat, 0) + 1

    # 生成新闻卡片
    def get_article_image(article: Dict) -> str:
        images = article.get('images', [])
        if images:
            return images[0].get('url', 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=600&q=80')
        return 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=600&q=80'

    news_cards_html = ''
    for i, article in enumerate(articles):
        title = clean_text(article.get('title', '无标题'))
        source = article.get('source', '西地新闻')
        category = get_category_for_source(source)
        time_ago = get_time_ago(article.get('scraped_at', ''))
        article_url = f'article-{i + 1}.html'
        img_url = get_article_image(article)

        news_cards_html += f'''
        <article class="news-card">
          <a href="{article_url}" class="card-link">
            <div class="card-image">
              <img src="{img_url}" alt="{title}" loading="lazy">
              <span class="card-category">{category}</span>
            </div>
            <div class="card-content">
              <h3 class="card-title">{title}</h3>
              <div class="card-meta">
                <span class="card-source">📰 {source}</span>
                <span class="card-time">🕐 {time_ago}</span>
              </div>
            </div>
          </a>
        </article>'''

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>西地新闻 - 海外华人新闻门户</title>
  <meta name="description" content="西地新闻是服务全球华人的新闻平台，聚合海外华人关心的国际、财经、科技、文化等资讯。">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      font-family: 'Noto Sans SC', 'Inter', -apple-system, system-ui, sans-serif;
      color: #1a1a1a;
      background: #f5f5f5;
      line-height: 1.6;
    }}
    .update-bar {{
      background: #fff3e0;
      padding: 8px 24px;
      text-align: center;
      font-size: 13px;
      color: #666;
    }}

    .header {{
      background: white;
      border-bottom: 1px solid rgba(0,0,0,0.08);
      position: sticky;
      top: 0;
      z-index: 100;
    }}
    .header-inner {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 0 24px;
      height: 64px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}
    .logo {{
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 22px;
      font-weight: 700;
      color: #1a1a1a;
      text-decoration: none;
    }}
    .logo-icon {{
      width: 36px;
      height: 36px;
      background: linear-gradient(135deg, #ff6b6b, #ee5a24);
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 18px;
    }}
    .nav {{
      display: flex;
      gap: 32px;
    }}
    .nav a {{
      font-size: 15px;
      font-weight: 500;
      color: #666;
      text-decoration: none;
      transition: color 0.2s;
    }}
    .nav a:hover {{ color: #0075de; }}
    .nav a.active {{ color: #0075de; }}

    .hero {{
      max-width: 1200px;
      margin: 32px auto;
      padding: 0 24px;
    }}
    .hero-grid {{
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 24px;
    }}
    .hero-main {{
      position: relative;
      border-radius: 16px;
      overflow: hidden;
      height: 420px;
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
      background: linear-gradient(transparent, rgba(0,0,0,0.85));
      color: white;
    }}
    .hero-main-overlay .category {{
      display: inline-block;
      background: #0075de;
      padding: 4px 12px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 600;
      margin-bottom: 12px;
    }}
    .hero-main-overlay h1 {{
      font-size: 26px;
      font-weight: 700;
      line-height: 1.3;
      margin-bottom: 12px;
    }}
    .hero-main-overlay a {{
      color: white;
      text-decoration: none;
    }}
    .hero-main-overlay .meta {{
      font-size: 13px;
      color: rgba(255,255,255,0.8);
    }}

    .hero-side {{
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}
    .hero-side-item {{
      position: relative;
      border-radius: 12px;
      overflow: hidden;
      flex: 1;
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
    .hero-side-overlay a {{
      color: white;
      text-decoration: none;
    }}
    .hero-side-overlay h3 {{
      font-size: 15px;
      font-weight: 600;
      line-height: 1.4;
    }}
    .hero-side-overlay .category {{
      display: inline-block;
      background: #2a9d99;
      padding: 3px 10px;
      border-radius: 12px;
      font-size: 11px;
      margin-bottom: 8px;
    }}

    .main-content {{
      max-width: 1200px;
      margin: 0 auto;
      padding: 32px 24px;
    }}
    .section-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
    }}
    .section-title {{
      font-size: 22px;
      font-weight: 700;
    }}
    .category-tabs {{
      display: flex;
      gap: 8px;
    }}
    .category-tab {{
      padding: 6px 16px;
      border-radius: 20px;
      font-size: 13px;
      border: 1px solid #ddd;
      background: white;
      cursor: pointer;
      transition: all 0.2s;
    }}
    .category-tab:hover {{
      border-color: #0075de;
      color: #0075de;
    }}
    .category-tab.active {{
      background: #0075de;
      color: white;
      border-color: #0075de;
    }}

    .news-grid {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 24px;
    }}
    .news-card {{
      background: white;
      border-radius: 16px;
      overflow: hidden;
      transition: transform 0.2s, box-shadow 0.2s;
    }}
    .news-card:hover {{
      transform: translateY(-4px);
      box-shadow: 0 12px 32px rgba(0,0,0,0.1);
    }}
    .card-link {{
      text-decoration: none;
      color: inherit;
      display: block;
    }}
    .card-image {{
      position: relative;
      height: 180px;
      overflow: hidden;
    }}
    .card-image img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      transition: transform 0.3s;
    }}
    .news-card:hover .card-image img {{
      transform: scale(1.05);
    }}
    .card-category {{
      position: absolute;
      top: 12px;
      left: 12px;
      background: #0075de;
      color: white;
      padding: 4px 10px;
      border-radius: 12px;
      font-size: 11px;
      font-weight: 600;
    }}
    .card-content {{
      padding: 20px;
    }}
    .card-title {{
      font-size: 16px;
      font-weight: 600;
      line-height: 1.5;
      margin-bottom: 12px;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }}
    .card-meta {{
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      color: #999;
    }}
    .card-source {{
      color: #0075de;
      font-weight: 500;
    }}

    .footer {{
      background: #1a1a1a;
      color: white;
      padding: 48px 24px;
      margin-top: 60px;
      text-align: center;
    }}
    .footer-grid {{
      max-width: 1200px;
      margin: 0 auto;
      display: grid;
      grid-template-columns: 2fr 1fr 1fr 1fr;
      gap: 48px;
      text-align: left;
      margin-bottom: 32px;
    }}
    .footer-brand p {{
      font-size: 14px;
      color: rgba(255,255,255,0.6);
      margin-top: 12px;
      line-height: 1.7;
    }}
    .footer-col h4 {{
      font-size: 14px;
      font-weight: 600;
      margin-bottom: 16px;
    }}
    .footer-col ul {{
      list-style: none;
    }}
    .footer-col li {{
      margin-bottom: 10px;
    }}
    .footer-col a {{
      font-size: 14px;
      color: rgba(255,255,255,0.6);
      text-decoration: none;
      transition: color 0.2s;
    }}
    .footer-col a:hover {{ color: white; }}
    .footer-bottom {{
      max-width: 1200px;
      margin: 0 auto;
      padding-top: 24px;
      border-top: 1px solid rgba(255,255,255,0.1);
      font-size: 13px;
      color: rgba(255,255,255,0.4);
    }}

    @media (max-width: 1024px) {{
      .hero-grid {{ grid-template-columns: 1fr; }}
      .news-grid {{ grid-template-columns: repeat(2, 1fr); }}
      .footer-grid {{ grid-template-columns: repeat(2, 1fr); }}
    }}
    @media (max-width: 768px) {{
      .nav {{ display: none; }}
      .news-grid {{ grid-template-columns: 1fr; }}
      .hero-grid {{ grid-template-columns: 1fr; }}
      .hero-main {{ height: 300px; }}
      .hero-side {{ flex-direction: row; }}
      .hero-side-item {{ height: 160px; }}
      .footer-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <!-- Update Bar -->
  <div class="update-bar">
    🔄 内容更新时间: {updated_at} · 共 {len(articles)} 篇精彩资讯
  </div>

  <!-- Header -->
  <header class="header">
    <div class="header-inner">
      <a href="index.html" class="logo">
        <div class="logo-icon">西</div>
        西地新闻
      </a>
      <nav class="nav">
        <a href="index.html" class="active">首页</a>
        <a href="#">国际</a>
        <a href="#">财经</a>
        <a href="#">科技</a>
        <a href="#">文化</a>
        <a href="#">体育</a>
      </nav>
    </div>
  </header>

  <!-- Hero -->
  <section class="hero">
    <div class="hero-grid">
      <div class="hero-main">
        <a href="article-1.html">
          <img src="{get_article_image(articles[0]) if articles else 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800&q=80'}" alt="">
          <div class="hero-main-overlay">
            <span class="category">{get_category_for_source(articles[0].get('source','')) if articles else '热门'}</span>
            <h1>{clean_text(articles[0].get('title','无标题')) if articles else '西地新闻'}</h1>
            <p class="meta">来源: {articles[0].get('source','西地新闻') if articles else ''} · 点击阅读</p>
          </div>
        </a>
      </div>
      <div class="hero-side">
        <div class="hero-side-item">
          <a href="article-2.html">
            <img src="{get_article_image(articles[1]) if len(articles) > 1 else 'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=600&q=80'}" alt="">
            <div class="hero-side-overlay">
              <span class="category">{get_category_for_source(articles[1].get('source','')) if len(articles) > 1 else '财经'}</span>
              <h3>{clean_text(articles[1].get('title',''))[:40] if len(articles) > 1 else '财经资讯'}</h3>
            </div>
          </a>
        </div>
        <div class="hero-side-item">
          <a href="article-3.html">
            <img src="{get_article_image(articles[2]) if len(articles) > 2 else 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=600&q=80'}" alt="">
            <div class="hero-side-overlay">
              <span class="category">{get_category_for_source(articles[2].get('source','')) if len(articles) > 2 else '科技'}</span>
              <h3>{clean_text(articles[2].get('title',''))[:40] if len(articles) > 2 else '科技前沿'}</h3>
            </div>
          </a>
        </div>
      </div>
    </div>
  </section>

  <!-- Main Content -->
  <main class="main-content">
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
      {news_cards_html}
    </div>
  </main>

  <!-- Footer -->
  <footer class="footer">
    <div class="footer-grid">
      <div class="footer-brand">
        <a href="index.html" class="logo" style="color:white;">
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

    return html


def generate_website(articles: List[Dict], output_dir: str = None) -> str:
    """生成完整的网站"""

    if output_dir is None:
        output_dir = os.path.dirname(__file__)

    os.makedirs(output_dir, exist_ok=True)

    print(f"📰 生成网站，共 {len(articles)} 篇文章...")

    # 1. 生成首页
    homepage_html = generate_homepage(articles)
    homepage_path = os.path.join(output_dir, 'index.html')
    with open(homepage_path, 'w', encoding='utf-8') as f:
        f.write(homepage_html)
    print(f"  ✓ 首页已生成: index.html")

    # 2. 生成文章详情页
    articles_dir = os.path.join(output_dir, 'articles')
    os.makedirs(articles_dir, exist_ok=True)

    for i, article in enumerate(articles):
        article_html = generate_article_page(article, i)
        article_filename = f'article-{i + 1}.html'
        article_path = os.path.join(output_dir, article_filename)
        with open(article_path, 'w', encoding='utf-8') as f:
            f.write(article_html)

    print(f"  ✓ {len(articles)} 篇文章详情页已生成")

    # 3. 保存文章数据
    articles_data = {
        'updated_at': datetime.now().isoformat(),
        'total_count': len(articles),
        'articles': articles
    }
    data_path = os.path.join(output_dir, 'articles_data.json')
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(articles_data, f, ensure_ascii=False, indent=2)

    # 复制到根目录
    root_output = os.path.dirname(os.path.dirname(__file__))
    root_website = os.path.join(root_output, 'website_output')
    os.makedirs(root_website, exist_ok=True)

    import shutil
    for item in ['index.html'] + [f'article-{i+1}.html' for i in range(len(articles))]:
        src = os.path.join(output_dir, item)
        if os.path.exists(src):
            shutil.copy(src, root_website)

    print(f"\n✅ 网站已生成: {root_website}")
    return root_website
