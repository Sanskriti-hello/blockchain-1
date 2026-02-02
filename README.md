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

* Stores UTXOs as `(tx_id, index) → {amount, owner}`
* Adds new UTXOs when transaction outputs are created
* Removes UTXOs when they are spent
* Checks existence of UTXOs to prevent double spending
* Computes balance of an address by summing owned UTXOs

---

### Part 2: Transaction Structure & Validation

Each transaction consists of:

* **Transaction ID**
* **Inputs**: references to previous unspent outputs
* **Outputs**: new UTXOs created by the transaction

Validation rules implemented:

1. All input UTXOs must exist in the UTXO set
2. No UTXO can be spent twice in the same transaction
3. Sum of input amounts must be greater than or equal to sum of output amounts
4. Output amounts must be strictly positive
5. No input UTXO may already be spent by an unconfirmed transaction (mempool conflict)

The transaction fee is calculated as:

```
fee = sum(inputs) - sum(outputs)
```

---

### Part 3: Mempool Management

* Stores valid but unconfirmed transactions
* Tracks UTXOs already referenced by pending transactions
* Rejects transactions that attempt to spend UTXOs already in use
* Supports selection of top transactions based on fee

---

### Part 4: Mining Simulation

* Selects transactions from the mempool
* Permanently updates the UTXO set
* Removes confirmed transactions from the mempool
* Awards miner the total transaction fees as a special UTXO

---

### Part 5: Double-Spending Prevention

* Detects double-spending within a single transaction
* Prevents double-spending across multiple unconfirmed transactions
* Demonstrates first-seen rule through controlled test scenarios

---

## Project Structure

The repository follows the structure shown below (as implemented in this submission):

```
blockchain-1/
├── src/
│   ├── __init__.py
│   ├── main.py            # Entry point (menu-driven interface)
│   ├── utxo_manager.py    # UTXO management (Part 1)
│   ├── transaction.py     # Transaction structure & validation (Part 2)
│   ├── mempool.py         # Mempool management (Part 3)
│   └── block.py           # Mining simulation (Part 4)
│
├── test/
│   ├── __init__.py
│   └── testing.py         # Test cases for validation & double-spending
│
├── __pycache__/           # Auto-generated Python cache files
│
└── README.md              # Project documentation
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
