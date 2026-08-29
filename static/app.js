// 明礼 MingLi · 前端逻辑
const HINTS = [
  { q: '知行合一，此心光明，亦复何言。', a: '王阳明' },
  { q: '粉骨碎身浑不怕，要留清白在人间。', a: '于谦' },
  { q: '封侯非我意，但愿海波平。', a: '戚继光' },
  { q: '情不知所起，一往而深。', a: '汤显祖' },
  { q: '大丈夫当朝碧海而暮苍梧。', a: '徐霞客' },
  { q: '铁肩担道义，辣手著文章。', a: '杨继盛' },
  { q: '愿以深心奉尘刹，不予自身求利益。', a: '张居正' },
  { q: '天覆地载，物号数万。', a: '宋应星' },
];

const TYPE_TO_SUBJECT_TYPE = {
  couplet: 'couplet',
  poem: 'historical_event',
  elegiac_prose: 'couplet',
  meme: 'meme',
};

let currentRating = 0;
let currentHistoryId = null;

// ============ 友好错误提示 ============
function _escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

/**
 * 渲染"API Key 未配置"引导卡片。
 * @param {string} message - 后端返回的详细说明（含 emoji 和换行）
 */
function _showApiKeyMissingGuide(message) {
  const body = document.getElementById('resultBody');
  if (!body) return;
  // 把后端多行字符串转成 <ol>/<ul> 友好格式
  const html = `
    <div class="api-key-guide">
      <div class="api-key-guide-header">
        <span class="api-key-guide-icon">🔑</span>
        <h3>首次使用：需要配置 API Key</h3>
      </div>
      <pre class="api-key-guide-detail">${_escapeHtml(message)}</pre>
      <div class="api-key-guide-steps">
        <p><strong>📝 三步完成配置：</strong></p>
        <ol>
          <li>用记事本打开 <code>.env</code> 文件（位于 MingLi.exe 同级目录）</li>
          <li>找到 <code>DEEPSEEK_API_KEY=</code> 这一行，把后面替换成你的密钥</li>
          <li>保存后<strong>重新双击 MingLi.exe</strong>启动即可</li>
        </ol>
        <p class="muted">💡 密钥申请地址（任选一家）：
          <a href="https://platform.deepseek.com/" target="_blank">DeepSeek（推荐·便宜）</a> ·
          <a href="https://bailian.console.aliyun.com/" target="_blank">通义千问</a> ·
          <a href="https://platform.minimaxi.com/user-center/payment/token-plan" target="_blank">MiniMax</a>
        </p>
        <p style="text-align:center;margin-top:1rem">
          <a href="/settings" class="btn-primary" style="display:inline-block;padding:0.6rem 1.5rem;border-radius:4px;text-decoration:none;color:#fff;background:#8b2a1f">⚙️ 打开 API 配置中心</a>
        </p>
      </div>
    </div>
  `;
  body.innerHTML = html;
  document.getElementById('result').hidden = false;
}

/**
 * 统一处理 generate 路由的错误响应
 */
async function _handleGenerateError(resp, fallbackPrefix = '生成失败') {
  let detail = '';
  let apiKeyMissing = false;
  try {
    const data = await resp.json();
    detail = typeof data.detail === 'string'
      ? data.detail
      : (data.detail?.message || JSON.stringify(data.detail));
    if (data.detail?.error === 'api_key_missing' || /API Key 未配置/i.test(detail)) {
      apiKeyMissing = true;
    }
  } catch {
    try { detail = await resp.text(); } catch {}
  }
  if (apiKeyMissing) {
    _showApiKeyMissingGuide(detail);
  } else {
    document.getElementById('resultBody').textContent = `${fallbackPrefix}：${detail || resp.statusText}`;
  }
}

