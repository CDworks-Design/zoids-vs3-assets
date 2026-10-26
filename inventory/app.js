'use strict';
const $ = id => document.getElementById(id);
const numbers = new Intl.NumberFormat('en-US');
const PAGE_SIZE = 50;
const INVENTORY_VERSION = '20261025-inventory4';
const state = { mode: 'models', page: 1, sections: [], datasets: {}, request: 0, ready: false, modelScope: '' };
const files = { models: 'assets', sources: 'sources' };
const inventoryURL = filename => `${filename}?v=${INVENTORY_VERSION}`;
const element = (tag, text, className) => {
  const item = document.createElement(tag);
  if (text !== undefined) item.textContent = text;
  if (className) item.className = className;
  return item;
};
const formatBytes = value => Number.isFinite(value) ? `${numbers.format(value)} B` : 'Not recorded';
const safePublishedPath = value => typeof value === 'string' && /^models\/zoid__[a-z0-9_]+\/zoid__[a-z0-9_]+\.glb$/.test(value) ? `../${value}` : null;
const modelCount = section => section.model_records ?? section.historical_models ?? 0;
const normalizeSearch = value => String(value).normalize('NFKC').toLowerCase();
const conversionLabel = value => ({ 'historical-converted': 'Historical conversion', 'preserved-primary-export': 'Preserved primary export' }[value] || value);

function mapLabels(info = {}) {
  const pairs = [];
  for (const [version, values] of Object.entries(info?.labels_by_version || {})) {
    if (Array.isArray(values) && values.length) pairs.push([version, values.join(' / ')]);
  }
  if (info?.entry_zero_label) pairs.push([info.version_kind || 'retained', info.entry_zero_label]);
  return pairs;
}

function appendLabels(container, record) {
  const label = record.identification?.retained_ui_display_label;
  if (label) {
    const group = element('div', undefined, 'retained-label');
    group.append(element('small', 'Retained weapon UI label'), element('span', label));
    container.append(group);
  }
  const labels = mapLabels(record.map_info);
  if (labels.length) {
    const group = element('div', undefined, 'retained-label');
    group.append(element('small', `Stage-info ${record.map_info.stage_info_id} · retained UI labels`));
    for (const [version, value] of labels) {
      const line = element('span', value);
      line.append(element('small', version, 'label-version'));
      group.append(line);
    }
    if (record.map_info.multiple_labels_within_version) group.append(element('span', 'Multiple labels in one version', 'badge warning'));
    container.append(group);
  }
}

function identificationEvidence(record) {
  const identification = record.identification || {};
  const map = record.map_info || {};
  return [
    ['Resource code', identification.resource_code],
    ['Part IDs', Array.isArray(identification.part_ids) ? identification.part_ids.join(', ') : undefined],
    ['Retained weapon UI label', identification.retained_ui_display_label],
    ['Weapon label status', identification.status],
    ['Identification confidence', identification.confidence],
    ['Weapon label source byte offset', identification.label_absolute_offset],
    ['Weapon label source byte length', identification.label_source_byte_length],
    ['Weapon label whitespace normalized', typeof identification.label_whitespace_normalized === 'boolean' ? (identification.label_whitespace_normalized ? 'Yes · catalog display trims source whitespace' : 'No') : undefined],
    ['Stage-info ID', map.stage_info_id],
    ['Stage-info source', map.stage_info_source_path],
    ...mapLabels(map).map(([version, label]) => [`Map label · ${version}`, label]),
    ['Map label status', map.status],
    ['Map label confidence', map.confidence],
    ['Map label meaning', map.meaning],
    ['Map association', map.association],
    ['Map label source byte length', map.label_source_byte_length],
    ['Map label whitespace normalized', typeof map.label_whitespace_normalized === 'boolean' ? (map.label_whitespace_normalized ? 'Yes · catalog display trims source whitespace' : 'No') : undefined],
    ['Multiple labels within one version', typeof map.multiple_labels_within_version === 'boolean' ? (map.multiple_labels_within_version ? 'Yes · no single name selected' : 'No') : undefined]
  ];
}

