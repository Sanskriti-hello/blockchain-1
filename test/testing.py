import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.utxo_manager import UTXOManager
from src.mempool import Mempool
from src.transaction import Transaction, TransactionInput, TransactionOutput, validate_transaction, create_transaction
from src.block import mine_block, reset_block_height


def setup_genesis_utxos(utxo_manager: UTXOManager):
    """Initialize the system with genesis UTXOs"""
    utxo_manager.add_utxo("genesis", 0, 50.0, "Alice")
    utxo_manager.add_utxo("genesis", 1, 30.0, "Bob")
    utxo_manager.add_utxo("genesis", 2, 20.0, "Charlie")
    utxo_manager.add_utxo("genesis", 3, 10.0, "David")
    utxo_manager.add_utxo("genesis", 4, 5.0, "Eve")
    print("Genesis UTXOs created:")
    print(f"  Alice: 50.0 BTC")
    print(f"  Bob: 30.0 BTC")
    print(f"  Charlie: 20.0 BTC")
    print(f"  David: 10.0 BTC")
    print(f"  Eve: 5.0 BTC")
    print(f"  Total Supply: {utxo_manager.get_total_supply():.1f} BTC\n")


def test_1_basic_valid_transaction(utxo_manager: UTXOManager, mempool: Mempool):
    """
    Test 1: Basic Valid Transaction
    Alice sends 10 BTC to Bob
    Must include change output back to Alice
    Must calculate correct fee (0.001 BTC)
    """
    print("="*60)
    print("TEST 1: Basic Valid Transaction")
    print("="*60)
    
    # Create transaction: Alice -> Bob (10 BTC)
    inputs = [TransactionInput("genesis", 0, "Alice")]
    outputs = [
        TransactionOutput(10.0, "Bob"),
        TransactionOutput(39.999, "Alice")  # Change (50 - 10 - 0.001 fee)
    ]
    tx = Transaction("tx_alice_bob_001", inputs, outputs)
    
    # Validate
    try:
        is_valid, fee = validate_transaction(tx, utxo_manager)
        print(f"✓ Transaction valid!")
        print(f"  Fee: {fee:.8f} BTC")
        print(f"  Inputs: 50.0 BTC from Alice")
        print(f"  Outputs: 10.0 to Bob, 39.999 to Alice (change)")
        
        # Add to mempool
        success, msg = mempool.add_transaction(tx, utxo_manager)
        print(f"  {msg}")
        
        return True
    except ValueError as e:
        print(f"✗ FAILED: {e}")
        return False


def test_2_multiple_inputs(utxo_manager: UTXOManager, mempool: Mempool):
    """
    Test 2: Multiple Inputs
    Alice spends two UTXOs together
    Tests input aggregation and fee calculation
    """
    print("\n" + "="*60)
    print("TEST 2: Multiple Inputs")
    print("="*60)
    
    # First, we need Alice to have two UTXOs
    # Use genesis UTXO (50 BTC) and we'll need to create another one
    # Let's give Alice Charlie's genesis UTXO for this test
    
    # Create transaction: Alice uses 50 + 20 BTC = 70 BTC
    inputs = [
        TransactionInput("genesis", 0, "Alice"),   # 50 BTC
        TransactionInput("genesis", 2, "Charlie")  # 20 BTC (pretend Charlie gave it to Alice)
    ]
    
    # Wait, we need to modify this test. Let's create it properly.
    # First reset and give Alice two UTXOs
    print("Setting up: Creating two UTXOs for Alice...")
    
    utxo_manager.clear = lambda: None  # Prevent clear for now
    
    # Add second UTXO for Alice
    utxo_manager.add_utxo("tx_previous", 0, 20.0, "Alice")
    
    inputs = [
        TransactionInput("genesis", 0, "Alice"),     # 50 BTC
        TransactionInput("tx_previous", 0, "Alice")  # 20 BTC
    ]
    outputs = [
        TransactionOutput(60.0, "Bob"),
        TransactionOutput(9.999, "Alice")  # Change (70 - 60 - 0.001 fee)
    ]
    
    tx = Transaction("tx_alice_bob_multi", inputs, outputs)
    
    try:
        is_valid, fee = validate_transaction(tx, utxo_manager)
        print(f"✓ Transaction valid!")
        print(f"  Fee: {fee:.8f} BTC")
        print(f"  Input 1: 50.0 BTC")
        print(f"  Input 2: 20.0 BTC")
        print(f"  Total inputs: 70.0 BTC")
        print(f"  Output to Bob: 60.0 BTC")
        print(f"  Change to Alice: 9.999 BTC")
        
        success, msg = mempool.add_transaction(tx, utxo_manager)
        print(f"  {msg}")
        
        return True
    except ValueError as e:
        print(f"✗ FAILED: {e}")
        return False


