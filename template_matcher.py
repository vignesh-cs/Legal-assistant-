import difflib
from typing import Dict, List, Tuple
import json
import os

class TemplateMatcher:
    def __init__(self, templates_dir: str = "templates"):
        self.templates_dir = templates_dir
        self.templates = self.load_templates()
        
    def load_templates(self) -> Dict[str, Dict]:
        """Load standard contract templates"""
        templates = {}
        
        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.txt'):
                contract_type = filename.replace('.txt', '').replace('_', ' ').title()
                with open(os.path.join(self.templates_dir, filename), 'r') as f:
                    content = f.read()
                    templates[contract_type] = self.parse_template(content)
                    
        return templates
    
    def parse_template(self, content: str) -> Dict:
        """Parse template into structured format"""
        sections = {}
        current_section = None
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('##'):
                current_section = line[2:].strip()
                sections[current_section] = []
            elif current_section and line:
                sections[current_section].append(line)
                
        return sections
    
    def match_contract_type(self, text: str) -> Tuple[str, float]:
        """Match contract to template type"""
        contract_types = list(self.templates.keys())
        
        # Simple keyword matching
        type_scores = {}
        for ctype in contract_types:
            score = 0
            ctype_lower = ctype.lower()
            
            if "employment" in ctype_lower and any(word in text.lower() for word in ['employee', 'employer', 'salary', 'termination']):
                score += 0.8
            if "vendor" in ctype_lower and any(word in text.lower() for word in ['vendor', 'supplier', 'purchase', 'goods']):
                score += 0.8
            if "lease" in ctype_lower and any(word in text.lower() for word in ['lease', 'rent', 'premises', 'landlord']):
                score += 0.8
            if "partnership" in ctype_lower and any(word in text.lower() for word in ['partner', 'partnership', 'profit sharing']):
                score += 0.8
            if "service" in ctype_lower and any(word in text.lower() for word in ['services', 'scope of work', 'deliverables']):
                score += 0.8
                
            type_scores[ctype] = score
            
        best_type = max(type_scores, key=type_scores.get)
        return best_type, type_scores[best_type]
    
    def compare_with_template(self, text: str, contract_type: str) -> List[Dict]:
        """Compare contract with standard template"""
        if contract_type not in self.templates:
            return []
        
        comparisons = []
        template = self.templates[contract_type]
        
        for section, clauses in template.items():
            for template_clause in clauses:
                # Simple similarity check
                similarity = difflib.SequenceMatcher(
                    None, 
                    template_clause.lower(), 
                    text.lower()
                ).ratio()
                
                comparisons.append({
                    'section': section,
                    'template_clause': template_clause,
                    'similarity': similarity,
                    'status': 'Present' if similarity > 0.7 else 'Missing'
                })
                
        return comparisons