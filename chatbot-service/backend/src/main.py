from fastapi import FastAPI
from fastapi_keycloak import FastAPIKeycloak
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

keycloak_url = os.getenv("KEYCLOAK_URL")
realm = os.getenv("KEYCLOAK_REALM")
client_id = os.getenv("KEYCLOAK_CLIENT_ID")
client_secret = os.getenv("KEYCLOAK_CLIENT_SECRET")

keycloak = FastAPIKeycloak(
    server_url=keycloak_url,
    client_id=client_id,
    client_secret=client_secret,
    admin_client_secret=client_secret,
    realm=realm,
    callback_uri="http://localhost:8000/callback"
)

keycloak.add_swagger_config(app)

from .chatbot_routes import router as chatbot_router
app.include_router(chatbot_router)