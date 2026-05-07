export type GameState = 
  | "idle"
  | "active"
  | "paused"
  | "completed"
  | "failed";

export type QuestStatus = 
  | "available"
  | "active"
  | "completed"
  | "failed"
  | "expired";

export type QuestType = 
  | "tutorial"
  | "daily"
  | "weekly"
  | "story"
  | "challenge"
  | "achievement";

export type RewardType = 
  | "xp"
  | "credits"
  | "relic"
  | "realm_key"
  | "lee_wuh_blessing"
  | "title"
  | "badge";

export type Realm = {
  id: string;
  name: string;
  description: string;
  level: number;
  unlocked: boolean;
  requirements: {
    xp?: number;
    quests?: string[];
    relics?: string[];
    realms?: string[];
  };
  rewards: {
    xp: number;
    credits: number;
    unlocks: string[];
  };
  leeWuhPresence: "mentor" | "guide" | "guardian" | "stranger";
  environment: "peaceful" | "mysterious" | "challenging" | "sacred";
  createdAt: number;
};

export type Quest = {
  id: string;
  realmId: string;
  type: QuestType;
  title: string;
  description: string;
  objectives: QuestObjective[];
  rewards: QuestReward[];
  status: QuestStatus;
  difficulty: "easy" | "medium" | "hard" | "legendary";
  estimatedTime: number; // minutes
  requirements: {
    level?: number;
    quests?: string[];
    items?: string[];
  };
  leeWuhGuidance?: string;
  createdAt: number;
  startedAt?: number;
  completedAt?: number;
  expiresAt?: number;
};

export type QuestObjective = {
  id: string;
  description: string;
  type: "generate_clips" | "earn_credits" | "reach_level" | "collect_relic" | "complete_quest" | "social_action";
  target: number;
  current: number;
  completed: boolean;
  hidden?: boolean;
};

export type QuestReward = {
  type: RewardType;
  amount: number;
  description: string;
  rare: boolean;
};

export type PlayerState = {
  id: string;
  userId: string;
  currentRealm: string;
  level: number;
  xp: {
    current: number;
    total: number;
    nextLevel: number;
  };
  credits: number;
  relics: string[];
  realmKeys: string[];
  titles: string[];
  badges: string[];
  stats: {
    clipsGenerated: number;
    creditsEarned: number;
    questsCompleted: number;
    realmsUnlocked: number;
    playTime: number;
    achievements: number;
  };
  inventory: PlayerInventory;
  relationships: {
    leeWuh: number; // -100 to 100 friendship score
    realms: Record<string, number>; // realm affinity
  };
  preferences: {
    autoSave: boolean;
    notifications: boolean;
    leeWuhVoice: boolean;
    difficulty: "easy" | "normal" | "hard";
  };
  createdAt: number;
  lastActive: number;
  sessionTime: number;
};

export type PlayerInventory = {
  maxSlots: number;
  items: InventoryItem[];
};

export type InventoryItem = {
  id: string;
  type: "relic" | "key" | "consumable" | "equipment" | "cosmetic";
  name: string;
  description: string;
  rarity: "common" | "uncommon" | "rare" | "epic" | "legendary";
  quantity: number;
  usable: boolean;
  effects?: ItemEffect[];
  stackable: boolean;
};

export type ItemEffect = {
  type: "xp_boost" | "credit_bonus" | "quest_helper" | "revelation" | "protection";
  duration: number; // minutes
  value: number;
  description: string;
};

export type LeeWuhInteraction = {
  id: string;
  type: "dialogue" | "guidance" | "challenge" | "blessing" | "test";
  realmId: string;
  content: string;
  choices?: InteractionChoice[];
  requirements?: {
    level?: number;
    relics?: string[];
    friendship?: number;
  };
  rewards?: {
    xp?: number;
    credits?: number;
    items?: string[];
    friendship?: number;
  };
  triggered: boolean;
  createdAt: number;
};

export type InteractionChoice = {
  id: string;
  text: string;
  requirements?: {
    level?: number;
    items?: string[];
    stats?: Record<string, number>;
  };
  outcomes?: {
    success?: string;
    failure?: string;
    rewards?: QuestReward[];
    consequences?: string;
  };
};

