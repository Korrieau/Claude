// ============================================================================
// The site
// ----------------------------------------------------------------------------
// One valley, seen from a fixed raised angle. The swarm comes down it from the
// far end and the outpost sits at the near end, so the whole frame reads as a
// single front line with the camera behind our own back.
// ============================================================================
const TILE = 4;                       // world units per build tile
const GW = 64, GH = 84;               // tiles across, tiles deep
const WW = GW * TILE, WH = GH * TILE; // 256 x 336 world units
const PLATEAU = 24;                   // cliff height

// Terrain codes
const T_OPEN = 0, T_ROCK = 1;
const terrain = new Uint8Array(GW * GH);
const idx = (x, y) => y * GW + x;
const inb = (x, y) => x >= 0 && y >= 0 && x < GW && y < GH;
const clamp = (v, a, b) => v < a ? a : v > b ? b : v;
const rnd = (a, b) => a + Math.random() * (b - a);

// ---- value noise ----------------------------------------------------------
const NP = new Uint8Array(512);
for (let i = 0; i < 256; i++) { const v = (Math.random() * 256) | 0; NP[i] = v; NP[i + 256] = v; }
function vn(x, y) {
  const xi = Math.floor(x), yi = Math.floor(y);
  const xf = x - xi, yf = y - yi;
  const u = xf * xf * (3 - 2 * xf), v = yf * yf * (3 - 2 * yf);
  const h = (a, b) => NP[(NP[a & 255] + (b & 255)) & 255] / 255;
  const a = h(xi, yi), b = h(xi + 1, yi), c = h(xi, yi + 1), e = h(xi + 1, yi + 1);
  const t1 = a + (b - a) * u, t2 = c + (e - c) * u;
  return t1 + (t2 - t1) * v;
}
function fbm(x, y) {
  return vn(x, y) * 0.54 + vn(x * 2.13, y * 2.13) * 0.28 +
         vn(x * 4.37, y * 4.37) * 0.12 + vn(x * 8.7, y * 8.7) * 0.06;
}

// ---- layout ---------------------------------------------------------------
// Two spurs pinch the valley twice on the way down. The ramps through them are
// the only ways through, which is what turns "hold a line" into a place rather
// than a number.
const GATES = [];
function blob(cx, cy, r) {
  const r2 = r * r;
  for (let y = Math.floor(cy - r); y <= cy + r; y++)
    for (let x = Math.floor(cx - r); x <= cx + r; x++)
      if (inb(x, y) && (x - cx) ** 2 + (y - cy) ** 2 <= r2) terrain[idx(x, y)] = T_ROCK;
}
function carve(cx, cy, r) {
  const r2 = r * r;
  for (let y = Math.floor(cy - r); y <= cy + r; y++)
    for (let x = Math.floor(cx - r); x <= cx + r; x++)
      if (inb(x, y) && (x - cx) ** 2 + (y - cy) ** 2 <= r2) terrain[idx(x, y)] = T_OPEN;
}
function ridge(pts, th, seed) {
  for (let i = 0; i < pts.length - 1; i++) {
    const [x0, y0] = pts[i], [x1, y1] = pts[i + 1];
    const steps = Math.max(2, Math.ceil(Math.hypot(x1 - x0, y1 - y0) * 1.6));
    for (let k = 0; k <= steps; k++) {
      const u = k / steps, x = x0 + (x1 - x0) * u, y = y0 + (y1 - y0) * u;
      blob(x, y, th * (0.60 + 0.75 * vn(x * 0.17 + seed, y * 0.17 + seed)));
    }
  }
}

