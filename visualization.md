# GraphRAG Halftone 3D Visualization System: Functional Specification

This specification outlines the visual styling, spatial behaviors, data contracts, and interactive capabilities for a 3D GraphRAG (Graph Retrieval-Augmented Generation) visualization engine running within a React application.

---

## 1. Visual Aesthetics & Stylistic Direction

The primary goal is to replicate a high-contrast, technical print/blueprint aesthetic featuring halftone screen shading, duotone color grading, optical depth of field, and cyberpunk-style telemetry linework.

### 1.1 Color Palette & Shading

* **Duotone Contrast:** The scene must maintain a strict duotone color palette consisting of deep prussian navy for the void and low-light areas, contrasted with an intense, electric yellow/amber for high-illumination regions and active elements.


* **Halftone Screening Behavior:**
* Spherical node surfaces must render using screen-space halftone dot patterns rather than continuous, smooth lighting gradients.


* Dot diameter must dynamically scale with virtual light intensity, surface curvature, and view angle (Fresnel falloff):


* Directly lit and rim-lit surfaces must feature large, densely packed dots that merge into solid yellow fields.


* Transition zones (terminators) must display discrete, circular dots against the dark background.


* Unlit surface areas must taper to minimal dot size or disappear into the navy background completely.


* Dot alignment must maintain a fixed angular grid orientation across the screen view (resembling traditional 45° offset industrial print screens) regardless of node rotation.





### 1.2 Optical Depth & Lens Simulation

* **Shallow Depth of Field:** The viewport must simulate a macro lens optical profile where objects closer to the camera and objects far in the background are blurred, leaving an adjustable focal slice pin-sharp.


* **Cinematic Bokeh:** Blurred foreground nodes must produce enlarged, soft circles of confusion rather than simple linear blurs.


* **Focal Tracking:** The focal plane must possess the ability to dynamically retarget to selected entities or active communities when focused.

### 1.3 Edges and Interconnections

* **Primary Cluster Edges:** Direct relationships within a local cluster must present as bright, solid cylindrical struts or prominent lines bridging adjacent nodes.


* **Cross-Cluster Bridges:** Relationships spanning across separate communities must render as thinner, delicate laser-like lines with slight transparency to prevent visual clutter across the graph.


* **Visual Hierarchy:** Edge luminance and thickness must reflect relationship weight, frequency of co-occurrence, or semantic confidence.

### 1.4 Technical Blueprint HUD & Orbital Linework

* **Orbital Guides:** Major community clusters must be framed by concentric, dashed, or dotted orbital planar rings tilted in 3D space.


* **Leader Lines & Telemetry Overlays:** High-degree nodes must feature leader lines projecting toward offset monospace labels containing entity metadata, technical identifiers, and status codes.


* **Background Data Noise:** Background space must incorporate faint, decorative architectural grids, point clouds, and micro-text matrices indicating data coordinates.



---

## 2. GraphRAG Data Model & Structural Hierarchy

The system must map GraphRAG data constructs into visible spatial layers:

| GraphRAG Concept | Spatial Representation | Visual Characteristics |
| --- | --- | --- |
| **Community Hubs (Level 0 / 1)** | Root nodes of major structural clusters.

 | Largest sphere diameter, dense halftone screening, anchor point for orbital rings and cluster labels.

 |
| **Entities / Concepts** | Sub-nodes orbiting community hubs.

 | Medium and smaller spheres whose radii scale based on centrality metrics (PageRank, degree). |
| **Micro-Nodes / Attributes** | Satellite entities surrounding concepts. | Smallest spheres tightly bound to parent entity clusters. |
| **Internal Co-occurrences** | Intra-community links.

 | Thick, yellow structural connectors.

 |
| **Inter-Community Links** | Semantic relationships between distinct clusters.

 | Fine, low-opacity lines spanning large spatial distances.

 |
| **Query Retrieval Paths** | Nodes and edges selected during RAG generation. | Animated luminance pulses, increased halftone dot radius, and persistent callout banners. |

