from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
import seaborn as sns


ROOT = Path(__file__).resolve().parents[1]
OUT_DATA = ROOT / "public" / "data"
OUT_MEDIA = ROOT / "public" / "media"

COUNTRIES = {
    "USA": "United States",
    "CHN": "China",
    "IND": "India",
    "DEU": "Germany",
    "GBR": "United Kingdom",
    "BRA": "Brazil",
    "ZAF": "South Africa",
}

INDICATORS = {
    "gdp": "NY.GDP.MKTP.CD",
    "gdp_per_capita": "NY.GDP.PCAP.CD",
    "population": "SP.POP.TOTL",
    "internet": "IT.NET.USER.ZS",
    "life_expectancy": "SP.DYN.LE00.IN",
    "health_spend_pc": "SH.XPD.CHEX.PC.CD",
    "urban_population": "SP.URB.TOTL.IN.ZS",
}

YEARS = range(2000, 2024)

PALETTE = {
    "USA": "#2563eb",
    "CHN": "#be3455",
    "IND": "#d97706",
    "DEU": "#0f766e",
    "GBR": "#6b8f3a",
    "BRA": "#7c3aed",
    "ZAF": "#334155",
}


def fetch_indicator(indicator_key: str, indicator_code: str) -> pd.DataFrame:
    country_list = ";".join(COUNTRIES.keys())
    url = (
        f"https://api.worldbank.org/v2/country/{country_list}/indicator/"
        f"{indicator_code}?format=json&date=2000:2023&per_page=20000"
    )
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    payload = response.json()
    rows = payload[1] if len(payload) > 1 and payload[1] else []
    if not rows:
        return pd.DataFrame(columns=["country_code", "country", "year", indicator_key])
    frame = pd.DataFrame(
        [
            {
                "country_code": row.get("countryiso3code"),
                "country": row["country"]["value"],
                "year": int(row["date"]),
                indicator_key: row["value"],
            }
            for row in rows
            if row.get("value") is not None
        ]
    )
    return frame


def build_panel() -> pd.DataFrame:
    base = pd.MultiIndex.from_product(
        [COUNTRIES.keys(), YEARS], names=["country_code", "year"]
    ).to_frame(index=False)
    base["country"] = base["country_code"].map(COUNTRIES)
    panel = base
    for key, code in INDICATORS.items():
        data = fetch_indicator(key, code)[["country_code", "year", key]]
        panel = panel.merge(data, on=["country_code", "year"], how="left")
    return panel.sort_values(["country_code", "year"]).reset_index(drop=True)


def latest_rows(panel: pd.DataFrame) -> pd.DataFrame:
    values = []
    for code, group in panel.groupby("country_code"):
        record = {"country_code": code, "country": COUNTRIES[code]}
        for column in INDICATORS:
            valid = group.dropna(subset=[column]).sort_values("year")
            if valid.empty:
                record[column] = np.nan
                record[f"{column}_year"] = None
            else:
                last = valid.iloc[-1]
                record[column] = float(last[column])
                record[f"{column}_year"] = int(last["year"])
        values.append(record)
    return pd.DataFrame(values)


def add_growth_metrics(panel: pd.DataFrame, latest: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for code, group in panel.groupby("country_code"):
        gdp = group.dropna(subset=["gdp"]).sort_values("year")
        yoy = gdp["gdp"].pct_change() * 100
        start = gdp.iloc[0]
        end = gdp.iloc[-1]
        cagr = ((end["gdp"] / start["gdp"]) ** (1 / (end["year"] - start["year"])) - 1) * 100
        latest_gdp = float(end["gdp"])
        gdp_2019 = gdp.loc[gdp["year"] == 2019, "gdp"]
        gdp_2020 = gdp.loc[gdp["year"] == 2020, "gdp"]
        pandemic_shock = np.nan
        recovery = np.nan
        if not gdp_2019.empty and not gdp_2020.empty:
            pandemic_shock = (float(gdp_2020.iloc[0]) / float(gdp_2019.iloc[0]) - 1) * 100
            recovery = (latest_gdp / float(gdp_2019.iloc[0]) - 1) * 100
        rows.append(
            {
                "country_code": code,
                "country": COUNTRIES[code],
                "gdp_cagr": cagr,
                "gdp_volatility": float(yoy.dropna().std()),
                "pandemic_shock": pandemic_shock,
                "recovery_since_2019": recovery,
                "latest_gdp": latest_gdp,
            }
        )
    return latest.merge(pd.DataFrame(rows), on=["country_code", "country"])


def fmt_trillion(value: float) -> str:
    return f"${value / 1e12:.1f}T"


def fmt_usd(value: float) -> str:
    return f"${value:,.0f}"


def fmt_percent(value: float) -> str:
    return f"{value:.1f}%"


def save_svg(fig: plt.Figure, filename: str) -> None:
    OUT_MEDIA.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_MEDIA / filename, format="svg", bbox_inches="tight")
    plt.close(fig)