export type SignalSprint = {
  id: string;
  name: string;
  description: string;
  duration: number; // minutes
  difficulty: "easy" | "medium" | "hard";
  objectives: SignalObjective[];
  rewards: SignalReward[];
  leaderboard: SignalLeaderboardEntry[];
  active: boolean;
  startsAt: number;
  endsAt: number;
  participantCount: number;
};

export type SignalObjective = {
  id: string;
  description: string;
  type: "speed" | "accuracy" | "creativity" | "engagement";
  target: number;
  points: number;
};

export type SignalReward = {
  rank: number;
  rewards: QuestReward[];
  title?: string;
};

export type SignalLeaderboardEntry = {
  userId: string;
  username: string;
  score: number;
  rank: number;
  completedAt?: number;
};

export type WorldConfig = {
  maxLevel: number;
  xpPerLevel: number[];
  startingCredits: number;
  maxInventorySlots: number;
  dailyQuestLimit: number;
  weeklyQuestLimit: number;
  realmUnlockRequirements: Record<string, any>;
  leeWuhFriendshipDecay: number; // per day
  autoSaveInterval: number; // minutes
};

// World Engine Implementation
export class WorldEngine {
  private playerStates: Map<string, PlayerState> = new Map();
  private realms: Map<string, Realm> = new Map();
  private quests: Map<string, Quest> = new Map();
  private interactions: Map<string, LeeWuhInteraction> = new Map();
  private signalSprints: Map<string, SignalSprint> = new Map();
  private config: WorldConfig;
  private eventCallbacks: Map<string, (event: WorldEvent) => void> = new Map();

  constructor(config?: Partial<WorldConfig>) {
    this.config = {
      maxLevel: 100,
      xpPerLevel: Array.from({ length: 100 }, (_, i) => 100 * (i + 1)),
      startingCredits: 100,
      maxInventorySlots: 20,
      dailyQuestLimit: 3,
      weeklyQuestLimit: 10,
      realmUnlockRequirements: {},
      leeWuhFriendshipDecay: 2, // 2 points per day
      autoSaveInterval: 5, // 5 minutes
      ...config,
    };

    this.initializeWorldData();
  }

