# Yinxin Huang Data Portfolio

Personal portfolio site for Yinxin Huang, built around World Bank data analysis projects.

## What This Site Shows

- API-based data collection from World Bank Open Data
- Python analysis with pandas, seaborn, and matplotlib
- Country-year cleaning, derived metrics, correlations, volatility, and composite scores
- Multi-panel dashboard-style visual storytelling
- Case study writing for non-technical readers
- Personal profile pages with Yinxin's own photos

## Portfolio Case Studies

The project section currently includes three World Bank analyses:

1. GDP Growth Quality and Resilience
2. Digital Development and Human Outcomes
3. Prosperity Context Beyond Headline GDP

Chart assets are stored in `public/media/`, and the supporting analysis data is stored in `public/data/world-bank-analysis.json`.

## Local Development

```bash
npm install
npm run build:analysis
npm run dev
```

The local preview runs at `http://localhost:4321`.

## Build

```bash
npm run build
```

## Data Source

The analysis uses [World Bank Open Data](https://data.worldbank.org/). The dataset is public; the portfolio questions, chart design, written summaries, and page packaging are customized for Yinxin Huang.
