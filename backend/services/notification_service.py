from models.hopdong_model import HopDong
import datetime
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    
    @staticmethod
    def check_expired_rentals():
        """Kiểm tra các hợp đồng sắp hết hạn trong 24 giờ tới"""
        now = datetime.datetime.now(datetime.timezone.utc)
        expired_soon = now + datetime.timedelta(days=1)
        
        rentals = HopDong.find_active()
        results = []
        
        for rental in rentals:
            end_date = rental['thoi_gian_ket_thuc']
            if end_date <= expired_soon and end_date > now:
                hours_left = (end_date - now).total_seconds() / 3600
                results.append({
                    'ma_hop_dong': rental['ma_hop_dong'],
                    'ma_bai_dang': rental['ma_bai_dang'],
                    'thoi_gian_ket_thuc': end_date,
                    'con_lai': round(hours_left, 1),
                    'don_vi': 'giờ'
                })
        
        return results
    
    @staticmethod
    def get_expired_rentals():
        """Lấy các hợp đồng đã hết hạn chưa trả"""
        now = datetime.datetime.now(datetime.timezone.utc)
        rentals = HopDong.find_active()
        results = []
        
        for rental in rentals:
            if rental['thoi_gian_ket_thuc'] < now:
                results.append(rental)
        
        return results