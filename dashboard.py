"""ORB Bot — Trading Analytics Dashboard.

Live analytics della strategia ORB su CSV generato dal bot NinjaTrader.
Avvio: streamlit run dashboard.py  (oppure doppio click su run_dashboard.bat)
"""
from __future__ import annotations

import calendar as calmod
from datetime import date as dt_date
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from config import CSV_PATH, SHEET_PUBLIC_CSV_URL

# ============================================================================ #
# CONFIG
# ============================================================================ #

REFRESH_MS = 30_000  # 30s: su cloud/mobile meno aggressivo, risparmia rate limit

C_WIN = "#16C784"
C_LOSS = "#EA3943"
C_NEUTRAL = "#9AA0A6"
C_ACCENT = "#3D8BFD"
C_GOLD = "#F5B700"
C_BG = "#0B0E14"
C_BG_SOFT = "#151921"
C_GRID = "#1F2430"
C_TEXT = "#E8EAED"
C_MUTED = "#9AA0A6"

TRADING_DAYS_YEAR = 252

MONTHS_IT = [
    "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
    "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre",
]
DOW_IT = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]

PLOTLY_LAYOUT = dict(
    paper_bgcolor=C_BG_SOFT,
    plot_bgcolor=C_BG_SOFT,
    font=dict(color=C_TEXT, family="Inter, system-ui, sans-serif", size=12),
    margin=dict(l=16, r=16, t=40, b=16),
    xaxis=dict(gridcolor=C_GRID, zerolinecolor=C_GRID),
    yaxis=dict(gridcolor=C_GRID, zerolinecolor=C_GRID),
    hoverlabel=dict(bgcolor=C_BG, font_size=12, font_family="Inter"),
    colorway=[C_ACCENT, C_WIN, C_GOLD, C_LOSS, "#9B51E0", "#56CCF2"],
)


# ============================================================================ #
# PAGE
# ============================================================================ #

st.set_page_config(
    page_title="ORB Bot — Analytics",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="●",
)

st_autorefresh(interval=REFRESH_MS, key="auto_refresh")

st.markdown(
    "<style>"
    "@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600;700&display=swap');"
    "html,body,[class*='css']{font-family:'Inter',system-ui,sans-serif!important}"
    ".block-container{padding-top:1.2rem;padding-bottom:3rem;max-width:1620px}"
    "h1,h2,h3{letter-spacing:-0.01em;font-weight:600}"
    "[data-testid='stMetric']{background:#151921;border:1px solid #222836;padding:14px 16px;border-radius:10px}"
    "[data-testid='stMetricLabel']{color:#9AA0A6!important;font-size:0.7rem!important;text-transform:uppercase;letter-spacing:0.08em;font-weight:500}"
    "[data-testid='stMetricValue']{font-size:1.5rem!important;font-weight:600!important;font-family:'JetBrains Mono',monospace!important}"
    "[data-testid='stMetricDelta']{font-size:0.75rem!important}"
    ".stTabs [data-baseweb='tab-list']{gap:2px;border-bottom:1px solid #222836}"
    ".stTabs [data-baseweb='tab']{background:transparent;padding:10px 20px;color:#9AA0A6;font-weight:500;font-size:0.92rem}"
    ".stTabs [aria-selected='true']{background:#161B26!important;color:#E8EAED!important;border-bottom:2px solid #3D8BFD!important}"
    ".hero{background:radial-gradient(ellipse at top,#1A2030 0%,#0F131B 70%);border:1px solid #222836;border-radius:16px;padding:28px 24px;text-align:center;margin:16px 0 22px 0;position:relative;overflow:hidden}"
    ".hero::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,#3D8BFD,transparent)}"
    ".hero-label{font-size:0.72rem;text-transform:uppercase;letter-spacing:0.18em;color:#9AA0A6;font-weight:500}"
    ".hero-value{font-size:3.2rem;font-weight:700;font-family:'JetBrains Mono',monospace;margin:8px 0 10px 0;line-height:1;text-shadow:0 2px 20px rgba(0,0,0,0.5)}"
    ".hero-sub{font-size:0.95rem;color:#B8BCC4;letter-spacing:0.02em}"
    ".hero-sub .chip{display:inline-block;padding:3px 10px;background:#161B26;border:1px solid #222836;border-radius:14px;margin:0 3px;font-family:'JetBrains Mono',monospace;font-size:0.85rem}"
    ".live-badge{display:inline-flex;align-items:center;gap:7px;background:rgba(22,199,132,0.1);border:1px solid rgba(22,199,132,0.3);padding:3px 10px;border-radius:20px;font-size:0.72rem;color:#16C784;font-weight:500;letter-spacing:0.06em}"
    ".live-dot{width:7px;height:7px;background:#16C784;border-radius:50%;animation:pulse 1.6s ease-in-out infinite}"
    "@keyframes pulse{50%{opacity:0.3;transform:scale(0.85)}}"
    ".sub{color:#9AA0A6;font-size:0.84rem}"
    ".card{background:#151921;border:1px solid #222836;border-radius:12px;padding:16px 18px}"
    ".stat-row{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.04);font-size:0.9rem}"
    ".stat-row:last-child{border-bottom:none}"
    ".stat-label{color:#9AA0A6}"
    ".stat-val{font-family:'JetBrains Mono',monospace;font-weight:600}"
    ".last-trade-card{background:#151921;border:1px solid #222836;border-radius:12px;padding:12px 16px;text-align:right}"
    "[data-testid='stSegmentedControl'] div[role='group'],[data-testid='stSegmentedControl'] div[role='radiogroup']{flex-wrap:nowrap!important}"
    "[data-testid='stSegmentedControl'] button{white-space:nowrap!important}"
    ".last-trade-label{font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;color:#9AA0A6;font-weight:500}"
    ".last-trade-val{font-size:1rem;font-weight:600;margin-top:4px;font-family:'JetBrains Mono',monospace}"
    ".month-header{text-align:center;margin:28px 0 14px 0}"
    ".month-title{font-size:1.25rem;font-weight:700;color:#E8EAED;letter-spacing:0.02em}"
    ".month-stats{margin-top:6px;font-size:0.88rem;color:#9AA0A6;font-family:'JetBrains Mono',monospace}"
    ".cal-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:8px;margin-bottom:8px}"
    ".cal-head{text-align:center;font-size:0.7rem;color:#6B7280;text-transform:uppercase;letter-spacing:0.12em;padding:8px 0;font-weight:600}"
    ".cal-cell{min-height:100px;padding:10px 12px;border-radius:12px;border:1px solid #1F2430;background:#0F131B;display:grid;grid-template-rows:auto 1fr auto;transition:transform 0.15s ease,box-shadow 0.15s ease;position:relative}"
    ".cal-cell.empty{border:1px dashed #1A1F2B;background:transparent;opacity:0.25}"
    ".cal-cell.filled:hover{transform:translateY(-2px);box-shadow:0 8px 20px rgba(0,0,0,0.4)}"
    ".cal-cell.weekend{opacity:0.55}"
    ".day-num{font-size:0.75rem;color:#6B7280;font-weight:600;letter-spacing:0.02em}"
    ".day-num.today{color:#3D8BFD;font-weight:700}"
    ".day-pnl{font-size:1.15rem;font-weight:700;font-family:'JetBrains Mono',monospace;text-align:center;align-self:center;line-height:1.1}"
    ".day-meta{font-size:0.62rem;color:#9AA0A6;text-align:right;text-transform:uppercase;letter-spacing:0.08em}"
    ".cal-legend{display:flex;gap:14px;align-items:center;justify-content:center;font-size:0.72rem;color:#9AA0A6;margin:12px 0}"
    ".legend-sw{width:14px;height:14px;border-radius:3px;display:inline-block;margin-right:5px;vertical-align:middle}"
    # ---------------- MOBILE (<=768px) ----------------
    "@media (max-width:768px){"
    ".block-container{padding:0.6rem 0.6rem 2rem 0.6rem!important}"
    "h1{font-size:1.35rem!important}"
    "h1 span{font-size:0.95rem!important;display:block;margin-top:2px}"
    ".hero{padding:18px 14px!important;margin:10px 0 16px 0!important;border-radius:12px!important}"
    ".hero-value{font-size:2.2rem!important}"
    ".hero-label{font-size:0.65rem!important}"
    ".hero-sub{font-size:0.8rem!important}"
    ".hero-sub .chip{font-size:0.72rem!important;padding:2px 7px!important;margin:2px!important;display:inline-block}"
    "[data-testid='stMetric']{padding:10px 12px!important}"
    "[data-testid='stMetricValue']{font-size:1.15rem!important}"
    "[data-testid='stMetricLabel']{font-size:0.62rem!important}"
    ".stTabs [data-baseweb='tab-list']{overflow-x:auto!important;flex-wrap:nowrap!important;scrollbar-width:thin}"
    ".stTabs [data-baseweb='tab']{padding:8px 12px!important;font-size:0.82rem!important;white-space:nowrap}"
    ".cal-grid{gap:3px!important}"
    ".cal-cell{min-height:62px!important;padding:4px 5px!important;border-radius:7px!important}"
    ".cal-head{font-size:0.58rem!important;padding:4px 0!important;letter-spacing:0.06em!important}"
    ".day-num{font-size:0.62rem!important}"
    ".day-pnl{font-size:0.72rem!important}"
    ".day-meta{display:none!important}"
    ".stat-row{font-size:0.82rem!important;padding:6px 0!important}"
    ".last-trade-card{text-align:left!important;margin-top:6px}"
    ".card{padding:12px 14px!important}"
    ".month-title{font-size:1.05rem!important}"
    ".month-stats{font-size:0.78rem!important}"
    "}"
    "</style>",
    unsafe_allow_html=True,
)


