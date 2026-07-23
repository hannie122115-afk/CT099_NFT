from database.connection import nhanvat_collection
import datetime
import uuid

class NhanVat:
    def __init__(self, ten_nhan_vat, ma_game):
        self.ma_nhan_vat = str(uuid.uuid4())
        self.ten_nhan_vat = ten_nhan_vat
        self.ma_game = ma_game
        self.created_at = datetime.datetime.now(datetime.timezone.utc)
    
    def to_dict(self):
        return {
            'ma_nhan_vat': self.ma_nhan_vat,
            'ten_nhan_vat': self.ten_nhan_vat,
            'ma_game': self.ma_game,
            'created_at': self.created_at
        }
    
    def save(self):
        nhanvat_collection.insert_one(self.to_dict())
        return self
    
    @staticmethod
    def find_by_game(ma_game):
        return list(nhanvat_collection.find({'ma_game': ma_game}, {'_id': 0}))
    
    @staticmethod
    def find_by_ma(ma_nhan_vat):
        return nhanvat_collection.find_one({'ma_nhan_vat': ma_nhan_vat}, {'_id': 0})
    
    @staticmethod
    def find_all():
        return list(nhanvat_collection.find({}, {'_id': 0}))