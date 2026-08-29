/* ============================================================
 * 明礼 MingLi · 设置页面 JS
 * - 加载并展示所有 LLM 提供商
 * - 编辑 API Key / Base URL / Model
 * - 测试连接 + 保存（热更新到运行中的服务）
 * ============================================================ */
(function () {
  'use strict';

  const $ = (id) => document.getElementById(id);
  const ESCAPE_MAP = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
  const escapeHtml = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ESCAPE_MAP[c]);

  let ALL_PROVIDERS = [];
  let CURRENT_CONFIG = null;

  // Toast 提示
  function toast(message, type = 'info', duration = 3500) {
    const el = $('toast');
    el.className = 'toast toast--' + type;
    el.textContent = message;
    el.style.display = 'block';
    clearTimeout(el._timer);
    el._timer = setTimeout(() => { el.style.display = 'none'; }, duration);
  }

  // 加载当前配置
  async function loadConfig() {
    try {
      const r = await fetch('/api/settings');
      if (!r.ok) throw new Error('HTTP ' + r.status);
      CURRENT_CONFIG = await r.json();
      ALL_PROVIDERS = CURRENT_CONFIG.providers;
      renderActiveCard();
      renderProviderList();
    } catch (e) {
      console.error('加载配置失败', e);
      $('providerList').innerHTML =
        '<div class="error-card">❌ 无法连接到后端：' + escapeHtml(e.message) +
        '<br><br>请确认 MingLi.exe 正在运行，端口 8765 可访问。</div>';
      $('statusText').textContent = '后端无响应';
      $('statusDot').className = 'status-dot status-dot--err';
    }
  }

  // 渲染：当前激活卡片
  function renderActiveCard() {
    $('activeProviderName').textContent = CURRENT_CONFIG.active_provider_name;
    $('activeModel').textContent = CURRENT_CONFIG.current_model || '(未配置)';
    $('activeKeyState').textContent = CURRENT_CONFIG.active_api_key_set
      ? '✓ 已配置（脱敏保存）' : '✗ 未配置';
    $('envPath').textContent = CURRENT_CONFIG.env_path;
    $('envPath').title = CURRENT_CONFIG.env_path;

    if (CURRENT_CONFIG.active_api_key_set) {
      $('statusText').textContent = '服务运行中 · 已就绪';
      $('statusDot').className = 'status-dot status-dot--ok';
      $('activeCard').classList.add('active-card--ready');
      $('activeCard').classList.remove('active-card--warn');
    } else {
      $('statusText').textContent = 'API Key 未配置';
      $('statusDot').className = 'status-dot status-dot--warn';
      $('activeCard').classList.add('active-card--warn');
      $('activeCard').classList.remove('active-card--ready');
    }
  }

  // 渲染：提供商列表
  function renderProviderList() {
    const list = $('providerList');
    list.innerHTML = '';
    ALL_PROVIDERS.forEach((p) => {
      const card = document.createElement('div');
      card.className = 'provider-card';
      if (p.id === CURRENT_CONFIG.active_provider) {
        card.classList.add('provider-card--active');
      }
      card.dataset.providerId = p.id;

      const statusBadge = p.api_key_set
        ? '<span class="badge badge--ok">✓ 密钥已设</span>'
        : '<span class="badge badge--warn">密钥未配</span>';
      const activeBadge = p.id === CURRENT_CONFIG.active_provider
        ? '<span class="badge badge--active">★ 当前激活</span>'
        : '';

      card.innerHTML = `
        <div class="provider-card-top">
          <h3 class="provider-card-name">${escapeHtml(p.name)}</h3>
          <div class="provider-card-badges">${activeBadge}${statusBadge}</div>
        </div>
        <div class="provider-card-meta">
          <div class="meta-row"><span class="meta-label">Base URL:</span> <code>${escapeHtml(p.base_url || '(空)')}</code></div>
          <div class="meta-row"><span class="meta-label">模型:</span> <code>${escapeHtml(p.model || '(空)')}</code></div>
          <div class="meta-row"><span class="meta-label">API Key:</span> <code>${escapeHtml(p.api_key_masked || '(空)')}</code></div>
        </div>
        ${p.note ? `<p class="provider-card-note">💡 ${escapeHtml(p.note)}</p>` : ''}
        <div class="provider-card-actions">
          <button class="btn btn-primary btn-sm" data-action="edit">✏️ 编辑</button>
          ${p.id !== CURRENT_CONFIG.active_provider
            ? `<button class="btn btn-secondary btn-sm" data-action="activate">★ 设为默认</button>`
            : ''}
        </div>
      `;

      card.querySelector('[data-action="edit"]').addEventListener('click', () => openEdit(p));
      const activateBtn = card.querySelector('[data-action="activate"]');
      if (activateBtn) {
        activateBtn.addEventListener('click', () => activateProvider(p));
      }
      list.appendChild(card);
    });
  }

  // 打开编辑表单
  function openEdit(p) {
    $('editProviderId').value = p.id;
    $('editProviderName').textContent = p.name;
    $('apiKey').value = '';
    $('apiKey').placeholder = p.api_key_set
      ? `已配置（${p.api_key_masked}），如需修改请输入新值`
      : '请输入 API Key';
    $('apiKeyHint').textContent = p.api_key_set
      ? `✓ 检测到已配置的密钥（脱敏：${p.api_key_masked}），留空表示不修改`
      : '⚠️ 当前未配置密钥，请填入真实 Key';

    $('baseUrl').value = p.base_url || p.default_base_url || '';
    $('baseUrlHint').innerHTML = `默认：<code>${escapeHtml(p.default_base_url || '(无)')}</code>`;

    $('modelName').value = p.model || '';
    $('modelHint').innerHTML = p.models && p.models.length
      ? '候选：' + p.models.map(m => `<code>${escapeHtml(m)}</code>`).join(' / ')
      : '手动输入模型标识符';

    const dl = $('modelSuggestions');
    dl.innerHTML = '';
    (p.models || []).forEach(m => {
      const opt = document.createElement('option');
      opt.value = m;
      dl.appendChild(opt);
    });

    // 文档说明
    const docsEl = $('docsContent');
    let docsHtml = '';
    if (p.docs) {
      docsHtml += `<p>📚 官方文档：<a href="${escapeHtml(p.docs)}" target="_blank">${escapeHtml(p.docs)}</a></p>`;
    }
    if (p.id === 'minimax') {
      docsHtml += '<ol><li>访问 platform.minimaxi.com 注册</li><li>开通 Token Plan 订阅</li><li>控制台 → API Keys 复制 Key</li><li>必须使用国内端点 api.minimaxi.com</li></ol>';
    } else if (p.id === 'deepseek') {
      docsHtml += '<ol><li>访问 platform.deepseek.com 注册</li><li>控制台 → API Keys 创建</li><li>充值（最低 1 元起）</li></ol>';
    } else if (p.id === 'qwen') {
      docsHtml += '<ol><li>阿里云控制台开通 DashScope</li><li>「API-KEY 管理」创建 Key</li><li>在「模型广场」开通所需模型（如 qwen-plus）</li></ol>';
    } else if (p.id === 'doubao') {
      docsHtml += '<ol><li>火山引擎控制台开通豆包</li><li>「在线推理」创建接入点（获取 model id）</li><li>API Key 管理获取 Key</li></ol>';
    } else if (p.id === 'openai') {
      docsHtml += '<p>需海外网络。在 platform.openai.com 创建 Key 并充值。</p>';
    } else if (p.id === 'moonshot') {
      docsHtml += '<ol><li>platform.moonshot.cn 注册</li><li>「API Key 管理」创建</li><li>支持 8k/32k/128k 上下文</li></ol>';
    } else if (p.id === 'zhipu') {
      docsHtml += '<ol><li>open.bigmodel.cn 注册</li><li>「API Keys」获取</li><li>glm-4-flash 免费使用</li></ol>';
    } else if (p.id === 'siliconflow') {
      docsHtml += '<ol><li>cloud.siliconflow.cn 注册</li><li>「API 密钥」创建</li><li>注册送 2000 万 Tokens 免费额度</li></ol>';
    } else if (p.id === 'ollama') {
      docsHtml += '<ol><li>ollama.com 下载安装</li><li>运行 <code>ollama pull qwen2.5:7b</code></li><li>Base URL: <code>http://localhost:11434/v1</code></li><li>API Key 留空（任意非空字符串即可）</li></ol>';
    } else if (p.id === 'custom') {
      docsHtml += '<p>任何 OpenAI 兼容协议的 API，包括：<ul>' +
        '<li><a href="https://github.com/songquanpeng/one-api" target="_blank">OneAPI</a>（聚合中转）</li>' +
        '<li><a href="https://openrouter.ai" target="_blank">OpenRouter</a>（统一网关）</li>' +
        '<li>各类 NewAPI / FastGPT / Dify 等</li></ul></p>' +
        '<p>填写你的服务商提供的 Base URL 和模型名即可。</p>';
    }
    docsEl.innerHTML = docsHtml;
    $('providerDocs').open = false;

    $('testResult').style.display = 'none';
    $('editSection').style.display = 'block';
    $('editSection').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  function closeEdit() {
    $('editSection').style.display = 'none';
  }

  // 测试连接
  async function testConnection() {
    const providerId = $('editProviderId').value;
    const apiKey = $('apiKey').value.trim();
    const baseUrl = $('baseUrl').value.trim();
    const model = $('modelName').value.trim();

    if (!baseUrl) { toast('请先填写 Base URL', 'warn'); return; }
    if (!model) { toast('请先填写模型名', 'warn'); return; }
    const p = CURRENT_CONFIG.providers.find(x => x.id === providerId);
    if (providerId !== 'ollama' && !apiKey && !(p && p.api_key_set)) {
      toast('请先填写 API Key（Ollama 除外）', 'warn');
      return;
    }

    const actualKey = (providerId === 'ollama' && !apiKey) ? 'ollama' : (apiKey || '');

    const btn = $('testBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> 测试中...';

    const resultEl = $('testResult');
    resultEl.style.display = 'block';
    resultEl.className = 'test-result test-result--pending';
    resultEl.innerHTML = '⏳ 正在测试连接...';

    try {
      const r = await fetch('/api/settings/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider_id: providerId,
          api_key: actualKey,
          base_url: baseUrl,
          model: model,
        }),
      });
      const data = await r.json();
      if (data.ok) {
        resultEl.className = 'test-result test-result--ok';
        resultEl.innerHTML = '✓ ' + escapeHtml(data.message) +
          (data.elapsed_ms ? `<br><small>响应 ${data.elapsed_ms} ms${data.model_used ? ' · 模型: ' + escapeHtml(data.model_used) : ''}</small>` : '');
      } else {
        resultEl.className = 'test-result test-result--err';
        resultEl.innerHTML = escapeHtml(data.message).replace(/\n/g, '<br>');
      }
    } catch (e) {
      resultEl.className = 'test-result test-result--err';
      resultEl.textContent = '❌ 请求失败：' + e.message;
    } finally {
      btn.disabled = false;
      btn.innerHTML = '<span class="btn-icon-text">🔌</span> 测试连接';
    }
  }

  // 保存配置
  async function saveConfig(e) {
    e.preventDefault();
    const providerId = $('editProviderId').value;
    const apiKey = $('apiKey').value.trim();
    const baseUrl = $('baseUrl').value.trim();
    const model = $('modelName').value.trim();

    if (!baseUrl) { toast('Base URL 不能为空', 'err'); return; }
    if (!model) { toast('模型名不能为空', 'err'); return; }

    let actualKey = apiKey;
    if (providerId === 'ollama' && !actualKey) {
      actualKey = 'ollama';
    }

    const btn = $('saveBtn');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> 保存中...';

    try {
      const r = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          providers: [{
            provider_id: providerId,
            api_key: actualKey || null,
            base_url: baseUrl,
            model: model,
          }],
        }),
      });
      const data = await r.json();
      if (data.ok) {
        toast('✓ ' + data.message, 'ok', 4000);
        closeEdit();
        await loadConfig();
      } else {
        toast('✗ ' + data.message, 'err', 5000);
      }
    } catch (e) {
      toast('✗ 保存失败：' + e.message, 'err', 5000);
    } finally {
      btn.disabled = false;
      btn.innerHTML = '💾 保存配置';
    }
  }

  // 设为默认
  async function activateProvider(p) {
    try {
      const r = await fetch('/api/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ llm_provider: p.id }),
      });
      const data = await r.json();
      if (data.ok) {
        toast('✓ 已切换到 ' + p.name + '（' + (data.active_model || '') + '）', 'ok', 3000);
        await loadConfig();
      } else {
        toast('✗ ' + data.message, 'err', 4000);
      }
    } catch (e) {
      toast('✗ 切换失败：' + e.message, 'err', 4000);
    }
  }

  // 复制 .env 路径
  async function copyEnvPath() {
    const path = $('envPath').textContent;
    try {
      await navigator.clipboard.writeText(path);
      toast('✓ 已复制到剪贴板', 'ok', 2000);
    } catch (e) {
      const ta = document.createElement('textarea');
      ta.value = path;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.select();
      try {
        document.execCommand('copy');
        toast('✓ 已复制到剪贴板', 'ok', 2000);
      } catch (e2) {
        toast('❌ 复制失败，请手动复制', 'err');
      }
      document.body.removeChild(ta);
    }
  }

  // 事件绑定
  document.addEventListener('DOMContentLoaded', () => {
    loadConfig();
    $('closeEdit').addEventListener('click', closeEdit);
    $('providerForm').addEventListener('submit', saveConfig);
    $('testBtn').addEventListener('click', testConnection);
    $('useAsActiveBtn').addEventListener('click', () => {
      const providerId = $('editProviderId').value;
      const p = ALL_PROVIDERS.find(x => x.id === providerId);
      if (p) activateProvider(p);
    });
    $('copyEnvPath').addEventListener('click', copyEnvPath);

    $('toggleKeyVisibility').addEventListener('click', () => {
      const input = $('apiKey');
      input.type = input.type === 'password' ? 'text' : 'password';
    });

    $('pasteKey').addEventListener('click', async () => {
      try {
        const text = await navigator.clipboard.readText();
        $('apiKey').value = text;
        toast('✓ 已粘贴', 'ok', 1500);
      } catch (e) {
        toast('❌ 无法访问剪贴板', 'err');
      }
    });

    $('baseUrl').addEventListener('focus', (e) => e.target.select());
    $('apiKey').addEventListener('focus', (e) => {
      if (e.target.value) e.target.select();
    });
  });
})();