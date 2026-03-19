import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

st.set_page_config(page_title="보건 정책 대시보드", layout="wide")

st.title("📊 감염병 정책 효과 분석 대시보드 (2024 vs 2025)")

# -----------------------------
# 한글 폰트 설정 (중요)
# -----------------------------
try:
    font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
    font = fm.FontProperties(fname=font_path)
    plt.rc('font', family=font.get_name())
except:
    st.warning("⚠️ 한글 폰트가 없을 수 있습니다. (NanumGothic 권장)")

# -----------------------------
# 데이터 생성 (정상 구조)
# -----------------------------
regions = ["서울","경기","인천","강원","충청","전라","경상","제주"]
viruses = ["인플루엔자","COVID-19","노로바이러스","RSV","아데노바이러스"]

data = []

for region in regions:
    for virus in viruses:
        # 2024
        prev_2024 = np.random.randint(50,80)
        imm_2024 = np.random.randint(40,60)
        rec_2024 = np.random.randint(90,95)

        # 2025 (정책 효과 반영)
        prev_2025 = prev_2024 - np.random.randint(10,20)
        imm_2025 = imm_2024 + np.random.randint(10,20)
        rec_2025 = rec_2024 + np.random.randint(2,5)

        data.append([2024, region, virus, prev_2024, imm_2024, rec_2024])
        data.append([2025, region, virus, prev_2025, imm_2025, rec_2025])

df = pd.DataFrame(data, columns=[
    "Year","Region","Virus","Prevalence","Immunity","Recovery"
])

# -----------------------------
# 전체 데이터 보기
# -----------------------------
st.subheader("📋 전체 데이터")
st.dataframe(df)

# -----------------------------
# 평균 비교
# -----------------------------
st.subheader("📈 전체 평균 비교")

summary = df.groupby("Year")[["Prevalence","Immunity","Recovery"]].mean().reset_index()
st.dataframe(summary)

# -----------------------------
# t-test (전체 기준)
# -----------------------------
st.subheader("🧪 정책 효과 t-test")

pre = df[df["Year"] == 2024]["Prevalence"]
post = df[df["Year"] == 2025]["Prevalence"]

t_stat, p_val = stats.ttest_ind(pre, post)

st.write(f"t-statistic: {t_stat:.3f}")
st.write(f"p-value: {p_val:.5f}")

if p_val < 0.05:
    st.success("✅ 정책 효과 유의미")
else:
    st.warning("⚠️ 유의미하지 않음")

# -----------------------------
# 인터랙티브 그래프 (핵심)
# -----------------------------
st.subheader("📊 인터랙티브 분석 그래프")

fig = px.line(
    df,
    x="Year",
    y="Prevalence",
    color="Region",
    line_group="Virus",
    facet_col="Virus",
    markers=True
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# 클릭 필터 느낌 (드롭다운)
# -----------------------------
st.subheader("🔍 상세 분석")

col1, col2 = st.columns(2)

selected_region = col1.selectbox("지역 선택", ["전체"] + regions)
selected_virus = col2.selectbox("바이러스 선택", ["전체"] + viruses)

filtered_df = df.copy()

if selected_region != "전체":
    filtered_df = filtered_df[filtered_df["Region"] == selected_region]

if selected_virus != "전체":
    filtered_df = filtered_df[filtered_df["Virus"] == selected_virus]

fig2 = px.bar(
    filtered_df,
    x="Region",
    y="Prevalence",
    color="Year",
    barmode="group",
    facet_col="Virus" if selected_virus == "전체" else None
)

st.plotly_chart(fig2, use_container_width=True)

# -----------------------------
# 정책 해석
# -----------------------------
st.subheader("📌 정책 해석")

st.write("""
- 전반적으로 2025년 발병률 감소
- 면역율 및 완치율 증가
- 정책 효과가 통계적으로 유의미하게 나타남

👉 결론: 예방 중심 정책 + 치료 접근성 강화가 핵심
""")
