import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

st.set_page_config(page_title="보건 정책 효과 분석 대시보드", layout="wide")

st.title("📊 감염병 정책 효과 분석 대시보드 (2024 vs 2025)")

# -----------------------------
# 샘플 데이터 생성 (보고서 기반)
# -----------------------------
data = {
    "Year": [2024,2025]*10,
    "Region": ["서울","서울","경기","경기","인천","인천","강원","강원","전라","전라"]*2,
    "Virus": ["인플루엔자","인플루엔자","COVID-19","COVID-19","노로바이러스","노로바이러스",
              "RSV","RSV","아데노바이러스","아데노바이러스"]*2,
    "Prevalence": [78,62,75,60,62,45,52,41,47,34]*2,
    "Immunity": [42,65,45,67,46,67,58,70,60,74]*2,
    "Recovery": [93,97,92,97,97,99,89,92,97,98]*2
}

df = pd.DataFrame(data)

# -----------------------------
# 사이드바 필터
# -----------------------------
st.sidebar.header("🔍 필터 선택")

region = st.sidebar.selectbox("지역 선택", df["Region"].unique())
virus = st.sidebar.selectbox("바이러스 선택", df["Virus"].unique())

filtered = df[(df["Region"] == region) & (df["Virus"] == virus)]

# -----------------------------
# 데이터 표시
# -----------------------------
st.subheader("📋 데이터 미리보기")
st.dataframe(filtered)

# -----------------------------
# 평균 비교
# -----------------------------
st.subheader("📈 정책 전후 평균 비교")

pre = filtered[filtered["Year"] == 2024]["Prevalence"]
post = filtered[filtered["Year"] == 2025]["Prevalence"]

col1, col2, col3 = st.columns(3)

col1.metric("2024 발병률 평균", f"{pre.mean():.2f}")
col2.metric("2025 발병률 평균", f"{post.mean():.2f}")
col3.metric("변화량", f"{post.mean()-pre.mean():.2f}")

# -----------------------------
# t-test 분석
# -----------------------------
st.subheader("🧪 t-test 결과")

if len(pre) > 0 and len(post) > 0:
    t_stat, p_val = stats.ttest_ind(pre, post)

    st.write(f"t-statistic: {t_stat:.3f}")
    st.write(f"p-value: {p_val:.5f}")

    if p_val < 0.05:
        st.success("✅ 통계적으로 유의미한 차이 있음 (p < 0.05)")
    else:
        st.warning("⚠️ 통계적으로 유의미하지 않음")

# -----------------------------
# 시각화
# -----------------------------
st.subheader("📊 발병률 비교 그래프")

fig, ax = plt.subplots()
years = ["2024", "2025"]
values = [pre.mean(), post.mean()]

ax.bar(years, values)
ax.set_ylabel("Prevalence Rate")
ax.set_title(f"{region} - {virus} 발병률 변화")

st.pyplot(fig)

# -----------------------------
# 정책 해석
# -----------------------------
st.subheader("📌 정책 효과 해석")

if p_val < 0.05:
    st.write("""
    정책 시행 이후 발병률이 유의미하게 감소하였으며,
    이는 예방 정책(백신, 위생관리, 공조 시스템)의 효과로 해석됩니다.
    """)
else:
    st.write("""
    정책 효과가 일부 존재하지만 통계적으로 명확하지 않습니다.
    추가 데이터 확보가 필요합니다.
    """)
