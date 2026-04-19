import React, { useState } from 'react';

function NetworkMap({ data }) {
  const [selectedNode, setSelectedNode] = useState(null);

  if (!data) {
    return <div className="loading">Loading network data...</div>;
  }

  return (
    <div className="network-map">
      <svg viewBox="0 0 1000 600" className="map-svg">
        <defs>
          <marker id="arrowhead" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto">
            <polygon points="0 0, 10 3, 0 6" fill="#999" />
          </marker>
        </defs>

        {/* Plants */}
        {data.plants && Object.entries(data.plants).map(([id, plant]) => (
          <circle 
            key={`plant-${id}`}
            cx={100 + Math.random() * 800}
            cy={100 + Math.random() * 400}
            r="20"
            className="plant-node"
            onClick={() => setSelectedNode({id, type: 'Plant', ...plant})}
          />
        ))}

        {/* Distribution Hubs */}
        {data.distribution_hubs && data.distribution_hubs.map((hub) => (
          <rect
            key={`hub-${hub.id}`}
            x={100 + Math.random() * 800 - 15}
            y={100 + Math.random() * 400 - 15}
            width="30"
            height="30"
            className="hub-node"
            onClick={() => setSelectedNode({type: 'Hub', ...hub})}
          />
        ))}

        {/* Cities */}
        {data.major_cities && data.major_cities.map((city) => (
          <circle
            key={`city-${city.id}`}
            cx={100 + Math.random() * 800}
            cy={100 + Math.random() * 400}
            r="10"
            className="city-node"
            onClick={() => setSelectedNode({type: 'City', ...city})}
          />
        ))}
      </svg>

      {selectedNode && (
        <div className="node-details">
          <h4>{selectedNode.type}: {selectedNode.name || selectedNode.id}</h4>
          {selectedNode.capacity && <p>Capacity: {selectedNode.capacity} MT</p>}
          {selectedNode.demand && <p>Demand: {selectedNode.demand} MT</p>}
          {selectedNode.current_stock && <p>Stock: {selectedNode.current_stock} MT</p>}
          <button onClick={() => setSelectedNode(null)}>Close</button>
        </div>
      )}
    </div>
  );
}

export default NetworkMap;
