import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys (Set these in .env file)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Use Claude 3 if available, else GPT-4
    USE_CLAUDE = bool(ANTHROPIC_API_KEY)
    
    # Model configurations
    CLAUDE_MODEL = "claude-3-opus-20240229"
    GPT_MODEL = "gpt-3.5-turbo"
    
    # NLP model
    SPACY_MODEL = "en_core_web_sm"
    
    # Risk thresholds
    RISK_THRESHOLDS = {
        'low': 0.3,
        'medium': 0.6,
        'high': 0.8
    }
    
    # Standard clauses for template matching
    STANDARD_CLAUSES = {
        'termination': ['termination', 'cancellation', 'end of agreement'],
        'indemnity': ['indemnify', 'hold harmless', 'indemnification'],
        'liability': ['liability', 'damages', 'compensation'],
        'confidentiality': ['confidential', 'nda', 'non-disclosure'],
        'jurisdiction': ['jurisdiction', 'governing law', 'venue'],
        'arbitration': ['arbitration', 'dispute resolution'],
        'payment': ['payment', 'fee', 'consideration'],
        'deliverables': ['deliverable', 'scope of work', 'services'],
        'ip_rights': ['intellectual property', 'copyright', 'patent']
    }