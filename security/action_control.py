import logging
from datetime import datetime
import os

class ActionController:
    """
    Controls and audits agent actions based on risk levels
    """
    
    def __init__(self, log_file=None):
        """Initialize action controller with audit logging"""
        if log_file is None:
            log_file = '/home/deepekagurunathan/molecular-intel-agent/logs/action_audit.log'
        
        # Ensure log directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Set up audit logger
        self.audit_logger = logging.getLogger('action_audit')
        self.audit_logger.setLevel(logging.INFO)
        
        # Avoid duplicate handlers
        if not self.audit_logger.handlers:
            handler = logging.FileHandler(log_file)
            formatter = logging.Formatter('%(asctime)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            handler.setFormatter(formatter)
            self.audit_logger.addHandler(handler)
        
        # Define action policies with risk levels
        self.policy = {
            'query_knowledge_graph': {'allowed': True, 'risk_level': 'LOW'},
            'extract_features': {'allowed': True, 'risk_level': 'MEDIUM'},
            'generate_recommendations': {'allowed': True, 'risk_level': 'HIGH'},
            'llm_call': {'allowed': True, 'risk_level': 'HIGH'},
            'database_write': {'allowed': False, 'risk_level': 'CRITICAL'},
            'export_patient_data': {'allowed': False, 'risk_level': 'CRITICAL'},
        }
    
    def authorize_action(self, action_type, details=None):
        """
        Check if an action is authorized based on policy
        
        Args:
            action_type: Type of action to authorize
            details: Optional dict with action details
            
        Returns:
            bool: True if authorized, False otherwise
        """
        if details is None:
            details = {}
        
        # Get policy for this action type
        action_policy = self.policy.get(action_type, {'allowed': False, 'risk_level': 'UNKNOWN'})
        
        is_allowed = action_policy['allowed']
        risk_level = action_policy['risk_level']
        
        # Log the authorization check
        log_message = (
            f"ACTION_CHECK | Type: {action_type} | "
            f"Risk: {risk_level} | "
            f"Allowed: {is_allowed} | "
            f"Details: {details}"
        )
        self.audit_logger.info(log_message)
        
        return is_allowed
    
    def log_action(self, action_type, status, details=None):
        """
        Log an action execution
        
        Args:
            action_type: Type of action executed
            status: 'SUCCESS' or 'FAILED'
            details: Optional dict with execution details
        """
        if details is None:
            details = {}
        
        risk_level = self.policy.get(action_type, {}).get('risk_level', 'UNKNOWN')
        
        log_message = (
            f"ACTION_EXECUTED | Type: {action_type} | "
            f"Status: {status} | "
            f"Risk: {risk_level} | "
            f"Details: {details}"
        )
        self.audit_logger.info(log_message)
    
    def require_user_confirmation(self, action_type, details, risk_level=None):
        """
        Require explicit user confirmation for risky actions
        
        Args:
            action_type: Type of action (e.g., 'llm_rationale_generation')
            details: Dictionary with action details to show user
            risk_level: 'LOW', 'MEDIUM', 'HIGH', or 'CRITICAL'
        
        Returns:
            bool: True if confirmed
            
        Raises:
            PermissionError: If user denies authorization (via st.stop())
        """
        import streamlit as st
        from datetime import datetime
        
        # Determine risk level if not provided
        if risk_level is None:
            risk_level = self.policy.get(action_type, {}).get('risk_level', 'MEDIUM')
        
        # Only require confirmation for HIGH and CRITICAL actions
        if risk_level not in ['HIGH', 'CRITICAL']:
            # Still log it but don't require confirmation
            self.audit_logger.info(
                f"ACTION_AUTO_APPROVED | Type: {action_type} | Risk: {risk_level} | "
                f"Details: {details} | Timestamp: {datetime.now().isoformat()}"
            )
            return True
        
        # Visual warning based on risk level
        if risk_level == 'CRITICAL':
            st.error(f"🚨 **CRITICAL RISK ACTION**: {action_type.replace('_', ' ').title()}")
        else:
            st.warning(f"⚠️ **HIGH RISK ACTION**: {action_type.replace('_', ' ').title()}")
        
        # Show expandable details
        with st.expander("🔍 View Action Details", expanded=True):
            for key, value in details.items():
                # Format the key nicely
                formatted_key = key.replace('_', ' ').title()
                
                # Handle different value types
                if isinstance(value, list):
                    st.write(f"**{formatted_key}**: `{', '.join(map(str, value))}`")
                else:
                    st.write(f"**{formatted_key}**: `{value}`")
        
        # Unique confirmation key (prevents checkbox conflicts)
        confirm_key = f"confirm_{action_type}_{hash(str(details))}"
        
        # Confirmation checkbox
        confirmed = st.checkbox(
            f"✓ I authorize this {risk_level.lower()} risk action and understand the implications",
            key=confirm_key
        )
        
        # If not confirmed, stop execution
        if not confirmed:
            # Log the denial
            self.audit_logger.info(
                f"ACTION_DENIED | Type: {action_type} | Risk: {risk_level} | "
                f"Details: {details} | Timestamp: {datetime.now().isoformat()}"
            )
            
            st.info("👆 Please authorize this action to proceed with analysis")
            st.stop()  # Halts Streamlit execution
            
            # This won't be reached due to st.stop(), but included for completeness
            raise PermissionError(f"User denied authorization for {action_type}")
        
        # Log the authorization
        self.audit_logger.info(
            f"ACTION_AUTHORIZED | Type: {action_type} | Risk: {risk_level} | "
            f"User: authorized | Details: {details} | Timestamp: {datetime.now().isoformat()}"
        )
        
        st.success(f"✅ {action_type.replace('_', ' ').title()} authorized")
        
        return True