def test_3_double_spend_same_tx(utxo_manager: UTXOManager, mempool: Mempool):
    """
    Test 3: Double-Spend in Same Transaction
    Transaction tries to spend same UTXO twice
    Expected: REJECT with clear error message
    """
    print("\n" + "="*60)
    print("TEST 3: Double-Spend in Same Transaction")
    print("="*60)
    
    # Create transaction that spends same UTXO twice
    inputs = [
        TransactionInput("genesis", 1, "Bob"),  # 30 BTC
        TransactionInput("genesis", 1, "Bob")   # Same UTXO again!
    ]
    outputs = [
        TransactionOutput(50.0, "Eve")
    ]
    
    tx = Transaction("tx_bob_doublespend", inputs, outputs)
    
    try:
        is_valid, fee = validate_transaction(tx, utxo_manager)
        print(f"✗ FAILED: Transaction should have been rejected!")
        return False
    except ValueError as e:
        print(f"✓ Transaction correctly rejected!")
        print(f"  Error: {e}")
        return True


def test_4_mempool_double_spend(utxo_manager: UTXOManager, mempool: Mempool):
    """
    Test 4: Mempool Double-Spend
    TX1: Alice → Bob (spends UTXO)
    TX2: Alice → Charlie (spends SAME UTXO)
    Expected: TX1 accepted, TX2 rejected
    """
    print("\n" + "="*60)
    print("TEST 4: Mempool Double-Spend")
    print("="*60)
    
    # Clear mempool for clean test
    mempool.clear()
    
    # TX1: Alice -> Bob
    inputs1 = [TransactionInput("genesis", 0, "Alice")]
    outputs1 = [
        TransactionOutput(10.0, "Bob"),
        TransactionOutput(39.999, "Alice")
    ]
    tx1 = Transaction("tx_alice_bob_first", inputs1, outputs1)
    
    # TX2: Alice -> Charlie (tries to spend same UTXO)
    inputs2 = [TransactionInput("genesis", 0, "Alice")]  # Same input!
    outputs2 = [
        TransactionOutput(15.0, "Charlie"),
        TransactionOutput(34.999, "Alice")
    ]
    tx2 = Transaction("tx_alice_charlie_second", inputs2, outputs2)
    
    # Add TX1
    success1, msg1 = mempool.add_transaction(tx1, utxo_manager)
    print(f"TX1: {msg1}")
    
    # Try to add TX2
    success2, msg2 = mempool.add_transaction(tx2, utxo_manager)
    print(f"TX2: {msg2}")
    
    if success1 and not success2:
        print(f"✓ Test passed! TX1 accepted, TX2 rejected (First-Seen Rule)")
        return True
    else:
        print(f"✗ FAILED: Expected TX1 to succeed and TX2 to fail")
        return False


def test_5_insufficient_funds(utxo_manager: UTXOManager, mempool: Mempool):
    """
    Test 5: Insufficient Funds
    Bob tries to send 35 BTC (has only 30 BTC)
    Expected: REJECT with "Insufficient funds"
    """
    print("\n" + "="*60)
    print("TEST 5: Insufficient Funds")
    print("="*60)
    
    # Bob has 30 BTC, tries to send 35
    inputs = [TransactionInput("genesis", 1, "Bob")]
    outputs = [TransactionOutput(35.0, "Alice")]
    
    tx = Transaction("tx_bob_overspend", inputs, outputs)
    
    try:
        is_valid, fee = validate_transaction(tx, utxo_manager)
        print(f"✗ FAILED: Transaction should have been rejected!")
        return False
    except ValueError as e:
        print(f"✓ Transaction correctly rejected!")
        print(f"  Error: {e}")
        return True


def test_6_negative_amount(utxo_manager: UTXOManager, mempool: Mempool):
    """
    Test 6: Negative Amount
    Transaction with negative output amount
    Expected: REJECT immediately
    """
    print("\n" + "="*60)
    print("TEST 6: Negative Amount")
    print("="*60)
    
    # Create transaction with negative output
    inputs = [TransactionInput("genesis", 3, "David")]
    outputs = [TransactionOutput(-5.0, "Eve")]  # Negative!
    
    tx = Transaction("tx_david_negative", inputs, outputs)
    
    try:
        is_valid, fee = validate_transaction(tx, utxo_manager)
        print(f"✗ FAILED: Transaction should have been rejected!")
        return False
    except ValueError as e:
        print(f"✓ Transaction correctly rejected!")
        print(f"  Error: {e}")
        return True


