"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import type { GameState, Lane, GameObject, GameStats } from "../../lib/game/types";
import { startSignalSprintSession, completeSignalSprintSession } from "../../lib/game/mockGameApi";
import SignalSprintHud from "./SignalSprintHud";
import SignalSprintResults from "./SignalSprintResults";

interface SignalSprintGameProps {
  onComplete?: () => void;
}

const GAME_DURATION = 60; // seconds (shortened for dev: 30s)
const SPAWN_RATE = 800; // ms between spawns
const GAME_SPEED = 2; // pixels per frame

export default function SignalSprintGame({ onComplete }: SignalSprintGameProps) {
  const [gameState, setGameState] = useState<GameState>("idle");
  const [playerLane, setPlayerLane] = useState<Lane>(1); // Start in center
  const [objects, setObjects] = useState<GameObject[]>([]);
  const [stats, setStats] = useState<GameStats>({
    score: 0,
    streak: 0,
    maxStreak: 0,
    signalCollected: 0,
    noiseHits: 0,
    durationMs: 0,
    startTime: 0,
  });
  const [timeLeft, setTimeLeft] = useState(GAME_DURATION);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [result, setResult] = useState<Awaited<ReturnType<typeof completeSignalSprintSession>> | null>(null);

  const gameLoopRef = useRef<number>();
  const spawnIntervalRef = useRef<NodeJS.Timeout>();

  // Handle lane movement
  const moveLeft = useCallback(() => {
    if (gameState !== "playing") return;
    setPlayerLane((prev) => (prev > 0 ? (prev - 1) as Lane : prev));
  }, [gameState]);

  const moveRight = useCallback(() => {
    if (gameState !== "playing") return;
    setPlayerLane((prev) => (prev < 2 ? (prev + 1) as Lane : prev));
  }, [gameState]);

  // Keyboard controls
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "ArrowLeft" || e.key === "a" || e.key === "A") {
        e.preventDefault();
        moveLeft();
      } else if (e.key === "ArrowRight" || e.key === "d" || e.key === "D") {
        e.preventDefault();
        moveRight();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [moveLeft, moveRight]);

  // Start game
  const startGame = async () => {
    const session = await startSignalSprintSession();
    setSessionId(session.sessionId);
    setGameState("playing");
    setTimeLeft(GAME_DURATION);
    setObjects([]);
    setStats({
      score: 0,
      streak: 0,
      maxStreak: 0,
      signalCollected: 0,
      noiseHits: 0,
      durationMs: 0,
      startTime: Date.now(),
    });
  };

  // Spawn objects
  useEffect(() => {
    if (gameState !== "playing") return;

    spawnIntervalRef.current = setInterval(() => {
      const lanes: Lane[] = [0, 1, 2];
      const newObjects: GameObject[] = lanes
        .filter(() => Math.random() > 0.3) // 70% chance per lane
        .map((lane) => ({
          id: crypto.randomUUID(),
          lane,
          type: Math.random() > 0.3 ? "signal" : "noise", // 70% signal
          position: -10, // Start above screen
        }));

      setObjects((prev) => [...prev, ...newObjects]);
    }, SPAWN_RATE);

    return () => {
      if (spawnIntervalRef.current) clearInterval(spawnIntervalRef.current);
    };
  }, [gameState]);

  // Game loop
  useEffect(() => {
    if (gameState !== "playing") return;

    const gameLoop = () => {
      // Move objects
      setObjects((prev) => {
        return prev
          .map((obj) => ({ ...obj, position: obj.position + GAME_SPEED }))
          .filter((obj) => obj.position < 110); // Remove off-screen
      });

      // Check collisions
      setObjects((prev) => {
        const playerY = 80; // Player position (bottom)
        const collisionRange = 8; // Collision tolerance

        const newObjects = prev.map((obj) => {
          if (obj.collected) return obj;

          // Check if in same lane and at player height
          if (
            obj.lane === playerLane &&
            Math.abs(obj.position - playerY) < collisionRange
          ) {
            // Collision detected
            setStats((s) => {
              if (obj.type === "signal") {
                const newStreak = s.streak + 1;
                return {
                  ...s,
                  score: s.score + 100 + newStreak * 10,
                  streak: newStreak,
                  maxStreak: Math.max(s.maxStreak, newStreak),
                  signalCollected: s.signalCollected + 1,
                };
              } else {
                return {
                  ...s,
                  score: Math.max(0, s.score - 50),
                  streak: 0,
                  noiseHits: s.noiseHits + 1,
                };
              }
            });
            return { ...obj, collected: true };
          }
          return obj;
        });

        return newObjects.filter((obj) => !obj.collected || obj.position < playerY + 10);
      });

      gameLoopRef.current = requestAnimationFrame(gameLoop);
    };

    gameLoopRef.current = requestAnimationFrame(gameLoop);

    return () => {
      if (gameLoopRef.current) cancelAnimationFrame(gameLoopRef.current);
    };
  }, [gameState, playerLane]);

  // Timer
  useEffect(() => {
    if (gameState !== "playing") return;

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          // Game over
          endGame();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [gameState]);

  // End game
  const endGame = async () => {
    if (!sessionId) return;

    setGameState("completed");

    const durationMs = Date.now() - stats.startTime;

    const result = await completeSignalSprintSession({
      sessionId,
      score: stats.score,
      durationMs,
      maxStreak: stats.maxStreak,
      signalCollected: stats.signalCollected,
      noiseHits: stats.noiseHits,
      clientVersion: "signal-sprint-v1",
      endedAt: new Date().toISOString(),
    });

    setResult(result);
  };

  // Render game objects
  const renderObject = (obj: GameObject) => {
    const laneX = obj.lane === 0 ? "25%" : obj.lane === 1 ? "50%" : "75%";

    return (
      <div
        key={obj.id}
        className={`absolute w-8 h-8 rounded-full transform -translate-x-1/2 ${
          obj.type === "signal"
            ? "bg-[#C9A24A] shadow-lg shadow-[#C9A24A]/50"
            : "bg-red-500 shadow-lg shadow-red-500/50"
        }`}
        style={{
          left: laneX,
          top: `${obj.position}%`,
        }}
      >
        {obj.type === "signal" ? (
          <svg className="w-5 h-5 m-1.5 text-black" fill="currentColor" viewBox="0 0 20 20">
            <path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM18 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM5.05 6.464A1 1 0 106.464 5.05l-.707-.707a1 1 0 00-1.414 1.414l.707.707zM5 10a1 1 0 01-1 1H3a1 1 0 110-2h1a1 1 0 011 1zM8 16v-1h4v1a2 2 0 11-4 0zM12 14c.015-.34.208-.646.477-.859a4 4 0 10-4.954 0c.27.213.462.519.477.859h4z" />
          </svg>
        ) : (
          <svg className="w-5 h-5 m-1.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        )}
      </div>
    );
  };

  // Game over screen
  if (gameState === "completed" && result) {
    return (
      <SignalSprintResults
        result={result}
        stats={stats}
        onPlayAgain={startGame}
        onBack={onComplete}
      />
    );
  }

  return (
    <div className="relative w-full max-w-md mx-auto aspect-[3/4] bg-[#0a0a0a] rounded-xl overflow-hidden border border-[#1a1a1a]">
      {/* HUD */}
      <SignalSprintHud
        score={stats.score}
        streak={stats.streak}
        timeLeft={timeLeft}
        maxTime={GAME_DURATION}
        gameState={gameState}
        onStart={startGame}
      />

      {/* Game Area */}
      {gameState === "playing" && (
        <>
          {/* Lane dividers */}
          <div className="absolute inset-0 flex">
            <div className="flex-1 border-r border-[#1a1a1a]" />
            <div className="flex-1 border-r border-[#1a1a1a]" />
            <div className="flex-1" />
          </div>

          {/* Objects */}
          {objects.map(renderObject)}

          {/* Player */}
          <div
            className="absolute bottom-8 w-12 h-12 transform -translate-x-1/2 transition-all duration-150"
            style={{
              left: playerLane === 0 ? "25%" : playerLane === 1 ? "50%" : "75%",
            }}
          >
            <div className="w-full h-full bg-white rounded-lg shadow-lg shadow-white/20 flex items-center justify-center">
              <svg className="w-8 h-8 text-[#0a0a0a]" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clipRule="evenodd" />
              </svg>
            </div>
          </div>

          {/* Touch controls */}
          <div className="absolute bottom-0 left-0 right-0 flex justify-between p-4">
            <button
              onClick={moveLeft}
              className="w-16 h-16 bg-[#1a1a1a] rounded-full flex items-center justify-center active:bg-[#2a2a2a]"
              aria-label="Move left"
            >
              <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </button>
            <button
              onClick={moveRight}
              className="w-16 h-16 bg-[#1a1a1a] rounded-full flex items-center justify-center active:bg-[#2a2a2a]"
              aria-label="Move right"
            >
              <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </>
      )}

      {/* Demo Mode Badge */}
      <div className="absolute top-16 left-2 px-2 py-1 bg-[#C9A24A]/20 border border-[#C9A24A]/40 rounded text-xs text-[#C9A24A]">
        DEMO MODE
      </div>
    </div>
  );
}
