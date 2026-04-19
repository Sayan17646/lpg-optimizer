import React, { useEffect, useState } from 'react';
import axios from 'axios';

function RealTimeMonitor({ data }) {
  const [supply, setSupply] = useState(null);

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await axios.get('/api/supply/status');
        setSupply(res.data);
      } catch {}
    };
    fetch();
    const id = setInterval(fetch, 8000);
    return () => clearInterval(id);
  }, []);

  const networkStats = data ? [
    { label: 'Plants', value: Object.keys(data.plants || {}).length, color: '#fca5a5' },
    { label: 'Hubs', value: (data.distribution_hubs || []).length, color: '#fcd34d' },
    { label: 'Cities', value: (data.major_cities || []).length, color: '#6ee7b7' },
    { label: 'OMCs', value: 3, color: '#a78bfa' },
  ] : [];

  return (
    <div>
      <div className="status-grid" style={{ marginBottom: '1.25rem' }}>
        {networkStats.map(s => (
          <div className="status-item" key={s.label}>
            <span>{s.label}</span>
            <strong style={{ color: s.color }}>{s.value}</strong>
          </div>
        ))}
      </div>

      {supply && (
        <div>
          <div style={{ fontSize: '0.72rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: '0.75rem', fontWeight: 600 }}>
            Live Plant Utilization
          </div>
          <div className="flow-bars">
            {Object.entries(supply.supply || {}).map(([plant, info]) => (
              <div className="flow-bar-row" key={plant}>
                <div className="flow-bar-labels">
                  <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                    {plant.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </span>
                  <span style={{ fontSize: '0.75rem', color: '#a78bfa', fontWeight: 700 }}>
                    {(info.utilization * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="flow-bar-track">
                  <div
                    className="flow-bar-fill"
                    style={{
                      width: `${info.utilization * 100}%`,
                      background: info.utilization > 0.9
                        ? 'linear-gradient(90deg, #ef4444, #f97316)'
                        : 'linear-gradient(90deg, #8b5cf6, #3b82f6)',
                    }}
                  />
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.68rem', color: '#475569' }}>
                  <span>{info.available.toFixed(0)} MT available</span>
                  <span>{info.capacity.toFixed(0)} MT capacity</span>
                </div>
              </div>
            ))}
          </div>
          <div style={{
            marginTop: '1rem',
            padding: '0.75rem 1rem',
            background: 'rgba(16,185,129,0.08)',
            border: '1px solid rgba(16,185,129,0.2)',
            borderRadius: 10,
            display: 'flex',
            justifyContent: 'space-between',
            fontSize: '0.78rem',
          }}>
            <span style={{ color: '#94a3b8' }}>Total Available</span>
            <strong style={{ color: '#6ee7b7' }}>{supply.total_available_mt?.toFixed(0)} / {supply.total_capacity_mt?.toFixed(0)} MT</strong>
          </div>
        </div>
      )}
    </div>
  );
}

export default RealTimeMonitor;
