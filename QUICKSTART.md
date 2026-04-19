# LPG Optimization System - Complete Installation & Usage Guide

## 📋 Prerequisites

- Python 3.9+
- Node.js 16+
- npm or yarn
- Git
- PostgreSQL (optional, for production)

## 🚀 Installation

### Step 1: Clone/Setup Project

```bash
# Navigate to your lpg-optimizer folder
cd C:\Users\USER\lpg-optimizer
```

### Step 2: Backend Installation

```bash
# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install backend dependencies
cd backend
pip install -r requirements.txt
```

### Step 3: Frontend Installation

```bash
# From project root (in new terminal)
cd frontend

# Create React app if not exists
npx create-react-app . --template minimal

# Install additional dependencies
npm install axios react-router-dom recharts
```

### Step 4: Configuration

```bash
# From project root
cp .env.example .env

# Edit .env with your settings (optional for development)
```

## ▶️ Running the System

### Terminal 1: Backend Server

```bash
# From lpg-optimizer directory
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

python run.py
```

✅ Backend starts at: **http://localhost:5000**

### Terminal 2: Frontend Server

```bash
# From lpg-optimizer/frontend directory
npm start
```

✅ Frontend starts at: **http://localhost:3000**

## 📡 API Endpoints

### Quick Test
```bash
# Check if backend is running
curl http://localhost:5000/api/health

# Get network topology
curl http://localhost:5000/api/network

# Run optimization
curl -X POST http://localhost:5000/api/optimize \
  -H "Content-Type: application/json" \
  -d '{"config": {"use_vam": true}}'

# Get latest results
curl http://localhost:5000/api/optimize/latest

# Get supply status
curl http://localhost:5000/api/supply/status

# Get demand forecast
curl "http://localhost:5000/api/demand/forecast?location=city_delhi&days=1"
```

## 🧪 Testing

```bash
# Run unit tests
python tests.py

# Run specific test class
python -m unittest tests.TestVAMSolver

# Run with verbosity
python tests.py -v
```

## 📊 Dashboard Features

1. **Network Topology Map** - Visual representation of LPG distribution network
2. **Real-time Status** - Supply levels at each plant
3. **Demand Forecast** - 24-hour demand trends
4. **Optimization Results** - Cost breakdown, routes, allocations
5. **Supply Status** - Utilization rates by plant
6. **Allocation Heatmap** - Visual transport allocation matrix

## ⚙️ Configuration

Edit `.env` or use API `PUT /api/config`:

```env
OPTIMIZATION_INTERVAL_HOURS=6          # Reoptimize every 6 hours
SERVICE_LEVEL_TARGET=0.95              # 95% demand met
USE_VAM=True                           # Enable Vogel's method
USE_DP=True                            # Enable DP optimization
USE_NETWORK_FLOW=True                  # Enable network flow
```

## 🔧 Troubleshooting

### Backend won't start
```bash
# Check if port 5000 is in use
netstat -ano | findstr :5000  # Windows
lsof -i :5000  # Mac/Linux

# Kill process if needed
taskkill /PID <PID> /F  # Windows
kill -9 <PID>  # Mac/Linux
```

### Frontend connection issues
- Check CORS settings in `.env`
- Verify backend is running on port 5000
- Check browser console for errors

### Import errors in Python
```bash
# Ensure virtual environment is activated
# Reinstall packages
pip install --force-reinstall -r requirements.txt
```

## 📁 Project Structure Reference

```
lpg-optimizer/
├── backend/
│   ├── optimization/
│   │   ├── vam_solver.py           ← Transport problem
│   │   ├── dp_engine.py            ← Inventory & routing
│   │   ├── network_flow.py         ← Multi-level flows
│   │   └── __init__.py
│   ├── data_pipeline/
│   │   ├── data_fetcher.py         ← Real-time data
│   │   └── __init__.py
│   ├── models/
│   │   ├── data_models.py          ← Data structures
│   │   └── __init__.py
│   ├── app.py                      ← Flask API
│   ├── requirements.txt
│   └── __init__.py
├── frontend/
│   ├── App.jsx                     ← Main component
│   ├── App.css                     ← Styling
│   ├── components.jsx              ← Dashboard components
│   └── [React setup files]
├── run.py                          ← Main entry point
├── tests.py                        ← Unit tests
├── .env.example                    ← Configuration template
└── README.md
```

## 🎯 Key Algorithms

### VAM (Vogel's Approximation Method)
- Solves transport problems efficiently
- Minimizes total transportation cost
- Algorithm: Greedy with penalty calculations
- Time complexity: O(m×n) iterations

### DP (Dynamic Programming)
- EOQ (Economic Order Quantity) for inventory
- Multi-period planning
- Vehicle routing optimization
- Time complexity: Depends on state space

### Network Flow (Min-Cost Max-Flow)
- Successive Shortest Paths algorithm
- Handles multi-level distribution network
- Capacity constraints
- Time complexity: O(n×m×log(n))

## 📊 Sample Optimization Run

```bash
# 1. Check current network status
curl http://localhost:5000/api/supply/status

# 2. Run optimization
curl -X POST http://localhost:5000/api/optimize

# 3. Get results
curl http://localhost:5000/api/optimize/latest

# Expected response:
{
  "status": "success",
  "timestamp": "2026-04-17T10:30:00",
  "execution_time_ms": 1250,
  "vam_result": {
    "total_cost": 450000,
    "routes": [
      {"supplier": 0, "customer": 2, "quantity": 500, "cost_per_unit": 900},
      ...
    ]
  },
  "config": {...}
}
```

## 🌐 Real-world Integration

### Connect to Live APIs
1. Replace mock data in `data_fetcher.py` with real APIs
2. Integrate with:
   - Government petroleum ministry (petroleum.nic.in)
   - Company ERP systems (IOCL, HPCL, Reliance)
   - Weather services (OpenWeatherMap)
   - Market price feeds

### Database Integration
```bash
# Install PostgreSQL support
pip install psycopg2-binary sqlalchemy

# Create database
createdb lpg_optimizer

# Run migrations (implement as needed)
```

## 📈 Performance Tips

1. **Cache Results**: Use Redis for frequently accessed data
2. **Batch Requests**: Group API calls together
3. **Optimize Database Queries**: Add proper indexing
4. **Use Async Operations**: Leverage async/await in data pipeline
5. **Container Deployment**: Use Docker for consistent environment

## 🚀 Production Deployment

### Docker Compose
```yaml
version: '3'
services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
  
  postgres:
    image: postgres:14
    environment:
      - POSTGRES_DB=lpg_optimizer
```

### Deploy
```bash
docker-compose up -d
```

## 📞 Support

For issues or questions:
1. Check README.md
2. Review API documentation in comments
3. Run tests to verify setup
4. Check logs: `backend/logs/lpg_optimizer.log`

## ✅ Next Steps

1. ✅ Complete project structure created
2. ⏳ Implement real API data sources
3. ⏳ Add PostgreSQL database
4. ⏳ Deploy to production
5. ⏳ Set up monitoring & alerts

---

**System Status**: Ready for development & testing  
**Last Updated**: 2026-04-17  
