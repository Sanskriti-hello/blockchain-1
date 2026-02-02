import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from typing import Dict, Tuple, List
import copy

# manages unspent transaction outputs (utxos)
class UTXOManager:
    # initializes the utxo manager
    def __init__(self):
        self.utxo_set: Dict[Tuple[str, int], Dict[str, object]] = {}

    # adds a new utxo
    def add_utxo(self, tx_id: str, index: int, amount: float, owner: str) -> None:
        if amount <= 0:
            raise ValueError(f"utxo amount must be positive, got {amount}")

        key = (tx_id, index)
        self.utxo_set[key] = {
            "amount": amount,
            "owner": owner
        }

    # removes a utxo
    def remove_utxo(self, tx_id: str, index: int) -> None:
        key = (tx_id, index)
        if key not in self.utxo_set:
            raise KeyError(f"utxo {key} does not exist or already spent")

        del self.utxo_set[key]

    # checks if a utxo exists
    def exists(self, tx_id: str, index: int) -> bool:
        return (tx_id, index) in self.utxo_set

    # calculates balance for an owner
    def get_balance(self, owner: str) -> float:
        balance = 0.0
        for utxo in self.utxo_set.values():
            if utxo["owner"] == owner:
                balance += utxo["amount"]
        return balance
    
    # returns a snapshot of the utxo set
    def get_snapshot(self) -> Dict[Tuple[str, int], Dict[str, object]]:
        return copy.deepcopy(self.utxo_set)
    
    # loads a utxo set snapshot
    def load_snapshot(self, snapshot: Dict[Tuple[str, int], Dict[str, object]]) -> None:
        self.utxo_set = copy.deepcopy(snapshot)

    # returns utxos for a specific owner
    def get_utxos_for_owner(self, owner: str) -> List[Tuple[str, int, float]]:
        results = []
        for (tx_id, index), data in self.utxo_set.items():
            if data["owner"] == owner:
                results.append((tx_id, index, data["amount"]))
        return results

    # gets the amount of a specific utxo
    def get_utxo_amount(self, tx_id: str, index: int) -> float:
        key = (tx_id, index)
        if key not in self.utxo_set:
            raise KeyError(f"utxo {key} does not exist")

        return self.utxo_set[key]["amount"]
    
    # gets the owner of a specific utxo
    def get_utxo_owner(self, tx_id: str, index: int) -> str:
        key = (tx_id, index)
        if key not in self.utxo_set:
            raise KeyError(f"utxo {key} does not exist")
        
        return self.utxo_set[key]["owner"]

    # returns human-readable utxo set
    def __str__(self) -> str:
        if not self.utxo_set:
            return "utxo set is empty."

        lines = ["current utxo set:"]
        for (tx_id, index), data in sorted(self.utxo_set.items()):
            lines.append(
                f"  ({tx_id}, {index}) -> {data['amount']:.8f} btc owned by {data['owner']}"
            )
        return "\n".join(lines)
    
    # calculates total supply
    def get_total_supply(self) -> float:
        return sum(utxo["amount"] for utxo in self.utxo_set.values())
