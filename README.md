# Bitcoin Transaction & UTXO Simulator

## Course Information

**CS 216 – Introduction to Blockchain**
Assignment: **Bitcoin Transaction & UTXO Simulator**
Submission: Public GitHub Repository

---

## Project Overview

This project implements a **simplified simulation of Bitcoin’s transaction system** using the **UTXO (Unspent Transaction Output) model**. The simulator demonstrates how transactions are created, validated, temporarily stored, and finally confirmed through mining, while preventing double-spending.

The implementation follows the specifications given in the CS 216 assignment document and is designed as a **local, single-node simulation** (no networking or cryptography involved).

---

## Learning Objectives

Through this project, we demonstrate:

* Understanding of the **UTXO model** and how balances are derived
* Correct implementation of **Bitcoin-style transaction validation rules**
* Prevention of **double-spending** using UTXO tracking and mempool checks
* Simulation of the **transaction lifecycle** from creation to confirmation
* Basic understanding of **miner incentives and transaction fees**

---

## Features Implemented

### Part 1: UTXO Manager

#### Theoretical Foundation

The **Unspent Transaction Output (UTXO)** model is the fundamental accounting mechanism in Bitcoin. Unlike account-based systems (like traditional banks or Ethereum), Bitcoin doesn't maintain account balances. Instead:

- **UTXOs are discrete chunks of Bitcoin** that represent spendable amounts
- Each UTXO is created as an output of a transaction
- Once spent, a UTXO is consumed entirely and cannot be reused
- New UTXOs are created from the outputs of new transactions
- A user's "balance" is the sum of all UTXOs they control

**Key Analogy**: Think of UTXOs like physical cash bills. If you have a $50 bill and want to pay $30, you must:
1. Give the entire $50 bill (consume the UTXO)
2. Receive $30 worth of goods (create output to recipient)
3. Receive $20 in change (create change output back to yourself)

#### Implementation Details

| **Component** | **Function** | **Purpose** | **Key Logic** |
|---------------|--------------|-------------|---------------|
| **UTXO Storage** | `UTXOManager.__init__()` | Initialize the UTXO set as a dictionary | `utxo_set: Dict[Tuple[str, int], Dict[str, object]]` stores `(tx_id, index) → {amount, owner}` |
| **Add UTXO** | `add_utxo()` | Create a new unspent output | Validates `amount > 0`, creates key `(tx_id, index)`, stores `{amount, owner}` |
| **Remove UTXO** | `remove_utxo()` | Mark a UTXO as spent | Checks existence with `key in utxo_set`, raises `KeyError` if not found, deletes from dictionary |
| **Check Existence** | `exists()` | Verify if a UTXO is unspent | Returns `(tx_id, index) in self.utxo_set` - O(1) lookup |
| **Calculate Balance** | `get_balance()` | Sum all UTXOs for an owner | Iterates through all UTXOs, sums amounts where `utxo["owner"] == owner` |
| **Get Owner's UTXOs** | `get_utxos_for_owner()` | Retrieve all spendable UTXOs | Returns list of `(tx_id, index, amount)` tuples for specific owner |
| **Snapshot** | `get_snapshot()` | Save current UTXO state | Deep copy of `utxo_set` for rollback capability during failed mining |
| **Load Snapshot** | `load_snapshot()` | Restore previous state | Replaces current `utxo_set` with saved snapshot |


---

### Part 2: Transaction Structure & Validation

#### Theoretical Foundation

A Bitcoin transaction transforms existing UTXOs into new UTXOs through the following lifecycle:

```
Creation → Validation → Mempool → Mining → Confirmation
```

**Stages Explained**:

1. **Creation**: User selects input UTXOs and specifies output amounts
2. **Validation**: System verifies all rules are satisfied
3. **Mempool**: Valid transactions wait in memory pool
4. **Mining**: Miner includes transaction in a block
5. **Confirmation**: Transaction becomes permanent, UTXOs updated

#### Implementation Details

| **Stage** | **Function** | **Purpose** | **Key Operations** |
|-----------|--------------|-------------|-------------------|
| **Transaction Creation** | `create_transaction()` | Build a transaction from sender to recipient | 1. Get sender's UTXOs via `get_utxos_for_owner()`<br>2. Sort by amount (descending)<br>3. Select UTXOs until `total >= amount + fee`<br>4. Create `TransactionInput` objects<br>5. Create output to recipient<br>6. Create change output if `change > 0.0001 BTC`<br>7. Generate unique `tx_id` |
| **Input Creation** | `TransactionInput.__init__()` | Reference a previous UTXO to spend | Stores `prev_tx_id`, `output_index`, `owner` (simulates signature) |
| **Output Creation** | `TransactionOutput.__init__()` | Specify new UTXO to create | Stores `amount` and recipient `address` |
| **Transaction Structure** | `Transaction.__init__()` | Bundle inputs and outputs | Stores `tx_id`, `inputs: List`, `outputs: List`, `fee`, `is_validated` flag |
| **ID Generation** | `generate_tx_id()` | Create unique identifier | Combines `sender`, `recipient`, `timestamp_ms`, `random_4_digits` |

