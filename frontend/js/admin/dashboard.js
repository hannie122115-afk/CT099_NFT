import { api, showToast, requireAuth } from '../api.js';

if (!requireAuth()) {
    window.location.href = '../user/login.html';
    throw new Error('Unauthorized');
}

const user = api.getCurrentUser();
if (!user || user.role !== 'admin') {
    window.location.href = '../user/dashboard.html';
    throw new Error('Access denied');
}

// Update user info
document.getElementById('avatarLetter').textContent = user.fullname.charAt(0).toUpperCase();
document.getElementById('userName').textContent = user.fullname || user.username;

async function loadAdminDashboard() {
    try {
        // Get stats
        const stats = await api.adminGetStats();
        if (stats.success) {
            document.getElementById('adminUsers').textContent = stats.totalUsers || 0;
            document.getElementById('adminNFTs').textContent = stats.totalNFTs || 0;
            document.getElementById('adminRentals').textContent = stats.totalRentals || 0;
            document.getElementById('adminVolume').textContent = stats.totalVolume || 0;
        }

        // Get recent rentals
        const rentals = await api.adminGetAllRentals();
        if (rentals.success) {
            renderAdminActivity(rentals.rentals.slice(0, 10));
        }

    } catch (error) {
        showToast('Không thể tải dữ liệu admin', 'error');
    }
}

function renderAdminActivity(rentals) {
    const container = document.getElementById('adminActivity');
    if (!rentals || rentals.length === 0) {
        container.innerHTML = `
            <div style="text-align:center;padding:30px;color:var(--text-muted);">
                <i class="fa-solid fa-inbox" style="font-size:24px;"></i>
                <p style="margin-top:8px;">Chưa có hoạt động nào</p>
            </div>
        `;
        return;
    }

    container.innerHTML = `
        <table class="admin-table">
            <thead>
                <tr>
                    <th>NFT</th>
                    <th>Renter</th>
                    <th>Amount</th>
                    <th>Status</th>
                    <th>Date</th>
                </tr>
            </thead>
            <tbody>
                ${rentals.map(r => `
                    <tr>
                        <td>#${r.nft_id.slice(0, 8)}</td>
                        <td>${r.renter_address.slice(0, 10)}...</td>
                        <td>${r.total_price || 0} COINS</td>
                        <td><span class="badge-status ${r.status === 'active' ? 'badge-rented' : r.status === 'completed' ? 'badge-available' : 'badge-expired'}">${r.status}</span></td>
                        <td>${new Date(r.created_at).toLocaleDateString()}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// Logout
document.getElementById('logoutBtn').addEventListener('click', (e) => {
    e.preventDefault();
    api.logout();
    showToast('Đã đăng xuất', 'info');
    setTimeout(() => window.location.href = '../user/login.html', 500);
});

// Mobile toggle
document.querySelector('.mobile-menu')?.addEventListener('click', () => {
    document.querySelector('.sidebar').classList.toggle('open');
});

loadAdminDashboard();
setInterval(loadAdminDashboard, 30000);