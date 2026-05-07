export type TransactionType = 
  | "credit_purchase"
  | "subscription_payment"
  | "job_payment"
  | "refund"
  | "payout"
  | "bonus_credit"
  | "penalty_deduction"
  | "platform_fee";

export type TransactionStatus = 
  | "pending"
  | "processing"
  | "completed"
  | "failed"
  | "cancelled"
  | "disputed";

export type WalletType = 
  | "user"
  | "creator"
  | "platform"
  | "escrow";

export type EntitlementType = 
  | "basic_access"
  | "premium_features"
  | "unlimited_renders"
  | "priority_support"
  | "marketplace_access"
  | "advanced_analytics"
  | "api_access"
  | "whitelabel";

export type SubscriptionTier = 
  | "free"
  | "basic"
  | "pro"
  | "enterprise";

export type Transaction = {
  id: string;
  type: TransactionType;
  status: TransactionStatus;
  userId: string;
  amount: number;
  currency: string;
  description: string;
  metadata?: Record<string, any>;
  relatedId?: string; // Related job, subscription, etc.
  createdAt: number;
  processedAt?: number;
  completedAt?: number;
  failedAt?: number;
  gateway?: "stripe" | "whop" | "paypal" | "crypto";
  gatewayTransactionId?: string;
  fee?: number;
  netAmount?: number;
};

export type Wallet = {
  id: string;
  userId: string;
  type: WalletType;
  balance: number;
  currency: string;
  frozenBalance: number; // Held for disputes, pending transactions
  totalEarned: number;
  totalSpent: number;
  transactions: string[]; // Transaction IDs
  createdAt: number;
  updatedAt: number;
  lastActivity?: number;
};

export type Entitlement = {
  id: string;
  userId: string;
  type: EntitlementType;
  status: "active" | "inactive" | "expired" | "suspended";
  grantedAt: number;
  expiresAt?: number;
  source: "subscription" | "purchase" | "grant" | "achievement";
  sourceId?: string;
  usage?: {
    current: number;
    limit: number;
    period: "daily" | "weekly" | "monthly" | "lifetime";
    resetAt?: number;
  };
  metadata?: Record<string, any>;
};

export type Subscription = {
  id: string;
  userId: string;
  tier: SubscriptionTier;
  status: "active" | "cancelled" | "expired" | "past_due";
  currentPeriodStart: number;
  currentPeriodEnd: number;
  cancelAtPeriodEnd: boolean;
  amount: number;
  currency: string;
  interval: "month" | "year";
  entitlements: EntitlementType[];
  createdAt: number;
  updatedAt: number;
  gateway?: "stripe" | "whop";
  gatewaySubscriptionId?: string;
};

export type PayoutRequest = {
  id: string;
  userId: string;
  amount: number;
  currency: string;
  method: "bank_transfer" | "paypal" | "crypto" | "whop";
  destination: string;
  status: "pending" | "processing" | "completed" | "failed" | "cancelled";
  requestedAt: number;
  processedAt?: number;
  completedAt?: number;
  fee?: number;
  netAmount?: number;
  transactionId?: string;
  notes?: string;
  metadata?: Record<string, any>;
};

export type WalletConfig = {
  defaultCurrency: string;
  minimumBalance: number;
  maximumBalance: number;
  transactionFee: number;
  payoutFee: number;
  disputeHoldPeriod: number;
  subscriptionGracePeriod: number;
  supportedCurrencies: string[];
  supportedGateways: string[];
};

// Wallet Engine Implementation
export class WalletEngine {
  private wallets: Map<string, Wallet> = new Map();
  private transactions: Map<string, Transaction> = new Map();
  private entitlements: Map<string, Entitlement> = new Map();
  private subscriptions: Map<string, Subscription> = new Map();
  private payoutRequests: Map<string, PayoutRequest> = new Map();
  private config: WalletConfig;
  private eventCallbacks: Map<string, (event: WalletEvent) => void> = new Map();

  constructor(config?: Partial<WalletConfig>) {
    this.config = {
      defaultCurrency: "USD",
      minimumBalance: 0,
      maximumBalance: 10000,
      transactionFee: 0.029, // 2.9%
      payoutFee: 0.05, // 5%
      disputeHoldPeriod: 7 * 24 * 60 * 60 * 1000, // 7 days
      subscriptionGracePeriod: 3 * 24 * 60 * 60 * 1000, // 3 days
      supportedCurrencies: ["USD", "EUR", "GBP"],
      supportedGateways: ["stripe", "whop", "paypal"],
      ...config,
    };

    this.initializeMockData();
  }

