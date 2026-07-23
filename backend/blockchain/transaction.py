from .crypto import Crypto
from .wallet import Wallet
import json
import time
import uuid

class Transaction:
    def __init__(self, sender, receiver, amount, action='transfer', data=None):
        self.id = str(uuid.uuid4())
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.action = action  # 'transfer', 'mint_nft', 'rent_nft', 'return_nft', 'deposit', 'withdraw'
        self.data = data or {}
        self.timestamp = time.time()
        self.signature = None
        self.public_key = None
        self.hash = None
        self._calculate_hash()
    
    def _calculate_hash(self):
        """Tính hash của transaction"""
        tx_data = {
            'id': self.id,
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount,
            'action': self.action,
            'data': self.data,
            'timestamp': self.timestamp
        }
        self.hash = Crypto.sha256(json.dumps(tx_data, sort_keys=True))
        return self.hash
    
    def sign(self, private_key, public_key):
        """Ký giao dịch"""
        self.public_key = public_key
        tx_data = {
            'id': self.id,
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount,
            'action': self.action,
            'data': self.data,
            'timestamp': self.timestamp,
            'public_key': public_key
        }
        message = json.dumps(tx_data, sort_keys=True)
        self.signature = Crypto.sign_message(
            Crypto.string_to_private_key(private_key),
            message
        )
        return self.signature
    
    def verify(self):
        """Xác minh chữ ký"""
        if not self.signature or not self.public_key:
            return False
        
        tx_data = {
            'id': self.id,
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount,
            'action': self.action,
            'data': self.data,
            'timestamp': self.timestamp,
            'public_key': self.public_key
        }
        message = json.dumps(tx_data, sort_keys=True)
        public_key = Crypto.string_to_public_key(self.public_key)
        return Crypto.verify_signature(public_key, message, self.signature)
    
    def to_dict(self):
        """Chuyển transaction thành dict"""
        return {
            'id': self.id,
            'sender': self.sender,
            'receiver': self.receiver,
            'amount': self.amount,
            'action': self.action,
            'data': self.data,
            'timestamp': self.timestamp,
            'public_key': self.public_key,
            'signature': self.signature,
            'hash': self.hash
        }
    
    @staticmethod
    def from_dict(data):
        """Tạo transaction từ dict"""
        tx = Transaction(
            sender=data['sender'],
            receiver=data['receiver'],
            amount=data['amount'],
            action=data.get('action', 'transfer'),
            data=data.get('data', {})
        )
        tx.id = data['id']
        tx.timestamp = data['timestamp']
        tx.public_key = data.get('public_key')
        tx.signature = data.get('signature')
        tx.hash = data['hash']
        return tx
    
    @staticmethod
    def create_rental_transaction(renter, owner, nft_id, amount, deposit):
        """Tạo giao dịch thuê NFT"""
        return Transaction(
            sender=renter,
            receiver=owner,
            amount=amount,
            action='rent_nft',
            data={
                'nft_id': nft_id,
                'deposit': deposit,
                'rental_start': time.time()
            }
        )

    @staticmethod
    def create_return_transaction(renter, owner, nft_id, deposit):
        """Tạo giao dịch trả NFT"""
        return Transaction(
            sender=owner,
            receiver=renter,
            amount=deposit,
            action='return_nft',
            data={
                'nft_id': nft_id,
                'return_time': time.time()
            }
        )