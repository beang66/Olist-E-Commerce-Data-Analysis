"""
Olist 브라질 이커머스 대시보드 (Streamlit)

실행 방법 (터미널):  streamlit run app.py
필요한 데이터:       data/orders.csv.gz, data/items.csv.gz  (03 노트북에서 생성)
"""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# ── 1. 페이지 기본 설정 (반드시 다른 st 명령보다 먼저) ─────────────────────
st.set_page_config(page_title="Olist 이커머스 대시보드", page_icon="📦", layout="wide")

# app.py 가 있는 폴더 기준으로 data 폴더를 찾음 → 어느 위치에서 실행해도, 배포 서버에서도 경로가 맞음
DATA_DIR = Path(__file__).parent / "data"
WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]


# ── 2. 데이터 불러오기 ────────────────────────────────────────────────
@st.cache_data  # 한 번 읽은 결과를 기억해 두고 재사용 → 필터를 바꿀 때마다 파일을 다시 읽지 않아 빠름
def load_data():
    orders = pd.read_csv(DATA_DIR / "orders.csv.gz", parse_dates=["purchase_ts"])
    items = pd.read_csv(DATA_DIR / "items.csv.gz")
    return orders, items


orders, items = load_data()

# ── 3. 사이드바: 필터 ────────────────────────────────────────────────
st.sidebar.title("🔎 필터")
first_day = orders["purchase_ts"].min().date()
last_day = orders["purchase_ts"].max().date()
period = st.sidebar.date_input("주문 기간", value=(first_day, last_day),
                               min_value=first_day, max_value=last_day)
if len(period) != 2:                       # 달력에서 시작일만 고른 순간에는 날짜가 1개
    st.info("👈 주문 기간의 끝 날짜까지 선택해 주세요.")
    st.stop()                              # 여기서 화면 그리기를 멈춤
start, end = period

all_states = sorted(orders["customer_state"].unique())
picked_states = st.sidebar.multiselect("고객 지역 (주)", all_states, placeholder="전체 지역")
st.sidebar.caption("지역을 고르지 않으면 전체 지역을 보여 줍니다.")

# 필터 적용: 조건에 맞는 행만 True
mask = orders["purchase_ts"].dt.date.between(start, end)
if picked_states:
    mask &= orders["customer_state"].isin(picked_states)
f_orders = orders[mask]
f_items = items[items["order_id"].isin(f_orders["order_id"])]

if f_orders.empty:
    st.warning("조건에 맞는 주문이 없습니다. 필터를 바꿔 보세요.")
    st.stop()

# ── 4. 제목과 핵심 지표(KPI) ─────────────────────────────────────────
st.title("📦 Olist 브라질 이커머스 대시보드")
region = "전체 지역" if not picked_states else ", ".join(picked_states)
st.caption(f"배송 완료 주문 기준 · {start} ~ {end} · {region}")

k1, k2, k3 = st.columns(3)          # 지표 6개를 3개씩 두 줄로 (한 줄에 6개면 숫자가 잘림)
k4, k5, k6 = st.columns(3)
k1.metric("주문 수", f"{len(f_orders):,}건")
k2.metric("매출", f"R$ {f_orders['payment_value'].sum() / 1e6:,.2f}M")
k3.metric("객단가 (평균)", f"R$ {f_orders['payment_value'].mean():,.0f}")
k4.metric("배송 기간 (중앙값)", f"{f_orders['delivery_days'].median():.1f}일")
k5.metric("배송 지연율", f"{f_orders['late'].mean() * 100:.1f}%")
k6.metric("평균 리뷰", f"{f_orders['review_score'].mean():.2f}점")

# ── 5. 탭별 분석 화면 ───────────────────────────────────────────────
tab_sales, tab_time, tab_cat, tab_ship, tab_state, tab_data = st.tabs(
    ["📈 매출 추이", "🕒 주문 시간", "🛍️ 카테고리", "🚚 배송·리뷰", "🗺️ 지역", "📄 데이터"])

# (1) 매출 추이
with tab_sales:
    choice = st.radio("보고 싶은 지표", ["매출", "주문 수", "객단가"], horizontal=True)
    # "MS"(Month Start): 각 달을 1일 날짜로 표시 → x축 '2017-01' 눈금과 막대 위치가 정확히 맞음
    monthly = (f_orders.set_index("purchase_ts").resample("MS")
               .agg(revenue=("payment_value", "sum"), orders=("order_id", "count"),
                    aov=("payment_value", "mean"))
               .reset_index())
    column = {"매출": "revenue", "주문 수": "orders", "객단가": "aov"}[choice]
    fig = px.bar(monthly, x="purchase_ts", y=column, labels={"purchase_ts": "주문 월", column: choice},
                 title=f"월별 {choice}")
    fig.update_xaxes(dtick="M1", tickformat="%Y-%m", tickangle=-45)
    st.plotly_chart(fig, width="stretch")

