const FALLBACK_LOCALE = "en-US";

const RTL_BASE_LANGUAGES = new Set(["ar", "fa", "he", "ku", "ps", "sd", "ug", "ur"]);

export function resolveLocale(acceptLanguage?: string | null) {
  if (!acceptLanguage) {
    return FALLBACK_LOCALE;
  }

  const first = acceptLanguage
    .split(",")
    .map((entry) => entry.trim().split(";")[0])
    .find(Boolean);

  try {
    return Intl.getCanonicalLocales(first || FALLBACK_LOCALE)[0] || FALLBACK_LOCALE;
  } catch {
    return FALLBACK_LOCALE;
  }
}

export function resolveDirection(locale: string) {
  const base = locale.toLowerCase().split("-")[0];
  return RTL_BASE_LANGUAGES.has(base) ? "rtl" : "ltr";
}

export function formatCurrency(value?: number | null, currency = "USD", locale = FALLBACK_LOCALE) {
  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format((value || 0) / 100);
}

export function formatCount(value?: number | null, locale = FALLBACK_LOCALE) {
  return new Intl.NumberFormat(locale).format(value || 0);
}

export function formatPercent(value?: number | null, locale = FALLBACK_LOCALE) {
  return new Intl.NumberFormat(locale, {
    style: "percent",
    maximumFractionDigits: 0,
  }).format((value || 0) / 100);
}
