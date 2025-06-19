import keycloak from './keycloak'; // Corrected path to the Keycloak instance

const API_URL = 'http://localhost:8000'; // Use localhost for local dev

export async function sendMessageToChatbot(message, token) {
  if (!token) {
    throw new Error("Aucun token disponible. Veuillez vous connecter.");
  }
  const response = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": `Bearer ${token}`
    },
    body: JSON.stringify({ message })
  });
  if (!response.ok) {
    throw new Error("Erreur lors de l'envoi du message au chatbot");
  }
  return response.json();
}