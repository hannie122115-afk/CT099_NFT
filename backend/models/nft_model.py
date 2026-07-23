from database.connection import nft_collection
import datetime
import uuid

class NFT:
    def __init__(self, ten, mo_ta, dia_chi_chu_so_huu, gia_thue, ma_vat_pham, url_hinh_anh=None):
        self.ma_nft = str(uuid.uuid4())
        self.ten = ten
        self.mo_ta = mo_ta
        self.dia_chi_chu_so_huu = dia_chi_chu_so_huu
        self.gia_thue = gia_thue
        self.ma_vat_pham = ma_vat_pham
        self.url_hinh_anh = url_hinh_anh
        self.trang_thai = 'co_san'  # 'co_san', 'dang_thue', 'tam_ngung'
        self.so_lan_thue = 0
        self.tong_thu_nhap = 0
        self.created_at = datetime.datetime.now(datetime.timezone.utc)
    
    def to_dict(self):
        return {
            'ma_nft': self.ma_nft,
            'ten': self.ten,
            'mo_ta': self.mo_ta,
            'dia_chi_chu_so_huu': self.dia_chi_chu_so_huu,
            'gia_thue': self.gia_thue,
            'ma_vat_pham': self.ma_vat_pham,
            'url_hinh_anh': self.url_hinh_anh,
            'trang_thai': self.trang_thai,
            'so_lan_thue': self.so_lan_thue,
            'tong_thu_nhap': self.tong_thu_nhap,
            'created_at': self.created_at
        }
    
    def save(self):
        nft_collection.insert_one(self.to_dict())
        return self
    
    @staticmethod
    def find_by_ma(ma_nft):
        return nft_collection.find_one({'ma_nft': ma_nft}, {'_id': 0})
    
    @staticmethod
    def find_by_owner(dia_chi_vi):
        return list(nft_collection.find({'dia_chi_chu_so_huu': dia_chi_vi}, {'_id': 0}))
    
    @staticmethod
    def find_available():
        return list(nft_collection.find({'trang_thai': 'co_san'}, {'_id': 0}))
    
    @staticmethod
    def find_by_vat_pham(ma_vat_pham):
        return list(nft_collection.find({'ma_vat_pham': ma_vat_pham}, {'_id': 0}))
    
    @staticmethod
    def find_all():
        return list(nft_collection.find({}, {'_id': 0}))
    
    @staticmethod
    def update_status(ma_nft, status):
        nft_collection.update_one(
            {'ma_nft': ma_nft},
            {'$set': {'trang_thai': status}}
        )
    
    @staticmethod
    def update_stats(ma_nft, earned):
        nft_collection.update_one(
            {'ma_nft': ma_nft},
            {
                '$inc': {'so_lan_thue': 1, 'tong_thu_nhap': earned}
            }
        )