import type { FeaturedPost } from "../types/config";

export const featuredPosts: FeaturedPost[] = [
  {
    title: "GDP Growth Quality and Resilience",
    description:
      "A four-panel view of GDP scale, indexed growth, CAGR, volatility, and recovery after 2019.",
    date: "2026-06-17",
    url: "/featured#gdp-scale-growth",
    author: "Yinxin Huang",
    image: {
      url: "/media/yinxin-gdp-scale.svg",
      alt: "GDP growth quality and resilience analysis preview",
    },
    publisher: "pandas · seaborn · matplotlib · macro indicators",
  },
  {
    title: "Digital Development and Human Outcomes",
    description:
      "A comparison of internet adoption, life expectancy, health spending, urbanization, and indicator correlations.",
    date: "2026-06-17",
    url: "/featured#internet-health-development",
    author: "Yinxin Huang",
    image: {
      url: "/media/yinxin-internet-adoption.svg",
      alt: "Digital development and human outcomes analysis preview",
    },
    publisher: "World Bank API · correlation · heatmap · KPI framing",
  },
  {
    title: "Prosperity Context Beyond Headline GDP",
    description:
      "A look at how GDP rankings change when population scale, per-capita output, urbanization, and a context score are added.",
    date: "2026-06-17",
    url: "/featured#gdp-per-capita-context",
    author: "Yinxin Huang",
    image: {
      url: "/media/yinxin-gdp-per-capita.svg",
      alt: "Prosperity context analysis preview",
    },
    publisher: "Python · pandas · bubble charts · composite scoring",
  },
];
