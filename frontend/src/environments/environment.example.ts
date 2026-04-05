export const environment = {
  production: false,
  apiUrl: 'https://api.dev.example.com',
  cognito: {
    userPoolId: 'COGNITO_USER_POOL_ID',
    clientId: 'COGNITO_CLIENT_ID',
    domain: 'example-dev.auth.us-east-1.amazoncognito.com',
    redirectUri: 'http://localhost:4200/callback',
    logoutUri: 'http://localhost:4200',
  },
};
