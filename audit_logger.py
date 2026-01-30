# audit_logger.py - Fixed with proper imports
import json
import datetime
import hashlib
import os
from typing import Dict, List, Any  # Add this import

class AuditLogger:
    def __init__(self, log_dir: str = "audit_logs"):
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    def generate_hash(self, content: str) -> str:
        """Generate hash for document"""
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def log_analysis(self, document_hash: str, analysis_data: Dict[str, Any]) -> str:
        """Log analysis results"""
        timestamp = datetime.datetime.now().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'document_hash': document_hash,
            'analysis': analysis_data
        }
        
        log_file = os.path.join(self.log_dir, f"{document_hash}.json")
        
        # Read existing log if any
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                try:
                    existing_logs = json.load(f)
                    if not isinstance(existing_logs, list):
                        existing_logs = [existing_logs]
                except json.JSONDecodeError:
                    existing_logs = []
        else:
            existing_logs = []
        
        # Add new entry
        existing_logs.append(log_entry)
        
        # Write back
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(existing_logs, f, indent=2, ensure_ascii=False)
            
        return log_file
    
    def get_audit_trail(self, document_hash: str) -> List[Dict]:
        """Retrieve audit trail for document"""
        log_file = os.path.join(self.log_dir, f"{document_hash}.json")
        
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []