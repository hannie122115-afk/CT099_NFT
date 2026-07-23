from database.connection import game_collection
import datetime
import uuid

class Game:
    def __init__(self, ten_game, mo_ta_game, nha_phat_hanh=''):
        self.ma_game = str(uuid.uuid4())
        self.ten_game = ten_game
        self.mo_ta_game = mo_ta_game
        self.nha_phat_hanh = nha_phat_hanh
        self.created_at = datetime.datetime.now(datetime.timezone.utc)
    
    def to_dict(self):
        return {
            'ma_game': self.ma_game,
            'ten_game': self.ten_game,
            'mo_ta_game': self.mo_ta_game,
            'nha_phat_hanh': self.nha_phat_hanh,
            'created_at': self.created_at
        }
    
    def save(self):
        game_collection.insert_one(self.to_dict())
        return self
    
    @staticmethod
    def find_all():
        return list(game_collection.find({}, {'_id': 0}))
    
    @staticmethod
    def find_by_ma(ma_game):
        return game_collection.find_one({'ma_game': ma_game}, {'_id': 0})