function buildLayout() {
  terrain.fill(T_OPEN);

  // valley walls: the frame of the whole map
  ridge([[-2, -2], [2, 14], [-1, 30], [3, 48], [0, 66], [2, 86]], 7.5, 4.1);
  ridge([[GW + 2, -2], [GW - 3, 15], [GW + 1, 32], [GW - 4, 50], [GW - 1, 68], [GW + 1, 86]], 7.5, 61.7);

  // the far shoulder, with one pass in it
  ridge([[6, 17], [22, 20], [30, 16]], 6.0, 12.9);
  ridge([[40, 17], [54, 21], [GW - 4, 17]], 6.0, 33.5);

  // the near shoulder, the line the outpost actually defends
  ridge([[4, 44], [18, 47], [26, 43]], 6.6, 51.2);
  ridge([[38, 44], [52, 48], [GW - 3, 44]], 6.6, 70.4);

  // outcrops so the floor is not a board
  for (let i = 0; i < 13; i++) {
    const px = rnd(8, GW - 8), py = rnd(6, GH * 0.62);
    ridge([[px, py], [px + rnd(-6, 6), py + rnd(-4, 4)]], rnd(2.4, 4.2), i * 9.3);
  }

  // the passes
  const cut = (x, y, r) => { carve(x, y, r); GATES.push({ x, y }); };
  cut(GW * 0.53, 18, 5.5);
  cut(GW * 0.30, 45.5, 5.0);
  cut(GW * 0.72, 45.5, 5.0);

  // held ground in front of the camera
  for (let y = 54; y < GH - 2; y++) for (let x = 3; x < GW - 3; x++) terrain[idx(x, y)] = T_OPEN;
  carve(GW / 2, GH - 12, 12);
}
buildLayout();

// ============================================================================
// Terrain mesh
// ----------------------------------------------------------------------------
// A heightfield, not a stack of painted layers. The plateau is a hard step in
// that field, so the cliff face falls out of the geometry and is lit by the
// same sun as everything else. Rock is wherever the ground is steep, which
// means the material follows the shape instead of being assigned per tile.
// ============================================================================
const SS = 3;                                  // heightfield samples per tile
const HW = GW * SS + 1, HH = GH * SS + 1;
const height = new Float32Array(HW * HH);
const rockness = new Float32Array(HW * HH);

function buildHeightfield() {
  const m = new Float32Array(HW * HH), g = new Float32Array(HW * HH);
  for (let j = 0; j < HH; j++) for (let i = 0; i < HW; i++) {
    const gx = clamp((i / SS) | 0, 0, GW - 1), gy = clamp((j / SS) | 0, 0, GH - 1);
    m[j * HW + i] = terrain[idx(gx, gy)] === T_ROCK ? 1 : 0;
  }
  // Blur then re-threshold. This is what takes the plateau outline off the
  // tile grid: the boundary ends up following a smooth iso-contour instead of
  // a staircase of square cells.
  const RB = 4, W2 = RB * 2 + 1;
  for (let pass = 0; pass < 3; pass++) {
    for (let j = 0; j < HH; j++) {
      const row = j * HW; let acc = 0;
      for (let i = -RB; i <= RB; i++) acc += m[row + clamp(i, 0, HW - 1)];
      for (let i = 0; i < HW; i++) {
        g[row + i] = acc / W2;
        acc += m[row + Math.min(HW - 1, i + RB + 1)] - m[row + Math.max(0, i - RB)];
      }
    }
    for (let i = 0; i < HW; i++) {
      let acc = 0;
      for (let j = -RB; j <= RB; j++) acc += g[clamp(j, 0, HH - 1) * HW + i];
      for (let j = 0; j < HH; j++) {
        m[j * HW + i] = acc / W2;
        acc += g[Math.min(HH - 1, j + RB + 1) * HW + i] - g[Math.max(0, j - RB) * HW + i];
      }
    }
  }
  for (let j = 0; j < HH; j++) for (let i = 0; i < HW; i++) {
    const k = j * HW + i, wx = i / SS * TILE, wz = j / SS * TILE;
    // Macro relief first. Without this the site is a tray: flat floor with
    // flat lids dropped on it, which is what made the terrain read wrong.
    // The ground has to be a valley before anything is built on it - walls
    // climbing away on both sides, and the whole floor rising as it runs
    // back up the valley away from the camera.
    const ax = Math.abs(wx - WW / 2) / (WW / 2);
    // The floor has to stay the majority of the frame, so the sides only
    // start climbing in the outer third and top out well under the map width.
    const w = clamp((ax - 0.62) / 0.38, 0, 1);
    const walls = w * w * (3 - 2 * w) * 74 + ax * ax * 9;
    const back = Math.pow(1 - wz / WH, 2.0) * 30;
    let roll = (fbm(wx / 105, wz / 105) - 0.5) * 9
             + (fbm(wx / 34, wz / 34) - 0.5) * 3.4
             + (fbm(wx / 11, wz / 11) - 0.5) * 1.2;
    // gullies and buttresses on the valley sides, so the walls are eroded
    // rock rather than a poured ramp
    roll += w * ((fbm(wx / 19 + 5.5, wz / 46 + 2.2) - 0.5) * 26
               + (fbm(wx / 7 + 1.1, wz / 15 + 9.9) - 0.5) * 8);
    // then the designed benches, as a hard step on top of that relief
    const step = clamp((m[k] - 0.46) * 2.2, 0, 1);
    const shaped = step * step * (3 - 2 * step);
    height[k] = walls + back + roll + shaped * PLATEAU;
    rockness[k] = shaped;
  }
}
buildHeightfield();

