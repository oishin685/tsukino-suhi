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
    layout="wide",
)


@st.cache_resource
def get_conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c


conn = get_conn()

# ── 定義 ─────────────────────────────────────────────────────────────────────

NUMBER_GROUPS = [
    {"name": "過去数",       "kanzen": "kako_kanzen",      "moto": "kako_moto"},
    {"name": "現在数",       "kanzen": "genzai_kanzen",    "moto": "genzai_moto"},
    {"name": "未来数",       "kanzen": "mirai_kanzen",     "moto": "mirai_moto"},
    {"name": "メッセージ数", "kanzen": "message_kanzen",   "moto": "message_moto"},
    {"name": "アンサー数",   "kanzen": "answer_kanzen",    "moto": "answer_moto"},
    {"name": "スター数",     "kanzen": "star_kanzen",      "moto": "star_moto"},
    {"name": "本質",         "kanzen": "honshitsu_kanzen", "moto": "honshitsu_moto"},
    {"name": "性格",         "kanzen": "seikaku_kanzen",   "moto": "seikaku_moto"},
    {"name": "統合数",       "kanzen": "tougou_kanzen",    "moto": "tougou_moto"},
    {"name": "素質",         "kanzen": "soshitsu_kanzen",  "moto": "soshitsu_moto"},
]

LABELS_6 = [
    ("過去数",       "kako_moto",    "kako_kanzen"),
    ("現在数",       "genzai_moto",  "genzai_kanzen"),
    ("未来数",       "mirai_moto",   "mirai_kanzen"),
    ("メッセージ数", "message_moto", "message_kanzen"),
    ("アンサー数",   "answer_moto",  "answer_kanzen"),
    ("スター数",     "star_moto",    "star_kanzen"),
]

LABELS_EXTRA = [
    ("本質",   "honshitsu_moto", "honshitsu_kanzen"),
    ("性格",   "seikaku_moto",   "seikaku_kanzen"),
    ("統合数", "tougou_moto",    "tougou_kanzen"),
    ("素質",   "soshitsu_moto",  "soshitsu_kanzen"),
]

COL_TO_LABEL = {"month": "月", "day": "日", "year": "年代"}
for _g in NUMBER_GROUPS:
    COL_TO_LABEL[_g["kanzen"]] = f"{_g['name']}（一桁にした値）"
    COL_TO_LABEL[_g["moto"]] = f"{_g['name']}（元の数字）"


def fmt_6(moto: int, kanzen: int) -> str:
    return str(kanzen) if moto == kanzen else f"{moto} からの {kanzen}"


def fmt_extra(moto: int, kanzen: int) -> str:
    return str(moto) if moto == kanzen else f"{moto}／{kanzen}"


def run_query(sql: str, params: list) -> pd.DataFrame:
    cur = conn.execute(sql, params)
    if not cur.description:
        return pd.DataFrame()
    cols = [d[0] for d in cur.description]
    return pd.DataFrame([tuple(r) for r in cur.fetchall()], columns=cols)


# ── 日付検索ページ ─────────────────────────────────────────────────────────────

def page_search():
    st.title("🌙 月の数秘®︎ 数字検索")
    st.caption("生年月日を選ぶと、6つの数字とさらに見ていく数字が出ます")

    d = st.date_input(
        "生年月日",
        value=date(1990, 1, 1),
        min_value=date(1900, 1, 1),
        max_value=date(2500, 12, 31),
    )

    if not d:
        return

    row = conn.execute("SELECT * FROM dates WHERE date = ?", (d.isoformat(),)).fetchone()
    if row is None:
        st.error("この日付はデータベースにありません")
        return

    st.divider()
    st.subheader(f"{d.year}年{d.month}月{d.day}日")

    cols = st.columns(2)
    for i, (label, mc, kc) in enumerate(LABELS_6):
        with cols[i % 2]:
            st.metric(label=label, value=fmt_6(row[mc], row[kc]))

    st.divider()
    st.caption("さらに見ていく数字")
    cols2 = st.columns(4)
    for i, (label, mc, kc) in enumerate(LABELS_EXTRA):
        with cols2[i]:
            st.metric(label=label, value=fmt_extra(row[mc], row[kc]))


