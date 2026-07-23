// ============================================
// API CONFIG
// ============================================
const API_BASE = 'http://localhost:5000/api';

class ApiService {
    constructor() {
        this.token = localStorage.getItem('token');
    }

    getHeaders() {
        const headers = { 'Content-Type': 'application/json' };
        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`;
        }
        return headers;
    }

    async request(endpoint, method = 'GET', data = null) {
        const options = { method, headers: this.getHeaders() };
        if (data) options.body = JSON.stringify(data);

        try {
            const res = await fetch(`${API_BASE}${endpoint}`, options);
            return await res.json();
        } catch (error) {
            return { success: false, message: error.message };
        }
    }

    // ===== AUTH =====
    async register(username, password, fullname, email) {
        return this.request('/auth/register', 'POST', { username, password, fullname, email });
    }

    async login(username, password) {
        const result = await this.request('/auth/login', 'POST', { username, password });
        if (result.success) {
            this.token = result.token;
            localStorage.setItem('token', result.token);
            localStorage.setItem('user', JSON.stringify(result.user));
        }
        return result;
    }

    logout() {
        this.token = null;
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = 'login.html';
    }

    getCurrentUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    }

    // ===== WALLET =====
    async getWallet(username) {
        return this.request(`/wallet/${username}`);
    }

    async deposit(username, amount) {
        return this.request('/wallet/deposit', 'POST', { username, amount });
    }

    // ===== NFT =====
    async mintNFT(username, name, description, price, item_id, image_url) {
        return this.request('/nft/mint', 'POST', { username, name, description, price, item_id, image_url });
    }

    async getAllNFTs() {
        return this.request('/nft/all');
    }

    async getAvailableNFTs() {
        return this.request('/nft/list');
    }

    async getUserNFTs(username) {
        return this.request(`/nft/user/${username}`);
    }

    async getNFTById(nftId) {
        return this.request(`/nft/${nftId}`);
    }

    // ===== RENTAL =====
    async createRental(username, nft_id, days, character_id) {
        return this.request('/rental/create', 'POST', { username, nft_id, days, character_id });
    }

    async returnRental(rentalId) {
        return this.request(`/rental/return/${rentalId}`, 'POST');
    }

    async getUserRentals(username) {
        return this.request(`/rental/user/${username}`);
    }

    // ===== GAME =====
    async getGames(username) {
        return this.request(`/games?username=${username}`);
    }

    async getAllGames() {
        return this.request('/games/all');
    }

    async getCharactersByGame(gameId) {
        return this.request(`/games/${gameId}/characters`);
    }

    async getItemsByCharacter(characterId) {
        return this.request(`/characters/${characterId}/items`);
    }

    async checkCompatibility(characterId, itemId) {
        return this.request(`/characters/${characterId}/compatibility/${itemId}`);
    }
}

const api = new ApiService();

// ===== TOAST =====
function showToast(message, type = 'success') {
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    const toast = document.createElement('div');
    toast.className = `toast-item ${type}`;
    toast.innerHTML = `<span>${message}</span>`;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// ===== CHECK AUTH =====
function checkAuth() {
    return !!localStorage.getItem('token');
}

function requireAuth() {
    if (!checkAuth()) {
        window.location.href = 'login.html';
        return false;
    }
    return true;
}