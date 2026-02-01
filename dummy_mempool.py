class DummyMempool:
    """
    Temporary mempool used only for testing mining logic.
    """

    def __init__(self, transactions):
        self.transactions = transactions

    def get_top_transactions(self, n):
        return self.transactions[:n]

    def remove_transaction(self, tx_id):
        self.transactions = [
            tx for tx in self.transactions if tx["tx_id"] != tx_id
        ]