  private initializeMockData(): void {
    // Initialize mock user wallets
    const mockWallets: Wallet[] = [
      {
        id: "wallet_user_1",
        userId: "user_1",
        type: "user",
        balance: 150.00,
        currency: "USD",
        frozenBalance: 25.00,
        totalEarned: 0,
        totalSpent: 125.00,
        transactions: [],
        createdAt: Date.now() - 30 * 24 * 60 * 60 * 1000,
        updatedAt: Date.now(),
        lastActivity: Date.now(),
      },
      {
        id: "wallet_creator_1",
        userId: "creator_1",
        type: "creator",
        balance: 2450.75,
        currency: "USD",
        frozenBalance: 150.00,
        totalEarned: 5000.00,
        totalSpent: 500.00,
        transactions: [],
        createdAt: Date.now() - 60 * 24 * 60 * 60 * 1000,
        updatedAt: Date.now(),
        lastActivity: Date.now(),
      },
    ];

    mockWallets.forEach(wallet => {
      this.wallets.set(wallet.id, wallet);
    });
  }

  // Wallet Management
  createWallet(userId: string, type: WalletType, currency: string = this.config.defaultCurrency): string {
    const walletId = `wallet_${type}_${userId}`;
    const wallet: Wallet = {
      id: walletId,
      userId,
      type,
      balance: 0,
      currency,
      frozenBalance: 0,
      totalEarned: 0,
      totalSpent: 0,
      transactions: [],
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };

    this.wallets.set(walletId, wallet);
    this.notifyEvent({ type: "wallet_created", data: wallet });
    return walletId;
  }

  getWallet(userId: string, type?: WalletType): Wallet | undefined {
    if (type) {
      return Array.from(this.wallets.values()).find(w => w.userId === userId && w.type === type);
    }
    return Array.from(this.wallets.values()).find(w => w.userId === userId);
  }

  getWalletById(walletId: string): Wallet | undefined {
    return this.wallets.get(walletId);
  }

  getAllWallets(): Wallet[] {
    return Array.from(this.wallets.values());
  }

  updateWallet(walletId: string, updates: Partial<Wallet>): boolean {
    const wallet = this.wallets.get(walletId);
    if (!wallet) return false;

    const updatedWallet = { ...wallet, ...updates, updatedAt: Date.now() };
    this.wallets.set(walletId, updatedWallet);
    this.notifyEvent({ type: "wallet_updated", data: updatedWallet });
    return true;
  }

