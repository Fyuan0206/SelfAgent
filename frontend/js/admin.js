/**
 * Self-Agent Admin Panel JavaScript
 * Handles dashboard, skills, rules, and profiles management
 */

// ==================== Configuration ====================
const API_BASE = window.location.origin;
const DBT_ADMIN_KEY = 'dbt-admin-secret-key'; // Default key, should match backend

// ==================== State ====================
const AdminState = {
    skills: [],
    rules: [],
    profiles: [],
    users: [],
    modules: [],
    stats: null,
    currentPage: 'dashboard',
    // Rule editing state
    currentRuleConditions: {
        emotion_conditions: [],
        trigger_signals: [],
        arousal: null,
        context_contains: [],
        risk_level: null
    }
};

// Available emotions and signals for rule conditions
const EMOTION_OPTIONS = ['焦虑', '悲伤', '愤怒', '恐惧', '空虚感', '羞愧', '内疚', '孤独', '绝望', '激越'];
const SIGNAL_OPTIONS = ['agitation_level', 'dissociation_level', 'hopelessness', 'self_harm_risk', 'suicidal_ideation'];
const OPERATOR_OPTIONS = ['>=', '>', '<=', '<', '=='];

// ==================== Initialization ====================
document.addEventListener('DOMContentLoaded', async () => {
    // Check admin authentication
    if (!Auth.isLoggedIn()) {
        window.location.href = 'login.html';
        return;
    }

    // Initialize dark mode
    if (localStorage.getItem('darkMode') === 'true') {
        document.documentElement.classList.add('dark');
    }

    // Load user info
    try {
        const user = await Auth.getCurrentUser();
        updateUserDisplay(user);
    } catch (e) {
        console.error('Failed to load user:', e);
    }

    // Load initial data
    await loadDashboardData();
});

function updateUserDisplay(user) {
    document.getElementById('user-name').textContent = user.username || '管理员';
    document.getElementById('user-email').textContent = user.email || '';
    document.getElementById('user-avatar').textContent = (user.username || 'A')[0].toUpperCase();
}

// ==================== Navigation ====================
function showPage(page) {
    AdminState.currentPage = page;

    // Update sidebar
    document.querySelectorAll('.sidebar-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.page === page) {
            item.classList.add('active');
        }
    });

    // Update page title
    const titles = {
        dashboard: '仪表板',
        skills: '技能管理',
        rules: '规则管理',
        profiles: '用户画像',
        users: '用户管理'
    };
    document.getElementById('page-title').textContent = titles[page] || page;

    // Show/hide pages
    document.querySelectorAll('.page-content').forEach(el => el.classList.add('hidden'));
    document.getElementById(`page-${page}`).classList.remove('hidden');

    // Load page data
    if (page === 'dashboard') loadDashboardData();
    else if (page === 'skills') loadSkills();
    else if (page === 'rules') loadRules();
    else if (page === 'profiles') loadProfiles();
    else if (page === 'users') loadUsers();

    // Close mobile sidebar
    if (window.innerWidth < 1024) toggleSidebar();
}

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('mobile-overlay');
    sidebar.classList.toggle('-translate-x-full');
    overlay.classList.toggle('hidden');
}

function toggleDarkMode() {
    document.documentElement.classList.toggle('dark');
    localStorage.setItem('darkMode', document.documentElement.classList.contains('dark'));
}

// ==================== API Helpers ====================
async function fetchDBTAdmin(endpoint, options = {}) {
    const response = await fetch(`${API_BASE}/api/v1/admin${endpoint}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            'X-Admin-Key': DBT_ADMIN_KEY,
            ...options.headers
        }
    });
    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || `HTTP ${response.status}`);
    }
    return response.json();
}

async function fetchProfileAPI(endpoint) {
    const response = await Auth.fetch(`${API_BASE}/api/v1/admin${endpoint}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
}

// ==================== Dashboard ====================
async function loadDashboardData() {
    try {
        const stats = await fetchDBTAdmin('/stats');
        AdminState.stats = stats;

        document.getElementById('stat-skills').textContent = stats.total_skills || 0;
        document.getElementById('stat-rules').textContent = stats.total_rules || 0;
        document.getElementById('stat-modules').textContent = stats.total_modules || 0;

        // Load profiles count
        try {
            const profiles = await fetchProfileAPI('/profiles');
            document.getElementById('stat-users').textContent = profiles.length || 0;
            AdminState.profiles = profiles;
        } catch (e) {
            document.getElementById('stat-users').textContent = '--';
        }

        // Render charts
        renderSkillsChart(stats.skills_per_module || {});
        renderModulesChart(stats);
    } catch (error) {
        console.error('Failed to load dashboard:', error);
        showToast('加载仪表板数据失败', 'error');
    }
}

function renderSkillsChart(skillsPerModule) {
    const ctx = document.getElementById('skillsChart');
    if (!ctx) return;

    const labels = Object.keys(skillsPerModule);
    const data = Object.values(skillsPerModule);
    const colors = ['#6366f1', '#ec4899', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4'];

    if (window.skillsChartInstance) window.skillsChartInstance.destroy();

    window.skillsChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels.length ? labels : ['暂无数据'],
            datasets: [{
                data: data.length ? data : [1],
                backgroundColor: labels.length ? colors.slice(0, labels.length) : ['#e5e7eb'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { padding: 20, usePointStyle: true } }
            }
        }
    });
}

