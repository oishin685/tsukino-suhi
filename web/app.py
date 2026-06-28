import streamlit as st
import sqlite3
import os
import pandas as pd
import plotly.express as px
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


# ── キャッシュ付きクエリ ─────────────────────────────────

@st.cache_data
def load_genzai_by_decade():
    df = pd.read_sql("""
        SELECT decade, genzai_kanzen, COUNT(*) as count
        FROM dates
        GROUP BY decade, genzai_kanzen
        ORDER BY decade, genzai_kanzen
    """, get_conn())
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
    """, get_conn())


@st.cache_data
def load_mirai_dist():
    return pd.read_sql("""
        SELECT mirai_kanzen as number, COUNT(*) as count
        FROM dates
        GROUP BY mirai_kanzen
        ORDER BY mirai_kanzen
    """, get_conn())


# ── ページ: 日付検索 ──────────────────────────────────────

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

        cols = st.columns(2)
        for i, (label, mc, kc) in enumerate(LABELS_6):
            with cols[i % 2]:
                val = fmt_6(row[mc], row[kc])
                st.metric(label=label, value=val)

        st.divider()
        st.caption("さらに見ていく数字")
        cols2 = st.columns(4)
        for i, (label, mc, kc) in enumerate(LABELS_EXTRA):
            with cols2[i]:
                val = fmt_extra(row[mc], row[kc])
                st.metric(label=label, value=val)


# ── ページ: 統計 ─────────────────────────────────────────

def page_stats():
    st.title("📊 月の数秘®︎ 統計")

    # 現在数：10年ごとの分布
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

    # 過去数の分布
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

    # 未来数の分布
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


# ── ナビゲーション ───────────────────────────────────────

page = st.sidebar.radio(
    "メニュー",
    ["🔍 日付検索", "📊 統計"],
)

if page == "🔍 日付検索":
    page_search()
else:
    page_stats()
