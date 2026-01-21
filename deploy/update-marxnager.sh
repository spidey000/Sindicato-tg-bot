#!/bin/bash
# Auto-deploy webhook for Marxnager Bot
# This script triggers Portainer stack redeployment via API

# Configuration - UPDATE THESE VALUES
STACK_NAME="marxnager-bot"
PORTAINER_URL="http://localhost:9000"  # Change to your Portainer URL
PORTAINER_USERNAME="admin"              # Your Portainer username
PORTAINER_PASSWORD="your-password"      # Your Portainer password
ENDPOINT_ID="1"                         # Check in Portainer URL (usually 1 for local)

# Get authentication token
echo "Authenticating with Portainer..."
TOKEN=$(curl -s -X POST "$PORTAINER_URL/api/auth" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$PORTAINER_USERNAME\",\"password\":\"$PORTAINER_PASSWORD\"}" \
  | jq -r '.jwt')

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
    echo "ERROR: Failed to authenticate with Portainer"
    exit 1
fi

echo "Authentication successful"

# Get stack ID
echo "Finding stack ID for $STACK_NAME..."
STACK_ID=$(curl -s -X GET "$PORTAINER_URL/api/stacks" \
  -H "Authorization: Bearer $TOKEN" \
  | jq -r ".[] | select(.Name==\"$STACK_NAME\") | .Id")

if [ -z "$STACK_ID" ]; then
    echo "ERROR: Stack '$STACK_NAME' not found"
    exit 1
fi

echo "Stack ID: $STACK_ID"

# Redeploy stack
echo "Triggering redeployment..."
RESPONSE=$(curl -s -X POST "$PORTAINER_URL/api/stacks/$STACK_ID/redeploy?endpointId=$ENDPOINT_ID" \
  -H "Authorization: Bearer $TOKEN")

echo "Redeploy triggered for $STACK_NAME"
echo "Check Portainer logs for progress"