function searchableRecord(record) {
  return normalizeSearch([
    record.id, record.label, record.path, record.source_path, record.category, record.category_title,
    record.conversion_status, record.historical_conversion_status,
    record.identification?.resource_code, record.identification?.retained_ui_display_label,
    record.identification?.part_ids?.join(' '),
    record.map_info?.stage_info_id, ...mapLabels(record.map_info).flat()
  ].filter(value => value !== undefined && value !== null).join(' '));
}

async function readJSON(filename) {
  const response = await fetch(inventoryURL(filename), { cache: 'no-store' });
  if (!response.ok) throw new Error('Inventory unavailable');
  return response.json();
}

function detailsFor(pairs) {
  const details = element('details');
  details.append(element('summary', 'View evidence'));
  const list = element('dl');
  for (const [label, value] of pairs) {
    if (value === undefined || value === null || value === '') continue;
    list.append(element('dt', label), element('dd', String(value)));
  }
  details.append(list);
  return details;
}

function modelRow(record) {
  const row = element('tr');
  const name = element('td');
  name.append(element('strong', record.label || record.id), element('code', record.id), element('code', record.source_path, 'source-path'));
  if (record.conversion_status) name.append(element('small', conversionLabel(record.conversion_status)));
  appendLabels(name, record);
  const category = element('td', record.category_title || record.category);
  const size = element('td', formatBytes(record.export_bytes));
  const status = element('td');
  const publishedPath = safePublishedPath(record.published_model);
  if (publishedPath) {
    status.append(element('span', 'Published model', 'badge published'));
    const download = element('a', record.published_export_matches_record === false ? 'Published source variant GLB ↓' : 'Published GLB ↓', 'download-model');
    download.href = publishedPath;
    download.download = record.published_model.split('/').at(-1);
    download.setAttribute('aria-label', `Download published ${record.id} GLB`);
    status.append(download);
  }
  const availability = {
    'verified-local': ['Verified locally', 'badge'],
    'missing-local': ['Not found locally', 'badge warning'],
    'hash-mismatch': ['Local hash differs', 'badge warning']
  }[record.availability] || ['Availability unverified', 'badge warning'];
  status.append(element('span', availability[0], availability[1]));
  if (typeof record.catalog_snapshot?.included === 'boolean') status.append(element('small', record.catalog_snapshot.included ? 'Included in source snapshot' : 'Not included in source snapshot'));
  if (!publishedPath) status.append(element('small', 'No public download in this inventory.'));
  const evidence = element('td');
  const validation = record.validation || {};
  evidence.append(detailsFor([
    ['Conversion status', conversionLabel(record.conversion_status)],
    ['Source SHA-256', record.source_sha256],
    ['Source bytes', formatBytes(record.source_bytes)],
    ['Recorded export SHA-256', record.export_sha256],
    ['Published GLB matches this export', typeof record.published_export_matches_record === 'boolean' ? (record.published_export_matches_record ? 'Yes' : 'No · published link is a different export of this source') : undefined],
    ['Local verification source', record.validation_source === 'published-model' ? 'Published model bytes' : record.validation_source === 'extractor-export' ? 'Extractor export bytes' : record.validation_source],
    ['Header / JSON check', validation.glb2_header_json_valid === true ? 'Passed' : validation.glb2_header_json_valid === false ? 'Failed' : 'Not recorded'],
    ['Animation status', record.animation_status],
    ['Source catalog snapshot date', record.catalog_snapshot?.as_of],
    ['Included in source catalog snapshot', typeof record.catalog_snapshot?.included === 'boolean' ? (record.catalog_snapshot.included ? 'Yes' : 'No') : undefined],
    ['Source catalog package recorded', typeof record.catalog_snapshot?.package_recorded === 'boolean' ? (record.catalog_snapshot.package_recorded ? 'Yes' : 'No') : undefined],
    ...identificationEvidence(record),
    ['Remaining work', record.remaining_work]
  ]));
  row.append(name, category, size, status, evidence);
  return row;
}

