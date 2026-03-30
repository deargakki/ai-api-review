from setuptools import setup, find_packages

setup(
    name="api-review-agent",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "langchain>=0.1.0",
        "openai>=1.0.0",
        "PyGithub>=2.1.0",
        "atlassian-python-api>=3.40.0",
        "pyyaml>=6.0",
        "jinja2>=3.1.0",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.9",
)
