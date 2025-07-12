#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Docker启动脚本
用于在Docker容器中启动PikPak下载服务
"""

import os
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def start_service():
    """启动服务"""
    try:
        import uvicorn
        from main import app
        
        # 从环境变量获取主机和端口配置
        host = os.getenv("SERVER_HOST", "0.0.0.0")
        port = int(os.getenv("SERVER_PORT", "8000"))
        
        logger.info(f"启动PikPak下载服务: http://{host}:{port}")
        logger.info(f"API文档地址: http://localhost:{port}/docs")
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info"
        )
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        raise

def main():
    """主函数"""
    logger.info("PikPak下载服务启动中...")
    start_service()

if __name__ == "__main__":
    main()