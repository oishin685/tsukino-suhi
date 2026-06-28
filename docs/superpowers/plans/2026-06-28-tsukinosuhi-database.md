# 月の数秘®︎ データベース＆Webアプリ 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 1900〜2500年の全日付の月の数秘®︎ 全数字をSQLiteに保存し、Streamlit WebアプリとCLIで検索・統計閲覧できるようにする

**Architecture:** SQLiteに全日付の計算済み数字を保存（219,150行）。Streamlit WebアプリはStreamlit Community Cloudにデプロイしてスマホ・PCから使えるようにする。ツクヨミ用CLIは同じSQLiteを直接参照する。

**Tech Stack:** Python 3.13, SQLite3（標準ライブラリ）, Streamlit, Pandas, Plotly Express, pytest

---

## ファイル構成

```
tsukino-suhi/
├── calc/
│   └── calculator.py       # 計算ロジック（純粋関数のみ）
├── db/
│   └── build_db.py         # 全日付をSQLiteに書き込むスクリプト
├── web/
│   └── app.py              # Streamlit Webアプリ
├── cli/
│   └── lookup.py           # ツクヨミ用CLIツール
├── tests/
│   └── test_calculator.py  # 計算ロジックのテスト
├── tsukino_suhi.db         # 生成済みDB（gitにコミットする）
├── requirements.txt
└── .gitignore
```

---

## Task 1: プロジェクトセットアップ

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`

- [ ] **Step 1: requirements.txt を作成**

```
streamlit>=1.35.0
pandas>=2.0.0
plotly>=5.18.0
pytest>=8.0.0
```

- [ ] **Step 2: .gitignore を作成**

```
__pycache__/
*.pyc
.DS_Store
*.egg-info/
.venv/
```

※ `tsukino_suhi.db` は `.gitignore` に入れない（Streamlit Community Cloud で必要なため）

- [ ] **Step 3: フォルダ作成**

```bash
mkdir -p calc db web cli tests
touch calc/__init__.py tests/__init__.py
```

- [ ] **Step 4: 依存ライブラリをインストール**

```bash
pip install streamlit pandas plotly pytest
```

期待出力: `Successfully installed ...` が出れば OK

---

## Task 2: 計算テストを先に書く（TDD）

**Files:**
- Create: `tests/test_calculator.py`

定義書にある5つの実例をテストケースとして使う。

- [ ] **Step 1: test_calculator.py を作成**

```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from calc.calculator import calc_all


# ── 浅田真央（1990-09-25）──────────────────────────────────
def test_asada_mao():
    r = calc_all(1990, 9, 25)
    assert r["kako_moto"] == 25
    assert r["kako_kanzen"] == 7
    assert r["genzai_moto"] == 35
    assert r["genzai_kanzen"] == 8
    assert r["mirai_moto"] == 16
    assert r["mirai_kanzen"] == 7
    assert r["message_moto"] == 76
    assert r["message_kanzen"] == 4
    assert r["answer_moto"] == 80
    assert r["answer_kanzen"] == 8
    assert r["star_moto"] == 96
    assert r["star_kanzen"] == 6


# ── 吉高ゆり子（1988-07-22）マスターナンバーテスト ─────────
def test_yoshitaka_yuriko():
    r = calc_all(1988, 7, 22)
    assert r["kako_moto"] == 22
    assert r["kako_kanzen"] == 22   # 22日生まれ → マスターナンバー
    assert r["genzai_moto"] == 37
    assert r["genzai_kanzen"] == 1
    assert r["mirai_moto"] == 11
    assert r["mirai_kanzen"] == 11  # 7+2+2=11 → マスターナンバー
    assert r["message_moto"] == 70
    assert r["message_kanzen"] == 7
    assert r["answer_moto"] == 77
    assert r["answer_kanzen"] == 5
    assert r["star_moto"] == 88
    assert r["star_kanzen"] == 7