// ============ DOM 初始化 ============
document.addEventListener('DOMContentLoaded', () => {
  // Tab 切换
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => switchTab(tab.dataset.tab));
  });

  // 顶部历史按钮
  document.getElementById('historyToggle').addEventListener('click', () => switchTab('history'));

  // 表单提交
  ['couplet', 'poem', 'elegiac_prose', 'meme'].forEach(t => {
    const form = document.getElementById('form-' + t);
    if (form) form.addEventListener('submit', e => {
      e.preventDefault();
      submitForm(t, form);
    });
  });

  // 结果关闭
  document.getElementById('closeResult').addEventListener('click', () => {
    document.getElementById('result').hidden = true;
    currentHistoryId = null;
  });

  // 评分
  document.querySelectorAll('#stars button').forEach(btn => {
    btn.addEventListener('click', () => {
      currentRating = +btn.dataset.v;
      document.querySelectorAll('#stars button').forEach((b, i) => {
        b.classList.toggle('filled', i < currentRating);
        b.textContent = i < currentRating ? '★' : '☆';
      });
      submitFeedback(currentRating);
    });
  });

  // 打印
  document.getElementById('printBtn').addEventListener('click', () => window.print());

  // 右下角提示轮换
  rotateHint();
  setInterval(rotateHint, 6000);

  // 默认填充挽联下拉
  loadSubjects('couplet');

  // 绑定知识图谱切换按钮
  bindKgToggles();
});

// ============ Tab 切换 ============
function switchTab(name) {
  document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.dataset.tab === name));
  document.querySelectorAll('.panel').forEach(p => p.classList.toggle('active', p.id === 'panel-' + name));
  if (name === 'history') loadHistory();
  else if (['couplet','poem','elegiac_prose','meme'].includes(name)) {
    loadSubjects(TYPE_TO_SUBJECT_TYPE[name] || name);
  }
}

// ============ 加载主题列表 ============
// 每个面板/按钮跟踪当前 entity_type，方便"知识图谱"切换
const _panelSubjectState = new WeakMap();

async function loadSubjects(type, scope = null) {
  try {
    // scope 是可选的 Element 上下文（表示限定到某面板的 select）
    let url = `/api/subjects?type=${encodeURIComponent(type)}`;
    const stateKey = scope || document;
    const cur = _panelSubjectState.get(stateKey) || {};
    if (cur.entityType) url += `&entity_type=${encodeURIComponent(cur.entityType)}`;
    const r = await fetch(url);
    const data = await r.json();
    const subjects = data.subjects || [];

    const targets = scope
      ? [scope.querySelector('select[name="subject"]')].filter(Boolean)
      : document.querySelectorAll('.gen-form select[name="subject"]');
    targets.forEach(sel => {
      const prev = sel.value;
      sel.innerHTML = '';
      subjects.forEach(s => {
        const opt = document.createElement('option');
        opt.value = s;
        opt.textContent = s;
        sel.appendChild(opt);
      });
      if (prev && subjects.includes(prev)) sel.value = prev;
    });

    // 记录当前状态
    _panelSubjectState.set(stateKey, { entityType: cur.entityType || '' });

    // 控制台提示 KG 统计
    if (data.kg_loaded && data.kg_stats) {
      const k = data.kg_stats;
      console.log(`[KG] 已加载：${k.entities} 实体 / ${k.relationships} 关系 / ${k.relation_types} 关系类型`);
    }
  } catch (e) {
    console.error('loadSubjects failed:', e);
  }
}

// 绑定"📚 知识图谱"切换按钮
function bindKgToggles() {
  document.querySelectorAll('.kg-toggle').forEach(btn => {
    btn.addEventListener('click', async () => {
      const entity = btn.dataset.entity;
      // 找到最近的 .gen-form 容器，作为 scope
      const form = btn.closest('.gen-form');
      if (!form) return;
      // 找到当前面板 type（通过最近 panel id 映射）
      const panel = btn.closest('.panel');
      let type = 'couplet';
      if (panel && panel.id) {
        type = TYPE_TO_SUBJECT_TYPE[panel.id.replace('panel-', '')] || panel.id.replace('panel-', '');
      }
      // 切换状态
      const cur = _panelSubjectState.get(form) || {};
      const next = (cur.entityType === entity) ? '' : entity;
      _panelSubjectState.set(form, { entityType: next });
      btn.classList.toggle('active', !!next);
      btn.textContent = next ? `📚 ${entity} (已启用)` : '📚 知识图谱';
      await loadSubjects(type, form);
    });
  });
}

