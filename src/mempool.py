import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from typing import List, Set, Tuple, Optional
from src.transaction import Transaction

# stores unconfirmed transactions
class Mempool:
    # initializes the mempool
    def __init__(self, max_size: int = 50):
        self.transactions: List[Transaction] = []
        self.spent_utxos: Set[Tuple[str, int]] = set()
        self.max_size = max_size
        self.tx_by_id = {}

    # validates and adds transaction to mempool
    def add_transaction(self, tx: Transaction, utxo_manager) -> Tuple[bool, str]:
        if tx.tx_id in self.tx_by_id:
            return False, "transaction already in mempool"
        
        if len(self.transactions) >= self.max_size:
            lowest_fee_tx = min(self.transactions, key=lambda t: t.fee)
            
            if tx.fee <= lowest_fee_tx.fee:
                return False, f"mempool full and transaction fee too low (need > {lowest_fee_tx.fee:.8f} btc)"
            
            self._remove_transaction(lowest_fee_tx.tx_id)
            print(f"evicted transaction {lowest_fee_tx.tx_id} (fee: {lowest_fee_tx.fee:.8f} btc)")

        is_valid, error_msg = tx.is_valid(utxo_manager, self.spent_utxos)
        if not is_valid:
            return False, f"invalid transaction: {error_msg}"

        for tx_input in tx.inputs:
            utxo = (tx_input.prev_tx_id, tx_input.output_index)
            if utxo in self.spent_utxos:
                conflicting_tx_id = None
                for existing_tx in self.transactions:
                    for existing_input in existing_tx.inputs:
                        if (existing_input.prev_tx_id, existing_input.output_index) == utxo:
                            conflicting_tx_id = existing_tx.tx_id
                            break
                    if conflicting_tx_id:
                        break
                
                return False, f"utxo {utxo} already spent in mempool by {conflicting_tx_id} (first-seen rule)"

        self.transactions.append(tx)
        self.tx_by_id[tx.tx_id] = tx

        for tx_input in tx.inputs:
            utxo = (tx_input.prev_tx_id, tx_input.output_index)
            self.spent_utxos.add(utxo)

        return True, f"transaction {tx.tx_id} added to mempool (fee: {tx.fee:.8f} btc)"

    # internally removes a transaction
    def _remove_transaction(self, tx_id: str) -> bool:
        if tx_id not in self.tx_by_id:
            return False
        
        tx = self.tx_by_id[tx_id]
        
        for tx_input in tx.inputs:
            utxo = (tx_input.prev_tx_id, tx_input.output_index)
            self.spent_utxos.discard(utxo)
        
        self.transactions.remove(tx)
        del self.tx_by_id[tx_id]
        
        return True

    # removes transaction from mempool
    def remove_transaction(self, tx_id: str) -> bool:
        return self._remove_transaction(tx_id)

    # returns top n transactions by fee
    def get_top_transactions(self, n: int) -> List[Transaction]:
        sorted_txs = sorted(self.transactions, key=lambda tx: tx.fee, reverse=True)
        return sorted_txs[:n]

    # gets a specific transaction by id
    def get_transaction(self, tx_id: str) -> Optional[Transaction]:
        return self.tx_by_id.get(tx_id)

    # returns number of transactions in mempool
    def size(self) -> int:
        return len(self.transactions)

    # clears all transactions from mempool
    def clear(self) -> None:
        self.transactions.clear()
        self.spent_utxos.clear()
        self.tx_by_id.clear()

    # checks if a utxo is spent in the mempool
    def is_utxo_spent(self, tx_id: str, index: int) -> bool:
        return (tx_id, index) in self.spent_utxos

    # returns human-readable mempool view
    def __str__(self) -> str:
        if not self.transactions:
            return "mempool is empty."
        
        lines = [f"mempool ({len(self.transactions)} transactions):"]
        for tx in sorted(self.transactions, key=lambda t: t.fee, reverse=True):
            lines.append(f"  {tx.tx_id}: {len(tx.inputs)} inputs -> {len(tx.outputs)} outputs, fee={tx.fee:.8f} btc")
        return "\n".join(lines)
    
    # calculates total fees in mempool
    def get_total_fees(self) -> float:
        return sum(tx.fee for tx in self.transactions)
    
    # gets mempool statistics
    def get_statistics(self) -> dict:
        if not self.transactions:
            return {
                "size": 0,
                "total_fees": 0.0,
                "avg_fee": 0.0,
                "max_fee": 0.0,
                "min_fee": 0.0
            }
        
        fees = [tx.fee for tx in self.transactions]
        return {
            "size": len(self.transactions),
            "total_fees": sum(fees),
            "avg_fee": sum(fees) / len(fees),
            "max_fee": max(fees),
            "min_fee": min(fees)
        }