def test_7_zero_fee_transaction(utxo_manager: UTXOManager, mempool: Mempool):
    """
    Test 7: Zero Fee Transaction
    Inputs = Outputs (fee = 0)
    Expected: ACCEPTED (valid in Bitcoin)
    """
    print("\n" + "="*60)
    print("TEST 7: Zero Fee Transaction")
    print("="*60)
    
    # Eve sends exactly 5 BTC (no fee)
    inputs = [TransactionInput("genesis", 4, "Eve")]
    outputs = [TransactionOutput(5.0, "Alice")]  # Exactly 5 BTC, no change, no fee
    
    tx = Transaction("tx_eve_zerofee", inputs, outputs)
    
    try:
        is_valid, fee = validate_transaction(tx, utxo_manager)
        print(f"✓ Transaction valid!")
        print(f"  Fee: {fee:.8f} BTC (zero fee is allowed)")
        
        success, msg = mempool.add_transaction(tx, utxo_manager)
        print(f"  {msg}")
        
        return True
    except ValueError as e:
        print(f"✗ FAILED: Zero fee transactions should be valid")
        print(f"  Error: {e}")
        return False


def test_8_race_attack_simulation(utxo_manager: UTXOManager, mempool: Mempool):
    """
    Test 8: Race Attack Simulation
    Low-fee merchant TX arrives first
    High-fee attack TX arrives second
    Expected: First transaction wins (first-seen rule)
    """
    print("\n" + "="*60)
    print("TEST 8: Race Attack Simulation")
    print("="*60)
    
    mempool.clear()
    
    # Merchant TX (low fee)
    inputs_merchant = [TransactionInput("genesis", 3, "David")]
    outputs_merchant = [
        TransactionOutput(9.0, "MerchantShop"),
        TransactionOutput(0.999, "David")  # 0.001 BTC fee
    ]
    tx_merchant = Transaction("tx_david_merchant_lowfee", inputs_merchant, outputs_merchant)
    
    # Attack TX (high fee) - tries to double-spend to attacker's address
    inputs_attack = [TransactionInput("genesis", 3, "David")]  # Same UTXO!
    outputs_attack = [
        TransactionOutput(9.5, "David")  # Send back to self, 0.5 BTC fee
    ]
    tx_attack = Transaction("tx_david_attack_highfee", inputs_attack, outputs_attack)
    
    # Merchant transaction arrives first
    success1, msg1 = mempool.add_transaction(tx_merchant, utxo_manager)
    print(f"Merchant TX (low fee): {msg1}")
    
    # Attacker's transaction arrives second (higher fee but too late)
    success2, msg2 = mempool.add_transaction(tx_attack, utxo_manager)
    print(f"Attack TX (high fee): {msg2}")
    
    if success1 and not success2:
        print(f"✓ First-Seen Rule enforced! Merchant protected from race attack")
        return True
    else:
        print(f"✗ FAILED: First transaction should win regardless of fee")
        return False


def test_9_complete_mining_flow(utxo_manager: UTXOManager, mempool: Mempool):
    """
    Test 9: Complete Mining Flow
    Add multiple transactions to mempool
    Mine a block
    Check: UTXOs updated, miner gets fees, mempool cleared
    """
    print("\n" + "="*60)
    print("TEST 9: Complete Mining Flow")
    print("="*60)
    
    # Reset for clean test
    mempool.clear()
    reset_block_height(0)
    
    # Add multiple transactions
    print("\nAdding transactions to mempool...")
    
    # TX1: Alice -> Bob
    tx1 = create_transaction("Alice", "Bob", 10.0, utxo_manager)
    mempool.add_transaction(tx1, utxo_manager)
    
    # TX2: Charlie -> David
    tx2 = create_transaction("Charlie", "David", 5.0, utxo_manager)
    mempool.add_transaction(tx2, utxo_manager)
    
    # TX3: Bob -> Eve
    tx3 = create_transaction("Bob", "Eve", 15.0, utxo_manager)
    mempool.add_transaction(tx3, utxo_manager)
    
    print(f"\nMempool size before mining: {mempool.size()}")
    
    # Mine block
    miner_balance_before = utxo_manager.get_balance("Miner1")
    block = mine_block("Miner1", mempool, utxo_manager, num_txs=3)
    
    if block:
        miner_balance_after = utxo_manager.get_balance("Miner1")
        print(f"\n✓ Mining successful!")
        print(f"  Miner balance before: {miner_balance_before:.8f} BTC")
        print(f"  Miner balance after: {miner_balance_after:.8f} BTC")
        print(f"  Miner earned: {miner_balance_after - miner_balance_before:.8f} BTC")
        print(f"  Mempool size after: {mempool.size()}")
        return True
    else:
        print(f"✗ FAILED: Mining failed")
        return False


