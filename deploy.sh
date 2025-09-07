#!/bin/bash

set -e  # Exit on any error

echo "Starting deployment of the shared data structure between api and sp_worker..."

# Step 1: Create shared volume if it doesn't exist
echo "Managing shared volume..."
if ! docker volume ls | grep -q "airflow_shared-data"; then
    docker volume create airflow_shared-data
    echo "Created volume: airflow_shared-data"
else
    echo "Volume airflow_shared-data already exists"
fi

# Step 1.5: Fix permissions RIGHT AFTER creating volume, BEFORE starting containers
echo "Setting up volume permissions for both Airflow (50000:0) and API (1000:0) access..."
docker run --rm -v airflow_shared-data:/shared-data alpine sh -c "
    mkdir -p /shared-data/raw_data &&
    chown -R 50000:0 /shared-data &&
    chmod -R 775 /shared-data &&
    echo 'Volume set up for shared access between Airflow and API'
"

# Step 2: Deploy the Smart Pricing Airflow worker
echo "Deploying sp_worker..."
cd sp_worker
./deploy.sh
cd ..

# Step 3: Deploy API service
echo "Deploying API service..."
cd api
./deploy.sh
cd ..

echo "Deployment complete!"