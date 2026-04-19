import React, { useState } from 'react';

const SUPPLIERS = [
  { key: 'reliance_jamnagar', label: 'Reliance\nJamnagar' },
  { key: 'ioc_kochi',         label: 'IOC\nKochi' },
  { key: 'hpcl_mumbai',       label: 'HPCL\nMumbai' },
  { key: 'bharat_import',     label: 'Bharat\nImport' },
];

const CUSTOMERS = [
  { key: 'city_delhi',     label: 'Delhi' },
  { key: 'city_mumbai',   label: 'Mumbai' },
  { key: 'city_bangalore',label: 'Bangalore' },
  { key: 'city_kolkata',  label: 'Kolkata' },
  { key: 'city_hyderabad',label: 'Hyderabad' },
];

function getColor(value, maxValue) {
  if (value <= 0) return null;
  const ratio = Math.min(value / maxValue, 1);
  if (ratio > 0.7) return `rgba(139,92,246,${0.5 + ratio * 0.5})`;
  if (ratio > 0.35) return `rgba(59,130,246,${0.4 + ratio * 0.5})`;
  return `rgba(6,182,212,${0.3 + ratio * 0.5})`;
}

function AllocationHeatmap({ optimization }) {
  const [hoveredCell, setHoveredCell] = useState(null);

  const routes = optimization?.vam_result?.routes || [];

  // Build lookup: supplier × customer → quantity
  const lookup = {};
  let maxQty = 0;
  routes.forEach(r => {
    lookup[`${r.supplier}__${r.customer}`] = r;
    if (r.quantity > maxQty) maxQty = r.quantity;
  });

  const totalAllocated = routes.reduce((s, r) => s + (r.quantity || 0), 0);
  const totalCost = routes.reduce((s, r) => s + (r.cost || 0), 0);

  return (
    <div>
      {/* Summary strip */}
      <div style={{ display: 'flex', gap: '1.5rem', marginBottom: '1.25rem', flexWrap: 'wrap' }}>
        {[
          { label: 'Total Allocated', value: `${totalAllocated.toFixed(0)} MT`, color: '#a78bfa' },
          { label: 'Total Routes', value: routes.length, color: '#60a5fa' },
          { label: 'Total Transport Cost', value: `₹${(totalCost / 1e5).toFixed(2)}L`, color: '#6ee7b7' },
        ].map(m => (
          <div key={m.label} style={{
            background: 'rgba(255,255,255,0.03)',
            border: '1px solid rgba(255,255,255,0.08)',
            borderRadius: 10,
            padding: '0.7rem 1.1rem',
            minWidth: 140,
          }}>
            <div style={{ fontSize: '0.68rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 3 }}>{m.label}</div>
            <div style={{ fontSize: '1.2rem', fontWeight: 800, color: m.color }}>{m.value}</div>
          </div>
        ))}
      </div>

      {/* No data state */}
      {routes.length === 0 && (
        <div className="loading">
          Run optimization to see the allocation heatmap
        </div>
      )}

      {routes.length > 0 && (
        <div className="heatmap-wrapper">
          {/* Column headers */}
          <div className="heatmap-col-labels">
            {CUSTOMERS.map(c => (
              <div key={c.key} className="heatmap-col-label">{c.label}</div>
            ))}
          </div>

          {/* Rows */}
          <div className="heatmap-grid">
            {SUPPLIERS.map((s, si) => (
              <div key={s.key} className="heatmap-row-wrap">
                <div className="heatmap-row-label">{s.label.replace('\n', ' ')}</div>
                <div className="heatmap-inner-row">
                  {CUSTOMERS.map((c, ci) => {
                    const routeKey = `${s.key}__${c.key}`;
                    const route = lookup[routeKey];
                    const qty = route?.quantity || 0;
                    const cost = route?.cost || 0;
                    const unitCost = route?.unit_cost || 0;
                    const bg = getColor(qty, maxQty);
                    const isHovered = hoveredCell === routeKey;

                    return (
                      <div
                        key={c.key}
                        className={`heatmap-cell ${qty <= 0 ? 'zero' : ''}`}
                        style={bg ? { background: bg } : {}}
                        onMouseEnter={() => setHoveredCell(routeKey)}
                        onMouseLeave={() => setHoveredCell(null)}
                      >
                        {qty > 0 ? `${qty.toFixed(0)}` : '—'}
                        {isHovered && qty > 0 && (
                          <div className="heatmap-tooltip">
                            {s.label.replace('\n',' ')} → {c.label}<br/>
                            Qty: <b>{qty.toFixed(0)} MT</b><br/>
                            Cost: <b>₹{cost.toFixed(0)}</b><br/>
                            ₹/MT: <b>{unitCost.toFixed(0)}</b>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          {/* Color scale legend */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginTop: '1.25rem' }}>
            <span style={{ fontSize: '0.7rem', color: '#64748b' }}>Low allocation</span>
            <div style={{
              height: 8, width: 180, borderRadius: 99,
              background: 'linear-gradient(90deg, rgba(6,182,212,0.5), rgba(59,130,246,0.7), rgba(139,92,246,1))',
            }} />
            <span style={{ fontSize: '0.7rem', color: '#64748b' }}>High allocation</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default AllocationHeatmap;
