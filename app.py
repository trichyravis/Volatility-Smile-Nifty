
"""
Volatility Smile vs Skew — Interactive Explainer
The Mountain Path Academy
Prof. V. Ravichandran
──────────────────────────────────────────────────
Hull Ch. 20 | Nifty 50 Option Chain | CFA / FRM / MBA
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# ══════════════════════════════════════════════════════════
#  PAGE CONFIG & CONSTANTS
# ══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Volatility Smile vs Skew — The Mountain Path Academy",
    page_icon="⛰",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Mountain Path Palette
GOLD = "#FFD700"
BLUE = "#003366"
MID_BLUE = "#004d80"
CARD_BG = "#112240"
TEXT = "#e6f1ff"
MUTED = "#8892b0"
GREEN = "#28a745"
RED = "#dc3545"
LIGHT_BLUE = "#ADD8E6"
BG_DARK = "#1a2332"
BG_MID = "#243447"
HULL_AMBER = "#f0c040"
PLOT_BG = "#0a1628"

LINKEDIN = "https://www.linkedin.com/in/trichyravis"
GITHUB = "https://github.com/trichyravis"
WEBSITE = "https://themountainpathacademy.com"

# ══════════════════════════════════════════════════════════
#  DATA
# ══════════════════════════════════════════════════════════
NIFTY_SPOT = 24250

nifty_data = pd.DataFrame({
    "Strike (K)": [23000, 23250, 23500, 23750, 24000, 24250, 24500, 24750, 25000, 25250, 25500],
    "Call IV (%)": [18.2, 17.1, 15.8, 14.3, 12.8, 11.9, 12.4, 13.1, 14.0, 15.2, 16.5],
    "Put IV (%)":  [19.8, 18.6, 17.2, 15.5, 13.4, 12.1, 11.8, 12.2, 12.9, 13.8, 14.9],
})
nifty_data["K/S₀"] = nifty_data["Strike (K)"] / NIFTY_SPOT

# FX-style smile (symmetric)
smile_moneyness = np.array([0.90, 0.92, 0.94, 0.96, 0.98, 1.00, 1.02, 1.04, 1.06, 1.08, 1.10])
smile_iv = np.array([18.5, 16.8, 15.2, 13.8, 12.6, 12.0, 12.5, 13.6, 15.0, 16.7, 18.4])

# Equity-style skew
skew_moneyness = np.array([0.90, 0.92, 0.94, 0.96, 0.98, 1.00, 1.02, 1.04, 1.06, 1.08, 1.10])
skew_iv = np.array([22.0, 20.2, 18.5, 16.8, 15.0, 13.8, 13.2, 12.9, 12.7, 12.6, 12.6])

# Fine curves for smooth plotting
x_fine = np.linspace(0.88, 1.12, 100)

def smooth_interp(x_orig, y_orig, x_new):
    from scipy.interpolate import CubicSpline
    cs = CubicSpline(x_orig, y_orig)
    return cs(x_new)


# ══════════════════════════════════════════════════════════
#  GLOBAL STYLES
# ══════════════════════════════════════════════════════════
st.html(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Source+Sans+Pro:wght@300;400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    .stApp {{
        background: linear-gradient(135deg, {BG_DARK}, {BG_MID}, #2a3f5f);
    }}
    
    /* Hide default Streamlit chrome */
    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 1rem;
        max-width: 1100px;
    }}
    
    /* Tab styling — two-row wrap */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
        background: rgba(0,51,102,0.4);
        border-radius: 10px;
        padding: 8px;
        flex-wrap: wrap !important;
        justify-content: center;
    }}
    .stTabs [data-baseweb="tab-list"] > div:first-child {{
        /* Hide the default highlight bar since wrapping breaks it */
        display: none !important;
    }}
    .stTabs [data-baseweb="tab"] {{
        color: {MUTED};
        font-family: 'Source Sans Pro', sans-serif;
        font-weight: 600;
        font-size: 0.86rem;
        border-radius: 8px;
        padding: 8px 16px;
        white-space: nowrap;
        border: 1px solid transparent;
        transition: all 0.2s ease;
    }}
    .stTabs [data-baseweb="tab"]:hover {{
        background: rgba(255,215,0,0.1);
        border-color: rgba(255,215,0,0.25);
    }}
    .stTabs [aria-selected="true"] {{
        background: {GOLD} !important;
        color: {BLUE} !important;
        border-color: {GOLD} !important;
    }}
    .stTabs [data-baseweb="tab-panel"] {{
        padding-top: 1rem;
    }}
    .stTabs [data-baseweb="tab-highlight"] {{
        display: none !important;
    }}
    
    /* Selectbox, slider, number_input */
    .stSelectbox label, .stSlider label, .stNumberInput label {{
        color: {LIGHT_BLUE} !important;
        -webkit-text-fill-color: {LIGHT_BLUE} !important;
        font-family: 'Source Sans Pro', sans-serif !important;
        font-weight: 600 !important;
    }}
    
    /* Metric */
    [data-testid="stMetricValue"] {{
        color: {GOLD} !important;
        -webkit-text-fill-color: {GOLD} !important;
        font-family: 'Playfair Display', serif !important;
    }}
    [data-testid="stMetricLabel"] {{
        color: {LIGHT_BLUE} !important;
        -webkit-text-fill-color: {LIGHT_BLUE} !important;
    }}
    [data-testid="stMetricDelta"] {{
        font-family: 'JetBrains Mono', monospace !important;
    }}
</style>
""")


# ══════════════════════════════════════════════════════════
#  HELPER: HTML BLOCKS
# ══════════════════════════════════════════════════════════
def mountain_header():
    st.html(f"""
    <div style="
        background: rgba(0,51,102,0.92);
        border-bottom: 3px solid {GOLD};
        border-radius: 12px 12px 0 0;
        padding: 18px 28px;
        margin-bottom: 4px;
        user-select: none;
    ">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
            <div>
                <span style="font-family:'Playfair Display',serif; color:{GOLD}; -webkit-text-fill-color:{GOLD}; font-size:1.5rem; font-weight:700;">
                    ⛰ Volatility Smile vs Skew
                </span>
                <br>
                <span style="font-family:'Source Sans Pro',sans-serif; color:{LIGHT_BLUE}; -webkit-text-fill-color:{LIGHT_BLUE}; font-size:0.88rem; font-weight:300;">
                    Hull Chapter 20 — Interactive Explainer with Nifty 50 Option Chain Data
                </span>
            </div>
            <div style="text-align:right;">
                <span style="font-family:'Source Sans Pro',sans-serif; color:{MUTED}; -webkit-text-fill-color:{MUTED}; font-size:0.72rem;">
                    Prof. V. Ravichandran
                </span>
                <br>
                <span style="font-family:'Source Sans Pro',sans-serif; color:{MUTED}; -webkit-text-fill-color:{MUTED}; font-size:0.68rem;">
                    NMIMS Bangalore · BITS Pilani · RV University · Goa Institute of Management
                </span>
            </div>
        </div>
    </div>
    """)


def hull_box(label: str, content: str):
    st.html(f"""
    <div style="
        background: rgba(240,192,64,0.07);
        border: 1px solid rgba(240,192,64,0.28);
        border-radius: 9px;
        padding: 16px 20px;
        margin: 10px 0 14px;
        user-select: none;
    ">
        <div style="
            font-family:'Source Sans Pro',sans-serif;
            font-size:0.65rem;
            text-transform:uppercase;
            letter-spacing:1.8px;
            color:{MUTED}; -webkit-text-fill-color:{MUTED};
            margin-bottom:7px;
        ">{label}</div>
        <div style="
            font-family:'JetBrains Mono',monospace;
            font-size:0.84rem;
            line-height:1.7;
            color:{HULL_AMBER}; -webkit-text-fill-color:{HULL_AMBER};
        ">{content}</div>
    </div>
    """)


def voiceover_box(text: str):
    st.html(f"""
    <div style="
        background: rgba(0,51,102,0.5);
        border-left: 3px solid {GOLD};
        border-radius: 0 9px 9px 0;
        padding: 14px 20px;
        margin: 10px 0;
        user-select: none;
    ">
        <div style="
            font-family:'Source Sans Pro',sans-serif;
            font-size:0.68rem;
            text-transform:uppercase;
            letter-spacing:1.4px;
            color:{GOLD}; -webkit-text-fill-color:{GOLD};
            margin-bottom:5px;
            font-weight:700;
        ">🎙 Voiceover / Class Note</div>
        <div style="
            font-family:'Source Sans Pro',sans-serif;
            font-size:0.9rem;
            line-height:1.6;
            color:{TEXT}; -webkit-text-fill-color:{TEXT};
        ">{text}</div>
    </div>
    """)


def insight_card(title: str, body: str, accent: str = LIGHT_BLUE):
    st.html(f"""
    <div style="
        background: rgba(0,51,102,0.3);
        border: 1px solid {accent}33;
        border-radius: 9px;
        padding: 16px 18px;
        margin: 6px 0;
        user-select: none;
    ">
        <div style="
            font-family:'Source Sans Pro',sans-serif;
            font-size:0.84rem;
            font-weight:600;
            color:{accent}; -webkit-text-fill-color:{accent};
            margin-bottom:5px;
        ">{title}</div>
        <div style="
            font-family:'Source Sans Pro',sans-serif;
            font-size:0.82rem;
            line-height:1.5;
            color:{MUTED}; -webkit-text-fill-color:{MUTED};
        ">{body}</div>
    </div>
    """)


