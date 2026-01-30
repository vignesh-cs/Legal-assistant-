# setup.py
from setuptools import setup, find_packages

setup(
    name="legal-assistant-sme",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'streamlit>=1.28.0',
        'spacy>=3.7.0',
        'nltk>=3.8.0',
        'PyPDF2>=3.0.0',
        'python-docx>=1.1.0',
        'pandas>=2.1.0',
        'pdfplumber>=0.10.0',
        'googletrans>=4.0.0',
        'langdetect>=1.0.9',
        'sentence-transformers>=2.2.0',
        'plotly>=5.17.0'
    ],
    python_requires='>=3.8',
)