// Anything too steep to walk becomes rock for the simulation as well, so the
// terrain the player reads is exactly the terrain the swarm has to obey.
function deriveFootingFromSlope() {
  for (let gy = 0; gy < GH; gy++) for (let gx = 0; gx < GW; gx++) {
    let lo = 1e9, hi = -1e9;
    for (let j = 0; j <= SS; j++) for (let i = 0; i <= SS; i++) {
      const h = height[clamp(gy * SS + j, 0, HH - 1) * HW + clamp(gx * SS + i, 0, HW - 1)];
      if (h < lo) lo = h; if (h > hi) hi = h;
    }
    if (hi - lo > TILE * 1.05) terrain[idx(gx, gy)] = T_ROCK;
  }
}
deriveFootingFromSlope();

function sampleHeight(wx, wz) {
  const fx = clamp(wx / TILE * SS, 0, HW - 1.001), fz = clamp(wz / TILE * SS, 0, HH - 1.001);
  const i = fx | 0, j = fz | 0, u = fx - i, v = fz - j;
  const a = height[j * HW + i], b = height[j * HW + i + 1];
  const c = height[(j + 1) * HW + i], d = height[(j + 1) * HW + i + 1];
  return (a + (b - a) * u) + ((c + (d - c) * u) - (a + (b - a) * u)) * v;
}

// ---- surface colour -------------------------------------------------------
// Sampled off the reference captures rather than picked by eye: the grass
// there is olive and desaturated, and the stone is a cool blue-grey.
const C_GRASS_LO = new THREE.Color('#3F5029');
const C_GRASS_HI = new THREE.Color('#8B9B58');
const C_DIRT     = new THREE.Color('#7C7458');
const C_ROCK_LO  = new THREE.Color('#4E5049');
const C_ROCK_HI  = new THREE.Color('#9B9C92');

