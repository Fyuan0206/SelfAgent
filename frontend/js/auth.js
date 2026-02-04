/**
 * Self-Agent Authentication Module
 * JWT Token management and API authentication
 */

const Auth = {
    // API endpoints
    API_BASE: window.location.origin,

    // Storage keys
    TOKEN_KEY: 'selfagent_token',
    USER_KEY: 'selfagent_user',

    /**
     * Register a new user
     * @param {string} email - User email
     * @param {string} username - Username
     * @param {string} password - Password (min 6 chars)
     * @returns {Promise<object>} User data with token
     */
    async register(email, username, password) {
        const response = await fetch(`${this.API_BASE}/api/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, username, password })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || '注册失败');
        }

        // Store token and user info
        this.setToken(data.access_token);
        this.setUser(data.user);

        return data;
    },

    /**
     * Login with email and password
     * @param {string} email - User email
     * @param {string} password - Password
     * @returns {Promise<object>} User data with token
     */
    async login(email, password) {
        const response = await fetch(`${this.API_BASE}/api/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || '登录失败');
        }

        // Store token and user info
        this.setToken(data.access_token);
        this.setUser(data.user);

        return data;
    },

    /**
     * Logout - clear stored credentials
     */
    logout() {
        localStorage.removeItem(this.TOKEN_KEY);
        localStorage.removeItem(this.USER_KEY);
        // Redirect to login page
        window.location.href = 'login.html';
    },

    /**
     * Get current user info from API
     * @returns {Promise<object>} User details with quota
     */
    async getCurrentUser() {
        const token = this.getToken();
        if (!token) {
            throw new Error('未登录');
        }

        const response = await fetch(`${this.API_BASE}/api/auth/me`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                this.logout();
                throw new Error('登录已过期，请重新登录');
            }
            throw new Error('获取用户信息失败');
        }

        const data = await response.json();
        this.setUser(data);
        return data;
    },

    /**
     * Get user quota info
     * @returns {Promise<object>} Quota information
     */
    async getQuota() {
        const token = this.getToken();
        if (!token) {
            throw new Error('未登录');
        }

        const response = await fetch(`${this.API_BASE}/api/auth/quota`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('获取额度信息失败');
        }

        return await response.json();
    },

    /**
     * Check if user is logged in
     * @returns {boolean}
     */
    isLoggedIn() {
        return !!this.getToken();
    },

    /**
     * Check if current user is admin
     * @returns {boolean}
     */
    isAdmin() {
        const user = this.getUser();
        return user && user.role === 'admin';
    },

    /**
     * Get stored token
     * @returns {string|null}
     */
    getToken() {
        return localStorage.getItem(this.TOKEN_KEY);
    },

    /**
     * Set token in storage
     * @param {string} token
     */
    setToken(token) {
        localStorage.setItem(this.TOKEN_KEY, token);
    },

    /**
     * Get stored user info
     * @returns {object|null}
     */
    getUser() {
        const userStr = localStorage.getItem(this.USER_KEY);
        if (!userStr) return null;
        try {
            return JSON.parse(userStr);
        } catch {
            return null;
        }
    },

    /**
     * Set user info in storage
     * @param {object} user
     */
    setUser(user) {
        localStorage.setItem(this.USER_KEY, JSON.stringify(user));
    },

    /**
     * Get authorization headers for API requests
     * @returns {object} Headers object with Authorization
     */
    getAuthHeaders() {
        const token = this.getToken();
        return token ? { 'Authorization': `Bearer ${token}` } : {};
    },

    /**
     * Make authenticated API request
     * @param {string} url - API endpoint
     * @param {object} options - Fetch options
     * @returns {Promise<Response>}
     */
    async fetch(url, options = {}) {
        const token = this.getToken();

        const headers = {
            ...options.headers,
            ...(token ? { 'Authorization': `Bearer ${token}` } : {})
        };

        const response = await fetch(url, {
            ...options,
            headers
        });

        // Handle 401 Unauthorized
        if (response.status === 401) {
            this.logout();
            throw new Error('登录已过期，请重新登录');
        }

        return response;
    },

    /**
     * Require authentication - redirect to login if not logged in
     * Call this at the start of protected pages
     */
    requireAuth() {
        if (!this.isLoggedIn()) {
            window.location.href = 'login.html';
            return false;
        }
        return true;
    },

    /**
     * Require admin role - redirect if not admin
     */
    requireAdmin() {
        if (!this.isLoggedIn()) {
            window.location.href = 'login.html';
            return false;
        }
        if (!this.isAdmin()) {
            alert('需要管理员权限');
            window.location.href = 'index.html';
            return false;
        }
        return true;
    }
};

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Auth;
}
