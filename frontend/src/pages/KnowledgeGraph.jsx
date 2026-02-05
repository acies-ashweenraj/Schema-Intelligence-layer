import { useEffect, useRef, useState } from "react";
import NeoVis from "neovis.js";

export default function KnowledgeGraph({ neo4j }) {
  const vizRef = useRef(null);
  const vizInstance = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);

  // 🔹 Fully dynamic caption resolver
  function resolveCaption(node) {
    const props = node?.properties || {};

    // 1. Exact "name"
    if (props.name) return String(props.name);

    // 2. Any property containing "name"
    const nameKey = Object.keys(props).find(k =>
      k.toLowerCase().includes("name")
    );
    if (nameKey) return String(props[nameKey]);

    // 3. Any string property
    const stringKey = Object.keys(props).find(
      k => typeof props[k] === "string"
    );
    if (stringKey) return String(props[stringKey]);

    // 4. Fallback to Neo4j internal id
    return `Node ${node.identity}`;
  }

  useEffect(() => {
    if (!neo4j?.uri || !neo4j?.user || !neo4j?.password) return;
    if (!vizRef.current) return;

    vizRef.current.innerHTML = "";

    const config = {
      containerId: vizRef.current.id,

      neo4j: {
        serverUrl: neo4j.uri,
        serverUser: neo4j.user,
        serverPassword: neo4j.password,
      },

      // 🔹 Fully dynamic labels
      labels: {
        "*": {
          caption: resolveCaption,
          shape: "dot",
          size: 28,
          font: {
            size: 16,
            face: "Arial",
            color: "#111827",
            strokeWidth: 2,
            strokeColor: "#ffffff",
            background: "rgba(255,255,255,0.9)",
          },
        },
      },

      // 🔹 Fully dynamic relationships
      relationships: {
        "*": {
          caption: true,
          arrows: { to: { enabled: true } },
          font: {
            size: 12,
            strokeWidth: 1,
            strokeColor: "#ffffff",
          },
        },
      },

      physics: {
        enabled: true,
        stabilization: { iterations: 300 },
        barnesHut: {
          gravitationalConstant: -12000,
          springLength: 160,
          springConstant: 0.04,
        },
      },

      visConfig: {
        interaction: {
          hover: true,
          zoomView: true,
          dragView: true,
        },
        nodes: {
          scaling: {
            label: {
              enabled: true,
              min: 14,
              max: 30,
            },
          },
        },
      },

      // 🔹 Generic query – nothing hardcoded
      initialCypher: `
        MATCH (n)-[r]->(m)
        RETURN n, r, m
        LIMIT 400
      `,
    };

    vizInstance.current = new NeoVis(config);
    vizInstance.current.render();

    // Node click → property panel
    vizInstance.current.registerOnEvent("clickNode", e => {
      setSelectedNode({
        labels: e.node.labels,
        properties: e.node.properties,
      });
    });

    return () => {
      vizInstance.current = null;
    };
  }, [neo4j]);

  return (
    <div className="grid grid-cols-12 gap-4">
      {/* GRAPH */}
      <div className="col-span-9">
        <div
          id="neo4j-graph"
          ref={vizRef}
          className="w-full h-[600px] border rounded-xl bg-white"
        />
      </div>

      {/* NODE DETAILS */}
      <div className="col-span-3">
        <div className="bg-white border rounded-xl p-4">
          <div className="font-semibold mb-2">Node Details</div>

          {!selectedNode && (
            <div className="text-sm text-slate-500">
              Click a node to view properties
            </div>
          )}

          {selectedNode && (
            <div className="text-sm space-y-1">
              <div>
                <b>Labels:</b> {selectedNode.labels.join(", ")}
              </div>

              {Object.entries(selectedNode.properties).map(([k, v]) => (
                <div key={k}>
                  <b>{k}:</b> {String(v)}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
