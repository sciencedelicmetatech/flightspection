# FlightSpection
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23378369.svg)](https://doi.org/10.5281/zenodo.23378369)
[![AGMI L4](https://img.shields.io/badge/AGMI-L4-success)](https://agentmemoryintegrity.org/stores/recallspection-exact-anchor.html)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![CI](https://github.com/sciencedelicmetatech/flightspection/actions/workflows/ci.yml/badge.svg)](https://github.com/sciencedelicmetatech/flightspection/actions/workflows/ci.yml)

**Tamper-Evident Memory and Order-Invariant Reasoning for Trustworthy Agency**

FlightSpection is a pure-Python, zero-dependency reference integration that replaces silent-wrong AI memory with explicit `Err(Tamper)` refusals. 

Current AI architectures conflate fuzzy reasoning with fuzzy memory, leading to silent hallucinations and the "Fried Brain Effect" (human cognitive overload caused by acting as the out-of-band memory layer). FlightSpection solves this by separating the exact memory layer (L1) from the fuzzy reasoning layer (L2).

## The Headline Result
In 1,000 end-to-end adversarial trials, a naive vector store produced an **11.4% silent-wrong** rate. FlightSpection produced **0.0% silent-wrong** answers (with a 52% safe refusal rate). 

It converts wrong answers into explicit refusals.

## Architecture

```text
[ L1: Exact Memory (Recallspection) ] 
  - HMAC-SHA256 tags
  - SHA-256 hash chains
  - AGMI L4 Validated
          |
          v
[ The Bridge (FlightSpection) ] 
  - Refuses to execute if memory is tampered
  - Returns Err(Tamper) instead of guessing
          |
          v
[ L2: Reasoning (Orderspector) ] 
  - Sound, complete verifier
  - Fail-closed static proposers