def setup_style() -> None:
    sns.set_theme(
        context="talk",
        style="whitegrid",
        font="DejaVu Sans",
        rc={
            "axes.facecolor": "#fffdf8",
            "figure.facecolor": "#f5f9f8",
            "grid.color": "#d7dde4",
            "axes.edgecolor": "#d7dde4",
            "axes.labelcolor": "#2f3e46",
            "xtick.color": "#52616b",
            "ytick.color": "#52616b",
            "text.color": "#132a34",
        },
    )


def add_title(fig: plt.Figure, title: str, subtitle: str) -> None:
    fig.text(0.02, 0.985, title, fontsize=23, weight="bold", color="#132a34", va="top")
    fig.text(0.02, 0.947, subtitle, fontsize=12.5, color="#52616b", va="top")


def plot_gdp_complex(panel: pd.DataFrame, metrics: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14.5, 9.2))
    fig.subplots_adjust(top=0.86, hspace=0.35, wspace=0.28)
    add_title(
        fig,
        "GDP Growth Quality: Scale, Momentum, and Volatility",
        "World Bank current US$ GDP, 2000-2023. Analysis combines indexed growth, CAGR, volatility, and recovery context.",
    )

    indexed = []
    for code, group in panel.dropna(subset=["gdp"]).groupby("country_code"):
        group = group.sort_values("year").copy()
        base = group.loc[group["year"] == group["year"].min(), "gdp"].iloc[0]
        group["gdp_index"] = group["gdp"] / base * 100
        indexed.append(group)
    indexed = pd.concat(indexed)
    sns.lineplot(
        data=indexed,
        x="year",
        y="gdp_index",
        hue="country_code",
        palette=PALETTE,
        linewidth=2.8,
        ax=axes[0, 0],
    )
    axes[0, 0].set_title("Indexed GDP growth, 2000 = 100", loc="left", fontsize=13, weight="bold")
    axes[0, 0].set_xlabel("")
    axes[0, 0].set_ylabel("Index")
    axes[0, 0].legend(title="", ncols=2, frameon=False, fontsize=9)

    ranked = metrics.sort_values("latest_gdp", ascending=False)
    ranked = ranked.assign(latest_gdp_trillion=ranked["latest_gdp"] / 1e12)
    sns.barplot(
        data=ranked,
        y="country_code",
        x="latest_gdp_trillion",
        hue="country_code",
        palette=PALETTE,
        legend=False,
        ax=axes[0, 1],
    )
    axes[0, 1].set_title("Latest GDP scale", loc="left", fontsize=13, weight="bold")
    axes[0, 1].set_xlabel("US$ trillions")
    axes[0, 1].set_ylabel("")
    for i, row in enumerate(ranked.itertuples()):
        axes[0, 1].text(row.latest_gdp / 1e12 + 0.25, i, fmt_trillion(row.latest_gdp), va="center", fontsize=10)

    scatter = metrics.copy()
    sizes = np.sqrt(scatter["latest_gdp"] / scatter["latest_gdp"].max()) * 900
    axes[1, 0].scatter(
        scatter["gdp_volatility"],
        scatter["gdp_cagr"],
        s=sizes,
        c=[PALETTE[c] for c in scatter["country_code"]],
        alpha=0.82,
        edgecolor="white",
        linewidth=1.4,
    )
    for row in scatter.itertuples():
        axes[1, 0].text(row.gdp_volatility + 0.04, row.gdp_cagr, row.country_code, fontsize=10, weight="bold")
    axes[1, 0].axhline(scatter["gdp_cagr"].median(), color="#94a3b8", linestyle="--", linewidth=1)
    axes[1, 0].axvline(scatter["gdp_volatility"].median(), color="#94a3b8", linestyle="--", linewidth=1)
    axes[1, 0].set_title("Growth pace vs. volatility", loc="left", fontsize=13, weight="bold")
    axes[1, 0].set_xlabel("GDP YoY volatility")
    axes[1, 0].set_ylabel("GDP CAGR")

    recovery = metrics.sort_values("recovery_since_2019", ascending=False)
    recovery_palette = {
        row.country_code: "#0f766e" if row.recovery_since_2019 >= 0 else "#be3455"
        for row in recovery.itertuples()
    }
    sns.barplot(
        data=recovery,
        y="country_code",
        x="recovery_since_2019",
        hue="country_code",
        palette=recovery_palette,
        legend=False,
        ax=axes[1, 1],
    )
    axes[1, 1].axvline(0, color="#475569", linewidth=1)
    axes[1, 1].set_title("Latest GDP vs. 2019 baseline", loc="left", fontsize=13, weight="bold")
    axes[1, 1].set_xlabel("Change since 2019")
    axes[1, 1].set_ylabel("")
    axes[1, 1].xaxis.set_major_formatter(lambda x, _: f"{x:.0f}%")

    save_svg(fig, "yinxin-gdp-scale.svg")


