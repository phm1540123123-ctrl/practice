import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

st.set_page_config(
    page_title="한강 수질 모니터링 · 2020",
    page_icon="💧",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}

.main { background-color: #f0f4f8; }

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1280px;
}

h1, h2, h3 { font-family: 'Noto Sans KR', sans-serif; }

.metric-card {
    background: white;
    border-radius: 14px;
    padding: 20px 24px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07);
    border-left: 4px solid #2563eb;
    margin-bottom: 8px;
}
.metric-card.orange { border-left-color: #ea580c; }
.metric-card.green  { border-left-color: #16a34a; }
.metric-card.red    { border-left-color: #dc2626; }

.metric-label {
    font-size: 12px;
    color: #6b7280;
    font-weight: 500;
    letter-spacing: 0.05em;
    margin-bottom: 4px;
}
.metric-value {
    font-size: 26px;
    font-weight: 700;
    color: #111827;
    line-height: 1.1;
}
.metric-sub {
    font-size: 11px;
    color: #9ca3af;
    margin-top: 3px;
}

.insight-box {
    background: white;
    border-radius: 14px;
    padding: 20px 24px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07);
    margin-bottom: 16px;
}
.insight-title {
    font-size: 15px;
    font-weight: 700;
    color: #1e3a5f;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.insight-body {
    font-size: 13.5px;
    color: #374151;
    line-height: 1.75;
}
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    margin-right: 4px;
}
.badge-blue  { background: #dbeafe; color: #1d4ed8; }
.badge-orange{ background: #ffedd5; color: #c2410c; }
.badge-green { background: #dcfce7; color: #15803d; }
.badge-red   { background: #fee2e2; color: #b91c1c; }
.badge-gray  { background: #f3f4f6; color: #374151; }

.section-header {
    font-size: 18px;
    font-weight: 700;
    color: #1e3a5f;
    border-bottom: 2px solid #e5e7eb;
    padding-bottom: 8px;
    margin: 28px 0 18px;
}

.chart-card {
    background: white;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.07);
    margin-bottom: 20px;
}

stExpander { border-radius: 12px !important; }
</style>
""", unsafe_allow_html=True)


# ── 데이터 로드 ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    import csv, os
    def parse_csv(path):
        rows = []
        for enc in ('cp949', 'euc-kr', 'utf-8-sig', 'utf-8'):
            try:
                with open(path, encoding=enc) as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        rows.append(row)
                return rows
            except (UnicodeDecodeError, FileNotFoundError):
                continue
        raise ValueError(f"파일을 읽을 수 없습니다: {path}")

    def daily_means(rows, col):
        from collections import defaultdict
        daily = defaultdict(list)
        for r in rows:
            v = r[col].strip()
            if v and v != '-':
                try:
                    date = r['일시'].split(' ')[0]
                    daily[date].append(float(v))
                except Exception:
                    pass
        return {d: round(sum(vs) / len(vs), 3) for d, vs in daily.items()}

    base = os.path.dirname(__file__)
    ph_rows = parse_csv(os.path.join(base, '수소이온농도.csv'))
    do_rows = parse_csv(os.path.join(base, '용존산소.csv'))

    ph_ny = daily_means(ph_rows, '노량진')
    ph_sy = daily_means(ph_rows, '선유')
    do_ny = daily_means(do_rows, '노량진')
    do_sy = daily_means(do_rows, '선유')

    dates = sorted(set(list(ph_ny) + list(ph_sy) + list(do_ny) + list(do_sy)))
    df = pd.DataFrame({
        'date': pd.to_datetime(dates),
        'pH_노량진': [ph_ny.get(d) for d in dates],
        'pH_선유':   [ph_sy.get(d) for d in dates],
        'DO_노량진': [do_ny.get(d) for d in dates],
        'DO_선유':   [do_sy.get(d) for d in dates],
    })
    return df


df = load_data()

# ── 헤더 ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding: 10px 0 24px;">
    <div style="font-size:36px; font-weight:800; color:#1e3a5f; letter-spacing:-0.5px;">
        💧 한강 수질 모니터링
    </div>
    <div style="font-size:15px; color:#6b7280; margin-top:6px;">
        노량진 · 선유 측정소 &nbsp;|&nbsp; 2020년 수소이온농도(pH) &amp; 용존산소(DO) 일별 분석
    </div>
</div>
""", unsafe_allow_html=True)

# ── 요약 지표 ─────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
metrics = [
    ("pH 평균 (노량진)", f"{df['pH_노량진'].mean():.2f}", "범위 6.80 – 8.30", "blue"),
    ("pH 평균 (선유)",   f"{df['pH_선유'].mean():.2f}",   "범위 6.60 – 8.40", "orange"),
    ("DO 평균 (노량진)", f"{df['DO_노량진'].mean():.2f} mg/L", "범위 2.1 – 12.3", "green"),
    ("DO 평균 (선유)",   f"{df['DO_선유'].mean():.2f} mg/L",   "범위 2.0 – 12.5", "red"),
]
for col, (label, val, sub, color) in zip([c1, c2, c3, c4], metrics):
    with col:
        st.markdown(f"""
        <div class="metric-card {color}">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{val}</div>
            <div class="metric-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

# ── 컨트롤 ────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📊 대화형 시계열 그래프</div>', unsafe_allow_html=True)

col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([2, 2, 2])
with col_ctrl1:
    view_mode = st.selectbox(
        "표시 방식",
        ["pH와 DO 동시 표시", "pH만 표시", "DO만 표시"],
        label_visibility="visible"
    )
with col_ctrl2:
    stations = st.multiselect(
        "측정 지점 선택",
        ["노량진", "선유"],
        default=["노량진", "선유"]
    )
with col_ctrl3:
    date_range = st.date_input(
        "기간 선택",
        value=(df['date'].min().date(), df['date'].max().date()),
        min_value=df['date'].min().date(),
        max_value=df['date'].max().date(),
    )

# 날짜 필터
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    mask = (df['date'].dt.date >= date_range[0]) & (df['date'].dt.date <= date_range[1])
    dff = df[mask].copy()
else:
    dff = df.copy()

if not stations:
    st.warning("측정 지점을 하나 이상 선택해 주세요.")
    st.stop()

# ── 색상 ──────────────────────────────────────────────────────────────────────
COLORS = {
    '노량진_pH': '#2563eb',
    '선유_pH':   '#ea580c',
    '노량진_DO': '#0891b2',
    '선유_DO':   '#d97706',
}
REF_COLOR_pH = 'rgba(156,163,175,0.5)'
REF_COLOR_DO = 'rgba(220,38,38,0.35)'

# ── 그래프 ────────────────────────────────────────────────────────────────────
show_ph = view_mode in ["pH와 DO 동시 표시", "pH만 표시"]
show_do = view_mode in ["pH와 DO 동시 표시", "DO만 표시"]

if show_ph and show_do:
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=("수소이온농도 (pH)", "용존산소 (DO, mg/L)")
    )
    ph_row, do_row = 1, 2
else:
    fig = go.Figure()
    ph_row = do_row = None

def add_trace(fig, x, y, name, color, row=None, dash='solid', width=1.8):
    kwargs = dict(
        x=x, y=y, name=name,
        mode='lines',
        line=dict(color=color, width=width, dash=dash),
        hovertemplate=f"<b>{name}</b><br>%{{x|%Y-%m-%d}}<br>값: %{{y:.2f}}<extra></extra>",
    )
    if row:
        fig.add_trace(go.Scatter(**kwargs), row=row, col=1)
    else:
        fig.add_trace(go.Scatter(**kwargs))

def add_hline(fig, y, label, color, row=None, is_subplots=True):
    if is_subplots and row:
        fig.add_hline(y=y, line_dash='dot', line_color=color,
                      annotation_text=label,
                      annotation_font_size=11,
                      annotation_font_color=color,
                      row=row, col=1)
    else:
        fig.add_hline(y=y, line_dash='dot', line_color=color,
                      annotation_text=label,
                      annotation_font_size=11,
                      annotation_font_color=color)

is_subplots = show_ph and show_do

if show_ph:
    for st_name in stations:
        col_name = f'pH_{st_name}'
        add_trace(fig, dff['date'], dff[col_name], f'{st_name} pH',
                  COLORS[f'{st_name}_pH'], row=ph_row if is_subplots else None)
    if is_subplots:
        fig.add_hline(y=6.5, line_dash='dot', line_color='rgba(156,163,175,0.8)',
                      annotation_text='하한 기준 6.5', annotation_font_size=10,
                      annotation_font_color='gray', row=1, col=1)
        fig.add_hline(y=8.5, line_dash='dot', line_color='rgba(156,163,175,0.8)',
                      annotation_text='상한 기준 8.5', annotation_font_size=10,
                      annotation_font_color='gray', row=1, col=1)
    else:
        fig.add_hline(y=6.5, line_dash='dot', line_color='gray',
                      annotation_text='하한 기준 6.5', annotation_font_size=10)
        fig.add_hline(y=8.5, line_dash='dot', line_color='gray',
                      annotation_text='상한 기준 8.5', annotation_font_size=10)

if show_do:
    for st_name in stations:
        col_name = f'DO_{st_name}'
        add_trace(fig, dff['date'], dff[col_name], f'{st_name} DO',
                  COLORS[f'{st_name}_DO'], row=do_row if is_subplots else None)
    if is_subplots:
        fig.add_hline(y=5.0, line_dash='dot', line_color='rgba(220,38,38,0.7)',
                      annotation_text='수생태계 주의 5.0', annotation_font_size=10,
                      annotation_font_color='#dc2626', row=2, col=1)
    else:
        fig.add_hline(y=5.0, line_dash='dot', line_color='#dc2626',
                      annotation_text='수생태계 주의 5.0', annotation_font_size=10,
                      annotation_font_color='#dc2626')

# 레이아웃
fig.update_layout(
    height=560 if is_subplots else 380,
    plot_bgcolor='white',
    paper_bgcolor='white',
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(
        orientation='h', yanchor='bottom', y=1.01,
        xanchor='right', x=1,
        bgcolor='rgba(255,255,255,0.9)',
        bordercolor='#e5e7eb', borderwidth=1,
        font=dict(size=12)
    ),
    hovermode='x unified',
    font=dict(family="Noto Sans KR, sans-serif"),
)
fig.update_xaxes(showgrid=True, gridcolor='#f3f4f6', linecolor='#e5e7eb')
fig.update_yaxes(showgrid=True, gridcolor='#f3f4f6', linecolor='#e5e7eb')

st.markdown('<div class="chart-card">', unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True,
                                                        'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
                                                        'displaylogo': False})
st.markdown('</div>', unsafe_allow_html=True)

st.caption("💡 범례를 클릭하면 개별 계열을 켜고 끌 수 있습니다. 그래프를 드래그하면 확대, 더블클릭하면 초기화됩니다.")

# ── 월별 평균 바 차트 ──────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📅 월별 평균 비교</div>', unsafe_allow_html=True)

dff['month'] = dff['date'].dt.month
monthly = dff.groupby('month').mean(numeric_only=True).reset_index()
month_labels = ['1월','2월','3월','4월','5월','6월','7월','8월','9월','10월','11월','12월']

tab1, tab2 = st.tabs(["📈 pH 월별 평균", "🫧 DO 월별 평균"])

with tab1:
    fig_m = go.Figure()
    if '노량진' in stations:
        fig_m.add_trace(go.Bar(x=month_labels, y=monthly['pH_노량진'],
                               name='노량진', marker_color='#3b82f6', opacity=0.85))
    if '선유' in stations:
        fig_m.add_trace(go.Bar(x=month_labels, y=monthly['pH_선유'],
                               name='선유', marker_color='#f97316', opacity=0.85))
    fig_m.add_hline(y=6.5, line_dash='dot', line_color='gray', annotation_text='하한 6.5')
    fig_m.add_hline(y=8.5, line_dash='dot', line_color='gray', annotation_text='상한 8.5')
    fig_m.update_layout(
        barmode='group', height=300, plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=10, r=10, t=20, b=10),
        yaxis=dict(range=[6.0, 9.0], title='pH'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        font=dict(family="Noto Sans KR, sans-serif"),
    )
    st.plotly_chart(fig_m, use_container_width=True, config={'displaylogo': False})

with tab2:
    fig_d = go.Figure()
    if '노량진' in stations:
        fig_d.add_trace(go.Bar(x=month_labels, y=monthly['DO_노량진'],
                               name='노량진', marker_color='#0891b2', opacity=0.85))
    if '선유' in stations:
        fig_d.add_trace(go.Bar(x=month_labels, y=monthly['DO_선유'],
                               name='선유', marker_color='#d97706', opacity=0.85))
    fig_d.add_hline(y=5.0, line_dash='dot', line_color='#dc2626',
                    annotation_text='수생태계 주의 5.0 mg/L', annotation_font_color='#dc2626')
    fig_d.update_layout(
        barmode='group', height=300, plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(l=10, r=10, t=20, b=10),
        yaxis=dict(range=[0, 13], title='mg/L'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        font=dict(family="Noto Sans KR, sans-serif"),
    )
    st.plotly_chart(fig_d, use_container_width=True, config={'displaylogo': False})


# ── pH–DO 산점도 ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🔗 pH–DO 상관관계</div>', unsafe_allow_html=True)

fig_s = go.Figure()
scatter_cfg = [
    ('노량진', 'pH_노량진', 'DO_노량진', '#2563eb'),
    ('선유',   'pH_선유',   'DO_선유',   '#ea580c'),
]
for name, ph_col, do_col, color in scatter_cfg:
    if name not in stations:
        continue
    tmp = dff[[ph_col, do_col, 'date']].dropna()
    fig_s.add_trace(go.Scatter(
        x=tmp[ph_col], y=tmp[do_col],
        mode='markers',
        name=name,
        marker=dict(color=color, size=5, opacity=0.55),
        hovertemplate=(f"<b>{name}</b><br>pH: %{{x:.2f}}<br>"
                       f"DO: %{{y:.2f}} mg/L<br>%{{customdata}}<extra></extra>"),
        customdata=tmp['date'].dt.strftime('%Y-%m-%d'),
    ))
    # 추세선
    valid = tmp.dropna()
    if len(valid) > 2:
        z = np.polyfit(valid[ph_col], valid[do_col], 1)
        xr = np.linspace(valid[ph_col].min(), valid[ph_col].max(), 100)
        fig_s.add_trace(go.Scatter(
            x=xr, y=np.polyval(z, xr),
            mode='lines', name=f'{name} 추세선',
            line=dict(color=color, width=1.5, dash='dash'),
            showlegend=True,
        ))

fig_s.update_layout(
    height=360, plot_bgcolor='white', paper_bgcolor='white',
    margin=dict(l=20, r=20, t=20, b=20),
    xaxis=dict(title='pH', showgrid=True, gridcolor='#f3f4f6'),
    yaxis=dict(title='DO (mg/L)', showgrid=True, gridcolor='#f3f4f6'),
    legend=dict(orientation='h', yanchor='bottom', y=1.01, xanchor='right', x=1),
    font=dict(family="Noto Sans KR, sans-serif"),
)
st.plotly_chart(fig_s, use_container_width=True, config={'displaylogo': False})

corr_ny = dff[['pH_노량진', 'DO_노량진']].dropna().corr().iloc[0, 1]
corr_sy = dff[['pH_선유', 'DO_선유']].dropna().corr().iloc[0, 1]
st.info(f"📐 피어슨 상관계수 — 노량진: **{corr_ny:.3f}** &nbsp;|&nbsp; 선유: **{corr_sy:.3f}**")


# ── 심층 해석 ──────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">🔬 수질 데이터 심층 해석</div>', unsafe_allow_html=True)

insights = [
    ("🌸 봄철 pH 급등 — 식물성 플랑크톤의 광합성",
     """<span class="badge badge-blue">3–4월</span>
     두 지점 모두 pH가 연중 최고치(노량진 8.3, 선유 8.4)를 기록합니다.
     수온이 올라가면 강 속 식물성 플랑크톤이 폭발적으로 증식하고,
     활발한 <b>광합성</b>이 수중 CO₂를 소비합니다. CO₂가 줄면 탄산(H₂CO₃)이 감소해
     수소이온 농도가 낮아지고 pH가 상승합니다.
     <br><br>
     봄철 오후 시간대(14~18시)에 일중 pH 편차가 최대 1.0 이상 벌어지는 현상도
     같은 이유입니다. 빛이 강한 낮 시간의 광합성 → CO₂ 소비 → pH 상승의 사이클이
     일별 데이터에서도 표준편차 증가로 나타납니다."""),

    ("☀️ 여름철 DO 위기 — 수생태계 스트레스 구간",
     """<span class="badge badge-red">5월 말 – 6월</span>
     노량진 6월 평균 DO <b>5.95 mg/L</b>, 선유 <b>5.51 mg/L</b>로 급락합니다.
     순간 최솟값은 노량진 2.1 mg/L, 선유 2.0 mg/L까지 떨어졌습니다.
     <br><br>
     원인은 두 가지가 겹칩니다. 첫째, 수온이 높을수록 물에 녹을 수 있는 산소의 최대량
     (포화 용존산소)이 줄어듭니다(20°C: 9.1 mg/L → 30°C: 7.5 mg/L).
     둘째, 봄에 번성했던 플랑크톤·조류가 죽어 분해될 때
     박테리아가 산소를 대량 소비합니다.
     <br><br>
     환경부 기준 생물생존 최소 요구치는 <b>5 mg/L</b>입니다. 이 구간에서
     민감 어종(쏘가리, 참마자 등)에게 생존 스트레스가 발생할 가능성이 있습니다."""),

    ("❄️ 겨울철 DO 최고치 — 차가운 물의 산소 포화",
     """<span class="badge badge-green">11–12월</span>
     노량진 12월 평균 DO <b>11.17 mg/L</b>, 선유 <b>10.91 mg/L</b>로 최고를 기록합니다.
     수온이 낮을수록 물 분자 간 간격이 좁아져 기체 용해도가 증가하기 때문입니다.
     이 시기는 pH도 7.4–7.5로 중성에 가깝고 DO도 풍부해
     수생태계 관점에서 가장 쾌적한 환경입니다."""),

    ("🏙️ 노량진 vs 선유 — 공간적 수질 차이",
     """선유는 노량진에 비해 계절 변동폭이 큽니다
     (<b>pH 연간 범위 1.8 vs 1.5</b>, <b>DO 변동폭 유사하나 하한이 더 낮음</b>).
     선유 지점은 한강 하류 쪽으로 유속이 느리고 퇴적물·유기물이 더 많이 쌓이는 구간입니다.
     유기물이 많을수록 분해 시 산소 소비가 늘어나 DO 하락 폭이 커집니다.
     <br><br>
     또한 선유 8월 데이터는 유효 측정치가 424건(정상 730건)으로
     절반 가까이 결측됩니다. 센서 이상, 유지 보수, 또는 수질 악화로 인한
     장비 트러블로 추정되며 이 기간 해석에 주의가 필요합니다."""),

    ("🔗 pH–DO 양의 상관관계 (r = 0.77 / 0.65)",
     """두 지표가 함께 오르내리는 이유는 공통 원인이 있기 때문입니다.
     <br>
     • 봄 광합성 활발 → CO₂ 소비 → pH ↑, O₂ 생산 → DO ↑<br>
     • 여름 유기물 분해 → CO₂ 방출 → pH ↓, O₂ 소비 → DO ↓<br><br>
     노량진의 상관계수(0.77)가 선유(0.65)보다 높은 것은,
     선유에서 다른 국소적 오염·퇴적 요인이 추가로 DO를 낮춰
     pH와의 연동성을 일부 희석시키기 때문으로 해석됩니다."""),

    ("🏅 수질 등급 평가 (환경부 하천 수질 기준)",
     """연간 평균으로 볼 때 두 지점 모두 <b>2~3등급</b> 수준입니다.
     <br><br>
     <table style="font-size:12.5px; border-collapse:collapse; width:100%;">
       <tr style="background:#f9fafb;">
         <th style="padding:6px 10px; border:1px solid #e5e7eb; text-align:left;">등급</th>
         <th style="padding:6px 10px; border:1px solid #e5e7eb;">pH 기준</th>
         <th style="padding:6px 10px; border:1px solid #e5e7eb;">DO 기준 (mg/L)</th>
         <th style="padding:6px 10px; border:1px solid #e5e7eb;">용도</th>
       </tr>
       <tr>
         <td style="padding:6px 10px; border:1px solid #e5e7eb;"><span class="badge badge-blue">1등급 (매우 좋음)</span></td>
         <td style="padding:6px 10px; border:1px solid #e5e7eb; text-align:center;">6.5–8.5</td>
         <td style="padding:6px 10px; border:1px solid #e5e7eb; text-align:center;">≥ 7.5</td>
         <td style="padding:6px 10px; border:1px solid #e5e7eb;">상수원, 자연환경 보전</td>
       </tr>
       <tr style="background:#f9fafb;">
         <td style="padding:6px 10px; border:1px solid #e5e7eb;"><span class="badge badge-green">2등급 (좋음)</span></td>
         <td style="padding:6px 10px; border:1px solid #e5e7eb; text-align:center;">6.5–8.5</td>
         <td style="padding:6px 10px; border:1px solid #e5e7eb; text-align:center;">≥ 5.0</td>
         <td style="padding:6px 10px; border:1px solid #e5e7eb;">1급 수질 정수 처리</td>
       </tr>
       <tr>
         <td style="padding:6px 10px; border:1px solid #e5e7eb;"><span class="badge badge-orange">3등급 (보통)</span></td>
         <td style="padding:6px 10px; border:1px solid #e5e7eb; text-align:center;">6.5–8.5</td>
         <td style="padding:6px 10px; border:1px solid #e5e7eb; text-align:center;">≥ 5.0</td>
         <td style="padding:6px 10px; border:1px solid #e5e7eb;">농업용수, 수산용수</td>
       </tr>
       <tr style="background:#f9fafb;">
         <td style="padding:6px 10px; border:1px solid #e5e7eb;"><span class="badge badge-red">4등급 이하</span></td>
         <td style="padding:6px 10px; border:1px solid #e5e7eb; text-align:center;">6.0–8.5</td>
         <td style="padding:6px 10px; border:1px solid #e5e7eb; text-align:center;">≥ 2.0</td>
         <td style="padding:6px 10px; border:1px solid #e5e7eb;">공업용수, 처리 후 이용</td>
       </tr>
     </table>
     <br>
     겨울–봄(10월~4월): DO ≥ 7.5 → <b>1등급</b> 충족.<br>
     여름(5월 말~9월): DO가 5.0 mg/L 근방 또는 이하로 내려가는 구간 발생 → <b>2~4등급 경계</b>.
     연간 관리 목표는 여름철 DO 하락을 최소화하는 것이 핵심입니다."""),
]

for title, body in insights:
    with st.expander(title, expanded=False):
        st.markdown(f'<div class="insight-body">{body}</div>', unsafe_allow_html=True)


# ── 원시 데이터 ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-header">📋 원시 데이터</div>', unsafe_allow_html=True)
cols_show = ['date'] + [f'pH_{s}' for s in stations] + [f'DO_{s}' for s in stations]
display_df = dff[cols_show].copy()
display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
display_df.columns = ['날짜'] + [f'pH ({s})' for s in stations] + [f'DO ({s}) mg/L' for s in stations]
st.dataframe(display_df, use_container_width=True, height=280)

csv_bytes = display_df.to_csv(index=False).encode('utf-8-sig')
st.download_button("⬇️ CSV 다운로드", csv_bytes, file_name="hangang_water_quality_2020.csv", mime="text/csv")

st.markdown("""
<div style="text-align:center; font-size:12px; color:#9ca3af; margin-top:40px; padding-bottom:10px;">
    데이터 출처: 환경부 수질측정망 (2020) &nbsp;|&nbsp; 노량진·선유 측정소 시간별 측정값 일평균
</div>
""", unsafe_allow_html=True)