# (2) 주문 시간 — 요일 × 시간 히트맵
with tab_time:
    t = f_orders.assign(weekday=f_orders["purchase_ts"].dt.dayofweek.map(dict(enumerate(WEEKDAYS))),
                        hour=f_orders["purchase_ts"].dt.hour)
    heat = (t.pivot_table(index="weekday", columns="hour", values="order_id", aggfunc="count")
            .reindex(index=WEEKDAYS, columns=range(24)).fillna(0))
    fig = px.imshow(heat, labels=dict(x="시", y="요일", color="주문 수"), aspect="auto",
                    color_continuous_scale="Blues", title="요일 × 시간대 주문 수")
    fig.update_xaxes(dtick=1)
    st.plotly_chart(fig, width="stretch")
    st.caption("진한 칸일수록 주문이 많은 시간대입니다. 프로모션 · 고객센터 운영 시간 결정에 활용할 수 있습니다.")

# (3) 카테고리
with tab_cat:
    left, right = st.columns([1, 3])
    basis = left.radio("순위 기준", ["매출", "판매 수량"])
    top_n = left.slider("표시할 개수", min_value=5, max_value=30, value=15)
    cat = f_items.groupby("category").agg(revenue=("price", "sum"), items=("order_id", "size"))
    col = "revenue" if basis == "매출" else "items"
    top = cat.sort_values(col, ascending=False).head(top_n).iloc[::-1]   # 가로 막대: 1위가 맨 위에 오도록 뒤집기
    fig = px.bar(top, x=col, y=top.index, orientation="h",
                 labels={col: basis, "category": "카테고리"}, title=f"카테고리 {basis} TOP {top_n}")
    fig.update_layout(height=max(400, top_n * 24))
    right.plotly_chart(fig, width="stretch")

# (4) 배송과 리뷰
with tab_ship:
    left, right = st.columns(2)
    bins = [0, 7, 14, 21, 30, 60, 1000]
    labels = ["~7일", "8~14일", "15~21일", "22~30일", "31~60일", "60일+"]
    groups = pd.cut(f_orders["delivery_days"], bins=bins, labels=labels)
    by_group = f_orders.groupby(groups, observed=True)["review_score"].mean().reset_index()
    fig = px.bar(by_group, x="delivery_days", y="review_score", text_auto=".2f",
                 labels={"delivery_days": "배송 기간", "review_score": "평균 리뷰 점수"},
                 title="배송 기간별 평균 리뷰 점수")
    fig.update_yaxes(range=[1, 5])
    left.plotly_chart(fig, width="stretch")

    late_rate = (f_orders.set_index("purchase_ts").resample("MS")["late"].mean() * 100).reset_index()
    fig = px.line(late_rate, x="purchase_ts", y="late", markers=True,
                  labels={"purchase_ts": "주문 월", "late": "지연율 (%)"}, title="월별 배송 지연율")
    right.plotly_chart(fig, width="stretch")

    on_time = f_orders.loc[~f_orders["late"], "review_score"].mean()
    delayed = f_orders.loc[f_orders["late"], "review_score"].mean()
    st.info(f"제때 도착한 주문의 평균 리뷰는 **{on_time:.2f}점**, 지연된 주문은 **{delayed:.2f}점**입니다.")

# (5) 지역
with tab_state:
    state = f_orders.groupby("customer_state").agg(
        orders=("order_id", "count"), revenue=("payment_value", "sum"),
        median_days=("delivery_days", "median"), late_rate=("late", "mean"),
        review=("review_score", "mean"))
    state["late_rate"] *= 100
    names = {"주문 수": "orders", "매출": "revenue", "배송 기간 (중앙값)": "median_days",
             "지연율 (%)": "late_rate", "평균 리뷰": "review"}
    pick = st.selectbox("비교할 지표", list(names))
    s = state.sort_values(names[pick], ascending=False)
    fig = px.bar(s, x=s.index, y=names[pick], labels={"customer_state": "주(state)", names[pick]: pick},
                 title=f"주(state)별 {pick}")
    st.plotly_chart(fig, width="stretch")
    st.dataframe(state.rename(columns={v: k for k, v in names.items()}).rename_axis("주(state)").round(2), width="stretch")

# (6) 전처리된 주문 데이터 확인 · 내려받기 (원본 Kaggle CSV가 아님)
with tab_data:
    st.write(f"필터가 적용된 주문 **{len(f_orders):,}건** 중 앞의 1,000건")
    st.dataframe(f_orders.head(1000), width="stretch")
    st.download_button("⬇️ 필터 결과 CSV 내려받기",
                       data=f_orders.to_csv(index=False).encode("utf-8-sig"),   # utf-8-sig: 엑셀에서 한글이 안 깨짐
                       file_name="olist_filtered_orders.csv", mime="text/csv")

st.divider()
st.caption("데이터: Olist Brazilian E-Commerce Public Dataset (Kaggle, CC BY-NC-SA 4.0) · 교육용 분석 대시보드")
