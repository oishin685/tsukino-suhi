import streamlit as st
import sqlite3
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    return str(kanzen) if moto == kanzen else f"{kanzen}／{moto}"


def fmt_extra(moto: int, kanzen: int) -> str:
    return str(moto) if moto == kanzen else f"{moto}／{kanzen}"


def is_zorome(n) -> bool:
    try:
        s = str(int(n))
        return len(s) > 1 and len(set(s)) == 1
    except (ValueError, TypeError):
        return False


def zorome_required_for(col: str) -> list:
    if col.endswith("_kanzen"):
        return [11, 22, 33]
    elif col.endswith("_moto"):
        return [11, 22, 33, 44, 55, 66, 77, 88, 99]
    return []


def run_query(sql: str, params: list) -> pd.DataFrame:
    cur = conn.execute(sql, params)
    if not cur.description:
        return pd.DataFrame()
    cols = [d[0] for d in cur.description]
    return pd.DataFrame([tuple(r) for r in cur.fetchall()], columns=cols)


# ── 日付検索ページ ─────────────────────────────────────────────────────────────

def page_search():
    st.title("🌙 月の数秘®︎ 数字検索")
    st.caption("生年月日を選ぶと、6つの数字と本質・性格・統合数・素質が出ます")

    d = st.date_input(
        "生年月日",
        value=date(1990, 1, 1),
        min_value=date(1, 1, 1),
        max_value=date(3000, 12, 31),
    )

    if not d:
        return

    row = conn.execute("SELECT * FROM dates WHERE date = ?", (d.isoformat(),)).fetchone()
    if row is None:
        st.error("この日付はデータベースにありません")
        return

    st.divider()
    st.subheader(f"{d.year}年{d.month}月{d.day}日")

    row1 = st.columns(3)
    for i, (label, mc, kc) in enumerate(LABELS_6[:3]):
        with row1[i]:
            st.metric(label=label, value=fmt_6(row[mc], row[kc]))

    row2 = st.columns(3)
    for i, (label, mc, kc) in enumerate(LABELS_6[3:]):
        with row2[i]:
            st.metric(label=label, value=fmt_6(row[mc], row[kc]))

    st.divider()
    cols2 = st.columns(4)
    for i, (label, mc, kc) in enumerate(LABELS_EXTRA):
        with cols2[i]:
            st.metric(label=label, value=fmt_extra(row[mc], row[kc]))


# ── 統計探索ページ ─────────────────────────────────────────────────────────────

COL_LABEL = {"month": "月", "day": "日"}
for _g in NUMBER_GROUPS:
    COL_LABEL[_g["kanzen"]] = f"{_g['name']}（一桁にした値）"
    COL_LABEL[_g["moto"]] = f"{_g['name']}（元の数字）"