function sourceRow(record) {
  const row = element('tr');
  const name = element('td'); name.append(element('code', record.path));
  appendLabels(name, record);
  const provenance = record.provenance === 'image-identical' ? 'Image-identical' : record.provenance === 'local-generated' ? 'Local generated' : 'Unresolved';
  const status = element('td'); status.append(element('span', provenance, `badge${record.provenance === 'image-identical' ? '' : ' warning'}`));
  const evidence = element('td'); evidence.append(detailsFor([
    ['SHA-256', record.sha256],
    ['Source path', record.path],
    ['Files with the same content', record.same_content_files],
    ['Historical conversion status', record.historical_conversion_status],
    ...identificationEvidence(record)
  ]));
  row.append(name, element('td', record.category_title || record.category), element('td', formatBytes(record.bytes)), status, evidence);
  return row;
}

function updateCategoryOptions() {
  const selected = $('category').value;
  const all = element('option', 'All categories'); all.value = 'all';
  const options = state.sections.map(section => {
    const count = state.mode === 'models' ? modelCount(section) : section.source_files;
    const option = element('option', `${section.title} (${numbers.format(count || 0)})`);
    option.value = section.id;
    return option;
  });
  $('category').replaceChildren(all, ...options);
  $('category').value = options.some(option => option.value === selected) ? selected : 'all';
}

function render() {
  const dataset = state.datasets[state.mode];
  if (!dataset) return;
  const query = normalizeSearch($('search').value.trim());
  const category = $('category').value;
  const filtered = dataset.filter(item => (category === 'all' || item.record.category === category) && item.search.includes(query));
  const pages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  state.page = Math.min(Math.max(1, state.page), pages);
  const offset = (state.page - 1) * PAGE_SIZE;
  const end = Math.min(offset + PAGE_SIZE, filtered.length);
  const headings = state.mode === 'models' ? ['Model / source file', 'Category', 'Recorded export size', 'Availability', 'Evidence'] : ['Source file / retained labels', 'Category', 'File size', 'Provenance', 'Evidence'];
  const headingRow = element('tr');
  for (const heading of headings) { const cell = element('th', heading); cell.scope = 'col'; headingRow.append(cell); }
  $('table-head').replaceChildren(headingRow);
  const fragment = document.createDocumentFragment();
  for (const { record } of filtered.slice(offset, end)) fragment.append(state.mode === 'models' ? modelRow(record) : sourceRow(record));
  $('records').replaceChildren(fragment);
  $('table-caption').textContent = state.mode === 'models' ? 'Model export records' : 'Extractor source files';
  const kind = state.mode === 'models' ? 'model records' : 'source files';
  $('result-count').textContent = `${numbers.format(filtered.length)} of ${numbers.format(dataset.length)} ${kind}${filtered.length ? ` · Showing ${numbers.format(offset + 1)}–${numbers.format(end)}` : ''}`;
  $('empty').hidden = filtered.length > 0;
  $('table-wrap').hidden = filtered.length === 0;
  $('page-count').textContent = `Page ${numbers.format(state.page)} of ${numbers.format(pages)}`;
  $('previous').disabled = state.page <= 1 || !filtered.length;
  $('next').disabled = state.page >= pages || !filtered.length;
}

