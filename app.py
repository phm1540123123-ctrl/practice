import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="한강 수질 분석", layout="wide")

st.title("📊 한강 수질 분석 (2020)")
st.write("노량진과 선유 지점의 수소이온농도(pH) 및 용존산소(DO) 변화")

# 데이터 불러오기
ph = pd.read_csv("수소이온농도.csv")
do = pd.read_csv("용존산소.csv")

# 컬럼명 통일 (필요 시 수정)
ph.columns = ["날짜", "노량진_pH", "선유_pH"]
do.columns = ["날짜", "노량진_DO", "선유_DO"]

# 날짜 병합
df = pd.merge(ph, do, on="날짜")

# 날짜 형식 변환
df["날짜"] = pd.to_datetime(df["날짜"])

# -----------------------------
# 📈 그래프
# -----------------------------
fig = go.Figure()

# 노량진 pH
fig.add_trace(go.Scatter(
    x=df["날짜"],
    y=df["노량진_pH"],
    mode='lines+markers',
    name='노량진 pH'
))

# 선유 pH
fig.add_trace(go.Scatter(
    x=df["날짜"],
    y=df["선유_pH"],
    mode='lines+markers',
    name='선유 pH'
))

# 노량진 DO
fig.add_trace(go.Scatter(
    x=df["날짜"],
    y=df["노량진_DO"],
    mode='lines+markers',
    name='노량진 DO',
    yaxis="y2"
))

# 선유 DO
fig.add_trace(go.Scatter(
    x=df["날짜"],
    y=df["선유_DO"],
    mode='lines+markers',
    name='선유 DO',
    yaxis="y2"
))

# 이중 y축 설정
fig.update_layout(
    title="날짜별 pH 및 용존산소 변화",
    xaxis_title="날짜",
    yaxis=dict(title="pH"),
    yaxis2=dict(
        title="용존산소 (mg/L)",
        overlaying='y',
        side='right'
    ),
    legend_title="항목",
    hovermode="x unified"
)

st.plotly_chart(fig, use_container_width=True)

st.info("💡 그래프의 범례를 클릭하면 각 데이터를 선택적으로 표시/숨김할 수 있습니다.")

# -----------------------------
# 📌 해석
# -----------------------------
st.header("📌 데이터 해석")

st.subheader("1️⃣ 수소이온농도(pH)")
st.write("""
- 전체적으로 pH 값은 약 7.3~7.4 수준으로 나타남
- 이는 중성~약알칼리성 범위로 자연 하천의 정상 범위에 해당함

👉 해석:
- 급격한 화학적 오염 없음
- 생물 서식에 적합한 환경 유지
- 수질 안정성이 높음
""")

st.subheader("2️⃣ 용존산소(DO)")
st.write("""
- DO 값은 약 9~10 mg/L 수준으로 매우 높음

👉 해석:
- 수질이 매우 양호함
- 유기물 오염이 적음
- 수중 생물 활동이 활발함
""")

st.subheader("3️⃣ 종합 분석")
st.write("""
pH와 DO를 함께 고려하면 다음과 같은 결론을 도출할 수 있음:

✔ 전반적으로 매우 건강한 수질 상태  
✔ 생태계 유지에 적합한 환경  
✔ 유기물 및 생활하수 오염 영향이 낮음  
""")

st.subheader("4️⃣ 지역별 차이")
st.write("""
노량진과 선유 지점을 비교하면:

- 노량진: DO가 약간 더 높은 경향
- 선유: 상대적으로 약간 낮음

👉 해석:
- 유속 차이
- 수체 정체 여부
- 오염원 유입 차이 가능성
""")

st.subheader("5️⃣ 활용 가능 인사이트")
st.write("""
이 데이터로 다음과 같은 분석이 가능함:

1. 계절별 수질 변화 분석  
2. 조류(녹조) 발생 가능성 평가  
3. 오염 유입 시점 탐지  
4. 수질 정책 효과 분석  

👉 특히 DO와 pH가 안정적이라는 점에서  
현재 한강은 매우 양호한 상태로 평가됨
""")