# ── 清さん（1964-04-28）さらに見ていく数字のテスト ─────────
def test_kiyo_san():
    r = calc_all(1964, 4, 28)
    assert r["kako_moto"] == 28
    assert r["kako_kanzen"] == 1
    assert r["genzai_moto"] == 34
    assert r["genzai_kanzen"] == 7
    assert r["mirai_moto"] == 14
    assert r["mirai_kanzen"] == 5
    assert r["message_moto"] == 76
    assert r["message_kanzen"] == 4
    assert r["answer_moto"] == 80
    assert r["answer_kanzen"] == 8
    assert r["star_moto"] == 94
    assert r["star_kanzen"] == 4
    assert r["honshitsu_moto"] == 62
    assert r["honshitsu_kanzen"] == 8
    assert r["seikaku_moto"] == 48
    assert r["seikaku_kanzen"] == 3
    assert r["tougou_moto"] == 90
    assert r["tougou_kanzen"] == 9
    assert r["soshitsu_moto"] == 156
    assert r["soshitsu_kanzen"] == 3   # 1+5+6=12→1+2=3


# ── 藤井聡太（2002-07-19）───────────────────────────────────
def test_fujii_sota():
    r = calc_all(2002, 7, 19)
    assert r["kako_moto"] == 19
    assert r["kako_kanzen"] == 1
    assert r["genzai_moto"] == 21
    assert r["genzai_kanzen"] == 3
    assert r["mirai_moto"] == 17
    assert r["mirai_kanzen"] == 8
    assert r["message_moto"] == 57
    assert r["message_kanzen"] == 3
    assert r["answer_moto"] == 60
    assert r["answer_kanzen"] == 6
    assert r["star_moto"] == 77
    assert r["star_kanzen"] == 5
    assert r["honshitsu_moto"] == 40
    assert r["honshitsu_kanzen"] == 4
    assert r["seikaku_moto"] == 38
    assert r["seikaku_kanzen"] == 11   # 3+8=11 → マスターナンバー
    assert r["tougou_moto"] == 74
    assert r["tougou_kanzen"] == 11    # 7+4=11 → マスターナンバー


# ── イーロン・マスク（1971-06-28）─────────────────────────
def test_elon_musk():
    r = calc_all(1971, 6, 28)
    assert r["kako_moto"] == 28
    assert r["kako_kanzen"] == 1
    assert r["genzai_moto"] == 34
    assert r["genzai_kanzen"] == 7
    assert r["mirai_moto"] == 16
    assert r["mirai_kanzen"] == 7
    assert r["message_moto"] == 78
    assert r["message_kanzen"] == 6
    assert r["answer_moto"] == 84
    assert r["answer_kanzen"] == 3
    assert r["star_moto"] == 100
    assert r["star_kanzen"] == 1


# ── 29日生まれ（過去数が 29→11 になるケース）───────────────
def test_kako_29_becomes_11():
    r = calc_all(2000, 1, 29)
    assert r["kako_moto"] == 29
    assert r["kako_kanzen"] == 11   # 2+9=11 → マスターナンバー


# ── 素質が 369 に収束する確認 ────────────────────────────
def test_soshitsu_369_law():
    r = calc_all(1990, 9, 25)
    assert r["soshitsu_kanzen"] in {3, 6, 9}

    r2 = calc_all(1964, 4, 28)
    assert r2["soshitsu_kanzen"] in {3, 6, 9}

    r3 = calc_all(2002, 7, 19)
    assert r3["soshitsu_kanzen"] in {3, 6, 9}
```

- [ ] **Step 2: テストを実行してすべて FAIL することを確認**

```bash
cd "/Volumes/Kingston APFS/Claude Code/tsukino-suhi"
python -m pytest tests/test_calculator.py -v
```

期待出力: `ModuleNotFoundError: No module named 'calc'` または全テスト FAILED

---

## Task 3: 計算ロジック実装

**Files:**
- Create: `calc/__init__.py`（空ファイル）
- Create: `calc/calculator.py`

- [ ] **Step 1: calc/calculator.py を作成**

```python
def _digit_sum(n: int) -> int:
    return sum(int(c) for c in str(n))


def _reduce(n: int, stops: set) -> int:
    while n > 9 and n not in stops:
        n = _digit_sum(n)
    return n


_KAKO_STOPS = {11, 22}
_GENZAI_STOPS = {11, 22, 33}
_MIRAI_STOPS = {11}
_STD_STOPS = {11, 22, 33}


def calc_kako(day: int) -> tuple:
    moto = day
    kanzen = _reduce(moto, _KAKO_STOPS)
    return moto, kanzen


def calc_genzai(year: int, month: int, day: int) -> tuple:
    moto = sum(int(c) for c in f"{year}{month:02d}{day:02d}")
    kanzen = _reduce(moto, _GENZAI_STOPS)
    return moto, kanzen


