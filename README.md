# ⚖️ Legal Assistant for Indian SMEs

## 🏆 Hackathon Solution - GUVI HCL Techathon

### Problem Statement
Small and Medium Enterprises (SMEs) in India struggle with understanding complex legal contracts, identifying risks, and getting affordable legal advice.

### Our Solution
An AI-powered legal assistant that helps SMEs understand contracts, identify risks, and get actionable advice in plain language.

### Key Features
1. **📄 Multi-Format Contract Analysis** - PDF, DOCX, DOC, TXT
2. **🌐 Bilingual Support** - English & Hindi contracts
3. **🎯 Risk Scoring** - High/Medium/Low risk classification
4. **🤖 AI-Powered Analysis** - Plain language explanations
5. **📊 Indian Law Focus** - Compliance with Indian regulations
6. **📑 Template Library** - SME-friendly contract templates
7. **📈 Knowledge Base** - Common issues for Indian SMEs

### Technology Stack
- **Frontend**: Streamlit
- **NLP**: spaCy, NLTK, Sentence Transformers
- **AI/ML**: OpenAI GPT-4 / Claude 3
- **Processing**: PDFplumber, python-docx
- **Visualization**: Plotly, Pandas

### Installation
```bash
# Clone repository
git clone <repository-url>
cd legal-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Download NLP models
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt')"

# Set API keys (optional for full features)
export OPENAI_API_KEY="your-key"  # or set in .env file