def mountain_footer():
    st.html(f"""
    <div style="
        text-align:center;
        padding:28px 20px 10px;
        margin-top:20px;
        border-top:1px solid rgba(255,215,0,0.12);
        user-select:none;
    ">
        <div style="font-family:'Playfair Display',serif; color:{GOLD}; -webkit-text-fill-color:{GOLD}; font-size:1rem; margin-bottom:6px;">
            ⛰ The Mountain Path Academy
        </div>
        <div style="font-family:'Source Sans Pro',sans-serif; color:{MUTED}; -webkit-text-fill-color:{MUTED}; font-size:0.74rem; margin-bottom:4px;">
            Prof. V. Ravichandran — Visiting Faculty @ NMIMS Bangalore, BITS Pilani, RV University Bangalore, Goa Institute of Management
        </div>
        <div style="font-family:'Source Sans Pro',sans-serif; font-size:0.76rem;">
            <a href="{WEBSITE}" target="_blank" style="color:{GOLD}; -webkit-text-fill-color:{GOLD}; text-decoration:none;">themountainpathacademy.com</a>
            &nbsp;·&nbsp;
            <a href="{LINKEDIN}" target="_blank" style="color:{GOLD}; -webkit-text-fill-color:{GOLD}; text-decoration:none;">LinkedIn</a>
            &nbsp;·&nbsp;
            <a href="{GITHUB}" target="_blank" style="color:{GOLD}; -webkit-text-fill-color:{GOLD}; text-decoration:none;">GitHub</a>
        </div>
    </div>
    """)


# ══════════════════════════════════════════════════════════
#  PLOTLY CHART BUILDER
# ══════════════════════════════════════════════════════════
def base_layout(title="", xaxis_title="K / S₀ (Moneyness)", yaxis_title="σ_imp (%)", height=480):
    return go.Layout(
        title=dict(
            text=title,
            font=dict(family="Playfair Display, serif", size=20, color=GOLD),
            x=0.01, y=0.97,
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=PLOT_BG,
        font=dict(family="Source Sans Pro, sans-serif", color=TEXT),
        height=height,
        margin=dict(l=65, r=30, t=55, b=60),
        xaxis=dict(
            title=dict(text=xaxis_title, font=dict(color=LIGHT_BLUE, size=14)),
            gridcolor="rgba(255,255,255,0.05)",
            zerolinecolor="rgba(255,255,255,0.08)",
            tickfont=dict(color=MUTED, size=12),
            tickformat=".2f",
        ),
        yaxis=dict(
            title=dict(text=yaxis_title, font=dict(color=LIGHT_BLUE, size=14)),
            gridcolor="rgba(255,255,255,0.05)",
            zerolinecolor="rgba(255,255,255,0.08)",
            tickfont=dict(color=MUTED, size=12),
            ticksuffix="%",
        ),
        legend=dict(
            bgcolor="rgba(17,34,64,0.85)",
            bordercolor="rgba(255,215,0,0.2)",
            borderwidth=1,
            font=dict(size=12, color=TEXT),
        ),
        hoverlabel=dict(
            bgcolor=CARD_BG,
            font_size=13,
            font_family="JetBrains Mono, monospace",
            bordercolor=GOLD,
        ),
    )


def add_atm_line(fig, x=1.0, label="ATM"):
    fig.add_shape(
        type="line", x0=x, x1=x, y0=0, y1=1, yref="paper",
        line=dict(color=GOLD, width=1.5, dash="dot"),
    )
    fig.add_annotation(
        x=x, y=1.02, yref="paper", text=label,
        showarrow=False, font=dict(color=GOLD, size=12, family="Source Sans Pro"),
    )


def chart_smile(height=480):
    """Chart 1 — Volatility Smile (FX Style)"""
    try:
        y_smooth = smooth_interp(smile_moneyness, smile_iv, x_fine)
    except Exception:
        y_smooth = np.interp(x_fine, smile_moneyness, smile_iv)

    fig = go.Figure(layout=base_layout("Chart 1 — Volatility Smile (FX Style)", height=height))
    fig.add_trace(go.Scatter(
        x=x_fine, y=y_smooth, mode="lines",
        line=dict(color=GOLD, width=3, shape="spline"),
        name="σ_imp (FX Smile)", hovertemplate="K/S₀: %{x:.3f}<br>IV: %{y:.1f}%<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=smile_moneyness, y=smile_iv, mode="markers",
        marker=dict(color=GOLD, size=9, line=dict(color=PLOT_BG, width=2)),
        name="Data Points", hovertemplate="K/S₀: %{x:.2f}<br>IV: %{y:.1f}%<extra></extra>",
    ))

    # Shaded tails
    fig.add_shape(type="rect", x0=0.88, x1=0.94, y0=0, y1=1, yref="paper",
                  fillcolor="rgba(220,53,69,0.06)", line_width=0)
    fig.add_shape(type="rect", x0=1.06, x1=1.12, y0=0, y1=1, yref="paper",
                  fillcolor="rgba(220,53,69,0.06)", line_width=0)
    fig.add_annotation(x=0.91, y=19, text="OTM Puts<br>(High IV)", showarrow=False,
                       font=dict(color=RED, size=11))
    fig.add_annotation(x=1.09, y=19, text="OTM Calls<br>(High IV)", showarrow=False,
                       font=dict(color=RED, size=11))

    add_atm_line(fig)
    fig.update_xaxes(range=[0.88, 1.12])
    fig.update_yaxes(range=[10, 20.5])
    return fig


def chart_skew(height=480):
    """Chart 2 — Volatility Skew (Nifty Put IV)"""
    m = nifty_data["K/S₀"].values
    iv = nifty_data["Put IV (%)"].values
    try:
        y_smooth = smooth_interp(m, iv, x_fine)
    except Exception:
        y_smooth = np.interp(x_fine, m, iv)

    fig = go.Figure(layout=base_layout("Chart 2 — Volatility Skew (Nifty 50 Put IV)", height=height))
    fig.add_trace(go.Scatter(
        x=x_fine, y=y_smooth, mode="lines",
        line=dict(color=RED, width=3, shape="spline"),
        name="Nifty Put IV",
    ))
    fig.add_trace(go.Scatter(
        x=m, y=iv, mode="markers+text",
        marker=dict(color=RED, size=10, line=dict(color=PLOT_BG, width=2)),
        text=[f"₹{s:,}" if s in [23000, 24250, 25500] else "" for s in nifty_data["Strike (K)"]],
        textposition="top center",
        textfont=dict(color=TEXT, size=11, family="JetBrains Mono"),
        name="Strike Points",
        hovertemplate="K: ₹%{customdata:,}<br>K/S₀: %{x:.3f}<br>Put IV: %{y:.1f}%<extra></extra>",
        customdata=nifty_data["Strike (K)"],
    ))

    # Fear premium shading
    mask = x_fine <= 1.0
    fig.add_trace(go.Scatter(
        x=np.concatenate([x_fine[mask], x_fine[mask][::-1]]),
        y=np.concatenate([y_smooth[mask], np.full(mask.sum(), 10)]),
        fill="toself", fillcolor="rgba(220,53,69,0.08)",
        line=dict(width=0), showlegend=False, hoverinfo="skip",
    ))
    fig.add_annotation(x=0.96, y=17.5, text="🔺 Fear Premium<br>Zone",
                       showarrow=False, font=dict(color=RED, size=12, family="Source Sans Pro"))

    add_atm_line(fig, x=1.0, label=f"ATM (₹{NIFTY_SPOT:,})")
    fig.update_xaxes(range=[0.93, 1.07])
    fig.update_yaxes(range=[10, 22])
    return fig


def chart_overlay(height=500):
    """Chart 3 — Smile vs Skew Overlay"""
    m = nifty_data["K/S₀"].values
    iv_put = nifty_data["Put IV (%)"].values
    try:
        smile_smooth = smooth_interp(smile_moneyness, smile_iv, x_fine)
        skew_smooth = smooth_interp(m, iv_put, x_fine)
    except Exception:
        smile_smooth = np.interp(x_fine, smile_moneyness, smile_iv)
        skew_smooth = np.interp(x_fine, m, iv_put)

    fig = go.Figure(layout=base_layout("Chart 3 — Smile vs Skew: The Overlay", height=height))

    # Divergence shading (left side)
    mask_left = x_fine <= 1.0
    x_left = x_fine[mask_left]
    fig.add_trace(go.Scatter(
        x=np.concatenate([x_left, x_left[::-1]]),
        y=np.concatenate([skew_smooth[mask_left], smile_smooth[mask_left][::-1]]),
        fill="toself", fillcolor="rgba(220,53,69,0.1)",
        line=dict(width=0), showlegend=False, hoverinfo="skip",
    ))

    # Smile curve (dashed)
    fig.add_trace(go.Scatter(
        x=x_fine, y=smile_smooth, mode="lines",
        line=dict(color=GOLD, width=3, dash="dash"),
        name="Smile (FX-style)",
    ))
    fig.add_trace(go.Scatter(
        x=smile_moneyness, y=smile_iv, mode="markers",
        marker=dict(color=GOLD, size=7, line=dict(color=PLOT_BG, width=1.5)),
        showlegend=False, hovertemplate="Smile — K/S₀: %{x:.2f}<br>IV: %{y:.1f}%<extra></extra>",
    ))

    # Nifty skew (solid)
    fig.add_trace(go.Scatter(
        x=x_fine, y=skew_smooth, mode="lines",
        line=dict(color=RED, width=4),
        name="Nifty 50 Put IV (Skew)",
    ))
    fig.add_trace(go.Scatter(
        x=m, y=iv_put, mode="markers",
        marker=dict(color=RED, size=9, line=dict(color=PLOT_BG, width=2)),
        showlegend=False, hovertemplate="Nifty — K/S₀: %{x:.3f}<br>Put IV: %{y:.1f}%<extra></extra>",
    ))

    fig.add_annotation(x=0.92, y=20.5, text="← Crash Risk<br>Premium",
                       showarrow=False, font=dict(color=RED, size=12))
    fig.add_annotation(x=1.08, y=17.5, text="Smile rises<br>symmetrically →",
                       showarrow=False, font=dict(color=GOLD, size=11))

    add_atm_line(fig)
    fig.update_xaxes(range=[0.88, 1.12])
    fig.update_yaxes(range=[10, 23])
    return fig


def chart_nifty_call_put(height=480):
    """Nifty Call IV vs Put IV by strike"""
    strikes = nifty_data["Strike (K)"]
    fig = go.Figure(layout=base_layout(
        "Nifty 50 — Call IV vs Put IV by Strike",
        xaxis_title="Strike Price (K)", height=height,
    ))
    fig.add_trace(go.Scatter(
        x=strikes, y=nifty_data["Call IV (%)"], mode="lines+markers",
        line=dict(color=LIGHT_BLUE, width=3), marker=dict(size=8, line=dict(color=PLOT_BG, width=2)),
        name="Call IV", hovertemplate="K: ₹%{x:,}<br>Call IV: %{y:.1f}%<extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=strikes, y=nifty_data["Put IV (%)"], mode="lines+markers",
        line=dict(color=RED, width=3), marker=dict(size=8, line=dict(color=PLOT_BG, width=2)),
        name="Put IV", hovertemplate="K: ₹%{x:,}<br>Put IV: %{y:.1f}%<extra></extra>",
    ))
    fig.add_shape(
        type="line", x0=NIFTY_SPOT, x1=NIFTY_SPOT, y0=0, y1=1, yref="paper",
        line=dict(color=GOLD, width=1.5, dash="dot"),
    )
    fig.add_annotation(x=NIFTY_SPOT, y=1.02, yref="paper", text=f"ATM ₹{NIFTY_SPOT:,}",
                       showarrow=False, font=dict(color=GOLD, size=12))
    fig.update_xaxes(tickformat=",")
    return fig


# ══════════════════════════════════════════════════════════
#  INTERACTIVE PARAMETER EXPLORER
# ══════════════════════════════════════════════════════════
def chart_parametric(sigma_atm, alpha, beta, height=480):
    """User-adjustable smile & skew from Hull formulas"""
    x = np.linspace(0.85, 1.15, 200)
    smile_y = sigma_atm + alpha * (x - 1.0) ** 2
    skew_y = sigma_atm - beta * (x - 1.0)
    skew_y = np.maximum(skew_y, 2)  # floor

    fig = go.Figure(layout=base_layout(
        "Interactive: Tune σ_ATM, α (smile), β (skew)", height=height
    ))
    fig.add_trace(go.Scatter(
        x=x, y=smile_y, mode="lines",
        line=dict(color=GOLD, width=3, dash="dash"),
        name=f"Smile: σ_ATM + {alpha:.0f}·(K/S₀ − 1)²",
    ))
    fig.add_trace(go.Scatter(
        x=x, y=skew_y, mode="lines",
        line=dict(color=RED, width=3),
        name=f"Skew: σ_ATM − {beta:.0f}·(K/S₀ − 1)",
    ))
    add_atm_line(fig)
    fig.update_xaxes(range=[0.85, 1.15])
    fig.update_yaxes(range=[0, max(smile_y.max(), skew_y.max()) + 3])
    return fig


# ══════════════════════════════════════════════════════════
#  RENDER
# ══════════════════════════════════════════════════════════
mountain_header()

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📖 Introduction",
    "😊 Volatility Smile",
    "📉 Volatility Skew",
    "📊 Nifty Option Chain",
    "🔀 Smile vs Skew Overlay",
    "🎛 Parameter Explorer",
    "🎓 Q&A — Test Yourself",
])