def calc_mirai(month: int, day: int) -> tuple:
    moto = sum(int(c) for c in f"{month:02d}{day:02d}")
    kanzen = _reduce(moto, _MIRAI_STOPS)
    return moto, kanzen


def calc_message(kako_moto: int, genzai_moto: int, mirai_moto: int) -> tuple:
    moto = kako_moto + genzai_moto + mirai_moto
    kanzen = _reduce(moto, _STD_STOPS)
    return moto, kanzen


def calc_answer(message_moto: int, message_kanzen: int) -> tuple:
    moto = message_moto + message_kanzen
    kanzen = _reduce(moto, _STD_STOPS)
    return moto, kanzen


def calc_star(answer_moto: int, mirai_moto: int) -> tuple:
    moto = answer_moto + mirai_moto
    kanzen = _reduce(moto, _STD_STOPS)
    return moto, kanzen


def calc_honshitsu(kako_moto: int, genzai_moto: int) -> tuple:
    moto = kako_moto + genzai_moto
    kanzen = _reduce(moto, _STD_STOPS)
    return moto, kanzen


def calc_seikaku(genzai_moto: int, mirai_moto: int) -> tuple:
    moto = genzai_moto + mirai_moto
    kanzen = _reduce(moto, _STD_STOPS)
    return moto, kanzen


def calc_tougou(mirai_moto: int, message_moto: int) -> tuple:
    moto = mirai_moto + message_moto
    kanzen = _reduce(moto, _STD_STOPS)
    return moto, kanzen


def calc_soshitsu(message_moto: int, answer_moto: int) -> tuple:
    moto = message_moto + answer_moto
    kanzen = _reduce(moto, set())   # 止めない → 3/6/9 に収束
    return moto, kanzen


def calc_all(year: int, month: int, day: int) -> dict:
    kako_m, kako_k = calc_kako(day)
    genzai_m, genzai_k = calc_genzai(year, month, day)
    mirai_m, mirai_k = calc_mirai(month, day)
    msg_m, msg_k = calc_message(kako_m, genzai_m, mirai_m)
    ans_m, ans_k = calc_answer(msg_m, msg_k)
    star_m, star_k = calc_star(ans_m, mirai_m)
    hon_m, hon_k = calc_honshitsu(kako_m, genzai_m)
    sei_m, sei_k = calc_seikaku(genzai_m, mirai_m)
    tou_m, tou_k = calc_tougou(mirai_m, msg_m)
    sos_m, sos_k = calc_soshitsu(msg_m, ans_m)

    return {
        "kako_moto": kako_m,       "kako_kanzen": kako_k,
        "genzai_moto": genzai_m,   "genzai_kanzen": genzai_k,
        "mirai_moto": mirai_m,     "mirai_kanzen": mirai_k,
        "message_moto": msg_m,     "message_kanzen": msg_k,
        "answer_moto": ans_m,      "answer_kanzen": ans_k,
        "star_moto": star_m,       "star_kanzen": star_k,
        "honshitsu_moto": hon_m,   "honshitsu_kanzen": hon_k,
        "seikaku_moto": sei_m,     "seikaku_kanzen": sei_k,
        "tougou_moto": tou_m,      "tougou_kanzen": tou_k,
        "soshitsu_moto": sos_m,    "soshitsu_kanzen": sos_k,
    }
```

- [ ] **Step 2: テストを実行してすべて PASS することを確認**

```bash
python -m pytest tests/test_calculator.py -v
```

期待出力: `8 passed` （全テスト緑）

- [ ] **Step 3: コミット**

```bash
git add calc/ tests/
git commit -m "feat: 月の数秘計算ロジックを実装（TDD）"
```

---

## Task 4: DB構築スクリプト

**Files:**
- Create: `db/build_db.py`

- [ ] **Step 1: db/build_db.py を作成**

```python
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
    genzai_moto         INTEGER NOT NULL,
    genzai_kanzen       INTEGER NOT NULL,
    mirai_moto          INTEGER NOT NULL,
    mirai_kanzen        INTEGER NOT NULL,
    message_moto        INTEGER NOT NULL,
    message_kanzen      INTEGER NOT NULL,
    answer_moto         INTEGER NOT NULL,
    answer_kanzen       INTEGER NOT NULL,
    star_moto           INTEGER NOT NULL,
    star_kanzen         INTEGER NOT NULL,
    honshitsu_moto      INTEGER NOT NULL,
    honshitsu_kanzen    INTEGER NOT NULL,
    seikaku_moto        INTEGER NOT NULL,
    seikaku_kanzen      INTEGER NOT NULL,
    tougou_moto         INTEGER NOT NULL,
    tougou_kanzen       INTEGER NOT NULL,
    soshitsu_moto       INTEGER NOT NULL,
    soshitsu_kanzen     INTEGER NOT NULL
);
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


