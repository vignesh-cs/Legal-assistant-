# legal_analyzer.py - Updated without googletrans
import openai
from typing import Dict, List, Any, Optional, Tuple
import json
from config import Config
import time

class LegalAnalyzer:
    def __init__(self, config: Config):
        self.config = config
        
        # Always use OpenAI since you have that key
        if config.OPENAI_API_KEY:
            openai.api_key = config.OPENAI_API_KEY
            self.use_openai = True
        else:
            self.use_openai = False
            print("Warning: No OpenAI API key found. Using basic analysis only.")
    
    def translate_if_needed(self, text: str, source_lang: str = "auto") -> str:
        """Simple translation without googletrans"""
        if source_lang == "hi":
            # For hackathon demo, we'll just return the text with a note
            # You can implement simple keyword translation if needed
            return f"[Hindi Text Detected]\n{text[:500]}..."
        return text
    
    def analyze_clause(self, clause_text: str, clause_type: str, is_hindi: bool = False) -> Dict[str, Any]:
        """Analyze a single clause using OpenAI"""
        
        # Translate if Hindi
        if is_hindi:
            clause_text_en = self.translate_if_needed(clause_text, "hi")
        else:
            clause_text_en = clause_text
        
        # For demo, limit text length
        if len(clause_text_en) > 2000:
            clause_text_en = clause_text_en[:2000] + "...[truncated]"
        
        prompt = f"""As a legal advisor for Indian SMEs, analyze this {clause_type}:

"{clause_text_en}"

Provide analysis in this EXACT JSON format:
{{
    "plain_language_explanation": "Simple explanation in business English",
    "potential_risks": ["Risk 1", "Risk 2", "Risk 3"],
    "unfair_terms": ["Term 1", "Term 2"],
    "suggested_alternative": "SME-friendly alternative wording",
    "compliance_notes": "Notes on Indian law compliance",
    "negotiation_tips": ["Tip 1", "Tip 2", "Tip 3"],
    "severity": "High/Medium/Low"
}}

Keep it practical and actionable for business owners."""
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                if self.use_openai:
                    response = openai.ChatCompletion.create(
                        model=self.config.GPT_MODEL,
                        messages=[
                            {"role": "system", "content": "You are a helpful legal assistant for Indian SMEs. Provide clear, practical advice in simple English. Always return valid JSON."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.1,
                        max_tokens=800
                    )
                    result_text = response.choices[0].message.content
                    
                    # Extract JSON from response
                    result_text = result_text.strip()
                    
                    # Find JSON in response
                    json_start = result_text.find('{')
                    json_end = result_text.rfind('}') + 1
                    
                    if json_start != -1 and json_end != 0:
                        json_str = result_text[json_start:json_end]
                        result = json.loads(json_str)
                    else:
                        # If no JSON found, create from text
                        result = self._parse_text_response(result_text)
                    
                    # Add language note if original was Hindi
                    if is_hindi:
                        result["original_language"] = "Hindi"
                        result["note"] = "Analysis based on translated text"
                    
                    return result
                    
                else:
                    # No API key - use basic analysis
                    return self._get_basic_analysis(clause_text_en, clause_type)
                
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Error analyzing clause: {e}")
                    return self._get_basic_analysis(clause_text_en, clause_type)
                time.sleep(1)  # Wait before retry
        
        return self._get_basic_analysis(clause_text_en, clause_type)
    
    def _get_basic_analysis(self, clause_text: str, clause_type: str) -> Dict[str, Any]:
        """Fallback analysis without API"""
        return {
            "plain_language_explanation": f"This is a {clause_type}. It contains standard legal terms that should be reviewed carefully.",
            "potential_risks": ["Standard legal risks apply", "Review with legal counsel"],
            "unfair_terms": ["Check for one-sided terms"],
            "suggested_alternative": "Consult legal counsel for appropriate wording",
            "compliance_notes": "Ensure compliance with Indian Contract Act, 1872",
            "negotiation_tips": ["Understand all terms", "Get legal advice", "Negotiate fair terms"],
            "severity": "Medium"
        }
    
    def _parse_text_response(self, text: str) -> Dict[str, Any]:
        """Parse text response into structured format"""
        # Simple parsing for fallback
        lines = text.split('\n')
        result = {
            "plain_language_explanation": "",
            "potential_risks": [],
            "unfair_terms": [],
            "suggested_alternative": "",
            "compliance_notes": "",
            "negotiation_tips": [],
            "severity": "Medium"
        }
        
        current_section = None
        for line in lines:
            line = line.strip()
            if 'explanation' in line.lower():
                current_section = 'explanation'
            elif 'risk' in line.lower():
                current_section = 'risks'
            elif 'alternative' in line.lower():
                current_section = 'alternative'
            elif 'tip' in line.lower():
                current_section = 'tips'
            elif line and current_section:
                if current_section == 'explanation':
                    result["plain_language_explanation"] += line + " "
                elif current_section == 'risks' and line.startswith('-'):
                    result["potential_risks"].append(line[1:].strip())
                elif current_section == 'alternative':
                    result["suggested_alternative"] += line + " "
                elif current_section == 'tips' and line.startswith('-'):
                    result["negotiation_tips"].append(line[1:].strip())
        
        return result
    
    def generate_summary(self, analysis_results: List[Dict], contract_type: str = "Unknown") -> str:
        """Generate executive summary using OpenAI"""
        if not self.use_openai:
            return self._generate_basic_summary(analysis_results, contract_type)
        
        summary_prompt = f"""Based on analysis of a {contract_type} contract for an Indian SME, provide a concise executive summary.

Key findings from analysis:
{json.dumps(analysis_results[:3], indent=2)}

Provide summary in this format:
1. Overall assessment (2-3 lines)
2. Top 3 immediate concerns
3. Recommended next steps
4. Urgency level (High/Medium/Low)

Keep it under 200 words, in simple business English."""
        
        try:
            response = openai.ChatCompletion.create(
                model=self.config.GPT_MODEL,
                messages=[
                    {"role": "system", "content": "Create a clear, actionable executive summary for a business owner."},
                    {"role": "user", "content": summary_prompt}
                ],
                temperature=0.1,
                max_tokens=400
            )
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating summary: {e}")
            return self._generate_basic_summary(analysis_results, contract_type)
    
    def _generate_basic_summary(self, analysis_results: List[Dict], contract_type: str) -> str:
        """Generate basic summary without API"""
        high_risk_count = sum(1 for a in analysis_results if a.get('severity', '').lower() == 'high')
        
        return f"""**Executive Summary for {contract_type}**
        
This contract requires careful review. Found {high_risk_count} high-risk clauses that need immediate attention.

**Key Concerns:**
1. Review all indemnity and liability clauses
2. Check termination conditions carefully
3. Verify jurisdiction is in India

**Next Steps:**
1. Discuss high-risk clauses with legal counsel
2. Negotiate fair terms before signing
3. Document all agreed changes

**Urgency: {'High' if high_risk_count > 0 else 'Medium'}**
"""
    
    def suggest_template_clause(self, clause_type: str, language: str = "en") -> str:
        """Provide SME-friendly template clause"""
        templates = {
            "en": {
                "Indemnity Clause": """**SME-Friendly Indemnity Clause:**
Each party shall indemnify the other only for direct losses caused by their gross negligence or willful misconduct. The total indemnity shall not exceed 1.5 times the contract value or ₹5,00,000, whichever is lower. This clause survives termination for 2 years.""",
                
                "Termination Clause": """**SME-Friendly Termination Clause:**
Either party may terminate this agreement with 30 days written notice. For material breach, 15 days notice to cure is required. Upon termination, each party shall return all confidential information. Payments due for services already rendered shall be made within 15 days.""",
                
                "Jurisdiction Clause": """**SME-Friendly Jurisdiction Clause:**
This agreement shall be governed by Indian laws. Any disputes shall be subject to the exclusive jurisdiction of courts in [City, State], India. Arbitration, if any, shall be conducted in India under the Arbitration and Conciliation Act, 1996.""",
                
                "Confidentiality Clause": """**SME-Friendly Confidentiality Clause:**
Confidential Information means information marked as confidential. The Receiving Party shall protect it using reasonable care for 3 years after termination. Information that becomes public through no fault of Receiver is not confidential.""",
                
                "Payment Clause": """**SME-Friendly Payment Clause:**
Payment of ₹[Amount] shall be made within 30 days of receiving a proper invoice. Late payments incur interest at 1.5% per month. All disputes regarding invoices must be raised within 15 days."""
            }
        }
        
        lang = language if language in templates else "en"
        return templates[lang].get(clause_type, "Standard clause not available for this type.")