# ============================================================================ #
# DATA
# ============================================================================ #


@st.cache_data(ttl=30, show_spinner=False)
def _fetch_raw() -> tuple[pd.DataFrame, str]:
    """Prova prima il Google Sheet pubblico, poi fallback al CSV locale.

    Ritorna (df, source_label). Cachato 30s per ridurre round-trip di rete.
    """
    # 1) Google Sheet pubblico (formato CSV via gviz)
    try:
        df = pd.read_csv(SHEET_PUBLIC_CSV_URL)
        if not df.empty:
            return df, "Google Sheet"
    except Exception:
        pass
    # 2) Fallback CSV locale (utile per dev offline)
    if CSV_PATH.exists():
        try:
            df = pd.read_csv(CSV_PATH)
            if not df.empty:
                return df, "CSV locale"
        except Exception:
            pass
    return pd.DataFrame(), "nessuna sorgente"


def load_trades() -> tuple[pd.DataFrame, str]:
    df, source = _fetch_raw()
    if df.empty:
        return df, source
    df["entry_dt"] = pd.to_datetime(df["entry_time"], errors="coerce")
    df["exit_dt"] = pd.to_datetime(df["exit_time"], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    df["is_win"] = df["pnl_usd"] > 0
    df["entry_hour_str"] = df["entry_dt"].dt.strftime("%H:%M")
    df["exit_hour_str"] = df["exit_dt"].dt.strftime("%H:%M")
    df["entry_hour"] = df["entry_dt"].dt.hour
    df["dow"] = df["entry_dt"].dt.dayofweek
    df["time_in_trade_min"] = (df["exit_dt"] - df["entry_dt"]).dt.total_seconds() / 60
    df["is_boost"] = df["r_target"] >= 1.0
    df["boost_label"] = df["is_boost"].map({True: "Boost 1.5R", False: "Normale 0.5R"})
    df["year_month"] = df["entry_dt"].dt.to_period("M")
    if "strategy_label" not in df.columns:
        df["strategy_label"] = "—"
    else:
        df["strategy_label"] = df["strategy_label"].fillna("—").astype(str)
    return df.sort_values("entry_dt").reset_index(drop=True), source


# ============================================================================ #
# METRICS
# ============================================================================ #


def compute_metrics(df: pd.DataFrame) -> dict:
    if df.empty:
        return {}

    n = len(df)
    wins = int(df["is_win"].sum())
    losses = n - wins
    wr = wins / n
    pnl_total = df["pnl_usd"].sum()

    gross_win = df.loc[df["is_win"], "pnl_usd"].sum()
    gross_loss = df.loc[~df["is_win"], "pnl_usd"].sum()
    avg_win = df.loc[df["is_win"], "pnl_usd"].mean() if wins else 0
    avg_loss = df.loc[~df["is_win"], "pnl_usd"].mean() if losses else 0

    payoff = (avg_win / abs(avg_loss)) if avg_loss < 0 else np.inf
    pf = (gross_win / abs(gross_loss)) if gross_loss < 0 else np.inf
    exp_usd = df["pnl_usd"].mean()
    exp_r = df["r_effective"].mean()

    equity = df["pnl_usd"].cumsum().values
    running_max = np.maximum.accumulate(equity)
    drawdown = equity - running_max
    max_dd = drawdown.min() if len(drawdown) else 0
    max_dd_pct = (max_dd / running_max.max()) * 100 if running_max.max() > 0 else 0
    recovery = (pnl_total / abs(max_dd)) if max_dd < 0 else np.inf

    daily = df.groupby("date")["pnl_usd"].sum()
    if len(daily) >= 2 and daily.std() > 0:
        sharpe = daily.mean() / daily.std() * np.sqrt(TRADING_DAYS_YEAR)
    else:
        sharpe = 0.0
    neg_daily = daily[daily < 0]
    if len(neg_daily) >= 2 and neg_daily.std() > 0:
        sortino = daily.mean() / neg_daily.std() * np.sqrt(TRADING_DAYS_YEAR)
    else:
        sortino = 0.0

    avg_win_r = df.loc[df["is_win"], "r_effective"].mean() if wins else 0
    avg_loss_r = df.loc[~df["is_win"], "r_effective"].mean() if losses else 0
    if avg_win_r > 0:
        kelly = (wr * avg_win_r - (1 - wr) * abs(avg_loss_r)) / avg_win_r
    else:
        kelly = 0.0

    dd_series = pd.Series(drawdown)
    in_dd = dd_series < 0
    dd_durations = []
    cur_dur = 0
    for v in in_dd:
        if v:
            cur_dur += 1
        elif cur_dur > 0:
            dd_durations.append(cur_dur)
            cur_dur = 0
    if cur_dur > 0:
        dd_durations.append(cur_dur)
    max_dd_duration = max(dd_durations, default=0)

    return dict(
        n=n, wins=wins, losses=losses, wr=wr,
        pnl_total=pnl_total, exp_usd=exp_usd, exp_r=exp_r,
        avg_win=avg_win, avg_loss=avg_loss,
        gross_win=gross_win, gross_loss=gross_loss,
        payoff=payoff, pf=pf,
        equity=equity, running_max=running_max, drawdown=drawdown,
        max_dd=max_dd, max_dd_pct=max_dd_pct,
        max_dd_duration=max_dd_duration,
        recovery=recovery, sharpe=sharpe, sortino=sortino, kelly=kelly,
        daily_pnl=daily,
        best_day=daily.max() if len(daily) else 0,
        worst_day=daily.min() if len(daily) else 0,
        best_trade=df["pnl_usd"].max(),
        worst_trade=df["pnl_usd"].min(),
        avg_time_in_trade=df["time_in_trade_min"].mean(),
    )


def short_strategy_label(label: str) -> str:
    """Es. 'SL0.6_RR2.5_SkipMon_BoostTueFri_R0.5-1.5' -> '0.6 RR2.5'."""
    if not label or label == "—":
        return label or "—"
    parts = label.split("_")
    sl_val = rr_val = None
    for p in parts:
        up = p.upper()
        if up.startswith("SL") and len(p) > 2:
            sl_val = p[2:]
        elif up.startswith("RR") and len(p) > 2:
            rr_val = p[2:]
    if sl_val and rr_val:
        return f"{sl_val} RR{rr_val}"
    if sl_val:
        return sl_val
    if rr_val:
        return f"RR{rr_val}"
    return " ".join(parts[:2]) if len(parts) >= 2 else label


def describe_strategy(label: str) -> str:
    if not label or label == "—":
        return "_Strategia non indicata nel CSV._"
    day_map = {
        "Mon": "lunedì", "Tue": "martedì", "Wed": "mercoledì",
        "Thu": "giovedì", "Fri": "venerdì", "Sat": "sabato", "Sun": "domenica",
    }

    def expand_days(tail: str) -> str:
        names = []
        i = 0
        while i < len(tail):
            chunk = tail[i:i + 3]
            names.append(day_map.get(chunk, chunk))
            i += 3
        return ", ".join(names) if names else "—"

    lines = []
    for p in label.split("_"):
        up = p.upper()
        if up.startswith("SL") and len(p) > 2:
            lines.append(f"- **SL {p[2:]}** — Stop Loss: {p[2:]} × OR size")
        elif up.startswith("RR") and len(p) > 2:
            lines.append(f"- **RR {p[2:]}** — Risk/Reward target 1:{p[2:]}")
        elif up.startswith("SKIP"):
            tail = p[4:]
            lines.append(f"- **Skip {expand_days(tail)}** — nessun trade in quel/quei giorni")
        elif up.startswith("BOOST"):
            tail = p[5:]
            lines.append(f"- **Boost {expand_days(tail)}** — R-target aumentato in quei giorni")
        elif up.startswith("R") and "-" in p and len(p) > 1:
            vals = p[1:].split("-")
            if len(vals) == 2:
                lines.append(f"- **R {vals[0]}–{vals[1]}** — R-target normale {vals[0]}R · boost {vals[1]}R")
            else:
                lines.append(f"- `{p}`")
        else:
            lines.append(f"- `{p}`")
    return "\n".join(lines)


def fmt_usd(v: float, sign: bool = False) -> str:
    if pd.isna(v) or v == np.inf or v == -np.inf:
        return "∞" if v == np.inf else "—"
    s = f"{v:+,.0f}" if sign else f"{v:,.0f}"
    return f"${s}"


def fmt_num(v: float, decimals: int = 2, suffix: str = "") -> str:
    if pd.isna(v) or v == np.inf:
        return "∞"
    return f"{v:.{decimals}f}{suffix}"


# ============================================================================ #
# CALENDAR
# ============================================================================ #


def render_month_calendar(df: pd.DataFrame, year: int, month: int) -> str:
    cal = calmod.Calendar(firstweekday=0)
    weeks = cal.monthdayscalendar(year, month)

    mask = df["entry_dt"].dt.year.eq(year) & df["entry_dt"].dt.month.eq(month)
    mdf = df[mask]
    daily_pnl = mdf.groupby("date")["pnl_usd"].sum().to_dict()
    daily_tr = mdf.groupby("date").size().to_dict()

    m_total = sum(daily_pnl.values()) if daily_pnl else 0
    m_trades = sum(daily_tr.values()) if daily_tr else 0
    m_wins = int(mdf["is_win"].sum())
    m_wr = (m_wins / m_trades * 100) if m_trades else 0

    max_abs = max((abs(p) for p in daily_pnl.values()), default=1) or 1
    today = dt_date.today()

    head_color = C_WIN if m_total >= 0 else C_LOSS
    sign = "+" if m_total >= 0 else ""

    html = (
        f'<div class="month-header">'
        f'<div class="month-title">{MONTHS_IT[month-1]} {year}</div>'
        f'<div class="month-stats">{m_trades} trade · WR {m_wr:.0f}% · '
        f'<span style="color:{head_color};font-weight:700">{sign}${m_total:,.0f}</span></div>'
        f'</div>'
        f'<div class="cal-grid">'
    )
    for d in DOW_IT:
        html += f'<div class="cal-head">{d}</div>'

    for week in weeks:
        for day in week:
            if day == 0:
                html += '<div class="cal-cell empty"></div>'
                continue
            cdate = dt_date(year, month, day)
            dow_idx = cdate.weekday()
            weekend_cls = " weekend" if dow_idx >= 5 else ""
            today_cls = " today" if cdate == today else ""

            if cdate in daily_pnl:
                pnl = daily_pnl[cdate]
                tr = daily_tr[cdate]
                intensity = min(abs(pnl) / max_abs, 1.0)
                if pnl >= 0:
                    bg = f"rgba(22,199,132,{0.12 + 0.42*intensity})"
                    col = "#3FE0A0"
                    bd = f"rgba(22,199,132,{0.35 + 0.3*intensity})"
                else:
                    bg = f"rgba(234,57,67,{0.12 + 0.42*intensity})"
                    col = "#FF6B75"
                    bd = f"rgba(234,57,67,{0.35 + 0.3*intensity})"
                pnl_sign = "+" if pnl >= 0 else ""
                html += (
                    f'<div class="cal-cell filled{weekend_cls}" '
                    f'style="background:{bg};border-color:{bd}">'
                    f'<div class="day-num{today_cls}">{day}</div>'
                    f'<div class="day-pnl" style="color:{col}">{pnl_sign}${pnl:,.0f}</div>'
                    f'<div class="day-meta">{tr} trade</div>'
                    f'</div>'
                )
            else:
                html += (
                    f'<div class="cal-cell{weekend_cls}">'
                    f'<div class="day-num{today_cls}">{day}</div>'
                    f'</div>'
                )
    html += "</div>"
    return html


# ============================================================================ #
# LOAD
# ============================================================================ #

df_all, data_source = load_trades()

# ============================================================================ #
# HEADER
# ============================================================================ #

header_l, header_r = st.columns([3, 1])
with header_l:
    st.markdown(
        "<h1 style='margin:0'>Opening Range Breakout "
        "<span style='color:#9AA0A6;font-weight:400;font-size:1.3rem'>Dashboard</span></h1>"
        "<div style='margin-top:8px;display:flex;gap:10px;align-items:center;flex-wrap:wrap'>"
        "<span class='live-badge'><span class='live-dot'></span>LIVE · 30s</span>"
        f"<span class='sub'>Sorgente: <code style='background:#12161F;padding:2px 6px;border-radius:4px'>{data_source}</code></span>"
        "</div>",
        unsafe_allow_html=True,
    )
with header_r:
    if not df_all.empty:
        lt = df_all.iloc[-1]
        c = C_WIN if lt["pnl_usd"] > 0 else C_LOSS
        st.markdown(
            f"<div class='last-trade-card'>"
            f"<div class='last-trade-label'>Ultimo trade</div>"
            f"<div class='last-trade-val'>{lt['date']} · {lt['entry_hour_str']} · "
            f"<span style='color:{c}'>{fmt_usd(lt['pnl_usd'], sign=True)}</span></div>"
            f"</div>",
            unsafe_allow_html=True,
        )

if df_all.empty:
    st.warning(
        f"Nessun trade disponibile (sorgente: {data_source}). "
        "Controlla che il bot abbia chiuso almeno un trade e che il sync verso Google Sheets sia andato."
    )
    st.stop()

# ============================================================================ #
# SIDEBAR FILTERS
# ============================================================================ #

with st.sidebar:
    st.markdown("### Filtri")

    with st.expander("Periodo", expanded=True):
        period = st.segmented_control(
            "Preset",
            options=["Tutto", "90g", "30g", "7g"],
            default="Tutto",
        )
        min_d, max_d = df_all["date"].min(), df_all["date"].max()
        date_range = st.date_input(
            "Range personalizzato",
            (min_d, max_d),
            min_value=min_d,
            max_value=max_d,
        )

    with st.expander("Strategia", expanded=True):
        strategy_options = sorted(df_all["strategy_label"].dropna().unique().tolist())
        strategy_filter = st.multiselect(
            "Strategia applicata",
            options=strategy_options,
            default=strategy_options,
            format_func=short_strategy_label,
            help="Filtra per la configurazione di strategia con cui sono stati eseguiti i trade.",
        )
        direction_filter = st.multiselect(
            "Direction",
            options=["long", "short"],
            default=["long", "short"],
        )
        exit_options = sorted(df_all["exit_type"].dropna().unique().tolist())
        exit_filter = st.multiselect("Exit type", options=exit_options, default=exit_options)

    with st.popover("Cosa significano le strategie?", use_container_width=True):
        st.markdown("### Dettaglio strategie")
        st.caption("Parsing automatico dei token della `strategy_label`.")
        for full in strategy_options:
            st.markdown(f"**{short_strategy_label(full)}**")
            st.caption(f"`{full}`")
            st.markdown(describe_strategy(full))
            st.markdown("")
        boost_mode = st.radio(
            "Tipo R-target",
            ["Tutti", "Solo boost 1.5R", "Solo normali 0.5R"],
            horizontal=False,
        )
        instruments = sorted(df_all["instrument"].dropna().unique().tolist())
        instr_filter = st.multiselect("Strumento", options=instruments, default=instruments)

    with st.expander("Avanzate"):
        hours_available = sorted(df_all["entry_hour_str"].dropna().unique().tolist())
        hour_filter = st.multiselect(
            "Orari entry",
            options=hours_available,
            default=hours_available,
        )
        available_dow = sorted(df_all["dow"].dropna().unique().tolist())
        dow_selected = st.multiselect(
            "Giorno settimana",
            options=available_dow,
            default=available_dow,
            format_func=lambda i: DOW_IT[int(i)],
        )

    st.markdown("---")
    st.markdown(
        f"<div class='sub'>Storico totale: <b>{len(df_all)}</b> trade<br/>"
        f"Dal <b>{min_d}</b> al <b>{max_d}</b></div>",
        unsafe_allow_html=True,
    )

# apply filters
today_ts = pd.Timestamp(df_all["date"].max())
if period == "7g":
    mask_date = df_all["date"] >= (today_ts - pd.Timedelta(days=7)).date()
elif period == "30g":
    mask_date = df_all["date"] >= (today_ts - pd.Timedelta(days=30)).date()
elif period == "90g":
    mask_date = df_all["date"] >= (today_ts - pd.Timedelta(days=90)).date()
else:
    if isinstance(date_range, tuple) and len(date_range) == 2:
        mask_date = (df_all["date"] >= date_range[0]) & (df_all["date"] <= date_range[1])
    else:
        mask_date = pd.Series(True, index=df_all.index)

mask = (
    mask_date
    & df_all["strategy_label"].isin(strategy_filter)
    & df_all["direction"].isin(direction_filter)
    & df_all["exit_type"].isin(exit_filter)
    & df_all["instrument"].isin(instr_filter)
    & df_all["entry_hour_str"].isin(hour_filter)
    & df_all["dow"].isin(dow_selected)
)
if boost_mode == "Solo boost 1.5R":
    mask &= df_all["is_boost"]
elif boost_mode == "Solo normali 0.5R":
    mask &= ~df_all["is_boost"]

df = df_all[mask].sort_values("entry_dt").reset_index(drop=True)

if df.empty:
    st.warning("Nessun trade con i filtri selezionati. Allenta i filtri dalla sidebar.")
    st.stop()

df["equity"] = df["pnl_usd"].cumsum()
df["running_max"] = df["equity"].cummax()
df["drawdown"] = df["equity"] - df["running_max"]
df["trade_num"] = range(1, len(df) + 1)
df["rolling_wr_20"] = df["is_win"].rolling(window=20, min_periods=3).mean() * 100
df["rolling_expR_20"] = df["r_effective"].rolling(window=20, min_periods=3).mean()

M = compute_metrics(df)

# ============================================================================ #
# HERO PnL
# ============================================================================ #

pnl_color = C_WIN if M["pnl_total"] >= 0 else C_LOSS
sign = "+" if M["pnl_total"] >= 0 else ""
st.markdown(
    f"<div class='hero'>"
    f"<div class='hero-label'>PnL Totale</div>"
    f"<div class='hero-value' style='color:{pnl_color}'>{sign}${M['pnl_total']:,.0f}</div>"
    f"<div class='hero-sub'>"
    f"<span class='chip'>{M['n']} trade</span>"
    f"<span class='chip'>WR {M['wr']*100:.1f}%</span>"
    f"<span class='chip'>Exp {M['exp_r']:+.2f}R</span>"
    f"<span class='chip'>PF {fmt_num(M['pf'],2)}</span>"
    f"<span class='chip' style='color:{C_LOSS}'>DD {fmt_usd(M['max_dd'])}</span>"
    f"</div></div>",
    unsafe_allow_html=True,
)

# ============================================================================ #
# TABS
# ============================================================================ #

tab_overview, tab_calendar, tab_perf, tab_strat, tab_eod, tab_trades = st.tabs(
    ["Overview", "Calendar", "Performance", "Strategy", "EOD", "Trade Log"]
)

# ============================================================================ #
# TAB: OVERVIEW
# ============================================================================ #
with tab_overview:
    c_eq, c_stats = st.columns([2.4, 1])

    with c_eq:
        st.markdown("#### Equity Curve")
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df["trade_num"], y=df["equity"], mode="lines", name="Equity",
                line=dict(color=C_WIN, width=2.5, shape="spline", smoothing=0.6),
                fill="tozeroy", fillcolor="rgba(22,199,132,0.09)",
                hovertemplate="<b>Trade #%{x}</b><br>Equity: $%{y:,.0f}<extra></extra>",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=df["trade_num"], y=df["running_max"], mode="lines", name="Peak",
                line=dict(color=C_NEUTRAL, dash="dot", width=1), hoverinfo="skip",
            )
        )
        fig.update_layout(**PLOTLY_LAYOUT, height=400, showlegend=True)
        fig.update_xaxes(title="Trade #")
        fig.update_yaxes(title="PnL cumulato $")
        st.plotly_chart(fig, width="stretch")

    with c_stats:
        st.markdown("#### Statistiche")
        stats_rows = [
            ("Expectancy $", fmt_usd(M["exp_usd"], sign=True), C_TEXT),
            ("Avg Win", fmt_usd(M["avg_win"], sign=True), C_WIN),
            ("Avg Loss", fmt_usd(M["avg_loss"], sign=True), C_LOSS),
            ("Payoff ratio", fmt_num(M["payoff"], 2), C_TEXT),
            ("Sharpe", fmt_num(M["sharpe"], 2), C_TEXT),
            ("Sortino", fmt_num(M["sortino"], 2), C_TEXT),
            ("Kelly %", f"{M['kelly']*100:.1f}%", C_TEXT),
            ("Recovery Factor", fmt_num(M["recovery"], 2), C_TEXT),
            ("Max DD $", fmt_usd(M["max_dd"]), C_LOSS),
            ("Max DD duration", f"{M['max_dd_duration']} trade", C_TEXT),
            ("Best trade", fmt_usd(M["best_trade"], sign=True), C_WIN),
            ("Worst trade", fmt_usd(M["worst_trade"], sign=True), C_LOSS),
            ("Best day", fmt_usd(M["best_day"], sign=True), C_WIN),
            ("Worst day", fmt_usd(M["worst_day"], sign=True), C_LOSS),
            ("Avg time in trade", fmt_num(M["avg_time_in_trade"], 0, " min"), C_TEXT),
        ]
        rows_html = "".join(
            f"<div class='stat-row'><span class='stat-label'>{lbl}</span>"
            f"<span class='stat-val' style='color:{col}'>{val}</span></div>"
            for lbl, val, col in stats_rows
        )
        st.markdown(f"<div class='card'>{rows_html}</div>", unsafe_allow_html=True)


