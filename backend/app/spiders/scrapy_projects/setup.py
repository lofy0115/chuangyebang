from setuptools import setup, find_packages

setup(
    name="scrapy_projects",
    version="1.0.0",
    description="Scrapy爬虫项目集合 - 淘宝、京东、微博等平台爬虫",
    author="",
    author_email="",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "scrapy>=2.0.0",
        "playwright>=1.0.0",
        "pyyaml>=5.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=21.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "taobao-spider=ecommerce.spiders.taobao_spider:main",
            "jd-spider=ecommerce.spiders.jd_spider:main",
            "weibo-spider=social.spiders.weibo_spider:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)