function renderModulesChart(stats) {
    const ctx = document.getElementById('modulesChart');
    if (!ctx) return;

    if (window.modulesChartInstance) window.modulesChartInstance.destroy();

    window.modulesChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['技能', '规则', '模块'],
            datasets: [{
                label: '总数',
                data: [stats.total_skills || 0, stats.total_rules || 0, stats.total_modules || 0],
                backgroundColor: ['#6366f1', '#ec4899', '#10b981'],
                borderRadius: 8
            }, {
                label: '启用',
                data: [stats.active_skills || 0, stats.active_rules || 0, stats.total_modules || 0],
                backgroundColor: ['#a5b4fc', '#f9a8d4', '#6ee7b7'],
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'bottom' } },
            scales: { y: { beginAtZero: true } }
        }
    });
}

// ==================== Skills Management ====================
async function loadSkills() {
    try {
        const skills = await fetchDBTAdmin('/skills');
        AdminState.skills = skills;
        renderSkillsTable(skills);

        // Load modules for filter
        const modules = [...new Set(skills.map(s => s.module_name).filter(Boolean))];
        const select = document.getElementById('skills-module-filter');
        select.innerHTML = '<option value="">全部模块</option>' +
            modules.map(m => `<option value="${m}">${m}</option>`).join('');
    } catch (error) {
        console.error('Failed to load skills:', error);
        document.getElementById('skills-table-body').innerHTML =
            '<tr><td colspan="7" class="px-6 py-8 text-center text-red-500">加载失败: ' + error.message + '</td></tr>';
    }
}

