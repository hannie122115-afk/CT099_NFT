import hashlib
import json
import ecdsa
import base58
from ecdsa import SECP256k1, SigningKey, VerifyingKey
import os

class Crypto:
    @staticmethod
    def sha256(data):
        """Tạo SHA-256 hash của dữ liệu"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return hashlib.sha256(data).hexdigest()
    
    @staticmethod
    def double_sha256(data):
        """Tạo double SHA-256 hash (dùng trong Bitcoin)"""
        return Crypto.sha256(Crypto.sha256(data).encode('utf-8'))
    
    @staticmethod
    def generate_key_pair():
        """Tạo cặp khóa ECDSA (Private Key, Public Key)"""
        private_key = SigningKey.generate(curve=SECP256k1)
        public_key = private_key.get_verifying_key()
        return private_key, public_key
    
    @staticmethod
    def private_key_to_string(private_key):
        """Chuyển private key thành string"""
        return private_key.to_string().hex()
    
    @staticmethod
    def public_key_to_string(public_key):
        """Chuyển public key thành string"""
        return public_key.to_string().hex()
    
    @staticmethod
    def string_to_private_key(private_key_hex):
        """Chuyển string thành private key"""
        return SigningKey.from_string(bytes.fromhex(private_key_hex), curve=SECP256k1)
    
    @staticmethod
    def string_to_public_key(public_key_hex):
        """Chuyển string thành public key"""
        return VerifyingKey.from_string(bytes.fromhex(public_key_hex), curve=SECP256k1)
    
    @staticmethod
    def sign_message(private_key, message):
        """Ký message bằng private key"""
        if isinstance(message, str):
            message = message.encode('utf-8')
        signature = private_key.sign(message)
        return signature.hex()
    
    @staticmethod
    def verify_signature(public_key, message, signature_hex):
        """Xác minh chữ ký"""
        if isinstance(message, str):
            message = message.encode('utf-8')
        signature = bytes.fromhex(signature_hex)
        try:
            return public_key.verify(signature, message)
        except:
            return False
    
    @staticmethod
    def generate_wallet_address(public_key):
        """Tạo địa chỉ ví từ public key (mô phỏng Bitcoin)"""
        # Bước 1: SHA-256 của public key
        sha256_hash = Crypto.sha256(public_key.to_string())
        
        # Bước 2: RIPEMD-160 (mô phỏng bằng SHA-256 cho đơn giản)
        ripe_hash = Crypto.sha256(sha256_hash)
        
        # Bước 3: Thêm version byte (0x00 cho mainnet)
        versioned = '00' + ripe_hash
        
        # Bước 4: Double SHA-256 checksum
        checksum = Crypto.double_sha256(versioned)[:8]
        
        # Bước 5: Kết hợp và Base58 encode
        address_hex = versioned + checksum
        address_bytes = bytes.fromhex(address_hex)
        
        # Base58 encode (mô phỏng)
        return base58.b58encode(address_bytes).decode('utf-8')
    
    @staticmethod
    def calculate_merkle_root(transactions):
        """Tính Merkle Root từ danh sách giao dịch"""
        if not transactions:
            return Crypto.sha256('empty')
        
        # Chuyển transactions thành hash
        hashes = [Crypto.sha256(json.dumps(tx, sort_keys=True)) for tx in transactions]
        
        # Xây dựng Merkle Tree
        while len(hashes) > 1:
            if len(hashes) % 2 != 0:
                hashes.append(hashes[-1])  # Duplicate last if odd
            
            new_hashes = []
            for i in range(0, len(hashes), 2):
                combined = hashes[i] + hashes[i+1]
                new_hashes.append(Crypto.sha256(combined))
            hashes = new_hashes
        
        return hashes[0]