# Frontend Setup for Keycloak Authentication

## 1. Install Keycloak JS

In your frontend directory, run:

```
npm install keycloak-js
```

## 2. Keycloak Instance

The file `api/keycloak.js` is already set up to connect to your Keycloak server. Adjust the URL if your Keycloak is not running on localhost.

## 3. Usage

- Import the Keycloak instance in your components or API files as needed:
  ```js
  import keycloak from './api/keycloak';
  ```
- Use `keycloak.init()` on app load to trigger login and obtain a token.

## 4. Example Initialization (in App.js or index.js)

```js
import keycloak from './api/keycloak';

keycloak.init({ onLoad: 'login-required' }).then(authenticated => {
  if (!authenticated) {
    window.location.reload();
  } else {
    // Keycloak is authenticated, you can use keycloak.token
  }
});
```

## 5. Pass the Token to API Calls

- Use `keycloak.token` as the Bearer token in your API requests. 

---

## 6. How to Use the Chatbot UI (`ChatWindow`)

You can add the chatbot UI anywhere in your React app. Here is a typical usage in `App.js`:

```js
import React, { useEffect, useState } from 'react';
import keycloak from './api/keycloak';
import ChatWindow from './components/ChatWindow';

function App() {
  const [token, setToken] = useState(null);

  useEffect(() => {
    keycloak.init({ onLoad: 'login-required' }).then(authenticated => {
      if (authenticated) {
        setToken(keycloak.token);
      }
    });
  }, []);

  if (!token) return <div>Authenticating...</div>;

  return (
    <div>
      {/* Your other app content */}
      <ChatWindow token={token} />
    </div>
  );
}

export default App;
```

- The `<ChatWindow />` component manages its own open/close state and conversation state.
- The floating orange chat button will appear on the left. Clicking it opens the chat panel.
- All API calls are authenticated using the Keycloak token you pass as a prop. 