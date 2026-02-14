#!/bin/bash

# Setup script for Credit Approval System

echo "==================================="
echo "Credit Approval System - Setup"
echo "==================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✓ Docker and Docker Compose are installed"
echo ""

# Build and start services
echo "Building and starting services..."
docker-compose up -d --build

echo ""
echo "Waiting for services to be ready..."
sleep 10

# Run migrations
echo ""
echo "Running database migrations..."
docker-compose exec -T web python manage.py migrate

# Ingest data
echo ""
echo "Ingesting initial data from Excel files..."
docker-compose exec -T web python manage.py ingest_data

echo ""
echo "==================================="
echo "Setup Complete!"
echo "==================================="
echo ""
echo "The application is now running at: http://localhost:8000"
echo ""
echo "Useful commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop services: docker-compose down"
echo "  - Create superuser: docker-compose exec web python manage.py createsuperuser"
echo ""
