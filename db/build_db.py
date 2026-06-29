import sqlite3
import sys
import os
from datetime import date, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from calc.calculator import calc_all

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "tsukino_suhi.db")

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS dates (
    date        TEXT PRIMARY KEY,
    year        INTEGER NOT NULL,
    month       INTEGER NOT NULL,
    day         INTEGER NOT NULL,
    decade      INTEGER NOT NULL,

    kako_moto           INTEGER NOT NULL,
    kako_kanzen         INTEGER NOT NULL,
    genzai_moto        INTEGER NOT NULL,
    genzai_kanzen      INTEGER NOT NULL,
    mirai_moto         INTEGER NOT NULL,
    mirai_kanzen       INTEGER NOT NULL,
    message_moto       INTEGER NOT NULL,
    message_kanzen     INTEGER NOT NULL,
    answer_moto        INTEGER NOT NULL,
    answer_kanzen      INTEGER NOT NULL,
    star_moto          INTEGER NOT NULL,
    star_kanzen        INTEGER NOT NULL,
    honshitsu_moto     INTEGER NOT NULL,
    honshitsu_kanzen   INTEGER NOT NULL,
    seikaku_moto       INTEGER NOT NULL,
    seikaku_kanzen     INTEGER NOT NULL,
    tougou_moto        INTEGER NOT NULL,
    tougou_kanzen      INTEGER NOT NULL,
    soshitsu_moto      INTEGER NOT NULL,
    soshitsu_kanzen    INTEGER NOT NULL
);
"""

CREATE_INDEXES = """
CREATE INDEX IF NOT EXISTS idx_decade ON dates(decade);
CREATE INDEX IF NOT EXISTS idx_month_day ON dates(month, day);
CREATE INDEX IF NOT EXISTS idx_genzai ON dates(genzai_kanzen);
CREATE INDEX IF NOT EXISTS idx_kako ON dates(kako_kanzen);
CREATE INDEX IF NOT EXISTS idx_mirai ON dates(mirai_kanzen);
"""

INSERT_SQL = """
INSERT OR REPLACE INTO dates VALUES (
    ?, ?, ?, ?, ?,
    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
    ?, ?, ?, ?, ?, ?, ?, ?
)
"""


def build(start_year: int = 1000, end_year: int = 2509):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript(CREATE_TABLE)
    conn.executescript(CREATE_INDEXES)

    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    current = start
    batch = []
    total = 0

    while current <= end:
        y, m, d = current.year, current.month, current.day
        r = calc_all(y, m, d)
        decade = (y // 10) * 10

        batch.append((
            current.isoformat(), y, m, d, decade,
            r["kako_moto"],      r["kako_kanzen"],
            r["genzai_moto"],    r["genzai_kanzen"],
            r["mirai_moto"],     r["mirai_kanzen"],
            r["message_moto"],   r["message_kanzen"],
            r["answer_moto"],    r["answer_kanzen"],
            r["star_moto"],      r["star_kanzen"],
            r["honshitsu_moto"], r["honshitsu_kanzen"],
            r["seikaku_moto"],   r["seikaku_kanzen"],
            r["tougou_moto"],    r["tougou_kanzen"],
            r["soshitsu_moto"],  r["soshitsu_kanzen"],
        ))

        if len(batch) >= 10000:
            conn.executemany(INSERT_SQL, batch)
            conn.commit()
            total += len(batch)
            print(f"  {total:,} 件 書き込み済み（最終: {current}）")
            batch = []

        current += timedelta(days=1)

    if batch:
        conn.executemany(INSERT_SQL, batch)
        conn.commit()
        total += len(batch)

    conn.close()
    print(f"\n完了: {total:,} 件 → {DB_PATH}")


if __name__ == "__main__":
    print("DB 構築中（数分かかります）...")
    build()
