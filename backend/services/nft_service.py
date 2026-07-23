from models.nft_model import NFT
from services.wallet_service import WalletService
import logging

logger = logging.getLogger(__name__)

class NFTService:
    
    @staticmethod
    def mint_nft(username, name, description, price, item_id=None, image_url=None):
        if price <= 0:
            return {'success': False, 'message': 'Price must be positive'}
        
        wallet = WalletService.get_wallet_by_user(username)
        if not wallet['success']:
            return {'success': False, 'message': 'Wallet not found'}
        
        owner_address = wallet['wallet']['address']
        
        nft = NFT(
            name=name,
            description=description,
            owner_address=owner_address,
            price=price,
            item_id=item_id,
            image_url=image_url
        )
        nft.save()
        
        return {
            'success': True,
            'message': 'NFT minted successfully',
            'nft': nft.to_dict()
        }
    
    @staticmethod
    def get_all_nfts():
        try:
            nfts = NFT.find_all()
            return {'success': True, 'nfts': nfts}
        except Exception as e:
            logger.error(f"get_all_nfts error: {e}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def get_available_nfts():
        try:
            nfts = NFT.find_available()
            return {'success': True, 'nfts': nfts}
        except Exception as e:
            logger.error(f"get_available_nfts error: {e}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def get_user_nfts(username):
        try:
            wallet = WalletService.get_wallet_by_user(username)
            if not wallet['success']:
                return {'success': False, 'message': 'Wallet not found'}
            
            address = wallet['wallet']['address']
            nfts = NFT.find_by_owner_address(address)
            
            return {'success': True, 'nfts': nfts}
        except Exception as e:
            logger.error(f"get_user_nfts error: {e}")
            return {'success': False, 'message': str(e)}
    
    # ===== THÊM CHỨC NĂNG CHO THUÊ =====
    
    @staticmethod
    def update_nft_price(username, nft_id, new_price):
        """Cập nhật giá cho thuê NFT"""
        try:
            if new_price <= 0:
                return {'success': False, 'message': 'Price must be positive'}
            
            # Kiểm tra NFT
            nft = NFT.find_by_id(nft_id)
            if not nft:
                return {'success': False, 'message': 'NFT not found'}
            
            # Kiểm tra chủ sở hữu
            wallet = WalletService.get_wallet_by_user(username)
            if not wallet['success']:
                return {'success': False, 'message': 'Wallet not found'}
            
            if nft['owner_address'] != wallet['wallet']['address']:
                return {'success': False, 'message': 'You are not the owner of this NFT'}
            
            # Cập nhật giá
            from database.connection import nfts_collection
            nfts_collection.update_one(
                {'id': nft_id},
                {'$set': {'price': new_price}}
            )
            
            return {
                'success': True,
                'message': f'NFT price updated to {new_price} COINS/day'
            }
        except Exception as e:
            logger.error(f"update_nft_price error: {e}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def toggle_nft_status(username, nft_id, status):
        """Bật/tắt trạng thái cho thuê của NFT"""
        try:
            valid_statuses = ['available', 'unavailable']
            if status not in valid_statuses:
                return {'success': False, 'message': f'Invalid status. Must be {valid_statuses}'}
            
            # Kiểm tra NFT
            nft = NFT.find_by_id(nft_id)
            if not nft:
                return {'success': False, 'message': 'NFT not found'}
            
            # Kiểm tra chủ sở hữu
            wallet = WalletService.get_wallet_by_user(username)
            if not wallet['success']:
                return {'success': False, 'message': 'Wallet not found'}
            
            if nft['owner_address'] != wallet['wallet']['address']:
                return {'success': False, 'message': 'You are not the owner of this NFT'}
            
            # Không thể set thành rented nếu đang có người thuê
            if nft['status'] == 'rented' and status == 'unavailable':
                return {'success': False, 'message': 'Cannot change status while NFT is rented'}
            
            # Cập nhật status
            from database.connection import nfts_collection
            nfts_collection.update_one(
                {'id': nft_id},
                {'$set': {'status': status}}
            )
            
            status_text = 'có sẵn để cho thuê' if status == 'available' else 'tạm ngưng cho thuê'
            return {
                'success': True,
                'message': f'NFT đã được {status_text}',
                'status': status
            }
        except Exception as e:
            logger.error(f"toggle_nft_status error: {e}")
            return {'success': False, 'message': str(e)}