/* ============================================================
   审思明辨——智判法案双擎系统  前端脚本
   ============================================================ */

const API_BASE = '';  // 同源，留空即可

// ===== Tab 切换 =====
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', e => {
        e.preventDefault();
        const tab = link.dataset.tab;
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
        link.classList.add('active');
        document.getElementById(`tab-${tab}`).classList.add('active');
    });
});

// ===== 工具函数 =====

function showLoading(text = '正在检索中，请稍候...') {
    document.getElementById('loading-text').textContent = text;
    document.getElementById('loading').classList.add('show');
}

function hideLoading() {
    document.getElementById('loading').classList.remove('show');
}

function showToast(msg, type = 'error') {
    const c = document.getElementById('toast-container');
    const d = document.createElement('div');
    d.className = `toast ${type}`;
    d.textContent = msg;
    c.appendChild(d);
    setTimeout(() => d.remove(), 4000);
}

/** 简易 Markdown -> HTML 转换 */
function renderMarkdown(text) {
    if (!text) return '';
    return text
        .replace(/^### (.+)$/gm, '<h3>$1</h3>')
        .replace(/^## (.+)$/gm, '<h2>$1</h2>')
        .replace(/^# (.+)$/gm, '<h1>$1</h1>')
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/^- (.+)$/gm, '<li>$1</li>')
        .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
        .replace(/^(\d+)\. (.+)$/gm, '<li>$2</li>')
        .replace(/\n\n/g, '</p><p>')
        .replace(/^(?!<[hul])(.+)$/gm, '<p>$1</p>')
        .replace(/<\/ul>\s*<ul>/g, '');
}

async function post(path, body) {
    const resp = await fetch(API_BASE + path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        throw new Error(err.detail || `请求失败 (${resp.status})`);
    }
    return resp.json();
}

// ===== 法律问答 =====

const qaHistory = [];

function appendMessage(role, content, isHtml = false) {
    const container = document.getElementById('qa-messages');
    // 移除欢迎语
    const welcome = container.querySelector('.welcome-msg');
    if (welcome) welcome.remove();

    const div = document.createElement('div');
    div.className = `message ${role}`;
    const avatar = role === 'user' ? '👤' : '⚖️';
    div.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-bubble ${role === 'assistant' ? 'md-content' : ''}">
            ${isHtml ? content : escapeHtml(content)}
        </div>`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function escapeHtml(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function appendTypingIndicator() {
    const container = document.getElementById('qa-messages');
    const div = document.createElement('div');
    div.id = 'typing-indicator';
    div.className = 'message assistant';
    div.innerHTML = `<div class="message-avatar">⚖️</div>
        <div class="message-bubble" style="padding:14px 20px;">
            <span class="spinner" style="width:16px;height:16px;border-width:2px;display:inline-block;vertical-align:middle;"></span>
            <span style="margin-left:8px;color:#888;font-size:13px;">正在思考中...</span>
        </div>`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function removeTypingIndicator() {
    const el = document.getElementById('typing-indicator');
    if (el) el.remove();
}

function handleQaKey(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendQaMessage();
    }
}

function askQuick(q) {
    document.getElementById('qa-input').value = q;
    sendQaMessage();
}

async function sendQaMessage() {
    const input = document.getElementById('qa-input');
    const query = input.value.trim();
    if (!query) return;

    input.value = '';
    appendMessage('user', query);
    appendTypingIndicator();

    // 法律问答：优先用类案检索接口，兼顾法条检索
    try {
        // 并发调用法条 + 类案
        const [lawRes, caseRes] = await Promise.all([
            post('/api/v1/laws/search', { query, page_size: 3, with_detail: false, with_ai: false }),
            post('/api/v1/cases/search', { query, page_size: 3, with_ai: false })
        ]);

        const laws = lawRes.data?.laws || [];
        const cases = caseRes.data?.cases || [];

        let html = '';
        if (laws.length > 0) {
            html += `<div style="margin-bottom:10px"><strong>📖 相关法规</strong><ul style="margin:6px 0 0 16px">`;
            laws.forEach(l => {
                const title = l.title || l.name || '未知法规';
                html += `<li style="margin-bottom:4px">${title}</li>`;
            });
            html += `</ul></div>`;
        }
        if (cases.length > 0) {
            html += `<div style="margin-bottom:10px"><strong>📋 相关案例</strong><ul style="margin:6px 0 0 16px">`;
            cases.forEach(c => {
                html += `<li style="margin-bottom:4px">${c.caseName || '未知案件'}（${c.courtName || ''} ${c.judgeDate || ''}）</li>`;
            });
            html += `</ul></div>`;
        }
        if (!laws.length && !cases.length) {
            html = `<p style="color:#888">未检索到相关法规或案例，建议前往"法条检索"或"类案匹配"进行更详细的查询。</p>`;
        } else {
            html += `<p style="color:#888;font-size:12px;margin-top:8px">💡 提示：可切换到「法条检索」或「类案匹配」获取 AI 深度分析报告</p>`;
        }

        removeTypingIndicator();
        appendMessage('assistant', html, true);

        // 更新对话历史
        qaHistory.push({ role: 'user', query });

    } catch (e) {
        removeTypingIndicator();
        appendMessage('assistant', `抱歉，查询出错：${e.message}，请检查后端服务是否正常运行。`, false);
    }
}


// ===== 法条检索 =====

async function searchLaws() {
    const query = document.getElementById('law-input').value.trim();
    if (!query) { showToast('请输入查询内容'); return; }

    const mode = document.querySelector('input[name="law-mode"]:checked').value;
    showLoading('正在检索法规...');

    try {
        const res = await post('/api/v1/laws/search', {
            query,
            field_name: mode,
            page_size: 5,
            with_detail: false,
            with_ai: true
        });
        renderLawResults(res.data);
    } catch (e) {
        showToast(e.message);
    } finally {
        hideLoading();
    }
}

function renderLawResults(data) {
    const container = document.getElementById('law-results');
    const laws = data.laws || [];

    if (!laws.length) {
        container.innerHTML = `<div class="empty-state"><div class="empty-icon">🔍</div><p>${data.analysis || '未找到相关法规'}</p></div>`;
        return;
    }

    let html = '';

    // AI 分析报告
    if (data.analysis && data.analysis !== '（未配置腾讯元器，仅展示检索结果）') {
        html += `<div class="analysis-section">
            <div class="analysis-title">⚖️ AI 法律分析</div>
            <div class="analysis-content md-content">${renderMarkdown(data.analysis)}</div>
        </div>`;
    }

    // 法规卡片
    html += `<div style="margin-bottom:12px;color:#888;font-size:13px">共检索到 <strong style="color:#1a3a5c">${data.total || laws.length}</strong> 条相关法规，展示前 ${laws.length} 条</div>`;
    laws.forEach((law, i) => {
        const title = law.title || law.name || '未知法规';
        const date = law.publishDate || law.issuedDate || '';
        const publisher = law.publisherName || law.issuer || '';
        const timeliness = law.timelinessName || '';
        const lawId = law.id || law.lawsId || '';
        const tagClass = timeliness === '现行有效' ? 'tag-valid' : timeliness === '失效' ? 'tag-invalid' : 'tag-court';

        html += `<div class="result-card" id="law-card-${i}">
            <div class="result-card-header">
                <div>
                    <div class="result-card-title">📄 ${title}</div>
                    <div class="result-card-meta">
                        <span>${publisher}</span>
                        <span>${date}</span>
                        ${timeliness ? `<span class="tag ${tagClass}">${timeliness}</span>` : ''}
                    </div>
                </div>
            </div>
            ${lawId ? `<div style="margin-top:8px">
                <span class="expand-btn" onclick="loadLawDetail('${lawId}', ${i})">查看全文 ▼</span>
            </div>` : ''}
            <div id="law-detail-${i}" style="display:none"></div>
        </div>`;
    });

    container.innerHTML = html;
}

async function loadLawDetail(lawId, idx) {
    const detailDiv = document.getElementById(`law-detail-${idx}`);
    const btn = detailDiv.previousElementSibling.querySelector('.expand-btn');

    if (detailDiv.style.display === 'block') {
        detailDiv.style.display = 'none';
        btn.textContent = '查看全文 ▼';
        return;
    }

    btn.textContent = '加载中...';
    try {
        const res = await post('/api/v1/laws/detail', { law_id: lawId });
        const body = res.data?.body || {};
        const content = body.lawDetailContent || '暂无全文内容';
        detailDiv.innerHTML = `<div style="margin-top:12px;padding:12px;background:#f9f9f9;border-radius:6px;font-size:13px;line-height:1.8;white-space:pre-wrap;max-height:400px;overflow-y:auto">${content}</div>`;
        detailDiv.style.display = 'block';
        btn.textContent = '收起全文 ▲';
    } catch (e) {
        btn.textContent = '加载失败，点击重试 ▼';
        showToast('加载全文失败：' + e.message);
    }
}

// 回车检索
document.getElementById('law-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') searchLaws();
});


// ===== 类案匹配 =====

async function searchCases() {
    const query = document.getElementById('case-input').value.trim();
    if (!query) { showToast('请输入案情描述'); return; }

    showLoading('正在检索类案，请稍候...');
    try {
        const res = await post('/api/v1/cases/search', {
            query,
            page_size: 5,
            with_ai: true
        });
        renderCaseResults(res.data);
    } catch (e) {
        showToast(e.message);
    } finally {
        hideLoading();
    }
}

function renderCaseResults(data) {
    const container = document.getElementById('case-results');
    const cases = data.cases || [];

    if (!cases.length) {
        container.innerHTML = `<div class="empty-state"><div class="empty-icon">🔍</div><p>${data.analysis || '未找到相关案例'}</p></div>`;
        return;
    }

    let html = '';

    // AI 分析报告
    if (data.analysis && data.analysis !== '（未配置腾讯元器，仅展示检索结果）') {
        html += `<div class="analysis-section">
            <div class="analysis-title">⚖️ AI 类案分析报告</div>
            <div class="analysis-content md-content">${renderMarkdown(data.analysis)}</div>
        </div>`;
    }

    html += `<div style="margin-bottom:12px;color:#888;font-size:13px">共检索到 <strong style="color:#1a3a5c">${data.total || cases.length}</strong> 个相关案例，展示前 ${cases.length} 个</div>`;

    cases.forEach((c, i) => {
        const name = c.caseName || '未知案件';
        const court = c.courtName || '';
        const date = c.judgeDate || c.judgeYear || '';
        const abstract = c.abstract || c.summary || '暂无摘要';
        const type = c.judgementTypeName || '';

        html += `<div class="result-card">
            <div class="result-card-header">
                <div>
                    <div class="result-card-title">📋 ${name}</div>
                    <div class="result-card-meta">
                        ${court ? `<span class="tag tag-court">${court}</span>` : ''}
                        <span>${date}</span>
                        ${type ? `<span>${type}</span>` : ''}
                    </div>
                </div>
            </div>
            <div class="result-card-body" id="case-body-${i}">${escapeHtml(abstract)}</div>
            ${abstract.length > 150 ? `<span class="expand-btn" onclick="toggleExpand('case-body-${i}', this)">展开全文 ▼</span>` : ''}
        </div>`;
    });

    container.innerHTML = html;
}

function toggleExpand(id, btn) {
    const el = document.getElementById(id);
    if (el.classList.contains('expanded')) {
        el.classList.remove('expanded');
        btn.textContent = '展开全文 ▼';
    } else {
        el.classList.add('expanded');
        btn.textContent = '收起 ▲';
    }
}

document.getElementById('case-input').addEventListener('keydown', e => {
    if (e.key === 'Enter') searchCases();
});


// ===== 诉讼策略推演 =====

async function analyzeStrategy() {
    const content = document.getElementById('strategy-input').value.trim();
    if (!content) { showToast('请输入案情描述或起诉状内容'); return; }
    if (content.length < 20) { showToast('案情描述太短，请提供更详细的信息'); return; }

    showLoading('正在进行策略推演，预计需要 15~30 秒...');
    try {
        const res = await post('/api/v1/strategy/analyze', { case_content: content });
        renderStrategyResults(res.data);
    } catch (e) {
        showToast('策略推演失败：' + e.message);
    } finally {
        hideLoading();
    }
}

function renderStrategyResults(data) {
    const container = document.getElementById('strategy-results');
    const report = data.strategy_report || '';

    if (!report) {
        container.innerHTML = `<div class="empty-state"><div class="empty-icon">⚠️</div><p>推演失败，请检查元器配置是否正确</p></div>`;
        return;
    }

    const html = `
        <div style="margin-bottom:16px;display:flex;gap:16px;font-size:13px;color:#888">
            <span>📋 参考类案：<strong style="color:#1a3a5c">${data.related_cases_count || 0}</strong> 个</span>
            <span>📖 相关法规：<strong style="color:#1a3a5c">${data.related_laws_count || 0}</strong> 条</span>
        </div>
        <div class="analysis-section">
            <div class="analysis-title">⚖️ 对方律师视角 · 质证意见与诉讼风险报告</div>
            <div class="analysis-content md-content">${renderMarkdown(report)}</div>
        </div>
        <div style="margin-top:16px;text-align:right">
            <button onclick="exportReport()" style="background:#1a3a5c;color:white;border:none;padding:10px 24px;border-radius:6px;cursor:pointer;font-size:14px">
                📄 导出报告
            </button>
        </div>`;

    container.innerHTML = html;
}

function exportReport() {
    const content = document.querySelector('#strategy-results .analysis-content');
    if (!content) return;
    const text = content.innerText;
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `诉讼策略报告_${new Date().toLocaleDateString('zh-CN')}.txt`;
    a.click();
}


// ===== 单选按钮样式同步 =====
document.querySelectorAll('input[name="law-mode"]').forEach(radio => {
    radio.addEventListener('change', () => {
        document.querySelectorAll('.mode-btn').forEach(b => b.classList.remove('active'));
        radio.closest('.mode-btn').classList.add('active');
    });
});
