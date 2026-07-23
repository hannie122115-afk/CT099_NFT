from flask import request, jsonify
from models.nhanvat_model import NhanVat
from models.vatpham_model import VatPham
from models.nft_model import NFT
from models.wallet_model import Wallet

def character_routes(app):
    
    @app.route('/api/characters', methods=['POST'])
    def create_character():
        data = request.get_json()
        if not data.get('ten_nhan_vat') or not data.get('ma_game'):
            return jsonify({'success': False, 'message': 'Thiếu tên nhân vật hoặc mã game'}), 400
        
        character = NhanVat(
            ten_nhan_vat=data['ten_nhan_vat'],
            ma_game=data['ma_game']
        )
        character.save()
        
        return jsonify({'success': True, 'character': character.to_dict()}), 201
    
    @app.route('/api/characters/<ma_nhan_vat>', methods=['DELETE'])
    def delete_character(ma_nhan_vat):
        from database.connection import nhanvat_collection
        result = nhanvat_collection.delete_one({'ma_nhan_vat': ma_nhan_vat})
        if result.deleted_count == 0:
            return jsonify({'success': False, 'message': 'Nhân vật không tồn tại'}), 404
        return jsonify({'success': True, 'message': 'Đã xóa nhân vật'}), 200
    
    @app.route('/api/characters/<ma_nhan_vat>/items', methods=['GET'])
    def get_items_by_character(ma_nhan_vat):
        """Lấy danh sách vật phẩm mà nhân vật có thể sử dụng"""
        items = VatPham.find_by_character(ma_nhan_vat)
        
        # Thêm thông tin NFT cho từng vật phẩm
        for item in items:
            nfts = NFT.find_by_vat_pham(item['ma_vat_pham'])
            
            # Kiểm tra chính xác có NFT hay không
            item['has_nft'] = len(nfts) > 0
            
            if nfts:
                # Lấy NFT đầu tiên
                nft = nfts[0]
                item['nft'] = nft
                
                # Lấy tên chủ sở hữu từ ví
                wallet = Wallet.find_by_address(nft['dia_chi_chu_so_huu'])
                if wallet:
                    item['nft']['ten_chu_so_huu'] = wallet.get('ten_nguoi_dung', 'Không rõ')
                else:
                    item['nft']['ten_chu_so_huu'] = 'Không rõ'
            else:
                item['nft'] = None
        
        return jsonify({'success': True, 'items': items}), 200
    
    @app.route('/api/characters/all', methods=['GET'])
    def get_all_characters():
        """Lấy tất cả nhân vật"""
        characters = NhanVat.find_all()
        return jsonify({'success': True, 'characters': characters}), 200
    
    @app.route('/api/characters/<ma_nhan_vat>', methods=['GET'])
    def get_character(ma_nhan_vat):
        """Lấy thông tin một nhân vật"""
        character = NhanVat.find_by_ma(ma_nhan_vat)
        if not character:
            return jsonify({'success': False, 'message': 'Nhân vật không tồn tại'}), 404
        
        # Lấy số lượng vật phẩm
        items = VatPham.find_by_character(ma_nhan_vat)
        character['so_vat_pham'] = len(items)
        
        return jsonify({'success': True, 'character': character}), 200