def build(start_year: int = 1900, end_year: int = 2500):
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(CREATE_TABLE)

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
```

- [ ] **Step 2: スクリプトを実行して DB を生成**

```bash
cd "/Volumes/Kingston APFS/Claude Code/tsukino-suhi"
python db/build_db.py
```

期待出力:
```
DB 構築中（数分かかります）...
  10,000 件 書き込み済み（最終: 1927-04-14）
  ...
完了: 219,146 件 → .../tsukino_suhi.db
```

- [ ] **Step 3: DB の中身を簡単に確認**

```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('tsukino_suhi.db')
print('行数:', conn.execute('SELECT COUNT(*) FROM dates').fetchone()[0])
print('最初の行:', conn.execute('SELECT * FROM dates LIMIT 1').fetchone())
print('最後の行:', conn.execute('SELECT * FROM dates ORDER BY date DESC LIMIT 1').fetchone())
conn.close()
"
```

期待出力: 行数が 219,000 前後、最初の行が 1900-01-01、最後が 2500-12-31

- [ ] **Step 4: コミット**

```bash
git add db/ tsukino_suhi.db
git commit -m "feat: 1900〜2500年の全日付 DB を構築"
```

---

## Task 5: CLIツール（ツクヨミ用）

**Files:**
- Create: `cli/lookup.py`

- [ ] **Step 1: cli/lookup.py を作成**

```python
#!/usr/bin/env python3
"""
使い方: python cli/lookup.py 1990-09-25
"""
import sqlite3
import sys
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "tsukino_suhi.db")

LABELS = [
    ("過去数",     "kako_moto",      "kako_kanzen"),
    ("現在数",     "genzai_moto",    "genzai_kanzen"),
    ("未来数",     "mirai_moto",     "mirai_kanzen"),
    ("メッセージ数", "message_moto",   "message_kanzen"),
    ("アンサー数",  "answer_moto",    "answer_kanzen"),
    ("スター数",   "star_moto",      "star_kanzen"),
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

    for label, moto_col, kanzen_col in LABELS:
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
```

- [ ] **Step 2: 動作確認（清さんの日付で検算）**

```bash
python cli/lookup.py 1964-04-28
```

期待出力:
```
1964年4月28日 の月の数秘®︎

────────────────────────────────────
  過去数         28 からの 1
  現在数         34 からの 7
  未来数         14 からの 5
  メッセージ数    76 からの 4
  アンサー数      80 からの 8
  スター数        94 からの 4
────────────────────────────────────
  本質          62／8
  性格          48／3
  統合数         90／9
  素質          156／3
```

- [ ] **Step 3: コミット**

```bash
git add cli/
git commit -m "feat: CLIツールを追加（日付指定で全数字を表示）"
```

---

## Task 6: Streamlit Webアプリ — 日付検索ページ

**Files:**
- Create: `web/app.py`

- [ ] **Step 1: web/app.py を作成（日付検索部分）**

```python
import streamlit as st
import sqlite3
import os
from datetime import date

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "tsukino_suhi.db")

st.set_page_config(
    page_title="月の数秘®︎ データベース",
    page_icon="🌙",
    layout="centered",
)

@st.cache_resource
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

conn = get_conn()


def fmt_6(moto: int, kanzen: int) -> str:
    if moto == kanzen:
        return str(kanzen)
    return f"{moto} からの {kanzen}"


def fmt_extra(moto: int, kanzen: int) -> str:
    if moto == kanzen:
        return str(moto)
    return f"{moto}／{kanzen}"