# ============================================================================ #
# TAB: CALENDAR
# ============================================================================ #
with tab_calendar:
    months_avail = sorted(df["year_month"].unique(), reverse=True)
    month_labels = [f"{MONTHS_IT[p.month-1]} {p.year}" for p in months_avail]
    label_to_period = dict(zip(month_labels, months_avail))

    c1, c2 = st.columns([1, 3])
    with c1:
        view_mode = st.radio("Vista", ["Mese singolo", "Tutti i mesi"], horizontal=False)
    with c2:
        if view_mode == "Mese singolo" and month_labels:
            selected_label = st.selectbox("Seleziona mese", month_labels, index=0)
            selected_periods = [label_to_period[selected_label]]
        else:
            selected_periods = months_avail

    st.markdown(
        "<div class='cal-legend'>"
        "<span><span class='legend-sw' style='background:rgba(234,57,67,0.55)'></span>Loss</span>"
        "<span><span class='legend-sw' style='background:#0F131B;border:1px solid #1F2430'></span>No trade</span>"
        "<span><span class='legend-sw' style='background:rgba(22,199,132,0.55)'></span>Win</span>"
        "</div>",
        unsafe_allow_html=True,
    )

    for period_p in selected_periods:
        html = render_month_calendar(df, period_p.year, period_p.month)
        st.markdown(html, unsafe_allow_html=True)


