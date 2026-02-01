import sys
import os

sys.path.append(os.path.abspath("src"))


from utxo_manager import UTXOManager
from block import mine_block
from dummy_mempool import DummyMempool


def main():
    # Genesis UTXO
    utxo = UTXOManager()
    utxo.add_utxo("genesis", 0, 50.0, "Alice")

    print("Before mining:")
    print(utxo)
    print("-" * 40)

    # Create a sample transaction
    tx = {
        "tx_id": "tx_alice_bob_1",
        "inputs": [
            {"prev_tx": "genesis", "index": 0, "owner": "Alice"}
        ],
        "outputs": [
            {"amount": 10.0, "address": "Bob"},
            {"amount": 39.999, "address": "Alice"}
        ],
        "fee": 0.001
    }

    mempool = DummyMempool([tx])

    # Mine block
    mine_block("Miner1", mempool, utxo)

    print("-" * 40)
    print("After mining:")
    print(utxo)


if __name__ == "__main__":
    main()