function renderSkillsTable(skills) {
    const tbody = document.getElementById('skills-table-body');
    if (!skills.length) {
        tbody.innerHTML = '<tr><td colspan="7" class="px-6 py-8 text-center text-gray-500 dark:text-gray-400">暂无技能数据</td></tr>';
        return;
    }

    tbody.innerHTML = skills.map(skill => `
        <tr class="hover:bg-gray-50 dark:hover:bg-slate-700/50">
            <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">${skill.id}</td>
            <td class="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">${escapeHtml(skill.name)}</td>
            <td class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">${escapeHtml(skill.name_en || '')}</td>
            <td class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">${escapeHtml(skill.module_name || '')}</td>
            <td class="px-6 py-4 text-sm">${'★'.repeat(skill.difficulty_level || 1)}${'☆'.repeat(3 - (skill.difficulty_level || 1))}</td>
            <td class="px-6 py-4">
                <span class="px-2 py-1 text-xs rounded-full ${skill.is_active ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'}">
                    ${skill.is_active ? '启用' : '禁用'}
                </span>
            </td>
            <td class="px-6 py-4">
                <div class="flex items-center gap-2">
                    <button onclick="editSkill(${skill.id})" class="p-1.5 hover:bg-gray-100 dark:hover:bg-slate-600 rounded-lg" title="编辑">
                        <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path></svg>
                    </button>
                    <button onclick="toggleSkill(${skill.id})" class="p-1.5 hover:bg-gray-100 dark:hover:bg-slate-600 rounded-lg" title="${skill.is_active ? '禁用' : '启用'}">
                        <svg class="w-4 h-4 ${skill.is_active ? 'text-yellow-500' : 'text-green-500'}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${skill.is_active ? 'M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636' : 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z'}"></path></svg>
                    </button>
                    <button onclick="deleteSkill(${skill.id})" class="p-1.5 hover:bg-gray-100 dark:hover:bg-slate-600 rounded-lg" title="删除">
                        <svg class="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

function filterSkills() {
    const search = document.getElementById('skills-search').value.toLowerCase();
    const module = document.getElementById('skills-module-filter').value;

    const filtered = AdminState.skills.filter(skill => {
        const matchSearch = !search || skill.name.toLowerCase().includes(search) || (skill.name_en || '').toLowerCase().includes(search);
        const matchModule = !module || skill.module_name === module;
        return matchSearch && matchModule;
    });

    renderSkillsTable(filtered);
}

// Skill Modal Functions
function openSkillModal(skill = null) {
    document.getElementById('skill-modal-title').textContent = skill ? '编辑技能' : '新建技能';
    document.getElementById('skill-id').value = skill?.id || '';
    document.getElementById('skill-name').value = skill?.name || '';
    document.getElementById('skill-name-en').value = skill?.name_en || '';
    document.getElementById('skill-description').value = skill?.description || '';
    document.getElementById('skill-difficulty').value = skill?.difficulty_level || 1;
    document.getElementById('skill-emotions').value = (skill?.trigger_emotions || []).join(', ');
    document.getElementById('skill-steps').value = (skill?.steps || []).join('\n');
    document.getElementById('skill-active').checked = skill?.is_active !== false;

    // Load modules dropdown
    loadModulesDropdown(skill?.module_id);

    document.getElementById('skill-modal').classList.remove('hidden');
}

async function loadModulesDropdown(selectedId = null) {
    const select = document.getElementById('skill-module');
    try {
        // Get unique modules from skills
        const modules = [...new Map(AdminState.skills.map(s => [s.module_id, { id: s.module_id, name: s.module_name }])).values()].filter(m => m.id);
        select.innerHTML = modules.map(m => `<option value="${m.id}" ${m.id === selectedId ? 'selected' : ''}>${m.name}</option>`).join('');
        if (!modules.length) select.innerHTML = '<option value="1">正念</option><option value="2">痛苦耐受</option><option value="3">情绪调节</option><option value="4">人际效能</option>';
    } catch (e) {
        select.innerHTML = '<option value="1">正念</option>';
    }
}

function closeSkillModal() {
    document.getElementById('skill-modal').classList.add('hidden');
}

async function saveSkill(event) {
    event.preventDefault();
    const id = document.getElementById('skill-id').value;
    const data = {
        name: document.getElementById('skill-name').value,
        name_en: document.getElementById('skill-name-en').value,
        module_id: parseInt(document.getElementById('skill-module').value),
        description: document.getElementById('skill-description').value,
        difficulty_level: parseInt(document.getElementById('skill-difficulty').value),
        trigger_emotions: document.getElementById('skill-emotions').value.split(',').map(s => s.trim()).filter(Boolean),
        steps: document.getElementById('skill-steps').value.split('\n').filter(Boolean),
        is_active: document.getElementById('skill-active').checked
    };

    try {
        if (id) {
            await fetchDBTAdmin(`/skills/${id}`, { method: 'PUT', body: JSON.stringify(data) });
            showToast('技能更新成功');
        } else {
            await fetchDBTAdmin('/skills', { method: 'POST', body: JSON.stringify(data) });
            showToast('技能创建成功');
        }
        closeSkillModal();
        loadSkills();
    } catch (error) {
        showToast('保存失败: ' + error.message, 'error');
    }
}

async function editSkill(id) {
    const skill = AdminState.skills.find(s => s.id === id);
    if (skill) openSkillModal(skill);
}

async function toggleSkill(id) {
    try {
        await fetchDBTAdmin(`/skills/${id}/toggle`, { method: 'POST' });
        showToast('状态已切换');
        loadSkills();
    } catch (error) {
        showToast('操作失败: ' + error.message, 'error');
    }
}

async function deleteSkill(id) {
    if (!confirm('确定要删除此技能吗？')) return;
    try {
        await fetchDBTAdmin(`/skills/${id}`, { method: 'DELETE' });
        showToast('技能已删除');
        loadSkills();
    } catch (error) {
        showToast('删除失败: ' + error.message, 'error');
    }
}

// ==================== Rules Management ====================
async function loadRules() {
    try {
        const rules = await fetchDBTAdmin('/rules');
        AdminState.rules = rules;
        renderRulesTable(rules);
    } catch (error) {
        console.error('Failed to load rules:', error);
        document.getElementById('rules-table-body').innerHTML =
            '<tr><td colspan="6" class="px-6 py-8 text-center text-red-500">加载失败: ' + error.message + '</td></tr>';
    }
}

function renderRulesTable(rules) {
    const tbody = document.getElementById('rules-table-body');
    if (!rules.length) {
        tbody.innerHTML = '<tr><td colspan="6" class="px-6 py-8 text-center text-gray-500 dark:text-gray-400">暂无规则数据</td></tr>';
        return;
    }

    tbody.innerHTML = rules.map(rule => `
        <tr class="hover:bg-gray-50 dark:hover:bg-slate-700/50">
            <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">${rule.id}</td>
            <td class="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">${escapeHtml(rule.rule_name)}</td>
            <td class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">${rule.priority}</td>
            <td class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">${(rule.skill_ids || []).join(', ') || '-'}</td>
            <td class="px-6 py-4">
                <span class="px-2 py-1 text-xs rounded-full ${rule.is_active ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'}">
                    ${rule.is_active ? '启用' : '禁用'}
                </span>
            </td>
            <td class="px-6 py-4">
                <div class="flex items-center gap-2">
                    <button onclick="editRule(${rule.id})" class="p-1.5 hover:bg-gray-100 dark:hover:bg-slate-600 rounded-lg" title="编辑">
                        <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path></svg>
                    </button>
                    <button onclick="toggleRule(${rule.id})" class="p-1.5 hover:bg-gray-100 dark:hover:bg-slate-600 rounded-lg">
                        <svg class="w-4 h-4 ${rule.is_active ? 'text-yellow-500' : 'text-green-500'}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${rule.is_active ? 'M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636' : 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z'}"></path></svg>
                    </button>
                    <button onclick="deleteRule(${rule.id})" class="p-1.5 hover:bg-gray-100 dark:hover:bg-slate-600 rounded-lg" title="删除">
                        <svg class="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

function filterRules() {
    const search = document.getElementById('rules-search').value.toLowerCase();
    const filtered = AdminState.rules.filter(rule => !search || rule.rule_name.toLowerCase().includes(search));
    renderRulesTable(filtered);
}

function openRuleModal(rule = null) {
    document.getElementById('rule-modal-title').textContent = rule ? '编辑规则' : '新建规则';
    document.getElementById('rule-id').value = rule?.id || '';
    document.getElementById('rule-name').value = rule?.rule_name || '';
    document.getElementById('rule-priority').value = rule?.priority || 500;
    document.getElementById('rule-description').value = rule?.description || '';
    document.getElementById('rule-skills').value = (rule?.skill_ids || []).join(', ');
    document.getElementById('rule-active').checked = rule?.is_active !== false;

    // Initialize conditions from rule or empty
    const conditions = rule?.conditions || {};
    AdminState.currentRuleConditions = {
        emotion_conditions: conditions.emotion_conditions || [],
        trigger_signals: conditions.trigger_signals || [],
        arousal: conditions.arousal || null,
        context_contains: conditions.context_contains || [],
        risk_level: conditions.risk_level || null
    };

    // Render conditions
    renderEmotionConditions();
    renderTriggerSignals();

    // Set arousal
    const hasArousal = AdminState.currentRuleConditions.arousal !== null;
    document.getElementById('arousal-enabled').checked = hasArousal;
    document.getElementById('arousal-inputs').classList.toggle('hidden', !hasArousal);
    if (hasArousal) {
        document.getElementById('arousal-min').value = AdminState.currentRuleConditions.arousal.min || 0;
        document.getElementById('arousal-max').value = AdminState.currentRuleConditions.arousal.max || 1;
    }

    // Set context keywords
    document.getElementById('rule-context').value = (AdminState.currentRuleConditions.context_contains || []).join(', ');

    // Set risk level
    document.getElementById('rule-risk-level').value = AdminState.currentRuleConditions.risk_level || '';

    document.getElementById('rule-modal').classList.remove('hidden');
}

function closeRuleModal() {
    document.getElementById('rule-modal').classList.add('hidden');
}

// Render emotion conditions list
function renderEmotionConditions() {
    const container = document.getElementById('emotion-conditions-list');
    const conditions = AdminState.currentRuleConditions.emotion_conditions;

    if (!conditions.length) {
        container.innerHTML = '<p class="text-xs text-gray-400 dark:text-gray-500">暂无情绪条件</p>';
        return;
    }

    container.innerHTML = conditions.map((cond, index) => `
        <div class="flex items-center gap-2 bg-gray-50 dark:bg-slate-700 rounded-lg p-2">
            <select onchange="updateEmotionCondition(${index}, 'emotion', this.value)" class="flex-1 px-2 py-1 bg-white dark:bg-slate-600 border border-gray-200 dark:border-slate-500 rounded text-sm text-gray-900 dark:text-white">
                ${EMOTION_OPTIONS.map(e => `<option value="${e}" ${cond.emotion === e ? 'selected' : ''}>${e}</option>`).join('')}
            </select>
            <select onchange="updateEmotionCondition(${index}, 'operator', this.value)" class="w-16 px-2 py-1 bg-white dark:bg-slate-600 border border-gray-200 dark:border-slate-500 rounded text-sm text-gray-900 dark:text-white">
                ${OPERATOR_OPTIONS.map(op => `<option value="${op}" ${cond.operator === op ? 'selected' : ''}>${op}</option>`).join('')}
            </select>
            <input type="number" step="0.1" min="0" max="1" value="${cond.value}" onchange="updateEmotionCondition(${index}, 'value', parseFloat(this.value))" class="w-16 px-2 py-1 bg-white dark:bg-slate-600 border border-gray-200 dark:border-slate-500 rounded text-sm text-gray-900 dark:text-white">
            <button type="button" onclick="removeEmotionCondition(${index})" class="p-1 text-red-500 hover:bg-red-100 dark:hover:bg-red-900/30 rounded">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
        </div>
    `).join('');
}

// Render trigger signals list
function renderTriggerSignals() {
    const container = document.getElementById('trigger-signals-list');
    const signals = AdminState.currentRuleConditions.trigger_signals;

    if (!signals.length) {
        container.innerHTML = '<p class="text-xs text-gray-400 dark:text-gray-500">暂无触发信号</p>';
        return;
    }

    container.innerHTML = signals.map((sig, index) => `
        <div class="flex items-center gap-2 bg-gray-50 dark:bg-slate-700 rounded-lg p-2">
            <select onchange="updateTriggerSignal(${index}, 'signal', this.value)" class="flex-1 px-2 py-1 bg-white dark:bg-slate-600 border border-gray-200 dark:border-slate-500 rounded text-sm text-gray-900 dark:text-white">
                ${SIGNAL_OPTIONS.map(s => `<option value="${s}" ${sig.signal === s ? 'selected' : ''}>${s}</option>`).join('')}
            </select>
            <select onchange="updateTriggerSignal(${index}, 'operator', this.value)" class="w-16 px-2 py-1 bg-white dark:bg-slate-600 border border-gray-200 dark:border-slate-500 rounded text-sm text-gray-900 dark:text-white">
                ${OPERATOR_OPTIONS.map(op => `<option value="${op}" ${sig.operator === op ? 'selected' : ''}>${op}</option>`).join('')}
            </select>
            <input type="number" step="0.1" min="0" max="1" value="${sig.value}" onchange="updateTriggerSignal(${index}, 'value', parseFloat(this.value))" class="w-16 px-2 py-1 bg-white dark:bg-slate-600 border border-gray-200 dark:border-slate-500 rounded text-sm text-gray-900 dark:text-white">
            <button type="button" onclick="removeTriggerSignal(${index})" class="p-1 text-red-500 hover:bg-red-100 dark:hover:bg-red-900/30 rounded">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
        </div>
    `).join('');
}

// Add emotion condition
function addEmotionCondition() {
    AdminState.currentRuleConditions.emotion_conditions.push({
        emotion: '焦虑',
        operator: '>=',
        value: 0.5
    });
    renderEmotionConditions();
}

// Update emotion condition
function updateEmotionCondition(index, field, value) {
    AdminState.currentRuleConditions.emotion_conditions[index][field] = value;
}

// Remove emotion condition
function removeEmotionCondition(index) {
    AdminState.currentRuleConditions.emotion_conditions.splice(index, 1);
    renderEmotionConditions();
}

// Add trigger signal
function addTriggerSignal() {
    AdminState.currentRuleConditions.trigger_signals.push({
        signal: 'agitation_level',
        operator: '>=',
        value: 0.4
    });
    renderTriggerSignals();
}

// Update trigger signal
function updateTriggerSignal(index, field, value) {
    AdminState.currentRuleConditions.trigger_signals[index][field] = value;
}

// Remove trigger signal
function removeTriggerSignal(index) {
    AdminState.currentRuleConditions.trigger_signals.splice(index, 1);
    renderTriggerSignals();
}

// Toggle arousal condition
function toggleArousalCondition() {
    const enabled = document.getElementById('arousal-enabled').checked;
    document.getElementById('arousal-inputs').classList.toggle('hidden', !enabled);
    if (!enabled) {
        AdminState.currentRuleConditions.arousal = null;
    } else {
        AdminState.currentRuleConditions.arousal = {
            min: parseFloat(document.getElementById('arousal-min').value) || 0,
            max: parseFloat(document.getElementById('arousal-max').value) || 1
        };
    }
}

async function saveRule(event) {
    event.preventDefault();
    const id = document.getElementById('rule-id').value;

    // Build conditions object
    const conditions = {};

    // Emotion conditions
    if (AdminState.currentRuleConditions.emotion_conditions.length > 0) {
        conditions.emotion_conditions = AdminState.currentRuleConditions.emotion_conditions;
    }

    // Trigger signals
    if (AdminState.currentRuleConditions.trigger_signals.length > 0) {
        conditions.trigger_signals = AdminState.currentRuleConditions.trigger_signals;
    }

    // Arousal
    if (document.getElementById('arousal-enabled').checked) {
        conditions.arousal = {
            min: parseFloat(document.getElementById('arousal-min').value) || 0,
            max: parseFloat(document.getElementById('arousal-max').value) || 1
        };
    }

    // Context keywords
    const contextKeywords = document.getElementById('rule-context').value.split(',').map(s => s.trim()).filter(Boolean);
    if (contextKeywords.length > 0) {
        conditions.context_contains = contextKeywords;
    }

    // Risk level
    const riskLevel = document.getElementById('rule-risk-level').value;
    if (riskLevel) {
        conditions.risk_level = riskLevel;
    }

    const data = {
        rule_name: document.getElementById('rule-name').value,
        priority: parseInt(document.getElementById('rule-priority').value),
        description: document.getElementById('rule-description').value,
        skill_ids: document.getElementById('rule-skills').value.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n)),
        conditions: conditions,
        is_active: document.getElementById('rule-active').checked
    };

    try {
        if (id) {
            await fetchDBTAdmin(`/rules/${id}`, { method: 'PUT', body: JSON.stringify(data) });
            showToast('规则更新成功');
        } else {
            await fetchDBTAdmin('/rules', { method: 'POST', body: JSON.stringify(data) });
            showToast('规则创建成功');
        }
        closeRuleModal();
        loadRules();
    } catch (error) {
        showToast('保存失败: ' + error.message, 'error');
    }
}

