from typing import Dict, Tuple, List
class UTXOManager:
    """
    Stores UTXOs as:
    (tx_id, index) -> {"amount": float, "owner": str}
    """

    def __init__(self):
        # Core UTXO database
        self.utxo_set: Dict[Tuple[str, int], Dict[str, object]] = {}

    def add_utxo(self, tx_id: str, index: int, amount: float, owner: str) -> None:
        """
        Add a new UTXO to the set.
        Called when a transaction output is created.
        """
        if amount <= 0:
            raise ValueError("UTXO amount must be positive")

        key = (tx_id, index)
        self.utxo_set[key] = {
            "amount": amount,
            "owner": owner
        }

    def remove_utxo(self, tx_id: str, index: int) -> None:
        """
        Remove a UTXO once it is spent.
        Prevents double-spending.
        """
        key = (tx_id, index)
        if key not in self.utxo_set:
            raise KeyError(f"UTXO {key} does not exist or already spent")

        del self.utxo_set[key]

    def exists(self, tx_id: str, index: int) -> bool:
        """
        Check if a UTXO exists and is unspent.
        Used during transaction validation.
        """
        return (tx_id, index) in self.utxo_set

    def get_balance(self, owner: str) -> float:
        """
        Calculate total balance for an address.
        Balance = sum of all UTXOs owned.
        """
        balance = 0.0
        for utxo in self.utxo_set.values():
            if utxo["owner"] == owner:
                balance += utxo["amount"]
        return balance

    def get_utxos_for_owner(self, owner: str) -> List[Tuple[str, int, float]]:
        """
        Return all UTXOs owned by a specific address.
        Useful for transaction input selection.
        """
        results = []
        for (tx_id, index), data in self.utxo_set.items():
            if data["owner"] == owner:
                results.append((tx_id, index, data["amount"]))
        return results

    def __str__(self) -> str:
        """
        Human-readable view of the UTXO set.
        """
        if not self.utxo_set:
            return "UTXO set is empty."

        lines = ["Current UTXO Set:"]
        for (tx_id, index), data in self.utxo_set.items():
            lines.append(
                f"  ({tx_id}, {index}) -> {data['amount']} BTC owned by {data['owner']}"
            )
        return "\n".join(lines)
