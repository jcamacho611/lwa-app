"use client";

import { useState, useEffect } from "react";
import Card from "../ui/Card";
import Button from "../ui/Button";

interface EngineStatus {
  name: string;
  status: "healthy" | "error" | "loading";
  description: string;
  endpoint: string;
}

export function CreativeEnginesPanel() {
  const [engines, setEngines] = useState<EngineStatus[]>([
    {
      name: "Thumbnail Engine",
      status: "loading",
      description: "Generates creative thumbnails for maximum engagement",
      endpoint: "/v1/creative/health"
    },
    {
      name: "B-roll Engine",
      status: "loading",
      description: "Creates supplementary footage for content enhancement",
      endpoint: "/v1/creative/health"
    },
    {
      name: "Hook Engine",
      status: "loading",
      description: "Generates viral hooks for content openings",
      endpoint: "/v1/creative/health"
    },
    {
      name: "Trend Intelligence",
      status: "loading",
      description: "Analyzes trends and identifies opportunities",
      endpoint: "/v1/creative/health"
    },
    {
      name: "Audience Persona",
      status: "loading",
      description: "Identifies target audiences and personalizes content",
      endpoint: "/v1/creative/health"
    },
    {
      name: "Offer CTA Engine",
      status: "loading",
      description: "Creates monetization opportunities and CTAs",
      endpoint: "/v1/creative/health"
    }
  ]);

  useEffect(() => {
    // Check engine health
    const checkEngineHealth = async () => {
      try {
        const response = await fetch("/api/v1/creative/health");
        const data = await response.json();
        
        if (data.status === "healthy") {
          setEngines(prev => prev.map(engine => ({
            ...engine,
            status: "healthy"
          })));
        }
      } catch (error) {
        setEngines(prev => prev.map(engine => ({
          ...engine,
          status: "error"
        })));
      }
    };

    checkEngineHealth();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy": return "text-green-600";
      case "error": return "text-red-600";
      case "loading": return "text-yellow-600";
      default: return "text-gray-600";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "healthy": return "✓";
      case "error": return "✗";
      case "loading": return "⟳";
      default: return "?";
    }
  };

  return (
    <Card className="p-6">
      <h3 className="text-xl font-semibold mb-4">Creative Engines</h3>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {engines.map((engine, index) => (
          <div key={index} className="border rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="font-medium">{engine.name}</h4>
              <span className={`text-2xl ${getStatusColor(engine.status)}`}>
                {getStatusIcon(engine.status)}
              </span>
            </div>
            <p className="text-sm text-gray-600 mb-3">{engine.description}</p>
            <Button
              variant="secondary"
              size="sm"
              className="w-full"
              disabled={engine.status !== "healthy"}
            >
              {engine.status === "healthy" ? "Configure" : "Unavailable"}
            </Button>
          </div>
        ))}
      </div>
    </Card>
  );
}
