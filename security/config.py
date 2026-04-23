"""Security configuration"""
import os

class SecurityConfig:
    # Environment
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    
    # Rate limiting
    MAX_REQUESTS_PER_HOUR = 100
    MAX_REQUESTS_PER_DAY = 1000
    
    # Input validation
    MAX_CLINICAL_NOTES_LENGTH = 5000
    MAX_PATIENT_ID_LENGTH = 20
    
    # PII handling
    ENABLE_PII_MASKING = True
    LOG_PII_DETECTIONS = True
    
    # LLM guardrails
    LLM_TEMPERATURE = 0.3  # Lower for more deterministic medical advice
    LLM_MAX_TOKENS = 2000
    LLM_TIMEOUT_SECONDS = 60
    
    # Action controls
    REQUIRE_APPROVAL_FOR_HIGH_RISK = True
    ENABLE_AUDIT_LOGGING = True
    AUDIT_LOG_RETENTION_DAYS = 90
    
    # Database security
    ENABLE_QUERY_PARAMETERIZATION = True
    MAX_QUERY_RESULTS = 1000
    
    # Session management
    SESSION_TIMEOUT_MINUTES = 30
    MAX_CONCURRENT_SESSIONS = 5