// ============ 表单提交（流式） ============
async function submitForm(type, form) {
  const btn = form.querySelector('button[type="submit"]');
  btn.disabled = true;
  const oldText = btn.textContent;
  btn.textContent = '生成中...';

  const fd = new FormData(form);
  const payload = { content_type: type };
  fd.forEach((v, k) => { payload[k] = v; });

  // 清空旧结果
  const resultEl = document.getElementById('result');
  resultEl.hidden = false;
  document.getElementById('resultTitle').textContent = '生成中...';
  document.getElementById('resultBody').textContent = '';
  document.getElementById('resultHorizontal').hidden = true;
  document.getElementById('resultTags').innerHTML = '';
  document.getElementById('resultSources').textContent = '';
  currentRating = 0;
  document.querySelectorAll('#stars button').forEach(b => { b.classList.remove('filled'); b.textContent = '☆'; });

  try {
    const resp = await fetch('/api/generate/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!resp.ok) {
      await _handleGenerateError(resp, '生成失败'); return;
    }
    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let meta = null;
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop();
      for (const line of lines) {
        if (!line.startsWith('data:')) continue;
        const raw = line.slice(5).trim();
        if (!raw) continue;
        try {
          const ev = JSON.parse(raw);
          if (ev.error) {
            const msg = ev.error.message || ev.error;
            if (typeof msg === 'string' && /API Key 未配置/i.test(msg)) {
              _showApiKeyMissingGuide(msg);
            } else {
              document.getElementById('resultBody').textContent = '生成失败：' + msg;
            }
            return;
          }
          if (ev.delta) {
            document.getElementById('resultBody').textContent += ev.delta;
          }
          if (ev.done) {
            meta = ev;
            document.getElementById('resultTitle').textContent = ev.title || payload.subject;
            currentHistoryId = ev.id;
            const tags = ev.tags || [];
            document.getElementById('resultTags').innerHTML =
              tags.map(t => `<span class="tag">#${t}</span>`).join('');
            const sources = ev.sources || [];
            document.getElementById('resultSources').textContent =
              sources.length ? '来源：' + sources.join('、') : '';
            // 尝试从 body 解析横批
            tryRenderHorizontal();
          }
        } catch (e) {
          console.error('parse error', e, raw);
        }
      }
    }
    if (!meta) {
      // 流式未收到 done，降级到非流式
      const r = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const d = await r.json();
      document.getElementById('resultTitle').textContent = d.title;
      document.getElementById('resultBody').textContent = d.body;
      currentHistoryId = d.id;
      document.getElementById('resultTags').innerHTML =
        (d.tags || []).map(t => `<span class="tag">#${t}</span>`).join('');
      document.getElementById('resultSources').textContent =
        (d.sources || []).length ? '来源：' + d.sources.join('、') : '';
      tryRenderHorizontal();
    }
  } catch (e) {
    document.getElementById('resultBody').textContent = '网络错误：' + e.message;
  } finally {
    btn.disabled = false;
    btn.textContent = oldText;
  }
}

function tryRenderHorizontal() {
  const body = document.getElementById('resultBody').textContent;
  const m = body.match(/横批[：:]\s*([^\n]+)/);
  if (m) {
    document.getElementById('resultHorizontal').hidden = false;
    document.getElementById('resultHorizontal').textContent = m[1].trim();
  }
}

// ============ 提交反馈 ============
async function submitFeedback(rating) {
  if (!rating) return;
  try {
    await fetch('/api/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        rating,
        history_id: currentHistoryId,
        content_type: currentContentType(),
        subject: currentSubject(),
      }),
    });
  } catch (e) {
    console.error('feedback failed', e);
  }
}

function currentContentType() {
  const active = document.querySelector('.tab.active');
  return active ? active.dataset.tab : '';
}

function currentSubject() {
  const active = document.querySelector('.panel.active .gen-form select[name="subject"]');
  return active ? active.value : '';
}

