"use client";

import { useState } from "react";

interface MarketplaceProduct {
  id: string;
  name: string;
  description: string;
  product_type: string;
  price: number;
  creator_name: string;
  status: string;
  rating: number;
  review_count: number;
  preview_url?: string;
}

interface MarketplaceJob {
  id: string;
  title: string;
  description: string;
  campaign_type: string;
  budget: number;
  status: string;
  deadline?: string;
  requirements: string[];
  applicant_count: number;
}

const mockProducts: MarketplaceProduct[] = [
  {
    id: "prod_001",
    name: "Clip Pack Starter Shell",
    description: "Example product lane for reviewed clip packages and metadata.",
    product_type: "clip_pack",
    price: 0,
    creator_name: "Example creator",
    status: "draft",
    rating: 0,
    review_count: 0,
    preview_url: "/previews/starter-pack.jpg",
  },
  {
    id: "prod_002",
    name: "Highlights Bundle Shell",
    description: "Example product lane for gameplay or stream highlight review.",
    product_type: "clip_pack",
    price: 0,
    creator_name: "Example creator",
    status: "draft",
    rating: 0,
    review_count: 0,
    preview_url: "/previews/gaming-bundle.jpg",
  },
];

const mockJobs: MarketplaceJob[] = [
  {
    id: "job_001",
    title: "Gaming Channel Clip Pack",
    description: "Create 10 engaging clips from 3 hours of gameplay footage",
    campaign_type: "clip_pack",
    budget: 0,
    status: "draft",
    deadline: undefined,
    requirements: ["Gaming knowledge", "Fast turnaround", "TikTok experience"],
    applicant_count: 12,
  },
  {
    id: "job_002",
    title: "Podcast Promotion Series",
    description: "Generate clips promoting new podcast episodes",
    campaign_type: "promotion",
    budget: 0,
    status: "draft",
    deadline: undefined,
    requirements: ["Audio editing", "Storytelling", "Social media savvy"],
    applicant_count: 8,
  },
];

