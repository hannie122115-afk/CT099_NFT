from database.connection import nguoidung_collection
import bcrypt
import jwt
import datetime
import uuid
from config import Config

class NguoiDung:
    def __init__(self, ten_nguoi_dung, mat_khau, ho_ten, email, so_dien_thoai='', vai_tro='nguoi_dung'):
        self.ma_nguoi_dung = str(uuid.uuid4())
        self.ten_nguoi_dung = ten_nguoi_dung
        self.ho_ten = ho_ten
        self.email = email
        self.so_dien_thoai = so_dien_thoai
        self.vai_tro = vai_tro
        self.dia_chi_vi = None
        
        if isinstance(mat_khau, str) and not mat_khau.startswith('$2b$'):
            self.mat_khau = self._hash_password(mat_khau)
        else:
            self.mat_khau = mat_khau
        
        self.created_at = datetime.datetime.now(datetime.timezone.utc)
    
    def _hash_password(self, password):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        if isinstance(self.mat_khau, str):
            stored = self.mat_khau.encode('utf-8')
        else:
            stored = self.mat_khau
        return bcrypt.checkpw(password.encode('utf-8'), stored)
    
    def generate_token(self):
        payload = {
            'ten_nguoi_dung': self.ten_nguoi_dung,
            'vai_tro': self.vai_tro,
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
        }
        return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')
    
    def to_dict(self):
        return {
            'ma_nguoi_dung': self.ma_nguoi_dung,
            'ten_nguoi_dung': self.ten_nguoi_dung,
            'ho_ten': self.ho_ten,
            'email': self.email,
            'so_dien_thoai': self.so_dien_thoai,
            'vai_tro': self.vai_tro,
            'dia_chi_vi': self.dia_chi_vi,
            'created_at': self.created_at
        }
    
    def save(self):
        nguoidung_collection.insert_one({
            'ma_nguoi_dung': self.ma_nguoi_dung,
            'ten_nguoi_dung': self.ten_nguoi_dung,
            'mat_khau': self.mat_khau,
            'ho_ten': self.ho_ten,
            'email': self.email,
            'so_dien_thoai': self.so_dien_thoai,
            'vai_tro': self.vai_tro,
            'dia_chi_vi': self.dia_chi_vi,
            'created_at': self.created_at
        })
        return self
    
    @staticmethod
    def find_by_ten_nguoi_dung(ten_nguoi_dung):
        data = nguoidung_collection.find_one({'ten_nguoi_dung': ten_nguoi_dung})
        if data:
            return NguoiDung.from_dict(data)
        return None
    
    @staticmethod
    def find_by_ma(ma_nguoi_dung):
        data = nguoidung_collection.find_one({'ma_nguoi_dung': ma_nguoi_dung})
        if data:
            return NguoiDung.from_dict(data)
        return None
    
    @staticmethod
    def find_all():
        return list(nguoidung_collection.find({}, {'_id': 0}))
    
    @staticmethod
    def from_dict(data):
        user = NguoiDung(
            ten_nguoi_dung=data['ten_nguoi_dung'],
            mat_khau=data['mat_khau'],
            ho_ten=data['ho_ten'],
            email=data['email'],
            so_dien_thoai=data.get('so_dien_thoai', ''),
            vai_tro=data.get('vai_tro', 'nguoi_dung')
        )
        user.ma_nguoi_dung = data['ma_nguoi_dung']
        user.dia_chi_vi = data.get('dia_chi_vi')
        user.created_at = data.get('created_at', datetime.datetime.now(datetime.timezone.utc))
        return user