---
## Part 3: Validation Rules

#### Theoretical Foundation

Bitcoin enforces strict validation rules to maintain consensus and prevent fraud:

1. **All inputs must exist**: Cannot spend non-existent or already-spent UTXOs
2. **No double-spending within transaction**: Each UTXO can only be used once per transaction
3. **Sufficient funds**: Sum of inputs ≥ Sum of outputs
4. **Positive outputs**: All output amounts must be > 0
5. **Ownership verification**: Spender must prove ownership of inputs
6. **Mempool conflict check**: UTXO not already spent by unconfirmed transaction

####  Implementation Details

| **Validation Rule** | **Function** | **Implementation** | **Error Handling** |
|---------------------|--------------|--------------------|--------------------|
| **Input Existence** | `validate_transaction()` - Check 1 | For each input:<br>`if not utxo_manager.exists(prev_tx_id, index):`<br>&nbsp;&nbsp;&nbsp;&nbsp;`raise ValueError("UTXO does not exist")` | Prevents spending non-existent UTXOs |
| **No Internal Double-Spend** | `validate_transaction()` - Check 2 | Maintain `seen_inputs: Set[Tuple]`<br>For each input:<br>`if (tx_id, index) in seen_inputs:`<br>&nbsp;&nbsp;&nbsp;&nbsp;`raise ValueError("Double spending")` | Prevents using same UTXO twice in one TX |
| **Ownership Match** | `validate_transaction()` - Check 3 | `utxo_owner = utxo_manager.get_utxo_owner(...)`<br>`if utxo_owner != input.owner:`<br>&nbsp;&nbsp;&nbsp;&nbsp;`raise ValueError("Owner mismatch")` | Simulates signature verification |
| **Mempool Conflict** | `validate_transaction()` - Check 4 | `if (tx_id, index) in mempool_spent_utxos:`<br>&nbsp;&nbsp;&nbsp;&nbsp;`raise ValueError("Already spent in mempool")` | Enforces first-seen rule |
| **Sufficient Balance** | `validate_transaction()` - Check 5 | `input_sum = sum(input amounts)`<br>`output_sum = sum(output amounts)`<br>`if input_sum < output_sum:`<br>&nbsp;&nbsp;&nbsp;&nbsp;`raise ValueError("Insufficient funds")` | Prevents creating money from nothing |
| **Positive Outputs** | `validate_transaction()` - Check 6 | For each output:<br>`if amount <= 0:`<br>&nbsp;&nbsp;&nbsp;&nbsp;`raise ValueError("Invalid amount")` | Prevents negative or zero outputs |

---

### Part 4: Mempool Management

#### Theoretical Foundation

The **mempool** (memory pool) is a temporary storage area for valid but unconfirmed transactions. Key concepts:

- **Holding Area**: Transactions wait here until included in a block
- **First-Seen Rule**: First transaction spending a UTXO is accepted; subsequent attempts rejected
- **Fee-Based Priority**: Higher-fee transactions are typically mined first
- **Conflict Detection**: Prevents double-spending across multiple unconfirmed transactions
- **Size Limits**: Mempool has capacity limits; lowest-fee transactions may be evicted

#### Implementation Details

| **Operation** | **Function** | **Purpose** | **Algorithm** |
|---------------|--------------|-------------|---------------|
| **Initialize** | `Mempool.__init__()` | Create mempool data structures | `transactions: List[Transaction]` - stores TXs<br>`spent_utxos: Set[Tuple]` - tracks used UTXOs<br>`tx_by_id: Dict[str, Transaction]` - fast lookup<br>`max_size: int` - capacity limit |
| **Add Transaction** | `add_transaction()` | Validate and accept new TX | **Step 1**: Check if TX already in mempool<br>**Step 2**: If mempool full, evict lowest-fee TX<br>**Step 3**: Validate TX via `tx.is_valid()`<br>**Step 4**: Check UTXO conflicts with `spent_utxos`<br>**Step 5**: Add TX to all data structures<br>**Step 6**: Mark input UTXOs as spent<br>**Step 7**: Return success/failure message |
| **Remove Transaction** | `remove_transaction()` | Remove TX after mining | **Step 1**: Lookup TX by ID<br>**Step 2**: Remove from `spent_utxos` set<br>**Step 3**: Remove from `transactions` list<br>**Step 4**: Delete from `tx_by_id` dict |
| **Get Top TXs** | `get_top_transactions()` | Select TXs for mining | Sort by fee (descending)<br>Return top N transactions |
| **Check UTXO Spent** | `is_utxo_spent()` | Query if UTXO is in use | Returns `(tx_id, index) in self.spent_utxos` |
| **Clear Mempool** | `clear()` | Reset all data structures | Empty all lists, sets, and dicts |
| **Get Statistics** | `get_statistics()` | Analyze mempool state | Calculate: size, total fees, avg/max/min fee |

