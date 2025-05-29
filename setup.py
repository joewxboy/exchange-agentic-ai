from setuptools import setup, find_packages

setup(
    name="openhorizon_client",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.8.0",
        "python-dotenv>=0.19.0",
    ],
    python_requires=">=3.7",
    author="Open Horizon Team",
    author_email="openhorizon@example.com",
    description="A Python client for the Open Horizon Exchange API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/open-horizon/exchange-api-client",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
) 