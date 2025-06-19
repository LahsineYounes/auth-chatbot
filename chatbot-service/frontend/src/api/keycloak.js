import Keycloak from 'keycloak-js';

const keycloak = new Keycloak({
  url: 'http://localhost:8080', // Change to your Keycloak server URL if needed
  realm: 'ent_est-realm',
  clientId: 'ent_est-client',
});

export default keycloak; 