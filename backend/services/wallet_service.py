from models.wallet_model import Wallet
from backend.models.nguoidung_model import User
from blockchain import get_blockchain, Transaction
import logging

logger = logging.getLogger(__name__)

class WalletService:
    
    @staticmethod
    def get_wallet_by_user(username):
        try:
            wallet = Wallet.find_by_username(username)
            if not wallet:
                user = User.find_by_username(username)
                if user and user.wallet_address:
                    wallet = Wallet.find_by_address(user.wallet_address)
            
            if not wallet:
                return {'success': False, 'message': 'Wallet not found'}
            
            blockchain = get_blockchain()
            balance = blockchain.get_balance(wallet.address)
            wallet.balance = balance
            Wallet.update_balance(wallet.address, balance)
            
            return {
                'success': True,
                'wallet': wallet.to_dict()
            }
        except Exception as e:
            logger.error(f"get_wallet_by_user error: {e}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def deposit(username, amount):
        if amount <= 0:
            return {'success': False, 'message': 'Amount must be positive'}
        
        try:
            user = User.find_by_username(username)
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            wallet = Wallet.find_by_username(username)
            if not wallet:
                from blockchain import create_wallet
                wallet_data = create_wallet()
                wallet = Wallet(
                    address=wallet_data['address'],
                    public_key=wallet_data['public_key'],
                    private_key=wallet_data['private_key'],
                    balance=0,
                    username=username
                )
                wallet.save()
                from database.connection import users_collection
                users_collection.update_one(
                    {'username': username},
                    {'$set': {'wallet_address': wallet.address}}
                )
            
            blockchain = get_blockchain()
            tx = Transaction(
                sender='system',
                receiver=wallet.address,
                amount=amount,
                action='deposit'
            )
            tx.hash = tx._calculate_hash()
            blockchain.pending_transactions.append(tx)
            block = blockchain.mine_pending_transactions(wallet.address)
            
            balance = blockchain.get_balance(wallet.address)
            Wallet.update_balance(wallet.address, balance)
            
            return {
                'success': True,
                'message': f'Deposited {amount} successfully',
                'new_balance': balance,
                'block_index': block.index if block else None
            }
        except Exception as e:
            logger.error(f"deposit error: {e}")
            return {'success': False, 'message': str(e)}