# ============================================================================ #
# TAB: PERFORMANCE
# ============================================================================ #
with tab_perf:
    st.markdown("#### Rolling metrics — finestra 20 trade")
    c_rwr, c_rexp = st.columns(2)
    with c_rwr:
        fig_rwr = go.Figure()
        fig_rwr.add_trace(
            go.Scatter(x=df["trade_num"], y=df["rolling_wr_20"],
                       line=dict(color=C_ACCENT, width=2.5, shape="spline"),
                       mode="lines", name="Rolling WR")
        )
        fig_rwr.add_hline(y=M["wr"] * 100, line_dash="dash", line_color=C_WIN,
                          annotation_text=f"WR medio {M['wr']*100:.1f}%",
                          annotation_font_color=C_WIN)
        fig_rwr.add_hline(y=50, line_dash="dot", line_color=C_NEUTRAL)
        fig_rwr.update_layout(**PLOTLY_LAYOUT, height=300, showlegend=False,
                              title=dict(text="Win Rate", x=0.01))
        fig_rwr.update_xaxes(title="Trade #")
        fig_rwr.update_yaxes(title="WR %")
        st.plotly_chart(fig_rwr, width="stretch")
    with c_rexp:
        fig_rexp = go.Figure()
        fig_rexp.add_trace(
            go.Scatter(x=df["trade_num"], y=df["rolling_expR_20"],
                       line=dict(color=C_GOLD, width=2.5, shape="spline"),
                       fill="tozeroy", fillcolor="rgba(245,183,0,0.1)",
                       mode="lines", name="Rolling Exp R")
        )
        fig_rexp.add_hline(y=M["exp_r"], line_dash="dash", line_color=C_ACCENT,
                           annotation_text=f"Exp R medio {M['exp_r']:+.2f}",
                           annotation_font_color=C_ACCENT)
        fig_rexp.add_hline(y=0, line_dash="dot", line_color=C_NEUTRAL)
        fig_rexp.update_layout(**PLOTLY_LAYOUT, height=300, showlegend=False,
                               title=dict(text="Expectancy R", x=0.01))
        fig_rexp.update_xaxes(title="Trade #")
        fig_rexp.update_yaxes(title="Exp R")
        st.plotly_chart(fig_rexp, width="stretch")

    st.markdown("#### Breakdown temporale")
    c_dow, c_hour = st.columns(2)
    with c_dow:
        dow_agg = df.groupby("dow").agg(
            trades=("is_win", "count"),
            wr=("is_win", lambda x: x.mean() * 100),
            pnl=("pnl_usd", "sum"),
        ).reset_index()
        dow_agg["dow_name"] = dow_agg["dow"].apply(lambda i: DOW_IT[int(i)])
        fig_dow = go.Figure(
            go.Bar(
                x=dow_agg["dow_name"], y=dow_agg["pnl"],
                marker_color=[C_WIN if v >= 0 else C_LOSS for v in dow_agg["pnl"]],
                marker_line_width=0,
                text=[f"{r['trades']} trade · WR {r['wr']:.0f}%" for _, r in dow_agg.iterrows()],
                textposition="outside", textfont=dict(color=C_MUTED, size=11),
                hovertemplate="<b>%{x}</b><br>PnL: $%{y:,.0f}<br>%{text}<extra></extra>",
            )
        )
        fig_dow.update_layout(**PLOTLY_LAYOUT, height=340,
                              title=dict(text="PnL per giorno settimana", x=0.01))
        fig_dow.update_yaxes(title="PnL $")
        st.plotly_chart(fig_dow, width="stretch")

    with c_hour:
        hour_agg = df.groupby("entry_hour_str").agg(
            trades=("is_win", "count"),
            wr=("is_win", lambda x: x.mean() * 100),
            pnl=("pnl_usd", "sum"),
        ).reset_index().sort_values("entry_hour_str")
        fig_hour = go.Figure(
            go.Bar(
                x=hour_agg["entry_hour_str"], y=hour_agg["pnl"],
                marker=dict(
                    color=hour_agg["wr"],
                    colorscale=[[0, C_LOSS], [0.5, C_BG_SOFT], [1, C_WIN]],
                    cmid=50, cmin=0, cmax=100,
                    colorbar=dict(title="WR%", thickness=10, len=0.7),
                ),
                text=[f"n={t}" for t in hour_agg["trades"]],
                textposition="outside", textfont=dict(color=C_MUTED, size=11),
                hovertemplate="<b>%{x}</b><br>PnL: $%{y:,.0f}<br>WR: %{marker.color:.0f}%<br>%{text}<extra></extra>",
            )
        )
        fig_hour.update_layout(**PLOTLY_LAYOUT, height=340,
                               title=dict(text="PnL per orario entry", x=0.01))
        fig_hour.update_yaxes(title="PnL $")
        st.plotly_chart(fig_hour, width="stretch")


