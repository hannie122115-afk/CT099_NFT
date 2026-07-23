from database.connection import danhgia_collection
import datetime
import uuid

class DanhGia:
    def __init__(self, ma_hop_dong, noi_dung, so_sao):
        self.ma_danh_gia = str(uuid.uuid4())
        self.ma_hop_dong = ma_hop_dong
        self.noi_dung = noi_dung
        self.so_sao = so_sao  # 1-5
        self.created_at = datetime.datetime.now(datetime.timezone.utc)
    
    def to_dict(self):
        return {
            'ma_danh_gia': self.ma_danh_gia,
            'ma_hop_dong': self.ma_hop_dong,
            'noi_dung': self.noi_dung,
            'so_sao': self.so_sao,
            'created_at': self.created_at
        }
    
    def save(self):
        danhgia_collection.insert_one(self.to_dict())
        return self
    
    @staticmethod
    def find_by_hop_dong(ma_hop_dong):
        return danhgia_collection.find_one({'ma_hop_dong': ma_hop_dong}, {'_id': 0})
    
    @staticmethod
    def find_all():
        return list(danhgia_collection.find({}, {'_id': 0}))