import pdfplumber
from docx import Document
import spacy
from typing import Dict, List, Any, Tuple
import re
from langdetect import detect
import nltk
from nltk.tokenize import sent_tokenize

class DocumentProcessor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        nltk.download('punkt', quiet=True)
        
    def extract_text(self, file_path: str, file_type: str) -> str:
        """Extract text from various document formats"""
        text = ""
        
        if file_type == "pdf":
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
                    
        elif file_type in ["docx", "doc"]:
            doc = Document(file_path)
            for para in doc.paragraphs:
                text += para.text + "\n"
                
        elif file_type == "txt":
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                
        return text.strip()
    
    def detect_language(self, text: str) -> str:
        """Detect language of the contract"""
        try:
            sample = text[:500] if len(text) > 500 else text
            return detect(sample)
        except:
            # Check for Hindi characters
            hindi_chars = set('अआइईउऊऋएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह')
            if any(char in hindi_chars for char in sample):
                return "hi"
            return "en"
    
    def extract_clauses(self, text: str) -> Dict[str, str]:
        """Extract clauses from contract text"""
        clauses = {}
        
        # Clean text
        text = re.sub(r'\s+', ' ', text)
        
        # Pattern to find numbered clauses
        patterns = [
            r'(?i)(?:clause|section|article|खंड|अनुच्छेद)\s+(\d+(?:\.\d+)*)[\.\s]+([^\n]+(?:\n(?!\s*(?:clause|section|article|खंड|अनुच्छेद)\s+\d)[^\n]*)*)',
            r'(?i)(\d+(?:\.\d+)*)\.\s+([^\n]+(?:\n(?!\s*\d+\.)[^\n]*)*)',
            r'(?i)(?:प्रावधान|धारा)\s+(\d+)[\s\.]+([^\n]+)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            for match in matches:
                clause_num = match.group(1)
                clause_text = match.group(2).strip()
                if len(clause_text) > 20:  # Minimum meaningful length
                    clauses[f"Clause {clause_num}"] = clause_text
        
        # If no numbered clauses found, split by sentences
        if not clauses:
            sentences = sent_tokenize(text)
            current_clause = []
            clause_num = 1
            
            for sentence in sentences:
                if len(sentence) > 50:  # Start new clause
                    if current_clause:
                        clauses[f"Paragraph {clause_num}"] = ' '.join(current_clause)
                        clause_num += 1
                        current_clause = []
                current_clause.append(sentence)
            
            if current_clause:
                clauses[f"Paragraph {clause_num}"] = ' '.join(current_clause)
                    
        return clauses
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities using spaCy"""
        # Only process if text is primarily English
        if self.detect_language(text) == 'hi':
            # For Hindi, use regex patterns only
            entities = {
                'PARTIES': [],
                'DATES': [],
                'MONEY': [],
                'ORG': [],
                'LAW': [],
                'LOC': []
            }
        else:
            # English text - use spaCy
            doc = self.nlp(text)
            
            entities = {
                'PARTIES': [],
                'DATES': [],
                'MONEY': [],
                'ORG': [],
                'LAW': [],
                'LOC': []
            }
            
            for ent in doc.ents:
                if ent.label_ in entities:
                    entities[ent.label_].append(ent.text)
        
        # Common regex patterns for both languages
        date_pattern = r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}'
        money_pattern = r'₹\s*\d+(?:,\d+)*(?:\.\d+)?|\$\s*\d+(?:,\d+)*(?:\.\d+)?|INR\s*\d+(?:,\d+)*(?:\.\d+)?|रुपये\s*\d+(?:,\d+)*(?:\.\d+)?'
        
        dates = re.findall(date_pattern, text, re.IGNORECASE)
        money = re.findall(money_pattern, text)
        
        # Extract parties (simple pattern for Hindi/English)
        party_patterns = [
            r'between\s+([^,]+?)\s+and\s+([^,\.]+)',
            r'पक्ष\s*:\s*([^\n]+)',
            r'पार्टी\s+(\d+)[\s:]+([^\n]+)'
        ]
        
        for pattern in party_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    for party in match:
                        entities['PARTIES'].append(party.strip())
                else:
                    entities['PARTIES'].append(match.strip())
        
        entities['DATES'].extend(dates)
        entities['MONEY'].extend(money)
        
        # Remove duplicates and empty strings
        for key in entities:
            entities[key] = list(set([e for e in entities[key] if e.strip()]))
            
        return entities
    
    def preprocess_for_llm(self, text: str) -> str:
        """Preprocess text for LLM analysis"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,;:!?()-₹$%/\n]', ' ', text)
        
        return text.strip()