# ============================================================================ #
# TAB: STRATEGY
# ============================================================================ #
with tab_strat:
    def agg_table(group_col: str) -> pd.DataFrame:
        return df.groupby(group_col).agg(
            trades=("is_win", "count"),
            wins=("is_win", "sum"),
            wr=("is_win", lambda x: x.mean() * 100),
            exp_r=("r_effective", "mean"),
            pnl=("pnl_usd", "sum"),
            avg_pnl=("pnl_usd", "mean"),
        ).round(2)

    strat_fmt = {
        "wr": "{:.1f}%",
        "exp_r": "{:+.3f}",
        "pnl": "${:+,.0f}",
        "avg_pnl": "${:+,.2f}",
    }
    c_dir, c_boost = st.columns(2)
    with c_dir:
        st.markdown("#### Per Direction")
        st.dataframe(agg_table("direction").style.format(strat_fmt), width="stretch")
    with c_boost:
        st.markdown("#### Per R-target")
        st.dataframe(agg_table("boost_label").style.format(strat_fmt), width="stretch")

    st.markdown("#### Tempo in trade")
    c_h, c_s = st.columns(2)
    with c_h:
        fig_tit = go.Figure()
        fig_tit.add_trace(
            go.Histogram(x=df.loc[df["is_win"], "time_in_trade_min"], name="Win",
                         marker_color=C_WIN, nbinsx=25, opacity=0.75, marker_line_width=0)
        )
        fig_tit.add_trace(
            go.Histogram(x=df.loc[~df["is_win"], "time_in_trade_min"], name="Loss",
                         marker_color=C_LOSS, nbinsx=25, opacity=0.75, marker_line_width=0)
        )
        fig_tit.update_layout(**PLOTLY_LAYOUT, height=300, barmode="overlay")
        fig_tit.update_xaxes(title="Minuti in trade")
        fig_tit.update_yaxes(title="Trade")
        st.plotly_chart(fig_tit, width="stretch")
    with c_s:
        fig_ts = go.Figure()
        fig_ts.add_trace(
            go.Scatter(
                x=df["time_in_trade_min"], y=df["r_effective"], mode="markers",
                marker=dict(
                    size=11,
                    color=df["is_win"].map({True: C_WIN, False: C_LOSS}),
                    line=dict(color=C_BG, width=1), opacity=0.85,
                ),
                hovertemplate="Tempo: %{x:.0f} min<br>R: %{y:+.2f}<extra></extra>",
            )
        )
        fig_ts.add_hline(y=0, line_dash="dot", line_color=C_NEUTRAL)
        fig_ts.update_layout(**PLOTLY_LAYOUT, height=300, showlegend=False)
        fig_ts.update_xaxes(title="Minuti in trade")
        fig_ts.update_yaxes(title="R effettivo")
        st.plotly_chart(fig_ts, width="stretch")


