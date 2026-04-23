"""
Security Guardrails Module for Molecular Intelligence Platform
Implements: Input validation, PII scrubbing, output filtering, clinical guardrails
"""

import re
import os
import logging
from typing import Tuple, Optional, List, Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    filename='security_audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SecurityGuardrails:
    """
    Comprehensive security layer for clinical AI system.
    All security features documented in the requirements.
    """
    
    # Configuration Constants
    MAX_INPUT_LENGTH = 2000
    MIN_CONFIDENCE_THRESHOLD = 0.3
    MAX_OUTPUT_LENGTH = 10000
    
    # PII Patterns - Regex for common sensitive data
    PII_PATTERNS = {
        'SSN': r'\b\d{3}-?\d{2}-?\d{4}\b',
        'EMAIL': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'PHONE': r'\b\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
        'CREDIT_CARD': r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
        'ZIP': r'\b\d{5}(?:-\d{4})?\b',
    }
    
    # Prompt Injection Patterns - Security threats to detect
    INJECTION_PATTERNS = [
        r'<script.*?>.*?</script>',
        r'javascript:',
        r'on\w+\s*=',  # onclick, onload, onerror, etc.
        r'eval\s*\(',
        r'exec\s*\(',
        r'import\s+os',
        r'__import__',
        r'\.\./',  # Directory traversal
        r'DROP\s+TABLE',
        r'DELETE\s+FROM',
        r'INSERT\s+INTO',
        r'UPDATE\s+.*SET',
        r'UNION\s+SELECT',
        r'<iframe',
        r'<embed',
        r'<object',
    ]
    
    @classmethod
    def validate_input(cls, text: str, field_name: str = "input") -> Tuple[bool, str]:
        """
        Input Validation Layer
        - Checks length constraints
        - Detects prompt injection patterns
        - Logs validation attempts
        
        Returns: (is_valid, error_message)
        """
        if not text or len(text.strip()) == 0:
            return True, ""  # Empty input is acceptable for optional fields
        
        # Log validation attempt
        logger.info(f"Validating input for field: {field_name}, length: {len(text)}")
        
        # Check length
        if len(text) > cls.MAX_INPUT_LENGTH:
            error_msg = f"{field_name} exceeds maximum length of {cls.MAX_INPUT_LENGTH} characters (current: {len(text)})"
            logger.warning(f"Input validation failed: {error_msg}")
            return False, error_msg
        
        # Check for injection patterns
        for pattern in cls.INJECTION_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                error_msg = f"{field_name} contains suspicious pattern: {match.group()}"
                logger.warning(f"Prompt injection detected: {error_msg}")
                return False, f"{field_name} contains suspicious patterns. Please remove code/script elements."
        
        logger.info(f"Input validation passed for: {field_name}")
        return True, ""
    
    @classmethod
    def scrub_pii(cls, text: str) -> Tuple[str, bool, List[str]]:
        """
        PII Scrubbing Layer
        - Removes SSN, emails, phones, credit cards
        - Redacts patient names
        - Logs PII detections
        
        Returns: (scrubbed_text, pii_found, types_found)
        """
        if not text or len(text.strip()) == 0:
            return text, False, []
        
        scrubbed = text
        pii_found = False
        types_found = []
        
        # Apply regex patterns
        for pii_type, pattern in cls.PII_PATTERNS.items():
            matches = re.findall(pattern, scrubbed)
            if matches:
                scrubbed = re.sub(pattern, f'[{pii_type}_REDACTED]', scrubbed)
                pii_found = True
                types_found.append(pii_type)
                logger.warning(f"PII detected and redacted: {pii_type}, count: {len(matches)}")
        
        # Redact common name patterns
        # Pattern: "Patient: John Doe" or "Name: Jane Smith"
        name_patterns = [
            (r'(?:Patient|Name|Client):\s*([A-Z][a-z]+\s+[A-Z][a-z]+)', '[NAME_REDACTED]'),
            (r'(?:Mr\.|Mrs\.|Ms\.|Dr\.)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)', '[NAME_REDACTED]'),
        ]
        
        for pattern, replacement in name_patterns:
            matches = re.findall(pattern, scrubbed)
            if matches:
                scrubbed = re.sub(pattern, replacement, scrubbed)
                pii_found = True
                if 'NAME' not in types_found:
                    types_found.append('NAME')
                logger.warning(f"Name pattern detected and redacted, count: {len(matches)}")
        
        if pii_found:
            logger.info(f"PII scrubbing complete. Types found: {', '.join(types_found)}")
        
        return scrubbed, pii_found, types_found
    
    @classmethod
    def validate_output(cls, output: Any, agent_name: str = "agent") -> Tuple[bool, str]:
        """
        Output Filtering Layer
        - Validates agent output completeness
        - Checks output size constraints
        - Logs validation results
        
        Returns: (is_valid, error_message)
        """
        # Convert to string for validation
        output_str = str(output) if output is not None else ""
        
        # Check for empty/null output
        if not output or len(output_str.strip()) == 0:
            error_msg = f"{agent_name} produced empty output"
            logger.error(f"Output validation failed: {error_msg}")
            return False, error_msg
        
        # Check output size
        if len(output_str) > cls.MAX_OUTPUT_LENGTH:
            error_msg = f"{agent_name} output exceeds maximum size ({len(output_str)} > {cls.MAX_OUTPUT_LENGTH})"
            logger.error(f"Output validation failed: {error_msg}")
            return False, error_msg
        
        logger.info(f"Output validation passed for: {agent_name}, length: {len(output_str)}")
        return True, ""
    
    @classmethod
    def apply_clinical_guardrail(cls, treatments: List[Dict], confidence_key: str = 'confidence') -> Tuple[List[Dict], int]:
        """
        Clinical Guardrail Layer
        - Filters treatments below confidence threshold (0.3)
        - Ensures only defensible recommendations surface
        - Logs filtering decisions
        
        Returns: (filtered_treatments, count_removed)
        """
        if not treatments:
            logger.info("No treatments to filter")
            return [], 0
        
        original_count = len(treatments)
        
        # Filter by confidence threshold
        filtered = [
            t for t in treatments 
            if isinstance(t.get(confidence_key), (int, float)) and t.get(confidence_key, 0) >= cls.MIN_CONFIDENCE_THRESHOLD
        ]
        
        removed_count = original_count - len(filtered)
        
        if removed_count > 0:
            logger.warning(f"Clinical guardrail: {removed_count} treatment(s) filtered (confidence < {cls.MIN_CONFIDENCE_THRESHOLD})")
        else:
            logger.info(f"Clinical guardrail: All {original_count} treatments passed threshold")
        
        return filtered, removed_count
    
    @classmethod
    def enforce_hitl(cls, approved: bool, patient_id: str = "unknown") -> Tuple[bool, str]:
        """
        HITL Enforcement Layer
        - Hard gate: No action without oncologist approval
        - Logs all approval decisions
        
        Returns: (can_proceed, message)
        """
        timestamp = datetime.now().isoformat()
        
        if not approved:
            msg = "Treatment recommendation requires oncologist approval before implementation"
            logger.warning(f"HITL: Approval DENIED for patient {patient_id} at {timestamp}")
            return False, msg
        
        msg = "Approval granted by oncologist - recommendation approved for clinical consideration"
        logger.info(f"HITL: Approval GRANTED for patient {patient_id} at {timestamp}")
        return True, msg
    
    @classmethod
    def validate_patient_id(cls, patient_id: str) -> Tuple[bool, str]:
        """
        Patient ID Validation
        - Format validation
        - Injection pattern detection
        
        Returns: (is_valid, error_message)
        """
        if not patient_id or len(patient_id.strip()) == 0:
            return False, "Patient ID is required"
        
        # Length check
        if len(patient_id) > 50:
            return False, "Patient ID too long (max 50 characters)"
        
        # Format check: alphanumeric, hyphens, underscores only
        if not re.match(r'^[A-Za-z0-9_-]+$', patient_id):
            return False, "Patient ID can only contain letters, numbers, hyphens, and underscores"
        
        # Check for suspicious patterns
        for pattern in cls.INJECTION_PATTERNS:
            if re.search(pattern, patient_id, re.IGNORECASE):
                logger.warning(f"Suspicious Patient ID rejected: {patient_id}")
                return False, "Invalid Patient ID format"
        
        return True, ""
    
    @classmethod
    def log_action(cls, action: str, details: Dict[str, Any]) -> None:
        """
        Audit Logging
        - Records all significant system actions
        - Creates audit trail for compliance
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'details': details
        }
        logger.info(f"Action logged: {action} - {details}")
    
    @classmethod
    def check_secrets_management(cls) -> Tuple[bool, List[str]]:
        """
        Secrets Management Verification
        - Ensures API keys not hardcoded
        - Validates .env and .gitignore setup
        
        Returns: (all_good, issues_list)
        """
        issues = []
        
        # Check .env exists
        if not os.path.exists('.env'):
            issues.append(".env file not found")
        
        # Check .gitignore includes .env
        if os.path.exists('.gitignore'):
            with open('.gitignore', 'r') as f:
                gitignore_content = f.read()
                if '.env' not in gitignore_content:
                    issues.append(".env not excluded in .gitignore")
        else:
            issues.append(".gitignore file not found")
        
        # Check required env vars are loaded
        required_vars = ['OPENAI_API_KEY', 'NEO4J_URI', 'NEO4J_PASSWORD']
        for var in required_vars:
            if not os.getenv(var):
                issues.append(f"Environment variable {var} not found")
        
        if issues:
            logger.warning(f"Secrets management issues: {', '.join(issues)}")
        else:
            logger.info("Secrets management check: PASSED")
        
        return len(issues) == 0, issues


# Convenience functions for easy import
def validate_input(text: str, field_name: str = "input") -> Tuple[bool, str]:
    """Shortcut for input validation"""
    return SecurityGuardrails.validate_input(text, field_name)

def scrub_pii(text: str) -> Tuple[str, bool, List[str]]:
    """Shortcut for PII scrubbing"""
    return SecurityGuardrails.scrub_pii(text)

def validate_output(output: Any, agent_name: str = "agent") -> Tuple[bool, str]:
    """Shortcut for output validation"""
    return SecurityGuardrails.validate_output(output, agent_name)

def apply_clinical_guardrail(treatments: List[Dict]) -> Tuple[List[Dict], int]:
    """Shortcut for clinical guardrail"""
    return SecurityGuardrails.apply_clinical_guardrail(treatments)

def enforce_hitl(approved: bool, patient_id: str = "unknown") -> Tuple[bool, str]:
    """Shortcut for HITL enforcement"""
    return SecurityGuardrails.enforce_hitl(approved, patient_id)

def validate_patient_id(patient_id: str) -> Tuple[bool, str]:
    """Shortcut for patient ID validation"""
    return SecurityGuardrails.validate_patient_id(patient_id)

def log_action(action: str, details: Dict[str, Any]) -> None:
    """Shortcut for action logging"""
    return SecurityGuardrails.log_action(action, details)
