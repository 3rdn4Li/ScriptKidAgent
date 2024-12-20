from setuptools import setup, find_packages

setup(
    name="agentlib",
    version="0.1.3",
    author="Amy Burnett + Wil Gibbs",
    author_email="wfgibbs@asu.edu",
    description="Library to make writing LLM agent components easy",
    long_description=open("readme.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/your_repo_url",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
    ],
    install_requires=[
        "langchain>=0.1.16,<=0.2.16",
        "langchain-openai>=0.1.3,<=0.1.24",
        "langchain-community<=0.2.16",
        "langchain-anthropic<=0.1.23",
        "Jinja2",
        "chromadb<=0.5.5",
        "astunparse<=1.6.3",
        "python-dotenv<=1.0.1",
        "requests",
        "Flask",
        "GitPython<=3.1.43",
        "python-dateutil",
        "redis<=5.0.8",
        "pika<=1.3.2",
        "pyyaml",
        "pymongo",
        "colorlog<=6.8.2",
        "pytest<=8.3.3",
        "litellm<=1.44.28",
    ],
    include_package_data=True,
    package_data={
        "agentlib": ["prompts/*", "static/*"],
    },
    entry_points={
        "console_scripts": [
            "agentviz = agentlib:web_console_main",
        ],
    },
)
