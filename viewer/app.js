'use strict';
let kind = 'dictionary';
let entries = [];
let generation = 0;
const byId = id => document.getElementById(id);
const labels = {dictionary: '字典', components: '部件', glyphs: '字形'};
function text(tag, value, className) {
  const node = document.createElement(tag);
  node.textContent = value;
  if (className) node.className = className;
  return node;
}
function showDetail(entry, selected) {
  document.querySelectorAll('.record').forEach(button => button.classList.toggle('selected', button === selected));
  const panel = byId('detail');
  panel.replaceChildren(text('p', labels[kind] + '档案', 'eyebrow'), text('h2', entry.name || entry.original));
  const image = document.createElement('img');
  image.src = '/asset?' + new URLSearchParams({kind, id: entry.id});
  image.alt = (entry.name || entry.original) + '的矢量轮廓';
  image.className = 'outline';
  image.addEventListener('error', () => image.replaceWith(text('p', '轮廓无法显示，请检查 SVG 文件。', 'error')));
  panel.append(image);
  const definitions = document.createElement('dl');
  const fields = kind === 'components' ? [['name', '名称'], ['source', '来源']] : kind === 'dictionary' ? [['original', '原字'], ['method', '造字法'], ['idea', '造字思路']] : [['original', '原字']];
  for (const [key, label] of fields) definitions.append(text('dt', label), text('dd', entry[key]));
  definitions.append(text('dt', '编号'), text('dd', entry.id));
  panel.append(definitions);
}
async function search() {
  const current = ++generation;
  byId('status').textContent = '正在读取目录…';
  try {
    const response = await fetch('/api/catalog?' + new URLSearchParams({kind, q: byId('query').value, method: kind === 'dictionary' ? byId('method').value : ''}));
    const data = await response.json();
    if (current !== generation) return;
    if (!response.ok) throw new Error(data.error || '目录读取失败');
    entries = data.entries;
    for (const [name, count] of Object.entries(data.counts)) byId('count-' + name).textContent = count;
    if (byId('method').options.length === 1) {
      for (const method of data.methods) {const option = text('option', method.name); option.value = method.name; byId('method').append(option);}
    }
    byId('results').replaceChildren();
    byId('detail').replaceChildren(text('div', '选择一条记录，查看轮廓与设计信息。', 'detail-placeholder'));
    for (const entry of entries) {
      const button = document.createElement('button');
      button.className = 'record';
      const thumbnail = document.createElement('img');
      thumbnail.src = '/asset?' + new URLSearchParams({kind, id: entry.id});
      thumbnail.alt = '';
      button.append(thumbnail, text('strong', entry.name || entry.original), text('span', entry.method || entry.source || entry.id));
      button.addEventListener('click', () => showDetail(entry, button));
      byId('results').append(button);
    }
    byId('empty').hidden = entries.length !== 0;
    const isEmpty = data.counts[kind] === 0;
    byId('empty-title').textContent = isEmpty ? labels[kind] + '尚未收录' : '没有找到匹配记录';
    byId('empty-description').textContent = isEmpty ? '框架已就绪。内容入库后，会在这里展示。' : '试试其他关键词，或清空筛选条件。';
    byId('status').textContent = '找到 ' + entries.length + ' 条记录';
  } catch (error) {
    if (current !== generation) return;
    byId('results').replaceChildren();
    byId('empty').hidden = true;
    byId('detail').replaceChildren();
    byId('status').textContent = '读取失败：' + error.message;
  }
}
document.querySelectorAll('.tab').forEach(button => button.addEventListener('click', () => {
  kind = button.dataset.kind;
  document.querySelectorAll('.tab').forEach(tab => {tab.classList.toggle('active', tab === button); tab.setAttribute('aria-pressed', String(tab === button));});
  byId('query').value = '';
  byId('method').value = '';
  byId('method').hidden = kind !== 'dictionary';
  byId('query').placeholder = kind === 'components' ? '搜索部件名称或来源' : kind === 'glyphs' ? '搜索原字或字形编号' : '搜索原字、造字法或造字思路';
  search();
}));
byId('search-form').addEventListener('submit', event => {event.preventDefault(); search();});
byId('method').addEventListener('change', search);
byId('refresh').addEventListener('click', search);
search();
