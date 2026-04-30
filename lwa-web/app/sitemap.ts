import type { MetadataRoute } from "next";
import { comparisonPages, useCasePages } from "../lib/search-pages";
import { absoluteUrl } from "../lib/seo";

export default function sitemap(): MetadataRoute.Sitemap {
  const staticRoutes = [
    "",
    "/generate",
    "/dashboard",
    "/campaigns",
    "/wallet",
    "/settings",
    "/history",
    "/upload",
    "/compare",
    "/use-cases",
  ];

  const dynamicRoutes = [...comparisonPages, ...useCasePages].map((page) => page.path);

  return [...staticRoutes, ...dynamicRoutes].map((route) => ({
    url: absoluteUrl(route),
    lastModified: new Date(),
    changeFrequency: route === "" ? "weekly" : route === "/generate" ? "weekly" : "monthly",
    priority:
      route === ""
        ? 1
        : route === "/generate"
          ? 0.95
          : route === "/compare" || route === "/use-cases"
            ? 0.82
            : 0.72,
  }));
}
