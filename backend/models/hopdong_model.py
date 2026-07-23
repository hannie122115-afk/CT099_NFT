from database.connection import hopdong_collection
import datetime
import uuid

class HopDong:
    def __init__(self, ma_bai_dang, ma_nguoi_thue, thoi_gian_bat_dau, thoi_gian_ket_thuc, ma_nhan_vat=None):
        self.ma_hop_dong = str(uuid.uuid4())
        self.ma_bai_dang = ma_bai_dang
        self.ma_nguoi_thue = ma_nguoi_thue
        self.ma_nhan_vat = ma_nhan_vat
        self.thoi_gian_bat_dau = thoi_gian_bat_dau
        self.thoi_gian_ket_thuc = thoi_gian_ket_thuc
        self.tong_tien = 0
        self.tien_coc = 0
        self.trang_thai_thue = 'dang_thue'
        self.danh_gia = None
        self.nhan_xet = None
        self.ngay_tra = None
        self.created_at = datetime.datetime.utcnow()  # Không có timezone
    
    def to_dict(self):
        return {
            'ma_hop_dong': self.ma_hop_dong,
            'ma_bai_dang': self.ma_bai_dang,
            'ma_nguoi_thue': self.ma_nguoi_thue,
            'ma_nhan_vat': self.ma_nhan_vat,
            'thoi_gian_bat_dau': self.thoi_gian_bat_dau,
            'thoi_gian_ket_thuc': self.thoi_gian_ket_thuc,
            'tong_tien': self.tong_tien,
            'tien_coc': self.tien_coc,
            'trang_thai_thue': self.trang_thai_thue,
            'danh_gia': self.danh_gia,
            'nhan_xet': self.nhan_xet,
            'ngay_tra': self.ngay_tra,
            'created_at': self.created_at
        }
    
    def save(self):
        hopdong_collection.insert_one(self.to_dict())
        return self
    
    @staticmethod
    def find_by_ma(ma_hop_dong):
        return hopdong_collection.find_one({'ma_hop_dong': ma_hop_dong}, {'_id': 0})
    
    @staticmethod
    def find_by_nguoi_thue(ma_nguoi_thue):
        return list(hopdong_collection.find({'ma_nguoi_thue': ma_nguoi_thue}, {'_id': 0}))
    
    @staticmethod
    def find_active():
        return list(hopdong_collection.find({'trang_thai_thue': 'dang_thue'}, {'_id': 0}))
    
    @staticmethod
    def find_all():
        return list(hopdong_collection.find({}, {'_id': 0}))
    
    @staticmethod
    def update_status(ma_hop_dong, status):
        hopdong_collection.update_one(
            {'ma_hop_dong': ma_hop_dong},
            {'$set': {'trang_thai_thue': status}}
        )