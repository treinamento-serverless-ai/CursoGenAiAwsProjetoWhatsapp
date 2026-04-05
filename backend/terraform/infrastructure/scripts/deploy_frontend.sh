#!/bin/bash
set -euo pipefail

echo "=========================================="
echo "  Frontend Deploy Automation"
echo "=========================================="

FRONTEND_DIR=$(cd "$FRONTEND_DIR" && pwd)
ENV_DIR="$FRONTEND_DIR/src/environments"

# --- Determine redirect/logout URIs ---
if [ -n "$FRONTEND_DOMAIN" ]; then
  AWS_REDIRECT="https://$FRONTEND_DOMAIN/callback"
  AWS_LOGOUT="https://$FRONTEND_DOMAIN"
else
  AWS_REDIRECT="http://localhost:4200/callback"
  AWS_LOGOUT="http://localhost:4200"
fi

# --- Step 1: Generate environment files ---
echo "[1/3] Generating Angular environment files..."

cat > "$ENV_DIR/environment.localhost.ts" <<EOF
export const environment = {
  production: false,
  apiUrl: '$API_URL',
  cognito: {
    userPoolId: '$COGNITO_USER_POOL_ID',
    clientId: '$COGNITO_CLIENT_ID',
    domain: '$COGNITO_DOMAIN',
    redirectUri: 'http://localhost:4200/callback',
    logoutUri: 'http://localhost:4200',
  },
};
EOF

cat > "$ENV_DIR/environment.aws.ts" <<EOF
export const environment = {
  production: true,
  apiUrl: '$API_URL',
  cognito: {
    userPoolId: '$COGNITO_USER_POOL_ID',
    clientId: '$COGNITO_CLIENT_ID',
    domain: '$COGNITO_DOMAIN',
    redirectUri: '$AWS_REDIRECT',
    logoutUri: '$AWS_LOGOUT',
  },
};
EOF

echo "  -> environment.localhost.ts generated"
echo "  -> environment.aws.ts generated"

# --- Step 2: Build Angular app ---
echo "[2/3] Building Angular app (production)..."
cd "$FRONTEND_DIR"
npm install --silent --legacy-peer-deps
npx ng build --configuration=production

# --- Step 3: Sync to S3 ---
echo "[3/3] Syncing build to S3 bucket: $S3_BUCKET"

# Angular 21 outputs to dist/<project-name>/browser
BUILD_DIR="$FRONTEND_DIR/dist/agendente/browser"
if [ ! -d "$BUILD_DIR" ]; then
  # Fallback: try dist/agendente
  BUILD_DIR="$FRONTEND_DIR/dist/agendente"
fi

aws s3 sync "$BUILD_DIR" "s3://$S3_BUCKET" --delete --region "$AWS_REGION"

echo "=========================================="
echo "  Frontend deploy complete!"
echo "=========================================="