async function loadMode() {
  const request = ++state.request;
  const mode = state.mode;
  $('load-error').hidden = true;
  $('empty').hidden = true;
  $('table-wrap').hidden = false;
  $('table-wrap').setAttribute('aria-busy', 'true');
  $('records').replaceChildren();
  $('result-count').textContent = `Loading ${mode === 'models' ? 'model records' : 'source files'}…`;
  $('previous').disabled = true;
  $('next').disabled = true;
  for (const button of document.querySelectorAll('[data-mode]')) button.setAttribute('aria-pressed', String(button.dataset.mode === mode));
  $('mode-note').textContent = mode === 'models'
    ? `${state.modelScope} Local verification, source-snapshot inclusion and public downloads are shown separately.`
    : 'Every inventoried extractor file, including supporting data and local generated files. Search retained map labels here; labels stay attached to the exact records supported by the evidence.';
  $('csv-download').href = inventoryURL(`${files[mode]}.csv`);
  $('json-download').href = inventoryURL(`${files[mode]}.json`);
  updateCategoryOptions();
  try {
    if (!state.datasets[mode]) {
      const data = await readJSON(`${files[mode]}.json`);
      if (!Array.isArray(data.records)) throw new Error('Invalid inventory');
      state.datasets[mode] = data.records.map(record => ({ record, search: searchableRecord(record) }));
    }
    if (request !== state.request) return;
    render();
  } catch (error) {
    if (request !== state.request) return;
    $('load-error').hidden = false;
    $('table-wrap').hidden = true;
    $('result-count').textContent = 'Inventory unavailable.';
  } finally {
    if (request === state.request) $('table-wrap').setAttribute('aria-busy', 'false');
  }
}

function clearFilters() {
  $('search').value = '';
  $('category').value = 'all';
  state.page = 1;
  render();
  $('search').focus();
}

async function start() {
  $('load-error').hidden = true;
  try {
    const data = await readJSON('sections.json');
    if (!Array.isArray(data.sections)) throw new Error('Invalid categories');
    state.sections = [...data.sections].sort((a, b) => a.title.localeCompare(b.title));
    $('snapshot').textContent = `Inventory snapshot: ${data.snapshot_date}`;
    const sum = key => state.sections.reduce((total, section) => total + (Number(section[key]) || 0), 0);
    const totalModels = state.sections.reduce((total, section) => total + modelCount(section), 0);
    state.modelScope = `${numbers.format(totalModels)} model records: ${numbers.format(sum('historical_models'))} historical conversions and ${numbers.format(sum('preserved_models'))} preserved primary exports.`;
    const metrics = [[sum('source_files'), 'extractor files'], [totalModels, 'model export records'], [state.sections.length, 'resource families'], [sum('verified_local_models'), 'model exports verified locally']];
    $('metrics').replaceChildren(...metrics.map(([value, label]) => { const item = element('div', undefined, 'metric'); item.append(element('strong', numbers.format(value)), element('span', label)); return item; }));
    $('families').replaceChildren(...state.sections.map(section => {
      const button = element('button', undefined, 'family'); button.type = 'button';
      button.append(element('strong', section.title), element('span', `${numbers.format(section.source_files)} ${section.source_files === 1 ? 'file' : 'files'} · ${numbers.format(modelCount(section))} model records`));
      button.addEventListener('click', () => {
        state.mode = 'sources'; state.page = 1;
        $('search').value = '';
        updateCategoryOptions(); $('category').value = section.id;
        loadMode(); $('browse-title').focus(); $('browse').scrollIntoView({ block: 'start' });
      });
      return button;
    }));
    state.ready = true;
    for (const control of [...document.querySelectorAll('[data-mode]'), $('search'), $('category'), $('clear')]) control.disabled = false;
    await loadMode();
  } catch (error) {
    $('snapshot').textContent = 'The inventory snapshot could not be loaded.';
    $('load-error').hidden = false;
    $('table-wrap').hidden = true;
    $('result-count').textContent = 'Inventory unavailable.';
  }
}

for (const button of document.querySelectorAll('[data-mode]')) button.addEventListener('click', () => { state.mode = button.dataset.mode; state.page = 1; loadMode(); });
for (const id of ['search', 'category']) $(id).addEventListener(id === 'search' ? 'input' : 'change', () => { state.page = 1; render(); });
for (const id of ['clear', 'empty-clear']) $(id).addEventListener('click', clearFilters);
for (const [id, direction] of [['previous', -1], ['next', 1]]) $(id).addEventListener('click', () => { state.page += direction; render(); $('browse-title').focus(); $('browse').scrollIntoView({ block: 'start' }); });
$('retry').addEventListener('click', () => state.ready ? loadMode() : start());
start();
