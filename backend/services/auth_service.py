from models.nguoidung_model import NguoiDung
import logging

logger = logging.getLogger(__name__)

class AuthService:
    
    @staticmethod
    def register(ten_nguoi_dung, mat_khau, ho_ten, email, so_dien_thoai=''):
        try:
            if NguoiDung.find_by_ten_nguoi_dung(ten_nguoi_dung):
                return {'success': False, 'message': 'Tên đăng nhập đã tồn tại'}
            
            user = NguoiDung(ten_nguoi_dung, mat_khau, ho_ten, email, so_dien_thoai)
            user.save()
            
            return {
                'success': True,
                'message': 'Đăng ký thành công',
                'user': user.to_dict()
            }
        except Exception as e:
            logger.error(f"Register error: {e}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def login(ten_nguoi_dung, mat_khau):
        try:
            user = NguoiDung.find_by_ten_nguoi_dung(ten_nguoi_dung)
            if not user:
                return {'success': False, 'message': 'Người dùng không tồn tại'}
            
            if not user.check_password(mat_khau):
                return {'success': False, 'message': 'Mật khẩu không đúng'}
            
            token = user.generate_token()
            
            return {
                'success': True,
                'message': 'Đăng nhập thành công',
                'token': token,
                'user': user.to_dict()
            }
        except Exception as e:
            logger.error(f"Login error: {e}")
            return {'success': False, 'message': str(e)}