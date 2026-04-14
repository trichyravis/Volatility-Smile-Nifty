
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
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
        background: rgba(0,51,102,0.4);
        border-radius: 10px;
        padding: 6px;
    }}
    .stTabs [data-baseweb="tab"] {{
        color: {MUTED};
        font-family: 'Source Sans Pro', sans-serif;
        font-weight: 600;
        font-size: 0.88rem;
        border-radius: 8px;
        padding: 8px 18px;
    }}
    .stTabs [aria-selected="true"] {{
        background: {GOLD} !important;
        color: {BLUE} !important;
    }}
    .stTabs [data-baseweb="tab-panel"] {{
        padding-top: 1rem;
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

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📖 Introduction",
    "😊 Volatility Smile",
    "📉 Volatility Skew",
    "📊 Nifty Option Chain",
    "🔀 Smile vs Skew Overlay",
    "🎛 Parameter Explorer",
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


# ── FOOTER ────────────────────────────────────────────────
mountain_footer()