# ============================================================================ #
# TAB: EOD
# ============================================================================ #
with tab_eod:
    eod_df = df[df["exit_type"] == "EOD"]
    tp_df = df[df["exit_type"] == "TP"]
    sl_df = df[df["exit_type"] == "SL"]

    n_eod = len(eod_df)
    if n_eod == 0:
        st.info("Nessun trade chiuso in EOD tra i filtri selezionati. Gli EOD sono "
                "trade dove il bot ha chiuso a fine sessione senza aver toccato TP o SL.")
    else:
        eod_wins = int(eod_df["is_win"].sum())
        eod_wr = eod_wins / n_eod * 100
        eod_pnl = eod_df["pnl_usd"].sum()
        eod_exp_r = eod_df["r_effective"].mean()
        eod_avg_pnl = eod_df["pnl_usd"].mean()
        eod_share = n_eod / M["n"] * 100

        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Trade EOD", f"{n_eod}", f"{eod_share:.1f}% del totale")
        k2.metric("WR EOD", f"{eod_wr:.1f}%", f"{eod_wins}W · {n_eod - eod_wins}L")
        k3.metric("PnL EOD totale", fmt_usd(eod_pnl, sign=True))
        k4.metric("Avg PnL EOD", fmt_usd(eod_avg_pnl, sign=True))
        k5.metric("Expectancy R EOD", f"{eod_exp_r:+.2f}")

        st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)

        comp = pd.DataFrame({
            "Exit": ["TP", "SL", "EOD"],
            "Trade": [len(tp_df), len(sl_df), n_eod],
            "WR %": [
                (tp_df["is_win"].mean() * 100) if len(tp_df) else 0,
                (sl_df["is_win"].mean() * 100) if len(sl_df) else 0,
                eod_wr,
            ],
            "Avg R": [
                tp_df["r_effective"].mean() if len(tp_df) else 0,
                sl_df["r_effective"].mean() if len(sl_df) else 0,
                eod_exp_r,
            ],
            "PnL $": [tp_df["pnl_usd"].sum(), sl_df["pnl_usd"].sum(), eod_pnl],
            "Avg time (min)": [
                tp_df["time_in_trade_min"].mean() if len(tp_df) else 0,
                sl_df["time_in_trade_min"].mean() if len(sl_df) else 0,
                eod_df["time_in_trade_min"].mean() if n_eod else 0,
            ],
        })

        st.markdown("#### Confronto exit type")
        c1, c2 = st.columns(2)
        with c1:
            fig_cnt = go.Figure(
                go.Bar(
                    x=comp["Exit"], y=comp["Trade"],
                    marker_color=[C_WIN, C_LOSS, C_GOLD], marker_line_width=0,
                    text=comp["Trade"], textposition="outside",
                    textfont=dict(color=C_TEXT, size=12),
                )
            )
            fig_cnt.update_layout(**PLOTLY_LAYOUT, height=300,
                                  title=dict(text="Numero di trade per tipo di uscita", x=0.01))
            fig_cnt.update_yaxes(title="Trade")
            st.plotly_chart(fig_cnt, width="stretch")
        with c2:
            fig_r = go.Figure(
                go.Bar(
                    x=comp["Exit"], y=comp["Avg R"],
                    marker_color=[C_WIN if v >= 0 else C_LOSS for v in comp["Avg R"]],
                    marker_line_width=0,
                    text=[f"{v:+.2f}" for v in comp["Avg R"]], textposition="outside",
                    textfont=dict(color=C_TEXT, size=12),
                )
            )
            fig_r.add_hline(y=0, line_dash="dot", line_color=C_NEUTRAL)
            fig_r.update_layout(**PLOTLY_LAYOUT, height=300,
                                title=dict(text="Expectancy R medio per tipo di uscita", x=0.01))
            fig_r.update_yaxes(title="Avg R")
            st.plotly_chart(fig_r, width="stretch")

        st.dataframe(
            comp.style.format({
                "WR %": "{:.1f}",
                "Avg R": "{:+.3f}",
                "PnL $": "{:+,.2f}",
                "Avg time (min)": "{:.0f}",
            }),
            width="stretch", hide_index=True,
        )

        st.markdown("<div style='margin-top:14px'></div>", unsafe_allow_html=True)
        c_d, c_h = st.columns(2)

        with c_d:
            st.markdown("#### EOD per direction")
            dir_eod = eod_df.groupby("direction").agg(
                trade=("is_win", "count"),
                wr=("is_win", lambda x: x.mean() * 100),
                pnl=("pnl_usd", "sum"),
            ).reset_index()
            if len(dir_eod):
                fig_ed = go.Figure(
                    go.Bar(
                        x=dir_eod["direction"], y=dir_eod["pnl"],
                        marker_color=[C_WIN if v >= 0 else C_LOSS for v in dir_eod["pnl"]],
                        marker_line_width=0,
                        text=[f"{r['trade']} trade · WR {r['wr']:.0f}%" for _, r in dir_eod.iterrows()],
                        textposition="outside", textfont=dict(color=C_MUTED, size=11),
                    )
                )
                fig_ed.update_layout(**PLOTLY_LAYOUT, height=300)
                fig_ed.update_yaxes(title="PnL $")
                st.plotly_chart(fig_ed, width="stretch")

        with c_h:
            st.markdown("#### EOD per orario entry")
            hour_eod = eod_df.groupby("entry_hour_str").agg(
                trade=("is_win", "count"),
                pnl=("pnl_usd", "sum"),
            ).reset_index().sort_values("entry_hour_str")
            if len(hour_eod):
                fig_eh = go.Figure(
                    go.Bar(
                        x=hour_eod["entry_hour_str"], y=hour_eod["pnl"],
                        marker_color=[C_WIN if v >= 0 else C_LOSS for v in hour_eod["pnl"]],
                        marker_line_width=0,
                        text=[f"n={t}" for t in hour_eod["trade"]],
                        textposition="outside", textfont=dict(color=C_MUTED, size=11),
                    )
                )
                fig_eh.update_layout(**PLOTLY_LAYOUT, height=300)
                fig_eh.update_yaxes(title="PnL $")
                st.plotly_chart(fig_eh, width="stretch")

        st.markdown("#### Trade EOD — dettaglio")
        eod_show = eod_df[[
            "date", "entry_hour_str", "direction", "entry_price", "exit_price",
            "pnl_usd", "r_effective", "time_in_trade_min", "r_target",
        ]].rename(columns={
            "entry_hour_str": "entry",
            "time_in_trade_min": "minuti",
            "r_effective": "R",
            "r_target": "target",
        }).iloc[::-1].reset_index(drop=True)

        def _col(v):
            if pd.isna(v): return ""
            return f"color: {C_WIN}; font-weight: 600" if v > 0 else f"color: {C_LOSS}; font-weight: 600"

        st.dataframe(
            eod_show.style.map(_col, subset=["pnl_usd", "R"]).format({
                "entry_price": "{:.2f}", "exit_price": "{:.2f}",
                "pnl_usd": "{:+,.2f}", "R": "{:+.3f}",
                "minuti": "{:.0f}", "target": "{:.2f}",
            }),
            width="stretch", hide_index=True,
        )

        st.caption(
            "**Come leggere l'EOD**: se il PnL medio degli EOD è positivo, il bot sta "
            "'raschiando' profit da trade che non hanno raggiunto il TP — potresti valutare "
            "TP più conservativi. Se è negativo, stai tenendo troppo a lungo posizioni in "
            "perdita: rivedi l'orario di entry o aggiungi un time-stop intermedio."
        )


