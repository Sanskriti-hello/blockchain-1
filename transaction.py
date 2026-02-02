from typing import List, Dict, Tuple, Set

class Transaction:
    """
    Transaction structure:
    {
        "tx_id": str,
        "inputs": [
            {
                "prev_tx": str,
                "index": int,
                "owner": str
            }
        ],
        "outputs": [
            {
                "amount": float,
                "address": str
            }
        ]
    }
    """

    def __init__(self, tx_id: str, inputs: List[Dict], outputs: List[Dict]):
        self.tx_id = tx_id
        self.inputs = inputs
        self.outputs = outputs
        self.fee = 0.0


def validate_transaction(
    tx: Transaction,
    utxo_manager,
    is_utxo_spent_in_mempool=None
) -> float:
    """
    Validate a transaction using UTXO rules.

    Parameters:
    - tx: Transaction to validate
    - utxo_manager: UTXOManager instance
    - is_utxo_spent_in_mempool: optional function
      (tx_id: str, index: int) -> bool

    Returns:
    - Transaction fee

    Raises:
    - ValueError if transaction is invalid
    """

    input_sum = 0.0
    output_sum = 0.0
    seen_inputs: Set[Tuple[str, int]] = set()

    # Validate inputs
    for inp in tx.inputs:
        prev_tx = inp["prev_tx"]
        index = inp["index"]
        utxo_key = (inp["prev_tx"], inp["index"])

        # Rule 2: No double spending within same transaction
        if utxo_key in seen_inputs:
            raise ValueError(f"Double spending detected in {utxo_key} transaction inputs")
        seen_inputs.add(utxo_key)

        # Rule 1: Input UTXO must exist
        if not utxo_manager.exists(inp["prev_tx"], inp["index"]):
            raise ValueError(f"UTXO {utxo_key} does not exist")

        utxo = utxo_manager.utxo_set[utxo_key]

        # Ownership check
        if utxo["owner"] != inp["owner"]:
            raise ValueError("Input owner does not match UTXO owner")

        # Rule 5: No conflict with mempool (delegated)
        if is_utxo_spent_in_mempool is not None:
            if is_utxo_spent_in_mempool(inp["prev_tx"], inp["index"]):
                raise ValueError("UTXO already spent in unconfirmed transaction")

        input_sum += utxo["amount"]


    # Validate outputs
    for out in tx.outputs:
        # Rule 4: No negative outputs
        if out["amount"] <= 0:
            raise ValueError("Output amount must be positive")
        output_sum += out["amount"]

    # Rule 3: Sum(inputs) ≥ Sum(outputs)
    if input_sum < output_sum:
        raise ValueError("Insufficient input balance")

    tx.fee = input_sum - output_sum
    return True, tx.fee