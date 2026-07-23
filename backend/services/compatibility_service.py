from models.nhanvat_model import CharacterItem
from models.nft_model import NFT
from models.vatpham_model import Item
from models.hopdong_model import Rental

class CompatibilityService:
    
    @staticmethod
    def check_nft_compatibility(nft_id, character_id):
        """
        Kiểm tra NFT có thể được sử dụng bởi nhân vật không
        """
        # 1. Lấy NFT
        nft = NFT.find_by_id(nft_id)
        if not nft:
            return {
                'compatible': False,
                'message': 'NFT không tồn tại'
            }
        
        # 2. Lấy item từ NFT
        item = Item.find_by_id(nft.get('item_id'))
        if not item:
            return {
                'compatible': False,
                'message': 'NFT không đại diện cho vật phẩm nào'
            }
        
        # 3. Kiểm tra nhân vật có thể sử dụng vật phẩm này không
        can_use = CharacterItem.can_use(character_id, item['id'])
        
        if can_use:
            return {
                'compatible': True,
                'message': f'Nhân vật có thể sử dụng {item["name"]}',
                'item': item
            }
        else:
            return {
                'compatible': False,
                'message': f'Nhân vật không thể sử dụng {item["name"]}',
                'item': item
            }
    
    @staticmethod
    def get_usable_nfts_for_character(character_id, user_address):
        """
        Lấy danh sách NFT mà nhân vật có thể sử dụng
        """
        # 1. Lấy tất cả vật phẩm nhân vật có thể dùng
        character_items = CharacterItem.get_items_by_character(character_id)
        item_ids = [ci['item_id'] for ci in character_items]
        
        # 2. Lấy NFT của user
        user_nfts = NFT.find_by_owner(user_address)
        
        # 3. Lọc NFT có item_id thuộc danh sách
        compatible_nfts = []
        for nft in user_nfts:
            if nft.get('item_id') in item_ids:
                compatible_nfts.append(nft)
        
        return compatible_nfts