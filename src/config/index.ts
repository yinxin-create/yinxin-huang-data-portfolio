import type {
  NavBarLink,
  Identity,
  AboutPageContent,
  FeaturedPageContent,
  HomePageContent,
  NowPageContent,
} from "../types/config";

import { socialLinks, homeSocialLinks } from "./social";
import { sourceLinks } from "./source";

export const identity: Identity = {
  name: "Yinxin Huang",
  logo: "/img/profile-main.jpg",
  email: "",
};

export const openGraphImage: string = "/img/profile-about.jpg";
const siteUrl = "https://yinxin-create.github.io/yinxin-huang-data-portfolio";
const siteDomain = "yinxin-create.github.io";

export const navBarLinks: NavBarLink[] = [
  {
    title: "Home",
    url: "/",
  },
  {
    title: "Projects",
    url: "/featured",
  },
  {
    title: "About",
    url: "/about",
  },
];

export const homePageContent: HomePageContent = {
  seo: {
    title: "Yinxin Huang | Data Analysis Projects",
    description:
      "Yinxin Huang's portfolio of World Bank data analyses using Python, pandas, seaborn, and matplotlib.",
    image: openGraphImage,
    domain: siteDomain,
    url: siteUrl,
  },
  role: "World Bank data analysis",
  company: "Python, pandas, seaborn, matplotlib",
  description:
    "A small portfolio using public indicators to practice data cleaning, comparison, chart design, and written interpretation.",
  socialLinks,
  homeSocialLinks,
  links: [
    {
      title: "Projects",
      url: "/featured",
      icon: "mdi:chart-box-outline",
    },
  ],
};

export const aboutPageContent: AboutPageContent = {
  seo: {
    title: "About | Yinxin Huang",
    description:
      "About Yinxin Huang's interest in data analysis, public datasets, Python, and visualization.",
    image: openGraphImage,
    domain: siteDomain,
    url: `${siteUrl}/about`,
  },
  subtitle: "Curious about data, careful with comparisons.",
  about: {
    description:
      "A concise profile centered on data curiosity, public datasets, analytical thinking, and clear communication.",
    image_l: {
      url: "/img/profile-about.jpg",
      alt: "Profile photo",
    },
    image_r: {
      url: "/img/profile-main.jpg",
      alt: "Profile portrait",
    },
  },
  work: {
    description: "",
    items: [],
  },
  connect: {
    description: "",
    links: [],
  },
};

export const featuredPageContent: FeaturedPageContent = {
  seo: {
    title: "Projects | Yinxin Huang",
    description:
      "World Bank data analyses covering growth quality, digital development, and prosperity context.",
    image: openGraphImage,
    domain: siteDomain,
    url: `${siteUrl}/featured`,
  },
  subtitle: "Python analyses using World Bank Open Data.",
};

export const nowPageContent: NowPageContent = {
  seo: {
    title: "Now | Yinxin Huang",
    description: "Current focus for the portfolio.",
    image: openGraphImage,
    domain: siteDomain,
    url: `${siteUrl}/now`,
  },
  title: "Now",
  subtitle: "Portfolio build in progress.",
  sourceLinks,
};

export * from "./music";
export * from "./social";
export * from "./featured";
export * from "./source";
export * from "./analytics";
export * from "./github";
