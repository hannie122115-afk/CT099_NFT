from flask import request, jsonify
from models.game_model import Game
from models.nhanvat_model import NhanVat

def game_routes(app):
    
    @app.route('/api/games', methods=['GET'])
    def get_games():
        games = Game.find_all()
        for game in games:
            characters = NhanVat.find_by_game(game['ma_game'])
            game['so_nhan_vat'] = len(characters)
        return jsonify({'success': True, 'games': games}), 200
    
    @app.route('/api/games', methods=['POST'])
    def create_game():
        data = request.get_json()
        if not data.get('ten_game'):
            return jsonify({'success': False, 'message': 'Thiếu tên game'}), 400
        
        game = Game(
            ten_game=data['ten_game'],
            mo_ta_game=data.get('mo_ta_game', ''),
            nha_phat_hanh=data.get('nha_phat_hanh', '')
        )
        game.save()
        
        return jsonify({'success': True, 'game': game.to_dict()}), 201
    
    @app.route('/api/games/<ma_game>/characters', methods=['GET'])
    def get_characters_by_game(ma_game):
        characters = NhanVat.find_by_game(ma_game)
        return jsonify({'success': True, 'characters': characters}), 200