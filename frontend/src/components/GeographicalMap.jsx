import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix Leaflet default icon path issue with webpack
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

function GeographicalMap({ data, optimization }) {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const routeLayerRef = useRef(null);

  // Plant lat/lon lookup for drawing routes
  const plantCoords = useRef({});

  useEffect(() => {
    if (!data || mapInstanceRef.current) return;

    const map = L.map('india-map', {
      center: [20.5937, 78.9629],
      zoom: 5,
      scrollWheelZoom: true,
      zoomControl: true,
    });

    mapInstanceRef.current = map;
    mapRef.current = map;

    // OpenStreetMap tile layer (filtered dark via CSS)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
      maxZoom: 18,
    }).addTo(map);

    // ── Plants (red glowing circles) ──
    if (data.plants) {
      Object.entries(data.plants).forEach(([id, plant]) => {
        const [lat, lon] = plant.location;
        plantCoords.current[id] = [lat, lon];

        const marker = L.circleMarker([lat, lon], {
          radius: 13,
          fillColor: '#ef4444',
          color: '#fca5a5',
          weight: 2,
          opacity: 0.9,
          fillOpacity: 0.85,
        }).addTo(map);

        marker.bindPopup(`
          <div style="font-family:Inter,sans-serif;padding:4px">
            <div style="font-weight:700;font-size:13px;margin-bottom:4px">🏭 ${plant.name}</div>
            <div style="font-size:11px;color:#94a3b8">
              <b style="color:#f1f5f9">Capacity:</b> ${plant.capacity} MT/day<br/>
              <b style="color:#f1f5f9">Type:</b> ${plant.type || 'Refinery'}
            </div>
          </div>
        `);

        // Pulsing glow effect via second transparent circle
        L.circleMarker([lat, lon], {
          radius: 22,
          fillColor: '#ef4444',
          color: '#ef4444',
          weight: 1,
          opacity: 0.25,
          fillOpacity: 0.08,
          interactive: false,
        }).addTo(map);
      });
    }

    // ── Distribution Hubs (orange) ──
    if (data.distribution_hubs) {
      data.distribution_hubs.forEach((hub) => {
        const [lat, lon] = hub.location;

        const marker = L.circleMarker([lat, lon], {
          radius: 10,
          fillColor: '#f59e0b',
          color: '#fcd34d',
          weight: 2,
          opacity: 0.9,
          fillOpacity: 0.85,
        }).addTo(map);

        marker.bindPopup(`
          <div style="font-family:Inter,sans-serif;padding:4px">
            <div style="font-weight:700;font-size:13px;margin-bottom:4px">🏢 ${hub.name}</div>
            <div style="font-size:11px;color:#94a3b8">Distribution Hub</div>
          </div>
        `);
      });
    }

    // ── Cities (green) ──
    if (data.major_cities) {
      data.major_cities.forEach((city) => {
        const [lat, lon] = city.location;

        const marker = L.circleMarker([lat, lon], {
          radius: 8,
          fillColor: '#10b981',
          color: '#6ee7b7',
          weight: 2,
          opacity: 0.9,
          fillOpacity: 0.85,
        }).addTo(map);

        marker.bindPopup(`
          <div style="font-family:Inter,sans-serif;padding:4px">
            <div style="font-weight:700;font-size:13px;margin-bottom:4px">🏙️ ${city.name}</div>
            <div style="font-size:11px;color:#94a3b8">
              <b style="color:#f1f5f9">Demand:</b> ${city.demand_mt} MT/day<br/>
              <b style="color:#f1f5f9">OMC:</b> ${city.omc || 'Mixed'}
            </div>
          </div>
        `);
      });
    }

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, [data]);

  // ── Draw route lines when optimization result arrives ──
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map || !optimization?.vam_result?.routes) return;

    // Clear old route layer
    if (routeLayerRef.current) {
      routeLayerRef.current.clearLayers();
    } else {
      routeLayerRef.current = L.layerGroup().addTo(map);
    }

    // City coordinates (approximate, based on known locations)
    const cityCoords = {
      city_delhi:     [28.6139, 77.2090],
      city_mumbai:    [19.0760, 72.8777],
      city_bangalore: [12.9716, 77.5946],
      city_kolkata:   [22.5726, 88.3639],
      city_hyderabad: [17.3850, 78.4867],
    };

    const supplierCoords = {
      reliance_jamnagar: [22.4707, 70.0577],
      ioc_kochi:         [9.9312, 76.2673],
      hpcl_mumbai:       [19.0760, 72.8777],
      bharat_import:     [13.0827, 80.2707],
    };

    const maxCost = Math.max(...optimization.vam_result.routes.map(r => r.cost || 1));

    optimization.vam_result.routes.forEach((route) => {
      const from = supplierCoords[route.supplier];
      const to = cityCoords[route.customer];
      if (!from || !to) return;

      const intensity = 1 - (route.cost / maxCost);
      const color = intensity > 0.5 ? '#8b5cf6' : '#3b82f6';
      const weight = 1 + (route.quantity / 200);

      const line = L.polyline([from, to], {
        color,
        weight: Math.min(weight, 5),
        opacity: 0.6,
        dashArray: '6 4',
      });

      line.bindPopup(`
        <div style="font-family:Inter,sans-serif;padding:4px">
          <div style="font-weight:700;font-size:12px;margin-bottom:4px;color:#a78bfa">Route</div>
          <div style="font-size:11px;color:#94a3b8">
            <b style="color:#f1f5f9">From:</b> ${route.supplier}<br/>
            <b style="color:#f1f5f9">To:</b> ${route.customer}<br/>
            <b style="color:#f1f5f9">Qty:</b> ${route.quantity?.toFixed(0)} MT<br/>
            <b style="color:#f1f5f9">Cost:</b> ₹${route.cost?.toFixed(0)}
          </div>
        </div>
      `);

      routeLayerRef.current.addLayer(line);
    });
  }, [optimization]);

  return (
    <div>
      <div className="map-legend">
        <div className="legend-item">
          <div className="legend-dot" style={{ background: '#ef4444' }} />
          <span>Refineries / Plants</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot" style={{ background: '#f59e0b' }} />
          <span>Distribution Hubs</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot" style={{ background: '#10b981' }} />
          <span>Demand Cities</span>
        </div>
        <div className="legend-item">
          <div className="legend-dot" style={{ background: '#8b5cf6', borderRadius: 2 }} />
          <span>VAM Allocation Routes</span>
        </div>
      </div>
      <div className="map-container">
        <div id="india-map" style={{ width: '100%', height: '100%' }} />
      </div>
    </div>
  );
}

export default GeographicalMap;
