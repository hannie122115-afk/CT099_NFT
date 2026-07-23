from .crypto import Crypto
from .transaction import Transaction
import time
import json

class Block:
    def __init__(self, index, previous_hash, transactions, timestamp=None, nonce=0, difficulty=4):
        self.index = index
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.timestamp = timestamp or time.time()
        self.nonce = nonce
        self.difficulty = difficulty
        self.merkle_root = Crypto.calculate_merkle_root(
            [tx.to_dict() for tx in transactions]
        )
        self.hash = self.calculate_hash()
    
    def calculate_hash(self):
        """Tính hash của block"""
        block_data = {
            'index': self.index,
            'previous_hash': self.previous_hash,
            'merkle_root': self.merkle_root,
            'timestamp': self.timestamp,
            'nonce': self.nonce,
            'difficulty': self.difficulty,
            'transactions': [tx.to_dict() for tx in self.transactions]
        }
        return Crypto.sha256(json.dumps(block_data, sort_keys=True))
    
    def mine_block(self):
        """Đào block (Proof of Work)"""
        target = '0' * self.difficulty
        while self.hash[:self.difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()
        print(f"⛏️ Block {self.index} mined! Nonce: {self.nonce}, Hash: {self.hash[:10]}...")
        return self.hash
    
    def is_valid(self):
        """Kiểm tra block hợp lệ"""
        # Kiểm tra hash
        if self.hash != self.calculate_hash():
            print(f"❌ Block {self.index}: Hash mismatch")
            return False
        
        # Kiểm tra Proof of Work
        target = '0' * self.difficulty
        if self.hash[:self.difficulty] != target:
            print(f"❌ Block {self.index}: Invalid PoW")
            return False
        
        # Kiểm tra Merkle Root
        current_merkle = Crypto.calculate_merkle_root(
            [tx.to_dict() for tx in self.transactions]
        )
        if current_merkle != self.merkle_root:
            print(f"❌ Block {self.index}: Merkle root mismatch")
            return False
        
        # Kiểm tra từng transaction (bỏ qua system transactions)
        for tx in self.transactions:
            if tx.sender != 'system' and tx.action != 'mining_reward':
                if not tx.verify():
                    print(f"❌ Block {self.index}: Invalid transaction {tx.id}")
                    return False
        
        return True
    
    def to_dict(self):
        """Chuyển block thành dict"""
        return {
            'index': self.index,
            'previous_hash': self.previous_hash,
            'merkle_root': self.merkle_root,
            'timestamp': self.timestamp,
            'nonce': self.nonce,
            'difficulty': self.difficulty,
            'transactions': [tx.to_dict() for tx in self.transactions],
            'hash': self.hash
        }
    
    @staticmethod
    def from_dict(data):
        """Tạo block từ dict"""
        transactions = [Transaction.from_dict(tx) for tx in data['transactions']]
        block = Block(
            index=data['index'],
            previous_hash=data['previous_hash'],
            transactions=transactions,
            timestamp=data['timestamp'],
            nonce=data['nonce'],
            difficulty=data['difficulty']
        )
        block.merkle_root = data['merkle_root']
        block.hash = data['hash']
        return block
    
    @staticmethod
    def create_genesis_block():
        """Tạo genesis block"""
        genesis_tx = Transaction(
            sender='system',
            receiver='system',
            amount=0,
            action='genesis'
        )
        genesis_tx.hash = genesis_tx._calculate_hash()
        return Block(0, '0', [genesis_tx], difficulty=4)