async function editRule(id) {
    const rule = AdminState.rules.find(r => r.id === id);
    if (rule) openRuleModal(rule);
}

async function toggleRule(id) {
    try {
        await fetchDBTAdmin(`/rules/${id}/toggle`, { method: 'POST' });
        showToast('状态已切换');
        loadRules();
    } catch (error) {
        showToast('操作失败: ' + error.message, 'error');
    }
}

async function deleteRule(id) {
    if (!confirm('确定要删除此规则吗？')) return;
    try {
        await fetchDBTAdmin(`/rules/${id}`, { method: 'DELETE' });
        showToast('规则已删除');
        loadRules();
    } catch (error) {
        showToast('删除失败: ' + error.message, 'error');
    }
}

// ==================== Profiles Management ====================
async function loadProfiles() {
    try {
        const profiles = await fetchProfileAPI('/profiles');
        AdminState.profiles = profiles;
        renderProfilesList(profiles);
    } catch (error) {
        console.error('Failed to load profiles:', error);
        document.getElementById('profiles-list').innerHTML =
            '<div class="col-span-full text-center py-8 text-red-500">加载失败: ' + error.message + '</div>';
    }
}

function renderProfilesList(profiles) {
    const container = document.getElementById('profiles-list');
    if (!profiles.length) {
        container.innerHTML = '<div class="col-span-full text-center py-8 text-gray-500 dark:text-gray-400">暂无用户画像数据</div>';
        return;
    }

    container.innerHTML = profiles.map(profile => `
        <div class="bg-white dark:bg-slate-800 rounded-2xl p-5 shadow-sm hover:shadow-md transition-shadow cursor-pointer" onclick="viewProfile('${escapeHtml(profile.user_id)}')">
            <div class="flex items-center gap-3 mb-4">
                <div class="w-12 h-12 rounded-full gradient-bg flex items-center justify-center text-white font-medium text-lg">
                    ${(profile.user_id || 'U')[0].toUpperCase()}
                </div>
                <div class="flex-1 min-w-0">
                    <p class="font-medium text-gray-900 dark:text-white truncate">${escapeHtml(profile.user_id)}</p>
                    <p class="text-xs text-gray-500 dark:text-gray-400">创建: ${formatDate(profile.created_at)}</p>
                </div>
            </div>
            <div class="grid grid-cols-2 gap-3 text-sm">
                <div class="bg-gray-50 dark:bg-slate-700 rounded-lg p-2">
                    <p class="text-gray-500 dark:text-gray-400 text-xs">互动次数</p>
                    <p class="font-semibold text-gray-900 dark:text-white">${profile.total_interactions || 0}</p>
                </div>
                <div class="bg-gray-50 dark:bg-slate-700 rounded-lg p-2">
                    <p class="text-gray-500 dark:text-gray-400 text-xs">干预次数</p>
                    <p class="font-semibold text-gray-900 dark:text-white">${profile.intervention_count || 0}</p>
                </div>
            </div>
        </div>
    `).join('');
}

