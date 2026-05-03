"use client";

import { useState, useEffect } from "react";
import Card from "../ui/Card";
import Button from "../ui/Button";

interface CreatorProgress {
  creator_id: string;
  xp: {
    level: number;
    total_xp: number;
    next_level_xp: number;
    xp_totals: Record<string, number>;
  };
  unlocked_realms: string[];
  completed_quests: string[];
  current_realm: string | null;
  achievements: string[];
}

interface Realm {
  realm_type: string;
  name: string;
  description: string;
  required_level: number;
  required_xp: Record<string, number>;
  unlocked: boolean;
}

export function GameWorldPanel() {
  const [progress, setProgress] = useState<CreatorProgress | null>(null);
  const [realms, setRealms] = useState<Realm[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadGameData = async () => {
      try {
        // Load creator progress (using mock user ID for demo)
        const progressResponse = await fetch("/api/v1/game-world/progress/demo-user");
        const progressData = await progressResponse.json();
        
        if (progressData.success) {
          setProgress(progressData);
        }

        // Load realms
        const realmsResponse = await fetch("/api/v1/game-world/realms");
        const realmsData = await realmsResponse.json();
        
        if (realmsData.success) {
          setRealms(realmsData.realms);
        }
      } catch (error) {
        console.error("Failed to load game data:", error);
      } finally {
        setLoading(false);
      }
    };

    loadGameData();
  }, []);

  if (loading) {
    return (
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4">Game World</h3>
        <div className="text-center py-8">
          <div className="text-gray-500">Loading game world data...</div>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Creator Progress */}
      {progress && (
        <Card className="p-6">
          <h3 className="text-xl font-semibold mb-4">Creator Progress</h3>
          <div className="grid gap-6 md:grid-cols-2">
            <div>
              <h4 className="font-medium mb-3">Level & XP</h4>
              <div className="bg-gradient-to-r from-purple-100 to-indigo-100 rounded-lg p-4">
                <div className="text-2xl font-bold text-purple-900 mb-2">
                  Level {progress.xp.level}
                </div>
                <div className="text-sm text-purple-700 mb-3">
                  {progress.xp.total_xp} / {progress.xp.next_level_xp} XP
                </div>
                <div className="w-full bg-purple-200 rounded-full h-2">
                  <div
                    className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                    style={{
                      width: `${(progress.xp.total_xp / progress.xp.next_level_xp) * 100}%`
                    }}
                  />
                </div>
              </div>
              
              <div className="mt-4 space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Creator XP:</span>
                  <span>{progress.xp.xp_totals.creator_xp || 0}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Trust XP:</span>
                  <span>{progress.xp.xp_totals.trust_xp || 0}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Sales XP:</span>
                  <span>{progress.xp.xp_totals.sales_xp || 0}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Proof XP:</span>
                  <span>{progress.xp.xp_totals.proof_xp || 0}</span>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-medium mb-3">Achievements</h4>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Unlocked Realms:</span>
                  <span>{progress.unlocked_realms.length}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Completed Quests:</span>
                  <span>{progress.completed_quests.length}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Achievements:</span>
                  <span>{progress.achievements.length}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Current Realm:</span>
                  <span>{progress.current_realm || "None"}</span>
                </div>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Realms */}
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4">Creator Realms</h3>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {realms.map((realm, index) => (
            <div
              key={realm.realm_type}
              className={`border rounded-lg p-4 ${
                realm.unlocked ? "border-green-500 bg-green-50" : "border-gray-300 bg-gray-50"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium">{realm.name}</h4>
                <span className={`text-sm px-2 py-1 rounded ${
                  realm.unlocked ? "bg-green-500 text-white" : "bg-gray-400 text-white"
                }`}>
                  {realm.unlocked ? "Unlocked" : "Locked"}
                </span>
              </div>
              <p className="text-sm text-gray-600 mb-3">{realm.description}</p>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span>Required Level:</span>
                  <span className={progress && progress.xp.level >= realm.required_level ? "text-green-600" : "text-red-600"}>
                    {realm.required_level}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Required XP:</span>
                  <span>{Object.values(realm.required_xp).reduce((a, b) => a + b, 0)}</span>
                </div>
              </div>
              <Button
                variant="secondary"
                size="sm"
                className="w-full mt-3"
                disabled={!realm.unlocked}
              >
                {realm.unlocked ? "Enter Realm" : "Requirements Not Met"}
              </Button>
            </div>
          ))}
        </div>
      </Card>

      {/* Quick Actions */}
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4">Quick Actions</h3>
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
          <Button variant="secondary" size="sm">
            View Quests
          </Button>
          <Button variant="secondary" size="sm">
            Realms Guide
          </Button>
          <Button variant="secondary" size="sm">
            XP History
          </Button>
          <Button variant="secondary" size="sm">
            Achievements
          </Button>
        </div>
      </Card>
    </div>
  );
}
