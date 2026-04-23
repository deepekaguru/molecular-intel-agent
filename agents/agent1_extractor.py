# GNU Head
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import json
import os

load_dotenv()

def run(state):
    print("Agent 1 running — extracting genomic features...")
    
    # Initialize secure LLM wrapper INSIDE the function
    from security.llm_wrapper import SecureLLMClient
    secure_llm = SecureLLMClient(model="gpt-4o-mini", temperature=0.3)
    
    clinical_notes = state.get('clinical_notes', '')
    
    # Preserve mutations already selected from the form
    state.setdefault('mutations', [])
    state.setdefault('cnvs', [])
    state.setdefault('fusions', [])
    
    # If no clinical notes provided, skip LLM extraction
    if not clinical_notes or clinical_notes.strip() == '':
        print("No clinical notes provided - using form-selected mutations only")
        return state
    
    prompt = f"""
Extract genomic features from these clinical notes:

{clinical_notes}

Return ONLY a JSON object (no markdown, no backticks) with these keys:
{{
    "mutations": ["gene1", "gene2"],
    "cnvs": ["amplification1", "deletion1"],
    "fusions": ["fusion1", "fusion2"]
}}

If none found for a category, use empty array [].
"""

    # ========== LEVEL 2 CONFIRMATION: USER AUTHORIZATION REQUIRED ==========
    # Import action controller
    from security.action_control import ActionController
    import streamlit as st
    
    action_controller = ActionController()
    
    # Prepare detailed action information for user review
    action_details = {
        "purpose": "Extract genomic features from clinical notes",
        "input_length": f"{len(clinical_notes)} characters",
        "mutations_already_selected": len(state.get('mutations', [])),
        "estimated_api_cost": "$0.01 - $0.03 per call",
        "data_destination": "OpenAI API (external service)",
        "model": "gpt-4o-mini",
        "temperature": 0.3,
        "note_preview": clinical_notes[:100] + "..." if len(clinical_notes) > 100 else clinical_notes
    }
    
    # Require user confirmation before making LLM call
    try:
        action_controller.require_user_confirmation(
            action_type="llm_feature_extraction",
            details=action_details,
            risk_level="MEDIUM"  # MEDIUM - extracting features, less risky than generating recommendations
        )
    except Exception as e:
        # If confirmation fails or user denies, log and skip extraction
        print(f"⚠️ LLM call authorization denied: {e}")
        print("Using form-selected mutations only (no LLM extraction)")
        
        # Log the denial
        action_controller.log_action(
            action_type="llm_feature_extraction",
            status="DENIED",
            details={"reason": str(e)}
        )
        
        return state
    
    # ========== END OF LEVEL 2 CONFIRMATION SECTION ==========
    
    # User authorized - proceed with LLM call
    print("✅ User authorized LLM call - proceeding with feature extraction...")
    
    # Use secure LLM wrapper with guardrails
    result = secure_llm.chat_completion(
        prompt=prompt,
        system_message="You are a genomic data extraction assistant. Return only valid JSON.",
        user_role='all'
    )
    
    if result['success']:
        try:
            # Parse JSON response
            response_text = result['response'].strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
                response_text = response_text.strip()
            
            extracted = json.loads(response_text)
            
            # Merge with existing mutations from form (avoid duplicates)
            existing_mutations = set(state.get('mutations', []))
            new_mutations = set(extracted.get('mutations', []))
            state['mutations'] = list(existing_mutations | new_mutations)
            
            # Add CNVs and fusions (preserve existing)
            state.setdefault('cnvs', [])
            state['cnvs'].extend(extracted.get('cnvs', []))
            
            state.setdefault('fusions', [])
            state['fusions'].extend(extracted.get('fusions', []))
            
            print(f"✅ Extracted features: {len(state['mutations'])} mutations, "
                  f"{len(state['cnvs'])} CNVs, {len(state['fusions'])} fusions")
            
            # Log successful execution
            action_controller.log_action(
                action_type="llm_feature_extraction",
                status="SUCCESS",
                details={
                    "mutations_extracted": len(new_mutations),
                    "total_mutations": len(state['mutations'])
                }
            )
            
        except json.JSONDecodeError as e:
            print(f"⚠️ JSON parsing error: {e}")
            print(f"LLM response: {result['response']}")
            # Preserve existing mutations from form
            state.setdefault('mutations', [])
            state.setdefault('cnvs', [])
            state.setdefault('fusions', [])
            
            action_controller.log_action(
                action_type="llm_feature_extraction",
                status="FAILED",
                details={"error": f"JSON parsing error: {str(e)}"}
            )
    else:
        print(f"❌ LLM extraction failed: {result.get('error')}")
        # Preserve existing mutations
        state.setdefault('mutations', [])
        state.setdefault('cnvs', [])
        state.setdefault('fusions', [])
        
        action_controller.log_action(
            action_type="llm_feature_extraction",
            status="FAILED",
            details={"error": result.get('error', 'Unknown error')}
        )
    
    return state
