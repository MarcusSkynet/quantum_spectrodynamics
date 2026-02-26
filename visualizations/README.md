# Interactive 3D Visualizations

Self-contained Three.js web applications for exploring QSD geometry. Open any `.html` file directly in a modern web browser — no server or build step required.

## Contents

| File | Visualization | Description |
|---|---|---|
| `qsd_4simplex.html` | **4-Simplex: The Engine of Time** | Interactive exploration of the 4-simplex geometry underlying the [[5,1,3]] code. Rotate, zoom, and inspect vertex/edge relationships. |
| `qsd_4simplex_network.html` | **Tensor Network: 4 Code Blocks** | Visualization of four interlocking [[5,1,3]] code blocks forming the QSD tensor network. Shows how information flows between code blocks. |
| `qsd_4simplex_snap_mechanism.html` | **Snap Mechanism: Anchor Decoupling** | Animated demonstration of the QSD "Snap" mechanism — how dimensional anchors decouple to produce syndrome energy transitions. |

## Usage

```bash
# Simply open in your browser
open qsd_4simplex.html              # macOS
xdg-open qsd_4simplex.html          # Linux
start qsd_4simplex.html             # Windows
```

### Controls

- **Left-click + drag** — Rotate the scene
- **Scroll wheel** — Zoom in/out
- **Right-click + drag** — Pan

## Technical Details

Each visualization is a single self-contained HTML file embedding:

- Three.js (r128) for 3D rendering via WebGL
- All geometry, materials, and animation logic inline
- No external dependencies or network requests

Tested in Chrome, Firefox, Safari, and Edge (2024+).
