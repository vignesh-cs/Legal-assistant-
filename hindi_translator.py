# hindi_translator.py - Simple Hindi support without external dependencies

class SimpleHindiTranslator:
    """Basic Hindi support for hackathon demo"""
    
    HINDI_KEYWORDS_MAP = {
        # Hindi to English keyword mapping
        'पक्ष': 'Party',
        'अनुबंध': 'Contract',
        'समझौता': 'Agreement',
        'भुगतान': 'Payment',
        'राशि': 'Amount',
        'तारीख': 'Date',
        'समाप्ति': 'Termination',
        'दायित्व': 'Liability',
        'क्षतिपूर्ति': 'Indemnity',
        'गोपनीयता': 'Confidentiality',
        'क्षेत्राधिकार': 'Jurisdiction',
        'मध्यस्थता': 'Arbitration',
        'अनुच्छेद': 'Clause',
        'धारा': 'Section',
        'हस्ताक्षर': 'Signature',
        'नियम': 'Terms',
        'शर्तें': 'Conditions'
    }
    
    @staticmethod
    def detect_hindi(text: str) -> bool:
        """Check if text contains Hindi characters"""
        hindi_range = range(0x0900, 0x097F + 1)
        return any(ord(char) in hindi_range for char in text[:500])
    
    @staticmethod
    def translate_keywords(text: str) -> str:
        """Translate Hindi keywords to English for demo"""
        result = text
        for hindi, english in SimpleHindiTranslator.HINDI_KEYWORDS_MAP.items():
            if hindi in text:
                result = result.replace(hindi, f"{english} ({hindi})")
        return result
    
    @staticmethod
    def get_hindi_template(template_name: str) -> str:
        """Get Hindi version of templates for demo"""
        templates = {
            'nda': """गैर-प्रकटीकरण समझौता (एनडीए)

1. पक्ष:
   - प्रकट करने वाला पक्ष: [कंपनी का नाम]
   - प्राप्त करने वाला पक्ष: [दूसरी पार्टी]

2. गोपनीय जानकारी:
   व्यावसायिक रहस्य, ग्राहक सूची, आदि।

3. अवधि:
   2 वर्षों के लिए प्रभावी।

4. भारतीय कानून:
   भारतीय कानून लागू होंगे।"""
        }
        return templates.get(template_name.lower(), "हिंदी टेम्पलेट उपलब्ध नहीं है")