# LWA Whop Entitlement Verification Runbook

## Overview

This runbook verifies the Whop paid-access, subscription, and customer entitlement flow to ensure LWA can sell access cleanly and accurately enforce paid features.

## Current Whop Flow Architecture

### Backend Components
- **Webhook Endpoint**: `/v1/webhooks/whop` - Receives Whop subscription events
- **Entitlement Store**: SQLite database for webhook events and user plan tracking
- **Plan Resolution**: Maps webhook events to user plan status (free/pro/scale)
- **Credit Gating**: Daily quota enforcement based on user plan

### Frontend Components
- **Pricing Page**: `/pricing` - Displays plans and current entitlement status
- **Plan Display**: Shows user's current plan and entitlement source
- **Mock Data Fallback**: Uses mock data when API calls fail

### Integration Points
- **Railway Backend**: `https://lwa-backend-production-c9cc.up.railway.app`
- **Whop Storefront**: `https://whop.com/lwa-app/lwa-ai-content-repurposer`
- **Webhook Processing**: Signature verification and event deduplication

## Required Environment Variables

### Backend Whop Configuration
```bash
# Required for Whop integration
WHOP_API_KEY=whop_your_api_key
WHOP_WEBHOOK_SECRET=whop_your_webhook_secret
WHOP_COMPANY_ID=your_whop_company_id
WHOP_PRODUCT_ID=your_whop_product_id

# Enable/disable Whop verification
ENABLE_WHOP_VERIFICATION=true

# Database for webhook events
PLATFORM_DB_PATH=/data/platform.db
```

### Frontend Configuration
```bash
# API endpoints
NEXT_PUBLIC_API_BASE_URL=https://lwa-backend-production-c9cc.up.railway.app
NEXT_PUBLIC_BACKEND_URL=https://lwa-backend-production-c9cc.up.railway.app
```

### Railway Service Configuration
```bash
# Railway deployment
RAILWAY_TOKEN=your_railway_token
RAILWAY_ENVIRONMENT=production
```

## Webhook Routes and Processing

### Primary Webhook Endpoint
- **Route**: `POST /v1/webhooks/whop`
- **Authentication**: HMAC-SHA256 signature verification
- **Headers**: `whop-signature`, `x-whop-signature`, or `x-signature`
- **Payload**: JSON event data from Whop

### Event Processing Logic
1. **Signature Verification**: Validate webhook authenticity
2. **Event Deduplication**: Prevent duplicate processing
3. **User Identification**: Extract user email from event data
4. **Plan Resolution**: Map event type to plan status
5. **Database Update**: Update user plan in local database

### Supported Event Types
- **Valid Events**: `valid`, `paid`, `succeeded`, `active`, `created`, `renewed` → `pro` plan
- **Invalid Events**: `invalid`, `cancel`, `failed`, `expired`, `deleted`, `refunded`, `chargeback` → `free` plan

## Checkout and Paywall Flow

### Current State
- **No Live Checkout**: Frontend shows pricing page but no actual checkout integration
- **Mock Data**: Uses mock entitlement data when API calls fail
- **Plan Display**: Shows current entitlement status but no upgrade flow

### Missing Components
- **Checkout Links**: No direct Whop checkout integration
- **Payment Processing**: No frontend payment flow
- **Plan Upgrade UI**: No upgrade buttons or flows
- **Webhook Testing**: No webhook testing interface

## User States and Entitlement Decision Points

### User State Classification
1. **Unauthenticated**: No authentication token
2. **Free Plan**: Basic access with daily limits
3. **Pro Plan**: Paid access with higher limits
4. **Expired Plan**: Previously paid, now expired
5. **Webhook Failed**: Entitlement sync issues

### Entitlement Decision Logic
```python
# Priority order for plan resolution
1. API Key (Scale) > API Key (Pro) > User Plan > Free Launch IP > Free IP
2. Daily quota enforcement based on plan
3. Feature flag access based on plan level
```

### Plan Benefits
- **Free**: 5 generations/day, basic features
- **Pro**: 25 generations/day, premium exports, wallet view
- **Scale**: 100 generations/day, campaign mode, batch processing

## Manual Testing Checklist

### Backend Verification
- [ ] Whop webhook endpoint responds to POST requests
- [ ] Webhook signature verification works
- [ ] Event processing updates user plans correctly
- [ ] Database stores webhook events properly
- [ ] Plan resolution logic functions correctly

### Frontend Verification
- [ ] Pricing page loads and displays plans
- [ ] Current entitlement status shows correctly
- [ ] Mock data fallback works when API fails
- [ ] Plan features display accurately
- [ ] User authentication flows work

### Integration Testing
- [ ] Webhook events from Whop are received
- [ ] User plan updates reflect in frontend
- [ ] Credit quota enforcement works per plan
- [ ] Feature flags enforce plan restrictions
- [ ] Error handling works gracefully

### Railway Environment
- [ ] Backend URL is accessible and healthy
- [ ] Environment variables are configured
- [ ] Database persistence works across restarts
- [ ] SSL certificates are valid
- [ ] Health checks pass

## Railway Environment Variable Checklist

### Required Variables
```bash
# Whop Integration
WHOP_API_KEY=✅ Set
WHOP_WEBHOOK_SECRET=✅ Set
WHOP_COMPANY_ID=✅ Set
WHOP_PRODUCT_ID=✅ Set
ENABLE_WHOP_VERIFICATION=✅ Set

# Database
PLATFORM_DB_PATH=✅ Set

# API Configuration
API_KEY_HEADER_NAME=x-api-key
CLIENT_ID_HEADER_NAME=x-client-id
```