  private initializeWorldData(): void {
    // Initialize realms
    const realms: Realm[] = [
      {
        id: "realm_1",
        name: "Genesis Realm",
        description: "The beginning of your journey with Lee-Wuh. A peaceful realm of learning and discovery.",
        level: 1,
        unlocked: true,
        requirements: {},
        rewards: { xp: 100, credits: 50, unlocks: ["realm_2"] },
        leeWuhPresence: "mentor",
        environment: "peaceful",
        createdAt: Date.now(),
      },
      {
        id: "realm_2",
        name: "Mystic Gardens",
        description: "A mysterious realm where ancient knowledge grows like flowers in an eternal garden.",
        level: 5,
        unlocked: false,
        requirements: { xp: 500, realms: ["realm_1"] },
        rewards: { xp: 250, credits: 150, unlocks: ["realm_3"] },
        leeWuhPresence: "guide",
        environment: "mysterious",
        createdAt: Date.now(),
      },
      {
        id: "realm_3",
        name: "Challenge Peaks",
        description: "A challenging realm that tests your skills and resolve. Only the worthy may pass.",
        level: 10,
        unlocked: false,
        requirements: { xp: 1500, quests: ["quest_tutorial_complete"], realms: ["realm_1", "realm_2"] },
        rewards: { xp: 500, credits: 300, unlocks: ["realm_4"] },
        leeWuhPresence: "guardian",
        environment: "challenging",
        createdAt: Date.now(),
      },
    ];

    realms.forEach(realm => {
      this.realms.set(realm.id, realm);
    });

    // Initialize quests
    const quests: Quest[] = [
      {
        id: "quest_tutorial",
        realmId: "realm_1",
        type: "tutorial",
        title: "First Steps",
        description: "Learn the basics of the LWA world and meet Lee-Wuh for the first time.",
        objectives: [
          {
            id: "obj_1",
            description: "Generate your first clip",
            type: "generate_clips",
            target: 1,
            current: 0,
            completed: false,
          },
          {
            id: "obj_2",
            description: "Speak with Lee-Wuh",
            type: "social_action",
            target: 1,
            current: 0,
            completed: false,
          },
        ],
        rewards: [
          { type: "xp", amount: 50, description: "Experience points", rare: false },
          { type: "credits", amount: 25, description: "Credits", rare: false },
          { type: "title", amount: 1, description: "Novice Creator", rare: false },
        ],
        status: "available",
        difficulty: "easy",
        estimatedTime: 10,
        requirements: {},
        leeWuhGuidance: "Welcome, young creator. I am Lee-Wuh, your guide in this realm. Let us begin your journey together.",
        createdAt: Date.now(),
      },
      {
        id: "quest_daily_1",
        realmId: "realm_1",
        type: "daily",
        title: "Daily Creation",
        description: "Create 3 clips to maintain your creative flow.",
        objectives: [
          {
            id: "obj_3",
            description: "Generate 3 clips",
            type: "generate_clips",
            target: 3,
            current: 0,
            completed: false,
          },
        ],
        rewards: [
          { type: "xp", amount: 25, description: "Experience points", rare: false },
          { type: "credits", amount: 15, description: "Credits", rare: false },
        ],
        status: "available",
        difficulty: "easy",
        estimatedTime: 15,
        requirements: {},
        createdAt: Date.now(),
        expiresAt: Date.now() + 24 * 60 * 60 * 1000,
      },
    ];

    quests.forEach(quest => {
      this.quests.set(quest.id, quest);
    });

    // Initialize interactions
    const interactions: LeeWuhInteraction[] = [
      {
        id: "interaction_first_meeting",
        type: "dialogue",
        realmId: "realm_1",
        content: "Welcome to the realm of creation. I am Lee-Wuh, your guide and mentor. Together, we will unlock your true potential as a creator.",
        choices: [
          {
            id: "choice_1",
            text: "I'm ready to learn!",
            outcomes: {
              success: "Lee-Wuh smiles knowingly. 'Excellent. Your journey begins now.'",
              rewards: [{ type: "xp", amount: 10, description: "Enthusiasm bonus", rare: false }],
            },
          },
          {
            id: "choice_2",
            text: "Tell me more about this realm.",
            outcomes: {
              success: "Lee-Wuh gestures to the surrounding landscape. 'This is a place of infinite possibility, limited only by your imagination.'",
            },
          },
        ],
        triggered: false,
        createdAt: Date.now(),
      },
    ];

    interactions.forEach(interaction => {
      this.interactions.set(interaction.id, interaction);
    });

    // Initialize signal sprint
    const signalSprint: SignalSprint = {
      id: "sprint_weekly_1",
      name: "Weekly Creator Sprint",
      description: "Generate as many high-quality clips as possible in 60 minutes!",
      duration: 60,
      difficulty: "medium",
      objectives: [
        {
          id: "signal_obj_1",
          description: "Generate clips",
          type: "speed",
          target: 10,
          points: 10,
        },
        {
          id: "signal_obj_2",
          description: "Achieve high scores",
          type: "accuracy",
          target: 5,
          points: 20,
        },
      ],
      rewards: [
        {
          rank: 1,
          rewards: [
            { type: "credits", amount: 500, description: "First place prize", rare: true },
            { type: "title", amount: 1, description: "Sprint Champion", rare: true },
          ],
        },
        {
          rank: 2,
          rewards: [
            { type: "credits", amount: 300, description: "Second place prize", rare: false },
          ],
        },
        {
          rank: 3,
          rewards: [
            { type: "credits", amount: 150, description: "Third place prize", rare: false },
          ],
        },
      ],
      leaderboard: [],
      active: false,
      startsAt: Date.now() + 24 * 60 * 60 * 1000, // Tomorrow
      endsAt: Date.now() + 24 * 60 * 60 * 1000 + 60 * 60 * 1000, // Tomorrow + 1 hour
      participantCount: 0,
    };

    this.signalSprints.set(signalSprint.id, signalSprint);
  }

