// Draws orthogonal arrows between elements after layout.
// wire(fromId, toId, {from:'right', to:'left', at:0.5, at2:0.5, color, dash, width, label, labelAt})
const WIRES = [];
function wire(a, b, o = {}) { WIRES.push([a, b, o]); }

function drawWires() {
  const canvas = document.querySelector('.canvas');
  const c = canvas.getBoundingClientRect();
  const svg = document.querySelector('svg.wires');
  svg.setAttribute('width', c.width);
  svg.setAttribute('height', c.height);
  const ns = 'http://www.w3.org/2000/svg';
  const defs = document.createElementNS(ns, 'defs');
  svg.appendChild(defs);
  const markers = {};
  const marker = color => {
    if (markers[color]) return markers[color];
    const id = 'm' + Object.keys(markers).length;
    const m = document.createElementNS(ns, 'marker');
    Object.entries({ id, viewBox: '0 0 10 10', refX: 8, refY: 5, markerWidth: 5, markerHeight: 5, orient: 'auto-start-reverse' })
      .forEach(([k, v]) => m.setAttribute(k, v));
    m.innerHTML = `<path d="M0,0 L10,5 L0,10 z" fill="${color}"/>`;
    defs.appendChild(m);
    return (markers[color] = id);
  };
  const pt = (el, side, at) => {
    const r = el.getBoundingClientRect();
    const x = r.left - c.left, y = r.top - c.top;
    if (side === 'right') return [x + r.width, y + r.height * at];
    if (side === 'left') return [x, y + r.height * at];
    if (side === 'top') return [x + r.width * at, y];
    return [x + r.width * at, y + r.height];
  };
  for (const [a, b, o] of WIRES) {
    const from = o.from || 'right', to = o.to || 'left';
    let [x1, y1] = pt(document.getElementById(a), from, o.at ?? 0.5);
    let [x2, y2] = pt(document.getElementById(b), to, o.at2 ?? 0.5);
    if (o.x != null) x1 = x2 = c.width * o.x;  // straight vertical wire at a fixed fraction of the canvas
    const vert = s => s === 'top' || s === 'bottom';
    let d, lx, ly;
    if (vert(from) && vert(to)) {
      const my = o.mid ?? (y1 + y2) / 2;
      d = `M${x1},${y1} V${my} H${x2} V${y2}`; lx = (x1 + x2) / 2; ly = my;
    } else if (!vert(from) && !vert(to)) {
      const mx = o.mid ?? (x1 + x2) / 2;
      d = `M${x1},${y1} H${mx} V${y2} H${x2}`; lx = mx; ly = (y1 + y2) / 2;
    } else if (vert(from)) {
      d = `M${x1},${y1} V${y2} H${x2}`; lx = x1; ly = y2;
    } else {
      d = `M${x1},${y1} H${x2} V${y2}`; lx = x2; ly = y1;
    }
    const color = o.color || '#475569';
    const p = document.createElementNS(ns, 'path');
    p.setAttribute('d', d);
    p.setAttribute('fill', 'none');
    p.setAttribute('stroke', color);
    p.setAttribute('stroke-width', o.width || 3);
    p.setAttribute('stroke-linejoin', 'round');
    if (o.dash) p.setAttribute('stroke-dasharray', o.dash);
    p.setAttribute('marker-end', `url(#${marker(color)})`);
    if (o.both) p.setAttribute('marker-start', `url(#${marker(color)})`);
    svg.appendChild(p);
    if (o.label) {
      const l = document.createElement('div');
      l.className = 'wire-label';
      l.innerHTML = o.label;
      l.style.left = (o.lx ?? lx) + 'px';
      l.style.top = (o.ly ?? ly) + 'px';
      if (o.labelColor) { l.style.borderColor = o.labelColor; l.style.color = o.labelColor; }
      canvas.appendChild(l);
    }
  }
  // Size the printed page to the canvas.
  document.documentElement.style.setProperty('--w', Math.ceil(c.width) + 'px');
  document.documentElement.style.setProperty('--h', Math.ceil(c.height) + 'px');
  const st = document.createElement('style');
  st.textContent = `@page { size: ${Math.ceil(c.width)}px ${Math.ceil(c.height)}px; margin: 0; }`;
  document.head.appendChild(st);
}
document.fonts.ready.then(drawWires);