export function MarketplacePanel() {
  const [activeTab, setActiveTab] = useState<"products" | "jobs" | "profiles">("products");
  const [filterCategory, setFilterCategory] = useState<string>("all");

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="rounded-2xl border border-white/10 bg-white/[0.04] p-6">
        <div className="flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-[#00D9FF]/20 text-3xl">
            🛒
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-semibold text-white">Opportunity Marketplace</h3>
            <p className="text-sm text-white/50">Find jobs, campaigns, and creator resources</p>
          </div>
          <div className="flex gap-4 text-right">
            <div>
              <div className="text-sm text-white/50">Live Jobs</div>
              <div className="text-xl font-bold text-[#00D9FF]">Off</div>
            </div>
            <div>
              <div className="text-sm text-white/50">Rail State</div>
              <div className="text-xl font-bold text-[#00D9FF]">V0</div>
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2">
        {[
          { id: "products", label: "Products", icon: "📦" },
          { id: "jobs", label: "Jobs", icon: "💼" },
          { id: "profiles", label: "Creators", icon: "👥" },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-2 rounded-xl px-4 py-3 text-sm font-medium transition-all ${
              activeTab === tab.id
                ? "bg-[#C9A24A] text-black"
                : "border border-white/10 bg-white/[0.04] text-white/70 hover:bg-white/[0.08]"
            }`}
          >
            <span>{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Products Tab */}
      {activeTab === "products" && (
        <div className="space-y-4">
          {/* Filters */}
          <div className="flex flex-wrap gap-2">
            {["all", "template", "library", "preset"].map((cat) => (
              <button
                key={cat}
                onClick={() => setFilterCategory(cat)}
                className={`rounded-full px-3 py-1 text-xs transition ${
                  filterCategory === cat
                    ? "bg-[#C9A24A] text-black"
                    : "border border-white/10 bg-white/[0.04] text-white/50 hover:bg-white/[0.08]"
                }`}
              >
                {cat.charAt(0).toUpperCase() + cat.slice(1)}
              </button>
            ))}
          </div>

          {/* Product Grid */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {mockProducts.map((product) => (
              <div
                key={product.id}
                className="rounded-2xl border border-white/10 bg-white/[0.04] p-5 transition hover:border-white/20"
              >
                <div className="mb-3 flex items-start justify-between">
                  <div>
                    <span className="mb-2 inline-block rounded-full bg-white/10 px-2 py-1 text-xs capitalize text-white/50">
                      {product.product_type}
                    </span>
                    <h4 className="font-medium text-white">{product.name}</h4>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-[#E9C77B]">Pricing later</div>
                  </div>
                </div>

                <p className="mb-4 text-sm text-white/50">{product.description}</p>

                <div className="mb-4 flex items-center gap-2 text-sm">
                  <span className="text-white/50">By {product.creator_name}</span>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-1">
                    <span className="text-[#E9C77B]">★</span>
                    <span className="text-sm font-medium text-white">No reviews yet</span>
                  </div>
                  <button className="rounded-lg bg-[#C9A24A] px-3 py-2 text-sm font-medium text-black transition hover:bg-[#E9C77B]">
                    View
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Jobs Tab */}
      {activeTab === "jobs" && (
        <div className="space-y-4">
          {/* Job Filters */}
          <div className="flex flex-wrap gap-2">
            {["all", "content_series", "repurpose", "brand"].map((type) => (
              <button
                key={type}
                className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs capitalize text-white/50 transition hover:bg-white/[0.08]"
              >
                {type.replace("_", " ")}
              </button>
            ))}
          </div>

          {/* Job List */}
          <div className="space-y-4">
            {mockJobs.map((job) => (
              <div
                key={job.id}
                className="rounded-2xl border border-white/10 bg-white/[0.04] p-5 transition hover:border-white/20"
              >
                <div className="mb-3 flex items-start justify-between">
                  <div>
                    <div className="mb-1 flex items-center gap-2">
                      <span className="rounded-full bg-green-400/20 px-2 py-1 text-xs text-green-400">
                        {job.status}
                      </span>
                      <span className="text-xs capitalize text-white/30">{job.campaign_type}</span>
                    </div>
                    <h4 className="text-lg font-medium text-white">{job.title}</h4>
                  </div>
                  <div className="text-right">
                    <div className="text-xl font-bold text-[#E9C77B]">Draft</div>
                    <div className="text-xs text-white/30">budget state</div>
                  </div>
                </div>

                <p className="mb-4 text-sm text-white/50">{job.description}</p>

                <div className="mb-4 flex flex-wrap gap-2">
                  {job.requirements.map((req, idx) => (
                    <span
                      key={idx}
                      className="rounded-full bg-white/[0.02] px-2 py-1 text-xs text-white/50"
                    >
                      {req}
                    </span>
                  ))}
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4 text-sm">
                    <span className="text-white/50">Applications manual</span>
                    {job.deadline && (
                      <span className="text-white/30">Deadline: {job.deadline}</span>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <button className="rounded-lg border border-white/10 bg-white/[0.04] px-3 py-2 text-sm text-white transition hover:bg-white/[0.08]">
                      Details
                    </button>
                    <button className="rounded-lg bg-[#C9A24A] px-3 py-2 text-sm font-medium text-black transition hover:bg-[#E9C77B]">
                      Draft only
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Profiles Tab */}
      {activeTab === "profiles" && (
        <div className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {[
              { name: "Creator profile shell", specialty: "TikTok Shorts", rating: "Not live", jobs: "Manual", earnings: "Disabled" },
              { name: "Caption profile shell", specialty: "Captions & Text", rating: "Not live", jobs: "Manual", earnings: "Disabled" },
              { name: "Hook profile shell", specialty: "Hook Writing", rating: "Not live", jobs: "Manual", earnings: "Disabled" },
              { name: "Editor profile shell", specialty: "Long-form to Short", rating: "Not live", jobs: "Manual", earnings: "Disabled" },
            ].map((creator, idx) => (
              <div
                key={idx}
                className="rounded-2xl border border-white/10 bg-white/[0.04] p-5 text-center transition hover:border-white/20"
              >
                <div className="mb-3 flex h-16 w-16 items-center justify-center rounded-full bg-gradient-to-br from-[#C9A24A] to-[#6D3BFF] text-2xl text-white">
                  {creator.name.charAt(0)}
                </div>
                <h4 className="mb-1 font-medium text-white">{creator.name}</h4>
                <p className="mb-3 text-sm text-white/50">{creator.specialty}</p>

                <div className="mb-3 flex items-center justify-center gap-1">
                  <span className="text-[#E9C77B]">★</span>
                  <span className="font-medium text-white">{creator.rating}</span>
                </div>

                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="rounded-lg bg-white/[0.02] p-2">
                    <div className="font-medium text-white">{creator.jobs}</div>
                    <div className="text-xs text-white/30">Reviews</div>
                  </div>
                  <div className="rounded-lg bg-white/[0.02] p-2">
                    <div className="font-medium text-[#E9C77B]">{creator.earnings}</div>
                    <div className="text-xs text-white/30">Payouts</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-3">
        <button className="rounded-xl bg-[#C9A24A] px-4 py-3 text-sm font-semibold text-black transition hover:bg-[#E9C77B]">
          Post a Job
        </button>
        <button className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-medium text-white transition hover:bg-white/[0.08]">
          Sell Product
        </button>
        <button className="rounded-xl border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-medium text-white transition hover:bg-white/[0.08]">
          My Listings
        </button>
      </div>
    </div>
  );
}
