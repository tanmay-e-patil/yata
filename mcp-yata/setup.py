from setuptools import setup, find_packages

setup(
    name="mcp-yata",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "mcp>=1.0.0",
        "httpx>=0.25.0",
        "authlib>=1.2.0",
        "pydantic>=2.5.0",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.8",
    author="Yata Team",
    description="MCP Server for Yata Todo Application",
)