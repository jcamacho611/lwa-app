# LWA Environment Variables

## Overview

This document catalogs all environment variables required for LWA's API integrations, organized by tier and implementation status. Variables are marked with their security level and implementation requirements.

## Security Levels

- **Public**: Safe to expose in client-side code
- **Secret**: Must never be exposed in client-side code
- **Internal**: Used only in backend/services
- **High Risk**: Requires special handling and compliance

## Tier 1 — Core Product Environment Variables

### LWA Backend API
```bash
# Public
NEXT_PUBLIC_API_BASE_URL=https://api.lwa.ai
NEXT_PUBLIC_BACKEND_URL=https://api.lwa.ai

# Internal
BACKEND_URL=https://api.lwa.ai
```

### Storage (S3/R2/Supabase)
```bash
# Secret
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
S3_BUCKET=lwa-assets
R2_ENDPOINT=https://your-account.r2.cloudflarestorage.com
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_key
```

### Redis/RQ/Celery/Railway Workers
```bash
# Internal
REDIS_URL=redis://localhost:6379
RAILWAY_TOKEN=your_railway_token
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379
```

### FFmpeg Media Pipeline
```bash
# Internal
FFMPEG_PATH=/usr/bin/ffmpeg
FFPROBE_PATH=/usr/bin/ffprobe
MEDIA_TEMP_DIR=/tmp/lwa-media
MAX_VIDEO_SIZE=1073741824  # 1GB in bytes
MAX_CONVERSION_TIME=300     # 5 minutes in seconds
```

### Transcription APIs
```bash
# Secret - Choose one or more
OPENAI_API_KEY=sk-openai-api-key
ASSEMBLYAI_API_KEY=your_assemblyai_key
DEEPGRAM_API_KEY=your_deepgram_key

# Internal
TRANSCRIPTION_PROVIDER=openai  # openai | assemblyai | deepgram
TRANSCRIPTION_MODEL=whisper-1
MAX_AUDIO_LENGTH=3600  # 1 hour in seconds
```

### LLM APIs
```bash
# Secret - Choose one or more
OPENAI_API_KEY=sk-openai-api-key
ANTHROPIC_API_KEY=sk-ant-api-key

# Internal
LLM_PROVIDER=openai  # openai | anthropic
LLM_MODEL=gpt-4-turbo
LLM_MAX_TOKENS=4000
LLM_TEMPERATURE=0.7
RATE_LIMIT_REQUESTS_PER_MINUTE=60
```

### Analytics (PostHog)
```bash
# Public
NEXT_PUBLIC_POSTHOG_HOST=https://app.posthog.com

# Secret
POSTHOG_API_KEY=phc_your_posthog_key
POSTHOG_PROJECT_ID=your_project_id
```

## Tier 2 — Premium Clipping Engine Environment Variables

### YouTube Data API
```bash
# Secret
YOUTUBE_API_KEY=your_youtube_api_key

# Internal
YOUTUBE_API_QUOTA_LIMIT=10000  # Daily quota
YOUTUBE_MAX_VIDEO_DURATION=7200  # 2 hours in seconds
```

### Social Posting APIs
```bash
# Secret - High Risk
TIKTOK_API_KEY=your_tiktok_api_key
TIKTOK_API_SECRET=your_tiktok_api_secret
INSTAGRAM_API_KEY=your_instagram_api_key
INSTAGRAM_API_SECRET=your_instagram_api_secret
YOUTUBE_API_KEY=your_youtube_api_key
YOUTUBE_CLIENT_ID=your_youtube_client_id
YOUTUBE_CLIENT_SECRET=your_youtube_client_secret

# Internal
SOCIAL_POSTING_RATE_LIMIT=10  # Posts per minute
SOCIAL_POSTING_MAX_RETRIES=3
```

### Licensed Music APIs
```bash
# Secret - High Risk
EPIDEMIC_API_KEY=your_epidemic_key
SOUNDSTRIPE_API_KEY=your_soundstripe_key
LICKD_API_KEY=your_lickd_key

# Internal
MUSIC_LICENSE_PROVIDER=epidemic  # epidemic | soundstripe | lickd
MUSIC_TRACK_LIMIT=100  # Tracks per project
MUSIC_DURATION_LIMIT=180  # 3 minutes in seconds
```