def plot_digital_complex(panel: pd.DataFrame, metrics: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14.5, 9.2))
    fig.subplots_adjust(top=0.86, hspace=0.36, wspace=0.3)
    add_title(
        fig,
        "Digital Development Context: Adoption, Health, and Urbanization",
        "Multi-indicator World Bank analysis using internet adoption, life expectancy, health spending, and urban population share.",
    )

    sns.lineplot(
        data=panel.dropna(subset=["internet"]),
        x="year",
        y="internet",
        hue="country_code",
        palette=PALETTE,
        linewidth=2.6,
        ax=axes[0, 0],
    )
    axes[0, 0].set_title("Internet adoption trajectories", loc="left", fontsize=13, weight="bold")
    axes[0, 0].set_xlabel("")
    axes[0, 0].set_ylabel("% of population")
    axes[0, 0].legend(title="", ncols=2, frameon=False, fontsize=9)

    latest = metrics.dropna(subset=["internet", "life_expectancy", "health_spend_pc"]).copy()
    size = np.sqrt(latest["health_spend_pc"] / latest["health_spend_pc"].max()) * 950
    axes[0, 1].scatter(
        latest["internet"],
        latest["life_expectancy"],
        s=size,
        c=[PALETTE[c] for c in latest["country_code"]],
        alpha=0.82,
        edgecolor="white",
        linewidth=1.4,
    )
    for row in latest.itertuples():
        axes[0, 1].text(row.internet + 0.35, row.life_expectancy, row.country_code, fontsize=10, weight="bold")
    axes[0, 1].set_title("Digital access vs. life expectancy", loc="left", fontsize=13, weight="bold")
    axes[0, 1].set_xlabel("Internet users, latest available")
    axes[0, 1].set_ylabel("Life expectancy, latest")

    heat = metrics.set_index("country_code")[["internet", "life_expectancy", "health_spend_pc", "urban_population"]]
    heat = heat.rename(
        columns={
            "internet": "Internet",
            "life_expectancy": "Life exp.",
            "health_spend_pc": "Health $/cap",
            "urban_population": "Urban %",
        }
    )
    z = (heat - heat.mean()) / heat.std(ddof=0)
    sns.heatmap(
        z,
        cmap=sns.diverging_palette(18, 185, s=72, l=56, as_cmap=True),
        center=0,
        linewidths=1,
        linecolor="#fffdf8",
        cbar_kws={"label": "Z-score"},
        ax=axes[1, 0],
    )
    axes[1, 0].set_title("Relative development profile", loc="left", fontsize=13, weight="bold")
    axes[1, 0].set_xlabel("")
    axes[1, 0].set_ylabel("")

    corr_source = panel[["internet", "life_expectancy", "health_spend_pc", "urban_population"]].dropna()
    corr = corr_source.corr()
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap=sns.light_palette("#2563eb", as_cmap=True),
        vmin=0,
        vmax=1,
        linewidths=1,
        linecolor="#fffdf8",
        cbar=False,
        ax=axes[1, 1],
    )
    axes[1, 1].set_title("Indicator correlation map", loc="left", fontsize=13, weight="bold")
    axes[1, 1].set_xticklabels(["Internet", "Life exp.", "Health $", "Urban %"], rotation=25, ha="right")
    axes[1, 1].set_yticklabels(["Internet", "Life exp.", "Health $", "Urban %"], rotation=0)

    save_svg(fig, "yinxin-internet-adoption.svg")


