from blockchain import create_wallet, get_blockchain, Transaction

def test_blockchain():
    print("🧪 Testing Blockchain...")
    
    # Reset blockchain
    global _blockchain
    _blockchain = None
    
    # 1. Tạo ví
    wallet1 = create_wallet()
    wallet2 = create_wallet()
    print(f"✅ Wallet 1: {wallet1['address'][:10]}...")
    print(f"✅ Wallet 2: {wallet2['address'][:10]}...")
    
    # 2. Tạo blockchain
    blockchain = get_blockchain()
    
    # 3. NẠP TIỀN VÀO WALLET 1
    print("\n💰 Nạp tiền vào Wallet 1...")
    deposit_tx = Transaction(
        sender='system',
        receiver=wallet1['address'],
        amount=100,
        action='deposit'
    )
    deposit_tx.hash = deposit_tx._calculate_hash()
    blockchain.pending_transactions.append(deposit_tx)
    
    # 4. Đào block đầu tiên (Deposit + Mining Reward)
    print("⛏️ Mining block 1 (Deposit)...")
    block1 = blockchain.mine_pending_transactions(wallet1['address'])
    if block1:
        print(f"✅ Block {block1.index} mined!")
    
    # Kiểm tra số dư sau deposit + reward
    balance1 = blockchain.get_balance(wallet1['address'])
    print(f"💰 Wallet 1 balance: {balance1}")
    
    # 5. Tạo giao dịch chuyển tiền
    print("\n💸 Tạo giao dịch chuyển 30 từ Wallet 1 sang Wallet 2...")
    tx = Transaction(
        sender=wallet1['address'],
        receiver=wallet2['address'],
        amount=30,
        action='transfer'
    )
    tx.sign(wallet1['private_key'], wallet1['public_key'])
    
    # 6. Thêm giao dịch
    if blockchain.add_transaction(tx):
        print("✅ Transaction added to pending")
    else:
        print("❌ Transaction failed!")
        return
    
    # 7. Đào block thứ 2 (Transfer + Mining Reward)
    print("\n⛏️ Mining block 2 (Transfer)...")
    block2 = blockchain.mine_pending_transactions(wallet1['address'])
    if block2:
        print(f"✅ Block {block2.index} mined!")
    
    # 8. Kiểm tra số dư cuối cùng
    balance1 = blockchain.get_balance(wallet1['address'])
    balance2 = blockchain.get_balance(wallet2['address'])
    print(f"\n💰 Wallet 1 balance: {balance1}")
    print(f"💰 Wallet 2 balance: {balance2}")
    
    # 9. Kiểm tra blockchain
    print(f"\n🔍 Blockchain valid: {blockchain.is_chain_valid()}")
    print(f"📊 Chain length: {len(blockchain.chain)}")
    
    # 10. Hiển thị tất cả giao dịch
    print("\n📋 Transaction history:")
    for block in blockchain.chain:
        print(f"  Block {block.index}:")
        for tx in block.transactions:
            print(f"    - {tx.action}: {tx.sender[:10]} → {tx.receiver[:10]} ({tx.amount})")

if __name__ == "__main__":
    test_blockchain()