#!/usr/bin/env python3
"""
西地新闻 - 存储模块
管理新闻数据的存储和读取
"""

import os
import json
import shutil
from datetime import datetime
from typing import List, Dict

STORAGE_DIR = os.path.join(os.path.dirname(__file__))
RAW_DIR = os.path.join(STORAGE_DIR, 'raw')
REWRITTEN_DIR = os.path.join(STORAGE_DIR, 'rewritten')
ARCHIVE_DIR = os.path.join(STORAGE_DIR, 'archive')

def ensure_dirs():
    """确保存储目录存在"""
    for d in [RAW_DIR, REWRITTEN_DIR, ARCHIVE_DIR]:
        os.makedirs(d, exist_ok=True)

def save_raw_news(news_list: List[Dict]) -> str:
    """保存原始爬取的新闻"""
    ensure_dirs()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'raw_news_{timestamp}.json'
    filepath = os.path.join(RAW_DIR, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(news_list, f, ensure_ascii=False, indent=2)

    # 更新 latest
    latest_path = os.path.join(RAW_DIR, 'latest.json')
    with open(latest_path, 'w', encoding='utf-8') as f:
        json.dump(news_list, f, ensure_ascii=False, indent=2)

    return filepath

def save_rewritten_news(news_list: List[Dict]) -> str:
    """保存AI改写后的新闻"""
    ensure_dirs()
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'rewritten_news_{timestamp}.json'
    filepath = os.path.join(REWRITTEN_DIR, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(news_list, f, ensure_ascii=False, indent=2)

    # 更新 latest
    latest_path = os.path.join(REWRITTEN_DIR, 'latest.json')
    with open(latest_path, 'w', encoding='utf-8') as f:
        json.dump(news_list, f, ensure_ascii=False, indent=2)

    return filepath

def get_latest_raw_news() -> List[Dict]:
    """获取最新的原始新闻"""
    latest_path = os.path.join(RAW_DIR, 'latest.json')
    if os.path.exists(latest_path):
        with open(latest_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def get_latest_rewritten_news() -> List[Dict]:
    """获取最新的改写后新闻"""
    latest_path = os.path.join(REWRITTEN_DIR, 'latest.json')
    if os.path.exists(latest_path):
        with open(latest_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def archive_old_news(days: int = 7):
    """归档超过指定天数的旧文件"""
    ensure_dirs()
    cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)

    for source_dir in [RAW_DIR, REWRITTEN_DIR]:
        for filename in os.listdir(source_dir):
            if filename == 'latest.json':
                continue
            filepath = os.path.join(source_dir, filename)
            if os.path.getmtime(filepath) < cutoff:
                # 移动到 archive
                archive_subdir = os.path.join(
                    ARCHIVE_DIR,
                    os.path.basename(source_dir)
                )
                os.makedirs(archive_subdir, exist_ok=True)
                shutil.move(filepath, os.path.join(archive_subdir, filename))
                print(f"  📦 已归档: {filename}")

def export_for_website() -> str:
    """导出网站所需的JSON格式"""
    news_list = get_latest_rewritten_news()

    # 转换为网站格式
    website_data = {
        'updated_at': datetime.now().isoformat(),
        'total_count': len(news_list),
        'news': news_list
    }

    output_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'website'
    )
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, 'news_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(website_data, f, ensure_ascii=False, indent=2)

    return output_path

def get_stats() -> Dict:
    """获取存储统计信息"""
    def count_files(dir_path):
        if os.path.exists(dir_path):
            return len([f for f in os.listdir(dir_path) if f.endswith('.json') and f != 'latest.json'])
        return 0

    raw_count = count_files(RAW_DIR)
    rewritten_count = count_files(REWRITTEN_DIR)

    latest_raw = get_latest_raw_news()
    latest_rewritten = get_latest_rewritten_news()

    return {
        'raw_files': raw_count,
        'rewritten_files': rewritten_count,
        'latest_raw_count': len(latest_raw),
        'latest_rewritten_count': len(latest_rewritten),
        'storage_dir': STORAGE_DIR
    }

if __name__ == '__main__':
    print("=" * 50)
    print("📊 西地新闻 - 存储统计")
    print("=" * 50)
    stats = get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