function filterProfiles() {
    const search = document.getElementById('profiles-search').value.toLowerCase();
    const filtered = AdminState.profiles.filter(p => !search || p.user_id.toLowerCase().includes(search));
    renderProfilesList(filtered);
}

async function viewProfile(userId) {
    try {
        const profile = await fetchProfileAPI(`/profiles/${encodeURIComponent(userId)}`);
        renderProfileDetail(profile);
        document.getElementById('profile-modal').classList.remove('hidden');
    } catch (error) {
        showToast('加载用户画像失败: ' + error.message, 'error');
    }
}

function renderProfileDetail(profile) {
    const container = document.getElementById('profile-detail-content');
    const emotions = profile.emotion_baseline || {};
    const personality = profile.personality || {};
    const risk = profile.risk_prediction || {};

    container.innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div class="bg-gray-50 dark:bg-slate-700 rounded-xl p-4">
                <h4 class="font-medium text-gray-900 dark:text-white mb-2">基本信息</h4>
                <p class="text-sm text-gray-600 dark:text-gray-400">用户ID: ${escapeHtml(profile.user_id)}</p>
                <p class="text-sm text-gray-600 dark:text-gray-400">创建时间: ${formatDate(profile.created_at)}</p>
                <p class="text-sm text-gray-600 dark:text-gray-400">更新时间: ${formatDate(profile.updated_at)}</p>
            </div>
            <div class="bg-gray-50 dark:bg-slate-700 rounded-xl p-4">
                <h4 class="font-medium text-gray-900 dark:text-white mb-2">互动统计</h4>
                <p class="text-sm text-gray-600 dark:text-gray-400">总互动: ${profile.total_interactions || 0} 次</p>
                <p class="text-sm text-gray-600 dark:text-gray-400">危机次数: ${profile.crisis_count || 0} 次</p>
                <p class="text-sm text-gray-600 dark:text-gray-400">干预次数: ${profile.intervention_count || 0} 次</p>
            </div>
            <div class="bg-gray-50 dark:bg-slate-700 rounded-xl p-4">
                <h4 class="font-medium text-gray-900 dark:text-white mb-2">风险评估</h4>
                <p class="text-sm text-gray-600 dark:text-gray-400">危机概率: ${((risk.next_crisis_probability || 0) * 100).toFixed(1)}%</p>
                <p class="text-sm text-gray-600 dark:text-gray-400">数据质量: ${((profile.data_quality_score || 0) * 100).toFixed(1)}%</p>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div class="bg-gray-50 dark:bg-slate-700 rounded-xl p-4">
                <h4 class="font-medium text-gray-900 dark:text-white mb-3">情绪基准线</h4>
                <div class="space-y-2">
                    ${Object.entries(emotions).map(([emotion, value]) => `
                        <div class="flex items-center gap-2">
                            <span class="text-sm text-gray-600 dark:text-gray-400 w-16">${emotion}</span>
                            <div class="flex-1 bg-gray-200 dark:bg-slate-600 rounded-full h-2">
                                <div class="bg-indigo-500 h-2 rounded-full" style="width: ${(value * 100).toFixed(0)}%"></div>
                            </div>
                            <span class="text-xs text-gray-500 w-10">${(value * 100).toFixed(0)}%</span>
                        </div>
                    `).join('') || '<p class="text-sm text-gray-500">暂无数据</p>'}
                </div>
            </div>
            <div class="bg-gray-50 dark:bg-slate-700 rounded-xl p-4">
                <h4 class="font-medium text-gray-900 dark:text-white mb-3">性格画像 (大五人格)</h4>
                <div class="space-y-2">
                    ${[
                        ['开放性', personality.openness],
                        ['尽责性', personality.conscientiousness],
                        ['外向性', personality.extraversion],
                        ['宜人性', personality.agreeableness],
                        ['神经质', personality.neuroticism]
                    ].map(([name, value]) => `
                        <div class="flex items-center gap-2">
                            <span class="text-sm text-gray-600 dark:text-gray-400 w-16">${name}</span>
                            <div class="flex-1 bg-gray-200 dark:bg-slate-600 rounded-full h-2">
                                <div class="bg-pink-500 h-2 rounded-full" style="width: ${((value || 0.5) * 100).toFixed(0)}%"></div>
                            </div>
                            <span class="text-xs text-gray-500 w-10">${((value || 0.5) * 100).toFixed(0)}%</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
}

function closeProfileModal() {
    document.getElementById('profile-modal').classList.add('hidden');
}

// ==================== Users Management ====================
async function fetchAdminAPI(endpoint, options = {}) {
    const response = await Auth.fetch(`${API_BASE}/api/admin${endpoint}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        }
    });
    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || `HTTP ${response.status}`);
    }
    return response.json();
}

