# 🚛 LPG Optimizer - Command Reference

## ⚡ Quick Commands

### Setup (First Time Only)

```bash
# Backend setup
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r backend/requirements.txt

# Frontend setup
cd frontend
npm install
cd ..
```

### Start Development

```bash
# Terminal 1: Backend
venv\Scripts\activate
python run.py
# → Backend at http://localhost:5000

# Terminal 2: Frontend  
cd frontend
npm start
# → Dashboard at http://localhost:3000
```

### Run Examples

```bash
# Show all algorithm examples
python examples.py
```

### Run Tests

```bash
# Run all tests
python tests.py

# Run specific test
python -m unittest tests.TestVAMSolver

# Verbose output
python tests.py -v
```

## 🐳 Docker Commands

```bash
# Build and start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop all
docker-compose down

# Remove volumes
docker-compose down -v

# Rebuild images
docker-compose build --no-cache
```

## 🧪 API Testing

```bash
# Health check
curl http://localhost:5000/api/health

# Get network topology
curl http://localhost:5000/api/network

# Get supply status
curl http://localhost:5000/api/supply/status

# Get demand forecast
curl "http://localhost:5000/api/demand/forecast?location=city_delhi&days=1"

# Run optimization
curl -X POST http://localhost:5000/api/optimize \
  -H "Content-Type: application/json" \
  -d '{"config": {"use_vam": true, "use_dp": true}}'

# Get latest results
curl http://localhost:5000/api/optimize/latest

# Get current allocation
curl http://localhost:5000/api/allocation/current
```

## 📁 Project Navigation

```bash
# Navigate to project
cd C:\Users\USER\lpg-optimizer

# View structure
tree /F  # Windows
ls -la   # Mac/Linux

# Backend files
ls backend/optimization/  # Core algorithms

# Frontend files
ls frontend/components/   # React components

# Documentation
ls *.md                   # All guides
```

## 🔧 Common Tasks

### Update Dependencies

```bash
# Python
pip install --upgrade -r backend/requirements.txt

# Node
cd frontend && npm update
```

### Clean Up

```bash
# Remove Python cache
rm -r __pycache__ *.pyc

# Remove node modules
rm -r frontend/node_modules
rm frontend/package-lock.json

# Remove Docker containers
docker-compose down
```

### Database Operations

```bash
# PostgreSQL connection
psql -h localhost -U lpg_admin -d lpg_optimizer

# Common queries
SELECT * FROM allocations;
SELECT * FROM demand_forecast;

# Backup
pg_dump lpg_optimizer > backup.sql

# Restore
psql lpg_optimizer < backup.sql
```

### File Operations

```bash
# View optimization algorithm
cat backend/optimization/vam_solver.py

# View API endpoints
grep "@app.route" backend/app.py

# Count lines of code
wc -l backend/**/*.py

# Find specific function
grep -n "def " backend/optimization/vam_solver.py
```

## 🚀 Deployment

```bash
# Local Docker
docker-compose up -d

# Check services
curl http://localhost:5000/api/health
curl http://localhost:3000

# View database
docker exec lpg-db psql -U lpg_admin -d lpg_optimizer -c "SELECT version();"

# Check Redis
docker exec lpg-cache redis-cli PING
```

## 🐛 Troubleshooting

```bash
# Check if ports are in use
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # Mac/Linux

# Kill process on port
taskkill /PID <PID> /F        # Windows
kill -9 <PID>                 # Mac/Linux

# Check Python version
python --version

# Check Node version
node --version

# Test imports
python -c "import numpy; print(numpy.__version__)"

# Run with debug info
set FLASK_DEBUG=1 && python run.py  # Windows
FLASK_DEBUG=1 python run.py          # Mac/Linux
```

## 📊 Monitoring

```bash
# Backend metrics (if Prometheus enabled)
curl http://localhost:5000/metrics

# Database connections
psql -c "SELECT * FROM pg_stat_activity;"

# System resources
docker stats

# Logs
tail -f backend/logs/lpg_optimizer.log
```