function buildTerrainMesh() {
  const geo = new THREE.PlaneGeometry(WW, WH, HW - 1, HH - 1);
  geo.rotateX(-Math.PI / 2);
  const pos = geo.attributes.position;
  const col = new Float32Array(pos.count * 3);
  const c = new THREE.Color();
  for (let j = 0; j < HH; j++) for (let i = 0; i < HW; i++) {
    const k = j * HW + i;
    pos.setY(k, height[k]);
  }
  geo.computeVertexNormals();
  const nrm = geo.attributes.normal;
  for (let j = 0; j < HH; j++) for (let i = 0; i < HW; i++) {
    const k = j * HW + i;
    const wx = i / SS * TILE, wz = j / SS * TILE;
    const slope = 1 - nrm.getY(k);                     // 0 flat, 1 vertical
    const rocky = clamp(slope * 3.4, 0, 1);
    if (rocky > 0.5) {
      // stone: value from how much light the face would take, plus grain
      const band = fbm(wx / 5.5, wz / 3.2);      // bedding, mostly horizontal
      c.copy(C_ROCK_LO).lerp(C_ROCK_HI, clamp(0.42 + band * 0.62, 0, 1));
    } else {
      const wet = fbm(wx / 70 + 31.7, wz / 70 + 12.3);
      c.copy(C_GRASS_LO).lerp(C_GRASS_HI, clamp((wet - 0.34) * 2.4 + fbm(wx / 9, wz / 9) * 0.5, 0, 1));
      if (wet > 0.62) c.lerp(C_DIRT, clamp((wet - 0.62) * 2.6, 0, 0.55));
      if (rocky > 0.16) c.lerp(C_ROCK_LO, (rocky - 0.16) * 1.6);
    }
    col[k * 3] = c.r; col[k * 3 + 1] = c.g; col[k * 3 + 2] = c.b;
  }
  geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
  const mat = new THREE.MeshStandardMaterial({
    vertexColors: true, roughness: 0.97, metalness: 0.0,
    map: detailTexture(), flatShading: false,
  });
  triplanar(mat, 1 / 22);
  const mesh = new THREE.Mesh(geo, mat);
  mesh.position.set(WW / 2, 0, WH / 2);
  mesh.receiveShadow = true;
  return mesh;
}

// Project the detail map from all three axes and blend by the surface
// normal. A plane's own UVs run flat across the map, so anything vertical -
// every cliff face - smears the texture into streaks down its whole height.
// That smear was the single worst artefact on the terrain.
function triplanar(mat, scale) {
  mat.onBeforeCompile = sh => {
    sh.uniforms.uTriScale = { value: scale };
    sh.vertexShader = sh.vertexShader
      .replace('#include <common>',
        '#include <common>\nvarying vec3 vWPos;\nvarying vec3 vWNrm;')
      .replace('#include <begin_vertex>',
        '#include <begin_vertex>\nvWPos = (modelMatrix * vec4(transformed, 1.0)).xyz;')
      .replace('#include <beginnormal_vertex>',
        '#include <beginnormal_vertex>\nvWNrm = normalize(mat3(modelMatrix) * objectNormal);');
    sh.fragmentShader = sh.fragmentShader
      .replace('#include <common>',
        '#include <common>\nvarying vec3 vWPos;\nvarying vec3 vWNrm;\nuniform float uTriScale;')
      .replace('#include <map_fragment>', [
        'vec3 triW = pow(abs(vWNrm), vec3(4.0));',
        'triW /= (triW.x + triW.y + triW.z);',
        'vec4 triC = texture2D(map, vWPos.zy * uTriScale) * triW.x',
        '          + texture2D(map, vWPos.xz * uTriScale) * triW.y',
        '          + texture2D(map, vWPos.xy * uTriScale) * triW.z;',
        'diffuseColor *= triC;',
      ].join('\n'));
  };
  mat.customProgramCacheKey = () => 'triplanar' + scale;
}

// A fine break-up texture so close ground is not a flat wash. Neutral, so it
// works over grass and stone alike.
function detailTexture() {
  const S = 256, c = document.createElement('canvas');
  c.width = c.height = S;
  const x = c.getContext('2d');
  x.fillStyle = '#808080'; x.fillRect(0, 0, S, S);
  for (let i = 0; i < 2600; i++) {
    const v = (Math.random() * 40 - 20) | 0;
    x.fillStyle = `rgba(${128 + v},${128 + v},${128 + v},0.5)`;
    const r = rnd(1, 7), px = Math.random() * S, py = Math.random() * S;
    x.beginPath(); x.ellipse(px, py, r, r * rnd(0.4, 1), rnd(0, 3.1), 0, 6.2832); x.fill();
  }
  // isotropic grain only: anything directional stretches into streaks where
  // the surface turns vertical
  for (let i = 0; i < 9000; i++) {
    const v = (Math.random() * 54 - 27) | 0;
    x.fillStyle = `rgba(${128 + v},${128 + v},${128 + v},0.34)`;
    const r = rnd(0.5, 1.9);
    x.beginPath(); x.arc(Math.random() * S, Math.random() * S, r, 0, 6.2832); x.fill();
  }
  const t = new THREE.CanvasTexture(c);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(1, 1);
  t.anisotropy = 8;
  return t;
}

