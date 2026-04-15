#!/usr/bin/env python3
"""
Vercel Cron API - 定时更新新闻
每天早上8点自动运行
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def handler(event, context):
    """Vercel Serverless Function handler"""
    from run import run_full_pipeline

    try:
        result = run_full_pipeline()
        return {
            'statusCode': 200,
            'body': 'OK' if result else 'Failed'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }

if __name__ == '__main__':
    handler(None, None)