# ── TAB 1: INTRODUCTION ──────────────────────────────────
with tab1:
    hull_box(
        "Hull Notation — Black-Scholes Framework",
        "c = S₀·N(d₁) − K·e<sup style='color:#f0c040;-webkit-text-fill-color:#f0c040;'>−rT</sup>·N(d₂)"
        "<br>"
        "d₁ = [ln(S₀/K) + (r + σ²/2)T] / (σ√T)"
        "<br><br>"
        "σ<sub style='color:#f0c040;-webkit-text-fill-color:#f0c040;'>imp</sub>(K, T) ≡ the value of σ that equates BS model price to observed market price"
        "<br>"
        f"<span style='color:{LIGHT_BLUE};-webkit-text-fill-color:{LIGHT_BLUE};'>If BS held perfectly → σ<sub>imp</sub> would be flat across all K. It isn't. That's the story.</span>"
    )

    c1, c2 = st.columns(2)
    with c1:
        insight_card(
            "📈 Volatility Smile",
            "Symmetric U-shape. Both deep ITM and deep OTM options trade at higher IV than ATM. "
            "Common in FX markets where currencies can jump in either direction with similar probability.",
            accent=GOLD,
        )
    with c2:
        insight_card(
            "📉 Volatility Skew (Smirk)",
            "Asymmetric — OTM puts (low strikes) carry much higher IV than OTM calls. "
            "Dominant in equity and index markets like Nifty 50. Driven by crash-risk premium post-1987.",
            accent=RED,
        )

    voiceover_box(
        "Black-Scholes assumes constant volatility across all strike prices. But when we invert the formula "
        "to extract σ<sub>imp</sub> from actual market prices, we get a <b>curve</b> — not a flat line. "
        "This pattern manifests as either a <b>smile</b> (symmetric, FX) or a <b>skew</b> (asymmetric, equities). "
        "Understanding the difference is essential for derivatives pricing, risk management, and your CFA/FRM exams."
    )

    hull_box(
        "Why Does This Matter?",
        f"<span style='color:{LIGHT_BLUE};-webkit-text-fill-color:{LIGHT_BLUE};'>1.</span> "
        "BS misprices deep OTM/ITM options if you use a single σ<br>"
        f"<span style='color:{LIGHT_BLUE};-webkit-text-fill-color:{LIGHT_BLUE};'>2.</span> "
        "The smile/skew reveals the market's <b>implied risk-neutral distribution</b><br>"
        f"<span style='color:{LIGHT_BLUE};-webkit-text-fill-color:{LIGHT_BLUE};'>3.</span> "
        "Skew directly impacts hedging costs — steeper skew = costlier downside protection<br>"
        f"<span style='color:{LIGHT_BLUE};-webkit-text-fill-color:{LIGHT_BLUE};'>4.</span> "
        "Practitioners use the <b>volatility surface</b> σ(K, T) — not a single number"
    )


# ── TAB 2: SMILE ─────────────────────────────────────────
with tab2:
    st.plotly_chart(chart_smile(), use_container_width=True, config={"displayModeBar": True, "toImageButtonOptions": {"format": "png", "width": 1200, "height": 600, "filename": "chart1_volatility_smile_mountain_path"}})

    hull_box(
        "Hull Notation — Smile Approximation",
        "σ<sub style='color:#f0c040;-webkit-text-fill-color:#f0c040;'>imp</sub>(K/S₀) ≈ σ<sub>ATM</sub> + α·(K/S₀ − 1)² &nbsp;&nbsp;where α &gt; 0"
        "<br>"
        f"<span style='color:{LIGHT_BLUE};-webkit-text-fill-color:{LIGHT_BLUE};'>Quadratic in moneyness → symmetric \"smile\" shape</span>"
        "<br>"
        f"<span style='color:{LIGHT_BLUE};-webkit-text-fill-color:{LIGHT_BLUE};'>Implies leptokurtic distribution: fat tails on BOTH sides relative to lognormal</span>"
    )

    voiceover_box(
        "In a classic volatility smile, both tails are elevated equally. The market assigns extra premium to large "
        "moves in <em>either</em> direction. Currency markets exhibit this pattern because currencies can jump up "
        "or down with comparable probability — there is no inherent 'crash' direction. The implied distribution "
        "is symmetric but fat-tailed (leptokurtic) relative to the lognormal assumed by Black-Scholes."
    )

    c1, c2 = st.columns(2)
    with c1:
        insight_card("Typical Markets", "Foreign exchange options (EUR/USD, USD/JPY), commodity options with symmetric risk profiles", GOLD)
    with c2:
        insight_card("Distributional Implication", "Implied RN distribution has heavier tails than lognormal on both sides — positive excess kurtosis", LIGHT_BLUE)


# ── TAB 3: SKEW ──────────────────────────────────────────
with tab3:
    st.plotly_chart(chart_skew(), use_container_width=True, config={"displayModeBar": True, "toImageButtonOptions": {"format": "png", "width": 1200, "height": 600, "filename": "chart2_volatility_skew_mountain_path"}})

    hull_box(
        "Hull Notation — Skew Approximation",
        "σ<sub style='color:#f0c040;-webkit-text-fill-color:#f0c040;'>imp</sub>(K/S₀) ≈ σ<sub>ATM</sub> − β·(K/S₀ − 1) &nbsp;&nbsp;where β &gt; 0"
        "<br>"
        f"<span style='color:{RED};-webkit-text-fill-color:{RED};'>Post-1987 crash: markets price crash risk into OTM puts permanently</span>"
        "<br>"
        f"<span style='color:{LIGHT_BLUE};-webkit-text-fill-color:{LIGHT_BLUE};'>Implies negatively skewed, leptokurtic implied distribution</span>"
    )

    voiceover_box(
        "After the 1987 crash, equity options never returned to a flat volatility structure. The skew tells us "
        "the market consistently prices in a higher probability of sharp downside moves. OTM puts at lower "
        "strikes carry a <b>fear premium</b> — what Hull describes as the 'crashophobia' effect "
        "(Rubinstein, 1994). Nifty 50 options follow this global equity pattern precisely."
    )

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("OTM Put IV (K=23,000)", "19.8%", "+7.7pp vs ATM", delta_color="inverse")
    with m2:
        st.metric("ATM Put IV (K=24,250)", "12.1%", "Baseline")
    with m3:
        st.metric("OTM Call IV (K=25,500)", "14.9%", "+2.8pp vs ATM", delta_color="inverse")