### Image Generation APIs
```bash
# Secret
OPENAI_API_KEY=sk-openai-api-key  # Reused from Tier 1
REPLICATE_API_TOKEN=r8_your_replicate_token
STABILITY_API_KEY=your_stability_key

# Internal
IMAGE_GENERATION_PROVIDER=openai  # openai | replicate | stability
IMAGE_GENERATION_MODEL=dall-e-3
IMAGE_SIZE=1024x1024
IMAGE_QUALITY=standard
IMAGE_GENERATION_RATE_LIMIT=5  # Images per minute
```

### Email Services
```bash
# Secret - Choose one
RESEND_API_KEY=re_your_resend_key
POSTMARK_API_KEY=your_postmark_key
SENDGRID_API_KEY=SG.your_sendgrid_key

# Internal
EMAIL_PROVIDER=resend  # resend | postmark | sendgrid
EMAIL_FROM=noreply@lwa.ai
EMAIL_REPLY_TO=support@lwa.ai
EMAIL_RATE_LIMIT=100  # Emails per hour
```

## Tier 3 — Marketplace/Creator Economy Environment Variables

### Stripe Connect / Payouts
```bash
# Secret - High Risk
STRIPE_SECRET_KEY=sk_live_your_stripe_key
STRIPE_PUBLISHABLE_KEY=pk_live_your_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
STRIPE_CONNECT_CLIENT_ID=ca_your_connect_client_id

# Internal
STRIPE_API_VERSION=2023-10-16
PAYOUT_MINIMUM_AMOUNT=1000  # $10.00 in cents
PAYOUT_PROCESSING_TIME=24  # Hours
```

### Whop Marketplace
```bash
# Secret - High Risk
WHOP_API_KEY=whop_your_api_key
WHOP_WEBHOOK_SECRET=whop_your_webhook_secret
WHOP_CLIENT_ID=your_whop_client_id
WHOP_CLIENT_SECRET=your_whop_client_secret

# Internal
WHOP_API_BASE_URL=https://api.whop.com
MARKETPLACE_COMMISSION_RATE=0.20  # 20%
```

### Moderation APIs
```bash
# Secret
MODERATION_API_KEY=your_moderation_key
CONTENT_SAFETY_API_KEY=your_content_safety_key

# Internal
MODERATION_PROVIDER=internal  # internal | third_party
CONTENT_REVIEW_REQUIRED=true
AUTO_MODERATION_THRESHOLD=0.8
```

### KYC Services
```bash
# Secret - High Risk
STRIPE_IDENTITY_VERIFICATION_KEY=your_stripe_identity_key
PERSONA_API_KEY=your_persona_api_key

# Internal
KYC_PROVIDER=stripe  # stripe | persona
KYC_REQUIRED_FOR_PAYOUTS=true
KYC_VERIFICATION_TIMEOUT=86400  # 24 hours in seconds
```

### Contract Management
```bash
# Secret - High Risk
DOCUSIGN_API_KEY=your_docusign_key
DOCUSIGN_CLIENT_ID=your_docusign_client_id
PANDADOC_API_KEY=your_pandadoc_key

# Internal
CONTRACT_PROVIDER=docusign  # docusign | pandadoc
CONTRACT_TEMPLATE_ID=tpl_your_template_id
CONTRACT_AUTO_SEND=true
```

## Tier 4 — World/Game/XR Environment Variables

### Blender Pipeline
```bash
# Internal
BLENDER_PATH=/usr/bin/blender
PYTHON_PATH=/usr/bin/python3
BLENDER_SCRIPTS_DIR=/opt/lwa/blender-scripts
BLENDER_ASSET_OUTPUT_DIR=/var/www/lwa/assets
MAX_BLENDER_RENDER_TIME=300  # 5 minutes
```

### Figma Integration
```bash
# Secret
FIGMA_API_KEY=figd_your_figma_key
FIGMA_WEBHOOK_SECRET=your_figma_webhook_secret

# Internal
FIGMA_TEAM_ID=your_team_id
FIGMA_FILE_ID=your_design_file_id
DESIGN_TOKEN_SYNC_INTERVAL=300  # 5 minutes
```

