"""
core/memory.py — L1 Recallspection.

Tamper-evident, hash-chained, HMAC-tagged key-value memory.
"""

import hashlib
import hmac
import os
import sqlite3
import threading
import time

GENESIS = "0" * 64


class ExactMemory:
    def __init__(self, db_path=":memory:", anchor_path=None, anchor_every=1000):
        self.db_path = db_path
        self.anchor_path = anchor_path
        self.anchor_every = anchor_every
        self._puts_since_anchor = 0
        self.lock = threading.RLock()
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()
        self.secret = self._get_or_create_secret()

    def _init_db(self):
        with self.lock:
            self.conn.execute("PRAGMA journal_mode=WAL")
            self.conn.execute("PRAGMA synchronous=NORMAL")
            self.conn.execute(
                "CREATE TABLE IF NOT EXISTS memory_store ("
                " id INTEGER PRIMARY KEY AUTOINCREMENT,"
                " key TEXT NOT NULL,"
                " value TEXT NOT NULL,"
                " version INTEGER NOT NULL,"
                " timestamp REAL NOT NULL,"
                " tag TEXT NOT NULL,"
                " chain_hash TEXT NOT NULL,"
                " prev_chain_hash TEXT NOT NULL)"
            )
            self.conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_key ON memory_store(key, id)")
            self.conn.execute(
                "CREATE TABLE IF NOT EXISTS config ("
                " key TEXT PRIMARY KEY, value TEXT NOT NULL)")
            self.conn.commit()

    def _get_or_create_secret(self):
        with self.lock:
            row = self.conn.execute(
                "SELECT value FROM config WHERE key='hmac_secret'").fetchone()
            if row:
                return bytes.fromhex(row["value"])
            secret = os.urandom(32)
            self.conn.execute(
                "INSERT INTO config (key,value) VALUES ('hmac_secret', ?)",
                (secret.hex(),))
            self.conn.commit()
            return secret

    def _tag(self, k, v, ver, ts):
        payload = f"{k}|{v}|{ver}|{ts}".encode()
        return hmac.new(self.secret, payload, hashlib.sha256).hexdigest()

    def _chain(self, prev, k, v, ver, ts, tag):
        blob = f"{prev}|{k}|{v}|{ver}|{ts}|{tag}".encode()
        return hashlib.sha256(blob).hexdigest()

    def _write_anchor(self, head):
        if not self.anchor_path:
            return
        tmp = self.anchor_path + ".tmp"
        with open(tmp, "w") as f:
            f.write(head)
        os.replace(tmp, self.anchor_path)

    def _read_anchor(self):
        if not self.anchor_path or not os.path.exists(self.anchor_path):
            return None
        with open(self.anchor_path) as f:
            return f.read().strip()

    def checkpoint(self):
        with self.lock:
            row = self.conn.execute(
                "SELECT chain_hash FROM memory_store"
                " ORDER BY id DESC LIMIT 1").fetchone()
            if row:
                self._write_anchor(row["chain_hash"])
            self._puts_since_anchor = 0

    def put(self, k, v):
        with self.lock:
            row = self.conn.execute(
                "SELECT version FROM memory_store WHERE key=?"
                " ORDER BY id DESC LIMIT 1", (k,)).fetchone()
            ver = (row["version"] + 1) if row else 1
            ts = time.time()
            tag = self._tag(k, v, ver, ts)
            last = self.conn.execute(
                "SELECT chain_hash FROM memory_store"
                " ORDER BY id DESC LIMIT 1").fetchone()
            prev = last["chain_hash"] if last else GENESIS
            chain = self._chain(prev, k, v, ver, ts, tag)
            self.conn.execute(
                "INSERT INTO memory_store"
                " (key,value,version,timestamp,tag,chain_hash,prev_chain_hash)"
                " VALUES (?,?,?,?,?,?,?)",
                (k, v, ver, ts, tag, chain, prev))
            self.conn.commit()
            self._puts_since_anchor += 1
            if self.anchor_every and self._puts_since_anchor >= self.anchor_every:
                self._write_anchor(chain)
                self._puts_since_anchor = 0
            return ver, tag, chain

    def get(self, k):
        with self.lock:
            row = self.conn.execute(
                "SELECT value,version,timestamp,tag FROM memory_store"
                " WHERE key=? ORDER BY id DESC LIMIT 1", (k,)).fetchone()
            if not row:
                return "Err(Missing)"
            exp = self._tag(k, row["value"], row["version"], row["timestamp"])
            if not hmac.compare_digest(row["tag"], exp):
                return "Err(Tamper)"
            return row["value"]

    def audit(self):
        with self.lock:
            rows = self.conn.execute(
                "SELECT * FROM memory_store ORDER BY id ASC").fetchall()
        prev = GENESIS
        for i, r in enumerate(rows):
            exp_tag = self._tag(r["key"], r["value"], r["version"], r["timestamp"])
            if not hmac.compare_digest(r["tag"], exp_tag):
                return {"ok": False, "at_id": r["id"], "index": i,
                        "reason": "tag_mismatch"}
            if r["prev_chain_hash"] != prev:
                return {"ok": False, "at_id": r["id"], "index": i,
                        "reason": "chain_link_broken"}
            exp_chain = self._chain(prev, r["key"], r["value"],
                                    r["version"], r["timestamp"], r["tag"])
            if not hmac.compare_digest(r["chain_hash"], exp_chain):
                return {"ok": False, "at_id": r["id"], "index": i,
                        "reason": "chain_hash_mismatch"}
            prev = r["chain_hash"]
        anchor = self._read_anchor()
        if anchor is not None and anchor != prev:
            return {"ok": False, "reason": "anchor_mismatch",
                    "audit_head": prev, "anchor_head": anchor}
        return {"ok": True, "length": len(rows), "head": prev}

    def count(self):
        with self.lock:
            return self.conn.execute(
                "SELECT COUNT(*) AS c FROM memory_store").fetchone()["c"]

    def close(self):
        with self.lock:
            self.checkpoint()
            self.conn.close()