# ── 統計探索ページ ─────────────────────────────────────────────────────────────

def page_stats():
    ROLE_OPTS = ["使わない", "絞り込み", "出力軸"]
    TIME_ROLE_OPTS = ["使わない", "出力軸"]  # 年代は期間で絞るため絞り込み不可

    with st.sidebar:
        st.divider()
        st.header("⚙️ 統計設定")

        st.subheader("📅 期間")
        c1, c2 = st.columns(2)
        with c1:
            start_year = int(st.number_input("開始年", 1900, 2500, 1900, step=1, key="sy"))
        with c2:
            end_year = int(st.number_input("終了年", 1900, 2500, 2500, step=1, key="ey"))

        granularity = int(st.selectbox(
            "年代の集計粒度",
            [1, 5, 10, 20, 50, 100],
            index=2,
            format_func=lambda x: f"{x}年ごと",
            key="gran",
        ))

        st.divider()
        st.subheader("🔢 ディメンション設定")
        st.caption("絞り込み＝値を指定して絞る　出力軸＝分布をグラフに出す")

        dim_roles = {}
        dim_values = {}

        with st.expander("📆 時間軸（月・日・年代）", expanded=False):
            for tl, tk, topts in [
                ("月",   "month", ROLE_OPTS),
                ("日",   "day",   ROLE_OPTS),
                ("年代", "year",  TIME_ROLE_OPTS),
            ]:
                r = st.radio(tl, topts, horizontal=True, key=f"role_{tk}")
                dim_roles[tk] = r
                if r == "絞り込み":
                    mv = 12 if tk == "month" else 31
                    dim_values[tk] = int(st.number_input(
                        f"{tl}の値", min_value=1, max_value=mv, value=1, key=f"val_{tk}"
                    ))

        for g in NUMBER_GROUPS:
            with st.expander(g["name"], expanded=False):
                for suffix, ck in [("一桁にした値", g["kanzen"]), ("元の数字", g["moto"])]:
                    r = st.radio(suffix, ROLE_OPTS, horizontal=True, key=f"role_{ck}")
                    dim_roles[ck] = r
                    if r == "絞り込み":
                        dim_values[ck] = int(st.number_input(
                            "値", min_value=1, value=1, key=f"val_{ck}"
                        ))

    # ── メイン ──────────────────────────────────────────────────────────────
    st.title("📊 月の数秘®︎ 統計探索")

    if start_year > end_year:
        st.error("開始年は終了年以下にしてください")
        return

    # WHERE句を構築
    base_params = [start_year, end_year]
    filter_parts = []
    filter_params = []
    for ck, role in dim_roles.items():
        if role == "絞り込み" and ck in dim_values:
            filter_parts.append(f"{ck} = ?")
            filter_params.append(dim_values[ck])

    where_base = "WHERE year >= ? AND year <= ?"
    where_all = where_base + (" AND " + " AND ".join(filter_parts) if filter_parts else "")
    all_params = base_params + filter_params
    has_filters = bool(filter_parts)

    # 対象件数
    try:
        total_count = int(run_query(
            f"SELECT COUNT(*) AS n FROM dates {where_all}", all_params
        ).iloc[0]["n"])
    except Exception as e:
        st.error(f"クエリエラー: {e}")
        return

    # サマリー表示
    filter_keys = [ck for ck in dim_roles if dim_roles[ck] == "絞り込み"]
    filter_text = "なし" if not filter_parts else "、".join(
        f"{COL_TO_LABEL.get(ck, ck)} = {dim_values[ck]}" for ck in filter_keys if ck in dim_values
    )
    mc1, mc2 = st.columns([1, 3])
    with mc1:
        st.metric("対象件数", f"{total_count:,} 件")
    with mc2:
        st.caption(f"期間：{start_year}〜{end_year}年 ／ 絞り込み：{filter_text}")

    # 出力軸を収集
    output_dims = []
    for ck, role in dim_roles.items():
        if role != "出力軸":
            continue
        if ck == "year":
            lbl = f"年代（{granularity}年ごと）"
            gexpr = f"(year / {granularity}) * {granularity}"
        else:
            lbl = COL_TO_LABEL.get(ck, ck)
            gexpr = ck
        output_dims.append({"label": lbl, "col": ck, "group_expr": gexpr})

    if not output_dims:
        st.info("サイドバーで「出力軸」を選ぶと分布グラフが表示されます。絞り込みと組み合わせて自由に探索できます。")
        return

    # 各出力軸の結果
    for dim in output_dims:
        st.divider()
        st.subheader(f"📈 {dim['label']}")

        gexpr = dim["group_expr"]
        lbl = dim["label"]

        q_filtered = f"""
            SELECT {gexpr} AS val, COUNT(*) AS count
            FROM dates {where_all}
            GROUP BY {gexpr} ORDER BY val
        """
        q_total = f"""
            SELECT {gexpr} AS val, COUNT(*) AS total
            FROM dates {where_base}
            GROUP BY {gexpr} ORDER BY val
        """

        try:
            df_f = run_query(q_filtered, all_params)
            df_t = run_query(q_total, base_params)
        except Exception as e:
            st.error(f"クエリエラー: {e}")
            continue

        if df_f.empty:
            st.warning("条件に一致するデータがありませんでした")
            continue

        df = df_f.merge(df_t, on="val", how="left")
        df["絞り込み内の割合(%)"] = (df["count"] / df["count"].sum() * 100).round(2)
        if has_filters:
            df["グループ内の発生率(%)"] = (df["count"] / df["total"] * 100).round(4)

        df = df.rename(columns={"val": lbl, "count": "件数", "total": "グループ合計"})
        df[lbl] = df[lbl].astype(str)

        tab_g, tab_t = st.tabs(["グラフ", "数値表"])

        with tab_g:
            if has_filters:
                gc1, gc2 = st.columns(2)
                with gc1:
                    fig1 = px.bar(
                        df, x=lbl, y="絞り込み内の割合(%)",
                        title="絞り込み内での分布",
                        text="絞り込み内の割合(%)",
                    )
                    fig1.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
                    fig1.update_layout(yaxis_title="割合（%）")
                    st.plotly_chart(fig1, use_container_width=True)
                with gc2:
                    fig2 = px.bar(
                        df, x=lbl, y="グループ内の発生率(%)",
                        title="グループ全体に対する発生率",
                        text="グループ内の発生率(%)",
                    )
                    fig2.update_traces(texttemplate="%{text:.3f}%", textposition="outside")
                    fig2.update_layout(yaxis_title="発生率（%）")
                    st.plotly_chart(fig2, use_container_width=True)
            else:
                fig = px.bar(
                    df, x=lbl, y="絞り込み内の割合(%)",
                    title=f"{lbl}の分布",
                    text="絞り込み内の割合(%)",
                )
                fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
                fig.update_layout(yaxis_title="割合（%）")
                st.plotly_chart(fig, use_container_width=True)

        with tab_t:
            show_cols = [lbl, "件数", "グループ合計", "絞り込み内の割合(%)"]
            if has_filters:
                show_cols.append("グループ内の発生率(%)")
            st.dataframe(df[show_cols], use_container_width=True, hide_index=True)


# ── ナビゲーション ─────────────────────────────────────────────────────────────

page = st.sidebar.radio("メニュー", ["🔍 日付検索", "📊 統計探索"], key="nav")

if page == "🔍 日付検索":
    page_search()
else:
    page_stats()
