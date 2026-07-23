from .block import Block
from .transaction import Transaction
from .crypto import Crypto
import json
import time
from typing import List, Optional

class Blockchain:
    def __init__(self, difficulty=4, mining_reward=10):
        self.chain = []
        self.pending_transactions = []
        self.difficulty = difficulty
        self.mining_reward = mining_reward
        self._initialize_chain()
    
    def _initialize_chain(self):
        """Khởi tạo blockchain với genesis block"""
        genesis = Block.create_genesis_block()
        genesis.hash = genesis.calculate_hash()
        self.chain.append(genesis)
    
    def get_last_block(self) -> Block:
        """Lấy block cuối cùng"""
        return self.chain[-1]
    
    def add_transaction(self, transaction: Transaction) -> bool:
        """Thêm giao dịch vào pending"""
        # Bỏ qua verify cho transaction từ system
        if transaction.sender != 'system':
            if not transaction.verify():
                print("❌ Transaction verification failed!")
                return False
            
            # Kiểm tra số dư
            balance = self.get_balance(transaction.sender)
            if balance < transaction.amount:
                print(f"❌ Insufficient balance! Need {transaction.amount}, have {balance}")
                return False
        
        self.pending_transactions.append(transaction)
        return True
    
    def mine_pending_transactions(self, miner_address: str) -> Optional[Block]:
        """Đào các giao dịch pending"""
        if not self.pending_transactions:
            print("❌ No pending transactions to mine!")
            return None
        
        # Tạo bản sao của pending transactions
        transactions_to_mine = self.pending_transactions.copy()
        
        # Tạo block mới
        new_block = Block(
            index=len(self.chain),
            previous_hash=self.get_last_block().hash,
            transactions=transactions_to_mine,
            difficulty=self.difficulty
        )
        
        # Đào block
        new_block.mine_block()
        
        # Thêm block vào chain
        self.chain.append(new_block)
        
        # Reset pending transactions
        self.pending_transactions = []
        
        # Thêm phần thưởng mining
        reward_tx = Transaction(
            sender='system',
            receiver=miner_address,
            amount=self.mining_reward,
            action='mining_reward'
        )
        reward_tx.hash = reward_tx._calculate_hash()
        self.pending_transactions.append(reward_tx)
        
        print(f"⛏️ Block {new_block.index} mined successfully!")
        return new_block
    
    def get_balance(self, address: str) -> float:
        """Lấy số dư của địa chỉ ví"""
        balance = 0
        
        # Kiểm tra tất cả block đã được xác nhận
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == address:
                    balance -= tx.amount
                if tx.receiver == address:
                    balance += tx.amount
        
        # KHÔNG tính pending transactions (chỉ tính đã xác nhận)
        # để tránh double counting
        
        return balance
    
    def get_transactions_by_address(self, address: str) -> List[dict]:
        """Lấy tất cả giao dịch của một địa chỉ"""
        transactions = []
        
        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == address or tx.receiver == address:
                    tx_dict = tx.to_dict()
                    tx_dict['block_index'] = block.index
                    tx_dict['block_hash'] = block.hash
                    transactions.append(tx_dict)
        
        return transactions
    
    def get_block_by_index(self, index: int) -> Optional[Block]:
        """Lấy block theo index"""
        if 0 <= index < len(self.chain):
            return self.chain[index]
        return None
    
    def get_block_by_hash(self, block_hash: str) -> Optional[Block]:
        """Lấy block theo hash"""
        for block in self.chain:
            if block.hash == block_hash:
                return block
        return None
    
    def get_transaction_by_id(self, tx_id: str) -> Optional[dict]:
        """Lấy giao dịch theo ID"""
        for block in self.chain:
            for tx in block.transactions:
                if tx.id == tx_id:
                    tx_dict = tx.to_dict()
                    tx_dict['block_index'] = block.index
                    tx_dict['block_hash'] = block.hash
                    return tx_dict
        return None
    
    def is_chain_valid(self) -> bool:
        """Kiểm tra tính hợp lệ của toàn bộ blockchain"""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            
            # Kiểm tra hash hiện tại
            if current.hash != current.calculate_hash():
                print(f"❌ Invalid hash at block {i}")
                return False
            
            # Kiểm tra previous hash
            if current.previous_hash != previous.hash:
                print(f"❌ Invalid previous hash at block {i}")
                return False
            
            # Kiểm tra block validity
            if not current.is_valid():
                print(f"❌ Invalid block at index {i}")
                return False
        
        return True
    
    def to_dict(self) -> dict:
        """Chuyển blockchain thành dict"""
        return {
            'chain': [block.to_dict() for block in self.chain],
            'pending_transactions': [tx.to_dict() for tx in self.pending_transactions],
            'difficulty': self.difficulty,
            'mining_reward': self.mining_reward,
            'length': len(self.chain)
        }
    
    @staticmethod
    def from_dict(data: dict):
        """Tạo blockchain từ dict"""
        blockchain = Blockchain(
            difficulty=data['difficulty'],
            mining_reward=data['mining_reward']
        )
        
        # Thay thế chain
        blockchain.chain = []
        for block_data in data['chain']:
            blockchain.chain.append(Block.from_dict(block_data))
        
        # Thêm pending transactions
        for tx_data in data['pending_transactions']:
            blockchain.pending_transactions.append(Transaction.from_dict(tx_data))
        
        return blockchain

# Singleton instance
_blockchain = None

def get_blockchain():
    """Lấy instance của blockchain (singleton)"""
    global _blockchain
    if _blockchain is None:
        _blockchain = Blockchain()
    return _blockchain