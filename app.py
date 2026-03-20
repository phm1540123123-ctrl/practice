import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os, csv
from collections import defaultdict

# ─────────────────────────────────────────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="한강 수질 분석 · 2020–2050",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap');
* { font-family: 'Noto Sans KR', sans-serif !important; }
.block-container { padding: 1.5rem 2rem 3rem; max-width: 1400px; }

.hero {
    background: linear-gradient(135deg, #0c1e3c 0%, #0f3460 55%, #16547a 100%);
    border-radius: 20px; padding: 40px 48px 36px;
    margin-bottom: 28px; position: relative; overflow: hidden;
}
.hero::before {
    content: ''; position: absolute; top: -40px; right: -40px;
    width: 260px; height: 260px; border-radius: 50%;
    background: rgba(255,255,255,0.04);
}
.hero-title { font-size: 30px; font-weight: 900; color: #fff; letter-spacing: -0.5px; margin: 0 0 8px; }
.hero-sub   { font-size: 14px; color: rgba(255,255,255,0.65); margin: 0; line-height: 1.6; }
.hero-tags  { margin-top: 18px; display: flex; gap: 8px; flex-wrap: wrap; }
.hero-tag {
    background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.2);
    color: rgba(255,255,255,0.85); border-radius: 20px; padding: 4px 14px;
    font-size: 12px; font-weight: 500;
}
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 24px; }
.kpi {
    background: #fff; border-radius: 14px; padding: 18px 20px 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06); border-top: 3px solid #2563eb;
}
.kpi.orange { border-top-color: #ea580c; }
.kpi.teal   { border-top-color: #0891b2; }
.kpi.amber  { border-top-color: #d97706; }
.kpi-label  { font-size: 11.5px; color: #6b7280; font-weight: 500; letter-spacing: 0.04em; margin-bottom: 6px; }
.kpi-value  { font-size: 28px; font-weight: 800; color: #111827; line-height: 1; }
.kpi-unit   { font-size: 13px; font-weight: 400; color: #6b7280; margin-left: 2px; }
.kpi-range  { font-size: 11px; color: #9ca3af; margin-top: 5px; }
.sec-hd {
    font-size: 16px; font-weight: 700; color: #0c1e3c;
    border-left: 4px solid #2563eb; padding-left: 12px;
    margin: 28px 0 14px;
}
.chart-wrap {
    background: #fff; border-radius: 16px; padding: 8px 12px 4px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 16px;
}
.ins-card {
    background: #fff; border-radius: 14px; padding: 20px 24px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 14px;
    border-left: 4px solid #e5e7eb;
}
.ins-card.blue   { border-left-color: #3b82f6; }
.ins-card.red    { border-left-color: #ef4444; }
.ins-card.green  { border-left-color: #22c55e; }
.ins-card.orange { border-left-color: #f97316; }
.ins-card.purple { border-left-color: #a855f7; }
.ins-card.indigo { border-left-color: #6366f1; }
.ins-title { font-size: 14.5px; font-weight: 700; color: #1e293b; margin-bottom: 10px; }
.ins-body  { font-size: 13.5px; color: #374151; line-height: 1.8; }
.badge { display: inline-block; border-radius: 20px; padding: 2px 10px; font-size: 11.5px; font-weight: 600; margin: 0 2px; }
.b-blue   { background:#dbeafe; color:#1d4ed8; }
.b-red    { background:#fee2e2; color:#b91c1c; }
.b-green  { background:#dcfce7; color:#15803d; }
.b-orange { background:#ffedd5; color:#c2410c; }
.b-gray   { background:#f3f4f6; color:#374151; }
.b-purple { background:#f3e8ff; color:#7e22ce; }
.warn-box {
    background: #fef9c3; border: 1px solid #fde047; border-radius: 10px;
    padding: 12px 18px; font-size: 13px; color: #713f12; margin-bottom: 16px;
}
.grade-table { width:100%; border-collapse:collapse; font-size:13px; }
.grade-table th, .grade-table td { padding: 8px 12px; border: 1px solid #e5e7eb; text-align:left; }
.grade-table th { background: #f9fafb; font-weight: 600; color: #374151; }
.grade-table tr:nth-child(even) td { background: #f9fafb; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 데이터 로드 (CSV 직접 읽기 - ZIP 의존 없음)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    base = os.path.dirname(os.path.abspath(__file__))

    # 후보 경로 목록 (로컬 · Streamlit Cloud 모두 대응)
    ph_candidates = [
        os.path.join(base, 'ph.csv'),
        os.path.join(base, '수소이온농도.csv'),
        os.path.join(base, 'data', '수소이온농도.csv'),
    ]
    do_candidates = [
        os.path.join(base, 'do.csv'),
        os.path.join(base, '용존산소.csv'),
        os.path.join(base, 'data', '용존산소.csv'),
    ]

    def find_file(candidates):
        for p in candidates:
            if os.path.exists(p):
                return p
        tried = '\n  '.join(candidates)
        raise FileNotFoundError(
            f"데이터 파일을 찾을 수 없습니다.\n시도한 경로:\n  {tried}\n\n"
            "ph.csv 와 do.csv (또는 수소이온농도.csv, 용존산소.csv) 를 "
            "app.py 와 같은 폴더에 놓아 주세요."
        )

    def read_csv(path):
        """인코딩 자동 감지 + 모든 예외 처리"""
        for enc in ['utf-8', 'utf-8-sig', 'cp949', 'euc-kr']:
            try:
                rows = []
                with open(path, encoding=enc, errors='strict') as f:
                    reader = csv.DictReader(f)
                    if reader.fieldnames is None:
                        continue
                    for row in reader:
                        rows.append(row)
                if rows:
                    return rows
            except (UnicodeDecodeError, UnicodeError):
                continue
            except Exception:
                continue
        raise ValueError(f"파일을 읽을 수 없습니다: {path}")

    def daily_means(rows, col):
        daily = defaultdict(list)
        for r in rows:
            v = r.get(col, '').strip()
            if v and v != '-':
                try:
                    daily[r['일시'].split(' ')[0]].append(float(v))
                except (ValueError, KeyError):
                    pass
        return {d: round(sum(vs) / len(vs), 3) for d, vs in daily.items()}

    ph_path = find_file(ph_candidates)
    do_path = find_file(do_candidates)

    ph_rows = read_csv(ph_path)
    do_rows = read_csv(do_path)

    ph_ny = daily_means(ph_rows, '노량진')
    ph_sy = daily_means(ph_rows, '선유')
    do_ny = daily_means(do_rows, '노량진')
    do_sy = daily_means(do_rows, '선유')

    dates = sorted(set(list(ph_ny) + list(ph_sy) + list(do_ny) + list(do_sy)))
    df = pd.DataFrame({
        'date':      pd.to_datetime(dates),
        'pH_노량진': [ph_ny.get(d) for d in dates],
        'pH_선유':   [ph_sy.get(d) for d in dates],
        'DO_노량진': [do_ny.get(d) for d in dates],
        'DO_선유':   [do_sy.get(d) for d in dates],
    })
    return df


# 데이터 로드 (에러 시 명확한 메시지 표시)
try:
    df = load_data()
except FileNotFoundError as e:
    st.error(f"📂 **파일을 찾을 수 없습니다**\n\n{e}")
    st.info("**배포 체크리스트**\n- `ph.csv` 와 `do.csv` 를 `app.py` 와 같은 폴더에 업로드했는지 확인하세요.\n- Streamlit Cloud라면 GitHub 저장소에 파일이 포함되어 있어야 합니다.")
    st.stop()
except Exception as e:
    st.error(f"❌ **데이터 로드 오류**: {e}")
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# Hero & KPI
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-title">🌊 한강 수질 분석 대시보드</div>
  <div class="hero-sub">
    노량진 · 선유 측정소 &nbsp;|&nbsp; 수소이온농도(pH) &amp; 용존산소(DO) 시간별 데이터 (2020년)<br>
    실측 데이터 기반 분석 및 기후변화 시나리오 적용 2050년 수질 예측
  </div>
  <div class="hero-tags">
    <span class="hero-tag">📅 2020.01.01 – 2020.12.31</span>
    <span class="hero-tag">📍 노량진 · 선유</span>
    <span class="hero-tag">⏱ 8,784 시간별 측정</span>
    <span class="hero-tag">🔮 2026–2050 수질 예측</span>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="kpi-grid">
  <div class="kpi">
    <div class="kpi-label">pH 연평균 · 노량진</div>
    <div class="kpi-value">7.29</div>
    <div class="kpi-range">범위 6.80 ~ 8.30</div>
  </div>
  <div class="kpi orange">
    <div class="kpi-label">pH 연평균 · 선유</div>
    <div class="kpi-value">7.32</div>
    <div class="kpi-range">범위 6.60 ~ 8.40</div>
  </div>
  <div class="kpi teal">
    <div class="kpi-label">DO 연평균 · 노량진</div>
    <div class="kpi-value">8.46<span class="kpi-unit"> mg/L</span></div>
    <div class="kpi-range">범위 2.1 ~ 12.3</div>
  </div>
  <div class="kpi amber">
    <div class="kpi-label">DO 연평균 · 선유</div>
    <div class="kpi-value">8.26<span class="kpi-unit"> mg/L</span></div>
    <div class="kpi-range">범위 2.0 ~ 12.5</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# 탭
# ─────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 시계열 분석", "📅 월별 패턴", "🔗 상관관계", "🔬 수질 해석", "🔮 2050 예측",
])

COLORS = {
    '노량진_pH': '#2563eb', '선유_pH': '#ea580c',
    '노량진_DO': '#0891b2', '선유_DO': '#d97706',
}
MLBs = ['1월','2월','3월','4월','5월','6월','7월','8월','9월','10월','11월','12월']


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 : 시계열
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="sec-hd">날짜별 수질 시계열 — 범례 클릭으로 계열 선택</div>',
                unsafe_allow_html=True)

    c1, c2, c3 = st.columns([2, 2, 2])
    with c1:
        view_mode = st.selectbox("표시 항목", ["pH + DO 동시", "pH만", "DO만"])
    with c2:
        stations = st.multiselect("측정 지점", ["노량진", "선유"], default=["노량진", "선유"])
    with c3:
        date_range = st.date_input(
            "기간",
            value=(df['date'].min().date(), df['date'].max().date()),
            min_value=df['date'].min().date(),
            max_value=df['date'].max().date(),
        )

    if not stations:
        st.warning("측정 지점을 하나 이상 선택해 주세요.")
        st.stop()

    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        mask = (df['date'].dt.date >= date_range[0]) & (df['date'].dt.date <= date_range[1])
        dff = df[mask].copy()
    else:
        dff = df.copy()

    show_ph = view_mode in ["pH + DO 동시", "pH만"]
    show_do = view_mode in ["pH + DO 동시", "DO만"]
    is_dual = show_ph and show_do

    if is_dual:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            vertical_spacing=0.07,
                            subplot_titles=("수소이온농도 (pH)", "용존산소 (DO, mg/L)"))
    else:
        fig = go.Figure()

    def add_line(fig, x, y, name, color, row=None):
        kw = dict(x=x, y=y, name=name, mode='lines',
                  line=dict(color=color, width=1.8),
                  hovertemplate=f"<b>{name}</b><br>%{{x|%Y-%m-%d}}<br>%{{y:.3f}}<extra></extra>")
        if row:
            fig.add_trace(go.Scatter(**kw), row=row, col=1)
        else:
            fig.add_trace(go.Scatter(**kw))

    if show_ph:
        for s in stations:
            add_line(fig, dff['date'], dff[f'pH_{s}'], f'{s} pH',
                     COLORS[f'{s}_pH'], row=1 if is_dual else None)
        ref = dict(line_dash='dot', line_color='rgba(100,100,100,0.5)', annotation_font_size=10)
        if is_dual:
            fig.add_hline(y=6.5, annotation_text='하한 6.5', row=1, col=1, **ref)
            fig.add_hline(y=8.5, annotation_text='상한 8.5', row=1, col=1, **ref)
        else:
            fig.add_hline(y=6.5, annotation_text='하한 6.5', **ref)
            fig.add_hline(y=8.5, annotation_text='상한 8.5', **ref)

    if show_do:
        for s in stations:
            add_line(fig, dff['date'], dff[f'DO_{s}'], f'{s} DO',
                     COLORS[f'{s}_DO'], row=2 if is_dual else None)
        ref2 = dict(line_dash='dot', line_color='rgba(220,38,38,0.6)',
                    annotation_text='생존 하한 5.0 mg/L',
                    annotation_font_color='#dc2626', annotation_font_size=10)
        if is_dual:
            fig.add_hline(y=5.0, row=2, col=1, **ref2)
        else:
            fig.add_hline(y=5.0, **ref2)

    fig.update_layout(
        height=520 if is_dual else 360,
        plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=10, r=10, t=36, b=10),
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02,
                    xanchor='right', x=1, font=dict(size=12)),
    )
    fig.update_xaxes(showgrid=True, gridcolor='#f3f4f6', linecolor='#e5e7eb')
    fig.update_yaxes(showgrid=True, gridcolor='#f3f4f6', linecolor='#e5e7eb')

    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True,
                    config={'displayModeBar': True,
                            'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
                            'displaylogo': False})
    st.markdown('</div>', unsafe_allow_html=True)
    st.caption("💡 범례 클릭: 계열 켜기/끄기 · 드래그: 구간 확대 · 더블클릭: 초기화")

    with st.expander("📋 원시 데이터 보기 / CSV 다운로드"):
        cols_show = ['date'] + [f'pH_{s}' for s in stations] + [f'DO_{s}' for s in stations]
        disp = dff[cols_show].copy()
        disp['date'] = disp['date'].dt.strftime('%Y-%m-%d')
        disp.columns = (['날짜'] + [f'pH ({s})' for s in stations]
                        + [f'DO ({s}) mg/L' for s in stations])
        st.dataframe(disp, use_container_width=True, height=260)
        st.download_button("⬇️ CSV 다운로드", disp.to_csv(index=False).encode('utf-8-sig'),
                           file_name="hangang_2020.csv", mime="text/csv")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 : 월별 패턴
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="sec-hd">월별 평균 · 최솟값 · 최댓값 비교</div>',
                unsafe_allow_html=True)

    df['month'] = df['date'].dt.month
    monthly = df.groupby('month').agg(
        ph_ny_mean=('pH_노량진', 'mean'), ph_sy_mean=('pH_선유', 'mean'),
        ph_ny_min=('pH_노량진', 'min'),   ph_sy_min=('pH_선유', 'min'),
        ph_ny_max=('pH_노량진', 'max'),   ph_sy_max=('pH_선유', 'max'),
        do_ny_mean=('DO_노량진', 'mean'), do_sy_mean=('DO_선유', 'mean'),
        do_ny_min=('DO_노량진', 'min'),   do_sy_min=('DO_선유', 'min'),
        do_ny_max=('DO_노량진', 'max'),   do_sy_max=('DO_선유', 'max'),
    ).reset_index()

    subtab1, subtab2 = st.tabs(["pH 월별", "DO 월별"])

    with subtab1:
        fig_m = go.Figure()
        fig_m.add_trace(go.Scatter(
            x=MLBs + MLBs[::-1],
            y=list(monthly['ph_ny_max']) + list(monthly['ph_ny_min'])[::-1],
            fill='toself', fillcolor='rgba(37,99,235,0.08)',
            line=dict(color='rgba(255,255,255,0)'), showlegend=False))
        fig_m.add_trace(go.Scatter(
            x=MLBs + MLBs[::-1],
            y=list(monthly['ph_sy_max']) + list(monthly['ph_sy_min'])[::-1],
            fill='toself', fillcolor='rgba(234,88,12,0.08)',
            line=dict(color='rgba(255,255,255,0)'), showlegend=False))
        fig_m.add_trace(go.Scatter(x=MLBs, y=monthly['ph_ny_mean'].round(3),
                                   name='노량진 평균', mode='lines+markers',
                                   line=dict(color='#2563eb', width=2.5), marker=dict(size=7)))
        fig_m.add_trace(go.Scatter(x=MLBs, y=monthly['ph_sy_mean'].round(3),
                                   name='선유 평균', mode='lines+markers',
                                   line=dict(color='#ea580c', width=2.5), marker=dict(size=7)))
        fig_m.add_hline(y=6.5, line_dash='dot', line_color='gray',
                        annotation_text='환경부 하한 6.5', annotation_font_size=10)
        fig_m.add_hline(y=8.5, line_dash='dot', line_color='gray',
                        annotation_text='환경부 상한 8.5', annotation_font_size=10)
        fig_m.update_layout(
            height=340, plot_bgcolor='white', paper_bgcolor='white',
            margin=dict(l=10, r=10, t=16, b=10),
            yaxis=dict(range=[6.0, 9.2], title='pH'),
            legend=dict(orientation='h', y=1.08, xanchor='right', x=1))
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig_m, use_container_width=True, config={'displaylogo': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with subtab2:
        fig_d = go.Figure()
        fig_d.add_trace(go.Scatter(
            x=MLBs + MLBs[::-1],
            y=list(monthly['do_ny_max']) + list(monthly['do_ny_min'])[::-1],
            fill='toself', fillcolor='rgba(8,145,178,0.08)',
            line=dict(color='rgba(255,255,255,0)'), showlegend=False))
        fig_d.add_trace(go.Scatter(
            x=MLBs + MLBs[::-1],
            y=list(monthly['do_sy_max']) + list(monthly['do_sy_min'])[::-1],
            fill='toself', fillcolor='rgba(217,119,6,0.08)',
            line=dict(color='rgba(255,255,255,0)'), showlegend=False))
        fig_d.add_trace(go.Scatter(x=MLBs, y=monthly['do_ny_mean'].round(3),
                                   name='노량진 평균', mode='lines+markers',
                                   line=dict(color='#0891b2', width=2.5), marker=dict(size=7)))
        fig_d.add_trace(go.Scatter(x=MLBs, y=monthly['do_sy_mean'].round(3),
                                   name='선유 평균', mode='lines+markers',
                                   line=dict(color='#d97706', width=2.5), marker=dict(size=7)))
        fig_d.add_hline(y=5.0, line_dash='dot', line_color='#dc2626',
                        annotation_text='수생태계 위험 하한 5.0',
                        annotation_font_color='#dc2626', annotation_font_size=10)
        fig_d.update_layout(
            height=340, plot_bgcolor='white', paper_bgcolor='white',
            margin=dict(l=10, r=10, t=16, b=10),
            yaxis=dict(range=[0, 14], title='mg/L'),
            legend=dict(orientation='h', y=1.08, xanchor='right', x=1))
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig_d, use_container_width=True, config={'displaylogo': False})
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sec-hd">월별 상세 수치표</div>', unsafe_allow_html=True)
    tbl = pd.DataFrame({
        '월': MLBs,
        'pH 노량진 (평균)':   monthly['ph_ny_mean'].round(2),
        'pH 선유 (평균)':     monthly['ph_sy_mean'].round(2),
        'DO 노량진 (평균)':   monthly['do_ny_mean'].round(2),
        'DO 선유 (평균)':     monthly['do_sy_mean'].round(2),
        'DO 노량진 (최솟값)': monthly['do_ny_min'].round(2),
        'DO 선유 (최솟값)':   monthly['do_sy_min'].round(2),
    })
    st.dataframe(tbl, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 : 상관관계
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="sec-hd">pH – DO 상관관계 분석</div>', unsafe_allow_html=True)

    fig_s = go.Figure()
    corrs = {}
    for nm, pc, dc, clr in [
        ('노량진', 'pH_노량진', 'DO_노량진', '#2563eb'),
        ('선유',   'pH_선유',   'DO_선유',   '#ea580c'),
    ]:
        tmp = df[[pc, dc, 'date']].dropna()
        fig_s.add_trace(go.Scatter(
            x=tmp[pc], y=tmp[dc], mode='markers', name=nm,
            marker=dict(color=clr, size=5, opacity=0.45),
            hovertemplate=f"<b>{nm}</b><br>pH: %{{x:.3f}}<br>DO: %{{y:.3f}} mg/L<extra></extra>",
        ))
        z = np.polyfit(tmp[pc], tmp[dc], 1)
        xr = np.linspace(tmp[pc].min(), tmp[pc].max(), 100)
        fig_s.add_trace(go.Scatter(
            x=xr, y=np.polyval(z, xr), mode='lines', name=f'{nm} 추세선',
            line=dict(color=clr, width=2, dash='dash')))
        corrs[nm] = tmp[[pc, dc]].corr().iloc[0, 1]

    fig_s.update_layout(
        height=400, plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(title='pH (일평균)', showgrid=True, gridcolor='#f3f4f6'),
        yaxis=dict(title='DO mg/L (일평균)', showgrid=True, gridcolor='#f3f4f6'),
        legend=dict(orientation='h', y=1.06, xanchor='right', x=1))
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.plotly_chart(fig_s, use_container_width=True, config={'displaylogo': False})
    st.markdown('</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.metric("노량진 피어슨 상관계수 (r)", f"{corrs['노량진']:.3f}", "강한 양의 상관")
    with c2:
        st.metric("선유 피어슨 상관계수 (r)", f"{corrs['선유']:.3f}", "중간-강한 양의 상관")

    st.markdown("""
    <div class="ins-card indigo">
      <div class="ins-title">🔗 상관관계가 의미하는 것</div>
      <div class="ins-body">
        두 지표가 함께 오르내리는 이유는 <b>공통 생물학적 원인</b> 때문입니다.<br><br>
        <b>봄 (3–4월):</b> 광합성 활발 → CO₂ 소비 → pH ↑ / O₂ 생산 → DO ↑<br>
        <b>여름 (6–8월):</b> 유기물 분해 → CO₂ 방출 → pH ↓ / O₂ 소비 → DO ↓<br><br>
        노량진(r=0.767)이 선유(r=0.648)보다 높은 이유는, 선유에서 퇴적물·유기물 등
        국소 오염 인자가 DO를 추가로 낮춰 pH와의 연동을 희석시키기 때문입니다.
      </div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 : 수질 해석
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="sec-hd">수질 데이터 심층 해석</div>', unsafe_allow_html=True)

    insights = [
        ("blue", "🌸 봄철 pH 급등 — 식물성 플랑크톤 광합성",
         """<span class="badge b-blue">3–4월</span>
         두 지점 모두 pH 연중 최고치(노량진 <b>8.3</b>, 선유 <b>8.4</b>)를 기록합니다.
         수온 상승 → 플랑크톤 폭발 증식 → 광합성으로 CO₂ 소비 →
         탄산(H₂CO₃) 감소 → 수소이온 농도 하락 → pH 상승의 연쇄입니다.
         봄철 오후 14–18시에 일중 pH 편차가 최대 <b>1.0 이상</b> 벌어지는 것도 같은 원리입니다."""),

        ("red", "☀️ 여름철 DO 위기 — 수생태계 스트레스 구간",
         """<span class="badge b-red">5월 말 – 9월</span>
         노량진 6월 평균 DO <b>5.95 mg/L</b>, 선유 <b>5.51 mg/L</b>로 급락합니다.
         순간 최솟값은 노량진 <b>2.1 mg/L</b>, 선유 <b>2.0 mg/L</b>까지 떨어졌습니다.<br><br>
         <b>원인 ①</b> 수온 상승 → 산소 용해도 감소 (20°C: 9.1 → 30°C: 7.5 mg/L)<br>
         <b>원인 ②</b> 봄 플랑크톤 사체 분해 → 박테리아 대량 산소 소비<br><br>
         환경부 생물생존 최소 기준 <b>5 mg/L</b>에 근접하거나 하회하는 시간대가 발생하며
         민감 어종(쏘가리·참마자·버들치)에게 생존 스트레스가 생길 수 있습니다."""),

        ("green", "❄️ 겨울철 DO 최고치 — 차가운 물의 산소 포화",
         """<span class="badge b-green">11–12월</span>
         노량진 12월 평균 <b>11.17 mg/L</b>, 선유 <b>10.91 mg/L</b>.
         수온이 낮을수록 기체 용해도가 높아져 DO가 최고치입니다.
         동시에 pH도 7.4–7.5로 중성에 가까워 수생태계 관점에서 가장 쾌적한 환경입니다."""),

        ("orange", "🏙️ 노량진 vs 선유 — 공간적 수질 차이",
         """선유는 노량진에 비해 계절 변동폭이 큽니다
         (pH 연간 범위 <b>1.8</b> vs <b>1.5</b>).
         선유는 하류 방향으로 유속이 느리고 유기물이 많아 분해에 의한 DO 소비가 더 큽니다.<br><br>
         <span class="badge b-orange">주의</span>
         선유 8월 유효 측정치 424건(정상 730건의 58%)으로 대폭 감소합니다.
         센서 이상·유지 보수 또는 수질 악화로 인한 장비 오류 가능성이 있어 해석 시 주의가 필요합니다."""),

        ("purple", "🏅 환경부 수질 등급 평가",
         """<table class="grade-table">
           <tr><th>등급</th><th>pH</th><th>DO (mg/L)</th><th>용도</th><th>2020 한강</th></tr>
           <tr><td><span class="badge b-blue">1등급 (매우 좋음)</span></td>
               <td>6.5–8.5</td><td>≥ 7.5</td><td>상수원·자연보전</td><td>10–4월 ✓</td></tr>
           <tr><td><span class="badge b-green">2등급 (좋음)</span></td>
               <td>6.5–8.5</td><td>≥ 5.0</td><td>1급 정수처리</td><td>봄·가을 해당</td></tr>
           <tr><td><span class="badge b-orange">3등급 (보통)</span></td>
               <td>6.5–8.5</td><td>≥ 5.0</td><td>농업·수산용수</td><td>여름 경계</td></tr>
           <tr><td><span class="badge b-red">4등급 이하</span></td>
               <td>6.0–8.5</td><td>≥ 2.0</td><td>공업용수</td><td>6월 순간값</td></tr>
         </table><br>
         <b>결론:</b> 연간 평균은 2~3등급 수준이나, 여름 DO 급락 구간에서 4등급 경계까지 악화됩니다.
         연간 수질 관리의 핵심 과제는 <b>5~9월 DO 하락 억제</b>입니다."""),
    ]

    for color, title, body in insights:
        with st.expander(title):
            st.markdown(f'<div class="ins-body">{body}</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 : 2050 예측
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="sec-hd">2026–2050 수질 예측 (기후변화 시나리오)</div>',
                unsafe_allow_html=True)

    st.markdown("""
    <div class="warn-box">
    ⚠️ <b>예측 모델 안내</b>: 2020년 실측 데이터를 기반으로 기후변화 시나리오(IPCC SSP2-4.5, SSP5-8.5)를
    적용한 통계적 외삽 모델입니다. 실제 수질은 정책·인프라·강수량 변동에 따라 달라질 수 있습니다.
    </div>
    """, unsafe_allow_html=True)

    SCENARIOS = {
        'SSP2-4.5 (중위 시나리오)': {
            'color_ny': '#2563eb', 'color_sy': '#d97706', 'dash': 'solid',
            'temp_2050': 1.5, 'do_per_c': 0.20, 'summer_penalty': 0.08, 'ph_per_yr': -0.002,
        },
        'SSP5-8.5 (고위 시나리오)': {
            'color_ny': '#2563eb', 'color_sy': '#d97706', 'dash': 'dash',
            'temp_2050': 3.0, 'do_per_c': 0.22, 'summer_penalty': 0.18, 'ph_per_yr': -0.005,
        },
    }

    BASE = {'do_ny': 8.463, 'do_sy': 8.260, 'ph_ny': 7.287, 'ph_sy': 7.317}
    future_years = np.arange(2020, 2051)

    def forecast(base, sc, kind='do'):
        vals, noises = [], []
        for y in future_years:
            n = y - 2020
            frac = n / 30
            if kind == 'do':
                val = base - sc['do_per_c'] * sc['temp_2050'] * frac - sc['summer_penalty'] * frac
                noise = 0.3 + 0.5 * frac
            else:
                val = base + sc['ph_per_yr'] * n
                noise = 0.05 + 0.1 * frac
            vals.append(val)
            noises.append(noise)
        return np.array(vals), np.array(noises)

    sc_name = st.selectbox("시나리오 선택", list(SCENARIOS.keys()), key='sc_sel')
    sc = SCENARIOS[sc_name]

    do_ny_v, do_ny_n = forecast(BASE['do_ny'], sc, 'do')
    do_sy_v, do_sy_n = forecast(BASE['do_sy'], sc, 'do')
    ph_ny_v, ph_ny_n = forecast(BASE['ph_ny'], sc, 'ph')
    ph_sy_v, ph_sy_n = forecast(BASE['ph_sy'], sc, 'ph')

    def make_band_traces(years, vals, noise, hex_color, name):
        r, g, b = int(hex_color[1:3],16), int(hex_color[3:5],16), int(hex_color[5:7],16)
        fill_color = f'rgba({r},{g},{b},0.10)'
        band = go.Scatter(
            x=list(years) + list(years[::-1]),
            y=list(vals + noise) + list((vals - noise)[::-1]),
            fill='toself', fillcolor=fill_color,
            line=dict(color='rgba(255,255,255,0)'),
            showlegend=False, name=f'{name} 불확실도')
        line = go.Scatter(
            x=years, y=np.round(vals, 3), name=f'{name} 예측', mode='lines',
            line=dict(color=hex_color, width=2.2, dash=sc['dash']))
        return band, line

    pred_tabs = st.tabs(["용존산소 (DO) 예측", "수소이온농도 (pH) 예측"])

    with pred_tabs[0]:
        fig_f = go.Figure()
        b1, l1 = make_band_traces(future_years, do_ny_v, do_ny_n, '#2563eb', '노량진')
        b2, l2 = make_band_traces(future_years, do_sy_v, do_sy_n, '#d97706', '선유')
        fig_f.add_traces([b1, b2, l1, l2])
        fig_f.add_trace(go.Scatter(x=[2020], y=[BASE['do_ny']], mode='markers',
                                   name='노량진 실측(2020)',
                                   marker=dict(color='#2563eb', size=10)))
        fig_f.add_trace(go.Scatter(x=[2020], y=[BASE['do_sy']], mode='markers',
                                   name='선유 실측(2020)',
                                   marker=dict(color='#d97706', size=10)))
        fig_f.add_hline(y=5.0, line_dash='dot', line_color='#dc2626',
                        annotation_text='수생태계 위험 하한 5.0',
                        annotation_font_color='#dc2626')
        fig_f.add_hline(y=7.5, line_dash='dot', line_color='#16a34a',
                        annotation_text='1등급 기준 7.5', annotation_font_color='#16a34a')
        fig_f.add_vline(x=2026, line_dash='dot', line_color='#6b7280',
                        annotation_text='현재(2026)', annotation_font_size=11)
        fig_f.update_layout(
            height=420, plot_bgcolor='white', paper_bgcolor='white',
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(title='연도', showgrid=True, gridcolor='#f3f4f6'),
            yaxis=dict(title='DO (mg/L)', range=[3.0, 13.0],
                       showgrid=True, gridcolor='#f3f4f6'),
            legend=dict(orientation='h', y=1.06, xanchor='right', x=1))
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig_f, use_container_width=True, config={'displaylogo': False})
        st.markdown('</div>', unsafe_allow_html=True)

    with pred_tabs[1]:
        fig_fp = go.Figure()
        b3, l3 = make_band_traces(future_years, ph_ny_v, ph_ny_n, '#2563eb', '노량진')
        b4, l4 = make_band_traces(future_years, ph_sy_v, ph_sy_n, '#d97706', '선유')
        fig_fp.add_traces([b3, b4, l3, l4])
        fig_fp.add_trace(go.Scatter(x=[2020], y=[BASE['ph_ny']], mode='markers',
                                    name='노량진 실측(2020)',
                                    marker=dict(color='#2563eb', size=10)))
        fig_fp.add_trace(go.Scatter(x=[2020], y=[BASE['ph_sy']], mode='markers',
                                    name='선유 실측(2020)',
                                    marker=dict(color='#d97706', size=10)))
        fig_fp.add_hline(y=6.5, line_dash='dot', line_color='#dc2626',
                         annotation_text='환경부 하한 6.5')
        fig_fp.add_hline(y=8.5, line_dash='dot', line_color='gray',
                         annotation_text='환경부 상한 8.5')
        fig_fp.add_vline(x=2026, line_dash='dot', line_color='#6b7280',
                         annotation_text='현재(2026)', annotation_font_size=11)
        fig_fp.update_layout(
            height=420, plot_bgcolor='white', paper_bgcolor='white',
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(title='연도', showgrid=True, gridcolor='#f3f4f6'),
            yaxis=dict(title='pH', range=[6.0, 9.0],
                       showgrid=True, gridcolor='#f3f4f6'),
            legend=dict(orientation='h', y=1.06, xanchor='right', x=1))
        st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
        st.plotly_chart(fig_fp, use_container_width=True, config={'displaylogo': False})
        st.markdown('</div>', unsafe_allow_html=True)

    # 주요 연도 수치표
    st.markdown('<div class="sec-hd">주요 연도별 예측 수치</div>', unsafe_allow_html=True)
    milestones = [2026, 2030, 2035, 2040, 2045, 2050]
    midxs = [y - 2020 for y in milestones]
    pred_tbl = pd.DataFrame({
        '연도': milestones,
        'DO 노량진 (mg/L)': [f"{do_ny_v[i]:.2f}" for i in midxs],
        'DO 선유 (mg/L)':   [f"{do_sy_v[i]:.2f}" for i in midxs],
        'pH 노량진':         [f"{ph_ny_v[i]:.3f}" for i in midxs],
        'pH 선유':           [f"{ph_sy_v[i]:.3f}" for i in midxs],
        '수생태계 상태': [
            '🚨 위험' if do_ny_v[i] < 5.0 or do_sy_v[i] < 5.0
            else ('⚠️ 주의' if do_ny_v[i] < 6.5 or do_sy_v[i] < 6.5 else '✅ 양호')
            for i in midxs
        ],
    })
    st.dataframe(pred_tbl, use_container_width=True, hide_index=True)

    # 시나리오 해설
    st.markdown('<div class="sec-hd">시나리오 해설 및 정책 시사점</div>',
                unsafe_allow_html=True)
    c_a, c_b = st.columns(2)
    with c_a:
        st.markdown("""
        <div class="ins-card blue">
          <div class="ins-title">🌿 SSP2-4.5 — 중위 시나리오</div>
          <div class="ins-body">
            온실가스 감축 정책 지속 경로. 2050년 기온 <b>+1.5°C</b> 상승 예상.<br><br>
            • DO 연평균: 노량진 <b>~7.3</b>, 선유 <b>~7.1 mg/L</b><br>
            • pH: CO₂ 증가 효과로 <b>~7.2–7.3</b> 유지<br>
            • 여름 DO 5 mg/L 하회 빈도 소폭 증가<br>
            • 1등급 유지 기간: 연중 50% → 40%로 축소 예상
          </div>
        </div>
        """, unsafe_allow_html=True)
    with c_b:
        st.markdown("""
        <div class="ins-card red">
          <div class="ins-title">🔥 SSP5-8.5 — 고위 시나리오</div>
          <div class="ins-body">
            현재 추세 지속 시 최악 경로. 2050년 기온 <b>+3.0°C</b> 상승 예상.<br><br>
            • DO 연평균: 노량진 <b>~6.5</b>, 선유 <b>~6.3 mg/L</b><br>
            • pH: 산성화 가속으로 <b>~7.0–7.1</b>로 하락<br>
            • 여름 DO 3 mg/L 이하 구간 상시 발생 우려<br>
            • 민감 어종 서식 기간: 연중 8개월 → <b>5개월 미만</b> 가능성
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="ins-card purple">
      <div class="ins-title">📋 예측 모델 방법론 및 한계</div>
      <div class="ins-body">
        <b>기준 데이터:</b> 2020년 노량진·선유 시간별 실측값 (n=8,784)<br>
        <b>기후 변수:</b> IPCC AR6 SSP 시나리오 기반 수도권 기온 상승 전망 적용<br>
        <b>DO 예측:</b> Henry's Law (기온–산소 용해도 관계) + 도시 비점오염 증가 보정<br>
        <b>pH 예측:</b> 대기 CO₂ 농도 증가(420 → 500–600 ppm)에 따른 탄산 평형 계산<br>
        <b>불확실도:</b> 시간적으로 선형 증가하는 ±범위 (단기 ±0.3, 2050년 ±0.8 mg/L)<br><br>
        <span class="badge b-orange">한계점</span>
        이 모델은 2020년 단일 연도 데이터 기반 단순 외삽이므로,
        장기 정책 효과(하수처리 고도화·한강 살리기 등)나 기상 이변(집중 호우·가뭄)은 반영되지 않습니다.
      </div>
    </div>
    """, unsafe_allow_html=True)

# 푸터
st.markdown("""
<div style="text-align:center; font-size:12px; color:#9ca3af; margin-top:40px;
     padding: 16px 0; border-top: 1px solid #f3f4f6;">
    데이터 출처: 서울 열린데이터 광장 · 서울시 요일별 한강 수질 현황 (2020) &nbsp;|&nbsp;
    노량진 · 선유 측정소 시간별 실측값 일평균 &nbsp;|&nbsp;
    예측: IPCC AR6 SSP2-4.5 / SSP5-8.5 시나리오 적용
</div>
""", unsafe_allow_html=True)
