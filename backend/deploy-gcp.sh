#!/bin/bash

# GCP Deployment Script for SG AI Backend
# Make sure to update the variables below with your project details

set -e

# Configuration - UPDATE THESE VALUES
PROJECT_ID="your-project-id"
REGION="us-central1"
SERVICE_NAME="sg-ai-backend"
DB_INSTANCE_NAME="sg-ai-db"
DB_NAME="mydb"
DB_USER="appuser"

echo "🚀 Starting GCP deployment for SG AI Backend"
echo "Project: $PROJECT_ID"
echo "Region: $REGION"

# Check if gcloud is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Please authenticate with gcloud first:"
    echo "   gcloud auth login"
    exit 1
fi

# Set the project
echo "📋 Setting GCP project..."
gcloud config set project $PROJECT_ID

# Enable required APIs
echo "🔧 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable sqladmin.googleapis.com

# Build and submit the Docker image
echo "🐳 Building Docker image..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Create Cloud SQL instance (if it doesn't exist)
echo "🗄️  Setting up Cloud SQL..."
if ! gcloud sql instances describe $DB_INSTANCE_NAME --quiet 2>/dev/null; then
    echo "Creating Cloud SQL instance..."
    gcloud sql instances create $DB_INSTANCE_NAME \
        --database-version=POSTGRES_14 \
        --tier=db-f1-micro \
        --region=$REGION \
        --storage-auto-increase
    
    echo "Creating database..."
    gcloud sql databases create $DB_NAME --instance=$DB_INSTANCE_NAME
    
    echo "Creating database user..."
    echo "Please enter a password for the database user:"
    gcloud sql users create $DB_USER --instance=$DB_INSTANCE_NAME --password-stdin
else
    echo "Cloud SQL instance already exists."
fi

# Deploy to Cloud Run
echo "☁️  Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --add-cloudsql-instances $PROJECT_ID:$REGION:$DB_INSTANCE_NAME \
    --set-env-vars ENVIRONMENT=production

echo "✅ Deployment completed!"
echo ""
echo "📝 Next steps:"
echo "1. Set up environment variables:"
echo "   gcloud run services update $SERVICE_NAME \\"
echo "     --set-env-vars DATABASE_URL='postgresql+asyncpg://$DB_USER:PASSWORD@/$DB_NAME?host=/cloudsql/$PROJECT_ID:$REGION:$DB_INSTANCE_NAME' \\"
echo "     --set-env-vars SECRET_KEY='your-secret-key'"
echo ""
echo "2. Run database migrations:"
echo "   - Connect to your Cloud SQL instance"
echo "   - Run: alembic upgrade head"
echo ""
echo "3. Configure your frontend to use the new backend URL"
echo ""
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)')
echo "🌐 Your service is available at: $SERVICE_URL" 