def page_search():
    st.title("🌙 月の数秘®︎ 数字検索")
    st.caption("生年月日を選ぶと、6つの数字とさらに見ていく数字が出ます")

    d = st.date_input(
        "生年月日",
        value=date(1990, 1, 1),
        min_value=date(1900, 1, 1),
        max_value=date(2500, 12, 31),
    )

    if d:
        row = conn.execute(
            "SELECT * FROM dates WHERE date = ?", (d.isoformat(),)
        ).fetchone()

        if row is None:
            st.error("この日付はデータベースにありません")
            return

        st.divider()
        st.subheader(f"{d.year}年{d.month}月{d.day}日")

        # 6つの数字
        labels_6 = [
            ("過去数",      "kako_moto",    "kako_kanzen"),
            ("現在数",      "genzai_moto",  "genzai_kanzen"),
            ("未来数",      "mirai_moto",   "mirai_kanzen"),
            ("メッセージ数", "message_moto", "message_kanzen"),
            ("アンサー数",  "answer_moto",  "answer_kanzen"),
            ("スター数",    "star_moto",    "star_kanzen"),
        ]
        cols = st.columns(2)
        for i, (label, mc, kc) in enumerate(labels_6):
            with cols[i % 2]:
                val = fmt_6(row[mc], row[kc])
                st.metric(label=label, value=val)

        # さらに見ていく数字
        st.divider()
        st.caption("さらに見ていく数字")
        labels_extra = [
            ("本質",   "honshitsu_moto", "honshitsu_kanzen"),
            ("性格",   "seikaku_moto",   "seikaku_kanzen"),
            ("統合数", "tougou_moto",    "tougou_kanzen"),
            ("素質",   "soshitsu_moto",  "soshitsu_kanzen"),
        ]
        cols2 = st.columns(4)
        for i, (label, mc, kc) in enumerate(labels_extra):
            with cols2[i]:
                val = fmt_extra(row[mc], row[kc])
                st.metric(label=label, value=val)


page_search()
```

- [ ] **Step 2: ローカルで起動して動作確認**

```bash
cd "/Volumes/Kingston APFS/Claude Code/tsukino-suhi"
streamlit run web/app.py
```

ブラウザが開いたら、清さんの誕生日（1964年4月28日）を選んで数字を確認する

期待動作:
- 過去数: `28 からの 1`
- 現在数: `34 からの 7`
- 本質: `62／8`

- [ ] **Step 3: コミット**

```bash
git add web/
git commit -m "feat: Streamlit 日付検索ページを追加"
```

---

## Task 7: Streamlit Webアプリ — 統計ページ

**Files:**
- Modify: `web/app.py`

- [ ] **Step 1: web/app.py に統計ページを追加**

`page_search()` 関数の定義の後、`page_search()` 呼び出しの前に以下を追加:

```python
import pandas as pd
import plotly.express as px


@st.cache_data
def load_genzai_by_decade():
    df = pd.read_sql("""
        SELECT decade, genzai_kanzen, COUNT(*) as count
        FROM dates
        GROUP BY decade, genzai_kanzen
        ORDER BY decade, genzai_kanzen
    """, conn)
    total_per_decade = df.groupby("decade")["count"].transform("sum")
    df["pct"] = (df["count"] / total_per_decade * 100).round(2)
    return df


@st.cache_data
def load_kako_dist():
    return pd.read_sql("""
        SELECT kako_kanzen as number, COUNT(*) as count
        FROM dates
        GROUP BY kako_kanzen
        ORDER BY kako_kanzen
    """, conn)


@st.cache_data
def load_mirai_dist():
    return pd.read_sql("""
        SELECT mirai_kanzen as number, COUNT(*) as count
        FROM dates
        GROUP BY mirai_kanzen
        ORDER BY mirai_kanzen
    """, conn)