### Canva Integration
```bash
# Secret
CANVA_API_KEY=your_canva_key
CANVA_APP_ID=your_canva_app_id

# Internal
CANVA_TEMPLATE_CATEGORY=social-media
CANVA_EXPORT_FORMAT=png
CANVA_MAX_EXPORT_SIZE=4096
```

### 3D Asset Pipeline
```bash
# Internal
THREEJS_PATH=/node_modules/three
GLTF_PIPELINE_PATH=/opt/gltf-pipeline
GLB_OUTPUT_DIR=/var/www/lwa/models
MAX_3D_FILE_SIZE=10485760  # 10MB in bytes
3D_ASSET_COMPRESSION=true
```

### Game Backend Services
```bash
# Secret - High Risk
NAKAMA_SERVER_KEY=your_nakama_key
COLYSEUS_API_KEY=your_colyseus_key
PLAYFAB_TITLE_ID=your_playfab_title_id
PLAYFAB_DEVELOPER_SECRET_KEY=your_playfab_key

# Internal
GAME_BACKEND_PROVIDER=nakama  # nakama | colyseus | playfab
GAME_SERVER_URL=https://game.lwa.ai
MAX_PLAYERS_PER_ROOM=8
GAME_TICK_RATE=60  # Hz
```

### XR/Meta Quest
```bash
# Secret - High Risk
META_QUEST_APP_ID=your_meta_app_id
META_QUEST_APP_SECRET=your_meta_app_secret
OPENXR_RUNTIME_PATH=/path/to/openxr

# Internal
XR_PLATFORM=meta  # meta | openxr
XR_RENDER_QUALITY=high
XR_TARGET_FRAMERATE=90
XR_MAX_SESSION_TIME=1800  # 30 minutes
```

### Real-time Networking
```bash
# Internal
WEBRTC_STUN_SERVER=stun:stun.lwa.ai:3478
WEBRTC_TURN_SERVER=turn:turn.lwa.ai:3478
TURN_SERVER_USERNAME=your_turn_user
TURN_SERVER_CREDENTIAL=your_turn_pass
UDP_SERVER_PORT=8080
MAX_NETWORK_LATENCY=100  # milliseconds
```

## Tier 5 — Blockchain/NFT Environment Variables

### Wallet Infrastructure
```bash
# Secret - High Risk
WALLETCONNECT_PROJECT_ID=your_walletconnect_project_id
PRIVY_API_KEY=your_privy_key
MAGIC_API_KEY=sk_your_magic_key

# Internal
WALLET_PROVIDER=privy  # privy | magic | walletconnect
BLOCKCHAIN_NETWORK=ethereum  # ethereum | polygon | arbitrum
RPC_ENDPOINT=https://mainnet.infura.io/v3/your_key
```

### Blockchain Infrastructure
```bash
# Secret - High Risk
ALCHEMY_API_KEY=your_alchemy_key
INFURA_PROJECT_ID=your_infura_project_id
QUICKNODE_ENDPOINT=https://your-name.quiknode.io/your-endpoint
THE_GRAPH_API_KEY=your_graph_key

# Internal
BLOCKCHAIN_RPC_PROVIDER=alchemy  # alchemy | infura | quicknode
BLOCKCHAIN_NETWORK_ID=1  # Ethereum mainnet
GAS_PRICE_STRATEGY=medium  # low | medium | high
```

### NFT Marketplace
```bash
# Secret - High Risk
OPENSEA_API_KEY=your_opensea_key
RESERVOIR_API_KEY=your_reservoir_key

# Internal
NFT_MARKETPLACE_PROVIDER=reservoir  # opensea | reservoir
NFT_CONTRACT_ADDRESS=0x_your_contract
NFT_ROYALTY_BPS=250  # 2.5%
NFT_MARKETPLACE_FEE_BPS=250  # 2.5%
```

