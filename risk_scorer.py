import re
from typing import Dict, List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

class RiskScorer:
    def __init__(self):
        # Remove sentence_transformers dependency
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
        self.risk_keywords = {
            'high': [
                'indemnify', 'hold harmless', 'unlimited liability', 
                'penalty', 'liquidated damages', 'irrevocable',
                'non-compete', 'non-solicit', 'assignment without consent',
                'sole discretion', 'unilateral', 'automatic renewal',
                'confidential information forever', 'proprietary information',
                'joint and several liability', 'consequential damages',
                'punitive damages', 'waiver of rights'
            ],
            'medium': [
                'termination for convenience', 'governing law',
                'jurisdiction', 'arbitration', 'force majeure',
                'limitation of liability', 'warranty', 'representation',
                'insurance', 'subcontract', 'change of control',
                'intellectual property rights', 'survival'
            ],
            'low': [
                'notice', 'amendment', 'severability',
                'entire agreement', 'counterparts', 'headings',
                'relationship of parties', 'publicity', 'assignment'
            ]
        }
        
        # Hindi keywords for risk detection
        self.hindi_risk_keywords = {
            'high': [
                'क्षतिपूर्ति', 'असीमित दायित्व', 'जुर्माना',
                'अपरिवर्तनीय', 'गैर-प्रतिस्पर्धा', 'एकतरफा',
                'स्वचालित नवीनीकरण', 'संयुक्त दायित्व'
            ],
            'medium': [
                'समाप्ति', 'क्षेत्राधिकार', 'मध्यस्थता',
                'अप्रत्याशित घटना', 'दायित्व सीमा', 'वारंटी'
            ]
        }
        
        self.indian_specific_risks = [
            'foreign jurisdiction', 'foreign law', 'overseas jurisdiction',
            'dispute resolution outside india', 'non-indian arbitration',
            'payment in foreign currency', 'offshore account',
            'lcia', 'siac', 'hkiac', 'icc arbitration',
            'new york law', 'english law', 'singapore law'
        ]
        
        self.indian_compliance_requirements = [
            'indian contract act', 'companies act', 'gst',
            'income tax act', 'arbitration and conciliation act',
            'consumer protection act', 'competition act'
        ]
    
    def detect_language(self, text: str) -> str:
        """Simple language detection"""
        hindi_chars = set('अआइईउऊऋएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह')
        if any(char in hindi_chars for char in text[:1000]):
            return "hi"
        return "en"
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using TF-IDF"""
        try:
            # Fit and transform the texts
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            
            # Calculate cosine similarity
            similarity = (tfidf_matrix * tfidf_matrix.T).toarray()[0, 1]
            return similarity
        except:
            # Fallback to simple word overlap
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            if not words1 or not words2:
                return 0.0
            return len(words1.intersection(words2)) / len(words1.union(words2))
    
    def score_clause(self, clause_text: str) -> Tuple[float, List[str], str]:
        """Score individual clause for risk"""
        clause_lower = clause_text.lower()
        language = self.detect_language(clause_text)
        
        risk_score = 0.0
        flags = []
        clause_type = "General Clause"
        
        # Check risk keywords based on language
        if language == "hi":
            # Hindi text - check Hindi keywords
            for level, keywords in self.hindi_risk_keywords.items():
                count = sum(1 for word in keywords if word in clause_text)
                if level == 'high':
                    risk_score += count * 0.15
                elif level == 'medium':
                    risk_score += count * 0.08
        else:
            # English text - check English keywords
            for level, keywords in self.risk_keywords.items():
                count = sum(1 for word in keywords if word in clause_lower)
                if level == 'high':
                    risk_score += count * 0.12
                elif level == 'medium':
                    risk_score += count * 0.06
                elif level == 'low':
                    risk_score += count * 0.02
        
        # Check for Indian-specific risks
        for risk in self.indian_specific_risks:
            if risk in clause_lower:
                risk_score = min(risk_score + 0.25, 1.0)
                flags.append(f"⚠️ Indian jurisdiction risk: '{risk}'")
        
        # Check for one-sided language patterns
        one_sided_patterns = [
            r'sole\s+discretion', r'exclusive\s+right',
            r'unilateral\s+(?:right|termination|amendment)',
            r'at its\s+(?:option|discretion)', r'may in its discretion'
        ]
        
        for pattern in one_sided_patterns:
            if re.search(pattern, clause_lower, re.IGNORECASE):
                risk_score = min(risk_score + 0.15, 1.0)
                flags.append("⚖️ One-sided language detected")
        
        # Check for ambiguous terms
        ambiguous_terms = ['reasonable', 'best efforts', 'as soon as practicable', 
                          'commercially reasonable', 'substantially']
        ambiguous_count = 0
        for term in ambiguous_terms:
            if term in clause_lower:
                ambiguous_count += 1
        
        if ambiguous_count > 0:
            risk_score = min(risk_score + (ambiguous_count * 0.08), 1.0)
            flags.append(f"❓ Contains {ambiguous_count} ambiguous term(s)")
        
        # Check for time pressure (short deadlines)
        time_patterns = [
            r'within\s+(\d+)\s+(?:hour|day)s?\b',
            r'(\d+)\s+(?:hour|day)s?\s+notice',
            r'immediately', r'forthwith', r'without delay'
        ]
        
        for pattern in time_patterns:
            matches = re.findall(pattern, clause_lower)
            for match in matches:
                if isinstance(match, str) and match.isdigit():
                    days = int(match)
                    if days < 7:  # Less than a week is high risk
                        risk_score = min(risk_score + 0.1, 1.0)
                        flags.append(f"⏰ Very short deadline: {days} days")
        
        # Identify clause type
        clause_type = self.identify_clause_type(clause_text, language)
        
        # Special scoring for high-risk clause types
        if clause_type in ["Indemnity Clause", "Liability Clause"]:
            risk_score = min(risk_score * 1.3, 1.0)
        
        # Cap score at 1.0
        risk_score = min(risk_score, 1.0)
        
        return risk_score, flags, clause_type
    
    def identify_clause_type(self, clause_text: str, language: str = "en") -> str:
        """Identify type of clause"""
        text_lower = clause_text.lower()
        
        # Define patterns for clause identification
        patterns = {
            "Indemnity Clause": [
                'indemnif', 'hold harmless', 'defend', 'क्षतिपूर्ति',
                'protect from loss', 'make whole'
            ],
            "Termination Clause": [
                'terminat', 'expir', 'end of agreement', 'समाप्ति',
                'cancellation', 'wind up'
            ],
            "Jurisdiction Clause": [
                'jurisdiction', 'governing law', 'venue', 'क्षेत्राधिकार',
                'applicable law', 'न्यायालय'
            ],
            "Arbitration Clause": [
                'arbitration', 'dispute resolution', 'मध्यस्थता',
                'mediation', 'conciliation'
            ],
            "Confidentiality Clause": [
                'confidential', 'nda', 'non-disclosure', 'गोपनीयता',
                'proprietary information', 'trade secret'
            ],
            "Payment Clause": [
                'payment', 'fee', 'price', 'consideration', 'भुगतान',
                'compensation', 'remuneration'
            ],
            "IP Rights Clause": [
                'intellectual property', 'ip', 'copyright', 'patent',
                'बौद्धिक संपदा', 'trademark', 'invention'
            ],
            "Warranty Clause": [
                'warrant', 'represent', 'guarantee', 'वारंटी',
                'assure', 'certify'
            ],
            "Liability Clause": [
                'liability', 'damage', 'compensation', 'दायित्व',
                'loss', 'claim'
            ],
            "Force Majeure Clause": [
                'force majeure', 'act of god', 'अप्रत्याशित घटना',
                'unforeseen circumstances'
            ]
        }
        
        # Check each pattern
        for clause_type, keywords in patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return clause_type
        
        return "General Clause"
    
    def get_risk_level(self, score: float) -> str:
        """Convert score to risk level with colors"""
        if score >= 0.7:
            return "High 🔴"
        elif score >= 0.4:
            return "Medium 🟡"
        else:
            return "Low 🟢"
    
    def calculate_composite_score(self, clause_scores: List[float]) -> float:
        """Calculate overall contract risk score"""
        if not clause_scores:
            return 0.0
        
        # Weight higher-risk clauses more heavily
        weighted_scores = []
        for score in clause_scores:
            if score >= 0.7:
                weighted_scores.append(score * 1.5)
            elif score >= 0.4:
                weighted_scores.append(score * 1.2)
            else:
                weighted_scores.append(score)
        
        composite = sum(weighted_scores) / len(weighted_scores)
        return min(composite, 1.0)