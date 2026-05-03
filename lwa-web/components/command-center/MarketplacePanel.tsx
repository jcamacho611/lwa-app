"use client";

import { useState, useEffect } from "react";
import Card from "../ui/Card";
import Button from "../ui/Button";

interface MarketplaceProduct {
  id: string;
  name: string;
  description: string;
  product_type: string;
  price: number;
  creator_name: string;
  status: string;
  created_at: string;
  download_count: number;
  rating: number;
  review_count: number;
  preview_url?: string;
  asset_urls: string[];
}

interface MarketplaceJob {
  id: string;
  title: string;
  description: string;
  campaign_type: string;
  budget: number;
  status: string;
  created_at: string;
  deadline?: string;
  requirements: string[];
  applicant_count: number;
  creator_profile?: {
    display_name: string;
    avatar_url?: string;
    rating: number;
  };
}

interface CreatorProfile {
  id: string;
  display_name: string;
  bio: string;
  specialties: string[];
  rating: number;
  completed_jobs: number;
  earnings: {
    approved: number;
    pending: number;
  };
  status: string;
}

export function MarketplacePanel() {
  const [products, setProducts] = useState<MarketplaceProduct[]>([]);
  const [jobs, setJobs] = useState<MarketplaceJob[]>([]);
  const [profiles, setProfiles] = useState<CreatorProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"products" | "jobs" | "profiles">("products");

  useEffect(() => {
    const loadData = async () => {
      try {
        // Load products
        try {
          const productsResponse = await fetch("/api/v1/marketplace/products");
          const productsData = await productsResponse.json();
          
          if (productsData.products && Array.isArray(productsData.products)) {
            setProducts(productsData.products.slice(0, 10));
          }
        } catch (error) {
          console.error("Failed to load products:", error);
        }

        // Load jobs
        try {
          const jobsResponse = await fetch("/api/v1/marketplace/jobs");
          const jobsData = await jobsResponse.json();
          
          if (jobsData.jobs && Array.isArray(jobsData.jobs)) {
            setJobs(jobsData.jobs.slice(0, 10));
          }
        } catch (error) {
          console.error("Failed to load jobs:", error);
        }

        // Load creator profiles
        try {
          const profilesResponse = await fetch("/api/v1/marketplace/profiles");
          const profilesData = await profilesResponse.json();
          
          if (profilesData.profiles && Array.isArray(profilesData.profiles)) {
            setProfiles(profilesData.profiles.slice(0, 10));
          }
        } catch (error) {
          console.error("Failed to load profiles:", error);
        }
      } catch (error) {
        console.error("Failed to load marketplace data:", error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active": return "text-green-600";
      case "pending": return "text-yellow-600";
      case "completed": return "text-blue-600";
      case "cancelled": return "text-red-600";
      case "approved": return "text-green-600";
      default: return "text-gray-600";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "active": return "✓";
      case "pending": return "⏳";
      case "completed": return "✓";
      case "cancelled": return "✗";
      case "approved": return "✓";
      default: return "?";
    }
  };

  const getRatingStars = (rating: number) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;
    
    for (let i = 0; i < fullStars; i++) {
      stars.push("⭐");
    }
    if (hasHalfStar) {
      stars.push("⭐");
    }
    for (let i = stars.length; i < 5; i++) {
      stars.push("☆");
    }
    
    return stars.join("");
  };

  if (loading) {
    return (
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4">Marketplace</h3>
        <div className="text-center py-8">
          <div className="text-gray-500">Loading marketplace data...</div>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab("products")}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === "products"
                ? "border-purple-500 text-purple-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            Products ({products.length})
          </button>
          <button
            onClick={() => setActiveTab("jobs")}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === "jobs"
                ? "border-purple-500 text-purple-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            Jobs ({jobs.length})
          </button>
          <button
            onClick={() => setActiveTab("profiles")}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === "profiles"
                ? "border-purple-500 text-purple-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            Creator Profiles ({profiles.length})
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === "products" && (
        <div className="space-y-4">
          {products.length > 0 ? (
            products.map((product) => (
              <Card key={product.id} className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="font-medium">{product.name}</h4>
                      <span className={`text-sm px-2 py-1 rounded ${getStatusColor(product.status)} bg-gray-100`}>
                        {getStatusIcon(product.status)} {product.status}
                      </span>
                      <span className="text-sm px-2 py-1 rounded bg-purple-100 text-purple-700">
                        {product.product_type}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{product.description}</p>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600 mb-2">
                      <div>
                        <span className="font-medium">Price:</span> {formatPrice(product.price)}
                      </div>
                      <div>
                        <span className="font-medium">Creator:</span> {product.creator_name}
                      </div>
                      <div>
                        <span className="font-medium">Downloads:</span> {product.download_count}
                      </div>
                      <div>
                        <span className="font-medium">Rating:</span> {getRatingStars(product.rating)} ({product.review_count})
                      </div>
                    </div>
                    <div className="text-sm text-gray-500">
                      Created: {formatDate(product.created_at)}
                    </div>
                  </div>
                  <div className="ml-4 space-y-2">
                    <Button variant="secondary" size="sm">
                      Preview
                    </Button>
                    <Button variant="secondary" size="sm">
                      Purchase
                    </Button>
                  </div>
                </div>
              </Card>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              No products found
            </div>
          )}
        </div>
      )}

      {activeTab === "jobs" && (
        <div className="space-y-4">
          {jobs.length > 0 ? (
            jobs.map((job) => (
              <Card key={job.id} className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="font-medium">{job.title}</h4>
                      <span className={`text-sm px-2 py-1 rounded ${getStatusColor(job.status)} bg-gray-100`}>
                        {getStatusIcon(job.status)} {job.status}
                      </span>
                      <span className="text-sm px-2 py-1 rounded bg-blue-100 text-blue-700">
                        {job.campaign_type}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{job.description}</p>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600 mb-2">
                      <div>
                        <span className="font-medium">Budget:</span> {formatPrice(job.budget)}
                      </div>
                      <div>
                        <span className="font-medium">Applicants:</span> {job.applicant_count}
                      </div>
                      <div>
                        <span className="font-medium">Created:</span> {formatDate(job.created_at)}
                      </div>
                      {job.deadline && (
                        <div>
                          <span className="font-medium">Deadline:</span> {formatDate(job.deadline)}
                        </div>
                      )}
                    </div>
                    {job.requirements.length > 0 && (
                      <div className="text-sm text-gray-600 mb-2">
                        <span className="font-medium">Requirements:</span> {job.requirements.join(", ")}
                      </div>
                    )}
                    {job.creator_profile && (
                      <div className="text-sm text-gray-600">
                        <span className="font-medium">Client:</span> {job.creator_profile.display_name} ({getRatingStars(job.creator_profile.rating)})
                      </div>
                    )}
                  </div>
                  <div className="ml-4 space-y-2">
                    <Button variant="secondary" size="sm">
                      View Details
                    </Button>
                    {job.status === "active" && (
                      <Button variant="secondary" size="sm">
                        Apply
                      </Button>
                    )}
                  </div>
                </div>
              </Card>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              No jobs found
            </div>
          )}
        </div>
      )}

      {activeTab === "profiles" && (
        <div className="space-y-4">
          {profiles.length > 0 ? (
            profiles.map((profile) => (
              <Card key={profile.id} className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="font-medium">{profile.display_name}</h4>
                      <span className={`text-sm px-2 py-1 rounded ${getStatusColor(profile.status)} bg-gray-100`}>
                        {getStatusIcon(profile.status)} {profile.status}
                      </span>
                      <span className="text-sm text-purple-600">
                        {getRatingStars(profile.rating)}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">{profile.bio}</p>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600 mb-2">
                      <div>
                        <span className="font-medium">Completed Jobs:</span> {profile.completed_jobs}
                      </div>
                      <div>
                        <span className="font-medium">Approved Earnings:</span> {formatPrice(profile.earnings.approved)}
                      </div>
                      <div>
                        <span className="font-medium">Pending Earnings:</span> {formatPrice(profile.earnings.pending)}
                      </div>
                      <div>
                        <span className="font-medium">Specialties:</span> {profile.specialties.join(", ")}
                      </div>
                    </div>
                  </div>
                  <div className="ml-4 space-y-2">
                    <Button variant="secondary" size="sm">
                      View Profile
                    </Button>
                    <Button variant="secondary" size="sm">
                      Hire Creator
                    </Button>
                  </div>
                </div>
              </Card>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              No creator profiles found
            </div>
          )}
        </div>
      )}

      {/* Quick Actions */}
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4">Quick Actions</h3>
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
          <Button variant="secondary" size="sm">
            Create Listing
          </Button>
          <Button variant="secondary" size="sm">
            Post Job
          </Button>
          <Button variant="secondary" size="sm">
            View Orders
          </Button>
          <Button variant="secondary" size="sm">
            Seller Dashboard
          </Button>
        </div>
      </Card>
    </div>
  );
}
