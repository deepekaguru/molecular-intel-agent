"""
Secure LLM wrapper with guardrails for OpenAI calls
"""
import os
from typing import Dict, Any, List
from datetime import datetime
import json
from langchain_openai import ChatOpenAI

# Import security modules
import sys
sys.path.append('/home/deepekagurunathan/molecular-intel-agent')
from security.llm_guardrails import LLMGuardrails
from security.data_security import DataSecurityHandler
from security.action_control import ActionController

class SecureLLMClient:
    """Wrapper around OpenAI with security guardrails"""
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.3):
        self.model = model
        self.temperature = temperature
        self.guardrails = LLMGuardrails()
        self.data_security = DataSecurityHandler()
        self.action_controller = ActionController()
        
        # Initialize OpenAI client
        self.client = ChatOpenAI(
            model=model,
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=temperature
        )
        
        # Track usage
        self.call_count = 0
        self.total_tokens = 0
    
    def chat_completion(
        self, 
        prompt: str, 
        system_message: str = None,
        max_tokens: int = 2000,
        user_role: str = 'all'
    ) -> Dict[str, Any]:
        """
        Secure chat completion with guardrails
        
        Args:
            prompt: User prompt to send to LLM
            system_message: Optional system message (uses default medical guardrails if None)
            max_tokens: Maximum tokens in response
            user_role: User role for authorization
            
        Returns:
            Dict with 'success', 'response', 'warnings', 'filtered'
        """
        
        # ===== GUARDRAIL 1: AUTHORIZATION =====
        if not self.action_controller.authorize_action('call_llm', user_role):
            return {
                'success': False,
                'error': 'Unauthorized LLM access',
                'response': None
            }
        
        # ===== GUARDRAIL 2: INPUT VALIDATION =====
        valid_input, error_msg = self.guardrails.validate_llm_input(prompt)
        if not valid_input:
            self.action_controller.log_action('call_llm', user_role, 'blocked', error_msg)
            return {
                'success': False,
                'error': error_msg,
                'response': None
            }
        
        # ===== GUARDRAIL 3: PII SCRUBBING =====
        masked_result = self.data_security.mask_pii(prompt)
        if masked_result['pii_detected']:
            # Log PII detection
            self.data_security.secure_log('pii_in_llm_input', {
                'pii_types': masked_result['pii_detected'],
                'masked': True
            }, level='WARNING')
        
        safe_prompt = masked_result['masked_text']
        
        # ===== GUARDRAIL 4: SYSTEM PROMPT ENFORCEMENT =====
        if system_message is None:
            system_message = self.guardrails.create_system_prompt()
        
        # ===== GUARDRAIL 5: MAKE LLM CALL =====
        try:
            # Log the call
            self.action_controller.log_action('call_llm', user_role, 'started', {
                'model': self.model,
                'prompt_length': len(safe_prompt)
            })
            
            # Invoke LLM
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": safe_prompt}
            ]
            
            response = self.client.invoke(messages)
            output_text = response.content
            
            # Track usage
            self.call_count += 1
            
        except Exception as e:
            self.action_controller.log_action('call_llm', user_role, 'failed', str(e))
            return {
                'success': False,
                'error': f'LLM call failed: {str(e)}',
                'response': None
            }
        
        # ===== GUARDRAIL 6: OUTPUT FILTERING =====
        filtered_output, warnings = self.guardrails.filter_llm_output(output_text)
        
        # ===== GUARDRAIL 7: SECURE LOGGING =====
        self.data_security.secure_log('llm_call_completed', {
            'model': self.model,
            'prompt_length': len(safe_prompt),
            'response_length': len(filtered_output),
            'warnings': len(warnings),
            'call_count': self.call_count
        })
        
        self.action_controller.log_action('call_llm', user_role, 'success', {
            'output_filtered': len(warnings) > 0
        })
        
        return {
            'success': True,
            'response': filtered_output,
            'warnings': warnings,
            'filtered': len(warnings) > 0,
            'pii_detected_in_input': masked_result['pii_detected']
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            'total_calls': self.call_count,
            'model': self.model,
            'temperature': self.temperature
        }
