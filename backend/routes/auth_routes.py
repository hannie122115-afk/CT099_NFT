from flask import request, jsonify
from services.auth_service import AuthService

def auth_routes(app):
    
    @app.route('/api/auth/register', methods=['POST'])
    def register():
        data = request.get_json()
        required = ['ten_nguoi_dung', 'mat_khau', 'ho_ten', 'email']
        for field in required:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'message': f'Thiếu {field}'}), 400
        
        result = AuthService.register(
            ten_nguoi_dung=data['ten_nguoi_dung'].strip(),
            mat_khau=data['mat_khau'],
            ho_ten=data['ho_ten'].strip(),
            email=data['email'].strip(),
            so_dien_thoai=data.get('so_dien_thoai', '')
        )
        
        if result['success']:
            return jsonify(result), 201
        return jsonify(result), 400
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        data = request.get_json()
        if 'ten_nguoi_dung' not in data or 'mat_khau' not in data:
            return jsonify({'success': False, 'message': 'Thiếu tên đăng nhập hoặc mật khẩu'}), 400
        
        result = AuthService.login(data['ten_nguoi_dung'], data['mat_khau'])
        
        if result['success']:
            return jsonify(result), 200
        return jsonify(result), 401