#!/bin/bash

# AI Server Production Deployment Script

set -e

echo "🚀 Starting AI Server Production Deployment..."

echo "Starting deployment of the shared data structure between api and sp_worker..."

# ------ SP v2 utils -----

echo "Setting up shared volume..."
docker volume create airflow_shared-data 2>/dev/null || echo "Volume already exists"

# Ensure Alpine exists locally (avoid credential errors)
if ! docker image inspect alpine:latest >/dev/null 2>&1; then
    echo "Pulling alpine:latest..."
    docker pull alpine:latest
fi

echo "Fixing volume permissions for Airflow (50000:0) and API (1000:0)..."
docker run --rm -v airflow_shared-data:/shared-data alpine sh -c "
    mkdir -p /shared-data/{raw_data,mlruns,outputs,processed,properties} &&
    chown -R 50000:0 /shared-data &&
    chmod -R 775 /shared-data &&
    echo 'Volume ready for Airflow & API'
"

# # Step 1: Create shared volume if it doesn't exist
# echo "Managing shared volume..."
# if ! docker volume ls | grep -q "airflow_shared-data"; then
#     docker volume create airflow_shared-data
#     echo "Created volume: airflow_shared-data"
# else
#     echo "Volume airflow_shared-data already exists"
# fi

# # Step 1.5: Fix permissions RIGHT AFTER creating volume, BEFORE starting containers
# echo "Setting up volume permissions for both Airflow (50000:0) and API (1000:0) access..."
# docker run --rm -v airflow_shared-data:/shared-data alpine sh -c "
#     mkdir -p /shared-data/raw_data &&
#     chown -R 50000:0 /shared-data &&
#     chmod -R 775 /shared-data &&
#     echo 'Volume set up for shared access between Airflow and API'
# "

# Step 2: Deploy the Smart Pricing Airflow worker
echo "Deploying sp_worker..."
cd sp_worker
chmod +x deploy.sh # Adding execute permissions
./deploy.sh
cd ..

# Step 3: Deploy API service
echo "Deploying API services..."
cd app
./deploy.sh
cd ..

echo "Deployment complete!"


echo "✅ Deployment complete!"
echo "🌐 Access the server at: http://localhost:8005"
echo "📖 API documentation: http://localhost:8005/docs"