# ============================================================================ #
# TAB: TRADE LOG
# ============================================================================ #
with tab_trades:
    st.markdown(f"#### Trade log ({len(df)} trade filtrati)")

    cols_show = [
        "date", "entry_hour_str", "direction", "entry_price", "qty",
        "or_size", "r_target", "exit_hour_str", "exit_type", "exit_price",
        "pnl_points", "pnl_usd", "r_effective", "time_in_trade_min", "instrument",
    ]
    table = df[cols_show].copy().rename(columns={
        "entry_hour_str": "entry",
        "exit_hour_str": "exit",
        "time_in_trade_min": "min",
        "r_effective": "R",
    }).iloc[::-1].reset_index(drop=True)

    def color_pnl(v):
        if pd.isna(v): return ""
        if v > 0: return f"color: {C_WIN}; font-weight: 600"
        if v < 0: return f"color: {C_LOSS}; font-weight: 600"
        return ""

    styled = table.style.map(color_pnl, subset=["pnl_usd", "R", "pnl_points"]).format({
        "entry_price": "{:.2f}", "exit_price": "{:.2f}",
        "or_size": "{:.2f}", "r_target": "{:.2f}",
        "pnl_points": "{:+.2f}", "pnl_usd": "{:+,.2f}",
        "R": "{:+.3f}", "min": "{:.0f}",
    })
    st.dataframe(styled, width="stretch", hide_index=True, height=520)

    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Scarica CSV filtrato", data=csv_bytes,
        file_name="orb_trades_filtered.csv", mime="text/csv",
    )
