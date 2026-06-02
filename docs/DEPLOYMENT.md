# MaterialGraph Deployment Guide

## Overview

MaterialGraph is deployed as a production-oriented FastAPI backend using:

* AWS EC2 (Ubuntu 24.04 LTS)
* Neon PostgreSQL
* SQLAlchemy
* Alembic
* systemd
* Nginx

Current deployment architecture:

Internet
↓
Nginx (Port 80)
↓
Uvicorn (127.0.0.1:8000)
↓
FastAPI
↓
Neon PostgreSQL

---

# Infrastructure

## AWS EC2

Instance Name:

materialgraph-api

Region:

ap-south-1 (Mumbai)

Instance Type:

t3.micro

Operating System:

Ubuntu Server 24.04 LTS

Elastic IP:

35.154.84.47

---

# Database

Provider:

Neon PostgreSQL

Database:

neondb

Production Branch:

production

SSL:

Required

Connection Pooling:

Enabled for application traffic

Direct Connection:

Used for Alembic migrations

---

# Environment Variables

Production environment file:

/opt/materialgraph/.env

Required variables:

DATABASE_URL=
DATABASE_MIGRATION_URL=
MATERIALS_PROJECT_API_KEY=
ENVIRONMENT=production
LOG_LEVEL=INFO

Important:

* Do not commit .env files.
* Production secrets are managed directly on EC2.
* Local development and production use separate environment files.

---

# Initial Server Setup

Update packages:

sudo apt update
sudo apt upgrade -y

Install dependencies:

sudo apt install -y python3-pip python3-venv git nginx

Verify:

python3 --version
git --version
nginx -v

---

# Application Deployment

Create deployment directory:

sudo mkdir -p /opt/materialgraph
sudo chown ubuntu:ubuntu /opt/materialgraph

Clone repository:

cd /opt/materialgraph

git clone https://github.com/jithinmathws/materialgraph.git

Enter project:

cd materialgraph

Create virtual environment:

python3 -m venv .venv

Activate:

source .venv/bin/activate

Install dependencies:

pip install --upgrade pip

pip install -e .

---

# Database Migration

Run migrations:

alembic upgrade head

Verify revision:

alembic current

Verify history:

alembic history

---

# FastAPI Verification

Manual startup:

uvicorn app.main:app --host 0.0.0.0 --port 8000

Health endpoint:

http://<server-ip>:8000/health

Expected:

{
"status": "ok"
}

---

# systemd Service

Service file:

/etc/systemd/system/materialgraph.service

Commands:

sudo systemctl daemon-reload

sudo systemctl start materialgraph

sudo systemctl enable materialgraph

Check status:

sudo systemctl status materialgraph

View logs:

sudo journalctl -u materialgraph -f

Restart:

sudo systemctl restart materialgraph

---

# Nginx Configuration

Site file:

/etc/nginx/sites-available/materialgraph

Configuration:

server {
listen 80 default_server;
server_name _;

```
location / {
    proxy_pass http://127.0.0.1:8000;

    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

}

Enable:

sudo ln -s /etc/nginx/sites-available/materialgraph /etc/nginx/sites-enabled/materialgraph

Disable default site:

sudo rm /etc/nginx/sites-enabled/default

Validate:

sudo nginx -t

Reload:

sudo systemctl reload nginx

---

# Security Group Rules

Inbound:

SSH (22)
Source: My IP

HTTP (80)
Source: Anywhere

HTTPS (443)
Source: Anywhere

Port 8000 is not publicly exposed.

---

# Production Endpoints

API Root:

http://35.154.84.47

Swagger UI:

http://35.154.84.47/docs

Health Check:

http://35.154.84.47/health

---

# Common Operations

Pull latest code:

cd /opt/materialgraph/materialgraph

git pull origin main

source .venv/bin/activate

Run migrations:

alembic upgrade head

Restart service:

sudo systemctl restart materialgraph

Verify:

curl http://127.0.0.1/health

---

# Troubleshooting

Check service:

sudo systemctl status materialgraph

Check logs:

sudo journalctl -u materialgraph -n 100 --no-pager

Check nginx:

sudo systemctl status nginx

Validate nginx:

sudo nginx -t

Restart nginx:

sudo systemctl restart nginx

Check listening ports:

sudo ss -tulpn

---

# Deployment History

Phase 1 Production Deployment

Date:

June 2026

Features:

* FastAPI backend
* Material candidate screening
* Candidate comparison
* Scenario ranking
* Sensitivity analysis
* Substitution analysis
* Materials Project integration
* Neon PostgreSQL
* Production AWS deployment
