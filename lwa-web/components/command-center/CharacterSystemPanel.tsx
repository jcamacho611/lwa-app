"use client";

import { useState, useEffect } from "react";
import Card from "../ui/Card";
import Button from "../ui/Button";

interface Character {
  id: string;
  role: string;
  name: string;
  description: string;
  unlocked: boolean;
  is_main_mascot: boolean;
  skins_count: number;
  abilities_count: number;
  quests_count: number;
}

interface CharacterDialogue {
  character_id: string;
  state: string;
  dialogue: string;
}

export function CharacterSystemPanel() {
  const [characters, setCharacters] = useState<Character[]>([]);
  const [mainMascot, setMainMascot] = useState<Character | null>(null);
  const [currentDialogue, setCurrentDialogue] = useState<string>("");
  const [selectedState, setSelectedState] = useState("idle");

  useEffect(() => {
    // Load characters
    const loadCharacters = async () => {
      try {
        const response = await fetch("/api/v1/character/profiles");
        const data = await response.json();
        
        if (data.success) {
          setCharacters(data.characters);
          
          // Find main mascot
          const mascot = data.characters.find((char: Character) => char.is_main_mascot);
          if (mascot) {
            setMainMascot(mascot);
          }
        }
      } catch (error) {
        console.error("Failed to load characters:", error);
      }
    };

    loadCharacters();
  }, []);

  useEffect(() => {
    // Load dialogue when main mascot or state changes
    if (mainMascot) {
      const loadDialogue = async () => {
        try {
          const response = await fetch(`/api/v1/character/dialogue/${mainMascot.id}/${selectedState}`);
          const data = await response.json();
          
          if (data.success) {
            setCurrentDialogue(data.dialogue || "");
          }
        } catch (error) {
          console.error("Failed to load dialogue:", error);
        }
      };

      loadDialogue();
    }
  }, [mainMascot, selectedState]);

  const states = [
    { value: "idle", label: "Idle" },
    { value: "thinking", label: "Thinking" },
    { value: "success", label: "Success" },
    { value: "warning", label: "Warning" },
    { value: "error", label: "Error" },
    { value: "excited", label: "Excited" }
  ];

  return (
    <div className="space-y-6">
      {/* Main Mascot Section */}
      {mainMascot && (
        <Card className="p-6">
          <h3 className="text-xl font-semibold mb-4">Lee-Wuh - AI Mascot</h3>
          <div className="grid gap-6 md:grid-cols-2">
            <div>
              <div className="bg-gradient-to-r from-purple-100 to-indigo-100 rounded-lg p-4 mb-4">
                <h4 className="font-medium text-purple-900 mb-2">{mainMascot.name}</h4>
                <p className="text-sm text-purple-700 mb-3">{mainMascot.description}</p>
                <div className="flex gap-4 text-sm">
                  <span className="text-purple-600">
                    <strong>Role:</strong> {mainMascot.role}
                  </span>
                  <span className="text-purple-600">
                    <strong>Status:</strong> {mainMascot.unlocked ? "Unlocked" : "Locked"}
                  </span>
                </div>
              </div>
              
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium mb-2">Character State</label>
                  <select
                    value={selectedState}
                    onChange={(e) => setSelectedState(e.target.value)}
                    className="w-full p-2 border rounded-md"
                  >
                    {states.map((state) => (
                      <option key={state.value} value={state.value}>
                        {state.label}
                      </option>
                    ))}
                  </select>
                </div>
                
                <Button
                  onClick={() => {
                    // Refresh dialogue
                    setSelectedState(selectedState);
                  }}
                  variant="secondary"
                  size="sm"
                >
                  Refresh Dialogue
                </Button>
              </div>
            </div>
            
            <div>
              <h4 className="font-medium mb-2">Current Dialogue</h4>
              <div className="bg-gray-50 rounded-lg p-4 min-h-[100px]">
                <p className="text-gray-700 italic">
                  {currentDialogue || "Loading dialogue..."}
                </p>
              </div>
            </div>
          </div>
        </Card>
      )}

      {/* Character Stats */}
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4">Character System</h3>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {characters.map((character) => (
            <div
              key={character.id}
              className={`border rounded-lg p-4 ${
                character.is_main_mascot ? "border-purple-500 bg-purple-50" : ""
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-medium">{character.name}</h4>
                {character.is_main_mascot && (
                  <span className="text-xs bg-purple-500 text-white px-2 py-1 rounded">
                    Main
                  </span>
                )}
              </div>
              <p className="text-sm text-gray-600 mb-3">{character.description}</p>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span>Status:</span>
                  <span className={character.unlocked ? "text-green-600" : "text-gray-500"}>
                    {character.unlocked ? "Unlocked" : "Locked"}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Skins:</span>
                  <span>{character.skins_count}</span>
                </div>
                <div className="flex justify-between">
                  <span>Abilities:</span>
                  <span>{character.abilities_count}</span>
                </div>
                <div className="flex justify-between">
                  <span>Quests:</span>
                  <span>{character.quests_count}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Quick Actions */}
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4">Quick Actions</h3>
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
          <Button variant="secondary" size="sm">
            View Skins
          </Button>
          <Button variant="secondary" size="sm">
            View Abilities
          </Button>
          <Button variant="secondary" size="sm">
            Active Quests
          </Button>
          <Button variant="secondary" size="sm">
            Character Guide
          </Button>
        </div>
      </Card>
    </div>
  );
}
