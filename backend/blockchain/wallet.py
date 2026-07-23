from .crypto import Crypto
from ecdsa import SECP256k1, SigningKey, VerifyingKey
import json
import time

class Wallet:
    def __init__(self, private_key=None):
        if private_key:
            self.private_key = Crypto.string_to_private_key(private_key)
        else:
            self.private_key, self.public_key = Crypto.generate_key_pair()
            self.public_key = self.private_key.get_verifying_key()
        
        # Lưu public key nếu chưa có
        if not hasattr(self, 'public_key'):
            self.public_key = self.private_key.get_verifying_key()
        
        self.address = Crypto.generate_wallet_address(self.public_key)
        self.balance = 0
    
    def get_private_key_string(self):
        """Lấy private key dạng string"""
        return Crypto.private_key_to_string(self.private_key)
    
    def get_public_key_string(self):
        """Lấy public key dạng string"""
        return Crypto.public_key_to_string(self.public_key)
    
    def sign_transaction(self, transaction_data):
        """Ký giao dịch"""
        message = json.dumps(transaction_data, sort_keys=True)
        return Crypto.sign_message(self.private_key, message)
    
    def verify_transaction(self, transaction):
        """Xác minh giao dịch"""
        # Tạo message từ transaction (không bao gồm signature)
        tx_data = {k: v for k, v in transaction.items() if k != 'signature'}
        message = json.dumps(tx_data, sort_keys=True)
        
        public_key = Crypto.string_to_public_key(transaction['public_key'])
        return Crypto.verify_signature(public_key, message, transaction['signature'])
    
    def to_dict(self):
        """Chuyển wallet thành dict"""
        return {
            'address': self.address,
            'public_key': self.get_public_key_string(),
            'balance': self.balance
        }
    
    @staticmethod
    def create_from_private_key(private_key_hex):
        """Tạo wallet từ private key hex"""
        return Wallet(private_key_hex)
    
    @staticmethod
    def create_new():
        """Tạo wallet mới"""
        return Wallet()

# Helper functions
def create_wallet():
    """Tạo ví mới và trả về thông tin"""
    wallet = Wallet.create_new()
    return {
        'address': wallet.address,
        'private_key': wallet.get_private_key_string(),
        'public_key': wallet.get_public_key_string()
    }

def create_wallet_from_private_key(private_key_hex):
    """Tạo ví từ private key"""
    wallet = Wallet.create_from_private_key(private_key_hex)
    return {
        'address': wallet.address,
        'public_key': wallet.get_public_key_string()
    }