def plot_prosperity_complex(panel: pd.DataFrame, metrics: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(14.5, 9.2))
    fig.subplots_adjust(top=0.86, hspace=0.36, wspace=0.3)
    add_title(
        fig,
        "Prosperity Context: Per-Capita Output, Population Scale, and Urbanization",
        "World Bank comparison that avoids reading headline GDP without population, per-person, and urban context.",
    )

    latest = metrics.dropna(subset=["gdp_per_capita", "population", "latest_gdp"]).copy()
    size = np.sqrt(latest["latest_gdp"] / latest["latest_gdp"].max()) * 1000
    axes[0, 0].scatter(
        latest["population"] / 1e6,
        latest["gdp_per_capita"],
        s=size,
        c=[PALETTE[c] for c in latest["country_code"]],
        alpha=0.84,
        edgecolor="white",
        linewidth=1.4,
    )
    axes[0, 0].set_xscale("log")
    for row in latest.itertuples():
        axes[0, 0].text(row.population / 1e6 * 1.04, row.gdp_per_capita, row.country_code, fontsize=10, weight="bold")
    axes[0, 0].set_title("GDP per capita with population scale", loc="left", fontsize=13, weight="bold")
    axes[0, 0].set_xlabel("Population, millions (log scale)")
    axes[0, 0].set_ylabel("GDP per capita")
    axes[0, 0].yaxis.set_major_formatter(lambda x, _: f"${x / 1000:.0f}k")

    ranked = latest.sort_values("gdp_per_capita", ascending=True)
    sns.barplot(
        data=ranked,
        y="country_code",
        x="gdp_per_capita",
        hue="country_code",
        palette=PALETTE,
        legend=False,
        ax=axes[0, 1],
    )
    axes[0, 1].set_title("Latest GDP per capita ranking", loc="left", fontsize=13, weight="bold")
    axes[0, 1].set_xlabel("US$ per person")
    axes[0, 1].set_ylabel("")
    axes[0, 1].xaxis.set_major_formatter(lambda x, _: f"${x / 1000:.0f}k")

    urban = panel.dropna(subset=["urban_population", "gdp_per_capita"]).copy()
    sns.scatterplot(
        data=urban,
        x="gdp_per_capita",
        y="urban_population",
        hue="country_code",
        palette=PALETTE,
        alpha=0.42,
        s=55,
        ax=axes[1, 0],
        legend=False,
    )
    latest_urban = latest.dropna(subset=["urban_population"])
    axes[1, 0].scatter(
        latest_urban["gdp_per_capita"],
        latest_urban["urban_population"],
        s=120,
        c=[PALETTE[c] for c in latest_urban["country_code"]],
        edgecolor="white",
        linewidth=1.4,
    )
    for row in latest_urban.itertuples():
        axes[1, 0].text(row.gdp_per_capita * 1.03, row.urban_population, row.country_code, fontsize=10, weight="bold")
    axes[1, 0].set_title("Prosperity vs. urbanization", loc="left", fontsize=13, weight="bold")
    axes[1, 0].set_xlabel("GDP per capita")
    axes[1, 0].set_ylabel("Urban population share")
    axes[1, 0].xaxis.set_major_formatter(lambda x, _: f"${x / 1000:.0f}k")
    axes[1, 0].yaxis.set_major_formatter(lambda y, _: f"{y:.0f}%")

    latest["prosperity_score"] = latest["gdp_per_capita"].rank(pct=True) * 50 + latest["life_expectancy"].rank(pct=True) * 30 + latest["internet"].rank(pct=True) * 20
    score = latest.sort_values("prosperity_score", ascending=False)
    sns.barplot(
        data=score,
        y="country_code",
        x="prosperity_score",
        hue="country_code",
        palette=PALETTE,
        legend=False,
        ax=axes[1, 1],
    )
    axes[1, 1].set_title("Composite context score", loc="left", fontsize=13, weight="bold")
    axes[1, 1].set_xlabel("Rank-based score: GDP/cap 50%, life 30%, internet 20%")
    axes[1, 1].set_ylabel("")
    axes[1, 1].set_xlim(0, 100)

    save_svg(fig, "yinxin-gdp-per-capita.svg")


