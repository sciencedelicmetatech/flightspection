# FlightSpection
**Tamper-Evident Memory and Order-Invariant Reasoning for Trustworthy Agency**

FlightSpection is a pure-Python, zero-dependency reference integration that replaces silent-wrong AI memory with explicit `Err(Tamper)` refusals. 

It combines two layers:
*   **L1 (Recallspection):** Tamper-evident, HMAC-tagged, hash-chained memory (Validated at **AGMI L4**).
*   **L2 (Orderspector):** Order-sensitivity detection with a fail-closed proposer tier.

## The Headline Result
In 1,000 adversarial trials, a naive vector store produced an **11.4% silent-wrong** rate. FlightSpection produced **0.0% silent-wrong** answers (with a 52% safe refusal rate).

## Quickstart
No pip install. No dependencies. Python 3.8+.

```bash
git clone https://github.com/sciencedelicmetatech/flightspection
cd flightspection
python run_all.py