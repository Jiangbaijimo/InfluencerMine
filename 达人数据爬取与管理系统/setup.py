# -*- coding: utf-8 -*-
"""
达人数据爬取与管理系统 - 安装配置
创建时间: 2025-01-23
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "达人数据爬取与管理系统"

# 读取requirements文件
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="daoren-crawler-system",
    version="1.0.0",
    author="GIMC 23F",
    author_email="",
    description="达人数据爬取与管理系统 - 支持多平台达人数据采集、分析和管理",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="",
    
    packages=find_packages(),
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database :: Database Engines/Servers",
    ],
    
    python_requires=">=3.8",
    
    install_requires=read_requirements(),
    
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ],
        "performance": [
            "ujson>=5.8.0",
            "lxml>=4.9.0",
            "aiohttp>=3.8.0",
        ],
        "analysis": [
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
            "plotly>=5.15.0",
            "scikit-learn>=1.3.0",
            "jieba>=0.42.1",
        ],
        "all": [
            "ujson>=5.8.0",
            "lxml>=4.9.0",
            "aiohttp>=3.8.0",
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
            "plotly>=5.15.0",
            "scikit-learn>=1.3.0",
            "jieba>=0.42.1",
        ]
    },
    
    entry_points={
        "console_scripts": [
            "daoren-crawler=crawler_main:main",
            "daoren-import=import_to_mysql:main",
            "daoren-account=account_manager:main",
            "daoren-scheduler=task_scheduler:main",
        ],
    },
    
    package_data={
        "": [
            "*.yaml",
            "*.yml",
            "*.json",
            "*.sql",
            "*.md",
            "*.txt",
        ],
    },
    
    include_package_data=True,
    
    zip_safe=False,
    
    keywords=[
        "crawler", "spider", "data-mining", "influencer", 
        "social-media", "data-analysis", "mysql", "python"
    ],
    
    project_urls={
        "Bug Reports": "",
        "Source": "",
        "Documentation": "",
    },
)