"""
Frontend components for LPG dashboard
"""

// NetworkMap.jsx - Display LPG network on map
import React, { useState, useEffect } from 'react';
import { BarChart, PieChart, LineChart } from 'recharts';

export function NetworkMap({ data }) {
  const [selectedNode, setSelectedNode] = useState(null);

  return (
    <div className="network-map">
      <svg viewBox="0 0 1000 600" className="map-svg">
        {/* Plants */}
        <g className="plants">
          {Object.entries(data.plants || {}).map(([id, plant]) => (
            <circle 
              key={id} 
              cx={plant.location[1] * 100} 
              cy={plant.location[0] * 100}
              r="15"
              className="plant-node"
              onClick={() => setSelectedNode({id, ...plant})}
            />
          ))}
        </g>

        {/* Hubs */}
        <g className="hubs">
          {(data.distribution_hubs || []).map((hub) => (
            <rect
              key={hub.id}
              x={hub.location[1] * 100 - 10}
              y={hub.location[0] * 100 - 10}
              width="20"
              height="20"
              className="hub-node"
              onClick={() => setSelectedNode({...hub})}
            />
          ))}
        </g>

        {/* Cities/Retail points */}
        <g className="cities">
          {(data.major_cities || []).map((city) => (
            <circle
              key={city.id}
              cx={city.location[1] * 100}
              cy={city.location[0] * 100}
              r="8"
              className="city-node"
              onClick={() => setSelectedNode({...city})}
            />
          ))}
        </g>
      </svg>

      {selectedNode && (
        <div className="node-details">
          <h3>{selectedNode.name || selectedNode.id}</h3>
          {selectedNode.capacity && <p>Capacity: {selectedNode.capacity} MT</p>}
          {selectedNode.demand_mt && <p>Demand: {selectedNode.demand_mt} MT</p>}
        </div>
      )}
    </div>
  );
}

// OptimizationResults.jsx
export function OptimizationResults({ result }) {
  return (
    <div className="optimization-results">
      <div className="metric">
        <span>Total Cost:</span>
        <strong>₹{result.vam_result?.total_cost?.toFixed(2) || 'N/A'}</strong>
      </div>
      <div className="metric">
        <span>Execution Time:</span>
        <strong>{result.execution_time_ms?.toFixed(1) || 'N/A'} ms</strong>
      </div>
      <div className="metric">
        <span>Routes Optimized:</span>
        <strong>{result.vam_result?.routes?.length || 0}</strong>
      </div>

      {result.vam_result?.routes && (
        <div className="routes-table">
          <table>
            <thead>
              <tr>
                <th>Supplier</th>
                <th>Customer</th>
                <th>Quantity (MT)</th>
                <th>Cost (₹)</th>
              </tr>
            </thead>
            <tbody>
              {result.vam_result.routes.slice(0, 10).map((route, idx) => (
                <tr key={idx}>
                  <td>S{route.supplier}</td>
                  <td>C{route.customer}</td>
                  <td>{route.quantity.toFixed(0)}</td>
                  <td>₹{route.total_cost.toFixed(0)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// RealTimeMonitor.jsx
export function RealTimeMonitor() {
  const [status, setStatus] = useState(null);

  React.useEffect(() => {
    const interval = setInterval(async () => {
      const response = await fetch('http://localhost:5000/api/supply/status');
      const data = await response.json();
      setStatus(data);
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="realtime-monitor">
      <h3>Network Status</h3>
      {status && (
        <div>
          <p>Total Supply: <strong>{status.total_available_mt?.toFixed(0)} MT</strong></p>
          <p>Network Utilization: <strong>{(status.network_utilization * 100).toFixed(1)}%</strong></p>
          <div className="utilization-bar">
            <div 
              className="bar-fill"
              style={{width: (status.network_utilization * 100) + '%'}}
            />
          </div>
        </div>
      )}
    </div>
  );
}

// SupplyStatus.jsx
export function SupplyStatus() {
  const [supply, setSupply] = useState(null);

  React.useEffect(() => {
    const interval = setInterval(async () => {
      const response = await fetch('http://localhost:5000/api/supply/status');
      const data = await response.json();
      setSupply(data);
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="supply-status">
      <h3>Plant Supply Status</h3>
      {supply?.supply && (
        <div className="plant-list">
          {Object.entries(supply.supply).map(([plant, data]) => (
            <div key={plant} className="plant-item">
              <span>{plant}</span>
              <div className="bar">
                <div 
                  className="value"
                  style={{width: (data.utilization * 100) + '%'}}
                />
              </div>
              <span>{data.available.toFixed(0)}/{data.capacity.toFixed(0)} MT</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// DemandForecast.jsx
export function DemandForecast() {
  const [forecast, setForecast] = React.useState(null);

  React.useEffect(() => {
    fetch('http://localhost:5000/api/demand/forecast?location=city_delhi&days=1')
      .then(r => r.json())
      .then(data => {
        const delhi_forecast = data.forecast?.city_delhi || [];
        const chartData = delhi_forecast.slice(0, 24).map((val, hr) => ({
          time: `${hr}:00`,
          demand: val
        }));
        setForecast(chartData);
      });
  }, []);

  return (
    <div className="demand-forecast">
      <h3>Delhi Demand Forecast (24h)</h3>
      {forecast && <LineChart width={300} height={200} data={forecast} />}
    </div>
  );
}

// AllocationChart.jsx
export function AllocationChart({ optimization }) {
  const data = optimization?.vam_result?.allocation_matrix || [];

  return (
    <div className="allocation-chart">
      <h3>Allocation Heatmap</h3>
      {data.length > 0 && (
        <div className="heatmap">
          {/* Render allocation matrix as colored grid */}
          {data.map((row, i) => (
            <div key={i} className="heatmap-row">
              {row.map((value, j) => (
                <div
                  key={`${i}-${j}`}
                  className="heatmap-cell"
                  style={{
                    backgroundColor: `rgba(76, 175, 80, ${Math.min(value / 100, 1)})`
                  }}
                  title={`S${i}-C${j}: ${value.toFixed(1)} MT`}
                />
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default {
  NetworkMap,
  OptimizationResults,
  RealTimeMonitor,
  SupplyStatus,
  DemandForecast,
  AllocationChart
};