  // Player State Management
  createPlayerState(userId: string): string {
    const playerStateId = `player_${userId}`;
    const playerState: PlayerState = {
      id: playerStateId,
      userId,
      currentRealm: "realm_1",
      level: 1,
      xp: {
        current: 0,
        total: 0,
        nextLevel: this.config.xpPerLevel[1],
      },
      credits: this.config.startingCredits,
      relics: [],
      realmKeys: ["realm_1"],
      titles: [],
      badges: [],
      stats: {
        clipsGenerated: 0,
        creditsEarned: 0,
        questsCompleted: 0,
        realmsUnlocked: 1,
        playTime: 0,
        achievements: 0,
      },
      inventory: {
        maxSlots: this.config.maxInventorySlots,
        items: [],
      },
      relationships: {
        leeWuh: 50, // Neutral starting point
        realms: {
          realm_1: 0,
        },
      },
      preferences: {
        autoSave: true,
        notifications: true,
        leeWuhVoice: true,
        difficulty: "normal",
      },
      createdAt: Date.now(),
      lastActive: Date.now(),
      sessionTime: 0,
    };

    this.playerStates.set(playerStateId, playerState);
    this.notifyEvent({ type: "player_created", data: playerState });
    return playerStateId;
  }

  getPlayerState(userId: string): PlayerState | undefined {
    return Array.from(this.playerStates.values()).find(state => state.userId === userId);
  }

  updatePlayerState(userId: string, updates: Partial<PlayerState>): boolean {
    const playerState = this.getPlayerState(userId);
    if (!playerState) return false;

    const updatedState = { ...playerState, ...updates, lastActive: Date.now() };
    this.playerStates.set(playerState.id, updatedState);
    this.notifyEvent({ type: "player_updated", data: updatedState });
    return true;
  }

  // Quest Management
  startQuest(userId: string, questId: string): boolean {
    const playerState = this.getPlayerState(userId);
    const quest = this.quests.get(questId);
    if (!playerState || !quest) return false;

    // Check requirements
    if (quest.requirements.level && playerState.level < quest.requirements.level) {
      return false;
    }

    quest.status = "active";
    quest.startedAt = Date.now();
    this.quests.set(questId, quest);

    this.notifyEvent({ type: "quest_started", data: { userId, quest } });
    return true;
  }

  updateQuestProgress(userId: string, questId: string, objectiveId: string, progress: number): boolean {
    const quest = this.quests.get(questId);
    if (!quest) return false;

    const objective = quest.objectives.find(obj => obj.id === objectiveId);
    if (!objective) return false;

    objective.current = Math.min(progress, objective.target);
    objective.completed = objective.current >= objective.target;

    // Check if quest is completed
    const allCompleted = quest.objectives.every(obj => obj.completed);
    if (allCompleted && quest.status === "active") {
      this.completeQuest(userId, questId);
    }

    this.quests.set(questId, quest);
    this.notifyEvent({ type: "quest_progress", data: { userId, quest, objective } });
    return true;
  }

  completeQuest(userId: string, questId: string): boolean {
    const playerState = this.getPlayerState(userId);
    const quest = this.quests.get(questId);
    if (!playerState || !quest) return false;

    quest.status = "completed";
    quest.completedAt = Date.now();

    // Award rewards
    quest.rewards.forEach(reward => {
      this.awardReward(userId, reward);
    });

    // Update player stats
    this.updatePlayerState(userId, {
      stats: {
        ...playerState.stats,
        questsCompleted: playerState.stats.questsCompleted + 1,
      },
    });

    this.quests.set(questId, quest);
    this.notifyEvent({ type: "quest_completed", data: { userId, quest } });
    return true;
  }

  private awardReward(userId: string, reward: QuestReward): void {
    const playerState = this.getPlayerState(userId);
    if (!playerState) return;

    switch (reward.type) {
      case "xp":
        this.addExperience(userId, reward.amount);
        break;
      case "credits":
        this.updatePlayerState(userId, {
          credits: playerState.credits + reward.amount,
          stats: {
            ...playerState.stats,
            creditsEarned: playerState.stats.creditsEarned + reward.amount,
          },
        });
        break;
      case "title":
        this.updatePlayerState(userId, {
          titles: [...playerState.titles, `title_${reward.amount}`],
        });
        break;
      case "badge":
        this.updatePlayerState(userId, {
          badges: [...playerState.badges, `badge_${reward.amount}`],
        });
        break;
      case "relic":
        this.addToInventory(userId, {
          id: `relic_${reward.amount}`,
          type: "relic",
          name: `Ancient Relic ${reward.amount}`,
          description: "A mysterious relic with unknown powers.",
          rarity: reward.rare ? "rare" : "common",
          quantity: 1,
          usable: true,
          stackable: false,
        });
        break;
    }
  }

