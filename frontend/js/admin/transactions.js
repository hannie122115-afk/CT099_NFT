import { api, showToast, requireAuth } from '../api.js';

if (!requireAuth()) {
    window.location.href = '../user/login.html';
    return;
}

const user = api.getCurrentUser();
if (!user || user.role !== 'admin') {
    window.location.href = '../user/dashboard.html';
    return;
}

document.getElementById('avatarLetter').textContent = user.fullname.charAt(0).toUpperCase();
document.getElementById('userName').textContent = user.fullname || user.username;

// Dữ liệu mẫu
const sampleTransactions = [
    { id: 'TX001', type: 'Nạp tiền', amount: 100, status: 'Hoàn thành', date: new Date().toLocaleString('vi-VN'), address: '0x1e30...0a64' },
    { id: 'TX002', type: 'Thuê NFT', amount: 70, status: 'Hoàn thành', date: new Date(Date.now() - 3600000).toLocaleString('vi-VN'), address: '0x2f41...1b75' },
    { id: 'TX003', type: 'Mining', amount: 50, status: 'Hoàn thành', date: new Date(Date.now() - 7200000).toLocaleString('vi-VN'), address: '0x1e30...0a64' },
    { id: 'TX004', type: 'Trả NFT', amount: 30, status: 'Đang xử lý', date: new Date(Date.now() - 10800000).toLocaleString('vi-VN'), address: '0x3g52...2c86' },
    { id: 'TX005', type: 'Mint NFT', amount: 0, status: 'Hoàn thành', date: new Date(Date.now() - 14400000).toLocaleString('vi-VN'), address: '0x1e30...0a64' },
];

async function loadTransactions() {
    try {
        // Thử gọi API
        const result = await api.adminGetAllRentals();
        if (result.success && result.rentals.length > 0) {
            document.getElementById('txCount').textContent = `${result.rentals.length} giao dịch`;
            renderTransactions(result.rentals);
        } else {
            // Dùng dữ liệu mẫu
            document.getElementById('txCount').textContent = `${sampleTransactions.length} giao dịch`;
            renderSampleTransactions();
        }
    } catch (error) {
        document.getElementById('txCount').textContent = `${sampleTransactions.length} giao dịch`;
        renderSampleTransactions();
    }
}

function renderSampleTransactions() {
    const container = document.getElementById('transactionsTable');
    
    const statusMap = {
        'Hoàn thành': 'badge-available',
        'Đang xử lý': 'badge-rented',
        'Thất bại': 'badge-disputed'
    };

    container.innerHTML = `
        <table class="admin-table">
            <thead>
                <tr>
                    <th>Mã GD</th>
                    <th>Loại</th>
                    <th>Địa chỉ</th>
                    <th>Số tiền</th>
                    <th>Trạng thái</th>
                    <th>Thời gian</th>
                </tr>
            </thead>
            <tbody>
                ${sampleTransactions.map(tx => `
                    <tr>
                        <td style="font-family:monospace;font-size:12px;font-weight:600;">${tx.id}</td>
                        <td>${tx.type}</td>
                        <td style="font-family:monospace;font-size:12px;">${tx.address}</td>
                        <td style="font-weight:600;color:${tx.amount > 0 ? 'var(--success)' : 'var(--text-muted)'};">${tx.amount > 0 ? `+${tx.amount}` : tx.amount} COINS</td>
                        <td><span class="badge-status ${statusMap[tx.status] || 'badge-expired'}">${tx.status}</span></td>
                        <td style="font-size:12px;color:var(--text-muted);">${tx.date}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

function renderTransactions(rentals) {
    const container = document.getElementById('transactionsTable');
    if (!rentals || rentals.length === 0) {
        container.innerHTML = `
            <div style="text-align:center;padding:30px;color:var(--text-muted);">
                <i class="fa-solid fa-list-ul" style="font-size:24px;"></i>
                <p style="margin-top:8px;">Chưa có giao dịch nào</p>
            </div>
        `;
        return;
    }

    const statusMap = {
        'active': 'badge-rented',
        'pending': 'badge-locked',
        'completed': 'badge-available',
        'cancelled': 'badge-disputed'
    };

    const statusText = {
        'active': 'Đang hoạt động',
        'pending': 'Chờ xử lý',
        'completed': 'Hoàn thành',
        'cancelled': 'Đã hủy'
    };

    container.innerHTML = `
        <table class="admin-table">
            <thead>
                <tr>
                    <th>Mã GD</th>
                    <th>NFT</th>
                    <th>Người thuê</th>
                    <th>Chủ sở hữu</th>
                    <th>Tổng tiền</th>
                    <th>Trạng thái</th>
                    <th>Thời gian</th>
                </tr>
            </thead>
            <tbody>
                ${rentals.map(r => `
                    <tr>
                        <td style="font-family:monospace;font-size:12px;font-weight:600;">${r.id.slice(0, 8)}...</td>
                        <td style="font-family:monospace;font-size:12px;">${r.nft_id.slice(0, 8)}...</td>
                        <td style="font-family:monospace;font-size:12px;">${r.renter_address ? r.renter_address.slice(0, 10) + '...' : '-'}</td>
                        <td style="font-family:monospace;font-size:12px;">${r.owner_address ? r.owner_address.slice(0, 10) + '...' : '-'}</td>
                        <td style="font-weight:600;color:var(--warning);">${r.total_price || 0} COINS</td>
                        <td><span class="badge-status ${statusMap[r.status] || 'badge-expired'}">${statusText[r.status] || r.status}</span></td>
                        <td style="font-size:12px;color:var(--text-muted);">${new Date(r.created_at).toLocaleString('vi-VN')}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
}

// Tìm kiếm
document.getElementById('searchInput')?.addEventListener('input', function() {
    const rows = document.querySelectorAll('#transactionsTable tbody tr');
    const keyword = this.value.toLowerCase().trim();
    rows.forEach(row => {
        row.style.display = row.textContent.toLowerCase().includes(keyword) ? '' : 'none';
    });
});

// Đăng xuất
document.getElementById('logoutBtn').addEventListener('click', (e) => {
    e.preventDefault();
    api.logout();
    showToast('Đã đăng xuất', 'info');
    setTimeout(() => window.location.href = '../user/login.html', 500);
});

document.querySelector('.mobile-menu')?.addEventListener('click', () => {
    document.querySelector('.sidebar').classList.toggle('open');
});

loadTransactions();
setInterval(loadTransactions, 30000);