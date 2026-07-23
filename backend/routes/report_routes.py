from flask import request, jsonify
from models.baocao_model import BaoCao
from models.hopdong_model import HopDong
from models.nguoidung_model import NguoiDung
from models.nft_model import NFT
from models.vatpham_model import VatPham
import jwt
from config import Config
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

def report_routes(app):
    
    @app.route('/api/reports/create', methods=['POST'])
    @token_required
    def create_report(current_user):
        data = request.get_json()
        required = ['ma_hop_dong', 'ly_do', 'noi_dung']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'message': f'Thiếu {field}'}), 400
        
        hopdong = HopDong.find_by_ma(data['ma_hop_dong'])
        if not hopdong:
            return jsonify({'success': False, 'message': 'Hợp đồng không tồn tại'}), 404
        
        # Kiểm tra người báo cáo có liên quan đến hợp đồng
        if hopdong['ma_nguoi_thue'] != current_user.ma_nguoi_dung:
            item = VatPham.find_by_ma(hopdong['ma_bai_dang'])
            if item:
                nfts = NFT.find_by_vat_pham(item['ma_vat_pham'])
                if nfts and nfts[0]['dia_chi_chu_so_huu'] != current_user.dia_chi_vi:
                    return jsonify({'success': False, 'message': 'Bạn không liên quan đến hợp đồng này'}), 403
        
        bao_cao = BaoCao(
            ma_hop_dong=data['ma_hop_dong'],
            nguoi_bao_cao=current_user.ma_nguoi_dung,
            ly_do=data['ly_do'],
            noi_dung=data['noi_dung']
        )
        bao_cao.save()
        
        return jsonify({
            'success': True,
            'message': 'Đã gửi báo cáo thành công',
            'bao_cao': bao_cao.to_dict()
        }), 201
    
    @app.route('/api/reports', methods=['GET'])
    @token_required
    def get_reports(current_user):
        """Lấy danh sách báo cáo (Admin only)"""
        if current_user.vai_tro != 'quan_tri':
            return jsonify({'success': False, 'message': 'Không có quyền'}), 403
        
        reports = BaoCao.find_all()
        return jsonify({'success': True, 'reports': reports}), 200
    
    @app.route('/api/reports/<ma_bao_cao>/status', methods=['PUT'])
    @token_required
    def update_report_status(current_user, ma_bao_cao):
        """Cập nhật trạng thái báo cáo (Admin only)"""
        if current_user.vai_tro != 'quan_tri':
            return jsonify({'success': False, 'message': 'Không có quyền'}), 403
        
        data = request.get_json()
        status = data.get('trang_thai')
        
        if status not in ['cho_xu_ly', 'dang_xu_ly', 'da_xu_ly']:
            return jsonify({'success': False, 'message': 'Trạng thái không hợp lệ'}), 400
        
        BaoCao.update_status(ma_bao_cao, status)
        return jsonify({'success': True, 'message': f'Đã cập nhật trạng thái thành {status}'}), 200