def page_stats():
    with st.sidebar:
        st.divider()
        with st.form("stats"):
            # 絞り込み設定（0＝使わない）
            st.subheader("🔍 絞り込み")
            st.caption("0 のままにすると絞り込みません")

            c1, c2 = st.columns(2)
            with c1:
                start_year = int(st.number_input("開始年", 0, 3000, 1950, step=1))
            with c2:
                end_year = int(st.number_input("終了年", 0, 3000, 2059, step=1))

            c1, c2 = st.columns(2)
            with c1:
                filt_month = int(st.number_input("月", 0, 12, 0, step=1))
            with c2:
                filt_day = int(st.number_input("日", 0, 31, 0, step=1))

            filt_nums = {}
            for g in NUMBER_GROUPS:
                st.caption(g["name"])
                c1, c2 = st.columns(2)
                with c1:
                    filt_nums[g["kanzen"]] = int(st.number_input(
                        "一桁", 0, value=0, step=1, key=f"f_{g['kanzen']}"
                    ))
                with c2:
                    filt_nums[g["moto"]] = int(st.number_input(
                        "元の数字", 0, value=0, step=1, key=f"f_{g['moto']}"
                    ))

            st.divider()

            # アウトプット設定
            st.subheader("📊 アウトプット")
            st.caption("分布を出したい数字にチェック（複数可）")

            c1, c2 = st.columns([1, 2])
            with c1:
                out_year = st.checkbox("年代")
            with c2:
                granularity = int(st.selectbox(
                    "粒度",
                    [1, 5, 10, 20, 50, 100],
                    index=2,
                    format_func=lambda x: f"{x}年ごと",
                ))

            c1, c2 = st.columns(2)
            with c1:
                out_month = st.checkbox("月", key="o_month")
            with c2:
                out_day = st.checkbox("日", key="o_day")

            out_nums = {}
            for g in NUMBER_GROUPS:
                st.caption(g["name"])
                c1, c2 = st.columns(2)
                with c1:
                    out_nums[g["kanzen"]] = st.checkbox("一桁", key=f"o_{g['kanzen']}")
                with c2:
                    out_nums[g["moto"]] = st.checkbox("元の数字", key=f"o_{g['moto']}")

            submitted = st.form_submit_button("▶ 集計する", use_container_width=True)

    # ── メイン ──────────────────────────────────────────────────────────────
    st.title("📊 月の数秘®︎ 統計探索")

    if submitted:
        st.session_state["_stats_ready"] = True

    if not st.session_state.get("_stats_ready"):
        st.info("サイドバーで絞り込みとアウトプットを設定してから「集計する」を押してください。")
        return

    if start_year > end_year:
        st.error("開始年は終了年以下にしてください")
        return

    # フィルター構築（0 は除外）
    filters = {}
    if filt_month > 0:
        filters["month"] = filt_month
    if filt_day > 0:
        filters["day"] = filt_day
    for col, val in filt_nums.items():
        if val > 0:
            filters[col] = val

    # 端数の年代を自動除外（年代出力選択時）
    decade_start_of_end = (end_year // granularity) * granularity
    if out_year and end_year < decade_start_of_end + granularity - 1:
        effective_end = decade_start_of_end - 1
    else:
        effective_end = end_year

    base_params = [start_year, effective_end]
    filter_parts = [f"{col} = ?" for col in filters]
    where_all = "WHERE year >= ? AND year <= ?" + (
        " AND " + " AND ".join(filter_parts) if filter_parts else ""
    )
    all_params = base_params + list(filters.values())

    # 対象件数
    try:
        total = int(run_query(
            f"SELECT COUNT(*) AS n FROM dates {where_all}", all_params
        ).iloc[0]["n"])
    except Exception as e:
        st.error(f"クエリエラー: {e}")
        return

    filter_text = "なし" if not filters else "、".join(
        f"{COL_LABEL.get(col, col)} = {val}" for col, val in filters.items()
    )
    period_str = f"{start_year}〜{effective_end}年"
    if effective_end != end_year:
        period_str += f"（{end_year}年は端数年代のため除外）"
    mc1, mc2 = st.columns([1, 3])
    with mc1:
        st.metric("対象件数", f"{total:,} 件")
    with mc2:
        st.caption(f"期間：{period_str} ／ 絞り込み：{filter_text}")

    # アウトプット収集
    num_out_cols = [col for col, checked in out_nums.items() if checked and col not in filters]
    bar_outputs = []
    if out_month and "month" not in filters:
        bar_outputs.append({"label": "月", "group_expr": "month"})
    if out_day and "day" not in filters:
        bar_outputs.append({"label": "日", "group_expr": "day"})
    if not out_year:
        for col in num_out_cols:
            bar_outputs.append({"label": COL_LABEL.get(col, col), "group_expr": col})

    if not out_year and not bar_outputs:
        st.info("アウトプットで見たい数字を選んでから集計してください。")
        return

    # ── ヒートマップ（年代 × 数字）──────────────────────────────────────────────
    if out_year and num_out_cols:
        hm_mode = st.radio(
            "表示モード",
            ["割合（%）", "偏差", "発生数"],
            horizontal=True,
            key="hm_mode",
        )
        for col in num_out_cols:
            lbl = COL_LABEL.get(col, col)
            st.divider()
            st.subheader(f"📈 年代（{granularity}年ごと）× {lbl}")
            q = f"""
                SELECT (year / {granularity}) * {granularity} AS decade,
                       {col} AS val,
                       COUNT(*) AS cnt
                FROM dates {where_all}
                GROUP BY decade, val
                ORDER BY decade, val
            """
            try:
                df_h = run_query(q, all_params)
            except Exception as e:
                st.error(f"クエリエラー: {e}")
                continue
            if df_h.empty:
                st.warning("該当するデータがありませんでした")
                continue

            # 縦=年代、横=数字値
            pivot = df_h.pivot(index="decade", columns="val", values="cnt").fillna(0)
            pivot.columns = pivot.columns.astype(int)
            for z in zorome_required_for(col):
                if z not in pivot.columns:
                    pivot[z] = 0
            pivot = pivot.sort_index(axis=1)
            # インデックス・列は文字列化（カテゴリ軸として扱わせる）
            pivot.columns = [str(c) for c in pivot.columns]
            pivot.index = [str(int(i)) for i in pivot.index]
            pivot = pivot.sort_index()

            if hm_mode == "割合（%）":
                display = pivot.div(pivot.sum(axis=1), axis=0) * 100
                midpoint, zmin_val, fmt, clabel = None, 0, ".1f", "割合（%）"
                _dmax = float(display.values.max())
                _nz = display.values[display.values > 0]
                _thresh = max(float(_nz.min()) / _dmax * 0.5, 1e-10) if len(_nz) and _dmax > 0 else 0.5
                colorscale = [[0.0, "rgb(20,20,20)"], [_thresh, "rgb(210,228,245)"],
                              [0.5, "rgb(107,174,214)"], [1.0, "rgb(8,48,107)"]]
            elif hm_mode == "偏差":
                pct = pivot.div(pivot.sum(axis=1), axis=0) * 100
                overall = pivot.sum(axis=0) / pivot.sum().sum() * 100
                display = pct.sub(overall, axis=1)
                colorscale, midpoint, zmin_val, fmt, clabel = "RdBu_r", 0.0, None, ".2f", "偏差（%pt）"
            else:
                display = pivot
                midpoint, zmin_val, fmt, clabel = None, 0, ".0f", "発生数"
                _dmax = float(display.values.max())
                _nz = display.values[display.values > 0]
                _thresh = max(float(_nz.min()) / _dmax * 0.5, 1e-10) if len(_nz) and _dmax > 0 else 0.5
                colorscale = [[0.0, "rgb(20,20,20)"], [_thresh, "rgb(210,228,245)"],
                              [0.5, "rgb(107,174,214)"], [1.0, "rgb(8,48,107)"]]

            col_list = list(display.columns)
            row_list = list(display.index)
            n_cells = len(row_list) * len(col_list)

            # ゾロ目列にオレンジ枠（カテゴリ軸のインデックス位置で指定）
            zorome_shapes = [
                dict(type="rect",
                     x0=i - 0.5, x1=i + 0.5,
                     y0=-0.5, y1=len(row_list) - 0.5,
                     line=dict(color="orange", width=3),
                     fillcolor="rgba(0,0,0,0)")
                for i, c in enumerate(col_list) if is_zorome(int(c))
            ]

            # セル内テキスト
            if n_cells < 300:
                fmt_map = {".1f": "{:.1f}", ".2f": "{:.2f}", ".0f": "{:.0f}"}
                fstr = fmt_map[fmt]
                text_arr = [[fstr.format(v) for v in row] for row in display.to_numpy()]
            else:
                text_arr = None

            height = min(max(600, len(row_list) * 60), 2000)
            # go.Heatmap で軸タイプを明示的にcategoryに固定
            trace = go.Heatmap(
                z=display.to_numpy(),
                x=col_list,
                y=row_list,
                colorscale=colorscale,
                zmid=midpoint,
                zmin=zmin_val,
                colorbar=dict(title=clabel),
                text=text_arr,
                texttemplate="%{text}" if text_arr else "",
                hoverongaps=False,
            )
            fig = go.Figure(data=[trace])
            fig.update_layout(
                title=f"年代（{granularity}年ごと）× {lbl}の{clabel}",
                xaxis=dict(type="category", title=lbl,
                           categoryorder="array", categoryarray=col_list),
                yaxis=dict(type="category", title="年代",
                           categoryorder="array", categoryarray=row_list,
                           autorange="reversed"),
                height=height,
                shapes=zorome_shapes,
            )
            st.plotly_chart(fig, use_container_width=True)

    # ── 年代のみ → 通常バーチャート ──────────────────────────────────────────────
    elif out_year:
        st.divider()
        lbl = f"年代（{granularity}年ごと）"
        st.subheader(f"📈 {lbl}")
        q = f"""
            SELECT (year / {granularity}) * {granularity} AS val, COUNT(*) AS count
            FROM dates {where_all}
            GROUP BY val ORDER BY val
        """
        try:
            df = run_query(q, all_params)
        except Exception as e:
            st.error(f"クエリエラー: {e}")
        else:
            if df.empty:
                st.warning("該当するデータがありませんでした")
            else:
                bar_colors = ["orange" if is_zorome(v) else "#636EFA" for v in df["val"]]
                df["割合(%)"] = (df["count"] / df["count"].sum() * 100).round(2)
                df = df.rename(columns={"val": lbl, "count": "件数"})
                df[lbl] = df[lbl].astype(str)
                tab_g, tab_t = st.tabs(["グラフ", "数値表"])
                with tab_g:
                    fig = px.bar(df, x=lbl, y="割合(%)", title=f"{lbl}の分布（{total:,}件中）", text="割合(%)")
                    fig.update_traces(marker_color=bar_colors, texttemplate="%{text:.1f}%", textposition="outside")
                    fig.update_layout(yaxis_title="割合（%）")
                    st.plotly_chart(fig, use_container_width=True)
                with tab_t:
                    st.dataframe(df[[lbl, "件数", "割合(%)"]], use_container_width=True, hide_index=True)

    # ── 通常バーチャート（月・日・数字） ──────────────────────────────────────────
    for dim in bar_outputs:
        st.divider()
        lbl = dim["label"]
        gexpr = dim["group_expr"]
        st.subheader(f"📈 {lbl}")
        q = f"""
            SELECT {gexpr} AS val, COUNT(*) AS count
            FROM dates {where_all}
            GROUP BY {gexpr} ORDER BY val
        """
        try:
            df = run_query(q, all_params)
        except Exception as e:
            st.error(f"クエリエラー: {e}")
            continue
        if df.empty:
            st.warning("該当するデータがありませんでした")
            continue
        # ゾロ目は必ずバーとして表示（値が0でも）
        zorome_ensure = zorome_required_for(gexpr)
        if zorome_ensure:
            existing = set(int(v) for v in df["val"].tolist())
            new_rows = [{"val": z, "count": 0} for z in zorome_ensure if z not in existing]
            if new_rows:
                df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
                df = df.sort_values("val").reset_index(drop=True)
        bar_colors = ["orange" if is_zorome(v) else "#636EFA" for v in df["val"]]
        df["割合(%)"] = (df["count"] / df["count"].sum() * 100).round(2)
        df = df.rename(columns={"val": lbl, "count": "件数"})
        df[lbl] = df[lbl].astype(str)
        tab_g, tab_t = st.tabs(["グラフ", "数値表"])
        with tab_g:
            fig = px.bar(df, x=lbl, y="割合(%)", title=f"{lbl}の分布（{total:,}件中）", text="割合(%)")
            fig.update_traces(marker_color=bar_colors, texttemplate="%{text:.1f}%", textposition="outside")
            fig.update_layout(yaxis_title="割合（%）")
            st.plotly_chart(fig, use_container_width=True)
        with tab_t:
            st.dataframe(df[[lbl, "件数", "割合(%)"]], use_container_width=True, hide_index=True)


# ── ナビゲーション ─────────────────────────────────────────────────────────────

page = st.sidebar.radio("メニュー", ["📊 統計探索", "🔍 日付検索"], key="nav")

if page == "📊 統計探索":
    page_stats()
else:
    page_search()
