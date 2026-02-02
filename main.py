from utxo_manager import UTXOManager
from mempool import Mempool
from transaction import Transaction, validate_transaction
from block import mine_block
from testing import run_tests
def main():
    um = UTXOManager()
    mp = Mempool()
    # Genesis
    um.add_utxo("genesis", 0, 50.0, "Alice")
    um.add_utxo("genesis", 1, 30.0, "Bob")
    um.add_utxo("genesis", 2, 20.0, "Charlie")
    
    while True:
        print("\n1. Create TX 2. View UTXOs 3. View Mempool 4. Mine 5. Run Tests 6. Exit")
        choice = input("Choice: ")
        
        if choice == "1":
            sender = input("Sender: ")
            bal = um.get_balance(sender)
            print(f"Balance: {bal}")
            if bal <= 0: continue
            
            # Simplified Input Selection
            avail = um.get_utxos_for_owner(sender)
            # logic to build tx inputs and outputs...
            # mp.add_transaction(tx) if validate_transaction(...)
            
        elif choice == "4":
            mine_block("Miner1", mp, um)
        elif choice == "5":
            run_tests(um, mp)
        elif choice == "6":
            break

if __name__ == "__main__":
    main()