// ============================================================================
// Scene
// ============================================================================
const scene = new THREE.Scene();
const SKY = new THREE.Color('#B7D3DE');
scene.background = SKY;
scene.fog = new THREE.Fog(SKY, 300, 1250);

const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
document.getElementById('stage').appendChild(renderer.domElement);

// The sun is warm and comes over the left shoulder; the sky fills the shade
// cool. That single contrast is what stops a landscape looking flat.
const sun = new THREE.DirectionalLight('#FFE7BE', 2.5);
sun.position.set(-1, 1.55, -0.75).normalize().multiplyScalar(300);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 40; sun.shadow.camera.far = 720;
sun.shadow.camera.left = -230; sun.shadow.camera.right = 230;
sun.shadow.camera.top = 230; sun.shadow.camera.bottom = -230;
sun.shadow.bias = -0.0012;
sun.shadow.normalBias = 0.6;
scene.add(sun);
scene.add(sun.target);
scene.add(new THREE.HemisphereLight('#B6D2E6', '#54633A', 1.9));
scene.add(new THREE.AmbientLight('#8FA6B8', 0.35));

scene.add(buildTerrainMesh());

// The land does not stop at the playable edge. A coarse surround rises into
// ridges outside the map and sits just under the border plateau inside it, so
// the site reads as one valley in a range rather than a slab in a void.
function buildSurround() {
  const SPAN = 2600, N = 150;
  const geo = new THREE.PlaneGeometry(SPAN, SPAN, N, N);
  geo.rotateX(-Math.PI / 2);
  const pos = geo.attributes.position;
  const col = new Float32Array(pos.count * 3);
  const c = new THREE.Color();
  const FAR_LO = new THREE.Color('#4A5A3E'), FAR_HI = new THREE.Color('#8C9AA0');
  for (let i = 0; i < pos.count; i++) {
    const wx = pos.getX(i) + WW / 2, wz = pos.getZ(i) + WH / 2;
    // signed distance to the play area: negative inside, positive outside
    const sx = Math.max(-wx, wx - WW), sz = Math.max(-wz, wz - WH);
    const sd = (sx > 0 || sz > 0)
      ? Math.hypot(Math.max(sx, 0), Math.max(sz, 0))
      : Math.max(sx, sz);
    let h;
    if (sd < -5) {
      h = -90;                                  // safely under the play mesh
    } else {
      const t = clamp(sd / 500, 0, 1);
      const ridged = Math.abs(fbm(wx / 230 + 7.1, wz / 230 + 3.3) - 0.5) * 2;
      // start from the height the map edge itself reaches, then keep climbing
      const edge = sampleHeight(clamp(wx, 1, WW - 1), clamp(wz, 1, WH - 1));
      const rise = edge + t * (60 + (1 - ridged) * 300 + fbm(wx / 80, wz / 80) * 90) * t
        + Math.min(t * 9, 1) * ((fbm(wx / 46 + 2.7, wz / 46 + 8.4) - 0.5) * 46
                              + (fbm(wx / 17, wz / 17) - 0.5) * 13);
      h = sd < 0 ? -90 + (rise + 90) * (sd + 5) / 5 : rise;
    }
    pos.setY(i, h);
    const t2 = clamp(Math.max(sd, 0) / 430, 0, 1);
    c.copy(FAR_LO).lerp(FAR_HI, clamp(t2 * 1.1 - 0.05 + (h - 90) / 380, 0, 1));
    col[i * 3] = c.r; col[i * 3 + 1] = c.g; col[i * 3 + 2] = c.b;
  }
  geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
  geo.computeVertexNormals();
  const m = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({
    vertexColors: true, roughness: 1, metalness: 0 }));
  m.position.set(WW / 2, 0, WH / 2);
  return m;
}
scene.add(buildSurround());

