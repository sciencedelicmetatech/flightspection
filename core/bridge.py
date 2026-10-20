import json
from core import orderspector as osp

def encode_rule(lhs, rhs):
    return json.dumps([lhs, rhs])

def decode_rule(s):
    return tuple(json.loads(s))

class Reasoner:
    def __init__(self, memory, rule_keys):
        self.memory = memory
        self.rule_keys = list(rule_keys)

    def reason(self, term):
        rules = []
        for k in self.rule_keys:
            v = self.memory.get(k)
            if v.startswith("Err("):
                return {"status": v, "result": None} # The Bridge refuses
            rules.append(decode_rule(v))
        
        r, steps = osp.rewrite(term, rules)
        return {"status": "Ok", "result": r, "steps": steps}