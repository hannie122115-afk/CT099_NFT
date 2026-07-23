from database.connection import vi_collection
import datetime

class Wallet:
    def __init__(self, dia_chi, ten_nguoi_dung, so_du=0, private_key='', public_key=''):
        self.dia_chi = dia_chi
        self.ten_nguoi_dung = ten_nguoi_dung
        self.so_du = so_du
        self.private_key = private_key
        self.public_key = public_key
        self.created_at = datetime.datetime.now(datetime.timezone.utc)
    
    def to_dict(self):
        return {
            'dia_chi': self.dia_chi,
            'ten_nguoi_dung': self.ten_nguoi_dung,
            'so_du': self.so_du,
            'private_key': self.private_key,
            'public_key': self.public_key,
            'created_at': self.created_at
        }
    
    def save(self):
        vi_collection.insert_one(self.to_dict())
        return self
    
    @staticmethod
    def find_by_address(dia_chi):
        return vi_collection.find_one({'dia_chi': dia_chi}, {'_id': 0})
    
    @staticmethod
    def find_by_username(ten_nguoi_dung):
        return vi_collection.find_one({'ten_nguoi_dung': ten_nguoi_dung}, {'_id': 0})
    
    @staticmethod
    def update_balance(dia_chi, new_balance):
        vi_collection.update_one(
            {'dia_chi': dia_chi},
            {'$set': {'so_du': new_balance}}
        )