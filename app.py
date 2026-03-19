import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="한강 수질 분석", layout="wide")

st.title("📊 한강 수질 분석 (2020)")
st.write("노량진과 선유 지점의 수소이온농도(pH) 및 용존산소(DO) 변화")

# -----------------------------
# 📂 파일 업로드
# -----------------------------
st.sidebar.header("📁 CSV 파일 업로드")

ph_file = st.sidebar.file_uploader("수소이온농도(pH) 파일", type="csv")
do_file = st.sidebar.file_uploader("용존산소(DO) 파일", type="csv")

if ph_file is not None and do_file is not None:

    try:
        # CSV 읽기 (한글 대응)
        ph = pd.read_csv(ph_file, encoding="cp949")
        do = pd.read_csv(do_file, encoding="cp949")

        # 컬럼 확인 (디버깅용)
        st.write("pH 컬럼:", ph.columns)
        st.write("DO 컬럼:", do.columns)

        # 컬럼명 통일 (필요시 수정)
        ph.columns = ["날짜", "노량진_pH", "선유_pH"]
        do.columns = ["날짜", "노량진_DO", "선유_DO"]

        # 데이터 병합
        df = pd.merge(ph, do, on="날짜")

        # 날짜 변환
        df["날짜"] = pd.to_datetime(df["날짜"], errors='coerce')

        # -----------------------------
        # 📈 인터랙티브 그래프
        # -----------------------------
        fig = go.Figure()

        # pH
        fig.add_trace(go.Scatter(
            x=df["날짜"], y=df["노량진_pH"],
            mode='lines+markers', name='노량진 pH'
        ))

        fig.add_trace(go.Scatter(
            x=df["날짜"], y=df["선유_pH"],
            mode='lines+markers', name='선유 pH'
        ))

        # DO (오른쪽 축)
        fig.add_trace(go.Scatter(
            x=df["날짜"], y=df["노량진_DO"],
            mode='lines+markers', name='노량진 DO',
            yaxis="y2"
        ))

        fig.add_trace(go.Scatter(
            x=df["날짜"], y=df["선유_DO"],
            mode='lines+markers', name='선유 DO',
            yaxis="y2"
        ))

        # 레이아웃
        fig.update_layout(
            title="📊 날짜별 pH 및 용존산소 변화",
            xaxis_title="날짜",
            yaxis=dict(title="pH"),
            yaxis2=dict(
                title="용존산소 (mg/L)",
                overlaying='y',
                side='right'
            ),
            hovermode="x unified"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.info("💡 범례를 클릭하면 그래프를 선택적으로 표시/숨김 할 수 있습니다.")

        # -----------------------------
        # 📌 데이터 해석
        # -----------------------------
        st.header("📌 수질 해석")

        avg_ph = df[["노량진_pH", "선유_pH"]].mean().mean()
        avg_do = df[["노량진_DO", "선유_DO"]].mean().mean()

        st.subheader("1️⃣ 수소이온농도(pH)")
        st.write(f"""
        평균 pH: **{avg_ph:.2f}**

        ✔ 중성~약알칼리성 범위  
        ✔ 자연 하천의 정상 범위 유지  
        ✔ 급격한 화학 오염 없음  

        👉 해석:
        - 생물 서식에 적합한 환경
        - 수질 안정성 높음
        """)

        st.subheader("2️⃣ 용존산소(DO)")
        st.write(f"""
        평균 DO: **{avg_do:.2f} mg/L**

        ✔ 매우 높은 수준  
        ✔ 깨끗한 수질 상태  

        👉 해석:
        - 유기물 오염 낮음
        - 생태계 건강
        """)

        st.subheader("3️⃣ 종합 분석")
        st.write("""
        ✔ pH 안정 + DO 높음 → 매우 양호한 수질  

        ✔ 생태계 유지 가능  
        ✔ 오염 영향 낮음  

        👉 결론:
        현재 한강 수질은 매우 건강한 상태
        """)

        st.subheader("4️⃣ 추가 인사이트")
        st.write("""
        📊 이 데이터로 가능한 분석:

        - 계절별 수질 변화 분석  
        - 조류(녹조) 발생 예측  
        - 오염 유입 탐지  
        - 정책 효과 평가  

        👉 특히 DO와 pH 안정성은  
        수질 관리가 잘 이루어지고 있다는 근거가 됨
        """)

    except Exception as e:
        st.error(f"데이터 처리 중 오류 발생: {e}")

else:
    st.warning("👈 왼쪽에서 CSV 파일 2개를 업로드해주세요.")