  // Transaction Management
  createTransaction(
    type: TransactionType,
    userId: string,
    amount: number,
    description: string,
    options?: {
      currency?: string;
      relatedId?: string;
      gateway?: "stripe" | "whop" | "paypal" | "crypto";
      metadata?: Record<string, any>;
    }
  ): string {
    const transactionId = `txn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    const transaction: Transaction = {
      id: transactionId,
      type,
      status: "pending",
      userId,
      amount,
      currency: options?.currency || this.config.defaultCurrency,
      description,
      relatedId: options?.relatedId,
      metadata: options?.metadata,
      createdAt: Date.now(),
      gateway: options?.gateway,
    };

    // Calculate fee
    if (type === "job_payment" || type === "payout") {
      transaction.fee = amount * this.config.payoutFee;
    } else {
      transaction.fee = amount * this.config.transactionFee;
    }
    transaction.netAmount = amount - transaction.fee;

    this.transactions.set(transactionId, transaction);
    this.notifyEvent({ type: "transaction_created", data: transaction });
    return transactionId;
  }

  getTransaction(transactionId: string): Transaction | undefined {
    return this.transactions.get(transactionId);
  }

  getTransactionsByUser(userId: string): Transaction[] {
    return Array.from(this.transactions.values()).filter(tx => tx.userId === userId);
  }

  getAllTransactions(): Transaction[] {
    return Array.from(this.transactions.values());
  }

  updateTransaction(transactionId: string, updates: Partial<Transaction>): boolean {
    const transaction = this.transactions.get(transactionId);
    if (!transaction) return false;

    const updatedTransaction = { ...transaction, ...updates };
    this.transactions.set(transactionId, updatedTransaction);
    this.notifyEvent({ type: "transaction_updated", data: updatedTransaction });
    return true;
  }

  // Balance Operations
  async processTransaction(transactionId: string): Promise<boolean> {
    const transaction = this.getTransaction(transactionId);
    if (!transaction) return false;

    this.updateTransaction(transactionId, { status: "processing" });

    // Simulate processing delay
    await new Promise(resolve => setTimeout(resolve, 1000 + Math.random() * 2000));

    const wallet = this.getWallet(transaction.userId);
    if (!wallet) {
      this.updateTransaction(transactionId, { 
        status: "failed", 
        failedAt: Date.now(),
        description: transaction.description + " - Wallet not found"
      });
      return false;
    }

    // Check balance for debits
    if (transaction.amount < 0 && wallet.balance < Math.abs(transaction.amount)) {
      this.updateTransaction(transactionId, { 
        status: "failed", 
        failedAt: Date.now(),
        description: transaction.description + " - Insufficient balance"
      });
      return false;
    }

    // Process the transaction
    const success = Math.random() > 0.1; // 90% success rate

    if (success) {
      // Update wallet balance
      const newBalance = wallet.balance + transaction.netAmount!;
      const newTotalSpent = transaction.amount < 0 ? wallet.totalSpent + Math.abs(transaction.amount) : wallet.totalSpent;
      const newTotalEarned = transaction.amount > 0 ? wallet.totalEarned + transaction.amount : wallet.totalEarned;

      this.updateWallet(wallet.id, {
        balance: newBalance,
        totalSpent: newTotalSpent,
        totalEarned: newTotalEarned,
        lastActivity: Date.now(),
      });

      // Add transaction to wallet
      wallet.transactions.push(transactionId);

      this.updateTransaction(transactionId, {
        status: "completed",
        processedAt: Date.now(),
        completedAt: Date.now(),
      });

      return true;
    } else {
      this.updateTransaction(transactionId, { 
        status: "failed", 
        failedAt: Date.now(),
        description: transaction.description + " - Processing failed"
      });
      return false;
    }
  }

  // Entitlement Management
  grantEntitlement(
    userId: string,
    type: EntitlementType,
    source: "subscription" | "purchase" | "grant" | "achievement",
    sourceId?: string,
    expiresAt?: number,
    usage?: {
      limit: number;
      period: "daily" | "weekly" | "monthly" | "lifetime";
    }
  ): string {
    const entitlementId = `ent_${userId}_${type}_${Date.now()}`;
    const entitlement: Entitlement = {
      id: entitlementId,
      userId,
      type,
      status: "active",
      grantedAt: Date.now(),
      expiresAt,
      source,
      sourceId,
      usage: usage ? {
        current: 0,
        limit: usage.limit,
        period: usage.period,
        resetAt: this.calculateNextReset(usage.period),
      } : undefined,
    };

    this.entitlements.set(entitlementId, entitlement);
    this.notifyEvent({ type: "entitlement_granted", data: entitlement });
    return entitlementId;
  }

  getEntitlementsByUser(userId: string): Entitlement[] {
    return Array.from(this.entitlements.values()).filter(ent => ent.userId === userId);
  }

  hasEntitlement(userId: string, type: EntitlementType): boolean {
    const entitlements = this.getEntitlementsByUser(userId);
    return entitlements.some(ent => 
      ent.type === type && 
      ent.status === "active" && 
      (!ent.expiresAt || ent.expiresAt > Date.now())
    );
  }

  useEntitlement(entitlementId: string, amount: number = 1): boolean {
    const entitlement = this.entitlements.get(entitlementId);
    if (!entitlement || entitlement.status !== "active") return false;

    if (entitlement.usage) {
      // Check if usage needs reset
      if (entitlement.usage.resetAt && Date.now() > entitlement.usage.resetAt) {
        entitlement.usage.current = 0;
        entitlement.usage.resetAt = this.calculateNextReset(entitlement.usage.period);
      }

      // Check limit
      if (entitlement.usage.current + amount > entitlement.usage.limit) {
        return false;
      }

      entitlement.usage.current += amount;
      this.entitlements.set(entitlementId, entitlement);
      this.notifyEvent({ type: "entitlement_used", data: entitlement });
      return true;
    }

    return true;
  }

  private calculateNextReset(period: "daily" | "weekly" | "monthly" | "lifetime"): number | undefined {
    const now = Date.now();
    switch (period) {
      case "daily":
        return new Date(now).setHours(24, 0, 0, 0);
      case "weekly":
        return new Date(now).setDate(new Date(now).getDate() + 7);
      case "monthly":
        return new Date(now).setMonth(new Date(now).getMonth() + 1);
      case "lifetime":
        return undefined;
    }
  }

  // Subscription Management
  createSubscription(
    userId: string,
    tier: SubscriptionTier,
    amount: number,
    interval: "month" | "year",
    gateway?: "stripe" | "whop"
  ): string {
    const subscriptionId = `sub_${userId}_${Date.now()}`;
    const now = Date.now();
    const periodEnd = interval === "month" 
      ? now + 30 * 24 * 60 * 60 * 1000
      : now + 365 * 24 * 60 * 60 * 1000;

    const subscription: Subscription = {
      id: subscriptionId,
      userId,
      tier,
      status: "active",
      currentPeriodStart: now,
      currentPeriodEnd: periodEnd,
      cancelAtPeriodEnd: false,
      amount,
      currency: this.config.defaultCurrency,
      interval,
      entitlements: this.getEntitlementsForTier(tier),
      createdAt: now,
      updatedAt: now,
      gateway,
    };

    this.subscriptions.set(subscriptionId, subscription);
    
    // Grant entitlements
    subscription.entitlements.forEach(entitlementType => {
      this.grantEntitlement(userId, entitlementType, "subscription", subscriptionId, subscription.currentPeriodEnd);
    });

    this.notifyEvent({ type: "subscription_created", data: subscription });
    return subscriptionId;
  }

  private getEntitlementsForTier(tier: SubscriptionTier): EntitlementType[] {
    switch (tier) {
      case "free":
        return ["basic_access"];
      case "basic":
        return ["basic_access", "marketplace_access"];
      case "pro":
        return ["basic_access", "marketplace_access", "unlimited_renders", "priority_support"];
      case "enterprise":
        return ["basic_access", "marketplace_access", "unlimited_renders", "priority_support", "advanced_analytics", "api_access", "whitelabel"];
      default:
        return [];
    }
  }

  getSubscription(userId: string): Subscription | undefined {
    return Array.from(this.subscriptions.values()).find(sub => sub.userId === userId && sub.status === "active");
  }

  cancelSubscription(subscriptionId: string): boolean {
    const subscription = this.subscriptions.get(subscriptionId);
    if (!subscription) return false;

    subscription.status = "cancelled";
    subscription.cancelAtPeriodEnd = true;
    subscription.updatedAt = Date.now();

    this.notifyEvent({ type: "subscription_cancelled", data: subscription });
    return true;
  }

  // Payout Management
  requestPayout(
    userId: string,
    amount: number,
    method: "bank_transfer" | "paypal" | "crypto" | "whop",
    destination: string,
    notes?: string
  ): string {
    const payoutId = `payout_${userId}_${Date.now()}`;
    const fee = amount * this.config.payoutFee;
    const netAmount = amount - fee;

    const payout: PayoutRequest = {
      id: payoutId,
      userId,
      amount,
      currency: this.config.defaultCurrency,
      method,
      destination,
      status: "pending",
      requestedAt: Date.now(),
      fee,
      netAmount,
      notes,
    };

    this.payoutRequests.set(payoutId, payout);
    
    // Freeze the amount in wallet
    const wallet = this.getWallet(userId, "creator");
    if (wallet && wallet.balance >= amount) {
      this.updateWallet(wallet.id, {
        balance: wallet.balance - amount,
        frozenBalance: wallet.frozenBalance + amount,
      });
    }

    this.notifyEvent({ type: "payout_requested", data: payout });
    return payoutId;
  }

  getPayoutRequestsByUser(userId: string): PayoutRequest[] {
    return Array.from(this.payoutRequests.values()).filter(payout => payout.userId === userId);
  }

  async processPayout(payoutId: string): Promise<boolean> {
    const payout = this.payoutRequests.get(payoutId);
    if (!payout) return false;

    this.updatePayout(payoutId, { status: "processing" });

    // Simulate processing
    await new Promise(resolve => setTimeout(resolve, 2000 + Math.random() * 3000));

    const success = Math.random() > 0.05; // 95% success rate

    if (success) {
      // Release frozen balance
      const wallet = this.getWallet(payout.userId, "creator");
      if (wallet) {
        this.updateWallet(wallet.id, {
          frozenBalance: wallet.frozenBalance - payout.amount,
        });
      }

      this.updatePayout(payoutId, {
        status: "completed",
        processedAt: Date.now(),
        completedAt: Date.now(),
      });

      // Create transaction record
      this.createTransaction("payout", payout.userId, -payout.amount, `Payout to ${payout.method}`, {
        relatedId: payoutId,
      });

      return true;
    } else {
      // Return frozen balance
      const wallet = this.getWallet(payout.userId, "creator");
      if (wallet) {
        this.updateWallet(wallet.id, {
          frozenBalance: wallet.frozenBalance - payout.amount,
          balance: wallet.balance + payout.amount,
        });
      }

      this.updatePayout(payoutId, { status: "failed" });
      return false;
    }
  }

  private updatePayout(payoutId: string, updates: Partial<PayoutRequest>): boolean {
    const payout = this.payoutRequests.get(payoutId);
    if (!payout) return false;

    const updatedPayout = { ...payout, ...updates };
    this.payoutRequests.set(payoutId, updatedPayout);
    this.notifyEvent({ type: "payout_updated", data: updatedPayout });
    return true;
  }

  // Analytics and Statistics
  getWalletStatistics(): {
    totalWallets: number;
    totalBalance: number;
    totalFrozen: number;
    totalTransactions: number;
    totalVolume: number;
    totalFees: number;
    transactionsByType: Record<TransactionType, number>;
    transactionsByStatus: Record<TransactionStatus, number>;
    activeSubscriptions: number;
    totalSubscriptions: number;
    pendingPayouts: number;
    totalPayouts: number;
  } {
    const wallets = this.getAllWallets();
    const transactions = this.getAllTransactions();
    const subscriptions = Array.from(this.subscriptions.values());
    const payouts = Array.from(this.payoutRequests.values());

    const totalBalance = wallets.reduce((sum, wallet) => sum + wallet.balance, 0);
    const totalFrozen = wallets.reduce((sum, wallet) => sum + wallet.frozenBalance, 0);
    const totalVolume = transactions.reduce((sum, tx) => sum + Math.abs(tx.amount), 0);
    const totalFees = transactions.reduce((sum, tx) => sum + (tx.fee || 0), 0);

    const transactionsByType = transactions.reduce((acc, tx) => {
      acc[tx.type] = (acc[tx.type] || 0) + 1;
      return acc;
    }, {} as Record<TransactionType, number>);

    const transactionsByStatus = transactions.reduce((acc, tx) => {
      acc[tx.status] = (acc[tx.status] || 0) + 1;
      return acc;
    }, {} as Record<TransactionStatus, number>);

    const activeSubscriptions = subscriptions.filter(sub => sub.status === "active").length;
    const pendingPayouts = payouts.filter(payout => payout.status === "pending").length;

    return {
      totalWallets: wallets.length,
      totalBalance,
      totalFrozen,
      totalTransactions: transactions.length,
      totalVolume,
      totalFees,
      transactionsByType,
      transactionsByStatus,
      activeSubscriptions,
      totalSubscriptions: subscriptions.length,
      pendingPayouts,
      totalPayouts: payouts.length,
    };
  }

  // Event Management
  onEvent(eventType: string, callback: (event: WalletEvent) => void): () => void {
    const callbackId = `${eventType}_${Date.now()}`;
    this.eventCallbacks.set(callbackId, callback);
    return () => {
      this.eventCallbacks.delete(callbackId);
    };
  }

  private notifyEvent(event: WalletEvent): void {
    this.eventCallbacks.forEach(callback => {
      try {
        callback(event);
      } catch (error) {
        console.error("Error in wallet event callback:", error);
      }
    });
  }
}

// Types
export type WalletEvent = {
  type: string;
  data: any;
  timestamp?: number;
};

// Singleton Instance
export const walletEngine = new WalletEngine();