  // Experience and Leveling
  addExperience(userId: string, amount: number): boolean {
    const playerState = this.getPlayerState(userId);
    if (!playerState) return false;

    let xpToAdd = amount;
    let levelsGained = 0;

    while (xpToAdd > 0 && playerState.level < this.config.maxLevel) {
      const xpNeeded = playerState.xp.nextLevel - playerState.xp.current;
      if (xpToAdd >= xpNeeded) {
        xpToAdd -= xpNeeded;
        playerState.xp.current = 0;
        playerState.xp.total += xpNeeded;
        playerState.level++;
        playerState.xp.nextLevel = this.config.xpPerLevel[playerState.level] || playerState.xp.nextLevel;
        levelsGained++;
      } else {
        playerState.xp.current += xpToAdd;
        playerState.xp.total += xpToAdd;
        xpToAdd = 0;
      }
    }

    this.updatePlayerState(userId, {
      xp: playerState.xp,
      level: playerState.level,
    });

    if (levelsGained > 0) {
      this.notifyEvent({ type: "level_up", data: { userId, levelsGained, newLevel: playerState.level } });
    }

    return true;
  }

  // Realm Management
  unlockRealm(userId: string, realmId: string): boolean {
    const playerState = this.getPlayerState(userId);
    const realm = this.realms.get(realmId);
    if (!playerState || !realm) return false;

    // Check requirements
    if (realm.requirements.xp && playerState.xp.total < realm.requirements.xp) {
      return false;
    }

    if (realm.requirements.realms && !realm.requirements.realms.every(r => playerState.realmKeys.includes(r))) {
      return false;
    }

    // Unlock realm
    realm.unlocked = true;
    this.realms.set(realmId, realm);

    this.updatePlayerState(userId, {
      realmKeys: [...playerState.realmKeys, realmId],
      stats: {
        ...playerState.stats,
        realmsUnlocked: playerState.stats.realmsUnlocked + 1,
      },
    });

    this.notifyEvent({ type: "realm_unlocked", data: { userId, realm } });
    return true;
  }

  travelToRealm(userId: string, realmId: string): boolean {
    const playerState = this.getPlayerState(userId);
    const realm = this.realms.get(realmId);
    if (!playerState || !realm || !realm.unlocked) return false;

    this.updatePlayerState(userId, { currentRealm: realmId });
    this.notifyEvent({ type: "realm_traveled", data: { userId, realm } });
    return true;
  }

  // Inventory Management
  addToInventory(userId: string, item: InventoryItem): boolean {
    const playerState = this.getPlayerState(userId);
    if (!playerState) return false;

    // Check if inventory is full
    if (playerState.inventory.items.length >= playerState.inventory.maxSlots) {
      return false;
    }

    // Check if item is stackable
    if (item.stackable) {
      const existingItem = playerState.inventory.items.find(i => i.id === item.id);
      if (existingItem) {
        existingItem.quantity += item.quantity;
      } else {
        playerState.inventory.items.push(item);
      }
    } else {
      playerState.inventory.items.push(item);
    }

    this.updatePlayerState(userId, { inventory: playerState.inventory });
    this.notifyEvent({ type: "item_added", data: { userId, item } });
    return true;
  }