def build_summary(panel: pd.DataFrame, metrics: pd.DataFrame) -> dict:
    latest_gdp = metrics.sort_values("latest_gdp", ascending=False).head(4)
    recovery = metrics.sort_values("recovery_since_2019", ascending=False).head(3)
    digital = metrics.dropna(subset=["internet", "life_expectancy"]).sort_values("internet", ascending=False).head(4)
    prosperity = metrics.dropna(subset=["gdp_per_capita"]).sort_values("gdp_per_capita", ascending=False).head(4)
    corr = panel[["internet", "life_expectancy", "health_spend_pc", "urban_population"]].dropna().corr()

    return {
        "generatedAt": pd.Timestamp.now(tz="UTC").isoformat(),
        "source": "World Bank Open Data API",
        "dateRange": "2000-2023",
        "countries": COUNTRIES,
        "projects": [
            {
                "id": "gdp-scale-growth",
                "title": "GDP Growth Quality and Resilience",
                "question": "Which economies combine scale, long-run momentum, lower volatility, and post-2019 recovery?",
                "chart": "/media/yinxin-gdp-scale.svg",
                "methods": [
                    "Country-year panel construction",
                    "Indexed growth baseline",
                    "CAGR and YoY volatility",
                    "2019 recovery benchmark",
                    "Bubble-size GDP scale comparison",
                ],
                "highlights": [
                    f"{row.country}: latest GDP {fmt_trillion(row.latest_gdp)}, CAGR {fmt_percent(row.gdp_cagr)}, volatility {fmt_percent(row.gdp_volatility)}"
                    for row in latest_gdp.itertuples()
                ]
                + [
                    "Strongest post-2019 recovery: "
                    + ", ".join(f"{row.country_code} {fmt_percent(row.recovery_since_2019)}" for row in recovery.itertuples())
                ],
            },
            {
                "id": "internet-health-development",
                "title": "Digital Development and Human Outcomes",
                "question": "How do internet adoption, health context, urbanization, and life expectancy move together?",
                "chart": "/media/yinxin-internet-adoption.svg",
                "methods": [
                    "Latest-available indicator joins",
                    "Correlation matrix",
                    "Z-score country profile heatmap",
                    "Bubble chart with health spending scale",
                ],
                "highlights": [
                    f"{row.country}: internet users {fmt_percent(row.internet)}, life expectancy {row.life_expectancy:.1f} years"
                    for row in digital.itertuples()
                ]
                + [
                    f"Internet and life expectancy correlation in the panel: {corr.loc['internet', 'life_expectancy']:.2f}"
                ],
            },
            {
                "id": "gdp-per-capita-context",
                "title": "Prosperity Context Beyond Headline GDP",
                "question": "How does the story change when GDP is read beside population, per-capita output, and urbanization?",
                "chart": "/media/yinxin-gdp-per-capita.svg",
                "methods": [
                    "Population-scale bubble plot",
                    "GDP per capita ranking",
                    "Urbanization context",
                    "Rank-based composite score",
                ],
                "highlights": [
                    f"{row.country}: GDP per capita {fmt_usd(row.gdp_per_capita)}, population {row.population / 1e6:,.0f}M"
                    for row in prosperity.itertuples()
                ],
            },
        ],
    }


def main() -> None:
    OUT_DATA.mkdir(parents=True, exist_ok=True)
    OUT_MEDIA.mkdir(parents=True, exist_ok=True)
    setup_style()
    panel = build_panel()
    latest = latest_rows(panel)
    metrics = add_growth_metrics(panel, latest)
    plot_gdp_complex(panel, metrics)
    plot_digital_complex(panel, metrics)
    plot_prosperity_complex(panel, metrics)
    summary = build_summary(panel, metrics)
    (OUT_DATA / "world-bank-analysis.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Generated {len(summary['projects'])} complex World Bank case studies with seaborn/matplotlib.")


if __name__ == "__main__":
    main()
