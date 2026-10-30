import json
import sqlite3
from pathlib import Path

class Spool:
    # SQLite WAL durable local queue on dedicated data VHDX.
    def __init__(self, filename):
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(filename)
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute("""CREATE TABLE IF NOT EXISTS queue (
          seq INTEGER PRIMARY KEY AUTOINCREMENT,
          sample_id TEXT NOT NULL UNIQUE,
          ts TEXT NOT NULL,
          machine_id TEXT NOT NULL,
          source TEXT NOT NULL,
          payload TEXT NOT NULL
        )""")
        self.db.commit()
    def add(self, sample):
        with self.db:
            self.db.execute('INSERT OR IGNORE INTO queue (sample_id,ts,machine_id,source,payload) VALUES (?,?,?,?,?)',
                (sample['sample_id'],sample['ts'],sample['machine_id'],sample['source'],json.dumps(sample['values'],allow_nan=False)))
    def batch(self, limit=100):
        return self.db.execute('SELECT seq, sample_id, ts, machine_id, source, payload FROM queue ORDER BY seq LIMIT ?', (limit,)).fetchall()
    def delete(self, seqs):
        with self.db:
            self.db.executemany('DELETE FROM queue WHERE seq=?', [(x,) for x in seqs])
    def count(self):
        return self.db.execute('SELECT count(*) FROM queue').fetchone()[0]