// ============================================================================
// Camera — fixed angle, pan and zoom only
// ============================================================================
const camera = new THREE.PerspectiveCamera(40, 1, 1, 2500);
const TILT = 47 * Math.PI / 180;
const cam = { tx: WW / 2, tz: WH - 130, dist: 430 };
function placeCamera() {
  cam.tx = clamp(cam.tx, 30, WW - 30);
  cam.tz = clamp(cam.tz, 40, WH - 96);
  cam.dist = clamp(cam.dist, 90, 700);
  const ty = sampleHeight(cam.tx, cam.tz);
  camera.position.set(cam.tx,
    ty + Math.sin(TILT) * cam.dist,
    cam.tz + Math.cos(TILT) * cam.dist);
  camera.lookAt(cam.tx, ty + 4, cam.tz);
  sun.target.position.set(cam.tx, ty, cam.tz);
  sun.position.copy(sun.target.position).add(new THREE.Vector3(-190, 300, -140));
}

function resize() {
  const w = innerWidth, h = innerHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
addEventListener('resize', resize);
resize();

// ---- input: drag to pan, wheel or pinch to zoom ----------------------------
const cv = renderer.domElement;
const ptrs = new Map();
let dragging = false, lastX = 0, lastY = 0, pinchD = 0, pinchZ = 0;

cv.addEventListener('contextmenu', e => e.preventDefault());
cv.addEventListener('pointerdown', e => {
  cv.setPointerCapture(e.pointerId);
  ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY });
  if (ptrs.size === 1) { dragging = true; lastX = e.clientX; lastY = e.clientY; }
  else if (ptrs.size === 2) {
    dragging = false;
    const [a, b] = [...ptrs.values()];
    pinchD = Math.hypot(a.x - b.x, a.y - b.y) || 1;
    pinchZ = cam.dist;
  }
});
cv.addEventListener('pointermove', e => {
  if (ptrs.has(e.pointerId)) ptrs.set(e.pointerId, { x: e.clientX, y: e.clientY });
  if (ptrs.size >= 2) {
    const [a, b] = [...ptrs.values()];
    const d = Math.hypot(a.x - b.x, a.y - b.y) || 1;
    cam.dist = pinchZ * (pinchD / d);
    return;
  }
  if (!dragging) return;
  // pan in the ground plane, scaled so a drag moves the ground under the finger
  const k = cam.dist * 0.0022;
  cam.tx -= (e.clientX - lastX) * k;
  cam.tz -= (e.clientY - lastY) * k / Math.cos(TILT) * 0.55;
  lastX = e.clientX; lastY = e.clientY;
});
function endPtr(e) {
  ptrs.delete(e.pointerId);
  if (ptrs.size === 0) dragging = false;
  else if (ptrs.size === 1) {
    const [only] = [...ptrs.values()];
    dragging = true; lastX = only.x; lastY = only.y;
  }
}
cv.addEventListener('pointerup', endPtr);
cv.addEventListener('pointercancel', endPtr);
cv.addEventListener('wheel', e => {
  e.preventDefault();
  cam.dist *= e.deltaY > 0 ? 1.12 : 0.89;
}, { passive: false });

// ============================================================================
// Frame
// ============================================================================
const vElev = document.getElementById('vElev'), vFps = document.getElementById('vFps');
let fpsT = performance.now(), fpsN = 0;

function frame() {
  requestAnimationFrame(frame);
  placeCamera();
  renderer.render(scene, camera);
  fpsN++;
  const now = performance.now();
  if (now - fpsT > 500) {
    vFps.textContent = Math.round(fpsN * 1000 / (now - fpsT));
    vElev.textContent = sampleHeight(cam.tx, cam.tz).toFixed(1);
    fpsT = now; fpsN = 0;
  }
}
document.getElementById('boot').remove();
frame();

window.__dbg = () => ({ tx: +cam.tx.toFixed(1), tz: +cam.tz.toFixed(1), dist: +cam.dist.toFixed(1) });
window.G = { cam, scene, camera, renderer, THREE, WW, WH, TILE, GW, GH, terrain, sampleHeight };