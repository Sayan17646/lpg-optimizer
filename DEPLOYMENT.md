# LPG Optimization System - Production Deployment Guide

## 🚀 Production Deployment

### Prerequisites
- Docker & Docker Compose installed
- AWS/GCP/Azure account (for cloud deployment)
- SSL certificates (for HTTPS)
- Domain name (optional but recommended)

### Local Docker Deployment

#### 1. Build and Run with Docker Compose

```bash
# From project root
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

Application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- Nginx Proxy: http://localhost

#### 2. Access Services

```bash
# Connect to PostgreSQL
psql -h localhost -U lpg_admin -d lpg_optimizer

# Check Redis
redis-cli -h localhost

# API health check
curl http://localhost:5000/api/health
```

### Cloud Deployment

#### AWS Deployment (ECS/Fargate)

```bash
# 1. Create ECR repository
aws ecr create-repository --repository-name lpg-backend
aws ecr create-repository --repository-name lpg-frontend

# 2. Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

# 3. Build and push images
docker build -t lpg-backend ./backend
docker tag lpg-backend:latest <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/lpg-backend:latest
docker push <ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/lpg-backend:latest

# 4. Deploy using CloudFormation or Terraform
# See infrastructure/ folder for IaC templates
```

#### Google Cloud (Cloud Run)

```bash
# 1. Enable Cloud Run API
gcloud services enable run.googleapis.com

# 2. Build and deploy backend
gcloud run deploy lpg-backend \
  --source=./backend \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated

# 3. Deploy frontend to Cloud Storage + CDN
gsutil mb gs://lpg-dashboard-prod
gsutil -m cp -r ./frontend/build/* gs://lpg-dashboard-prod/
```

#### Kubernetes Deployment

```bash
# Create namespace
kubectl create namespace lpg

# Deploy using Helm charts (see charts/ directory)
helm install lpg-optimizer ./charts/lpg-optimizer \
  --namespace lpg \
  --values values-prod.yaml

# Check deployment
kubectl get all -n lpg

# Port forward for testing
kubectl port-forward -n lpg svc/lpg-backend 5000:5000
```

### Environment Configuration

#### Production .env

```env
# Application
FLASK_ENV=production
DEBUG=False

# Database
DATABASE_URL=postgresql://user:password@prod-db.amazonaws.com:5432/lpg_optimizer
SQLALCHEMY_POOL_SIZE=20
SQLALCHEMY_POOL_RECYCLE=3600

# Redis Cache
REDIS_URL=redis://prod-cache.redis.cache.windows.net:6379

# API
API_HOST=0.0.0.0
API_PORT=5000
API_WORKERS=8
CORS_ORIGINS=https://lpg-dashboard.com

# Monitoring
LOG_LEVEL=INFO
LOG_FILE=/var/log/lpg/app.log
SENTRY_DSN=https://xxx@sentry.io/xxx

# Security
SECRET_KEY=<generate-strong-key>
JWT_SECRET=<generate-strong-key>
ENABLE_HTTPS=True
SSL_CERT=/etc/ssl/certs/cert.pem
SSL_KEY=/etc/ssl/private/key.pem

# Optimization
OPTIMIZATION_INTERVAL_HOURS=6
MAX_OPTIMIZATION_TIME_SECONDS=30
CACHE_TTL_SECONDS=300
```

### Monitoring & Logging

#### Setup Monitoring

```bash
# 1. Install Prometheus metrics
pip install prometheus-flask-exporter

# 2. Configure in app.py
from prometheus_flask_exporter import PrometheusMetrics
metrics = PrometheusMetrics(app)

# 3. Deploy Prometheus & Grafana
docker run -d -p 9090:9090 prom/prometheus
docker run -d -p 3001:3000 grafana/grafana
```

#### Log Aggregation (ELK Stack)

```bash
# Deploy ELK
docker-compose -f docker-compose.elk.yml up -d

# Configure Python logging
import logging
from pythonjsonlogger import jsonlogger

handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)
```

### Database Migration

```bash
# Create database
createdb lpg_optimizer

# Run migrations (implement as needed)
python manage.py db upgrade

# Backup database
pg_dump lpg_optimizer > backup_$(date +%Y%m%d).sql

# Restore from backup
psql lpg_optimizer < backup_20260417.sql
```

### SSL/TLS Setup

```bash
# Generate self-signed certificate (for testing)
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Use Let's Encrypt (for production)
certbot certonly --standalone -d lpg-optimizer.com
```

### CI/CD Pipeline

#### GitHub Actions Example

```yaml
name: Deploy LPG Optimizer

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Run tests
      run: |
        python -m venv venv
        source venv/bin/activate
        pip install -r backend/requirements.txt
        python tests.py
    
    - name: Build Docker images
      run: |
        docker build -t lpg-backend ./backend
        docker build -t lpg-frontend ./frontend
    
    - name: Push to ECR
      env:
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      run: |
        aws ecr-public get-login-password | docker login --username AWS --password-stdin public.ecr.aws
        docker push lpg-backend:latest
        docker push lpg-frontend:latest
    
    - name: Deploy to ECS
      run: |
        aws ecs update-service --cluster lpg-prod --service lpg-backend --force-new-deployment
```

### Performance Optimization

#### Caching Strategy

```python
# Cache optimization results
@app.route('/api/optimize')
@cache.cached(timeout=300)  # Cache for 5 minutes
def optimize():
    ...
```

#### Database Indexing

```sql
-- Add indexes for frequently queried fields
CREATE INDEX idx_demand_location ON demand(location_id);
CREATE INDEX idx_supply_date ON supply(date);
CREATE INDEX idx_allocation_from_to ON allocations(from_location, to_location);
```

#### API Rate Limiting

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/optimize')
@limiter.limit("10/minute")
def optimize():
    ...
```

### Scaling Considerations

#### Horizontal Scaling

```yaml
# Kubernetes horizontal pod autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: lpg-backend-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: lpg-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

#### Load Balancing

```nginx
# Nginx upstream configuration
upstream backend_cluster {
    least_conn;
    server backend-1:5000;
    server backend-2:5000;
    server backend-3:5000;
}

server {
    location /api/ {
        proxy_pass http://backend_cluster;
    }
}
```

### Disaster Recovery

#### Backup Strategy

```bash
# Automated daily backup script
#!/bin/bash
BACKUP_DIR="/backups"
DB_NAME="lpg_optimizer"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup database
pg_dump $DB_NAME | gzip > $BACKUP_DIR/db_$TIMESTAMP.sql.gz

# Upload to S3
aws s3 cp $BACKUP_DIR/db_$TIMESTAMP.sql.gz s3://lpg-backups/

# Keep only last 30 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete
```

### Security Best Practices

1. **Enable HTTPS** everywhere
2. **Use environment variables** for secrets
3. **Implement API authentication** (JWT tokens)
4. **Rate limiting** on all endpoints
5. **SQL injection prevention** (use parameterized queries)
6. **CORS** properly configured
7. **Security headers** (CSP, X-Frame-Options, etc.)

### Post-Deployment Checklist

- [ ] SSL/TLS certificates valid
- [ ] Database backups configured
- [ ] Monitoring & alerts active
- [ ] Logging aggregated
- [ ] API rate limiting enabled
- [ ] CORS properly configured
- [ ] Load testing completed
- [ ] Disaster recovery tested
- [ ] Security scanning passed
- [ ] Performance targets met

---

**Deployment Status**: Ready for production  
**Estimated Deployment Time**: 1-2 hours  
**Support**: See infrastructure/ documentation
