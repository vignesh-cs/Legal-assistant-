class HindiSupport:
    """Basic Hindi support without external dependencies"""
    
    HINDI_KEYWORDS = {
        'parties': ['पक्ष', 'पार्टी', 'भागीदार'],
        'date': ['तारीख', 'दिनांक', 'मिति'],
        'amount': ['राशि', 'धनराशि', 'कीमत', 'मूल्य'],
        'termination': ['समाप्ति', 'खत्म', 'समापन'],
        'liability': ['दायित्व', 'जिम्मेदारी'],
        'confidential': ['गोपनीय', 'रहस्य', 'गुप्त'],
        'jurisdiction': ['क्षेत्राधिकार', 'अधिकार क्षेत्र'],
        'arbitration': ['मध्यस्थता', 'पंच निर्णय']
    }
    
    @staticmethod
    def contains_hindi(text: str) -> bool:
        """Check if text contains Hindi characters"""
        hindi_range = range(0x0900, 0x097F + 1)
        return any(ord(char) in hindi_range for char in text)
    
    @staticmethod
    def extract_hindi_entities(text: str) -> dict:
        """Basic entity extraction for Hindi text"""
        entities = {
            'dates': [],
            'amounts': [],
            'parties': []
        }
        
        # Simple regex patterns for Hindi
        patterns = {
            'dates': r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}',
            'amounts': r'₹?\s*\d+(?:,\d+)*(?:\.\d+)?\s*(?:रुपये|रु\.?)',
            'parties': r'पक्ष\s*[०-९一二三四五六七八九十]+\s*[:：]\s*([^\n]+)'
        }
        
        import re
        for entity_type, pattern in patterns.items():
            matches = re.findall(pattern, text)
            entities[entity_type] = matches
        
        return entities
    
    @staticmethod
    def get_hindi_template(template_type: str) -> str:
        """Get Hindi version of common templates"""
        templates = {
            'nda': """गैर-प्रकटीकरण समझौता (एनडीए)

1. पार्टियां
यह समझौता [कंपनी का नाम] और [दूसरी पार्टी] के बीच है।

2. गोपनीय जानकारी
गोपनीय जानकारी में [विवरण] शामिल है।

3. दायित्व
प्राप्त करने वाला पक्ष गोपनीय जानकारी की रक्षा करेगा।

4. अपवाद
सार्वजनिक रूप से उपलब्ध जानकारी गोपनीय नहीं है।

5. अवधि
यह समझौता [2] वर्षों तक प्रभावी रहेगा।

6. भारतीय कानून
यह समझौता भारतीय कानून के अधीन है।""",
            
            'payment': """भुगतान खंड

1. भुगतान राशि: ₹[राशि]
2. भुगतान अवधि: इनवॉइस प्राप्ति के 30 दिनों के भीतर
3. विलंब शुल्क: 1.5% प्रति माह
4. भुगतान विधि: बैंक हस्तांतरण
5. कर: सभी राशियां लागू करों के अतिरिक्त हैं"""
        }
        
        return templates.get(template_type.lower(), "हिंदी टेम्पलेट उपलब्ध नहीं है")