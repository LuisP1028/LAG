/**
 * High-performance HTML5 Canvas Force-Directed Visualizer with Halftone Blueprint Shading.
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import * as d3 from 'd3';
import type { GraphNode, GraphLink } from '../types/graph';
import { getNodeVisual, CANVAS_PALETTE } from '../styles/graph_theme';
import { useGraphSync } from '../context/GraphSyncContext';

interface GraphCanvasProps {
  nodes: GraphNode[];
  links: GraphLink[];
  loading: boolean;
}

export const GraphCanvas: React.FC<GraphCanvasProps> = ({ nodes, links, loading }) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const simulationRef = useRef<d3.Simulation<GraphNode, d3.SimulationLinkDatum<GraphNode>> | null>(null);
  const transformRef = useRef<d3.ZoomTransform>(d3.zoomIdentity);
  const zoomBehaviorRef = useRef<d3.ZoomBehavior<HTMLCanvasElement, unknown> | null>(null);

  const {
    activeNodePKs,
    activeEdgeKeys,
    isIlluminated,
    selectedNode,
    selectNode,
    physicsFrozen,
  } = useGraphSync();

  const [hoveredNode, setHoveredNode] = useState<GraphNode | null>(null);
  const [fps, setFps] = useState<number>(60);
  const frameCountRef = useRef<number>(0);
  const lastFpsTimeRef = useRef<number>(performance.now());

  // Smooth camera zoom-to-fit framing for active illuminated subgraph
  const frameActiveSubgraph = useCallback((targetPKs: Set<string>) => {
    const canvas = canvasRef.current;
    if (!canvas || targetPKs.size === 0) return;

    const matchedNodes = nodes.filter((n) => targetPKs.has(n.primary_key) && n.x !== undefined && n.y !== undefined);
    if (matchedNodes.length === 0) return;

    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    matchedNodes.forEach((n) => {
      minX = Math.min(minX, n.x!);
      maxX = Math.max(maxX, n.x!);
      minY = Math.min(minY, n.y!);
      maxY = Math.max(maxY, n.y!);
    });

    const width = canvas.width / (window.devicePixelRatio || 1);
    const height = canvas.height / (window.devicePixelRatio || 1);

    const boundsWidth = Math.max(maxX - minX, 100);
    const boundsHeight = Math.max(maxY - minY, 100);

    const scale = Math.min(2.5, Math.max(0.6, 0.8 / Math.max(boundsWidth / width, boundsHeight / height)));
    const centerX = (minX + maxX) / 2;
    const centerY = (minY + maxY) / 2;

    const targetTransform = d3.zoomIdentity
      .translate(width / 2, height / 2)
      .scale(scale)
      .translate(-centerX, -centerY);

    const selection = d3.select(canvas);
    if (zoomBehaviorRef.current) {
      selection.transition().duration(350).ease(d3.easeCubicInOut).call(zoomBehaviorRef.current.transform, targetTransform);
    }
  }, [nodes]);

  // Trigger camera framing when isIlluminated changes
  useEffect(() => {
    if (isIlluminated && activeNodePKs.size > 0) {
      frameActiveSubgraph(activeNodePKs);
    }
  }, [isIlluminated, activeNodePKs, frameActiveSubgraph]);

  // Main canvas rendering loop
  const render = useCallback(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    const width = canvas.width / dpr;
    const height = canvas.height / dpr;

    // Measure FPS
    frameCountRef.current += 1;
    const now = performance.now();
    if (now - lastFpsTimeRef.current >= 1000) {
      setFps(Math.round((frameCountRef.current * 1000) / (now - lastFpsTimeRef.current)));
      frameCountRef.current = 0;
      lastFpsTimeRef.current = now;
    }

    ctx.save();
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Apply current zoom/pan transformation
    const transform = transformRef.current;
    ctx.translate(transform.x * dpr, transform.y * dpr);
    ctx.scale(transform.k * dpr, transform.k * dpr);

    // 1. Draw Architectural Grid Noise in Background
    ctx.save();
    ctx.strokeStyle = CANVAS_PALETTE.gridLines;
    ctx.lineWidth = 0.5 / transform.k;
    const gridSize = 100;
    const startX = Math.floor((-transform.x / transform.k - width) / gridSize) * gridSize;
    const endX = Math.ceil((-transform.x / transform.k + width * 2) / gridSize) * gridSize;
    const startY = Math.floor((-transform.y / transform.k - height) / gridSize) * gridSize;
    const endY = Math.ceil((-transform.y / transform.k + height * 2) / gridSize) * gridSize;

    ctx.beginPath();
    for (let x = startX; x <= endX; x += gridSize) {
      ctx.moveTo(x, startY);
      ctx.lineTo(x, endY);
    }
    for (let y = startY; y <= endY; y += gridSize) {
      ctx.moveTo(startX, y);
      ctx.lineTo(endX, y);
    }
    ctx.stroke();
    ctx.restore();

    // 2. Draw Orbital Blueprint Linework around major Hubs (Level 0/1 entities)
    nodes.forEach((node) => {
      if (['Policy', 'PublicLaw', 'Jurisdiction'].includes(node.label) && node.x !== undefined && node.y !== undefined) {
        ctx.save();
        const isActive = activeNodePKs.has(node.primary_key);
        ctx.strokeStyle = isActive ? 'rgba(255, 183, 3, 0.45)' : 'rgba(51, 65, 85, 0.35)';
        ctx.lineWidth = 1.0 / transform.k;
        ctx.setLineDash([4 / transform.k, 6 / transform.k]);
        ctx.beginPath();
        ctx.arc(node.x, node.y, (node.radius || 15) * 3.5, 0, Math.PI * 2);
        ctx.stroke();
        ctx.restore();
      }
    });

    // 3. Draw Links / Laser Struts
    links.forEach((link) => {
      const source = link.source as GraphNode;
      const target = link.target as GraphNode;
      if (source.x === undefined || source.y === undefined || target.x === undefined || target.y === undefined) return;

      const isActiveEdge = activeEdgeKeys.has(link.edge_key) ||
        (activeNodePKs.has(source.primary_key) && activeNodePKs.has(target.primary_key));

      let alpha = 0.55;
      let strokeColor = 'rgba(71, 85, 105, 0.6)';
      let lineWidth = 1.2 / transform.k;

      if (isIlluminated) {
        if (isActiveEdge) {
          alpha = 1.0;
          strokeColor = CANVAS_PALETTE.activeEdge;
          lineWidth = 3.5 / transform.k;
        } else {
          alpha = CANVAS_PALETTE.inactiveAttenuation;
          strokeColor = 'rgba(30, 41, 59, 0.3)';
        }
      }

      ctx.save();
      ctx.globalAlpha = alpha;
      ctx.strokeStyle = strokeColor;
      ctx.lineWidth = lineWidth;

      // Draw link line
      ctx.beginPath();
      ctx.moveTo(source.x, source.y);
      ctx.lineTo(target.x, target.y);
      ctx.stroke();

      // If active edge, draw animated directional indicator pulse
      if (isActiveEdge) {
        const midX = (source.x + target.x) / 2;
        const midY = (source.y + target.y) / 2;
        const angle = Math.atan2(target.y - source.y, target.x - source.x);

        ctx.save();
        ctx.translate(midX, midY);
        ctx.rotate(angle);
        ctx.fillStyle = CANVAS_PALETTE.accentAmber;
        ctx.beginPath();
        ctx.moveTo(6 / transform.k, 0);
        ctx.lineTo(-4 / transform.k, -3.5 / transform.k);
        ctx.lineTo(-4 / transform.k, 3.5 / transform.k);
        ctx.closePath();
        ctx.fill();
        ctx.restore();
      }

      ctx.restore();
    });

    // 4. Draw Nodes with Halftone Dot Shading
    nodes.forEach((node) => {
      if (node.x === undefined || node.y === undefined) return;

      const isActive = activeNodePKs.has(node.primary_key);
      const isSelected = selectedNode?.primary_key === node.primary_key;
      const isHovered = hoveredNode?.primary_key === node.primary_key;

      let alpha = 1.0;
      if (isIlluminated && !isActive) {
        alpha = CANVAS_PALETTE.inactiveAttenuation;
      }

      const visual = getNodeVisual(node.label);
      const baseRadius = visual.radius || 10;
      const radius = (isActive ? baseRadius * 1.3 : baseRadius) / Math.max(0.7, Math.min(1.4, transform.k));

      ctx.save();
      ctx.globalAlpha = alpha;

      // Pulsing outer halo for active/selected node
      if (isActive || isSelected) {
        ctx.save();
        ctx.strokeStyle = CANVAS_PALETTE.activeHalo;
        ctx.lineWidth = 3.5 / transform.k;
        ctx.beginPath();
        ctx.arc(node.x, node.y, radius + 5 / transform.k, 0, Math.PI * 2);
        ctx.stroke();
        ctx.restore();
      }

      // Base Node Fill
      ctx.beginPath();
      ctx.arc(node.x, node.y, radius, 0, Math.PI * 2);
      ctx.fillStyle = visual.badgeColor;
      ctx.fill();

      // Screen-Space Halftone Screening Simulation (Concentric Micro-Dots Shading)
      if (radius > 7) {
        ctx.save();
        ctx.beginPath();
        ctx.arc(node.x, node.y, radius, 0, Math.PI * 2);
        ctx.clip();

        // High-illumination offset dot cluster
        const highlightOffset = radius * 0.35;
        const hlX = node.x - highlightOffset;
        const hlY = node.y - highlightOffset;

        ctx.fillStyle = isActive ? '#fffbeb' : 'rgba(255, 255, 255, 0.4)';
        ctx.beginPath();
        ctx.arc(hlX, hlY, radius * 0.45, 0, Math.PI * 2);
        ctx.fill();

        // 45-degree halftone shadow dots on lower terminator
        ctx.fillStyle = 'rgba(10, 17, 40, 0.55)';
        const shadowSteps = 3;
        for (let i = 1; i <= shadowSteps; i++) {
          const dotRadius = (radius * 0.22) / i;
          const sX = node.x + (radius * 0.45 * i) / shadowSteps;
          const sY = node.y + (radius * 0.45 * i) / shadowSteps;
          ctx.beginPath();
          ctx.arc(sX, sY, dotRadius, 0, Math.PI * 2);
          ctx.fill();
        }
        ctx.restore();
      }

      // Border ring
      ctx.strokeStyle = isHovered ? '#ffffff' : 'rgba(255, 255, 255, 0.35)';
      ctx.lineWidth = 1.2 / transform.k;
      ctx.stroke();

      // 5. Node Captions (Human-readable name, non-occluding)
      const shouldShowLabel =
        isActive ||
        isSelected ||
        isHovered ||
        transform.k > 1.2 ||
        ['Policy', 'PublicLaw', 'Jurisdiction', 'CoveragePolicy'].includes(node.label);

      if (shouldShowLabel) {
        ctx.font = `${Math.max(9, Math.min(12, 11 / transform.k))}px "SF Mono", "Fira Code", monospace`;
        ctx.fillStyle = isActive ? CANVAS_PALETTE.accentAmber : CANVAS_PALETTE.textPrimary;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';

        // Truncate long captions cleanly
        let displayName = node.name || node.primary_key;
        if (displayName.length > 28) {
          displayName = displayName.substring(0, 26) + '...';
        }

        // Leader background badge
        const textWidth = ctx.measureText(displayName).width;
        const textY = node.y + radius + 4 / transform.k;
        ctx.fillStyle = 'rgba(10, 17, 40, 0.85)';
        ctx.fillRect(node.x - textWidth / 2 - 3 / transform.k, textY - 1 / transform.k, textWidth + 6 / transform.k, 13 / transform.k);

        ctx.fillStyle = isActive ? CANVAS_PALETTE.accentAmber : '#e2e8f0';
        ctx.fillText(displayName, node.x, textY);
      }

      ctx.restore();
    });

    ctx.restore();
  }, [nodes, links, isIlluminated, activeNodePKs, activeEdgeKeys, selectedNode, hoveredNode]);

  // Set up d3 force simulation
  useEffect(() => {
    if (!nodes.length) return;

    const canvas = canvasRef.current;
    if (!canvas) return;
    const width = canvas.clientWidth || 900;
    const height = canvas.clientHeight || 650;

    // Simulation parameters conforming to Ticket 005
    const simulation = d3
      .forceSimulation<GraphNode>(nodes)
      .force(
        'link',
        d3
          .forceLink<GraphNode, d3.SimulationLinkDatum<GraphNode>>(links as any)
          .id((d) => d.primary_key)
          .distance(45)
      )
      .force('charge', d3.forceManyBody().strength(-120))
      .force(
        'collision',
        d3.forceCollide<GraphNode>().radius((d) => (d.radius || 10) + 6)
      )
      .force('center', d3.forceCenter(width / 2, height / 2).strength(0.08))
      .alphaDecay(0.028);

    simulation.on('tick', () => {
      render();
    });

    simulationRef.current = simulation;

    return () => {
      simulation.stop();
    };
  }, [nodes, links, render]);

  // Manage physics freeze toggle
  useEffect(() => {
    if (!simulationRef.current) return;
    if (physicsFrozen) {
      simulationRef.current.alpha(0);
      simulationRef.current.stop();
    } else {
      simulationRef.current.alpha(0.3).restart();
    }
  }, [physicsFrozen]);

  // Zoom and Drag Behavior
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const zoom = d3
      .zoom<HTMLCanvasElement, unknown>()
      .scaleExtent([0.2, 5.0])
      .on('zoom', (event) => {
        transformRef.current = event.transform;
        render();
      });

    zoomBehaviorRef.current = zoom;
    d3.select(canvas).call(zoom);

    // Initial center transform
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;

    render();
  }, [render]);

  // Handle Resize
  useEffect(() => {
    const handleResize = () => {
      const canvas = canvasRef.current;
      if (!canvas) return;
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      render();
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [render]);

  // Mouse click and hover detection
  const handlePointerDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const transform = transformRef.current;

    const mouseX = (e.clientX - rect.left - transform.x) / transform.k;
    const mouseY = (e.clientY - rect.top - transform.y) / transform.k;

    // Hit test against nodes
    let clicked: GraphNode | null = null;
    for (let i = nodes.length - 1; i >= 0; i--) {
      const node = nodes[i];
      if (node.x === undefined || node.y === undefined) continue;
      const dist = Math.hypot(node.x - mouseX, node.y - mouseY);
      if (dist <= (node.radius || 10) + 4) {
        clicked = node;
        break;
      }
    }

    selectNode(clicked);
  };

  const handlePointerMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const transform = transformRef.current;

    const mouseX = (e.clientX - rect.left - transform.x) / transform.k;
    const mouseY = (e.clientY - rect.top - transform.y) / transform.k;

    let hovered: GraphNode | null = null;
    for (let i = nodes.length - 1; i >= 0; i--) {
      const node = nodes[i];
      if (node.x === undefined || node.y === undefined) continue;
      const dist = Math.hypot(node.x - mouseX, node.y - mouseY);
      if (dist <= (node.radius || 10) + 4) {
        hovered = node;
        break;
      }
    }

    if (hovered !== hoveredNode) {
      setHoveredNode(hovered);
      canvas.style.cursor = hovered ? 'pointer' : 'crosshair';
      render();
    }
  };

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%', overflow: 'hidden' }}>
      <canvas
        ref={canvasRef}
        style={{
          width: '100%',
          height: '100%',
          display: 'block',
          backgroundColor: CANVAS_PALETTE.bgVoid,
        }}
        onClick={handlePointerDown}
        onMouseMove={handlePointerMove}
      />

      {/* Blueprint HUD Telemetry Overlay */}
      <div
        style={{
          position: 'absolute',
          top: 14,
          left: 14,
          backgroundColor: 'rgba(10, 17, 40, 0.88)',
          border: '1px solid rgba(255, 183, 3, 0.35)',
          padding: '8px 14px',
          borderRadius: 4,
          fontFamily: '"SF Mono", "Fira Code", monospace',
          fontSize: 11,
          color: '#e2e8f0',
          boxShadow: '0 4px 16px rgba(0, 0, 0, 0.4)',
          pointerEvents: 'none',
          userSelect: 'none',
        }}
      >
        <div style={{ color: CANVAS_PALETTE.accentAmber, fontWeight: 700, marginBottom: 4, letterSpacing: '0.05em' }}>
          ◈ LAG KNOWLEDGE BLUEPRINT HUD
        </div>
        <div style={{ display: 'flex', gap: 14 }}>
          <span>NODES: <strong style={{ color: '#38bdf8' }}>{nodes.length}</strong></span>
          <span>EDGES: <strong style={{ color: '#38bdf8' }}>{links.length}</strong></span>
          <span>FPS: <strong style={{ color: fps >= 55 ? '#4ade80' : '#f87171' }}>{fps}</strong></span>
          <span>STATUS: <strong style={{ color: isIlluminated ? CANVAS_PALETTE.accentAmber : '#94a3b8' }}>
            {isIlluminated ? 'PATH ILLUMINATED' : 'EXPLORATION MODE'}
          </strong></span>
        </div>
      </div>

      {loading && (
        <div
          style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: 'rgba(10, 17, 40, 0.75)',
            backdropFilter: 'blur(3px)',
            color: CANVAS_PALETTE.accentAmber,
            fontFamily: '"SF Mono", monospace',
            fontSize: 14,
            fontWeight: 600,
            letterSpacing: '0.08em',
          }}
        >
          ◈ SYNCHRONIZING GRAPH TOPOLOGY...
        </div>
      )}
    </div>
  );
};
