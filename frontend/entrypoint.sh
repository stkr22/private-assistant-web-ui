#!/bin/sh
set -e

# Validate required configuration
if [ -z "$VITE_API_URL" ]; then
  echo "❌ ERROR: VITE_API_URL environment variable is required"
  exit 1
fi

# OAuth validation: both or neither
if [ -n "$VITE_OAUTH_AUTHORITY" ] && [ -z "$VITE_OAUTH_CLIENT_ID" ]; then
  echo "❌ ERROR: VITE_OAUTH_AUTHORITY is set but VITE_OAUTH_CLIENT_ID is not"
  exit 1
fi

if [ -z "$VITE_OAUTH_AUTHORITY" ] && [ -n "$VITE_OAUTH_CLIENT_ID" ]; then
  echo "❌ ERROR: VITE_OAUTH_CLIENT_ID is set but VITE_OAUTH_AUTHORITY is not"
  exit 1
fi

# Generate config.js
cat > /var/cache/nginx/config/config.js << 'EOF'
// Runtime configuration (auto-generated at container startup)
// DO NOT EDIT - This file is regenerated when the container starts
window.runtimeConfig = {
EOF

echo "  apiUrl: \"$VITE_API_URL\"," >> /var/cache/nginx/config/config.js

# Add OAuth configuration if both authority and clientId are present
if [ -n "$VITE_OAUTH_AUTHORITY" ] && [ -n "$VITE_OAUTH_CLIENT_ID" ]; then
  cat >> /var/cache/nginx/config/config.js << EOF
  oauth: {
    authority: "$VITE_OAUTH_AUTHORITY",
    clientId: "$VITE_OAUTH_CLIENT_ID",
EOF

  if [ -n "$VITE_OAUTH_REDIRECT_URI" ]; then
    echo "    redirectUri: \"$VITE_OAUTH_REDIRECT_URI\"," >> /var/cache/nginx/config/config.js
  fi

  if [ -n "$VITE_OAUTH_SCOPE" ]; then
    echo "    scope: \"$VITE_OAUTH_SCOPE\"," >> /var/cache/nginx/config/config.js
  fi

  echo "  }," >> /var/cache/nginx/config/config.js
fi

echo "};" >> /var/cache/nginx/config/config.js

echo "✅ Runtime configuration generated:"
cat /var/cache/nginx/config/config.js

# Start nginx
exec nginx -g 'daemon off;'