# ── TAB 4: NIFTY OPTION CHAIN ────────────────────────────
with tab4:
    st.plotly_chart(chart_nifty_call_put(), use_container_width=True, config={"displayModeBar": True, "toImageButtonOptions": {"format": "png", "width": 1200, "height": 600, "filename": "chart_nifty_call_put_iv_mountain_path"}})

    # Styled dataframe
    st.html(f"""
    <div style="
        font-family:'Source Sans Pro',sans-serif;
        color:{LIGHT_BLUE}; -webkit-text-fill-color:{LIGHT_BLUE};
        font-size:0.88rem;
        font-weight:600;
        margin:14px 0 6px;
        user-select:none;
    ">Nifty 50 Option Chain — Implied Volatility by Strike &nbsp;|&nbsp; Spot: ₹{NIFTY_SPOT:,}</div>
    """)

    display_df = nifty_data.copy()
    display_df["Status"] = display_df["Strike (K)"].apply(
        lambda k: "◆ ATM" if k == NIFTY_SPOT else ("ITM Call / OTM Put" if k < NIFTY_SPOT else "OTM Call / ITM Put")
    )
    display_df["K/S₀"] = display_df["K/S₀"].map("{:.4f}".format)
    display_df["Call IV (%)"] = display_df["Call IV (%)"].map("{:.1f}".format)
    display_df["Put IV (%)"] = display_df["Put IV (%)"].map("{:.1f}".format)
    display_df["Strike (K)"] = display_df["Strike (K)"].apply(lambda x: f"₹{x:,}")

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=430,
    )

    hull_box(
        "Key Observation (Hull Ch. 20.2)",
        f"Put IV at K=23,000 → <b>19.8%</b> &nbsp;vs&nbsp; ATM Put IV → <b>12.1%</b>"
        "<br>"
        f"<span style='color:{RED};-webkit-text-fill-color:{RED};'>Δσ = +7.7 percentage points — classic equity skew</span>"
        "<br>"
        f"<span style='color:{LIGHT_BLUE};-webkit-text-fill-color:{LIGHT_BLUE};'>OTM puts are much more expensive than BS with flat σ would predict</span>"
    )

    voiceover_box(
        "The data speaks clearly. Put IV at the 23,000 strike is nearly 8 percentage points higher than ATM. "
        "This is pure crash protection premium. Meanwhile, OTM call IV also rises at higher strikes, but less steeply — "
        "giving us that asymmetric skew we discussed. Notice how call IV forms a mild smile at very high strikes, "
        "while put IV is dominated by the downward-sloping skew."
    )


