from database.connection import giaodich_collection
import datetime
import uuid

class GiaoDich:
    def __init__(self, ma_hop_dong, loai_giao_dich, so_tien_giao_dich, hinh_thuc_thanh_toan, ma_nguoi_dung=None):
        self.ma_giao_dich = str(uuid.uuid4())
        self.ma_hop_dong = ma_hop_dong
        self.loai_giao_dich = loai_giao_dich  # 'thanh_toan_thue', 'hoan_tien_coc', 'phat', 'nap_tien'
        self.so_tien_giao_dich = so_tien_giao_dich
        self.hinh_thuc_thanh_toan = hinh_thuc_thanh_toan  # 'vi', 'the', 'chuyen_khoan'
        self.ma_nguoi_dung = ma_nguoi_dung  # ✅ THÊM TRƯỜNG NÀY
        self.thoi_gian_thanh_toan = datetime.datetime.now(datetime.timezone.utc)
        self.created_at = datetime.datetime.now(datetime.timezone.utc)
    
    def to_dict(self):
        return {
            'ma_giao_dich': self.ma_giao_dich,
            'ma_hop_dong': self.ma_hop_dong,
            'loai_giao_dich': self.loai_giao_dich,
            'so_tien_giao_dich': self.so_tien_giao_dich,
            'hinh_thuc_thanh_toan': self.hinh_thuc_thanh_toan,
            'ma_nguoi_dung': self.ma_nguoi_dung,  # ✅ THÊM TRƯỜNG NÀY
            'thoi_gian_thanh_toan': self.thoi_gian_thanh_toan,
            'created_at': self.created_at
        }
    
    def save(self):
        giaodich_collection.insert_one(self.to_dict())
        return self
    
    @staticmethod
    def find_by_hop_dong(ma_hop_dong):
        return list(giaodich_collection.find({'ma_hop_dong': ma_hop_dong}, {'_id': 0}))
    
    @staticmethod
    def find_all():
        return list(giaodich_collection.find({}, {'_id': 0}))
    
    @staticmethod
    def find_by_ma(ma_giao_dich):
        return giaodich_collection.find_one({'ma_giao_dich': ma_giao_dich}, {'_id': 0})