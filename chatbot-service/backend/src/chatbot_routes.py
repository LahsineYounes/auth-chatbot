from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, constr
from typing import Optional # Kept for now, might be used by RulesManager or other parts

from .main import keycloak # Assuming keycloak is initialized in main
from fastapi_keycloak import OIDCUser
from .ollama import generate_response
from .rules_manager import RulesManager # Assuming RulesManager class exists

# Initialize router and RulesManager
router = APIRouter()
rules_manager = RulesManager() # Or however it's supposed to be initialized

# Request and Response Models
class ChatRequest(BaseModel):
    message: constr

class ChatResponse(BaseModel):
    response: str
    source: str  # 'rule' or 'ai'

# Endpoints
@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user: OIDCUser = Depends(keycloak.get_current_user(roles=["etudiant", "enseignant"])) # Keycloak security
):
    # Basic logging (FastAPI will also log requests)
    print(f"User {user.email} (roles: {user.roles}) sent message: {request.message}")
    try:
        # 1. Try rule-based response
        rule_response = rules_manager.find_matching_rule(request.message)
        if rule_response:
            print(f"Rule matched for: {request.message}")
            return ChatResponse(response=rule_response, source="rule")

        # 2. If no rule, use AI
        print(f"No rule matched for: {request.message}. Forwarding to AI.")
        ai_response = generate_response(request.message) # From ollama.py
        if ai_response is None:
            # Handle case where ollama.py might return None if response key is missing
            raise HTTPException(status_code=500, detail="AI service returned an unexpected response.")
        return ChatResponse(response=ai_response, source="ai")

    except HTTPException as e:
        # Re-raise HTTPExceptions directly
        raise e
    except Exception as e:
        print(f"[ERROR] Chat endpoint error: {str(e)}") # Server-side log
        # Provide a generic error message to the client
        raise HTTPException(status_code=500, detail="An internal error occurred in the chatbot.")