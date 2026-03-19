import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy import stats

st.set_page_config(page_title="보건 정책 의사결정 대시보드", layout="wide")

st.title("📊 감염병 정책 효과 분석 & 의사결정 대시보드")

# -----------------------------
# 기본 데이터 정의
# -----------------------------
regions = ["서울","경기","인천","강원","충청","전라","경상","제주"]
viruses = ["인플루엔자","COVID-19","노로바이러스","RSV","아데노바이러스"]

cause_map = {
    "인플루엔자": "비말감염",
    "COVID-19": "에어로졸",
    "노로바이러스": "식품오염",
    "RSV": "면역저하",
    "아데노바이러스": "접촉감염"
}

policy_map = {
    "인플루엔자": "예방접종 확대",
    "COVID-19": "백신 및 치료제 강화",
    "노로바이러스": "위생관리 강화",
    "RSV": "시설 방역 강화",
    "아데노바이러스": "환기 개선"
}

data = []

# -----------------------------
# 데이터 생성
# -----------------------------
for region in regions:
    for virus in viruses:

        cause = cause_map[virus]
        policy = policy_map[virus]

        # 2024
        prev_2024 = np.random.randint(55,80)
        imm_2024 = np.random.randint(40,60)
        rec_2024 = np.random.randint(90,95)

        # 2025 (정책 효과 반영)
        prev_2025 = prev_2024 - np.random.randint(10,20)
        imm_2025 = imm_2024 + np.random.randint(10,20)
        rec_2025 = rec_2024 + np.random.randint(2,5)

        data.append([2024, region, virus, cause, policy, prev_2024, imm_2024, rec_2024])
        data.append([2025, region, virus, cause, policy, prev_2025, imm_2025, rec_2025])

df = pd.DataFrame(data, columns=[
    "Year","Region","Virus","Cause","Policy",
    "Prevalence","Immunity","Recovery"
])

# -----------------------------
# 데이터 보기
# -----------------------------
st.subheader("📋 전체 데이터")
st.dataframe(df)

# -----------------------------
# KPI 요약
# -----------------------------
st.subheader("📈 정책 효과 요약")

summary = df.groupby("Year")[["Prevalence","Immunity","Recovery"]].mean()

col1, col2, col3 = st.columns(3)

col1.metric("발병률 변화", f"{summary.loc[2025,'Prevalence']:.1f}",
            f"{summary.loc[2025,'Prevalence'] - summary.loc[2024,'Prevalence']:.1f}")

col2.metric("면역율 변화", f"{summary.loc[2025,'Immunity']:.1f}",
            f"{summary.loc[2025,'Immunity'] - summary.loc[2024,'Immunity']:.1f}")

col3.metric("완치율 변화", f"{summary.loc[2025,'Recovery']:.1f}",
            f"{summary.loc[2025,'Recovery'] - summary.loc[2024,'Recovery']:.1f}")

# -----------------------------
# t-test
# -----------------------------
st.subheader("🧪 통계 검정")

pre = df[df["Year"] == 2024]["Prevalence"]
post = df[df["Year"] == 2025]["Prevalence"]

t_stat, p_val = stats.ttest_ind(pre, post)

st.write(f"t-statistic: {t_stat:.3f}")
st.write(f"p-value: {p_val:.5f}")

# -----------------------------
# 인터랙티브 그래프
# -----------------------------
st.subheader("📊 통합 분석 그래프")

metric = st.selectbox("분석 지표 선택", ["Prevalence","Immunity","Recovery"])

fig = px.line(
    df,
    x="Year",
    y=metric,
    color="Region",
    line_dash="Virus",
    markers=True,
    hover_data=["Cause","Policy"]
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# 정책별 효과 분석
# -----------------------------
st.subheader("🏥 정책 효과 분석")

policy_effect = df.groupby(["Policy","Year"])["Prevalence"].mean().reset_index()

fig2 = px.bar(
    policy_effect,
    x="Policy",
    y="Prevalence",
    color="Year",
    barmode="group"
)

st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# 상세 필터
# -----------------------------
st.subheader("🔍 상세 분석")

col1, col2 = st.columns(2)

selected_region = col1.selectbox("지역", ["전체"] + regions)
selected_virus = col2.selectbox("바이러스", ["전체"] + viruses)

filtered = df.copy()

if selected_region != "전체":
    filtered = filtered[filtered["Region"] == selected_region]

if selected_virus != "전체":
    filtered = filtered[filtered["Virus"] == selected_virus]

st.dataframe(filtered)

# -----------------------------
# 정책 해석 자동 생성
# -----------------------------
st.subheader("📌 정책 효과 해석")

if p_val < 0.05:
    st.success("""
    ✔ 정책 시행 이후 발병률이 통계적으로 유의미하게 감소했습니다.
    
    ✔ 주요 효과:
    - 예방접종 및 백신 정책 → 면역율 증가
    - 위생관리 정책 → 노로바이러스 감소
    - 환기 개선 → 호흡기 감염 감소
    
    👉 결론: 정책은 실질적으로 효과적이며 확장 필요
    """)
else:
    st.warning("""
    정책 효과가 제한적으로 나타났습니다.
    추가적인 데이터 확보 및 정책 보완이 필요합니다.
    """)
