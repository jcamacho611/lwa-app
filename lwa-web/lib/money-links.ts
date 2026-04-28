export type MoneyLinkKey =
  | "whop"
  | "stripe"
  | "paypal"
  | "gumroad"
  | "lemonSqueezy"
  | "demoForm"
  | "affiliateForm"
  | "booking"
  | "contact";

export type MoneyLinkCategory = "checkout" | "demo" | "affiliate" | "booking" | "contact";

export type MoneyLink = {
  key: MoneyLinkKey;
  label: string;
  shortLabel: string;
  href: string;
  enabled: boolean;
  category: MoneyLinkCategory;
  description: string;
  priority: number;
  external: true;
};

export const DEFAULT_WHOP_URL = "https://whop.com/lwa-app/lwa-ai-content-repurposer/";

function envUrl(value?: string) {
  return value?.trim() || "";
}

function moneyLink({
  key,
  label,
  shortLabel,
  href,
  category,
  description,
  priority,
}: Omit<MoneyLink, "enabled" | "external">): MoneyLink {
  return {
    key,
    label,
    shortLabel,
    href,
    enabled: Boolean(href),
    category,
    description,
    priority,
    external: true,
  };
}

export const MONEY_LINKS: Record<MoneyLinkKey, MoneyLink> = {
  stripe: moneyLink({
    key: "stripe",
    label: "Pay directly",
    shortLabel: "Checkout",
    href: envUrl(process.env.NEXT_PUBLIC_LWA_STRIPE_PAYMENT_LINK),
    category: "checkout",
    description: "Use a direct checkout link when it is configured.",
    priority: 10,
  }),
  paypal: moneyLink({
    key: "paypal",
    label: "Pay with PayPal",
    shortLabel: "PayPal",
    href: envUrl(process.env.NEXT_PUBLIC_LWA_PAYPAL_URL),
    category: "checkout",
    description: "Use PayPal when that path fits the buyer.",
    priority: 20,
  }),
  gumroad: moneyLink({
    key: "gumroad",
    label: "Open Gumroad",
    shortLabel: "Gumroad",
    href: envUrl(process.env.NEXT_PUBLIC_LWA_GUMROAD_URL),
    category: "checkout",
    description: "Buy a clip pack, template, or offer through Gumroad when configured.",
    priority: 30,
  }),
  lemonSqueezy: moneyLink({
    key: "lemonSqueezy",
    label: "Open Lemon Squeezy",
    shortLabel: "Lemon Squeezy",
    href: envUrl(process.env.NEXT_PUBLIC_LWA_LEMON_SQUEEZY_URL),
    category: "checkout",
    description: "Use Lemon Squeezy for checkout when configured.",
    priority: 40,
  }),
  whop: moneyLink({
    key: "whop",
    label: "Open Whop",
    shortLabel: "Whop",
    href: envUrl(process.env.NEXT_PUBLIC_LWA_WHOP_URL) || DEFAULT_WHOP_URL,
    category: "checkout",
    description: "Use Whop access when that is the right purchase path.",
    priority: 50,
  }),
  demoForm: moneyLink({
    key: "demoForm",
    label: "Request demo",
    shortLabel: "Demo",
    href: envUrl(process.env.NEXT_PUBLIC_LWA_DEMO_FORM_URL),
    category: "demo",
    description: "Request a walkthrough or custom clipping discussion.",
    priority: 60,
  }),
  affiliateForm: moneyLink({
    key: "affiliateForm",
    label: "Join referral list",
    shortLabel: "Referral",
    href: envUrl(process.env.NEXT_PUBLIC_LWA_AFFILIATE_FORM_URL),
    category: "affiliate",
    description: "Register interest in partner or referral workflows.",
    priority: 70,
  }),
  booking: moneyLink({
    key: "booking",
    label: "Book a call",
    shortLabel: "Book",
    href: envUrl(process.env.NEXT_PUBLIC_LWA_BOOKING_URL),
    category: "booking",
    description: "Book time to review workflow fit.",
    priority: 80,
  }),
  contact: moneyLink({
    key: "contact",
    label: "Contact team",
    shortLabel: "Contact",
    href: envUrl(process.env.NEXT_PUBLIC_LWA_CONTACT_URL),
    category: "contact",
    description: "Reach the team for custom setup questions.",
    priority: 90,
  }),
};

export function getEnabledMoneyLinks() {
  return Object.values(MONEY_LINKS)
    .filter((link) => link.enabled)
    .sort((left, right) => left.priority - right.priority);
}

export function getMoneyLinkByKey(key: MoneyLinkKey) {
  const link = MONEY_LINKS[key];
  return link.enabled ? link : null;
}

export function getPrimaryMoneyLink() {
  return getEnabledMoneyLinks()[0] || MONEY_LINKS.whop;
}

export function buildUtmUrl(link: Pick<MoneyLink, "href" | "key" | "external">, source = "default") {
  if (!link.external) {
    return link.href;
  }

  try {
    const url = new URL(link.href);
    url.searchParams.set("utm_source", "lwa_web");
    url.searchParams.set("utm_medium", "money_cta");
    url.searchParams.set("utm_campaign", source || "default");
    url.searchParams.set("utm_content", link.key);
    return url.toString();
  } catch {
    return link.href;
  }
}
