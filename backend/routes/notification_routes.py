from flask import jsonify
from services.notification_service import NotificationService

def notification_routes(app):
    
    @app.route('/api/notifications/expired-soon', methods=['GET'])
    def get_expired_soon():
        """Lấy danh sách hợp đồng sắp hết hạn"""
        results = NotificationService.check_expired_rentals()
        return jsonify({
            'success': True,
            'notifications': results,
            'count': len(results)
        }), 200
    
    @app.route('/api/notifications/expired', methods=['GET'])
    def get_expired():
        """Lấy danh sách hợp đồng đã hết hạn"""
        results = NotificationService.get_expired_rentals()
        return jsonify({
            'success': True,
            'expired': results,
            'count': len(results)
        }), 200