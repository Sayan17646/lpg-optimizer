import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';
import GeographicalMap from './components/GeographicalMap';
import OptimizationResults from './components/OptimizationResults';
import RealTimeMonitor from './components/RealTimeMonitor';
import AllocationHeatmap from './components/AllocationHeatmap';

const API = '/api';

function KpiCard({ icon, label, value, sub, color }) {
  return (
    <div className="kpi-card" style={{ '--kpi-color': color }}>
      <span className="kpi-icon">{icon}</span>
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{value}</div>
      {sub && <div className="kpi-sub">{sub}</div>}
    </div>
  );
}

function SectionHeader({ icon, title, badge }) {
  return (
    <div className="section-header">
      <div className="section-title">
        <div className="icon">{icon}</div>
        {title}
      </div>
      {badge && <span className="section-badge">{badge}</span>}
    </div>
  );
}

export default function App() {
  const [networkData, setNetworkData] = useState(null);
  const [optimization, setOptimization] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastRun, setLastRun] = useState(null);

  useEffect(() => { fetchNetwork(); }, []);

  const fetchNetwork = async () => {
    try {
      const res = await axios.get(`${API}/network`);
      setNetworkData(res.data);
    } catch (e) {
      setError(`Network fetch failed: ${e.message}`);
    }
  };

  const runOptimization = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.post(`${API}/optimize`, {
        config: { use_vam: true, use_dp: true, use_network_flow: true, service_level_target: 0.95 }
      });
      setOptimization(res.data);
      setLastRun(new Date().toLocaleTimeString());
    } catch (e) {
      setError(`Optimization failed: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  // KPI values
  const vam = optimization?.vam_result;
  const nf  = optimization?.network_result;

  const totalCost   = vam?.total_cost ? `₹${(vam.total_cost / 1e5).toFixed(1)}L` : '—';
  const totalRoutes = vam?.routes?.length ?? '—';
  const execTime    = optimization?.execution_time_ms ? `${optimization.execution_time_ms.toFixed(0)} ms` : '—';
  const maxFlow     = nf?.max_flow ? `${nf.max_flow.toFixed(0)} MT` : '—';



  return (
    <div className="app">
      {/* ── Header ── */}
      <header className="app-header">
        <div className="header-brand">
          <div className="logo">⛽</div>
          <h1>LPG Supply Chain Optimizer — India</h1>
        </div>
        <div className="header-meta">
          <div className="live-badge">
            <div className="live-dot" />
            Live
          </div>
          {lastRun && <span style={{ fontSize: '0.75rem', color: '#475569' }}>Last run: {lastRun}</span>}
          <button
            id="run-optimization-btn"
            className={`btn-primary ${loading ? 'btn-running' : ''}`}
            onClick={runOptimization}
            disabled={loading}
          >
            {loading ? '⚙️ Optimizing…' : '▶ Run Optimization'}
          </button>
        </div>
      </header>

      {error && <div className="error-banner">⚠ {error}</div>}

      <main className="dashboard">

        {/* ── KPI row ── */}
        <div className="kpi-row">
          <KpiCard icon="💰" label="VAM Transport Cost" value={totalCost}
            sub={vam?.allocation_efficiency ? `${(vam.allocation_efficiency * 100).toFixed(1)}% efficiency` : 'Run optimization'}
            color="linear-gradient(90deg,#8b5cf6,#6366f1)" />
          <KpiCard icon="🛣️" label="Optimized Routes" value={totalRoutes}
            sub={vam ? `VAM iterations: ${vam.iterations || '—'}` : 'Run optimization'}
            color="linear-gradient(90deg,#3b82f6,#06b6d4)" />
          <KpiCard icon="⚡" label="Execution Time" value={execTime}
            sub="VAM + DP + Simplex + Flow"
            color="linear-gradient(90deg,#10b981,#06b6d4)" />
          <KpiCard icon="🌊" label="Max Network Flow" value={maxFlow}
            sub={nf ? `${nf.utilization_percent?.toFixed(1)}% utilized` : 'Run optimization'}
            color="linear-gradient(90deg,#f59e0b,#ef4444)" />
        </div>

        {/* ── India Network Map ── */}
        <div className="section">
          <SectionHeader icon="🗺" title="India LPG Network Map" badge="Live Routing" />
          {networkData
            ? <GeographicalMap data={networkData} optimization={optimization} />
            : <div className="loading">Loading network data…</div>
          }
        </div>

        {/* ── VAM Heatmap + Real-Time Monitor ── */}
        <div className="grid-2">
          <div className="section">
            <SectionHeader icon="🔥" title="VAM Allocation Heatmap" badge="Supplier → City" />
            <AllocationHeatmap optimization={optimization} />
          </div>
          <div className="section">
            <SectionHeader icon="📡" title="Real-Time Network Status" badge="Auto-refresh 8s" />
            <RealTimeMonitor data={networkData} />
          </div>
        </div>

        {/* ── Supply & Demand ── */}
        <div className="grid-2">
          <div className="section">
            <SectionHeader icon="🏭" title="Supply Sources" />
            {networkData?.plants && (
              <div className="supply-list">
                {Object.entries(networkData.plants).map(([id, p]) => (
                  <div className="supply-item" key={id}>
                    <span className="plant-name">{p.name}</span>
                    <span className="capacity-badge">{p.capacity} MT/day</span>
                  </div>
                ))}
              </div>
            )}
          </div>
          <div className="section">
            <SectionHeader icon="🏙️" title="Demand Centers" />
            {networkData?.major_cities && (
              <div className="demand-list">
                {networkData.major_cities.map(city => (
                  <div className="demand-item" key={city.id}>
                    <span className="city-name">{city.name}</span>
                    <span className="demand-badge-pill">{city.demand_mt} MT/day</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* ── Optimization Results (all 4 algorithms) ── */}
        {optimization && (
          <div className="section">
            <SectionHeader icon="✅" title="Optimization Results" badge="VAM · DP · Simplex · Flow" />
            <OptimizationResults result={optimization} />
          </div>
        )}

      </main>
    </div>
  );
}
