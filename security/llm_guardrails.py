import re
from typing import Dict, Any, List
from typing import Dict, Any, List, Tuple

class LLMGuardrails:
    """Enforce constraints on LLM interactions"""
    
    # Allowed topics for LLM interactions
    ALLOWED_TOPICS = [
        'cancer treatment',
        'molecular biology',
        'genomic analysis',
        'drug recommendations',
        'clinical trials',
        'medical literature'
    ]
    
    # Forbidden outputs
    FORBIDDEN_PATTERNS = [
        r'prescription\s+for\s+\d+\s+pills',  # Specific prescriptions
        r'take\s+\d+\s+mg\s+daily',  # Dosage instructions
        r'stop\s+taking\s+your\s+medication',  # Medical advice
        r'you\s+don\'t\s+need\s+a\s+doctor',
        r'social\s+security\s+number',
        r'credit\s+card',
        r'password',
    ]
    
    @staticmethod
    def create_system_prompt() -> str:
        """Create constrained system prompt for LLM"""
        return """You are a medical literature analysis assistant for oncology research.

STRICT CONSTRAINTS:
1. You ONLY analyze molecular pathways and recommend treatments based on published literature
2. You NEVER provide direct medical advice or prescriptions
3. You NEVER ask for or handle patient PII (names, SSN, addresses)
4. You MUST cite scientific sources for recommendations
5. You MUST include disclaimers that recommendations require physician review
6. You focus ONLY on cancer genomics and treatment matching

FORBIDDEN ACTIONS:
- Providing dosage instructions
- Suggesting patients stop current treatments
- Diagnosing conditions
- Handling sensitive personal information
- Discussing non-medical topics

Always prefix recommendations with: "Based on published literature, these treatments may be relevant. Final decisions require oncologist review."
"""
    
    @staticmethod
    def validate_llm_input(prompt: str) -> Tuple[bool, str]:
        """Validate input before sending to LLM"""
        # Check length
        if len(prompt) > 10000:
            return False, "Input too long. Maximum 10,000 characters."
        
        # Check for PII patterns
        pii_patterns = [
            (r'\b\d{3}-\d{2}-\d{4}\b', 'SSN'),
            (r'\b\d{16}\b', 'Credit card'),
            (r'password\s*[:=]\s*\S+', 'Password'),
        ]
        
        for pattern, pii_type in pii_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                return False, f"Input contains {pii_type}. Please remove sensitive data."
        
        return True, ""
    
    @staticmethod
    def filter_llm_output(output: str) -> Tuple[str, List[str]]:
        """Filter and sanitize LLM output"""
        warnings = []
        
        # Check for forbidden content
        for pattern in LLMGuardrails.FORBIDDEN_PATTERNS:
            if re.search(pattern, output, re.IGNORECASE):
                warnings.append(f"Output contained forbidden pattern: {pattern}")
                output = re.sub(pattern, '[REDACTED]', output, flags=re.IGNORECASE)
        
        # Ensure disclaimer is present
        if 'physician review' not in output.lower() and 'oncologist' not in output.lower():
            output += "\n\n⚠️ IMPORTANT: All recommendations require review and approval by a qualified oncologist."
        
        return output, warnings
    
    @staticmethod
    def enforce_rate_limits(user_id: str, requests_per_hour: int = 100) -> Tuple[bool, str]:
        """Enforce rate limits on LLM API calls"""
        # This would integrate with a Redis cache or database
        # Simplified version here
        # TODO: Implement with actual rate limiting backend
        return True, ""
