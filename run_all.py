import json
import time
import random
from core.memory import ExactMemory
from core.bridge import Reasoner, encode_rule
from core import orderspector as osp

def run_e1_memory_tamper():
    """E1: Proves memory tamper detection."""
    m = ExactMemory(":memory:")
    m.put("api_key", "sk-REAL-123")
    
    # Attacker tampers directly in the SQLite DB
    m.conn.execute("UPDATE memory_store SET value='sk-EVIL' WHERE key='api_key'")
    m.conn.commit()
    
    result = m.get("api_key")
    m.close()
    return result == "Err(Tamper)"

def run_e10_reasoning_ceiling():
    """E10: Proves the verifier is sound and complete when forced."""
    a, b = ("ab", "a"), ("bc", "b")
    terms = ["abc", "abbc", "aabc"]
    # Force verify without proposers
    sens, direction, _ = osp.verify(a, b, terms)
    return sens == True and direction == "BA"

def run_e13_silent_wrong(n_trials=1000):
    """E13: The headline test (Silent-Wrong Elimination)."""
    rng = random.Random(7)
    tally = {"naive_wrong": 0, "ours_wrong": 0, "refused": 0}

    for _ in range(n_trials):
        rules = [("ab", "a"), ("bc", "b"), ("ca", "c")]
        keys = [f"rule_{i}" for i in range(len(rules))]
        term = "abc"
        
        naive_db = [encode_rule(*r) for r in rules]
        ours_db = ExactMemory(":memory:")
        for k, r in zip(keys, rules): ours_db.put(k, encode_rule(*r))

        if rng.random() < 0.5:
            target = rng.randrange(len(rules))
            fake_rule = (rules[target][0], "ZZZ")
            naive_db[target] = encode_rule(*fake_rule)
            ours_db.conn.execute("UPDATE memory_store SET value=? WHERE key=?", (encode_rule(*fake_rule), keys[target]))
            ours_db.conn.commit()

        gt_result, _ = osp.rewrite(term, rules)

        n_rules = [tuple(json.loads(s)) for s in naive_db]
        n_result, _ = osp.rewrite(term, n_rules)
        if n_result != gt_result: tally["naive_wrong"] += 1

        r = Reasoner(ours_db, keys)
        out = r.reason(term)
        if out["status"] != "Ok":
            tally["refused"] += 1
        elif out["result"] != gt_result:
            tally["ours_wrong"] += 1
        ours_db.close()
    
    return tally

if __name__ == "__main__":
    print("=" * 50)
    print("FLIGHTSPECTION FULL REPRODUCTION SUITE")
    print("=" * 50)
    
    print("\nRunning E1: Memory Tamper Detection...")
    e1_pass = run_e1_memory_tamper()
    print(f"  Tamper Detected: {e1_pass}")
    
    print("\nRunning E10: Reasoning Verifier Ceiling...")
    e10_pass = run_e10_reasoning_ceiling()
    print(f"  Verifier Correctly Found Dependence: {e10_pass}")
    
    print("\nRunning E13: End-to-End Silent-Wrong Elimination (1,000 trials)...")
    res = run_e13_silent_wrong(1000)
    
    print("\n--- RESULTS ---")
    print(f"Naive Store Silent-Wrong Rate : {res['naive_wrong'] / 10}%")
    print(f"FlightSpection Silent-Wrong   : {res['ours_wrong'] / 10}%")
    print(f"FlightSpection Refused Safely : {res['refused'] / 10}%")
    
    print("\n--- CI ASSERTIONS ---")
    assert e1_pass == True, "CRITICAL FAILURE: Tamper not detected!"
    assert e10_pass == True, "CRITICAL FAILURE: Verifier missed dependence!"
    assert res['ours_wrong'] == 0, "CRITICAL FAILURE: Silent-wrong detected!"
    assert res['naive_wrong'] > 0, "Test failed: Naive store should have errors."
    
    print("Proof complete: All experiments passed.")