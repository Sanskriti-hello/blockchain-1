import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from typing import List, Set, Tuple
import time
import random

# represents a transaction input
class TransactionInput:
    # initializes a transaction input
    def __init__(self, prev_tx_id: str, output_index: int, owner: str):
        self.prev_tx_id = prev_tx_id
        self.output_index = output_index
        self.owner = owner
    
    def __repr__(self):
        return f"input({self.prev_tx_id}:{self.output_index} from {self.owner})"

# represents a transaction output
class TransactionOutput:
    # initializes a transaction output
    def __init__(self, amount: float, address: str):
        self.amount = amount
        self.address = address
    
    def __repr__(self):
        return f"output({self.amount} btc to {self.address})"

# defines transaction structure
class Transaction:
    # creates a new transaction
    def __init__(self, tx_id: str, inputs: List[TransactionInput], outputs: List[TransactionOutput]):
        self.tx_id = tx_id
        self.inputs = inputs
        self.outputs = outputs
        self.fee = 0.0
        self.is_validated = False
    
    # calculates total input amount
    def calculate_input_sum(self, utxo_manager) -> float:
        total = 0.0
        for inp in self.inputs:
            if utxo_manager.exists(inp.prev_tx_id, inp.output_index):
                total += utxo_manager.get_utxo_amount(inp.prev_tx_id, inp.output_index)
        return total
    
    # calculates total output amount
    def calculate_output_sum(self) -> float:
        return sum(out.amount for out in self.outputs)
    
    # validates transaction
    def is_valid(self, utxo_manager, mempool_spent_utxos: Set[Tuple[str, int]] = None) -> Tuple[bool, str]:
        try:
            validate_transaction(self, utxo_manager, mempool_spent_utxos)
            self.is_validated = True
            return True, "valid"
        except ValueError as e:
            return False, str(e)
    
    def __repr__(self):
        return f"transaction({self.tx_id}, {len(self.inputs)} inputs, {len(self.outputs)} outputs, fee={self.fee:.8f})"

# generates a unique transaction id
def generate_tx_id(sender: str, recipient: str = None) -> str:
    timestamp = int(time.time() * 1000)
    random_num = random.randint(1000, 9999)
    
    if recipient:
        return f"tx_{sender}_{recipient}_{timestamp}_{random_num}"
    else:
        return f"tx_{sender}_{timestamp}_{random_num}"

# validates a transaction
def validate_transaction(
    tx: Transaction,
    utxo_manager,
    mempool_spent_utxos: Set[Tuple[str, int]] = None
) -> Tuple[bool, float]:
    
    if mempool_spent_utxos is None:
        mempool_spent_utxos = set()

    input_sum = 0.0
    output_sum = 0.0
    seen_inputs: Set[Tuple[str, int]] = set()

    if not tx.inputs:
        raise ValueError("transaction must have at least one input")
    
    for inp in tx.inputs:
        utxo_key = (inp.prev_tx_id, inp.output_index)

        if utxo_key in seen_inputs:
            raise ValueError(f"double spending detected: utxo {utxo_key} used twice in same transaction")
        seen_inputs.add(utxo_key)

        if not utxo_manager.exists(inp.prev_tx_id, inp.output_index):
            raise ValueError(f"utxo {utxo_key} does not exist or already spent")

        utxo_amount = utxo_manager.get_utxo_amount(inp.prev_tx_id, inp.output_index)
        utxo_owner = utxo_manager.get_utxo_owner(inp.prev_tx_id, inp.output_index)

        if utxo_owner != inp.owner:
            raise ValueError(f"input owner mismatch: utxo owned by {utxo_owner}, claimed by {inp.owner}")

        if utxo_key in mempool_spent_utxos:
            raise ValueError(f"utxo {utxo_key} already spent by tx_{utxo_key[0]}")

        input_sum += utxo_amount
    
    if not tx.outputs:
        raise ValueError("transaction must have at least one output")
    
    for i, out in enumerate(tx.outputs):
        if out.amount <= 0:
            raise ValueError(f"output {i} has invalid amount: {out.amount} (must be positive)")
        output_sum += out.amount

    if input_sum < output_sum:
        raise ValueError(f"insufficient funds: inputs={input_sum:.8f} btc, outputs={output_sum:.8f} btc")

    fee = input_sum - output_sum
    tx.fee = fee
    
    return True, fee

# creates a transaction with automatic utxo selection
def create_transaction(
    sender: str,
    recipient: str,
    amount: float,
    utxo_manager,
    change_address: str = None
) -> Transaction:
    
    if change_address is None:
        change_address = sender
    
    available_utxos = utxo_manager.get_utxos_for_owner(sender)
    
    if not available_utxos:
        raise ValueError(f"{sender} has no utxos")
    
    selected_utxos = []
    total_selected = 0.0
    
    available_utxos.sort(key=lambda x: x[2], reverse=True)
    
    for tx_id, index, utxo_amount in available_utxos:
        selected_utxos.append((tx_id, index, utxo_amount))
        total_selected += utxo_amount
        
        if total_selected >= amount + 0.001:
            break
    
    if total_selected < amount:
        raise ValueError(f"insufficient funds: have {total_selected} btc, need {amount} btc")
    
    inputs = [
        TransactionInput(tx_id, index, sender)
        for tx_id, index, _ in selected_utxos
    ]
    
    outputs = [TransactionOutput(amount, recipient)]
    
    change = total_selected - amount - 0.001
    if change > 0.0001:
        outputs.append(TransactionOutput(change, change_address))
    
    tx_id = generate_tx_id(sender, recipient)
    
    return Transaction(tx_id, inputs, outputs)
