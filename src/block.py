import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from typing import List, Optional
from src.transaction import Transaction
from src.utxo_manager import UTXOManager
from src.mempool import Mempool
import time

# represents a block in the blockchain
class Block:
    # initializes a block
    def __init__(self, block_height: int, transactions: List[Transaction], miner: str, total_fees: float):
        self.block_height = block_height
        self.timestamp = int(time.time())
        self.transactions = transactions
        self.miner = miner
        self.total_fees = total_fees
        self.coinbase_tx_id = f"coinbase_{miner}_{block_height}_{self.timestamp}"
    
    def __repr__(self):
        return f"block(height={self.block_height}, txs={len(self.transactions)}, miner={self.miner}, fees={self.total_fees:.8f})"


# global block height counter
CURRENT_BLOCK_HEIGHT = 0

# simulates mining a block
def mine_block(
    miner_address: str,
    mempool: Mempool,
    utxo_manager: UTXOManager,
    num_txs: int = 5
) -> Optional[Block]:
    
    global CURRENT_BLOCK_HEIGHT
    
    print(f"\n{'='*60}")
    print(f"mining block #{CURRENT_BLOCK_HEIGHT + 1}")
    print(f"{ '='*60}")
    
    selected_txs: List[Transaction] = mempool.get_top_transactions(num_txs)
    
    if not selected_txs:
        print("no transactions available for mining.")
        return None
    
    print(f"selected {len(selected_txs)} transactions from mempool:")
    for i, tx in enumerate(selected_txs, 1):
        print(f"  {i}. {tx.tx_id} (fee: {tx.fee:.8f} btc)")
    
    utxo_snapshot = utxo_manager.get_snapshot()
    
    total_fees = 0.0
    successfully_applied = []
    
    try:
        for tx in selected_txs:
            is_valid, msg = tx.is_valid(utxo_manager)
            
            if not is_valid:
                print(f"warning: transaction {tx.tx_id} became invalid: {msg}")
                continue
            
            for inp in tx.inputs:
                try:
                    utxo_manager.remove_utxo(inp.prev_tx_id, inp.output_index)
                except KeyError as e:
                    print(f"error: could not spend utxo in {tx.tx_id}: {e}")
                    utxo_manager.load_snapshot(utxo_snapshot)
                    print("utxo state rolled back due to error")
                    return None
            
            for index, out in enumerate(tx.outputs):
                utxo_manager.add_utxo(
                    tx.tx_id,
                    index,
                    out.amount,
                    out.address
                )
            
            total_fees += tx.fee
            successfully_applied.append(tx)
        
        CURRENT_BLOCK_HEIGHT += 1
        block_height = CURRENT_BLOCK_HEIGHT
        coinbase_tx_id = f"coinbase_{miner_address}_{block_height}_{int(time.time())}"
        
        if total_fees > 0:
            utxo_manager.add_utxo(
                coinbase_tx_id,
                0,
                total_fees,
                miner_address
            )
            print(f"\ncoinbase created: {coinbase_tx_id}")
            print(f"miner {miner_address} receives {total_fees:.8f} btc in fees")
        
        for tx in successfully_applied:
            mempool.remove_transaction(tx.tx_id)
        
        print(f"\nblock #{block_height} mined successfully!")
        print(f"  transactions confirmed: {len(successfully_applied)}")
        print(f"  total fees: {total_fees:.8f} btc")
        print(f"  mempool size: {mempool.size()} transactions remaining")
        print(f"{ '='*60}\n")
        
        block = Block(block_height, successfully_applied, miner_address, total_fees)
        return block
        
    except Exception as e:
        print(f"error during mining: {e}")
        utxo_manager.load_snapshot(utxo_snapshot)
        print("utxo state rolled back due to error")
        return None

# gets the current block height
def get_current_block_height() -> int:
    return CURRENT_BLOCK_HEIGHT

# resets block height
def reset_block_height(height: int = 0):
    global CURRENT_BLOCK_HEIGHT
    CURRENT_BLOCK_HEIGHT = height