### Smart Contract Development
```bash
# Secret - High Risk
ETH_PRIVATE_KEY=your_eth_private_key
INFURA_PROJECT_ID=your_infura_project_id
ETHERSCAN_API_KEY=your_etherscan_key

# Internal
SMART_CONTRACT_FRAMEWORK=foundry  # foundry | hardhat
CONTRACT_VERIFICATION=true
DEPLOYMENT_NETWORK=ethereum  # ethereum | polygon | arbitrum
GAS_LIMIT=800000
```

## Development Environment Variables

### Database
```bash
# Internal
DATABASE_URL=postgresql://user:password@localhost:5432/lwa
DATABASE_POOL_SIZE=20
DATABASE_TIMEOUT=30000
```

### Development Tools
```bash
# Internal
NODE_ENV=development
LOG_LEVEL=debug
DEBUG=lwa:*
PORT=3000
HOST=localhost
```

### Testing
```bash
# Internal
TEST_DATABASE_URL=postgresql://test:test@localhost:5432/lwa_test
TEST_API_BASE_URL=http://localhost:3000/api
CI=true
COVERAGE=true
```

## Security Guidelines

### Required Safeguards
1. **Never commit secret keys to version control**
2. **Use environment-specific .env files**
3. **Rotate API keys regularly**
4. **Implement rate limiting for all external APIs**
5. **Use webhook signatures for verification**
6. **Encrypt sensitive data at rest**
7. **Audit access logs regularly**

### Environment File Structure
```
.env.example              # Template with all variables
.env.local                 # Local development (gitignored)
.env.development           # Development environment
.env.staging              # Staging environment
.env.production           # Production environment
```

### Key Rotation Schedule
- **API Keys**: Every 90 days
- **Database Credentials**: Every 180 days
- **Webhook Secrets**: Every 365 days
- **Service Account Keys**: Every 365 days

### Compliance Requirements
- **GDPR**: Data privacy and user consent
- **CCPA**: California privacy rights
- **SOC 2**: Security controls and audits
- **PCI DSS**: Payment card processing
- **KYC/AML**: Identity verification requirements

## Monitoring and Alerting

### API Monitoring
```bash
# Internal
API_MONITORING_ENABLED=true
API_TIMEOUT_THRESHOLD=5000  # 5 seconds
API_ERROR_RATE_THRESHOLD=0.05  # 5%
API_RESPONSE_TIME_ALERT=true
```

### Cost Controls
```bash
# Internal
COST_TRACKING_ENABLED=true
MONTHLY_API_BUDGET=1000.00  # USD
BUDGET_ALERT_THRESHOLD=0.80  # 80%
COST_PER_USER_LIMIT=10.00  # USD per user per month
```

### Performance Metrics
```bash
# Internal
PERFORMANCE_MONITORING=true
RESPONSE_TIME_SLO=200  # milliseconds
UPTIME_SLO=0.999  # 99.9%
ERROR_RATE_SLO=0.01  # 1%
```

## Deployment Configuration

### Docker Environment
```bash
# Internal
DOCKER_REGISTRY=registry.lwa.ai
DOCKER_IMAGE_TAG=latest
CONTAINER_MEMORY_LIMIT=2g
CONTAINER_CPU_LIMIT=2
```

### Kubernetes Environment
```bash
# Internal
KUBERNETES_NAMESPACE=lwa
REPLICA_COUNT=3
RESOURCE_REQUEST_CPU=500m
RESOURCE_REQUEST_MEMORY=1Gi
RESOURCE_LIMIT_CPU=1000m
RESOURCE_LIMIT_MEMORY=2Gi
```

### CDN Configuration
```bash
# Internal
CDN_DOMAIN=cdn.lwa.ai
CDN_CACHE_TTL=3600  # 1 hour
CDN_COMPRESSION=true
CDN_GZIP_ENABLED=true
```

## Emergency Procedures

### API Key Rotation
1. Generate new API key from provider
2. Update environment variables
3. Deploy with new key
4. Monitor for errors
5. Deactivate old key after 24 hours

### Service Outages
1. Check provider status pages
2. Enable fallback providers if available
3. Update status page for users
4. Monitor recovery progress
5. Post-mortem analysis

### Security Incidents
1. Immediately rotate compromised keys
2. Audit access logs
3. Notify security team
4. Document incident timeline
5. Implement preventive measures
