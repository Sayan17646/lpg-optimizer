"""
React Dashboard for LPG Optimization
Initialize with: npx create-react-app frontend && cd frontend
"""

// Main App component for LPG Dashboard

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

// Import components
import NetworkMap from './components/NetworkMap';
import OptimizationResults from './components/OptimizationResults';
import RealTimeMonitor from './components/RealTimeMonitor';
import DemandForecast from './components/DemandForecast';
import SupplyStatus from './components/SupplyStatus';
import AllocationChart from './components/AllocationChart';

const API_BASE = 'http://localhost:5000/api';

function App() {
  const [networkData, setNetworkData] = useState(null);
  const [optimization, setOptimization] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [autoOptimize, setAutoOptimize] = useState(true);
  const [optimizeInterval, setOptimizeInterval] = useState(300000); // 5 minutes

  useEffect(() => {
    // Load network data
    fetchNetworkData();
    
    // Set up auto-optimization
    if (autoOptimize) {
      const interval = setInterval(runOptimization, optimizeInterval);
      return () => clearInterval(interval);
    }
  }, [autoOptimize, optimizeInterval]);

  const fetchNetworkData = async () => {
    try {
      const response = await axios.get(`${API_BASE}/network`);
      setNetworkData(response.data);
    } catch (err) {
      setError(`Failed to load network: ${err.message}`);
    }
  };

  const runOptimization = async () => {
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/optimize`, {
        config: {
          use_vam: true,
          use_dp: true,
          use_network_flow: true,
          service_level_target: 0.95
        }
      });
      setOptimization(response.data);
      setError(null);
    } catch (err) {
      setError(`Optimization failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🚛 LPG Live Optimization System - India</h1>
        <div className="controls">
          <button 
            onClick={runOptimization} 
            disabled={loading}
            className="btn-primary"
          >
            {loading ? 'Running Optimization...' : 'Run Optimization'}
          </button>
          
          <label className="checkbox">
            <input 
              type="checkbox" 
              checked={autoOptimize} 
              onChange={(e) => setAutoOptimize(e.target.checked)}
            />
            Auto-optimize (every {optimizeInterval / 1000}s)
          </label>
        </div>
      </header>

      {error && <div className="error-banner">{error}</div>}

      <div className="dashboard">
        <section className="section">
          <h2>📍 Network Topology</h2>
          {networkData && <NetworkMap data={networkData} />}
        </section>

        <section className="section">
          <h2>📊 Real-Time Status</h2>
          <div className="grid-2">
            <RealTimeMonitor />
            <SupplyStatus />
          </div>
        </section>

        <section className="section">
          <h2>📈 Forecast & Analysis</h2>
          <div className="grid-2">
            <DemandForecast />
            <AllocationChart optimization={optimization} />
          </div>
        </section>

        {optimization && (
          <section className="section">
            <h2>✅ Optimization Results</h2>
            <OptimizationResults result={optimization} />
          </section>
        )}
      </div>
    </div>
  );
}

export default App;
