class Mempool:
    def __init__(self, max_size=50):
        self.transactions = []          
        self.spent_utxos = set()        
        self.max_size = max_size

    def add_transaction(self, tx, utxo_manager) -> tuple[bool, str]:
        """
        Validate and add transaction.
        Return (success, message)
        """

        if len(self.transactions) >= self.max_size:
            lowest_fee_tx = min(self.transactions, key=lambda t: t.fee)
            if tx.fee <= lowest_fee_tx.fee:
                return False, "Mempool full (lower fee)"
            self.remove_transaction(lowest_fee_tx.tx_id)


       
        if not tx.is_valid(utxo_manager):
            return False, "Invalid transaction"

       
        for tx_input in tx.inputs:
            utxo = (tx_input.prev_tx_id, tx_input.output_index)
            if utxo in self.spent_utxos:
                return False, "UTXO already spent in mempool"

       
        self.transactions.append(tx)

      
        for tx_input in tx.inputs:
            utxo = (tx_input.prev_tx_id, tx_input.output_index)
            self.spent_utxos.add(utxo)

        return True, "Transaction added to mempool"

    def remove_transaction(self, tx_id: str):
        """
        Remove transaction (when mined)
        """

        for tx in self.transactions:
            if tx.tx_id == tx_id:
                
                for tx_input in tx.inputs:
                    utxo = (tx_input.prev_tx_id, tx_input.output_index)
                    self.spent_utxos.discard(utxo)

                self.transactions.remove(tx)
                return

    def get_top_transactions(self, n: int) -> list:
        """
        Return top N transactions by fee (highest first)
        """

        
        sorted_txs = sorted(self.transactions, key=lambda tx: tx.fee, reverse=True)
        return sorted_txs[:n]

    def clear(self):
        """
        Clear all transactions
        """
        self.transactions.clear()
        self.spent_utxos.clear()