---

### Part 5: Mining Simulation

#### Theoretical Foundation

Mining is the process of:

1. **Selecting Transactions**: Choose pending transactions from mempool
2. **Creating a Block**: Bundle selected transactions together
3. **Updating UTXO Set**: Apply all transaction effects permanently
4. **Issuing Coinbase Reward**: Miner receives transaction fees
5. **Clearing Mempool**: Remove confirmed transactions

**Key Concepts**:
- **Block Height**: Sequential block number in the blockchain
- **Coinbase Transaction**: Special transaction that creates new coins (in our case, just fees)
- **Transaction Fees**: Miners collect sum of all fees from included transactions
- **Atomicity**: All transactions in a block succeed or none do (rollback on error)

#### Implementation Details

| **Mining Stage** | **Function** | **Purpose** | **Detailed Steps** |
|------------------|--------------|-------------|--------------------|
| **Block Structure** | `Block.__init__()` | Define block data structure | **Fields**:<br>• `block_height`: Position in chain<br>• `timestamp`: Unix timestamp<br>• `transactions`: List of confirmed TXs<br>• `miner`: Recipient of fees<br>• `total_fees`: Sum of all TX fees<br>• `coinbase_tx_id`: Unique ID for fee reward |
| **Initiate Mining** | `mine_block()` | Orchestrate entire mining process | **Step 1**: Select top N transactions by fee<br>**Step 2**: Create UTXO snapshot for rollback<br>**Step 3**: Validate each TX (may be invalid now)<br>**Step 4**: Apply TX effects to UTXO set<br>**Step 5**: Calculate total fees<br>**Step 6**: Create coinbase UTXO<br>**Step 7**: Remove TXs from mempool<br>**Step 8**: Increment block height<br>**Step 9**: Return Block object |
| **TX Selection** | `mempool.get_top_transactions()` | Choose TXs to include | Sort by `fee` (descending)<br>Return first `num_txs` transactions<br>Miners prioritize profit |
| **UTXO Update** | Inside `mine_block()` loop | Make transactions permanent | **For each TX**:<br>1. Remove all input UTXOs<br>2. Create all output UTXOs<br>3. Accumulate fee |
| **Coinbase Creation** | Inside `mine_block()` | Reward miner | `utxo_manager.add_utxo(`<br>&nbsp;&nbsp;`coinbase_tx_id,`<br>&nbsp;&nbsp;`0,`<br>&nbsp;&nbsp;`total_fees,`<br>&nbsp;&nbsp;`miner_address`<br>`)` |
| **Mempool Cleanup** | `mempool.remove_transaction()` | Clear confirmed TXs | For each successfully applied TX:<br>`mempool.remove_transaction(tx.tx_id)` |
| **Error Handling** | `utxo_manager.load_snapshot()` | Rollback on failure | If any TX fails:<br>Restore UTXO set to pre-mining state<br>Return `None` (mining failed) |


---

### Part 6: Double-Spending Prevention

#### Theoretical Foundation

**Double-spending** is the act of spending the same UTXO more than once. Bitcoin prevents this through multiple mechanisms:

1. **Within-Transaction Check**: Same UTXO cannot appear multiple times in one transaction's inputs
2. **UTXO Set Check**: UTXO must exist (not already spent in a previous confirmed transaction)
3. **Mempool Conflict Check**: UTXO cannot be used by two different pending transactions
4. **First-Seen Rule**: First transaction spending a UTXO is accepted; later attempts rejected
5. **Mining Validation**: Transactions are re-validated during mining (UTXO may have been spent by earlier TX in same block)

#### Implementation Details

