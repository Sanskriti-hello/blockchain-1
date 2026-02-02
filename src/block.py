from typing import List, Dict
from utxo_manager import UTXOManager


def mine_block(
    miner_address: str,
    mempool,
    utxo_manager: UTXOManager,
    num_txs: int = 5
) -> None:
    """
    Simulate mining a block.

    Steps:
    1. Select top transactions from mempool
    2. Permanently update the UTXO set
    3. Reward miner with transaction fees
    4. Remove mined transactions from mempool
    """

    #
    # Step 1: Select transactions
    selected_txs: List[Dict] = mempool.get_top_transactions(num_txs)

    if not selected_txs:
        print("No transactions available for mining.")
        return

    total_fees = 0.0

    # Step 2: Update UTXO set
    for tx in selected_txs:
        total_fees += tx.get("fee", 0.0)

        # Remove input UTXOs
        for inp in tx["inputs"]:
            utxo_manager.remove_utxo(
                inp["prev_tx"],
                inp["index"]
            )

        # Add output UTXOs
        for index, out in enumerate(tx["outputs"]):
            utxo_manager.add_utxo(
                tx["tx_id"],
                index,
                out["amount"],
                out["address"]
            )

    # Step 3: Miner reward (coinbase UTXO)
    utxo_manager.add_utxo(
        f"coinbase_{miner_address}",
        0,
        total_fees,
        miner_address
    )

    # Step 4: Remove mined transactions from mempool
    for tx in selected_txs:
        mempool.remove_transaction(tx["tx_id"])

    print(f"Selected {len(selected_txs)} transactions from mempool.")
    print(f"Total fees : {total_fees} BTC")
    print(f"Miner {miner_address} receives {total_fees} BTC")
    print("Block mined successfully!")
    print(f"Removed {len(selected_txs)} transactions from mempool")
