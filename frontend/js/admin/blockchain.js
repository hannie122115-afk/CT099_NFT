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

// Cập nhật thông tin admin
document.getElementById('avatarLetter').textContent = user.fullname.charAt(0).toUpperCase();
document.getElementById('userName').textContent = user.fullname || user.username;

// Hàm lấy dữ liệu blockchain
async function loadBlockchain() {
    try {
        // Gọi API lấy blockchain
        const response = await fetch('http://localhost:5000/api/blockchain', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
        });
        const result = await response.json();
        
        if (result.success) {
            renderBlockchain(result.data);
        } else {
            // Nếu chưa có API, dùng dữ liệu mẫu
            renderSampleData();
        }
    } catch (error) {
        console.log('API chưa sẵn sàng, dùng dữ liệu mẫu');
        renderSampleData();
    }
}

// Hiển thị dữ liệu mẫu
function renderSampleData() {
    // Thống kê
    document.getElementById('totalBlocks').textContent = '3';
    document.getElementById('totalTransactions').textContent = '5';
    document.getElementById('pendingTransactions').textContent = '0';
    document.getElementById('difficulty').textContent = '4';

    // Danh sách khối mẫu
    const blocks = [
        {
            index: 0,
            hash: '0000a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6',
            previous_hash: '0',
            timestamp: new Date().toISOString(),
            transactions: [
                { sender: 'system', receiver: 'system', amount: 0, action: 'genesis' }
            ]
        },
        {
            index: 1,
            hash: '0000b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7',
            previous_hash: '0000a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6',
            timestamp: new Date(Date.now() - 3600000).toISOString(),
            transactions: [
                { sender: 'system', receiver: '0x1e30...0a64', amount: 100, action: 'deposit' },
                { sender: 'system', receiver: '0x1e30...0a64', amount: 10, action: 'mining_reward' }
            ]
        },
        {
            index: 2,
            hash: '0000c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8',
            previous_hash: '0000b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7',
            timestamp: new Date(Date.now() - 7200000).toISOString(),
            transactions: [
                { sender: '0x1e30...0a64', receiver: '0x2f41...1b75', amount: 50, action: 'transfer' }
            ]
        }
    ];

    document.getElementById('blockCount').textContent = `${blocks.length} khối`;
    renderBlocks(blocks);
}

// Hiển thị danh sách khối
function renderBlocks(blocks) {
    const container = document.getElementById('blockchainList');
    
    if (!blocks || blocks.length === 0) {
        container.innerHTML = `
            <div style="text-align:center;padding:30px;color:var(--text-muted);">
                <i class="fa-solid fa-cube" style="font-size:24px;"></i>
                <p style="margin-top:8px;">Chưa có khối nào</p>
            </div>
        `;
        return;
    }

    container.innerHTML = blocks.map(block => `
        <div class="block-detail">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
                <strong>Khối #${block.index}</strong>
                <span style="color:var(--text-muted);font-size:12px;">
                    ${new Date(block.timestamp).toLocaleString('vi-VN')}
                </span>
            </div>
            <div style="margin-top:6px;">
                <span style="color:var(--text-muted);">Hash:</span>
                <span class="hash">${block.hash}</span>
            </div>
            <div style="margin-top:4px;">
                <span style="color:var(--text-muted);">Hash trước:</span>
                <span class="hash" style="font-size:12px;color:var(--text-muted);">${block.previous_hash}</span>
            </div>
            <div class="transactions">
                <strong>Giao dịch (${block.transactions.length})</strong>
                ${block.transactions.map(tx => `
                    <div class="tx-item">
                        <span class="from">${tx.sender.slice(0, 10)}</span>
                        <i class="fa-solid fa-arrow-right" style="color:var(--text-muted);font-size:10px;"></i>
                        <span class="to">${tx.receiver.slice(0, 10)}</span>
                        <span class="amount">${tx.amount} COINS</span>
                        <span style="color:var(--text-muted);font-size:10px;margin-left:8px;">${tx.action}</span>
                    </div>
                `).join('')}
            </div>
        </div>
    `).join('');
}

// Đăng xuất
document.getElementById('logoutBtn').addEventListener('click', (e) => {
    e.preventDefault();
    api.logout();
    showToast('Đã đăng xuất', 'info');
    setTimeout(() => window.location.href = '../user/login.html', 500);
});

// Toggle sidebar mobile
document.querySelector('.mobile-menu')?.addEventListener('click', () => {
    document.querySelector('.sidebar').classList.toggle('open');
});

// Tải dữ liệu
loadBlockchain();
setInterval(loadBlockchain, 30000);