async function loadUsers() {
    try {
        const users = await fetchAdminAPI('/users');
        AdminState.users = users;
        renderUsersTable(users);
    } catch (error) {
        console.error('Failed to load users:', error);
        document.getElementById('users-table-body').innerHTML =
            '<tr><td colspan="7" class="px-6 py-8 text-center text-red-500">加载失败: ' + error.message + '</td></tr>';
    }
}

function renderUsersTable(users) {
    const tbody = document.getElementById('users-table-body');
    if (!users.length) {
        tbody.innerHTML = '<tr><td colspan="7" class="px-6 py-8 text-center text-gray-500 dark:text-gray-400">暂无用户数据</td></tr>';
        return;
    }

    const roleLabels = { admin: '管理员', member: '会员', user: '普通用户' };
    const roleColors = {
        admin: 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400',
        member: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
        user: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
    };

    tbody.innerHTML = users.map(user => `
        <tr class="hover:bg-gray-50 dark:hover:bg-slate-700/50">
            <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">${user.id}</td>
            <td class="px-6 py-4 text-sm text-gray-900 dark:text-white">${escapeHtml(user.email)}</td>
            <td class="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">${escapeHtml(user.username || '-')}</td>
            <td class="px-6 py-4">
                <span class="px-2 py-1 text-xs rounded-full ${roleColors[user.role] || roleColors.user}">
                    ${roleLabels[user.role] || user.role}
                </span>
            </td>
            <td class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                ${user.role === 'admin' || user.role === 'member' ? '不限' : `${user.daily_used || 0}/${user.daily_quota || 50}`}
            </td>
            <td class="px-6 py-4">
                <span class="px-2 py-1 text-xs rounded-full ${user.is_active ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400'}">
                    ${user.is_active ? '启用' : '禁用'}
                </span>
            </td>
            <td class="px-6 py-4">
                <div class="flex items-center gap-2">
                    <button onclick="editUser(${user.id})" class="p-1.5 hover:bg-gray-100 dark:hover:bg-slate-600 rounded-lg" title="编辑">
                        <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path></svg>
                    </button>
                    <button onclick="toggleUserStatus(${user.id})" class="p-1.5 hover:bg-gray-100 dark:hover:bg-slate-600 rounded-lg" title="${user.is_active ? '禁用' : '启用'}">
                        <svg class="w-4 h-4 ${user.is_active ? 'text-yellow-500' : 'text-green-500'}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${user.is_active ? 'M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636' : 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z'}"></path></svg>
                    </button>
                    <button onclick="deleteUser(${user.id})" class="p-1.5 hover:bg-gray-100 dark:hover:bg-slate-600 rounded-lg" title="删除">
                        <svg class="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

function filterUsers() {
    const search = document.getElementById('users-search').value.toLowerCase();
    const role = document.getElementById('users-role-filter').value;

    const filtered = AdminState.users.filter(user => {
        const matchSearch = !search ||
            user.email.toLowerCase().includes(search) ||
            (user.username || '').toLowerCase().includes(search);
        const matchRole = !role || user.role === role;
        return matchSearch && matchRole;
    });

    renderUsersTable(filtered);
}

function openUserModal(user = null) {
    document.getElementById('user-modal-title').textContent = user ? '编辑用户' : '新建用户';
    document.getElementById('user-edit-id').value = user?.id || '';
    document.getElementById('user-email-input').value = user?.email || '';
    document.getElementById('user-username-input').value = user?.username || '';
    document.getElementById('user-password-input').value = '';
    document.getElementById('user-role-input').value = user?.role || 'user';
    document.getElementById('user-quota-input').value = user?.daily_quota || 50;
    document.getElementById('user-active-input').checked = user?.is_active !== false;

    // Password is required only for new users
    document.getElementById('user-password-input').required = !user;

    document.getElementById('user-modal').classList.remove('hidden');
}

function closeUserModal() {
    document.getElementById('user-modal').classList.add('hidden');
}

async function saveUser(event) {
    event.preventDefault();
    const id = document.getElementById('user-edit-id').value;
    const data = {
        email: document.getElementById('user-email-input').value,
        username: document.getElementById('user-username-input').value,
        role: document.getElementById('user-role-input').value,
        daily_quota: parseInt(document.getElementById('user-quota-input').value),
        is_active: document.getElementById('user-active-input').checked
    };

    const password = document.getElementById('user-password-input').value;
    if (password) {
        data.password = password;
    }

    try {
        if (id) {
            await fetchAdminAPI(`/users/${id}`, { method: 'PUT', body: JSON.stringify(data) });
            showToast('用户更新成功');
        } else {
            if (!password) {
                showToast('请输入密码', 'error');
                return;
            }
            await fetchAdminAPI('/users', { method: 'POST', body: JSON.stringify(data) });
            showToast('用户创建成功');
        }
        closeUserModal();
        loadUsers();
    } catch (error) {
        showToast('保存失败: ' + error.message, 'error');
    }
}

async function editUser(id) {
    const user = AdminState.users.find(u => u.id === id);
    if (user) openUserModal(user);
}

async function toggleUserStatus(id) {
    const user = AdminState.users.find(u => u.id === id);
    if (!user) return;

    try {
        await fetchAdminAPI(`/users/${id}`, {
            method: 'PUT',
            body: JSON.stringify({ is_active: !user.is_active })
        });
        showToast('状态已切换');
        loadUsers();
    } catch (error) {
        showToast('操作失败: ' + error.message, 'error');
    }
}

async function deleteUser(id) {
    if (!confirm('确定要删除此用户吗？此操作不可恢复。')) return;
    try {
        await fetchAdminAPI(`/users/${id}`, { method: 'DELETE' });
        showToast('用户已删除');
        loadUsers();
    } catch (error) {
        showToast('删除失败: ' + error.message, 'error');
    }
}

// ==================== Utility Functions ====================
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    try {
        return new Date(dateStr).toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
    } catch {
        return dateStr;
    }
}

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `fixed bottom-4 right-4 px-4 py-3 rounded-xl shadow-lg z-50 transition-all transform translate-y-0 ${
        type === 'error' ? 'bg-red-500 text-white' : 'bg-green-500 text-white'
    }`;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-y-2');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
