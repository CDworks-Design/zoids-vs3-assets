const $ = id => document.getElementById(id);
const dialog = $('model-dialog');
const numbers = new Intl.NumberFormat('en-US');
let assets = [], filter = 'all', viewer, selected, loadToken = 0, opener;
const bytes = n => n >= 1048576 ? `${(n / 1048576).toFixed(2)} MB` : `${Math.round(n / 1024)} KB`;
const isLow = asset => asset.id.includes('__low__');
const sourceId = asset => asset.id.split('__').at(-1).toUpperCase();
function element(tag, className, text) { const node = document.createElement(tag); if (className) node.className = className; if (text !== undefined) node.textContent = text; return node; }
function path(value) {
  if (!/^models\/zoid__[a-z0-9_]+\/(zoid__[a-z0-9_]+\.glb|textures\/texture_\d+\.png)$/.test(value)) throw new Error('Unexpected asset path');
  return value;
}
function makeCard(asset, index) {
  const card = element('article', 'model-card'); card.dataset.model = asset.id;
  const open = element('button', 'card-open'); open.type = 'button'; open.setAttribute('aria-label', `Inspect ${sourceId(asset)}${isLow(asset) ? ' low detail' : ''} in 3D`);
  const image = element('img'); image.src = `thumbnails/${asset.id}.webp`; image.alt = `Rendered preview of ${sourceId(asset)}${isLow(asset) ? ', low detail variant' : ''}`;
  image.loading = 'lazy'; image.decoding = 'async'; image.width = 640; image.height = 480;
  const imageStatus = element('span', 'card-image-status', 'Loading preview…');
  image.addEventListener('load', () => imageStatus.classList.add('loaded'));
  image.addEventListener('error', () => { imageStatus.textContent = 'Preview unavailable · open 3D view'; });
  open.append(image, imageStatus, element('span', 'card-index', String(index + 1).padStart(3, '0')));
  if (isLow(asset)) open.append(element('span', 'badge low', 'LOW DETAIL'));
  open.append(element('span', 'card-hover', 'Inspect model ↗'));
  open.addEventListener('click', () => openModel(asset, open));
  const body = element('div', 'card-body'), title = element('div', 'card-title-row');
  title.append(element('h3', '', sourceId(asset)), element('span', '', isLow(asset) ? 'LOW VARIANT' : 'STANDARD'));
  const specs = element('div', 'card-specs');
  specs.append(element('span', '', `${numbers.format(asset.validation.triangles)} triangles`), element('span', '', `${bytes(asset.model.bytes)}`));
  body.append(title, specs);
  const actions = element('div', 'card-actions');
  const download = element('a', '', 'GLB ↓'); download.href = path(asset.model.path); download.download = asset.model.path.split('/').at(-1); download.setAttribute('aria-label', `Download ${sourceId(asset)}${isLow(asset) ? ' low detail' : ''} GLB`);
  const textures = element('button', '', `${asset.textures.length} texture${asset.textures.length === 1 ? '' : 's'} ↗`); textures.type = 'button'; textures.setAttribute('aria-label', `View ${sourceId(asset)} texture downloads`); textures.addEventListener('click', () => openModel(asset, textures));
  actions.append(download, textures); card.append(open, body, actions); return card;
}
function renderGrid() {
  const query = $('search').value.trim().toLowerCase();
  let shown = assets.filter(asset => (filter === 'all' || (filter === 'low') === isLow(asset)) && `${asset.id} ${sourceId(asset)} ${asset.display_name} ${asset.source_asset}`.toLowerCase().includes(query));
  if ($('sort').value === 'size') shown.sort((a, b) => b.model.bytes - a.model.bytes);
  else if ($('sort').value === 'triangles') shown.sort((a, b) => b.validation.triangles - a.validation.triangles);
  else shown.sort((a, b) => sourceId(a).localeCompare(sourceId(b)) || Number(isLow(a)) - Number(isLow(b)));
  const fragment = document.createDocumentFragment();
  for (const asset of shown) fragment.append(makeCard(asset, assets.indexOf(asset)));
  $('grid').replaceChildren(fragment); $('empty').hidden = shown.length > 0;
  $('result-count').textContent = `${shown.length} of ${assets.length} model variants${query ? ` matching “${$('search').value.trim()}”` : ''}`;
}
async function loadCatalog() {
  $('collection-error').hidden = true; $('result-count').textContent = 'Loading collection…';
  try {
    const response = await fetch('catalog.json'); if (!response.ok) throw new Error('Catalog unavailable');
    const catalog = await response.json();
    if (!Array.isArray(catalog.assets) || catalog.assets.length !== 92) throw new Error('Unexpected collection');
    for (const asset of catalog.assets) { if (!/^zoid__[a-z0-9_]+$/.test(asset.id)) throw new Error('Unexpected ID'); path(asset.model.path); for (const texture of asset.textures) path(texture.path); }
    assets = catalog.assets; renderGrid();
  } catch (error) { $('collection-error').hidden = false; $('result-count').textContent = 'Collection unavailable'; }
}
function fillDetails(asset) {
  $('model-title').textContent = `${sourceId(asset)}${isLow(asset) ? ' / Low detail' : ''}`;
  $('variant-badge').textContent = isLow(asset) ? 'LOW DETAIL VARIANT' : 'STANDARD VARIANT'; $('variant-badge').className = `badge${isLow(asset) ? ' low' : ''}`;
  const facts = [['Source ID', sourceId(asset)], ['File format', 'GLB 2.0'], ['File size', bytes(asset.model.bytes)], ['Triangles', numbers.format(asset.validation.triangles)], ['Meshes', asset.validation.meshes], ['Textures', asset.textures.length]];
  $('model-facts').replaceChildren(...facts.map(([label, value]) => { const row = element('div'); row.append(element('dt', '', label), element('dd', '', value)); return row; }));
  $('download-model').href = path(asset.model.path); $('download-model').download = asset.model.path.split('/').at(-1);
  $('textures-title').textContent = `Textures / ${asset.textures.length}`;
  $('texture-list').replaceChildren(...asset.textures.map((texture, i) => {
    const link = element('a', 'texture-item'); link.href = path(texture.path); link.download = `${asset.id}-${texture.path.split('/').at(-1)}`; link.setAttribute('aria-label', `Download ${sourceId(asset)} texture ${i + 1} PNG`);
    const img = element('img'); img.src = path(texture.path); img.alt = ''; img.loading = 'lazy';
    const label = element('span', '', `Texture ${String(i + 1).padStart(2, '0')}`); label.append(element('small', '', `${texture.width} × ${texture.height} · PNG · ${bytes(texture.bytes)}`));
    link.append(img, label, element('b', '', '↓')); return link;
  }));
  $('animation-controls').hidden = true; $('clip').replaceChildren();
}
async function openModel(asset, source) {
  const token = ++loadToken; selected = asset; opener = source || opener;
  viewer?.dispose(); viewer = undefined;
  fillDetails(asset); $('retry-model').hidden = true;
  $('viewer-status').hidden = false; $('viewer-status').className = 'viewer-status'; $('viewer-status').textContent = `Loading ${sourceId(asset)}…`;
  if (!dialog.open) { dialog.showModal(); document.body.style.overflow = 'hidden'; $('close-viewer').focus(); }
  try {
    const { ModelViewer } = await import('./viewer.js');
    if (token !== loadToken || !dialog.open) return;
    const current = new ModelViewer($('viewport'), {
      onContextLost: () => { if (token === loadToken && dialog.open) showViewerError('The 3D graphics context was lost. Retry the model or use the GLB download.'); },
      onFinished: () => { $('playback-status').textContent = 'Clip finished. It was played once; choose Stop / reset to restore the initial pose.'; }
    });
    viewer = current;
    const result = await current.load(path(asset.model.path), percent => { if (token === loadToken) $('viewer-status').textContent = `Loading ${sourceId(asset)}… ${percent}%`; });
    if (token !== loadToken || !dialog.open) return;
    $('viewer-status').hidden = true;
    $('viewport').setAttribute('aria-label', `${sourceId(asset)} loaded. Drag to orbit, scroll or pinch to zoom. Arrow keys orbit, plus and minus zoom, R resets.`);
    if (result.clips.length) {
      $('animation-controls').hidden = false;
      $('animation-note').textContent = sourceId(asset) === 'A01' ? 'Accessory/reference clips only. These are not authenticated body animations.' : 'Measured idle/walk clips. Seamless looping and gameplay correctness are not guaranteed.';
      $('clip').replaceChildren(...result.clips.map((clip, i) => { const option = element('option', '', `${clip.name} · ${clip.duration.toFixed(2)}s`); option.value = String(i); return option; }));
      $('playback-status').textContent = 'Playback is opt-in; clips do not auto-loop.';
    }
  } catch (error) { if (token === loadToken && dialog.open && error.name !== 'AbortError') { viewer?.dispose(); viewer = undefined; showViewerError('The 3D preview could not load. WebGL may be unavailable, or the download failed. You can still download the original GLB.'); } }
}
function showViewerError(message) { $('viewer-status').hidden = false; $('viewer-status').className = 'viewer-status error'; $('viewer-status').textContent = message; $('retry-model').hidden = false; }
function closeModel() { ++loadToken; viewer?.dispose(); viewer = undefined; document.body.style.overflow = ''; opener?.focus(); }
$('close-viewer').addEventListener('click', () => dialog.close()); dialog.addEventListener('close', closeModel);
dialog.addEventListener('click', event => { if (event.target === dialog) { const rect = dialog.getBoundingClientRect(); if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close(); } });
$('orbit-left').addEventListener('click', () => viewer?.orbit(.25)); $('orbit-right').addEventListener('click', () => viewer?.orbit(-.25));
$('zoom-in').addEventListener('click', () => viewer?.zoom(.85)); $('zoom-out').addEventListener('click', () => viewer?.zoom(1.18)); $('reset-view').addEventListener('click', () => viewer?.home());
$('viewport').addEventListener('keydown', event => { const commands = { ArrowLeft: () => viewer?.orbit(.15), ArrowRight: () => viewer?.orbit(-.15), ArrowUp: () => viewer?.orbit(0, -.12), ArrowDown: () => viewer?.orbit(0, .12), '+': () => viewer?.zoom(.85), '=': () => viewer?.zoom(.85), '-': () => viewer?.zoom(1.18), r: () => viewer?.home(), R: () => viewer?.home() }; if (commands[event.key]) { event.preventDefault(); commands[event.key](); } });
$('retry-model').addEventListener('click', () => { if (selected) openModel(selected); });
$('play-clip').addEventListener('click', () => { viewer?.play(Number($('clip').value)); $('playback-status').textContent = 'Playing once · experimental preview'; });
$('stop-clip').addEventListener('click', () => { viewer?.stop(); $('playback-status').textContent = 'Stopped. Initial pose restored.'; });
$('clip').addEventListener('change', () => { viewer?.stop(); $('playback-status').textContent = 'Clip selected. Press Play once to preview.'; });
$('search').addEventListener('input', renderGrid); $('sort').addEventListener('change', renderGrid);
for (const button of document.querySelectorAll('[data-filter]')) button.addEventListener('click', () => { filter = button.dataset.filter; for (const other of document.querySelectorAll('[data-filter]')) other.setAttribute('aria-pressed', String(other === button)); renderGrid(); });
$('clear-filters').addEventListener('click', () => { $('search').value = ''; filter = 'all'; for (const button of document.querySelectorAll('[data-filter]')) button.setAttribute('aria-pressed', String(button.dataset.filter === 'all')); renderGrid(); $('search').focus(); });
$('retry-catalog').addEventListener('click', loadCatalog);
$('hero-inspect').addEventListener('click', () => { const asset = assets.find(a => a.id === 'zoid__a07'); if (asset) openModel(asset, $('hero-inspect')); });
document.addEventListener('keydown', event => { if (event.key === '/' && !dialog.open && !['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) { event.preventDefault(); $('search').focus(); } });
loadCatalog();
