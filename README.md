# FlightSpection
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23378369.svg)](https://doi.org/10.5281/zenodo.23378369)
[![AGMI L4](https://img.shields.io/badge/AGMI-L4-success)](https://agentmemoryintegrity.org/stores/recallspection-exact-anchor.html)

**Tamper-Evident Memory and Order-Invariant Reasoning for Trustworthy Agency**

FlightSpection is a pure-Python, zero-dependency reference integration that replaces silent-wrong AI memory with explicit `Err(Tamper)` refusals. 

It combines two layers:
* **L1 (Recallspection):** Tamper-evident, HMAC-tagged, hash-chained memory. Validated at **AGMI Level L4** (9/9 adversarial attacks rejected).
* **L2 (Orderspector):** Order-sensitivity detection with a fail-closed proposer tier.

## The Headline Result
In 1,000 adversarial trials, a naive vector store produced an **11.4% silent-wrong** rate. FlightSpection produced **0.0% silent-wrong** answers (with a 52% safe refusal rate).

## Architecture