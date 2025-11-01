from setuptools import setup, find_packages

setup(
    name="axiom-ai",
    version="1.0.0",
    author="Your Name", # You can change this
    author_email="your.email@example.com", # And this
    description="A sovereign, professional-grade RAG (Retrieval-Augmented Generation) system.",
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/YOUR_USERNAME/axiom", # Replace with your repo URL
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
    install_requires=[
        "nicegui",
        "openai<2.0.0",
        "pypdf",
        "sentence-transformers==2.7.0",
        "chromadb<0.5",
        "tiktoken",
        "chardet",
        "setuptools",
        "numpy<2.0",
        "PyYAML",
        "scikit-learn" 
    ],
    extras_require={
        "test": ["pytest"],
    },
)