# ── TAB 5: OVERLAY ───────────────────────────────────────
with tab5:
    st.plotly_chart(chart_overlay(height=520), use_container_width=True, config={"displayModeBar": True, "toImageButtonOptions": {"format": "png", "width": 1200, "height": 650, "filename": "chart3_smile_vs_skew_overlay_mountain_path"}})

    hull_box(
        "Hull — Why the Difference?",
        f"<span style='color:{GOLD};-webkit-text-fill-color:{GOLD};'><b>Smile</b></span>"
        " → Leptokurtic distribution (fat tails both sides) → FX, commodities"
        "<br>"
        f"<span style='color:{RED};-webkit-text-fill-color:{RED};'><b>Skew</b></span>"
        " → Negatively skewed + leptokurtic → Equities, indices"
        "<br><br>"
        f"<span style='color:{LIGHT_BLUE};-webkit-text-fill-color:{LIGHT_BLUE};'>"
        "Implied distribution = lognormal + heavy left tail (leverage effect + crashophobia)</span>"
    )

    voiceover_box(
        "This overlay is the key visual. The <b style='color:#FFD700;-webkit-text-fill-color:#FFD700;'>gold dashed curve</b> "
        "is a symmetric smile; the <b style='color:#dc3545;-webkit-text-fill-color:#dc3545;'>red solid curve</b> is "
        "Nifty's actual put IV. The shaded region on the left shows the divergence — the crash risk premium that "
        "exists in equity markets but not in FX. Hull connects this to the implied risk-neutral density being "
        "negatively skewed relative to lognormal. The right tails roughly converge, but the left tails diverge sharply."
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        insight_card("Smile ≠ Skew", "Symmetric (FX) vs asymmetric (equity). Both violate BS constant-σ but for different distributional reasons.", GOLD)
    with c2:
        insight_card("Crashophobia", "Post-1987, equity markets embed a permanent fear premium in OTM puts — heavier left tail.", RED)
    with c3:
        insight_card("Nifty = Global Pattern", "Indian index options show clear skew consistent with all major equity markets worldwide.", GREEN)
    with c4:
        insight_card("Trading Impact", "Steeper skew → costlier protective puts → affects risk reversals, collars, and tail hedging.", LIGHT_BLUE)


# ── TAB 6: PARAMETER EXPLORER ─────────────────────────────
with tab6:
    st.html(f"""
    <div style="
        font-family:'Playfair Display',serif;
        color:{GOLD}; -webkit-text-fill-color:{GOLD};
        font-size:1.15rem;
        margin-bottom:4px;
        user-select:none;
    ">🎛 Tune the Hull Approximations</div>
    <div style="
        font-family:'Source Sans Pro',sans-serif;
        color:{MUTED}; -webkit-text-fill-color:{MUTED};
        font-size:0.84rem;
        margin-bottom:14px;
        user-select:none;
    ">Adjust σ_ATM, α (smile curvature), and β (skew slope) to see how the shapes change</div>
    """)

    pc1, pc2, pc3 = st.columns(3)
    with pc1:
        sigma_atm = st.slider("σ_ATM (%)", min_value=5.0, max_value=30.0, value=12.0, step=0.5)
    with pc2:
        alpha = st.slider("α (Smile Curvature)", min_value=0.0, max_value=500.0, value=150.0, step=10.0)
    with pc3:
        beta = st.slider("β (Skew Slope)", min_value=0.0, max_value=100.0, value=40.0, step=2.0)

    st.plotly_chart(
        chart_parametric(sigma_atm, alpha, beta, height=500),
        use_container_width=True,
        config={"displayModeBar": True},
    )

    hull_box(
        "Formulas Being Plotted",
        f"<span style='color:{GOLD};-webkit-text-fill-color:{GOLD};'>Smile:</span> "
        f"σ_imp = {sigma_atm:.1f} + {alpha:.0f} × (K/S₀ − 1)²"
        "<br>"
        f"<span style='color:{RED};-webkit-text-fill-color:{RED};'>Skew:</span> "
        f"σ_imp = {sigma_atm:.1f} − {beta:.0f} × (K/S₀ − 1)"
    )

    voiceover_box(
        f"With σ<sub>ATM</sub> = {sigma_atm:.1f}%, the smile curve (α = {alpha:.0f}) produces a minimum at ATM "
        f"and rises symmetrically. The skew curve (β = {beta:.0f}) slopes downward from left to right. "
        "Try increasing β to simulate a post-crash environment with extreme fear. "
        "Increase α to model a currency pair with high jump risk in both directions."
    )


# ── TAB 7: Q&A — TEST YOURSELF ───────────────────────────
with tab7:

    # ── Q&A Data ──
    QA_SECTIONS = {
        "Section A — Foundations: What Is Implied Volatility?": [
            {
                "q": "Q1. What exactly is implied volatility (IV)?",
                "a": """Implied volatility is the value of σ that, when plugged into the Black-Scholes formula, makes the
model price equal to the observed market price of the option.

<b>Formally (Hull notation):</b> Given a market-observed call price c<sub>mkt</sub>, the implied volatility σ<sub>imp</sub> satisfies:

&emsp;c<sub>mkt</sub> = S₀·N(d₁) − K·e<sup>−rT</sup>·N(d₂) &nbsp;&nbsp;where d₁, d₂ use σ = σ<sub>imp</sub>

It is <b>not</b> a forecast of future volatility. It is the market's <b>consensus pricing input</b> — the volatility
that makes supply and demand balance at the observed premium.

<b>Key insight:</b> If Black-Scholes were perfectly correct (lognormal returns, constant σ), then σ<sub>imp</sub> would be
the same for every strike K and every expiry T. The fact that it varies is precisely what creates the smile/skew.""",
            },
            {
                "q": "Q2. How is implied volatility different from historical (realized) volatility?",
                "a": """<b>Historical Volatility (HV)</b> is backward-looking — it measures the standard deviation of past log returns
over a specific window (e.g., 20-day, 60-day). It tells you what <em>did</em> happen.

<b>Implied Volatility (IV)</b> is forward-looking — it is extracted from current option prices and reflects what
the market <em>expects</em> (or more precisely, what the market is <em>pricing in</em>) for future volatility over the
option's remaining life.

<table style="width:100%; margin:10px 0; font-size:0.82rem;">
<tr style="border-bottom:1px solid rgba(255,215,0,0.2);">
  <td style="color:#ADD8E6; padding:6px;"><b>Feature</b></td>
  <td style="color:#ADD8E6; padding:6px;"><b>Historical Vol</b></td>
  <td style="color:#ADD8E6; padding:6px;"><b>Implied Vol</b></td>
</tr>
<tr><td style="padding:4px 6px;">Direction</td><td style="padding:4px 6px;">Backward-looking</td><td style="padding:4px 6px;">Forward-looking</td></tr>
<tr><td style="padding:4px 6px;">Source</td><td style="padding:4px 6px;">Past return data</td><td style="padding:4px 6px;">Current option prices</td></tr>
<tr><td style="padding:4px 6px;">Model-free?</td><td style="padding:4px 6px;">Yes (pure statistics)</td><td style="padding:4px 6px;">No (requires BS or another model)</td></tr>
<tr><td style="padding:4px 6px;">Strike-dependent?</td><td style="padding:4px 6px;">No</td><td style="padding:4px 6px;">Yes — that's the smile/skew!</td></tr>
<tr><td style="padding:4px 6px;">Contains risk premium?</td><td style="padding:4px 6px;">No</td><td style="padding:4px 6px;">Yes — includes fear/greed</td></tr>
</table>

Typically, <b>IV > HV</b> because option sellers demand a risk premium (the "variance risk premium").""",
            },
            {
                "q": "Q3. Why does Black-Scholes assume constant volatility, and why is this unrealistic?",
                "a": """Black-Scholes (1973) was derived under several simplifying assumptions, including:
<br>• Geometric Brownian Motion: dS/S = μ·dt + σ·dW where σ is <b>constant</b>
<br>• Log-returns are normally distributed → prices are lognormally distributed
<br>• No jumps, no regime changes, no stochastic volatility

<b>Why this fails in practice:</b>
<br>• <b>Volatility clustering:</b> High-vol days tend to follow high-vol days (GARCH effects)
<br>• <b>Fat tails:</b> Real return distributions have excess kurtosis (more extreme events than normal)
<br>• <b>Negative skewness:</b> Equity markets crash more sharply than they rally
<br>• <b>Jump risk:</b> Sudden large moves (earnings, geopolitical events) are not captured by diffusion
<br>• <b>Leverage effect:</b> As stock prices fall, firm leverage rises → volatility increases

All of these violations show up in the option market as a <b>non-flat implied volatility surface</b>.
The smile and skew are the market's way of correcting for BS's flawed distributional assumptions.""",
            },
            {
                "q": "Q4. What is the volatility surface σ(K, T)?",
                "a": """The <b>volatility surface</b> is the complete three-dimensional mapping of implied volatility as a function
of both strike price K and time to expiration T:

&emsp;σ<sub>imp</sub> = σ(K, T)

<b>Along the strike dimension (fixed T):</b> You see the smile or skew — the pattern we study in this app.
<br><b>Along the maturity dimension (fixed K):</b> You see the <b>term structure of volatility</b> — IV often differs
for 1-month vs 3-month vs 1-year options on the same underlying.

Practitioners treat the volatility surface as an <b>empirical object</b> that must be calibrated daily from
market prices. It is the single most important input for:
<br>• Pricing exotic options
<br>• Computing Greeks (delta hedging with smile-adjusted IV)
<br>• Risk management (VaR for options portfolios)
<br>• Relative value trading (identifying "cheap" vs "expensive" options)

Hull (Ch. 20.4) emphasizes that the surface must be <b>arbitrage-free</b> — certain monotonicity and
convexity conditions must hold across both K and T dimensions.""",
            },
        ],
        "Section B — The Volatility Smile": [
            {
                "q": "Q5. What is a volatility smile and what shape does it take?",
                "a": """A <b>volatility smile</b> is a U-shaped or parabolic pattern where implied volatility is <b>lowest at ATM</b>
and <b>rises symmetrically</b> for both deep OTM and deep ITM options.

<b>Hull's quadratic approximation:</b>
&emsp;σ<sub>imp</sub>(K/S₀) ≈ σ<sub>ATM</sub> + α·(K/S₀ − 1)² &nbsp;&nbsp;where α > 0

The key feature is <b>symmetry</b> — the left wing (low strikes / OTM puts) and right wing (high strikes /
OTM calls) are approximately mirror images of each other.

<b>Visual signature:</b> Plot σ<sub>imp</sub> vs moneyness (K/S₀). If the curve looks like a "U" or a smile, you have it.

The smile tells you that the market believes extreme moves in <em>either</em> direction are more likely than
what a lognormal distribution would predict — i.e., the implied distribution has <b>fat tails on both sides</b>
(positive excess kurtosis, but near-zero skewness).""",
            },
            {
                "q": "Q6. In which markets do we typically observe a volatility smile?",
                "a": """The classic smile is most prominent in:

<b>1. Foreign Exchange (FX) Options</b> — This is the textbook example. EUR/USD, USD/JPY, GBP/USD options
all exhibit near-symmetric smiles. The reason: currencies don't have an inherent "crash" direction.
A sharp move in USD/JPY could be a yen appreciation (bad for Japanese exporters) or a yen depreciation
(bad for USD holders). Both tails carry risk.

<b>2. Some Commodity Options</b> — Particularly those with symmetric supply/demand shocks (e.g., agricultural
commodities where both droughts and bumper harvests create extreme moves).

<b>3. Short-dated equity options around specific events</b> — Earnings announcements can produce a temporary
smile because the stock could jump up (beat) or down (miss) with roughly equal probability.

<b>FX market convention:</b> Traders quote FX options using the <b>25-delta risk reversal</b> (skew) and
<b>25-delta butterfly</b> (curvature/smile). A large butterfly with small risk reversal = pure smile.

Hull (Ch. 20.1) notes that FX smiles became more pronounced after the 1990s currency crises.""",
            },
            {
                "q": "Q7. What distributional assumption does a smile imply? How does it differ from lognormal?",
                "a": """A volatility smile implies that the market's <b>risk-neutral distribution</b> has:

<b>1. Heavier tails than lognormal</b> (positive excess kurtosis / leptokurtic)
<br><b>2. Roughly symmetric</b> tails (near-zero skewness)

<b>Connecting smile to distribution (Hull Ch. 20.1):</b>
<br>• Deep OTM put is expensive → market assigns higher probability to large downside moves than lognormal
<br>• Deep OTM call is expensive → market assigns higher probability to large upside moves than lognormal
<br>• Both tails are fatter → the implied PDF has more weight in both tails and less in the center

Graphically, if you overlay the implied density on top of a lognormal density:
<br>• The implied PDF has <b>fatter tails</b> on both sides
<br>• The implied PDF has a <b>lower, wider peak</b>
<br>• The total area under both curves = 1 (they're both valid probability distributions)

<b>Models that produce smiles:</b>
<br>• Jump-diffusion (Merton, 1976) — adds random jumps to GBM
<br>• Stochastic volatility (Heston, 1993) — σ itself follows a random process
<br>• Variance Gamma and other Lévy processes""",
            },
            {
                "q": "Q8. How do you extract the implied risk-neutral distribution from option prices?",
                "a": """This is a powerful result from Breeden & Litzenberger (1978):

&emsp;<b>f(K) = e<sup>rT</sup> · ∂²C/∂K²</b>

The second derivative of the call price with respect to strike price, discounted, gives you the
<b>risk-neutral probability density function</b> at that strike.

<b>Intuition:</b> A butterfly spread (long K−ΔK call, short 2×K calls, long K+ΔK call) pays off only if
S<sub>T</sub> is near K. Its price, normalized, gives the probability that S<sub>T</sub> ≈ K.

<b>Practical implementation:</b>
<br>1. Collect call prices C(K) for many strikes at fixed T
<br>2. Fit a smooth curve through C vs K
<br>3. Differentiate twice: f(K) = e<sup>rT</sup> · C″(K)
<br>4. The resulting f(K) is the implied risk-neutral PDF

<b>What smile/skew means for f(K):</b>
<br>• Smile → f(K) has fat tails both sides (leptokurtic)
<br>• Skew → f(K) has a heavier left tail (negatively skewed)
<br>• Flat IV → f(K) is exactly lognormal (the BS case)

This is tested in CFA Level II and FRM Part 1 — know the formula and the intuition.""",
            },
        ],
        "Section C — The Volatility Skew": [
            {
                "q": "Q9. What is a volatility skew (smirk) and how does it differ from a smile?",
                "a": """A <b>volatility skew</b> (also called a "smirk") is an asymmetric pattern where:

&emsp;• OTM puts (low strikes) have <b>significantly higher IV</b> than ATM
<br>&emsp;• OTM calls (high strikes) have <b>slightly higher or similar IV</b> to ATM
<br>&emsp;• The curve slopes <b>downward from left to right</b>

<b>Hull's linear approximation:</b>
&emsp;σ<sub>imp</sub>(K/S₀) ≈ σ<sub>ATM</sub> − β·(K/S₀ − 1) &nbsp;&nbsp;where β > 0

<b>Key difference from smile:</b>
<br>• <b>Smile:</b> Symmetric U-shape — both wings elevated equally
<br>• <b>Skew:</b> Asymmetric — left wing (puts) much steeper than right wing (calls)

The skew dominates in <b>equity and equity index markets</b> worldwide — S&P 500, Euro Stoxx 50,
Nifty 50, FTSE 100, Nikkei 225. It appeared after the 1987 crash and has persisted ever since.

Numerically for Nifty: Put IV at K=23,000 is 19.8% vs ATM Put IV of 12.1% — a spread of
<b>+7.7 percentage points</b>. On the call side, OTM call IV at K=25,500 rises to only 16.5% (call)
and 14.9% (put). The asymmetry is stark.""",
            },
            {
                "q": "Q10. What caused the volatility skew to appear? Why October 1987?",
                "a": """Before October 19, 1987 (<b>Black Monday</b>), the implied volatility surface for equity options was
relatively flat — close to what BS predicted. On that single day:

&emsp;• The Dow Jones fell <b>22.6%</b> — the largest single-day percentage drop in history
<br>&emsp;• S&P 500 futures fell even more, briefly implying negative index values
<br>&emsp;• Portfolio insurance (dynamic hedging) amplified the crash through a feedback loop

<b>The aftermath:</b>
<br>• OTM put prices <b>permanently</b> increased — they never returned to pre-crash levels
<br>• Market makers realized that tail risk was far greater than lognormal implied
<br>• "Crashophobia" (Rubinstein, 1994) became embedded in option pricing

<b>Why it persists:</b>
<br>1. <b>Leverage effect</b> — falling prices → higher debt/equity → higher vol (asymmetric)
<br>2. <b>Demand for protection</b> — institutional investors systematically buy OTM puts as insurance
<br>3. <b>Supply-demand imbalance</b> — fewer natural sellers of OTM puts → prices stay elevated
<br>4. <b>Behavioral memory</b> — 1987, 2000, 2008, 2020 reinforced the fear of left-tail events
<br>5. <b>Regulatory capital</b> — Basel/Solvency requirements incentivize downside hedging""",
            },
            {
                "q": "Q11. What is 'crashophobia' and who coined the term?",
                "a": """<b>Crashophobia</b> was coined by Mark Rubinstein in his seminal 1994 paper. It describes the
persistent overpricing of OTM equity index puts relative to what any standard model
(including jump-diffusion or stochastic volatility) would predict.

<b>Rubinstein's argument:</b>
<br>• After 1987, the implied risk-neutral distribution for equity indices became <b>permanently
  left-skewed</b> — heavier left tail than even models with jumps would justify
<br>• This excess left-tail weight represents a <b>fear premium</b> — investors are willing to
  overpay for crash protection beyond what rational risk-neutral pricing would require
<br>• This is consistent with behavioral finance: <b>loss aversion</b> and <b>probability weighting</b>
  (overweighting rare catastrophic events, as in Prospect Theory)

<b>Empirical evidence:</b>
<br>• OTM puts on the S&P 500 have been systematically "overpriced" relative to realized
  outcomes — selling them (put-writing strategies) has generated positive alpha historically
<br>• The VIX (implied vol) consistently exceeds realized vol — the "variance risk premium"
<br>• This pattern holds globally: Nifty, FTSE, DAX, Nikkei all exhibit similar skew

<b>Exam note (CFA/FRM):</b> Crashophobia explains why the skew persists even in calm markets —
it's structural, not just a reaction to recent events.""",
            },
            {
                "q": "Q12. What distributional assumption does the equity skew imply?",
                "a": """The equity volatility skew implies that the market's risk-neutral distribution is:

<b>1. Negatively skewed</b> — heavier left tail (more probability mass for large drops)
<br><b>2. Leptokurtic</b> — fatter tails overall than lognormal (excess kurtosis > 0)
<br><b>3. Left tail >> Right tail</b> — the asymmetry is the defining feature

<b>Comparison with lognormal:</b>
<br>• Lognormal: already slightly right-skewed (prices can't go below zero but can go to infinity)
<br>• Implied distribution: <b>much more</b> left-skewed than lognormal — the market "flips" the skew

<b>Quantitative measures:</b>
<br>• <b>Skew premium</b> = IV(25-delta put) − IV(25-delta call) — measures asymmetry
<br>• <b>Risk reversal</b> = same concept, standard quoting convention
<br>• For Nifty: typical skew premium is 4-8 percentage points
<br>• For S&P 500: typically 5-10 percentage points

<b>Why negative skew for equities but not FX?</b>
<br>• Equities have a "floor fear" — companies can go bankrupt, indices can crash
<br>• Currencies are relative prices — USD weakness = EUR strength (symmetric)
<br>• The leverage effect is equity-specific (debt/equity ratio changes with price)""",
            },
        ],
        "Section D — Nifty 50 Specifics & Indian Market": [
            {
                "q": "Q13. Does Nifty 50 show a smile, a skew, or both?",
                "a": """Nifty 50 options show a <b>clear volatility skew</b>, consistent with global equity index behavior.

<b>Evidence from our data (Spot = ₹24,250):</b>
<br>• Put IV at K=23,000 (5.2% OTM): <b>19.8%</b>
<br>• Put IV at ATM K=24,250: <b>12.1%</b>
<br>• Put IV at K=25,500 (5.2% OTM call): <b>14.9%</b>

The <b>put skew</b> (downside) is 7.7pp above ATM, while the upside is only 2.8pp — classic asymmetry.

<b>However</b>, call IV also rises at high strikes, creating a slight "smirk" rather than a pure monotonic
decline. This is common — the skew is the dominant feature, but there's a mild uptick in the
right wing, especially for:
<br>• Short-dated options around events (budget, RBI policy, earnings season)
<br>• Periods of strong bullish momentum when call demand spikes

<b>India-specific factors amplifying the skew:</b>
<br>• Massive retail F&O participation (SEBI data: 90%+ of individual traders lose money)
<br>• Institutional demand for portfolio insurance (FIIs hedging India exposure)
<br>• Higher event risk (elections, RBI surprises, global oil shocks for oil-importing India)
<br>• SEBI's margin and lot-size regulations affecting supply-demand dynamics""",
            },
            {
                "q": "Q14. How does India VIX relate to the implied volatility surface?",
                "a": """<b>India VIX</b> is the Indian equivalent of the CBOE VIX. It measures the market's expectation of
30-day volatility for Nifty 50, computed from near- and next-month Nifty option prices.

<b>Methodology (model-free, following CBOE):</b>
<br>• Uses a wide range of OTM put and OTM call prices
<br>• Weighted by 1/K² — gives more weight to lower strikes (where skew lives)
<br>• Because of this weighting, India VIX <b>captures the skew effect</b>
<br>• A steeper skew → higher VIX, even if ATM IV is unchanged

<b>Key relationships:</b>
<br>• India VIX ≈ weighted average of IVs across the smile/skew, not just ATM IV
<br>• VIX > ATM IV always (because OTM puts with high IV get significant weight)
<br>• VIX typically trades at a <b>premium to realized vol</b> (variance risk premium)
<br>• Pre-event (budget, election): VIX spikes → skew steepens → OTM puts get very expensive
<br>• Post-event: VIX crushes → skew flattens → "vol sellers" profit

<b>Typical India VIX range:</b> 10-15 (calm), 15-25 (elevated), 25+ (crisis/extreme fear)""",
            },
            {
                "q": "Q15. How does SEBI's F&O regulation affect the skew in Indian markets?",
                "a": """SEBI has been actively tightening F&O market regulations, which directly impacts the volatility
surface structure:

<b>1. Increased lot sizes and margin requirements (2024-25):</b>
<br>• Higher margins for short OTM options → fewer willing sellers → OTM puts get more expensive → steeper skew
<br>• Reduced retail speculation → more informed/institutional pricing

<b>2. Weekly expiry restrictions:</b>
<br>• Only one weekly expiry per exchange (down from multiple indices)
<br>• Concentrated liquidity → more efficient price discovery → cleaner skew pattern
<br>• Less "theta decay farming" by retail → reduced artificial supply of OTM options

<b>3. Upfront premium collection for option buyers:</b>
<br>• Ensures genuine demand → reduces speculative noise in IV readings

<b>4. Position limits and surveillance:</b>
<br>• Large positions in deep OTM options get flagged → more orderly skew

<b>Net effect:</b> Indian option markets are becoming more institutional in character, and the skew
is likely to become <b>more stable and structurally similar</b> to developed markets like the S&P 500.
The "vol smile" artifacts from extreme retail speculation are being gradually eliminated.

<b>For students:</b> This is a great example of how market microstructure affects the volatility surface —
a topic that bridges derivatives (Hull) and market risk (FRM).""",
            },
        ],
        "Section E — Trading, Risk Management & Greeks": [
            {
                "q": "Q16. How does the skew affect delta hedging?",
                "a": """When the volatility surface is not flat, delta hedging becomes more complex because the
"correct" delta depends on which σ you use:

<b>1. BS Delta (using single σ):</b>
&emsp;Δ = N(d₁) where d₁ uses a single flat σ
&emsp;Problem: Ignores the fact that σ changes as S moves and K/S₀ changes

<b>2. "Sticky Strike" Delta:</b>
&emsp;Assumes each strike K keeps its own fixed IV as spot moves
&emsp;Δ<sub>sticky-K</sub> = ∂C/∂S with σ(K) held constant
&emsp;Common assumption for equity index options

<b>3. "Sticky Delta" (Sticky Moneyness) Delta:</b>
&emsp;Assumes the IV at a given moneyness level (K/S) stays constant as S moves
&emsp;Δ<sub>sticky-Δ</sub> = ∂C/∂S + (∂C/∂σ)·(∂σ/∂S)
&emsp;More common for FX options

<b>The practical difference:</b>
<br>• For OTM puts in a skew environment, sticky-strike delta is typically <b>less negative</b> than
  BS delta — you need fewer shares to hedge
<br>• The error can be 5-15% of delta for deep OTM options
<br>• Getting this wrong leads to P&L leakage over time ("vega-delta cross effect")

<b>Hull (Ch. 20.6):</b> "The smile affects the Greek letters computed from the BS model. Practitioners
  often adjust the Greeks to reflect the volatility smile."
""",
            },
            {
                "q": "Q17. What is a risk reversal and how does it measure the skew?",
                "a": """A <b>risk reversal</b> is a strategy that directly trades the skew:

&emsp;<b>Long risk reversal</b> = Buy OTM call + Sell OTM put (same delta, e.g., 25-delta)
<br>&emsp;<b>Short risk reversal</b> = Sell OTM call + Buy OTM put

<b>Risk reversal as a skew measure:</b>
&emsp;RR<sub>25Δ</sub> = σ<sub>imp</sub>(25Δ call) − σ<sub>imp</sub>(25Δ put)

<br>• If RR < 0 → puts are more expensive → <b>negative skew</b> (equity-style)
<br>• If RR ≈ 0 → symmetric → <b>pure smile</b>
<br>• If RR > 0 → calls are more expensive → <b>positive skew</b> (rare)

<b>For Nifty 50:</b> The risk reversal is typically <b>negative</b> (−4 to −8 vol points), confirming
the persistent equity skew. It widens during sell-offs and narrows during calm bullish phases.

<b>Trading applications:</b>
<br>• Skew traders go long/short risk reversals to bet on changes in skew steepness
<br>• Collar strategies (long put + short call) are <b>cheap</b> when skew is steep (put expensive but
  call cheap) — this is why portfolio managers use collars in skew-rich environments
<br>• Risk reversal quotes are the standard way FX desks communicate skew""",
            },
            {
                "q": "Q18. What is a butterfly spread and how does it measure the smile?",
                "a": """A <b>butterfly spread</b> isolates the curvature (convexity) of the volatility surface:

&emsp;<b>Long butterfly</b> = Buy 1× K₁ call + Sell 2× K₂ call + Buy 1× K₃ call
&emsp;where K₁ < K₂ < K₃ and K₂ = (K₁+K₃)/2

<b>Butterfly as a smile measure (25-delta):</b>
&emsp;BF<sub>25Δ</sub> = ½ × [σ<sub>imp</sub>(25Δ call) + σ<sub>imp</sub>(25Δ put)] − σ<sub>ATM</sub>

<br>• If BF > 0 → wings elevated above ATM → <b>smile exists</b> (positive curvature)
<br>• If BF ≈ 0 → flat wings → no smile
<br>• BF is always ≥ 0 in practice (no arbitrage requires convexity in the call price function)

<b>Relationship between RR and BF:</b>
<br>• <b>RR</b> measures <b>tilt/asymmetry</b> → skew component
<br>• <b>BF</b> measures <b>curvature/wings</b> → smile component
<br>• Together they fully characterize the 3-point smile (25Δ put, ATM, 25Δ call)

<b>For a pure smile (FX):</b> Large BF, small |RR|
<br><b>For a pure skew (equities):</b> Large |RR|, moderate BF
<br><b>Nifty:</b> Both BF and |RR| are significant — skew dominates but curvature exists too""",
            },
            {
                "q": "Q19. How does vega exposure change across the smile?",
                "a": """<b>Vega</b> (sensitivity of option price to a 1pp change in IV) varies across the smile:

&emsp;ν = S₀·√T·N′(d₁)

<b>Key relationships:</b>
<br>• Vega is <b>highest at ATM</b> (N′(d₁) peaks when d₁ ≈ 0)
<br>• Vega <b>declines</b> for deep ITM and deep OTM options
<br>• But in a skew environment, OTM puts have higher IV → their <b>dollar vega</b> is amplified

<b>Portfolio implications:</b>
<br>1. A portfolio of OTM puts is <b>short skew</b> — profits if skew flattens
<br>2. Market makers who sell OTM puts are <b>short vega AND short skew</b> — double exposure
<br>3. During a crash: IV spikes AND skew steepens → OTM put sellers face <b>convex losses</b>
<br>4. This is why 2008, 2020 produced massive losses for systematic put-selling strategies

<b>Vega-weighted skew exposure:</b>
<br>The "vega-weighted" skew is what matters for P&L, not just the IV difference. A 10pp IV
increase on an option with ν = 50 moves the price by ₹500 per lot. Traders track vega exposure
<em>by strike</em>, not just total portfolio vega.""",
            },
        ],
        "Section F — Models & Advanced Topics": [
            {
                "q": "Q20. Which models produce a volatility smile? Which produce a skew?",
                "a": """<b>Models that generate a SMILE (symmetric):</b>

<b>1. Jump-Diffusion (Merton, 1976):</b>
&emsp;dS/S = (μ−λk̄)dt + σdW + J·dN(λ)
<br>&emsp;Where J = random jump size, dN = Poisson process
<br>&emsp;If jumps are symmetric → smile. If jumps are asymmetric → can produce skew too.

<b>2. Stochastic Volatility — Heston (1993):</b>
&emsp;dS/S = μdt + √v·dW₁
<br>&emsp;dv = κ(θ−v)dt + ξ√v·dW₂
<br>&emsp;corr(dW₁, dW₂) = ρ
<br>&emsp;If ρ = 0 → pure smile. If ρ < 0 → skew (this is the equity case!).

<b>3. Variance Gamma (Madan, Carr, Chang, 1998):</b>
&emsp;Subordinated Brownian motion — can produce both smile and skew depending on parameters.

<b>Models that generate a SKEW:</b>
<br>• Heston with ρ < 0 (negative correlation between returns and vol)
<br>• CEV model (σ(S) = σ₀·S<sup>β−1</sup>, β < 1 → vol rises as S falls)
<br>• SABR model (popular in fixed income: σ follows its own stochastic process)
<br>• Local volatility (Dupire, 1994) — fitted to exactly reproduce any observed surface

<b>Exam tip:</b> Hull Ch. 20 focuses on <em>why</em> the smile/skew exists. Ch. 27 covers stochastic vol models.
For FRM, know Heston and SABR. For CFA, know the intuition behind smile/skew patterns.""",
            },
            {
                "q": "Q21. What is the Dupire local volatility model?",
                "a": """Dupire (1994) showed that you can find a <b>deterministic</b> volatility function σ<sub>loc</sub>(S,t)
that exactly reproduces all observed option prices (and hence the entire implied vol surface).

<b>Dupire's formula:</b>
&emsp;σ²<sub>loc</sub>(K,T) = 2 × [∂C/∂T + rK·∂C/∂K] / [K²·∂²C/∂K²]

This is derived from the Fokker-Planck (forward Kolmogorov) equation.

<b>Key properties:</b>
<br>• It's a <b>one-factor model</b> — only one source of randomness (dW)
<br>• It perfectly fits today's smile/skew by construction
<br>• σ<sub>loc</sub>(S,t) varies with both stock price and time — it's a surface, not a number
<br>• The local vol surface is <b>not the same</b> as the implied vol surface — local vol is typically
  roughly twice as curved

<b>Limitations:</b>
<br>• It predicts future smile dynamics poorly — the smile "flattens too quickly" over time
<br>• It doesn't capture <b>stochastic volatility</b> — vol changes are deterministic given S
<br>• Forward-starting options and cliquets are mispriced
<br>• Exotic option hedging can be unreliable

<b>In practice:</b> Dupire is used for initial calibration and as a baseline. Traders then layer
stochastic vol (Heston, SABR) or jump-diffusion on top for realistic dynamics.""",
            },
            {
                "q": "Q22. What is the SABR model and why is it important?",
                "a": """<b>SABR</b> (Stochastic Alpha Beta Rho) was introduced by Hagan et al. (2002) and is the industry
standard for modeling the smile in interest rate and FX options.

<b>Model dynamics:</b>
&emsp;dF = α·F<sup>β</sup>·dW₁ &nbsp;&nbsp;(forward rate)
<br>&emsp;dα = ν·α·dW₂ &nbsp;&nbsp;(stochastic volatility)
<br>&emsp;corr(dW₁, dW₂) = ρ

<b>Four parameters:</b>
<br>• <b>α</b> — initial volatility level (ATM vol)
<br>• <b>β</b> — elasticity parameter (0 = normal model, 1 = lognormal model)
<br>• <b>ρ</b> — correlation between F and α (controls skew: ρ < 0 → negative skew)
<br>• <b>ν</b> — vol-of-vol (controls curvature/smile wings)

<b>Hagan's approximation</b> gives a closed-form expression for σ<sub>imp</sub>(K) — making calibration fast.

<b>Why traders love it:</b>
<br>• Intuitive parameters: each one controls a specific feature of the smile
<br>• Fast calibration to market quotes (swaptions, caps/floors, FX)
<br>• Handles both smile and skew through ρ
<br>• Backbone parameter β can be fixed (reducing to 3-param calibration)

<b>Used extensively in:</b> swaption pricing, cap/floor trading, CMS spread options, FX volatility.""",
            },
        ],
        "Section G — CFA / FRM / MBA Exam Focus": [
            {
                "q": "Q23. [CFA Level II] If an equity index shows a volatility skew, what does this imply about the risk-neutral distribution vs lognormal?",
                "a": """<b>Model answer:</b>

The volatility skew for equity index options implies that the market's risk-neutral probability
distribution differs from the lognormal distribution assumed by Black-Scholes in two key ways:

<b>1. Negative skewness:</b> The risk-neutral distribution has a heavier left tail than the lognormal.
This means the market assigns a higher probability to large downside moves than Black-Scholes
would predict. This is evidenced by elevated implied volatilities for OTM puts (low strikes).

<b>2. Excess kurtosis (fat tails):</b> Both tails are somewhat heavier than lognormal, though the
effect is more pronounced on the left. This means extreme events in either direction are priced
as more likely than the lognormal assumption.

<b>Economic rationale:</b>
<br>• The leverage effect: as equity prices fall, financial leverage increases, making the firm
  riskier and increasing volatility — this creates an asymmetric vol-price relationship
<br>• Crashophobia: investors' demand for downside protection drives up OTM put prices
<br>• The skew has persisted since the 1987 crash and is observed globally

<b>Practical implication:</b> Using a single σ to price all strikes will <b>underprice</b> OTM puts
and <b>overprice</b> ATM options relative to the market.""",
            },
            {
                "q": "Q24. [FRM Part 1] Explain the difference between implied volatility and local volatility. Why might a risk manager care?",
                "a": """<b>Model answer:</b>

<b>Implied Volatility σ<sub>imp</sub>(K,T):</b>
<br>• The constant σ that, when inserted into Black-Scholes, reproduces the market price of a specific
  option with strike K and expiry T
<br>• It is a <b>per-option</b> quantity — each (K,T) pair has its own σ<sub>imp</sub>
<br>• It is a <b>model-dependent</b> concept (depends on BS framework)
<br>• It aggregates all non-BS effects (jumps, stochastic vol, skewness) into one number

<b>Local Volatility σ<sub>loc</sub>(S,t):</b>
<br>• The instantaneous volatility of the underlying at price level S and time t
<br>• Derived from the entire implied vol surface using Dupire's formula
<br>• It varies with both S and t — it's a <b>function</b>, not a single number
<br>• It is the unique diffusion coefficient that reproduces all vanilla option prices simultaneously

<b>Why a risk manager cares:</b>
<br>1. <b>VaR computation:</b> Using flat BS vol underestimates tail risk. The skew tells you the market
   prices in higher crash probability → VaR should reflect this
<br>2. <b>Stress testing:</b> In a sell-off, IV increases AND skew steepens → double hit to OTM put sellers
<br>3. <b>Model risk:</b> Local vol models may underestimate forward-starting option risk (smile dynamics)
<br>4. <b>Greeks accuracy:</b> Delta and gamma computed with flat vol can be materially wrong for OTM options""",
            },
            {
                "q": "Q25. [Practice] An ATM Nifty call has IV = 12%. An OTM put at K = 23,000 has IV = 19.8%. If you use 12% to price the put, by roughly how much do you underprice it?",
                "a": """<b>Setup:</b>
<br>• S₀ = ₹24,250, K = ₹23,000, ATM IV = 12%, True IV = 19.8%
<br>• Let's assume T = 30 days (0.082 years), r = 6.5%

<b>Approximate using vega:</b>
<br>The vega of an OTM put at this moneyness (K/S₀ = 0.948) is approximately ₹15-20 per 1% IV change
per lot (assuming lot size 25).

&emsp;ΔIV = 19.8% − 12.0% = <b>7.8 percentage points</b>
<br>&emsp;Approximate mispricing ≈ 7.8 × ₹17 ≈ <b>₹133 per lot</b> (rough estimate)

<b>Using Black-Scholes directly:</b>
<br>&emsp;Put price at σ = 12.0%: ≈ ₹18 per share → ₹450 per lot
<br>&emsp;Put price at σ = 19.8%: ≈ ₹98 per share → ₹2,450 per lot

<b>Underpricing: roughly ₹2,000 per lot — the put is 5× more expensive at the correct IV!</b>

<b>Key lesson:</b> Using a flat ATM vol to price OTM puts can lead to massive underpricing.
This is why the volatility surface exists — practitioners MUST use strike-specific IV.
Banks that ignored the skew in their risk models learned this lesson painfully in 2008.

<b>Exam tip:</b> You won't need exact calculations. Know the direction and magnitude of the error —
flat vol <b>always</b> underprices OTM puts in a skew environment.""",
            },
        ],
    }

    # ── Section title ──
    st.html(f"""
    <div style="
        font-family:'Playfair Display',serif;
        color:{GOLD}; -webkit-text-fill-color:{GOLD};
        font-size:1.35rem;
        margin-bottom:2px;
        user-select:none;
    ">🎓 Comprehensive Q&A — Volatility Smile & Skew</div>
    <div style="
        font-family:'Source Sans Pro',sans-serif;
        color:{MUTED}; -webkit-text-fill-color:{MUTED};
        font-size:0.86rem;
        margin-bottom:18px;
        user-select:none;
    ">25 questions spanning foundations, trading, models, and exam prep &nbsp;|&nbsp; Hull Ch. 20 &nbsp;|&nbsp; CFA / FRM / MBA</div>
    """)

    # ── Progress tracker ──
    if "qa_revealed" not in st.session_state:
        st.session_state.qa_revealed = set()

    total_q = sum(len(qas) for qas in QA_SECTIONS.values())
    revealed_count = len(st.session_state.qa_revealed)

    st.html(f"""
    <div style="
        background:rgba(0,51,102,0.4);
        border:1px solid rgba(255,215,0,0.15);
        border-radius:10px;
        padding:14px 20px;
        margin-bottom:18px;
        display:flex;
        justify-content:space-between;
        align-items:center;
        user-select:none;
    ">
        <div style="font-family:'Source Sans Pro',sans-serif; color:{TEXT}; -webkit-text-fill-color:{TEXT}; font-size:0.9rem;">
            Progress: <b style="color:{GOLD};-webkit-text-fill-color:{GOLD};">{revealed_count}</b> / {total_q} answers revealed
        </div>
        <div style="
            background:rgba(10,22,40,0.6);
            border-radius:6px;
            width:200px;
            height:10px;
            overflow:hidden;
        ">
            <div style="
                background:{GOLD};
                height:100%;
                width:{revealed_count/total_q*100:.0f}%;
                border-radius:6px;
                transition:width 0.3s;
            "></div>
        </div>
    </div>
    """)

    # ── Render sections ──
    q_index = 0
    for section_title, questions in QA_SECTIONS.items():
        st.html(f"""
        <div style="
            font-family:'Playfair Display',serif;
            color:{LIGHT_BLUE}; -webkit-text-fill-color:{LIGHT_BLUE};
            font-size:1.05rem;
            margin:22px 0 10px;
            padding-bottom:6px;
            border-bottom:1px solid rgba(173,216,230,0.2);
            user-select:none;
        ">{section_title}</div>
        """)

        for qa in questions:
            q_key = f"qa_{q_index}"

            # Question box (always visible)
            st.html(f"""
            <div style="
                background:rgba(0,51,102,0.35);
                border:1px solid rgba(255,215,0,0.12);
                border-left:3px solid {GOLD};
                border-radius:0 8px 8px 0;
                padding:12px 16px;
                margin:8px 0 4px;
                user-select:none;
            ">
                <div style="
                    font-family:'Source Sans Pro',sans-serif;
                    font-size:0.92rem;
                    font-weight:700;
                    color:{GOLD}; -webkit-text-fill-color:{GOLD};
                    line-height:1.5;
                ">{qa['q']}</div>
            </div>
            """)

            # Toggle button
            if st.button(
                "Hide Answer" if q_key in st.session_state.qa_revealed else "💡 Reveal Answer",
                key=q_key,
                use_container_width=True,
            ):
                if q_key in st.session_state.qa_revealed:
                    st.session_state.qa_revealed.discard(q_key)
                else:
                    st.session_state.qa_revealed.add(q_key)
                st.rerun()

            # Answer box (conditionally visible)
            if q_key in st.session_state.qa_revealed:
                st.html(f"""
                <div style="
                    background:rgba(17,34,64,0.85);
                    border:1px solid rgba(173,216,230,0.12);
                    border-radius:10px;
                    padding:18px 22px;
                    margin:4px 0 14px;
                    user-select:none;
                ">
                    <div style="
                        font-family:'Source Sans Pro',sans-serif;
                        font-size:0.86rem;
                        line-height:1.7;
                        color:{TEXT}; -webkit-text-fill-color:{TEXT};
                    ">{qa['a']}</div>
                </div>
                """)

            q_index += 1

    # ── Bottom summary ──
    voiceover_box(
        "This Q&A section covers the full breadth of volatility smile and skew topics as tested in "
        "CFA Level II (Derivatives), FRM Part 1 (Market Risk / Valuation & Risk Models), and MBA "
        "Derivatives courses. Each answer is designed to be self-contained — you can use any single "
        "answer as a class handout or exam revision note. For deeper exploration, see Hull Ch. 20 "
        "(Volatility Smiles), Ch. 27 (Martingales & Measures), and Natenberg Ch. 18 (Volatility Skew)."
    )

    hull_box(
        "Recommended Reading Sequence",
        f"<span style='color:{LIGHT_BLUE};-webkit-text-fill-color:{LIGHT_BLUE};'>1.</span> "
        "Hull, <i>Options, Futures & Other Derivatives</i>, Ch. 20: Volatility Smiles<br>"
        f"<span style='color:{LIGHT_BLUE};-webkit-text-fill-color:{LIGHT_BLUE};'>2.</span> "
        "Natenberg, <i>Option Volatility & Pricing</i>, Ch. 18: Volatility Skew<br>"
        f"<span style='color:{LIGHT_BLUE};-webkit-text-fill-color:{LIGHT_BLUE};'>3.</span> "
        "Gatheral, <i>The Volatility Surface</i> — for advanced practitioners<br>"
        f"<span style='color:{LIGHT_BLUE};-webkit-text-fill-color:{LIGHT_BLUE};'>4.</span> "
        "Rubinstein (1994), \"Implied Binomial Trees\" — the crashophobia paper<br>"
        f"<span style='color:{LIGHT_BLUE};-webkit-text-fill-color:{LIGHT_BLUE};'>5.</span> "
        "Dupire (1994), \"Pricing with a Smile\" — local volatility foundation"
    )
mountain_footer()