def page_stats():
    st.title("📊 月の数秘®︎ 統計")

    # ── 現在数：10年ごとの分布 ──────────────────────────────
    st.subheader("現在数の分布（10年ごと）")
    df = load_genzai_by_decade()

    tab1, tab2 = st.tabs(["グラフ", "数値"])

    with tab1:
        fig = px.bar(
            df,
            x="decade",
            y="pct",
            color=df["genzai_kanzen"].astype(str),
            barmode="group",
            labels={"decade": "年代", "pct": "割合（%）", "color": "現在数"},
            title="10年ごとの現在数の割合",
        )
        fig.update_layout(xaxis=dict(dtick=10))
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        pivot = df.pivot(index="decade", columns="genzai_kanzen", values="pct").fillna(0)
        st.dataframe(pivot.style.format("{:.1f}%"), use_container_width=True)

    st.divider()

    # ── 過去数の分布（年に関係なし）────────────────────────
    st.subheader("過去数の分布（年に関係なし）")
    df_kako = load_kako_dist()
    total_kako = df_kako["count"].sum()
    df_kako["pct"] = (df_kako["count"] / total_kako * 100).round(2)

    col1, col2 = st.columns(2)
    with col1:
        fig2 = px.bar(
            df_kako,
            x=df_kako["number"].astype(str),
            y="pct",
            labels={"x": "過去数", "pct": "割合（%）"},
            title="過去数の割合",
        )
        st.plotly_chart(fig2, use_container_width=True)
    with col2:
        st.dataframe(
            df_kako[["number", "count", "pct"]].rename(
                columns={"number": "過去数", "count": "件数", "pct": "割合(%)"}
            ),
            use_container_width=True,
            hide_index=True,
        )

    st.divider()

    # ── 未来数の分布（年に関係なし）────────────────────────
    st.subheader("未来数の分布（年に関係なし）")
    df_mirai = load_mirai_dist()
    total_mirai = df_mirai["count"].sum()
    df_mirai["pct"] = (df_mirai["count"] / total_mirai * 100).round(2)

    col3, col4 = st.columns(2)
    with col3:
        fig3 = px.bar(
            df_mirai,
            x=df_mirai["number"].astype(str),
            y="pct",
            labels={"x": "未来数", "pct": "割合（%）"},
            title="未来数の割合",
        )
        st.plotly_chart(fig3, use_container_width=True)
    with col4:
        st.dataframe(
            df_mirai[["number", "count", "pct"]].rename(
                columns={"number": "未来数", "count": "件数", "pct": "割合(%)"}
            ),
            use_container_width=True,
            hide_index=True,
        )
```

- [ ] **Step 2: app.py の末尾をナビゲーション付きに書き換える**

ファイル末尾の `page_search()` の呼び出し行を以下に置き換える:

```python
page = st.sidebar.radio(
    "メニュー",
    ["🔍 日付検索", "📊 統計"],
)

if page == "🔍 日付検索":
    page_search()
else:
    page_stats()
```

- [ ] **Step 3: ローカルで起動して統計ページを確認**

```bash
streamlit run web/app.py
```

確認ポイント:
- サイドバーに「日付検索」「統計」の切り替えが出る
- 統計ページでグラフと数値テーブルが出る
- 10年ごとのグラフでタブ切り替えができる

- [ ] **Step 4: コミット**

```bash
git add web/app.py
git commit -m "feat: 統計ページを追加（現在数10年ごと・過去数・未来数の分布）"
```

---

## Task 8: GitHub 公開 ＆ Streamlit Community Cloud デプロイ

**前提:** GitHub アカウントが必要。Streamlit Community Cloud アカウントも必要（無料・GitHub ログイン）。

- [ ] **Step 1: GitHub に新しいリポジトリを作成**

GitHub の画面で:
- Repository name: `tsukino-suhi`
- Visibility: **Private**（個人データを扱うため非公開推奨）
- README: なし

- [ ] **Step 2: git init して GitHub にプッシュ**

```bash
cd "/Volumes/Kingston APFS/Claude Code/tsukino-suhi"
git init
git add requirements.txt .gitignore calc/ db/ web/ cli/ tests/ tsukino_suhi.db
git commit -m "feat: 月の数秘データベース・Webアプリ 初回リリース"
git remote add origin https://github.com/<YOUR_USERNAME>/tsukino-suhi.git
git branch -M main
git push -u origin main
```

- [ ] **Step 3: Streamlit Community Cloud でデプロイ**

1. https://share.streamlit.io/ にアクセス
2. "New app" をクリック
3. Repository: `tsukino-suhi`
4. Branch: `main`
5. Main file path: `web/app.py`
6. "Deploy!" をクリック

数分後に URL が発行される。スマホ・PC・iPad どこからでもアクセスできる。

- [ ] **Step 4: スマホで動作確認**

発行された URL をスマホで開いて:
- 日付検索が動くか
- 統計グラフが表示されるか

---

## スペック確認

| 要件 | タスク |
|------|--------|
| 1900〜2500年の全日付 | Task 4 |
| 全数字（元の数字含む） | Task 3・4 |
| 日付検索 | Task 6 |
| 現在数10年ごと統計＋グラフ | Task 7 |
| 過去数・未来数の統計＋グラフ | Task 7 |
| スマホ・iPad対応 | Task 8 |
| ツクヨミ用CLI | Task 5 |
