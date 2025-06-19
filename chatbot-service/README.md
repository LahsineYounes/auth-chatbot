# Chatbot Service

## Keycloak Client Setup

### 1. Import the Realm
- Go to Keycloak admin console (`http://<auth-service-ip>:8080/admin`).
- Log in as admin.
- Click **Add realm** → **Import**.
- Select `auth-microservice/keycloak/realm-export.json` and import.

### 2. Verify the Client Configuration
- Go to your realm (`ent_est-realm`).
- Go to **Clients** → Find `ent_est-client`.
- Check:
  - **Client ID:** `ent_est-client`
  - **Client Protocol:** `openid-connect`
  - **Access Type:** `confidential`
  - **Valid Redirect URIs:** `*` (for dev; restrict in prod)
  - **Web Origins:** `*` (for dev; restrict in prod)
  - **Service Accounts Enabled:** `ON`
  - **Direct Access Grants Enabled:** `ON`
- Go to **Credentials** tab:
  - **Secret:** Should match your `.env` (`gZA4j6vLFk6YQcWIme7KvThJBJCPCYwC`)

### 3. Test the Client
- Get a token (example with curl):
  ```sh
  curl -X POST 'http://localhost:8080/realms/ent_est-realm/protocol/openid-connect/token' \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -d 'client_id=ent_est-client' \
    -d 'client_secret=gZA4j6vLFk6YQcWIme7KvThJBJCPCYwC' \
    -d 'grant_type=password' \
    -d 'username=student1' \
    -d 'password=student123'
  ```
- Use the `access_token` in API calls:
  - Add header: `Authorization: Bearer <access_token>`

### 4. User Roles
- Users and roles (`etudiant`, `enseignant`, `admin`) are pre-configured in the realm export.
- Add more users in Keycloak admin console under **Users** if needed. 