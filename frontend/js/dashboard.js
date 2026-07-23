import { api, showToast, formatAddress, requireAuth } from './api.js';

// =========================================
// CHECK AUTH
// =========================================
if (!requireAuth()) {
    throw new Error('Unauthorized');
}

// =========================================
// DOM ELEMENTS
// =========================================
const user = api.getCurrentUser();

// Sidebar user info
document.querySelector('.user-info strong').textContent = user.fullname;
document.querySelector('.avatar').textContent = user.fullname.charAt(0);

// Topbar
document.querySelector('.page-title h1').textContent = 'Dashboard';
document.querySelector('.page-title p').textContent =
    `Welcome back, ${user.fullname}. Here's your marketplace overview.`;

// Wallet balance
document.querySelector('.wallet-balance strong').innerHTML =
    `0.00 <small>COINS</small>`;

// =========================================
// LOAD DATA
// =========================================
async function loadDashboard() {
    try {
        // Get wallet
        const walletResult = await api.getWallet(user.username);
        if (walletResult.success) {
            const balance = walletResult.wallet.balance || 0;
            document.querySelector('.wallet-balance strong').innerHTML =
                `${balance.toFixed(2)} <small>COINS</small>`;

            // Update stats
            document.querySelectorAll('.stat-card h3')[0].innerHTML =
                `${balance.toFixed(2)} <small>COINS</small>`;
        }

        // Get user NFTs
        const nftsResult = await api.getUserNFTs(user.username);
        if (nftsResult.success) {
            document.querySelectorAll('.stat-card h3')[1].textContent =
                nftsResult.nfts.length;
        }

        // Get user rentals
        const rentalsResult = await api.getUserRentals(user.username);
        if (rentalsResult.success) {
            const activeRentals = rentalsResult.rentals.filter(
                r => r.status === 'active'
            );
            document.querySelectorAll('.stat-card h3')[2].textContent =
                activeRentals.length;

            // Update activity list
            renderActivity(rentalsResult.rentals.slice(0, 4));
        }

        // Get all NFTs for featured
        const allNFTs = await api.getAvailableNFTs();
        if (allNFTs.success) {
            renderFeaturedNFTs(allNFTs.nfts.slice(0, 3));
        }

    } catch (error) {
        console.error('Error loading dashboard:', error);
        showToast('Không thể tải dữ liệu', 'error');
    }
}

// =========================================
// RENDER ACTIVITY
// =========================================
function renderActivity(rentals) {
    const activityList = document.querySelector('.activity-list');
    if (!activityList) return;

    if (!rentals || rentals.length === 0) {
        activityList.innerHTML = `
            <div style="text-align:center;padding:30px;color:var(--text-muted);">
                <i class="fa-solid fa-inbox" style="font-size:24px;"></i>
                <p style="margin-top:8px;">Chưa có hoạt động nào</p>
            </div>
        `;
        return;
    }

    const icons = {
        'active': 'fa-handshake',
        'pending': 'fa-clock',
        'completed': 'fa-check',
        'cancelled': 'fa-times'
    };

    const iconClasses = {
        'active': 'transaction',
        'pending': 'mining',
        'completed': 'return',
        'cancelled': 'return'
    };

    activityList.innerHTML = rentals.map(rental => {
        const status = rental.status || 'pending';
        const icon = icons[status] || 'fa-circle';
        const iconClass = iconClasses[status] || 'transaction';
        const time = new Date(rental.created_at).toLocaleString('vi-VN');

        return `
            <div class="activity-item">
                <div class="activity-icon ${iconClass}">
                    <i class="fa-solid ${icon}"></i>
                </div>
                <div class="activity-info">
                    <strong>Rental #${rental.nft_id.slice(0, 8)}</strong>
                    <span>${status.toUpperCase()} • ${time}</span>
                </div>
                <div class="activity-amount neutral">
                    ${rental.total_price || 0} COINS
                </div>
            </div>
        `;
    }).join('');
}

// =========================================
// RENDER FEATURED NFTS
// =========================================
function renderFeaturedNFTs(nfts) {
    const grid = document.querySelector('.nft-grid');
    if (!grid) return;

    if (!nfts || nfts.length === 0) {
        grid.innerHTML = `
            <div style="grid-column:1/-1;text-align:center;padding:40px;color:var(--text-muted);">
                <i class="fa-solid fa-image" style="font-size:32px;"></i>
                <p style="margin-top:8px;">Chưa có NFT nào</p>
            </div>
        `;
        return;
    }

    const images = ['dragon', 'shield', 'dragon-alt'];
    const symbols = ['fa-dragon', 'fa-shield-halved', 'fa-wand-magic-sparkles'];

    grid.innerHTML = nfts.map((nft, index) => {
        const imgClass = images[index % images.length];
        const symbol = symbols[index % symbols.length];
        const status = nft.status || 'available';
        const isAvailable = status === 'available';

        return `
            <div class="nft-card">
                <div class="nft-image ${imgClass}">
                    <span class="nft-category">GAME ITEM</span>
                    <button class="favorite-button">
                        <i class="fa-regular fa-heart"></i>
                    </button>
                    <div class="nft-symbol">
                        <i class="fa-solid ${symbol}"></i>
                    </div>
                </div>
                <div class="nft-info">
                    <div class="nft-title-row">
                        <div>
                            <h3>${nft.name || 'Unnamed NFT'}</h3>
                            <span>${nft.description || 'No description'}</span>
                        </div>
                        <span class="availability ${isAvailable ? '' : 'rented'}">
                            <i></i>
                            ${isAvailable ? 'Available' : 'Rented'}
                        </span>
                    </div>
                    <div class="nft-details">
                        <div>
                            <span>Rental Price</span>
                            <strong>${nft.price || 0} <small>COINS / DAY</small></strong>
                        </div>
                        <div>
                            <span>Deposit</span>
                            <strong>${(nft.price || 0) * 0.2} <small>COINS</small></strong>
                        </div>
                    </div>
                    <button class="rent-button ${isAvailable ? '' : 'disabled'}">
                        ${isAvailable ? 'View Details' : 'Currently Rented'}
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

// =========================================
// LOGOUT
// =========================================
document.querySelector('.nav-item.logout')?.addEventListener('click', (e) => {
    e.preventDefault();
    api.logout();
});

// =========================================
// SIDEBAR TOGGLE (Mobile)
// =========================================
document.querySelector('.mobile-menu')?.addEventListener('click', () => {
    document.querySelector('.sidebar').classList.toggle('open');
});

// =========================================
// INIT
// =========================================
loadDashboard();

// Auto refresh every 30s
setInterval(loadDashboard, 30000);