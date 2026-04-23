import re
from typing import Dict, List, Tuple

class InputValidator:
    """Validate and sanitize user inputs to prevent injection attacks"""
    
    # Suspicious patterns that might indicate prompt injection
    INJECTION_PATTERNS = [
        r'ignore\s+previous\s+instructions',
        r'disregard\s+.*\s+above',
        r'system\s*:\s*you\s+are',
        r'<\s*script',
        r'javascript:',
        r'eval\s*\(',
        r'exec\s*\(',
        r'__import__',
        r'new\s+role',
        r'forget\s+everything',
        r'act\s+as\s+(?!a\s+medical)',  # Allow "act as a medical expert"
    ]
    
    # Allowed characters for different fields
    PATIENT_ID_PATTERN = r'^P-\d{4,6}$'
    AGE_RANGE = (0, 120)
    
    @staticmethod
    def validate_patient_id(patient_id: str) -> Tuple[bool, str]:
        """Validate patient ID format"""
        if not re.match(InputValidator.PATIENT_ID_PATTERN, patient_id):
            return False, "Invalid patient ID format. Use format: P-XXXX"
        return True, ""
    
    @staticmethod
    def validate_age(age: int) -> Tuple[bool, str]:
        """Validate age is within reasonable range"""
        if not (InputValidator.AGE_RANGE[0] <= age <= InputValidator.AGE_RANGE[1]):
            return False, f"Age must be between {InputValidator.AGE_RANGE[0]} and {InputValidator.AGE_RANGE[1]}"
        return True, ""
    
    @staticmethod
    def detect_prompt_injection(text: str) -> Tuple[bool, List[str]]:
        """Detect potential prompt injection attempts"""
        detected_patterns = []
        text_lower = text.lower()
        
        for pattern in InputValidator.INJECTION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                detected_patterns.append(pattern)
        
        is_suspicious = len(detected_patterns) > 0
        return is_suspicious, detected_patterns
    
    @staticmethod
    def sanitize_clinical_notes(text: str, max_length: int = 5000) -> str:
        """Sanitize clinical notes while preserving medical content"""
        # Truncate to max length
        text = text[:max_length]
        
        # Remove potential script injections
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove SQL injection attempts
        text = re.sub(r'(;|\-\-|\/\*|\*\/|xp_|sp_)', '', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    @staticmethod
    def validate_mutations(mutations: List[str], allowed_mutations: List[str]) -> Tuple[bool, str]:
        """Validate that mutations are from allowed list"""
        for mutation in mutations:
            if mutation not in allowed_mutations:
                return False, f"Invalid mutation: {mutation}"
        return True, ""
