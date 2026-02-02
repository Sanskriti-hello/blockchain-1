import utxo_manager
from transaction import Transaction, validate_transaction
from mempool import Mempool
def run_tests(utxo_manager, mempool):
    print("Test 3: Double-Spend in Same TX")
    try:
        tx = Transaction("Alice", 
                         [{"prev_tx": "genesis", "index": 0, "owner": "Alice"},
                          {"prev_tx": "genesis", "index": 0, "owner": "Alice"}],
                         [{"amount": 10, "address": "Bob"}])
        validate_transaction(tx, utxo_manager)
    except ValueError as e: print(f"Rejected: {e}")

    print("\nTest 4: Mempool Double-Spend")
    tx1 = Transaction("Alice", [{"prev_tx": "genesis", "index": 0, "owner": "Alice"}], 
                      [{"amount": 10, "address": "Bob"}, {"amount": 39.99, "address": "Alice"}])
    validate_transaction(tx1, utxo_manager, mempool.spent_utxos)
    mempool.add_transaction(tx1)
    
    try:
        tx2 = Transaction("Alice", [{"prev_tx": "genesis", "index": 0, "owner": "Alice"}], 
                          [{"amount": 5, "address": "Charlie"}])
        validate_transaction(tx2, utxo_manager, mempool.spent_utxos)
    except ValueError as e: print(f"Rejected TX2: {e}")

if __name__ == "__main__":
    run_tests(utxo_manager.UTXOManager(), Mempool())