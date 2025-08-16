#!/bin/bash

# ApexAnalytics AI - Deployment Script for apexanalytics-ai.space
echo "🚀 Deploying ApexAnalytics AI to apexanalytics-ai.space..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    print_status "Installing Railway CLI..."
    npm install -g @railway/cli
fi

# Login to Railway
print_status "Logging into Railway..."
railway login

# Initialize Railway project (if not already done)
if [ ! -f .railway ]; then
    print_status "Initializing Railway project..."
    railway init
fi

# Set environment variables
print_status "Setting environment variables..."
railway variables set FLASK_ENV=production
railway variables set SECRET_KEY=$(openssl rand -hex 32)

# Deploy to Railway
print_status "Deploying application..."
railway up

# Wait for deployment
print_status "Waiting for deployment to complete..."
sleep 30

# Get the deployment URL
print_status "Getting deployment URL..."
DEPLOY_URL=$(railway status --json | jq -r '.deployment.url')

print_success "🎉 Deployment successful!"
echo ""
echo "📱 Application URLs:"
echo "   Railway URL: $DEPLOY_URL"
echo "   Custom Domain: https://apexanalytics-ai.space"
echo "   www Domain: https://www.apexanalytics-ai.space"
echo ""

print_status "Next steps:"
echo "1. Add custom domain in Railway dashboard:"
echo "   - Go to Railway dashboard"
echo "   - Navigate to your project"
echo "   - Go to Settings > Domains"
echo "   - Add: apexanalytics-ai.space"
echo "   - Add: www.apexanalytics-ai.space"
echo ""
echo "2. Configure DNS records:"
echo "   Type: CNAME"
echo "   Name: @"
echo "   Value: $DEPLOY_URL"
echo ""
echo "3. Set API keys in Railway dashboard:"
echo "   - ODDS_API_KEY"
echo "   - ESPN_API_KEY"
echo "   - SPORTSRADAR_API_KEY"
echo "   - WEATHER_API_KEY"
echo "   - TWITTER_API_KEY"
echo ""
echo "4. SSL certificate will be automatically provisioned"
echo ""
print_success "Your ApexAnalytics AI will be live at https://apexanalytics-ai.space"
echo ""
echo "🔧 Management Commands:"
echo "   View logs: railway logs"
echo "   Open app: railway open"
echo "   Update deployment: railway up"