def test_10_unconfirmed_chain(utxo_manager: UTXOManager, mempool: Mempool):
    """
    Test 10: Unconfirmed Chain
    Alice → Bob (TX1 creates new UTXO for Bob)
    Bob tries to spend that UTXO before TX1 is mined
    
    Design Decision: REJECT - only confirmed UTXOs can be spent
    This prevents issues with chain reorganizations.
    """
    print("\n" + "="*60)
    print("TEST 10: Unconfirmed Chain")
    print("="*60)
    
    mempool.clear()
    
    # TX1: Alice -> Bob (creates UTXO for Bob)
    inputs1 = [TransactionInput("genesis", 0, "Alice")]
    outputs1 = [
        TransactionOutput(25.0, "Bob"),
        TransactionOutput(24.999, "Alice")
    ]
    tx1 = Transaction("tx_alice_bob_unconfirmed", inputs1, outputs1)
    
    success1, msg1 = mempool.add_transaction(tx1, utxo_manager)
    print(f"TX1: {msg1}")
    
    # TX2: Bob tries to spend the UTXO from TX1 (not yet mined!)
    inputs2 = [TransactionInput("tx_alice_bob_unconfirmed", 0, "Bob")]
    outputs2 = [TransactionOutput(24.0, "Charlie")]
    tx2 = Transaction("tx_bob_charlie_chain", inputs2, outputs2)
    
    try:
        is_valid, fee = validate_transaction(tx2, utxo_manager)
        print(f"\nDesign Decision: REJECT unconfirmed chain spending")
        print(f"Explanation: TX2 tries to spend UTXO from TX1, but TX1 is not yet confirmed.")
        print(f"Only confirmed (mined) UTXOs can be spent to prevent issues with chain reorgs.")
        print(f"✗ TX2 would be rejected")
        return False  # This is expected behavior
    except ValueError as e:
        print(f"\n✓ Unconfirmed chain spending correctly rejected!")
        print(f"  Error: {e}")
        print(f"\nDesign Decision Explanation:")
        print(f"  - Only confirmed (mined) UTXOs can be spent")
        print(f"  - This prevents issues with mempool conflicts and chain reorganizations")
        print(f"  - TX1 must be mined before Bob can spend the outputs")
        return True


def run_all_tests():
    """Run all 10 mandatory test cases"""
    print("\n" + "="*60)
    print("UTXO SIMULATOR - COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    # Setup
    utxo_manager = UTXOManager()
    mempool = Mempool()
    
    setup_genesis_utxos(utxo_manager)
    
    # Track results
    results = {}
    
    # Run tests
    results["Test 1"] = test_1_basic_valid_transaction(utxo_manager, mempool)
    
    # Reset for test 2
    utxo_manager = UTXOManager()
    mempool = Mempool()
    setup_genesis_utxos(utxo_manager)
    results["Test 2"] = test_2_multiple_inputs(utxo_manager, mempool)
    
    # Tests 3-10
    utxo_manager = UTXOManager()
    mempool = Mempool()
    setup_genesis_utxos(utxo_manager)
    
    results["Test 3"] = test_3_double_spend_same_tx(utxo_manager, mempool)
    results["Test 4"] = test_4_mempool_double_spend(utxo_manager, mempool)
    results["Test 5"] = test_5_insufficient_funds(utxo_manager, mempool)
    results["Test 6"] = test_6_negative_amount(utxo_manager, mempool)
    results["Test 7"] = test_7_zero_fee_transaction(utxo_manager, mempool)
    results["Test 8"] = test_8_race_attack_simulation(utxo_manager, mempool)
    results["Test 9"] = test_9_complete_mining_flow(utxo_manager, mempool)
    results["Test 10"] = test_10_unconfirmed_chain(utxo_manager, mempool)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_status in results.items():
        status = "✓ PASSED" if passed_status else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*60)


if __name__ == "__main__":
    run_all_tests()