---

## 3. Spatial Physics & Topology Layout

### 3.1 3D Clustering Engine

* **Hierarchical Separation:** The engine must enforce strict community isolation in 3D space: nodes belonging to the same Leiden or Louvain community must cluster tightly, while inter-cluster repulsion forces keep major hubs distinct.
* **Stable Resting State:** Once initial layout forces resolve, nodes must transition to a stable, static equilibrium to prevent disorienting drifting while a user reads data labels.
* **Micro-Motion / Ambient Life:** In equilibrium, the scene must support subtle ambient rotation or breathing oscillations to avoid feeling completely static.

### 3.2 Dynamic Hierarchy Expansion (Level-of-Detail)

* **Cluster Aggregation:** When viewed from a distance, dense clusters must collapse into single, prominent parent community spheres.
* **Semantic Zoom:** Zooming closer to a community hub must progressively unpack child entities and fine-grained text units, fading them in with proportional halftone dot transitions.

---

## 4. Interactive Behaviors & Exploration Modes

### 4.1 Viewport Controls

* **Three-Axis Orbital Navigation:** Users must be able to pan, rotate, and zoom the camera smoothly around the 3D graph center.
* **Camera Transition Interpolation:** Selecting any node or cluster must trigger a smooth camera transition (position and target orientation) that brings the item to the center of the active focal plane.

### 4.2 Selection, Hover, and Inspection States

* **Hover States:**
* Pointing to a node must instantly intensify its halftone contrast, display its primary label, and highlight all immediately connected edges.
* Non-connected nodes within the viewport must subtly dim or recede into the navy background to reduce noise.


* **Selection State (Deep Inspection):**
* Clicking an entity locks camera focus on that node and generates an attached, billboarded HUD display showing entity summaries, extracted source citations, and relationship strengths.
* Direct structural neighbors remain highlighted; distant unlinked subgraphs fall into deep bokeh blur.



### 4.3 GraphRAG Query Visualizer Mode

The interface must provide dedicated visual modes for GraphRAG operations:

* **Global Search Mode:**
* When a high-level query is executed, the visualization highlights the top-contributing **Community Summaries** across the graph.
* Orbital rings around relevant communities brighten, while non-relevant clusters dim out.


* **Local Search Mode:**
* When an entity-specific query is executed, the engine visualizes the retrieval path: highlighting the target entity, its immediate semantic neighborhood, and the specific text-chunk relationships utilized to construct the answer.


* **Retrieval Trace Playback:**
* Ability to animate data flow along edges, visualizing how context was assembled from raw chunks into synthesis nodes.



---

## 5. UI Integration & Telemetry Presentation

* **3D-to-2D Anchor Alignment:** Monospace annotations, metadata badges, and coordinate readouts must remain visually anchored to their corresponding 3D node coordinates while rendering sharp, un-blurred vector typography in screen space.
* **Non-Occluding Information Hierarchy:** Minor node labels must hide automatically when crowded to prevent text collision, showing labels only for significant hubs until the user zooms into a local cluster.
* **Status Readouts:** The periphery of the visualization canvas must support fixed HUD panels (graph statistics, total active tokens, community count, current query mode) matching the amber/navy technical look.

---

## 6. Performance & Operational Constraints

* **Frame Budget:** The visualizer must maintain a stable 60 FPS minimum during user navigation and panning.
* **Capacity:** The architecture must comfortably render graphs consisting of at least 2,000 active nodes and 5,000 edges without frame drops.
* **Dynamic Fidelity Scaling:**
* During high-speed camera motion or continuous user panning, resource-heavy effects such as depth-of-field sampling must temporarily scale down, returning to full quality once movement ceases.


* **Data Reactivity:** The visualization must smoothly accept updated graph datasets (e.g., when new documents are ingested or new RAG queries are processed) by interpolating node positions rather than forcing a hard scene reload.