### Optional Variables
```bash
# Free Launch Mode
FREE_LAUNCH_MODE=false

# High Volume Features
ENABLE_HIGH_VOLUME_CLIPS=false
HIGH_VOLUME_MAX_CLIPS=50

# Rate Limiting
FREE_DAILY_LIMIT=5
PRO_DAILY_LIMIT=25
SCALE_DAILY_LIMIT=100
```

## What Must Not Be Claimed Publicly

### Live Features
- ❌ "Live payments" - No checkout integration exists
- ❌ "Paid subscriptions" - No actual payment processing
- ❌ "Real-time entitlement sync" - Webhook processing is basic
- ❌ "Premium features unlocked" - No actual upgrade flow

### Capabilities
- ❌ "Instant plan upgrades" - No frontend upgrade flow
- ❌ "Automatic billing" - No billing integration
- ❌ "Payment processing" - No payment gateway integration
- ❌ "Subscription management" - No subscription UI

### Accurate Claims
- ✅ "Plan-based access control" - Entitlement system works
- ✅ "Daily quota enforcement" - Credit gating works
- ✅ "Feature flag management" - Plan-based features work
- ✅ "Webhook event processing" - Basic webhook handling works

## Implementation Gaps Identified

### Critical Gaps
1. **Frontend Checkout Integration**: No actual checkout flow
2. **Payment Processing**: No payment gateway integration
3. **Plan Upgrade UI**: No upgrade buttons or flows
4. **Webhook Testing**: No testing interface
5. **Error Recovery**: Limited error handling for webhook failures

### Minor Gaps
1. **Entitlement API**: Frontend lacks getMyEntitlement/listPlans API calls
2. **Plan Management**: No plan cancellation or change flows
3. **Billing History**: No billing or payment history display
4. **Customer Support**: No support tools for entitlement issues

### Recommended Next Steps
1. **Implement Frontend Checkout**: Add Whop checkout integration
2. **Create Upgrade Flow**: Build plan upgrade UI
3. **Add Webhook Testing**: Create webhook testing interface
4. **Enhance Error Handling**: Improve webhook failure recovery
5. **Add Billing Management**: Create subscription management UI

## Code Changes Needed

### Frontend API Implementation
```typescript
// Add to lib/worlds/api.ts
export async function getMyEntitlement(): Promise<UserEntitlement> {
  return mapUserEntitlement(await request<BackendEntitlement>("/worlds/entitlement/me"));
}

export async function listPlans(): Promise<BillingPlan[]> {
  const result = await request<BackendBillingPlan[]>("/worlds/plans");
  return result.map(mapBillingPlan);
}
```

### Backend API Routes
```python
# Add to app/api/routes/
GET /worlds/entitlement/me  # Return current user entitlement
GET /worlds/plans           # Return available plans
POST /worlds/plans/upgrade  # Initiate plan upgrade (future)
```

### Frontend Checkout Integration
```typescript
// Add checkout buttons to PricingPlans component
const handleCheckout = (planKey: string) => {
  // Redirect to Whop checkout
  window.open(`https://whop.com/checkout/${planKey}`, '_blank');
};
```

## Safety and Compliance Notes

### Security Considerations
- **Webhook Security**: All webhooks must be signature verified
- **API Key Protection**: API keys must be stored securely
- **Data Privacy**: User plan data must be protected
- **Rate Limiting**: Prevent abuse of entitlement checks

### Compliance Requirements
- **Payment Processing**: Must comply with payment regulations
- **Data Protection**: Must comply with GDPR/CCPA
- **Consumer Protection**: Must provide clear cancellation options
- **Tax Compliance**: Must handle tax calculations correctly

### Risk Mitigation
- **Webhook Failures**: Implement retry logic and fallbacks
- **Payment Disputes**: Clear refund and dispute policies
- **Plan Changes**: Graceful handling of plan downgrades
- **Service Outages**: Fallback to free plan during outages

## Monitoring and Alerting

### Key Metrics
- **Webhook Success Rate**: > 95% webhook processing success
- **Plan Sync Accuracy**: > 99% plan status accuracy
- **Entitlement API Response**: < 500ms average response time
- **Error Rate**: < 1% entitlement check failures

### Alerting Triggers
- **Webhook Failures**: > 5% webhook failure rate
- **Plan Sync Issues**: Entitlement database inconsistencies
- **API Errors**: > 2% entitlement API error rate
- **Payment Issues**: Failed payment notifications

## Testing Procedures

### Manual Testing
1. **Webhook Testing**: Send test webhook events from Whop dashboard
2. **Plan Testing**: Verify plan changes reflect correctly
3. **Quota Testing**: Test daily quota enforcement
4. **Feature Testing**: Verify feature flag enforcement

### Automated Testing
1. **Unit Tests**: Test entitlement resolution logic
2. **Integration Tests**: Test webhook processing
3. **End-to-End Tests**: Test complete entitlement flow
4. **Load Tests**: Test performance under load

## Documentation Requirements

### Technical Documentation
- **API Documentation**: Document entitlement API endpoints
- **Webhook Documentation**: Document webhook event format
- **Configuration Guide**: Document environment variables
- **Troubleshooting Guide**: Document common issues

### User Documentation
- **Plan Comparison**: Document plan differences
- **Upgrade Guide**: Document how to upgrade plans
- **Billing FAQ**: Document billing questions
- **Support Guide**: Document how to get help

## Conclusion

The Whop entitlement system has a solid foundation with webhook processing, plan resolution, and quota enforcement working correctly. However, critical frontend components for checkout and plan management are missing, preventing a complete paid access flow.

The next phase should focus on implementing the frontend checkout integration and plan upgrade flows to create a complete monetization system.

**Priority**: High - Complete checkout integration
**Risk**: Medium - Core functionality works, missing user-facing features
**Timeline**: 2-3 weeks for complete implementation
