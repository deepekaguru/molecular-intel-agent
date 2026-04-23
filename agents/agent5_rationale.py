# GNU Head
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

def run(state):
    print("Agent 5 running — generating clinical rationale...")
    
    # Initialize secure LLM wrapper INSIDE the function
    from security.llm_wrapper import SecureLLMClient
    secure_llm = SecureLLMClient(model="gpt-4o-mini", temperature=0.3)
    
    treatments = state['ranked_treatments'][:3]
    evidence = state['rag_evidence']
    mutations = state['mutations']
    
    prompt = f"""
You are a clinical oncology AI assistant.

Patient mutations: {mutations}

Top ranked treatments:
{treatments}

Supporting literature evidence:
{evidence}

For each treatment, write exactly 2 sentences of
clinical rationale explaining why it is recommended
for this patient based on their mutations and the evidence.

Format your response as:
1. [Drug name]: [2 sentence rationale]
2. [Drug name]: [2 sentence rationale]
3. [Drug name]: [2 sentence rationale]
"""

    # ========== LEVEL 2 CONFIRMATION: USER AUTHORIZATION REQUIRED ==========
    # Import action controller
    from security.action_control import ActionController
    import streamlit as st
    
    action_controller = ActionController()
    
    # Prepare detailed action information for user review
    action_details = {
        "purpose": "Generate clinical rationale for treatment recommendations",
        "mutations": mutations if mutations else "None selected",
        "top_treatments": [t.get('treatment', 'Unknown') for t in treatments] if treatments else [],
        "evidence_sources": len(evidence) if isinstance(evidence, list) else "N/A",
        "estimated_api_cost": "$0.01 - $0.05 per call",
        "data_destination": "OpenAI API (external service)",
        "model": "gpt-4o-mini",
        "temperature": 0.3,
        "pii_status": "Should be masked by input validator"
    }
    
    # Require user confirmation before making LLM call
    try:
        action_controller.require_user_confirmation(
            action_type="llm_rationale_generation",
            details=action_details,
            risk_level="HIGH"  # HIGH because sends patient data to external API
        )
    except Exception as e:
        # If confirmation fails or user denies, log and return safe default
        print(f"⚠️ LLM call authorization denied: {e}")
        state['rationale'] = "Rationale generation requires user authorization. Please authorize the action to proceed."
        
        # Log the denial
        action_controller.log_action(
            action_type="llm_rationale_generation",
            status="DENIED",
            details={"reason": str(e)}
        )
        
        return state
    
    # ========== END OF LEVEL 2 CONFIRMATION SECTION ==========
    
    # User authorized - proceed with LLM call
    print("✅ User authorized LLM call - proceeding with rationale generation...")
    
    # Use secure LLM wrapper with guardrails
    result = secure_llm.chat_completion(
        prompt=prompt,
        system_message="You are a clinical oncology AI assistant.",
        user_role='all'
    )
    
    if result['success']:
        state['rationale'] = result['response']
        
        # Log successful execution
        action_controller.log_action(
            action_type="llm_rationale_generation",
            status="SUCCESS",
            details={"response_length": len(result['response'])}
        )
        
        # Log any warnings from guardrails
        if result.get('warnings'):
            print(f"⚠️ LLM Warnings: {result['warnings']}")
    else:
        # Fallback if LLM fails
        state['rationale'] = "Unable to generate rationale at this time. Please try again."
        print(f"❌ LLM Error: {result.get('error', 'Unknown error')}")
        
        # Log the failure
        action_controller.log_action(
            action_type="llm_rationale_generation",
            status="FAILED",
            details={"error": result.get('error', 'Unknown error')}
        )
    
    return state
