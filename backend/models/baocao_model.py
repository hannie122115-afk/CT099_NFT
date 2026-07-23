from database.connection import db
import datetime
import uuid

baocao_collection = db['baocao']

class BaoCao:
    def __init__(self, ma_hop_dong, nguoi_bao_cao, ly_do, noi_dung):
        self.ma_bao_cao = str(uuid.uuid4())
        self.ma_hop_dong = ma_hop_dong
        self.nguoi_bao_cao = nguoi_bao_cao
        self.ly_do = ly_do  # 'khong_tra_nft', 'tra_cham', 'nft_bi_hu_hong', 'khac'
        self.noi_dung = noi_dung
        self.trang_thai = 'cho_xu_ly'  # 'cho_xu_ly', 'dang_xu_ly', 'da_xu_ly'
        self.created_at = datetime.datetime.now(datetime.timezone.utc)
    
    def to_dict(self):
        return {
            'ma_bao_cao': self.ma_bao_cao,
            'ma_hop_dong': self.ma_hop_dong,
            'nguoi_bao_cao': self.nguoi_bao_cao,
            'ly_do': self.ly_do,
            'noi_dung': self.noi_dung,
            'trang_thai': self.trang_thai,
            'created_at': self.created_at
        }
    
    def save(self):
        baocao_collection.insert_one(self.to_dict())
        return self
    
    @staticmethod
    def find_all():
        return list(baocao_collection.find({}, {'_id': 0}))
    
    @staticmethod
    def find_by_hop_dong(ma_hop_dong):
        return list(baocao_collection.find({'ma_hop_dong': ma_hop_dong}, {'_id': 0}))
    
    @staticmethod
    def update_status(ma_bao_cao, status):
        baocao_collection.update_one(
            {'ma_bao_cao': ma_bao_cao},
            {'$set': {'trang_thai': status}}
        )