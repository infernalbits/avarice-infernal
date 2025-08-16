#!/bin/bash

# Railway Deployment Script for Sports Betting AI
echo "🚀 Deploying to Railway..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Login to Railway
echo "Logging into Railway..."
railway login

# Initialize Railway project (if not already done)
if [ ! -f .railway ]; then
    echo "Initializing Railway project..."
    railway init
fi

# Deploy to Railway
echo "Deploying application..."
railway up

# Get the deployment URL
echo "Getting deployment URL..."
DEPLOY_URL=$(railway status --json | jq -r '.deployment.url')

echo "🎉 Deployment successful!"
echo "Your app is live at: $DEPLOY_URL"
echo ""
echo "Next steps:"
echo "1. Add custom domain in Railway dashboard"
echo "2. Set environment variables"
echo "3. Configure SSL certificate"
echo ""
echo "To view logs: railway logs"
echo "To open app: railway open"
