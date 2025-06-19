import os
import requests

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/v1/generate")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

def generate_response(message: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": message
    }
    try:
        print(f"[INFO] Appel Ollama: {OLLAMA_URL} | Prompt: {message}")
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        # Selon la version d'Ollama, la clé peut être 'response' ou 'message'
        return data.get("response") or data.get("message") or str(data)
    except requests.Timeout:
        print("[ERROR] Timeout lors de l'appel à Ollama")
        raise Exception("Le service IA ne répond pas (timeout)")
    except requests.RequestException as e:
        print(f"[ERROR] Ollama: {str(e)}")
        raise Exception(f"Erreur lors de l'appel à Ollama: {str(e)}")