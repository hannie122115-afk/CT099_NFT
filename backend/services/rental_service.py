from models.hopdong_model import Rental
from models.nft_model import NFT
from services.wallet_service import WalletService
from blockchain import get_blockchain, Transaction
import datetime
import logging

logger = logging.getLogger(__name__)

class RentalService:
    
    @staticmethod
    def create_rental(username, nft_id, days, character_id=None):
        try:
            print(f"📝 Creating rental: username={username}, nft_id={nft_id}, days={days}")
            
            if days <= 0:
                return {'success': False, 'message': 'Days must be positive'}
            
            # Lấy ví người thuê
            renter_wallet = WalletService.get_wallet_by_user(username)
            if not renter_wallet['success']:
                return {'success': False, 'message': 'Renter wallet not found'}
            
            renter_address = renter_wallet['wallet']['address']
            print(f"👤 Renter address: {renter_address}")
            
            # Lấy NFT
            nft = NFT.find_by_id(nft_id)
            if not nft:
                return {'success': False, 'message': 'NFT not found'}
            print(f"🖼️ NFT found: {nft}")
            
            if nft['status'] != 'available':
                return {'success': False, 'message': f'NFT is {nft["status"]}'}
            
            if nft['owner_address'] == renter_address:
                return {'success': False, 'message': 'Cannot rent your own NFT'}
            
            # Tính toán
            total_price = nft['price'] * days
            deposit = total_price * 0.2
            
            # Kiểm tra số dư
            blockchain = get_blockchain()
            balance = blockchain.get_balance(renter_address)
            print(f"💰 Balance: {balance}, Need: {total_price + deposit}")
            
            if balance < total_price + deposit:
                return {
                    'success': False,
                    'message': f'Insufficient balance. Need {total_price + deposit}, have {balance}'
                }
            
            # Tạo rental
            start_date = datetime.datetime.utcnow()
            end_date = start_date + datetime.timedelta(days=days)
            
            rental = Rental(
                nft_id=nft_id,
                renter_address=renter_address,
                owner_address=nft['owner_address'],
                start_date=start_date,
                end_date=end_date,
                total_price=total_price,
                deposit=deposit,
                character_id=character_id
            )
            rental.save()
            print(f"✅ Rental created: {rental.id}")
            
            # Cập nhật status NFT
            NFT.update_status(nft_id, 'rented')
            
            # Ghi blockchain
            tx = Transaction(
                sender=renter_address,
                receiver=nft['owner_address'],
                amount=total_price,
                action='rent_nft',
                data={
                    'rental_id': rental.id,
                    'nft_id': nft_id,
                    'days': days,
                    'deposit': deposit
                }
            )
            tx.hash = tx._calculate_hash()
            blockchain.pending_transactions.append(tx)
            blockchain.mine_pending_transactions(renter_address)
            
            return {
                'success': True,
                'message': 'Rental created successfully',
                'rental': rental.to_dict()
            }
            
        except Exception as e:
            print(f"❌ Create rental error: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def return_nft(rental_id):
        try:
            rental = Rental.find_by_id(rental_id)
            if not rental:
                return {'success': False, 'message': 'Rental not found'}
            
            if rental.status != 'active':
                return {'success': False, 'message': f'Rental is {rental.status}'}
            
            Rental.complete_rental(rental_id)
            NFT.update_status(rental.nft_id, 'available')
            
            # Hoàn trả tiền cọc
            blockchain = get_blockchain()
            tx = Transaction(
                sender=rental.owner_address,
                receiver=rental.renter_address,
                amount=rental.deposit,
                action='return_deposit',
                data={'rental_id': rental_id}
            )
            tx.hash = tx._calculate_hash()
            blockchain.pending_transactions.append(tx)
            blockchain.mine_pending_transactions(rental.owner_address)
            
            return {
                'success': True,
                'message': 'NFT returned successfully',
                'rental': rental.to_dict()
            }
        except Exception as e:
            print(f"❌ Return rental error: {e}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def get_user_rentals(username):
        try:
            wallet = WalletService.get_wallet_by_user(username)
            if not wallet['success']:
                return {'success': False, 'message': 'Wallet not found'}
            
            address = wallet['wallet']['address']
            rentals = Rental.find_by_renter(address)
            rentals.extend(Rental.find_by_owner(address))
            
            return {
                'success': True,
                'rentals': rentals
            }
        except Exception as e:
            print(f"❌ Get rentals error: {e}")
            return {'success': False, 'message': str(e)}