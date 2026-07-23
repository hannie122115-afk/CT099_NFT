from flask import request, jsonify
from models.nguoidung_model import NguoiDung
from models.game_model import Game
from models.nhanvat_model import NhanVat
from models.vatpham_model import VatPham
from models.nft_model import NFT
from models.hopdong_model import HopDong
from models.giaodich_model import GiaoDich
from models.danhgia_model import DanhGia
from models.wallet_model import Wallet
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

def admin_routes(app):
    
    @app.route('/api/admin/users', methods=['GET'])
    @token_required
    def admin_get_users(current_user):
        if current_user.vai_tro != 'quan_tri':
            return jsonify({'success': False, 'message': 'Không có quyền'}), 403
        users = NguoiDung.find_all()
        return jsonify({'success': True, 'users': users}), 200
    
    @app.route('/api/admin/users/<ma_nguoi_dung>/toggle-role', methods=['PUT'])
    @token_required
    def admin_toggle_role(current_user, ma_nguoi_dung):
        if current_user.vai_tro != 'quan_tri':
            return jsonify({'success': False, 'message': 'Không có quyền'}), 403
        user = NguoiDung.find_by_ma(ma_nguoi_dung)
        if not user:
            return jsonify({'success': False, 'message': 'Người dùng không tồn tại'}), 404
        new_role = 'quan_tri' if user.vai_tro == 'nguoi_dung' else 'nguoi_dung'
        from database.connection import nguoidung_collection
        nguoidung_collection.update_one(
            {'ma_nguoi_dung': ma_nguoi_dung},
            {'$set': {'vai_tro': new_role}}
        )
        return jsonify({'success': True, 'message': f'Đã đổi vai trò thành {new_role}'}), 200
    
    @app.route('/api/admin/games', methods=['GET'])
    @token_required
    def admin_get_games(current_user):
        if current_user.vai_tro != 'quan_tri':
            return jsonify({'success': False, 'message': 'Không có quyền'}), 403
        games = Game.find_all()
        for game in games:
            characters = NhanVat.find_by_game(game['ma_game'])
            game['so_nhan_vat'] = len(characters)
        return jsonify({'success': True, 'games': games}), 200
    
    @app.route('/api/admin/games', methods=['POST'])
    @token_required
    def admin_create_game(current_user):
        if current_user.vai_tro != 'quan_tri':
            return jsonify({'success': False, 'message': 'Không có quyền'}), 403
        data = request.get_json()
        if not data.get('ten_game'):
            return jsonify({'success': False, 'message': 'Thiếu tên game'}), 400
        game = Game(
            ten_game=data['ten_game'],
            mo_ta_game=data.get('mo_ta_game', ''),
            nha_phat_hanh=data.get('nha_phat_hanh', '')
        )
        game.save()
        return jsonify({'success': True, 'game': game.to_dict()}), 201
    
    @app.route('/api/admin/games/<ma_game>', methods=['DELETE'])
    @token_required
    def admin_delete_game(current_user, ma_game):
        if current_user.vai_tro != 'quan_tri':
            return jsonify({'success': False, 'message': 'Không có quyền'}), 403
        from database.connection import game_collection
        result = game_collection.delete_one({'ma_game': ma_game})
        if result.deleted_count == 0:
            return jsonify({'success': False, 'message': 'Game không tồn tại'}), 404
        return jsonify({'success': True, 'message': 'Đã xóa game'}), 200
    
    @app.route('/api/admin/characters', methods=['GET'])
    @token_required
    def admin_get_characters(current_user):
        if current_user.vai_tro != 'quan_tri':
            return jsonify({'success': False, 'message': 'Không có quyền'}), 403
        characters = NhanVat.find_all()
        return jsonify({'success': True, 'characters': characters}), 200
    
    @app.route('/api/admin/characters', methods=['POST'])
    @token_required
    def admin_create_character(current_user):
        if current_user.vai_tro != 'quan_tri':
            return jsonify({'success': False, 'message': 'Không có quyền'}), 403
        data = request.get_json()
        if not data.get('ten_nhan_vat') or not data.get('ma_game'):
            return jsonify({'success': False, 'message': 'Thiếu tên nhân vật hoặc mã game'}), 400
        character = NhanVat(
            ten_nhan_vat=data['ten_nhan_vat'],
            ma_game=data['ma_game']
        )
        character.save()
        return jsonify({'success': True, 'character': character.to_dict()}), 201
    
    @app.route('/api/admin/characters/<ma_nhan_vat>', methods=['DELETE'])
    @token_required
    def admin_delete_character(current_user, ma_nhan_vat):
        if current_user.vai_tro != 'quan_tri':
            return jsonify({'success': False, 'message': 'Không có quyền'}), 403
        from database.connection import nhanvat_collection
        result = nhanvat_collection.delete_one({'ma_nhan_vat': ma_nhan_vat})
        if result.deleted_count == 0:
            return jsonify({'success': False, 'message': 'Nhân vật không tồn tại'}), 404
        return jsonify({'success': True, 'message': 'Đã xóa nhân vật'}), 200
    
    @app.route('/api/admin/items', methods=['GET'])
    @token_required
    def admin_get_items(current_user):
        if current_user.vai_tro != 'quan_tri':
            return jsonify({'success': False, 'message': 'Không có quyền'}), 403
        items = VatPham.find_all()
        return jsonify({'success': True, 'items': items}), 200
    
    @app.route('/api/admin/items/<ma_vat_pham>', methods=['DELETE'])
    @token_required
    def admin_delete_item(current_user, ma_vat_pham):
        if current_user.vai_tro != 'quan_tri':
            return jsonify({'success': False, 'message': 'Không có quyền'}), 403
        from database.connection import vatpham_collection
        result = vatpham_collection.delete_one({'ma_vat_pham': ma_vat_pham})
        if result.deleted_count == 0:
            return jsonify({'success': False, 'message': 'Vật phẩm không tồn tại'}), 404
        return jsonify({'success': True, 'message': 'Đã xóa vật phẩm'}), 200
    
    @app.route('/api/admin/rentals', methods=['GET'])
    @token_required
    def admin_get_rentals(current_user):
        if current_user.vai_tro != 'quan_tri':
            return jsonify({'success': False, 'message': 'Không có quyền'}), 403
        rentals = HopDong.find_all()
        for rental in rentals:
            nguoi_thue = NguoiDung.find_by_ma(rental['ma_nguoi_thue'])
            if nguoi_thue:
                rental['ten_nguoi_thue'] = nguoi_thue['ten_nguoi_dung']
            item = VatPham.find_by_ma(rental['ma_bai_dang'])
            if item:
                rental['ten_vat_pham'] = item['ten_vat_pham']
                nfts = NFT.find_by_vat_pham(item['ma_vat_pham'])
                if nfts:
                    owner = Wallet.find_by_address(nfts[0]['dia_chi_chu_so_huu'])
                    if owner:
                        rental['ten_chu_so_huu'] = owner['ten_nguoi_dung']
        return jsonify({'success': True, 'rentals': rentals}), 200
    
    @app.route('/api/admin/transactions', methods=['GET'])
    @token_required
    def admin_get_transactions(current_user):
        if current_user.vai_tro != 'quan_tri':
            return jsonify({'success': False, 'message': 'Không có quyền'}), 403
        transactions = GiaoDich.find_all()
        return jsonify({'success': True, 'transactions': transactions}), 200
    
    @app.route('/api/admin/stats', methods=['GET'])
    @token_required
    def admin_get_stats(current_user):
        if current_user.vai_tro != 'quan_tri':
            return jsonify({'success': False, 'message': 'Không có quyền'}), 403
        stats = {
            'total_users': len(NguoiDung.find_all()),
            'total_games': len(Game.find_all()),
            'total_characters': len(NhanVat.find_all()),
            'total_items': len(VatPham.find_all()),
            'total_nfts': len(NFT.find_all()),
            'total_rentals': len(HopDong.find_all()),
            'total_transactions': len(GiaoDich.find_all()),
            'total_reviews': len(DanhGia.find_all())
        }
        return jsonify({'success': True, 'stats': stats}), 200