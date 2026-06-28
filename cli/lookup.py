#!/usr/bin/env python3
"""
使い方: python cli/lookup.py 1990-09-25
"""
import sqlite3
import sys
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "tsukino_suhi.db")

LABELS_6 = [
    ("過去数",      "kako_moto",    "kako_kanzen"),
    ("現在数",      "genzai_moto",  "genzai_kanzen"),
    ("未来数",      "mirai_moto",   "mirai_kanzen"),
    ("メッセージ数", "message_moto", "message_kanzen"),
    ("アンサー数",  "answer_moto",  "answer_kanzen"),
    ("スター数",    "star_moto",    "star_kanzen"),
]

LABELS_EXTRA = [
    ("本質",   "honshitsu_moto", "honshitsu_kanzen"),
    ("性格",   "seikaku_moto",   "seikaku_kanzen"),
    ("統合数", "tougou_moto",    "tougou_kanzen"),
    ("素質",   "soshitsu_moto",  "soshitsu_kanzen"),
]


def fmt_6(moto: int, kanzen: int) -> str:
    if moto == kanzen:
        return str(kanzen)
    return f"{moto} からの {kanzen}"


def fmt_extra(moto: int, kanzen: int) -> str:
    if moto == kanzen:
        return str(moto)
    return f"{moto}／{kanzen}"


def lookup(date_str: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM dates WHERE date = ?", (date_str,)).fetchone()
    conn.close()

    if row is None:
        print(f"日付 {date_str} はデータベースにありません")
        return

    y, m, d = row["year"], row["month"], row["day"]
    print(f"\n{y}年{m}月{d}日 の月の数秘®︎\n")
    print("─" * 36)

    for label, moto_col, kanzen_col in LABELS_6:
        val = fmt_6(row[moto_col], row[kanzen_col])
        print(f"  {label:<12} {val}")

    print("─" * 36)
    for label, moto_col, kanzen_col in LABELS_EXTRA:
        val = fmt_extra(row[moto_col], row[kanzen_col])
        print(f"  {label:<12} {val}")
    print()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("使い方: python cli/lookup.py YYYY-MM-DD")
        sys.exit(1)
    lookup(sys.argv[1])
