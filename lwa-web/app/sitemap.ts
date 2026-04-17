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
  ];

  const dynamicRoutes = [...comparisonPages, ...useCasePages].map((page) => page.path);

  return [...staticRoutes, ...dynamicRoutes].map((route) => ({
    url: absoluteUrl(route),
    lastModified: new Date(),
    changeFrequency: route === "" ? "weekly" : "monthly",
    priority: route === "" ? 1 : route === "/generate" ? 0.95 : 0.72,
  }));
}