  // Lee-Wuh Interaction
  triggerInteraction(userId: string, interactionId: string, choiceId?: string): boolean {
    const playerState = this.getPlayerState(userId);
    const interaction = this.interactions.get(interactionId);
    if (!playerState || !interaction) return false;

    if (interaction.triggered) return false;

    // Check requirements
    if (interaction.requirements?.level && playerState.level < interaction.requirements.level) {
      return false;
    }

    if (interaction.requirements?.friendship && playerState.relationships.leeWuh < interaction.requirements.friendship) {
      return false;
    }

    interaction.triggered = true;
    this.interactions.set(interactionId, interaction);

    // Process choice if provided
    if (choiceId && interaction.choices) {
      const choice = interaction.choices.find(c => c.id === choiceId);
      if (choice) {
        // Award choice rewards
        if (choice.outcomes?.rewards) {
          choice.outcomes.rewards.forEach(reward => {
            this.awardReward(userId, reward);
          });
        }

        // Update friendship
        if (interaction.rewards?.friendship) {
          this.updatePlayerState(userId, {
            relationships: {
              ...playerState.relationships,
              leeWuh: Math.max(-100, Math.min(100, playerState.relationships.leeWuh + interaction.rewards.friendship)),
            },
          });
        }
      }
    }

    this.notifyEvent({ type: "interaction_triggered", data: { userId, interaction, choiceId } });
    return true;
  }

  // Signal Sprint
  participateInSignalSprint(userId: string, sprintId: string): boolean {
    const sprint = this.signalSprints.get(sprintId);
    if (!sprint || !sprint.active) return false;

    // Add participant to leaderboard
    const existingEntry = sprint.leaderboard.find(entry => entry.userId === userId);
    if (!existingEntry) {
      sprint.leaderboard.push({
        userId,
        username: `user_${userId}`,
        score: 0,
        rank: sprint.leaderboard.length + 1,
      });
      sprint.participantCount++;
    }

    this.signalSprints.set(sprintId, sprint);
    this.notifyEvent({ type: "sprint_participated", data: { userId, sprint } });
    return true;
  }

  updateSprintScore(userId: string, sprintId: string, score: number): boolean {
    const sprint = this.signalSprints.get(sprintId);
    if (!sprint) return false;

    const entry = sprint.leaderboard.find(e => e.userId === userId);
    if (!entry) return false;

    entry.score += score;
    entry.completedAt = Date.now();

    // Re-rank leaderboard
    sprint.leaderboard.sort((a, b) => b.score - a.score);
    sprint.leaderboard.forEach((entry, index) => {
      entry.rank = index + 1;
    });

    this.signalSprints.set(sprintId, sprint);
    this.notifyEvent({ type: "sprint_score_updated", data: { userId, sprint, score } });
    return true;
  }

  // Analytics and Statistics
  getWorldStatistics(): {
    totalPlayers: number;
    activeRealms: number;
    totalQuests: number;
    completedQuests: number;
    averageLevel: number;
    totalPlayTime: number;
    signalSprintsActive: number;
    leeWuhFriendshipAverage: number;
  } {
    const players = Array.from(this.playerStates.values());
    const realms = Array.from(this.realms.values()).filter(r => r.unlocked);
    const quests = Array.from(this.quests.values());
    const completedQuests = quests.filter(q => q.status === "completed");
    const activeSprints = Array.from(this.signalSprints.values()).filter(s => s.active);

    const averageLevel = players.length > 0
      ? players.reduce((sum, player) => sum + player.level, 0) / players.length
      : 0;

    const totalPlayTime = players.reduce((sum, player) => sum + player.stats.playTime, 0);

    const leeWuhFriendshipAverage = players.length > 0
      ? players.reduce((sum, player) => sum + player.relationships.leeWuh, 0) / players.length
      : 0;

    return {
      totalPlayers: players.length,
      activeRealms: realms.length,
      totalQuests: quests.length,
      completedQuests: completedQuests.length,
      averageLevel,
      totalPlayTime,
      signalSprintsActive: activeSprints.length,
      leeWuhFriendshipAverage,
    };
  }

  // Event Management
  onEvent(eventType: string, callback: (event: WorldEvent) => void): () => void {
    const callbackId = `${eventType}_${Date.now()}`;
    this.eventCallbacks.set(callbackId, callback);
    return () => {
      this.eventCallbacks.delete(callbackId);
    };
  }

  private notifyEvent(event: WorldEvent): void {
    this.eventCallbacks.forEach(callback => {
      try {
        callback(event);
      } catch (error) {
        console.error("Error in world event callback:", error);
      }
    });
  }
}

// Types
export type WorldEvent = {
  type: string;
  data: any;
  timestamp?: number;
};

// Singleton Instance
export const worldEngine = new WorldEngine();
