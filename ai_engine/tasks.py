import json
import requests
from celery import shared_task
from django.conf import settings
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from core.models import Candidate
from .vector_service import VectorService

def update_ghl_contact(contact_id, data):
    """
    Helper function to update GoHighLevel contact via API.
    """
    ghl_token = getattr(settings, 'GHL_ACCESS_TOKEN', None)
    if not ghl_token:
        print("GHL_ACCESS_TOKEN not set, skipping GHL update.")
        return

    url = f"https://services.leadconnectorhq.com/contacts/{contact_id}"
    headers = {
        "Authorization": f"Bearer {ghl_token}",
        "Content-Type": "application/json",
        "Version": "2021-07-28"
    }
    
    try:
        response = requests.put(url, json=data, headers=headers)
        response.raise_for_status()
        print(f"Successfully updated GHL contact {contact_id}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to update GHL contact {contact_id}: {e}")

@shared_task
def process_audit_task(candidate_id):
    try:
        candidate = Candidate.objects.get(id=candidate_id)
    except Candidate.DoesNotExist:
        print(f"Candidate {candidate_id} not found.")
        return

    # Initialize Vector Service
    vector_service = VectorService()
    
    # Retrieval: Find relevant rules
    # We search for rules related to the target region and profession
    query = f"regulations for {candidate.profession} in {candidate.target_region} 2026 rules exam limit recency"
    relevant_docs = vector_service.search_rules(query, k=5)
    context_text = "\n\n".join([doc.page_content for doc in relevant_docs])

    # Analysis: Use GPT-4
    llm = ChatOpenAI(model="gpt-4", temperature=0, openai_api_key=settings.OPENAI_API_KEY)

    prompt_template = ChatPromptTemplate.from_template("""
    You are an expert credential auditor for international healthcare professionals migrating to {target_region}.
    
    Analyze the following candidate CV against the provided 2026 regulatory rules.
    
    Regulatory Rules (Context):
    {context}
    
    Candidate CV:
    {cv_text}
    
    Your task is to:
    1. Check for the 7-year exam limit rule.
    2. Check for recency of practice requirements.
    3. Determine if the candidate is eligible for a 'Fast Track' process.
    4. Assign a readiness score (0-100).
    
    Output MUST be a valid JSON object with the following structure:
    {{
        "readiness_score": <int>,
        "is_fast_track_eligible": <bool>,
        "audit_details": {{
            "exam_limit_check": "<string>",
            "recency_check": "<string>",
            "gaps_identified": ["<string>", ...],
            "recommendations": ["<string>", ...]
        }}
    }}
    """)

    messages = prompt_template.format_messages(
        target_region=candidate.target_region,
        context=context_text,
        cv_text=candidate.resume_text
    )

    try:
        response = llm.invoke(messages)
        content = response.content
        
        # Parse JSON response
        # Sometimes LLMs wrap JSON in markdown code blocks, strip them if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        audit_result = json.loads(content)
        
        # Update Candidate
        candidate.readiness_score = audit_result.get("readiness_score")
        candidate.is_fast_track_eligible = audit_result.get("is_fast_track_eligible", False)
        candidate.audit_report_json = audit_result
        candidate.save()
        
        # Update GHL
        ghl_data = {
            "customField": {
                "readiness_score": candidate.readiness_score,
                "fast_track_eligible": candidate.is_fast_track_eligible
            },
            "tags": ["audited", "fast_track"] if candidate.is_fast_track_eligible else ["audited"]
        }
        update_ghl_contact(candidate.ghl_contact_id, ghl_data)
        
        print(f"Successfully audited candidate {candidate_id}")

    except json.JSONDecodeError:
        print(f"Failed to parse JSON from LLM response for candidate {candidate_id}")
    except Exception as e:
        print(f"Error processing audit for candidate {candidate_id}: {e}")
