import React from 'react';

function OptimizationResults({ result }) {
  if (!result) return null;

  const vam    = result.vam_result    || {};
  const dp     = result.dp_result     || {};
  const flow   = result.network_result || {};
  const simplex = result.simplex_result || {};

  return (
    <div className="optimization-results">

      {/* ── KPI metrics ── */}
      <div className="metrics">
        {[
          { label: 'VAM Total Cost',   value: vam.total_cost ? `₹${vam.total_cost.toFixed(0)}` : '—' },
          { label: 'Routes Optimized', value: vam.routes?.length ?? 0 },
          { label: 'Execution Time',   value: `${result.execution_time_ms?.toFixed(1) || 0} ms` },
          { label: 'Network Flow',     value: `${flow.max_flow || 0} MT` },
        ].map(m => (
          <div className="metric" key={m.label}>
            <span>{m.label}</span>
            <strong>{m.value}</strong>
          </div>
        ))}
      </div>

      {/* ── VAM ── */}
      {vam.routes?.length > 0 && (
        <div className="or-section">
          <div className="or-section-header">
            <h3>📊 Vogel's Approximation Method — Transport Allocation</h3>
            <span className="algo-badge">VAM</span>
          </div>
          <div className="or-section-body">
            <p className="or-description">
              VAM minimizes transportation cost by iteratively allocating supply to the cell with lowest cost
              in the row/column with the highest penalty (opportunity cost of NOT using the cheapest route).
            </p>
            <table className="results-table">
              <thead>
                <tr>
                  <th>Supplier</th>
                  <th>Customer City</th>
                  <th>Quantity (MT)</th>
                  <th>Cost (₹)</th>
                  <th>₹ / MT</th>
                </tr>
              </thead>
              <tbody>
                {vam.routes.map((r, i) => (
                  <tr key={i}>
                    <td>{r.supplier?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</td>
                    <td>{r.customer?.replace('city_', '').replace(/\b\w/g, l => l.toUpperCase())}</td>
                    <td>{r.quantity?.toFixed(0)}</td>
                    <td><span className="cost-chip">₹{r.cost?.toFixed(0)}</span></td>
                    <td style={{ color: '#94a3b8' }}>₹{r.unit_cost?.toFixed(0)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div style={{ marginTop: '1rem', padding: '0.75rem 1rem', background: 'rgba(139,92,246,0.06)', border: '1px solid rgba(139,92,246,0.2)', borderRadius: 10, fontSize: '0.82rem', color: '#94a3b8' }}>
              <strong style={{ color: '#a78bfa' }}>Total Cost:</strong> ₹{vam.total_cost?.toFixed(0)} &nbsp;|&nbsp;
              <strong style={{ color: '#a78bfa' }}>Iterations:</strong> {vam.iterations} &nbsp;|&nbsp;
              <strong style={{ color: '#a78bfa' }}>Efficiency:</strong> {vam.allocation_efficiency ? `${(vam.allocation_efficiency * 100).toFixed(1)}%` : '—'}
            </div>
          </div>
        </div>
      )}

      {/* ── DP ── */}
      {dp.inventory_allocation && (
        <div className="or-section">
          <div className="or-section-header">
            <h3>📦 Dynamic Programming — EOQ & Safety Stock</h3>
            <span className="algo-badge">DP</span>
          </div>
          <div className="or-section-body">
            <p className="or-description">
              Economic Order Quantity (EOQ) + safety stock computed for each node using
              DP: minimizes total annual holding + ordering cost while achieving {dp.service_level ? `${(dp.service_level * 100).toFixed(0)}%` : '95%'} service level.
            </p>
            <table className="results-table">
              <thead>
                <tr>
                  <th>Location</th>
                  <th>EOQ (MT)</th>
                  <th>Safety Stock</th>
                  <th>Inventory Buffer</th>
                  <th>Lead Time</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(dp.eoq_details || {}).slice(0, 12).map(([loc, d]) => (
                  <tr key={loc}>
                    <td style={{ fontSize: '0.78rem' }}>{loc.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</td>
                    <td><span className="cost-chip">📦 {d.eoq?.toFixed(0)} MT</span></td>
                    <td style={{ color: '#fcd34d' }}>{d.safety_stock?.toFixed(0)} MT</td>
                    <td style={{ color: '#6ee7b7' }}>{(dp.inventory_allocation?.[loc] || 0).toFixed(0)} MT</td>
                    <td style={{ color: '#94a3b8' }}>{d.lead_time_days} days</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <div style={{ marginTop: '1rem', padding: '0.75rem 1rem', background: 'rgba(59,130,246,0.06)', border: '1px solid rgba(59,130,246,0.2)', borderRadius: 10, fontSize: '0.82rem', color: '#94a3b8' }}>
              <strong style={{ color: '#60a5fa' }}>Annual Cost:</strong> ₹{dp.total_annual_cost?.toFixed(0)} &nbsp;|&nbsp;
              <strong style={{ color: '#60a5fa' }}>Locations Optimized:</strong> {dp.locations_optimized} &nbsp;|&nbsp;
              <strong style={{ color: '#60a5fa' }}>Stockout Prob:</strong> {dp.stockout_probability ? `${(dp.stockout_probability * 100).toFixed(1)}%` : '—'}
            </div>
          </div>
        </div>
      )}

      {/* ── Network Flow ── */}
      {flow.status === 'success' && (
        <div className="or-section">
          <div className="or-section-header">
            <h3>🌐 Network Flow — Max-Flow / Min-Cost</h3>
            <span className="algo-badge">FLOW</span>
          </div>
          <div className="or-section-body">
            <p className="or-description">
              Finds the maximum feasible flow through the distribution network
              while minimizing total transportation cost (min-cost flow).
            </p>
            <div className="flow-stats">
              {[
                { label: 'Max Flow',        value: `${flow.max_flow?.toFixed(0)} MT/day` },
                { label: 'Utilization',     value: `${flow.utilization_percent?.toFixed(1)}%` },
                { label: 'Bottleneck Node', value: flow.bottleneck || '—' },
                { label: 'Total Cost',      value: `₹${flow.total_cost?.toFixed(0)}` },
              ].map(s => (
                <div className="flow-stat" key={s.label}>
                  <span>{s.label}</span>
                  <strong>{s.value}</strong>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ── Simplex ── */}
      {simplex.regional_allocation && (
        <div className="or-section">
          <div className="or-section-header">
            <h3>🗺️ Simplex (HiGHS LP) — Regional Allocation</h3>
            <span className="algo-badge">SIMPLEX</span>
          </div>
          <div className="or-section-body">
            <p className="or-description">
              Linear programming (revised Simplex via HiGHS solver) minimizes total transport cost
              subject to supply capacities and regional demand constraints.
            </p>
            <div className="regional-allocation">
              {Object.entries(simplex.regional_allocation).map(([region, d]) => {
                const pct = d.fulfillment_percent || 0;
                const fillColor = pct >= 95
                  ? 'linear-gradient(90deg,#10b981,#06b6d4)'
                  : pct >= 70
                    ? 'linear-gradient(90deg,#f59e0b,#ef4444)'
                    : 'linear-gradient(90deg,#ef4444,#dc2626)';
                return (
                  <div className="region-card" key={region}>
                    <div className="region-header">
                      <h4>{region}</h4>
                      <span className="demand-badge">{d.demand} MT</span>
                    </div>
                    <div className="region-details">
                      <div className="region-stat">
                        <span>Allocated</span>
                        <strong>{d.total_quantity?.toFixed(0)} MT</strong>
                      </div>
                      <div className="region-stat">
                        <span>Cost</span>
                        <strong>₹{d.total_cost?.toFixed(0)}</strong>
                      </div>
                      <div className="region-stat">
                        <span>Fulfillment</span>
                        <strong style={{ color: pct >= 95 ? '#6ee7b7' : '#fcd34d' }}>
                          {pct.toFixed(1)}%
                        </strong>
                      </div>
                    </div>
                    <div className="fulfillment-bar">
                      <div className="fulfillment-fill" style={{ width: `${Math.min(pct, 100)}%`, background: fillColor }} />
                    </div>
                    {Object.keys(d.plants || {}).length > 0 && (
                      <div className="plant-allocation">
                        <div className="allocation-label">From Plants</div>
                        {Object.entries(d.plants).map(([pl, qty]) => (
                          <div className="allocation-item" key={pl}>
                            <span>{pl.replace(/_/g, ' ')}</span>
                            <strong>{qty.toFixed(0)} MT</strong>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
            <div className="simplex-summary">
              <strong>Status:</strong> {simplex.optimization_status} &nbsp;|&nbsp;
              <strong>Method:</strong> {simplex.method} &nbsp;|&nbsp;
              <strong>Total Cost:</strong> ₹{simplex.total_cost?.toFixed(0)} &nbsp;|&nbsp;
              <strong>Regions:</strong> {simplex.regions}
            </div>
          </div>
        </div>
      )}

      {/* ── Performance ── */}
      <div className="or-section">
        <div className="or-section-header">
          <h3>⏱️ Performance & Summary</h3>
        </div>
        <div className="or-section-body">
          <div className="performance-grid">
            {[
              { label: 'Algorithms',    value: 'VAM · DP · Flow · Simplex' },
              { label: 'Total Routes',  value: `${vam.routes?.length || 0} routes` },
              { label: 'Exec Time',     value: `${result.execution_time_ms?.toFixed(1)} ms` },
              { label: 'Timestamp',     value: new Date(result.timestamp).toLocaleString() },
            ].map(p => (
              <div className="perf-item" key={p.label}>
                <span>{p.label}</span>
                <strong>{p.value}</strong>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default OptimizationResults;