// ============ 一键随机生成悼明梗文 ============
async function quickMeme() {
  const btn = document.getElementById('meme-quick-btn');
  if (!btn) return;
  btn.disabled = true;
  const oldText = btn.textContent;
  btn.textContent = '🎲 随机中...';

  const toneEl = document.getElementById('meme-tone');
  const lengthEl = document.getElementById('meme-length');
  const subjectEl = document.querySelector('#form-meme input[name="subject"]');
  const hintEl = document.querySelector('#form-meme input[name="hint"]');
  const payload = {
    subject: (subjectEl && subjectEl.value || '').trim() || null,
    tone: toneEl ? (toneEl.value || null) : null,
    length: lengthEl ? (lengthEl.value || null) : null,
    hint: hintEl ? hintEl.value.trim() : '',
  };

  const resultEl = document.getElementById('result');
  resultEl.hidden = false;
  document.getElementById('resultTitle').textContent = '🎲 抽取中...';
  document.getElementById('resultBody').textContent = '';
  document.getElementById('resultHorizontal').hidden = true;
  document.getElementById('resultTags').innerHTML = '';
  document.getElementById('resultSources').textContent = '';
  currentRating = 0;
  document.querySelectorAll('#stars button').forEach(b => { b.classList.remove('filled'); b.textContent = '☆'; });

  try {
    const r = await fetch('/api/meme/quick', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!r.ok) {
      await _handleGenerateError(r, '生成失败');
      return;
    }
    const data = await r.json();
    const preview = document.getElementById('memePreview');
    if (preview && data.meme) {
      document.getElementById('memePreviewText').textContent = '「' + data.meme.text + '」';
      document.getElementById('memePreviewSource').textContent = data.meme.source;
      document.getElementById('memePreviewCategory').textContent = data.meme.category;
      preview.hidden = false;
    }
    document.getElementById('resultTitle').textContent = '「' + data.meme.text + '」— ' + data.subject;
    document.getElementById('resultBody').textContent = data.result;
    document.getElementById('resultSources').textContent = '风格：' + data.tone + ' · 长度：' + data.length + ' · 出处：' + data.meme.source;
    document.getElementById('resultTags').innerHTML = '<span class="tag">#' + data.tone + '</span><span class="tag">#' + data.length + '</span><span class="tag">#' + data.meme.category + '</span><span class="tag">#' + data.subject + '</span>';
    currentHistoryId = null;
  } catch (e) {
    document.getElementById('resultBody').textContent = '网络错误：' + e.message;
  } finally {
    btn.disabled = false;
    btn.textContent = oldText;
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const quickBtn = document.getElementById('meme-quick-btn');
  if (quickBtn) quickBtn.addEventListener('click', quickMeme);

  // 跨界梗表单
  const crossForm = document.getElementById('form-crossover');
  if (crossForm) crossForm.addEventListener('submit', e => {
    e.preventDefault();
    submitCrossover(crossForm);
  });
});