## 📚 Code Quality

```bash
# Lint Python code
pylint backend/

# Format code
black backend/

# Type checking
mypy backend/

# Coverage report
coverage run -m pytest
coverage report
```

## 🎯 Development Workflow

```bash
# 1. Create new feature branch
git checkout -b feature/new-algorithm

# 2. Write code in backend/optimization/
# 3. Add tests in tests.py
# 4. Run tests locally
python tests.py

# 5. Format code
black backend/

# 6. Commit and push
git add .
git commit -m "feat: add new algorithm"
git push origin feature/new-algorithm

# 7. Create pull request
```

## 🔒 Security

```bash
# Generate secure .env
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Check dependencies for vulnerabilities
pip install safety
safety check

# HTTPS certificate generation
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem -keyout key.pem -days 365
```

## 📈 Performance Testing

```bash
# Load test with Apache Bench
ab -n 1000 -c 100 http://localhost:5000/api/health

# Optimization timing
time python examples.py

# Memory profiling
pip install memory-profiler
python -m memory_profiler examples.py

# Profiling
pip install py-spy
py-spy record -o profile.svg python examples.py
```

## 🌐 Network Diagnostics

```bash
# Check API connectivity
curl -v http://localhost:5000/api/health

# Trace requests
curl -H "User-Agent: Testing" -i http://localhost:5000/api

# DNS resolution
nslookup localhost

# Network interface
ipconfig  # Windows
ifconfig  # Mac/Linux
```

## 📝 File Editing

```bash
# View code with line numbers
cat -n backend/app.py | head -50

# Search in files
grep -n "def optimize" backend/app.py

# Find TODO/FIXME comments
grep -rn "TODO\|FIXME" backend/

# Replace text in files
sed -i 's/old_text/new_text/g' backend/app.py
```

## 🚀 Quick Deploy

```bash
# Prepare for deployment
docker build -t lpg-backend ./backend
docker build -t lpg-frontend ./frontend

# Tag images
docker tag lpg-backend myregistry.azurecr.io/lpg-backend:v1
docker tag lpg-frontend myregistry.azurecr.io/lpg-frontend:v1

# Push to registry
docker push myregistry.azurecr.io/lpg-backend:v1
docker push myregistry.azurecr.io/lpg-frontend:v1

# Deploy
kubectl apply -f deployment.yaml
```

## 💾 Data Management

```bash
# Export optimization results
curl http://localhost:5000/api/optimize/latest > results.json

# Import test data
python -c "from data_pipeline import *; load_test_data()"

# Query database
psql -c "COPY allocations TO 'export.csv' WITH CSV HEADER;"

# Backup entire system
tar -czf backup.tar.gz .
```

## 🔄 Continuous Integration

```bash
# Run full CI pipeline locally
python tests.py -v && \
  pylint backend/ && \
  docker build -t lpg-backend ./backend && \
  docker-compose up -d && \
  curl http://localhost:5000/api/health
```

## ⏱️ Scheduled Tasks

```bash
# Run optimization every hour (Windows Task Scheduler)
schtasks /create /tn "LPG-Optimize" \
  /tr "python C:\path\to\run.py" \
  /sc hourly

# Run optimization every hour (Linux cron)
0 * * * * cd /opt/lpg-optimizer && python run.py
```

## 📱 Mobile Testing

```bash
# Get local IP
ipconfig getifaddr en0  # Mac
hostname -I              # Linux

# Access from mobile
http://<YOUR_IP>:3000
```

---

## ✨ Useful Resources

- **Main Docs**: `README.md`
- **Quick Start**: `QUICKSTART.md`
- **Deployment**: `DEPLOYMENT.md`
- **Project Index**: `PROJECT_INDEX.md`
- **Examples**: Run `python examples.py`

## 📞 Support

- Check logs: `backend/logs/lpg_optimizer.log`
- Run tests: `python tests.py`
- View examples: `python examples.py`
- API docs: Check inline comments in `app.py`

---

**Last Updated**: 2026-04-17