| **Prevention Layer** | **Function** | **Check Logic** | **Example Scenario** |
|----------------------|--------------|-----------------|----------------------|
| **Internal Double-Spend** | `validate_transaction()` | Maintain `seen_inputs: Set`<br>For each input:<br>`if utxo in seen_inputs:`<br>&nbsp;&nbsp;`raise ValueError()` | **Attack**: TX with inputs `[(genesis,0), (genesis,0)]`<br>**Result**: Rejected - duplicate input detected |
| **UTXO Existence** | `validate_transaction()` | For each input:<br>`if not utxo_mgr.exists(tx_id, idx):`<br>&nbsp;&nbsp;`raise ValueError()` | **Attack**: Spend `(genesis, 0)` after Alice already spent it<br>**Result**: Rejected - UTXO doesn't exist |
| **Mempool Conflict** | `mempool.add_transaction()` | For each input:<br>`if utxo in spent_utxos:`<br>&nbsp;&nbsp;`return False, "conflict"` | **Attack**: TX1 spends `(genesis,0)`, TX2 tries to spend `(genesis,0)`<br>**Result**: TX1 accepted, TX2 rejected |
| **First-Seen Rule** | `mempool.add_transaction()` | When conflict detected:<br>Find `conflicting_tx_id`<br>Return error message | **Result**: "UTXO already spent by tx_X (first-seen rule)" |
| **Mining Re-validation** | `mine_block()` | Before applying TX:<br>`is_valid, msg = tx.is_valid(utxo_mgr)`<br>If invalid, skip TX | **Scenario**: Two mempool TXs spend same UTXO<br>**Result**: First TX mined, second becomes invalid |

## Key Design Decisions

### Decision 1: No Unconfirmed Chain Spending

**Decision**: Only confirmed (mined) UTXOs can be spent.

**Rationale**:
- Prevents mempool complexity
- Avoids issues with chain reorganizations
- Simplifies transaction validation

**Trade-off**:
- Real Bitcoin allows spending unconfirmed outputs
- Our simulation is more conservative

### Decision 2: First-Seen Rule Enforcement

**Decision**: First transaction spending a UTXO is accepted; later ones rejected.

**Rationale**:
- Prevents race attacks
- Provides predictable behavior
- Protects merchants from double-spending

**Alternative**: Replace-by-fee (RBF) - allow higher-fee TX to replace lower-fee TX
- More complex to implement
- Can enable attacks on merchants

### Decision 3: Greedy UTXO Selection

**Decision**: Select largest UTXOs first.

**Rationale**:
- Minimizes number of inputs
- Reduces transaction size
- Simple to implement

**Alternative**: Optimal selection algorithms
- More complex
- Marginal benefits in simulation

### Decision 4: Explicit Fee Model

**Decision**: Fee = Inputs - Outputs (implicit)

**Rationale**:
- Matches Bitcoin protocol
- Encourages understanding of fee mechanism
- Prevents accidental high fees (user must calculate change)

**Alternative**: Explicit fee parameter
- Easier for users
- Doesn't match real Bitcoin

### Decision 5: Mempool Size Limit

**Decision**: Fixed maximum size with fee-based eviction.

**Rationale**:
- Prevents memory exhaustion
- Incentivizes competitive fees
- Mimics real node behavior

**Configuration**:
```python
max_size = 50  # Maximum pending transactions
```
---

## Project Structure

The repository follows the structure shown below (as implemented in this submission):

```
blockchain-1/
├── src/
│   ├── __init__.py
│   ├── main.py            # Entry point (menu-driven interface)
│   ├── utxo_manager.py    # UTXO management logic
│   ├── transaction.py     # Transaction structure & validation
│   ├── mempool.py         # Mempool management & conflict detection
│   └── block.py           # Mining simulation & block creation
│
├── test/
│   ├── __init__.py
│   └── testing.py         # Comprehensive test suite (10/10 tests)
│
├── main_output.txt        # Sample output from running main.py
├── tests_output.txt       # Sample output from running testing.py
├── README.md              # Project documentation
└── __pycache__/           # Auto-generated Python cache files
```

---

## How to Run

### Requirements

* Python 3.8 or higher
* No external libraries required

### Steps

1. Clone the repository:

```bash
git clone <repository-url>
cd blockchain-1
```

2. Run the main program:

```bash
python src/main.py
```

3. (Optional) Run test cases:

```bash
python test/testing.py
```

---

## Example Workflow

1. Create a new transaction (select inputs and outputs)
2. Transaction is validated using UTXO and mempool rules
3. Valid transactions enter the mempool
4. Mining confirms transactions and updates the UTXO set
5. Miner receives accumulated transaction fees

---

## Test Scenarios

The project includes test cases demonstrating:

* Valid transactions with change output
* Multiple-input transactions
* Double-spending within a transaction
* Double-spending across transactions (mempool conflict)
* Insufficient balance errors
* Negative output rejection
* Zero-fee transactions
* Basic race-attack simulation

---

## Design Notes

* This is a **simulation**, not a real blockchain implementation
* No cryptographic signatures or networking are used
* Ownership is simulated using string comparison
* Emphasis is on correctness and clarity of logic rather than performance

---

## Team Information

**Team Name:** *HighOnByte*

**Team Members:**

1. Aastha          – 240004001
2. Bhavika Jaiswal – 240001017
3. Sankriti Jain   – 240001064
4. Suhani          – 240001077

---

## Declaration

This project is an original implementation created for academic purposes as part of CS 216. No external blockchain libraries were used.
