import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.utxo_manager import UTXOManager
from src.mempool import Mempool
from src.transaction import create_transaction
from src.block import mine_block, reset_block_height
from test.testing import run_all_tests

# prints the header
def print_header():
    print("\n" + "="*60)
    print("=== bitcoin transaction simulator ===")
    print("="*60)

# prints genesis block information
def print_genesis_info(utxo_manager: UTXOManager):
    print("\ninitial utxos (genesis block):")
    print(f"- alice: 50.0 btc")
    print(f"- bob: 30.0 btc")
    print(f"- charlie: 20.0 btc")
    print(f"- david: 10.0 btc")
    print(f"- eve: 5.0 btc")

# prints the main menu
def print_menu():
    print("\nmain menu:")
    print("1. create new transaction")
    print("2. view utxo set")
    print("3. view mempool")
    print("4. mine block")
    print("5. run test scenarios")
    print("6. exit")

# creates a transaction interactively
def create_transaction_interactive(utxo_manager: UTXOManager, mempool: Mempool):
    print("\n" + "-"*60)
    sender = input("enter sender: ").strip()
    
    if not sender:
        print("error: sender cannot be empty")
        return
    
    balance = utxo_manager.get_balance(sender)
    print(f"available balance: {balance:.1f} btc")
    
    if balance <= 0:
        print(f"error: {sender} has no funds")
        return
    
    recipient = input("enter recipient: ").strip()
    
    if not recipient:
        print("error: recipient cannot be empty")
        return
    
    try:
        amount = float(input("enter amount: ").strip())
        if amount <= 0:
            print("error: amount must be positive")
            return
    except ValueError:
        print("error: invalid amount")
        return
    
    if amount + 0.001 > balance:
        print(f"error: insufficient funds")
        return
    
    try:
        print("\ncreating transaction...")
        tx = create_transaction(sender, recipient, amount, utxo_manager)
        
        print(f"transaction valid! fee: {tx.fee:.3f} btc")
        print(f"transaction id: {tx.tx_id}")
        
        success, msg = mempool.add_transaction(tx, utxo_manager)
        
        if success:
            print(f"transaction added to mempool.")
            print(f"mempool now has {mempool.size()} transactions.")
        else:
            print(f"failed: {msg}")
            
    except ValueError as e:
        print(f"transaction failed: {e}")

# views the utxo set
def view_utxo_set(utxo_manager: UTXOManager):
    print("\n" + "-"*60)
    print("current utxo set")
    print("-"*60)
    
    if not utxo_manager.utxo_set:
        print("utxo set is empty")
        return
    
    for (tx_id, index), data in sorted(utxo_manager.utxo_set.items()):
        print(f"({tx_id}, {index}) -> {data['amount']:.3f} btc owned by {data['owner']}")
    
    print(f"\ntotal supply: {utxo_manager.get_total_supply():.3f} btc")

# views the mempool
def view_mempool(mempool: Mempool):
    print("\n" + "-"*60)
    print("mempool")
    print("-"*60)
    
    if mempool.size() == 0:
        print("mempool is empty")
        return
    
    stats = mempool.get_statistics()
    print(f"transactions: {stats['size']}")
    print(f"total fees: {stats['total_fees']:.8f} btc")
    
    if stats['size'] > 0:
        print(f"average fee: {stats['avg_fee']:.8f} btc")
        print(f"highest fee: {stats['max_fee']:.8f} btc")
        print(f"lowest fee: {stats['min_fee']:.8f} btc")
    
    print("\ntransactions (sorted by fee):")
    for tx in sorted(mempool.transactions, key=lambda t: t.fee, reverse=True):
        print(f"  {tx.tx_id}: {len(tx.inputs)} in, {len(tx.outputs)} out, fee={tx.fee:.8f} btc")

# mines a block interactively
def mine_block_interactive(utxo_manager: UTXOManager, mempool: Mempool):
    print("\n" + "-"*60)
    miner = input("enter miner name: ").strip()
    
    if not miner:
        print("error: miner name cannot be empty")
        return
    
    print("\nMining block...")
    block = mine_block(miner, mempool, utxo_manager, num_txs=5)
    
    if not block:
        print("mining failed - no transactions available")

# sets up genesis utxos
def setup_genesis_utxos(utxo_manager: UTXOManager):
    utxo_manager.add_utxo("genesis", 0, 50.0, "alice")
    utxo_manager.add_utxo("genesis", 1, 30.0, "bob")
    utxo_manager.add_utxo("genesis", 2, 20.0, "charlie")
    utxo_manager.add_utxo("genesis", 3, 10.0, "david")
    utxo_manager.add_utxo("genesis", 4, 5.0, "eve")

# main function to run the simulator
def main():
    utxo_manager = UTXOManager()
    mempool = Mempool()
    
    print_header()
    setup_genesis_utxos(utxo_manager)
    print_genesis_info(utxo_manager)
    
    while True:
        print_menu()
        choice = input("\nEnter choice: ").strip()
        
        if choice == "1":
            create_transaction_interactive(utxo_manager, mempool)
        elif choice == "2":
            view_utxo_set(utxo_manager)
        elif choice == "3":
            view_mempool(mempool)
        elif choice == "4":
            mine_block_interactive(utxo_manager, mempool)
        elif choice == "5":
            run_all_tests()
        elif choice == "6":
            print("\nExiting simulator...")
            break
        else:
            print("Invalid choice. please enter 1-6.")


if __name__ == "__main__":
    main()
