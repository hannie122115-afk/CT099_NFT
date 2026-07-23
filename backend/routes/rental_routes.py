from flask import request, jsonify
from models.hopdong_model import HopDong
from models.vatpham_model import VatPham
from models.nft_model import NFT
from models.nguoidung_model import NguoiDung
from models.giaodich_model import GiaoDich
from models.danhgia_model import DanhGia
from models.wallet_model import Wallet
from models.nhanvat_model import NhanVat
from config import Config
import datetime
import jwt
from functools import wraps

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'success': False, 'message': 'Vui lòng đăng nhập'}), 401
        try:
            if token.startswith('Bearer '):
                token = token.split(' ')[1]
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            current_user = NguoiDung.find_by_ten_nguoi_dung(data.get('ten_nguoi_dung'))
            if not current_user:
                return jsonify({'success': False, 'message': 'Người dùng không tồn tại'}), 401
        except:
            return jsonify({'success': False, 'message': 'Token không hợp lệ'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

def rental_routes(app):
    
    # ============================================================
    # TẠO HỢP ĐỒNG THUÊ (HỖ TRỢ THUÊ THEO GIỜ)
    # ============================================================
    @app.route('/api/rentals/create', methods=['POST'])
    @token_required
    def create_rental(current_user):
        data = request.get_json()
        required = ['ma_bai_dang']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'message': f'Thiếu {field}'}), 400
        
        item = VatPham.find_by_ma(data['ma_bai_dang'])
        if not item:
            return jsonify({'success': False, 'message': 'Vật phẩm không tồn tại'}), 404
        
        if item['trang_thai_thue'] != 'còn trống':
            return jsonify({'success': False, 'message': 'Vật phẩm đang được thuê'}), 400
        
        don_vi = item.get('don_vi_thue', 'ngay')
        
        # Xác định thời gian thuê
        if don_vi == 'gio':
            so_gio = data.get('so_gio', 1)
            if so_gio <= 0:
                return jsonify({'success': False, 'message': 'Số giờ không hợp lệ'}), 400
            max_gio = item['thoi_gian_thue_toi_da'] * 24
            if so_gio > max_gio:
                return jsonify({'success': False, 'message': f'Vượt quá thời gian thuê tối đa ({max_gio} giờ)'}), 400
            
            tong_tien = item['gia_thue'] * (so_gio / 24)
            end_date = datetime.datetime.utcnow() + datetime.timedelta(hours=so_gio)
            so_ngay_thue = so_gio / 24
            
        else:  # 'ngay' hoặc 'tuan'
            so_ngay = data.get('so_ngay_thue', 1)
            if so_ngay <= 0:
                return jsonify({'success': False, 'message': 'Số ngày không hợp lệ'}), 400
            if so_ngay > item['thoi_gian_thue_toi_da']:
                return jsonify({'success': False, 'message': f'Vượt quá thời gian thuê tối đa ({item["thoi_gian_thue_toi_da"]} ngày)'}), 400
            
            tong_tien = item['gia_thue'] * so_ngay
            end_date = datetime.datetime.utcnow() + datetime.timedelta(days=so_ngay)
            so_ngay_thue = so_ngay
        
        tien_coc = item['tien_dat_coc']
        
        # Tính phí dịch vụ
        from config import Config
        phi_dich_vu = tong_tien * Config.PLATFORM_FEE_PERCENT / 100
        tong_thanh_toan = tong_tien + tien_coc + phi_dich_vu
        
        wallet = Wallet.find_by_address(current_user.dia_chi_vi)
        if not wallet:
            return jsonify({'success': False, 'message': 'Không tìm thấy ví'}), 404
        
        if wallet['so_du'] < tong_thanh_toan:
            return jsonify({'success': False, 'message': f'Số dư không đủ. Cần {tong_thanh_toan} COINS'}), 400
        
        start_date = datetime.datetime.utcnow()
        
        hopdong = HopDong(
            ma_bai_dang=data['ma_bai_dang'],
            ma_nguoi_thue=current_user.ma_nguoi_dung,
            thoi_gian_bat_dau=start_date,
            thoi_gian_ket_thuc=end_date,
            ma_nhan_vat=data.get('ma_nhan_vat')
        )
        hopdong.tong_tien = tong_tien
        hopdong.tien_coc = tien_coc
        hopdong.so_ngay_thue = so_ngay_thue
        hopdong.don_vi_thue = don_vi
        hopdong.phi_dich_vu = phi_dich_vu
        hopdong.save()
        

    
    # ============================================================
    # TRẢ NFT
    # ============================================================
    @app.route('/api/rentals/return/<ma_hop_dong>', methods=['POST'])
    @token_required
    def return_rental(current_user, ma_hop_dong):
        hopdong = HopDong.find_by_ma(ma_hop_dong)
        if not hopdong:
            return jsonify({'success': False, 'message': 'Hợp đồng không tồn tại'}), 404
        
        if hopdong['trang_thai_thue'] != 'dang_thue':
            return jsonify({'success': False, 'message': 'Hợp đồng không ở trạng thái đang thuê'}), 400
        
        if hopdong['ma_nguoi_thue'] != current_user.ma_nguoi_dung:
            return jsonify({'success': False, 'message': 'Bạn không phải người thuê'}), 403
        
        HopDong.update_status(ma_hop_dong, 'da_tra')
        
        item = VatPham.find_by_ma(hopdong['ma_bai_dang'])
        if item:
            VatPham.update_status(item['ma_vat_pham'], 'còn trống')
        
        nfts = NFT.find_by_vat_pham(item['ma_vat_pham']) if item else []
        if nfts:
            NFT.update_status(nfts[0]['ma_nft'], 'co_san')
        
        if item:
            wallet = Wallet.find_by_address(current_user.dia_chi_vi)
            if wallet:
                Wallet.update_balance(wallet['dia_chi'], wallet['so_du'] + item['tien_dat_coc'])
                
                giao_dich = GiaoDich(
                    ma_hop_dong=ma_hop_dong,
                    loai_giao_dich='hoan_tien_coc',
                    so_tien_giao_dich=item['tien_dat_coc'],
                    hinh_thuc_thanh_toan='ví'
                )
                giao_dich.save()
        
        return jsonify({'success': True, 'message': 'Đã trả vật phẩm thành công'}), 200
    
    # ============================================================
    # HỦY HỢP ĐỒNG TRƯỚC HẠN
    # ============================================================
    @app.route('/api/rentals/cancel/<ma_hop_dong>', methods=['POST'])
    @token_required
    def cancel_rental(current_user, ma_hop_dong):
        hopdong = HopDong.find_by_ma(ma_hop_dong)
        if not hopdong:
            return jsonify({'success': False, 'message': 'Hợp đồng không tồn tại'}), 404
        
        if hopdong['ma_nguoi_thue'] != current_user.ma_nguoi_dung:
            return jsonify({'success': False, 'message': 'Bạn không phải người thuê'}), 403
        
        if hopdong['trang_thai_thue'] != 'dang_thue':
            return jsonify({'success': False, 'message': 'Hợp đồng không ở trạng thái đang thuê'}), 400
        
        now = datetime.datetime.utcnow()  # SỬA: dùng utcnow() không timezone
        start = hopdong['thoi_gian_bat_dau']
        
        # Tính số ngày/giờ đã thuê
        don_vi = hopdong.get('don_vi_thue', 'ngay')
        if don_vi == 'gio':
            so_don_vi_da_thue = (now - start).total_seconds() / 3600
            if so_don_vi_da_thue < 1:
                so_don_vi_da_thue = 1
            so_don_vi_da_thue = int(so_don_vi_da_thue)
        else:
            so_don_vi_da_thue = (now - start).days + 1  # SỬA: now - start đã hoạt động
            if so_don_vi_da_thue < 1:
                so_don_vi_da_thue = 1
        
        item = VatPham.find_by_ma(hopdong['ma_bai_dang'])
        if not item:
            return jsonify({'success': False, 'message': 'Vật phẩm không tồn tại'}), 404
        
        # Tính tiền hoàn lại
        tong_tien = hopdong['tong_tien']
        if don_vi == 'gio':
            gia_moi_don_vi = item['gia_thue'] / 24
            tong_tien_da_dung = gia_moi_don_vi * so_don_vi_da_thue
        else:
            tong_tien_da_dung = item['gia_thue'] * so_don_vi_da_thue
        
        if tong_tien_da_dung > tong_tien:
            tong_tien_da_dung = tong_tien
        
        tien_thua = tong_tien - tong_tien_da_dung
        if tien_thua < 0:
            tien_thua = 0
        
        tien_hoan = tien_thua + hopdong['tien_coc']
        
        wallet = Wallet.find_by_address(current_user.dia_chi_vi)
        if wallet:
            Wallet.update_balance(wallet['dia_chi'], wallet['so_du'] + tien_hoan)
            
            nfts = NFT.find_by_vat_pham(item['ma_vat_pham'])
            if nfts:
                owner_wallet = Wallet.find_by_address(nfts[0]['dia_chi_chu_so_huu'])
                if owner_wallet:
                    Wallet.update_balance(owner_wallet['dia_chi'], owner_wallet['so_du'] - tong_tien_da_dung)
        
        HopDong.update_status(ma_hop_dong, 'da_huy')
        VatPham.update_status(item['ma_vat_pham'], 'còn trống')
        
        nfts = NFT.find_by_vat_pham(item['ma_vat_pham'])
        if nfts:
            NFT.update_status(nfts[0]['ma_nft'], 'co_san')
        
        giao_dich = GiaoDich(
            ma_hop_dong=ma_hop_dong,
            loai_giao_dich='hoan_tien_coc',
            so_tien_giao_dich=tien_hoan,
            hinh_thuc_thanh_toan='ví'
        )
        giao_dich.save()
        
        return jsonify({
            'success': True,
            'message': f'Đã hủy hợp đồng. Hoàn lại {tien_hoan} COINS',
            'tien_hoan': tien_hoan,
            'so_don_vi_da_dung': so_don_vi_da_thue
        }), 200
    
    # ============================================================
    # GIA HẠN HỢP ĐỒNG
    # ============================================================
    @app.route('/api/rentals/extend/<ma_hop_dong>', methods=['POST'])
    @token_required
    def extend_rental(current_user, ma_hop_dong):
        data = request.get_json()
        them_ngay = data.get('them_ngay', 0)
        
        if them_ngay <= 0:
            return jsonify({'success': False, 'message': 'Số ngày gia hạn không hợp lệ'}), 400
        
        hopdong = HopDong.find_by_ma(ma_hop_dong)
        if not hopdong:
            return jsonify({'success': False, 'message': 'Hợp đồng không tồn tại'}), 404
        
        if hopdong['ma_nguoi_thue'] != current_user.ma_nguoi_dung:
            return jsonify({'success': False, 'message': 'Bạn không phải người thuê'}), 403
        
        if hopdong['trang_thai_thue'] != 'dang_thue':
            return jsonify({'success': False, 'message': 'Hợp đồng không ở trạng thái đang thuê'}), 400
        
        item = VatPham.find_by_ma(hopdong['ma_bai_dang'])
        if not item:
            return jsonify({'success': False, 'message': 'Vật phẩm không tồn tại'}), 404
        
        tong_ngay = (hopdong['thoi_gian_ket_thuc'] - hopdong['thoi_gian_bat_dau']).days + them_ngay
        if tong_ngay > item['thoi_gian_thue_toi_da']:
            return jsonify({'success': False, 'message': f'Vượt quá số ngày thuê tối đa ({item["thoi_gian_thue_toi_da"]} ngày)'}), 400
        
        tien_gia_han = item['gia_thue'] * them_ngay
        
        wallet = Wallet.find_by_address(current_user.dia_chi_vi)
        if not wallet:
            return jsonify({'success': False, 'message': 'Không tìm thấy ví'}), 404
        
        if wallet['so_du'] < tien_gia_han:
            return jsonify({'success': False, 'message': f'Số dư không đủ. Cần {tien_gia_han} COINS'}), 400
        
        Wallet.update_balance(wallet['dia_chi'], wallet['so_du'] - tien_gia_han)
        
        nfts = NFT.find_by_vat_pham(item['ma_vat_pham'])
        if nfts:
            owner_wallet = Wallet.find_by_address(nfts[0]['dia_chi_chu_so_huu'])
            if owner_wallet:
                Wallet.update_balance(owner_wallet['dia_chi'], owner_wallet['so_du'] + tien_gia_han)
        
        new_end = hopdong['thoi_gian_ket_thuc'] + datetime.timedelta(days=them_ngay)
        from database.connection import hopdong_collection
        hopdong_collection.update_one(
            {'ma_hop_dong': ma_hop_dong},
            {
                '$set': {'thoi_gian_ket_thuc': new_end},
                '$inc': {'tong_tien': tien_gia_han}
            }
        )
        
        giao_dich = GiaoDich(
            ma_hop_dong=ma_hop_dong,
            loai_giao_dich='gia_han',
            so_tien_giao_dich=tien_gia_han,
            hinh_thuc_thanh_toan='ví'
        )
        giao_dich.save()
        
        return jsonify({
            'success': True,
            'message': f'Gia hạn thành công {them_ngay} ngày',
            'thoi_gian_ket_thuc_moi': new_end.isoformat()
        }), 200
    
    # ============================================================
    # LẤY DANH SÁCH HỢP ĐỒNG CỦA USER
    # ============================================================
    @app.route('/api/rentals/user/<ma_nguoi_thue>', methods=['GET'])
    def get_user_rentals(ma_nguoi_thue):
        rentals = HopDong.find_by_nguoi_thue(ma_nguoi_thue)
        
        for rental in rentals:
            nguoi_thue = NguoiDung.find_by_ma(rental['ma_nguoi_thue'])
            if nguoi_thue:
                rental['ten_nguoi_thue'] = nguoi_thue.ten_nguoi_dung
            
            item = VatPham.find_by_ma(rental['ma_bai_dang'])
            if item:
                rental['ten_vat_pham'] = item['ten_vat_pham']
                rental['mo_ta_vat_pham'] = item['mo_ta']
                rental['gia_thue_vat_pham'] = item['gia_thue']
                rental['tien_coc_vat_pham'] = item['tien_dat_coc']
                
                nfts = NFT.find_by_vat_pham(item['ma_vat_pham'])
                if nfts:
                    nft = nfts[0]
                    rental['ma_nft'] = nft['ma_nft']
                    rental['ten_nft'] = nft['ten']
                    rental['gia_thue_nft'] = nft['gia_thue']
                    rental['trang_thai_nft'] = nft['trang_thai']
                    
                    owner_wallet = Wallet.find_by_address(nft['dia_chi_chu_so_huu'])
                    if owner_wallet:
                        rental['ten_chu_so_huu_nft'] = owner_wallet.get('ten_nguoi_dung', 'Không rõ')
                    else:
                        rental['ten_chu_so_huu_nft'] = 'Không rõ'
        
        return jsonify({'success': True, 'rentals': rentals}), 200
    
    # ============================================================
    # CHI TIẾT HỢP ĐỒNG
    # ============================================================
    @app.route('/api/rentals/<ma_hop_dong>/detail', methods=['GET'])
    @token_required
    def get_rental_detail(current_user, ma_hop_dong):
        hopdong = HopDong.find_by_ma(ma_hop_dong)
        if not hopdong:
            return jsonify({'success': False, 'message': 'Hợp đồng không tồn tại'}), 404
        
        item = VatPham.find_by_ma(hopdong['ma_bai_dang'])
        
        nfts = []
        ten_chu_so_huu = None
        if item:
            nfts = NFT.find_by_vat_pham(item['ma_vat_pham'])
            if nfts:
                owner_wallet = Wallet.find_by_address(nfts[0]['dia_chi_chu_so_huu'])
                if owner_wallet:
                    ten_chu_so_huu = owner_wallet.get('ten_nguoi_dung', 'Không rõ')
        
        nguoi_thue = NguoiDung.find_by_ma(hopdong['ma_nguoi_thue'])
        
        nhan_vat = None
        if hopdong.get('ma_nhan_vat'):
            nhan_vat = NhanVat.find_by_ma(hopdong['ma_nhan_vat'])
        
        giao_dichs = GiaoDich.find_by_hop_dong(ma_hop_dong)
        danh_gia = DanhGia.find_by_hop_dong(ma_hop_dong)
        
        vat_pham_data = None
        if item:
            vat_pham_data = {
                'ten': item.get('ten_vat_pham', 'Không rõ'),
                'mo_ta': item.get('mo_ta', 'Không có mô tả'),
                'gia_thue': item.get('gia_thue', 0),
                'tien_coc': item.get('tien_dat_coc', 0),
                'loai': item.get('loai', 'Không rõ'),
                'trang_thai': item.get('trang_thai_thue', 'Không rõ')
            }
        
        return jsonify({
            'success': True,
            'hop_dong': hopdong,
            'vat_pham': vat_pham_data,
            'nft': nfts[0] if nfts else None,
            'ten_chu_so_huu': ten_chu_so_huu,
            'nguoi_thue': nguoi_thue.to_dict() if nguoi_thue else None,
            'nhan_vat': nhan_vat if nhan_vat else None,
            'giao_dich': giao_dichs,
            'danh_gia': danh_gia
        }), 200
    
    # ============================================================
    # ĐỀ XUẤT NHÂN VẬT PHÙ HỢP
    # ============================================================
    @app.route('/api/rentals/suggest-characters/<ma_vat_pham>', methods=['GET'])
    def suggest_characters(ma_vat_pham):
        item = VatPham.find_by_ma(ma_vat_pham)
        if not item:
            return jsonify({'success': False, 'message': 'Vật phẩm không tồn tại'}), 404
        
        if item.get('duoc_dung_cho'):
            character = NhanVat.find_by_ma(item['duoc_dung_cho'])
            if character:
                return jsonify({
                    'success': True,
                    'suggested': [character],
                    'message': f'Vật phẩm này chỉ dùng cho nhân vật {character["ten_nhan_vat"]}'
                }), 200
        
        characters = NhanVat.find_by_game(item['ma_game'])
        
        return jsonify({
            'success': True,
            'suggested': characters,
            'message': f'Đề xuất {len(characters)} nhân vật trong game'
        }), 200
    
    # ============================================================
    # ĐÁNH GIÁ HỢP ĐỒNG
    # ============================================================
    @app.route('/api/rentals/<ma_hop_dong>/review', methods=['POST'])
    @token_required
    def add_review(current_user, ma_hop_dong):
        data = request.get_json()
        so_sao = data.get('so_sao')
        noi_dung = data.get('noi_dung')
        
        if not so_sao or so_sao < 1 or so_sao > 5:
            return jsonify({'success': False, 'message': 'Số sao phải từ 1-5'}), 400
        
        hopdong = HopDong.find_by_ma(ma_hop_dong)
        if not hopdong:
            return jsonify({'success': False, 'message': 'Hợp đồng không tồn tại'}), 404
        
        if hopdong['trang_thai_thue'] != 'da_tra':
            return jsonify({'success': False, 'message': 'Chỉ có thể đánh giá sau khi đã trả NFT'}), 400
        
        existing = DanhGia.find_by_hop_dong(ma_hop_dong)
        if existing:
            return jsonify({'success': False, 'message': 'Đã đánh giá hợp đồng này'}), 400
        
        danhgia = DanhGia(
            ma_hop_dong=ma_hop_dong,
            noi_dung=noi_dung,
            so_sao=so_sao
        )
        danhgia.save()
        
        return jsonify({'success': True, 'message': 'Đánh giá thành công'}), 201