// ============ 悼明之作·跨界梗 ============
async function submitCrossover(form) {
  const btn = form.querySelector('button[type="submit"]');
  btn.disabled = true;
  const oldText = btn.textContent;
  btn.textContent = '考据中…';

  const fd = new FormData(form);
  const payload = {
    work_name: (fd.get('work_name') || '').trim(),
    work_desc: (fd.get('work_desc') || '').trim(),
    subject:   (fd.get('subject') || '').trim(),
    tone:      fd.get('tone') || '考据',
    length:    fd.get('length') || '中',
    hint:      (fd.get('hint') || '').trim(),
  };

  if (!payload.work_name) {
    document.getElementById('resultBody').textContent = '请填写文化作品名称。';
    document.getElementById('result').hidden = false;
    btn.disabled = false;
    btn.textContent = oldText;
    return;
  }

  try {
    const r = await fetch('/api/meme/crossover', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await r.json();
    if (!r.ok) {
      await _handleGenerateError(r, '生成失败');
      document.getElementById('result').hidden = false;
      return;
    }

    // 解析 LLM JSON 输出（如果是 JSON）；否则整段当 body
    let parsed = null;
    const raw = (data.result || '').trim();
    try {
      const m = raw.match(/\{[\s\S]*\}/);
      if (m) parsed = JSON.parse(m[0]);
    } catch (_) { /* 非 JSON，原样显示 */ }

    const title = parsed?.title || '悼明之作·考据';
    const body  = parsed?.body  || raw || '（生成结果为空）';
    const tags  = Array.isArray(parsed?.tags) ? parsed.tags : [];
    const note  = parsed?.note || '';

    document.getElementById('result').hidden = false;
    document.getElementById('resultTitle').textContent =
      '「' + data.work_name + '」— ' + title;
    document.getElementById('resultBody').innerHTML =
      escapeHtml(body).replace(/\n/g, '<br>') +
      (note ? '<p class="meme-note">【考据思路】' + escapeHtml(note) + '</p>' : '');
    document.getElementById('resultHorizontal').hidden = true;
    document.getElementById('resultSources').textContent =
      '文体：' + data.tone + ' · 长度：' + data.length +
      ' · 关联：' + data.subject +
      ' · 考据对象：' + data.work_name;
    document.getElementById('resultTags').innerHTML =
      tags.map(t => `<span class="tag">#${escapeHtml(t)}</span>`).join('') +
      `<span class="tag">#${escapeHtml(data.tone)}</span>` +
      `<span class="tag">#${escapeHtml(data.length)}</span>` +
      `<span class="tag">#考据:${escapeHtml(data.work_name)}</span>`;
    currentHistoryId = null;
    window.scrollTo({ top: document.getElementById('result').offsetTop - 20, behavior: 'smooth' });
  } catch (e) {
    document.getElementById('resultBody').textContent = '网络错误：' + e.message;
    document.getElementById('result').hidden = false;
  } finally {
    btn.disabled = false;
    btn.textContent = oldText;
  }
}


// ============ 历史记录 ============
async function loadHistory() {
  const list = document.getElementById('historyList');
  list.innerHTML = '<p class="muted">加载中...</p>';
  try {
    const r = await fetch('/api/history?limit=20');
    const data = await r.json();
    const items = data.items || [];
    if (!items.length) {
      list.innerHTML = '<p class="muted">暂无历史记录，开始第一次创作吧。</p>';
      return;
    }
    list.innerHTML = '';
    items.forEach(it => {
      const div = document.createElement('div');
      div.className = 'history-item';
      const title = it.title || it.subject;
      const date = (it.created_at || '').replace('T', ' ');
      div.innerHTML = `
        <h4>${escapeHtml(title)}</h4>
        <div class="meta">${escapeHtml(it.subject)} · ${escapeHtml(it.content_type)} · ${escapeHtml(date)}</div>
        <div class="muted">${escapeHtml((it.body || '').slice(0, 60))}...</div>
      `;
      div.addEventListener('click', () => {
        document.getElementById('result').hidden = false;
        document.getElementById('resultTitle').textContent = it.title || it.subject;
        document.getElementById('resultBody').textContent = it.body || '';
        document.getElementById('resultHorizontal').hidden = true;
        document.getElementById('resultTags').innerHTML =
          (it.tags || []).map(t => `<span class="tag">#${escapeHtml(t)}</span>`).join('');
        document.getElementById('resultSources').textContent =
          (it.sources || []).length ? '来源：' + it.sources.map(escapeHtml).join('、') : '';
        currentHistoryId = it.id;
        window.scrollTo({ top: document.getElementById('result').offsetTop - 20, behavior: 'smooth' });
      });
      list.appendChild(div);
    });
  } catch (e) {
    list.innerHTML = '<p class="muted">加载失败：' + e.message + '</p>';
  }
}

// ============ 右下角提示 ============
function rotateHint() {
  const h = HINTS[Math.floor(Math.random() * HINTS.length)];
  document.getElementById('hintQuote').textContent = h.q;
  document.getElementById('hintAuthor').textContent = '—— ' + h.a;
}

// ============ 工具 ============
function escapeHtml(s) {
  if (s == null) return '';
  return String(s).replace(/[&<>"']/g, c => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
  }[c]));
}
