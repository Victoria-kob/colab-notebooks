"""
Create an interactive Gapminder-style data dashboard from V-Dem data.
Generates a self-contained HTML webpage with:
  - Animated bubble chart (GDP per capita vs Life Expectancy, sized by population)
  - Year slider and play/pause controls
  - Distributions of life expectancy and GDP per capita for the selected year
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import html as html_mod
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "Lecture_4" / "Data_Raw" / "VDem" / "V-Dem-CY-Full+Others-v15.csv"
OUTPUT_HTML = Path(__file__).resolve().parent / "gapminder_dashboard.html"

# ── Load & wrangle ──────────────────────────────────────────────────────────
print("Loading data...")
df = pd.read_csv(DATA_PATH, usecols=["country_name", "year", "e_pelifeex", "e_gdppc", "e_pop"])

df = df.rename(columns={
    "e_pelifeex": "lifeExp",
    "e_gdppc": "gdpPercap",
    "e_pop": "pop",
})

df = df.dropna(subset=["gdpPercap", "lifeExp", "pop"])

# ── Build animated bubble chart ─────────────────────────────────────────────
print("Building bubble chart...")
fig_bubble = px.scatter(
    df.sort_values("year"),
    x="gdpPercap",
    y="lifeExp",
    size="pop",
    hover_name="country_name",
    hover_data={"gdpPercap": ":.1f", "lifeExp": ":.1f", "pop": ":.0f"},
    animation_frame="year",
    title="Life Expectancy vs GDP per Capita",
    labels={
        "gdpPercap": "GDP per Capita (thousand USD)",
        "lifeExp": "Life Expectancy (years)",
        "pop": "Population (thousands)",
        "year": "Year",
    },
    size_max=55,
    opacity=0.65,
    template="plotly_white",
    log_x=True,
)

fig_bubble.update_layout(
    xaxis=dict(
        title="GDP per Capita (thousand USD, log scale)",
        range=[
            pd.np.log10(df["gdpPercap"].min() * 0.8) if hasattr(pd, "np") else __import__("numpy").log10(df["gdpPercap"].min() * 0.8),
            pd.np.log10(df["gdpPercap"].max() * 1.2) if hasattr(pd, "np") else __import__("numpy").log10(df["gdpPercap"].max() * 1.2),
        ],
    ),
    yaxis=dict(
        title="Life Expectancy (years)",
        range=[df["lifeExp"].min() * 0.85, df["lifeExp"].max() * 1.05],
    ),
    showlegend=False,
    margin=dict(t=80, b=40),
    height=600,
)

fig_bubble.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 250
fig_bubble.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 150

bubble_html = fig_bubble.to_html(full_html=False, include_plotlyjs=False)

# ── Build static 2019 snapshot charts ───────────────────────────────────────
print("Building snapshot charts...")
df_2019 = df[df["year"] == 2019]

# Life expectancy histogram
fig_hist_life = px.histogram(
    df_2019, x="lifeExp", nbins=25, color_discrete_sequence=["#4e79a7"],
    title="Distribution of Life Expectancy (2019)",
    labels={"lifeExp": "Life Expectancy (years)"},
    template="plotly_white",
)
fig_hist_life.update_layout(
    yaxis_title="Count",
    margin=dict(t=50, b=40, l=50, r=20),
    height=350,
    bargap=0.05,
)
hist_life_html = fig_hist_life.to_html(full_html=False, include_plotlyjs=False)

# GDP per capita histogram
fig_hist_gdp = px.histogram(
    df_2019, x="gdpPercap", nbins=25, color_discrete_sequence=["#f28e2b"],
    title="Distribution of GDP per Capita (2019)",
    labels={"gdpPercap": "GDP per Capita (thousand USD)"},
    template="plotly_white",
)
fig_hist_gdp.update_layout(
    yaxis_title="Count",
    margin=dict(t=50, b=40, l=50, r=20),
    height=350,
    bargap=0.05,
)
hist_gdp_html = fig_hist_gdp.to_html(full_html=False, include_plotlyjs=False)

# ── Summary stats table ─────────────────────────────────────────────────────
years_available = sorted(df["year"].unique())
n_countries = df["country_name"].nunique()
year_range = f"{years_available[0]}–{years_available[-1]}"

# ── Assemble HTML ────────────────────────────────────────────────────────────
print("Assembling dashboard HTML...")

dashboard_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Gapminder Dashboard – V-Dem Data</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>
<style>
  :root {{
    --bg: #f7f8fa;
    --card-bg: #ffffff;
    --accent: #4e79a7;
    --text: #2c3e50;
    --muted: #7f8c8d;
  }}
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
                 Ubuntu, Cantarell, 'Helvetica Neue', sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.6;
  }}
  header {{
    background: linear-gradient(135deg, var(--accent), #2c5f8a);
    color: white;
    padding: 2rem 1rem;
    text-align: center;
  }}
  header h1 {{ font-size: 2rem; font-weight: 700; }}
  header p {{ opacity: 0.85; margin-top: 0.3rem; font-size: 1rem; }}
  .stats-bar {{
    display: flex;
    justify-content: center;
    gap: 2rem;
    padding: 1rem;
    background: var(--card-bg);
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
  }}
  .stat {{ text-align: center; }}
  .stat .num {{ font-size: 1.5rem; font-weight: 700; color: var(--accent); }}
  .stat .label {{ font-size: 0.8rem; color: var(--muted); text-transform: uppercase; }}
  .container {{ max-width: 1200px; margin: 1.5rem auto; padding: 0 1rem; }}
  .card {{
    background: var(--card-bg);
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    padding: 1rem;
    margin-bottom: 1.5rem;
  }}
  .row {{ display: flex; gap: 1.5rem; }}
  .row > .card {{ flex: 1; min-width: 0; }}
  footer {{
    text-align: center;
    padding: 1.5rem;
    color: var(--muted);
    font-size: 0.85rem;
  }}
  @media (max-width: 768px) {{
    .row {{ flex-direction: column; }}
  }}
</style>
</head>
<body>

<header>
  <h1>Gapminder-Style Data Dashboard</h1>
  <p>Exploring GDP, Life Expectancy &amp; Population using V-Dem v15 data</p>
</header>

<div class="stats-bar">
  <div class="stat">
    <div class="num">{n_countries}</div>
    <div class="label">Countries</div>
  </div>
  <div class="stat">
    <div class="num">{year_range}</div>
    <div class="label">Year Range</div>
  </div>
  <div class="stat">
    <div class="num">{len(df):,}</div>
    <div class="label">Observations</div>
  </div>
</div>

<div class="container">

  <!-- Main animated bubble chart -->
  <div class="card">
    {bubble_html}
  </div>

  <!-- Distribution row -->
  <div class="row">
    <div class="card">
      {hist_life_html}
    </div>
    <div class="card">
      {hist_gdp_html}
    </div>
  </div>

  <!-- Methodology note -->
  <div class="card" style="font-size:0.9rem; color: var(--muted);">
    <strong>Data source:</strong> Varieties of Democracy (V-Dem) v15 dataset.<br>
    <strong>Variables:</strong> <code>e_gdppc</code> (GDP per capita, thousand USD),
    <code>e_pelifeex</code> (life expectancy at birth, years),
    <code>e_pop</code> (population in thousands).
  </div>

</div>

<footer>
  POLI3148 Data Science in Politics &amp; Public Policy – HKU &middot;
  Dashboard generated from V-Dem v15
</footer>

</body>
</html>
"""

OUTPUT_HTML.write_text(dashboard_html, encoding="utf-8")
print(f"Dashboard saved to {OUTPUT_HTML}")
