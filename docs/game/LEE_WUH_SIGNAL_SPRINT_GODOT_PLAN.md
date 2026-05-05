# Lee-Wuh: Signal Sprint — Godot Game Plan

## Executive Summary

Free-first game development stack using Blender for assets and Godot for the game engine, with LWA web app as the launcher and marketplace hub.

## Technology Stack

### Free Production Pipeline
- **Blender** = Lee-Wuh/world/sword/NPC assets (already working)
- **Godot** = Actual game prototype engine
- **Next.js/LWA web** = Launcher, shell, account, marketplace, agent, previews
- **Backend** = Progress/rewards/contracts (future phase)

## Game Title

**Lee-Wuh: Signal Sprint**

## Core Game Loop (First Prototype)

### Objective
Run through Lee-Wuh's realm, collect signal orbs, dodge noise, power up the Realm Blade, complete creator missions.

### Mechanics
1. **Movement** - 3-lane runner (left/right/jump)
2. **Collection** - Signal fragments (gold orbs) increase score
3. **Avoidance** - Noise blocks (red obstacles) reduce flow state
4. **Power-up** - Realm Blade activation clears path
5. **Mission** - Complete creator challenges to unlock rewards

### Visual Design
- Black + Gold + Purple color scheme (matching LWA)
- Lee-Wuh as guide/overlord (not playable character initially)
- Signal vs Noise visual language
- Realm environment with purple aura effects

## Architecture

### Separation of Concerns
```
lwa-godot/          # Separate Godot project folder
├── scenes/
│   ├── main_game.tscn
│   ├── character_select.tscn
│   └── realm_portal.tscn
├── scripts/
│   ├── player_controller.gd
│   ├── signal_orb.gd
│   └── realm_blade.gd
├── assets/
│   ├── lee-wuh-character.glb    # From Blender pipeline
│   ├── realm_environment.glb    # From Blender pipeline
│   └── realm_blade.glb          # From Blender pipeline
└── export/
    └── web/                      # HTML5 export for web embedding
```

### LWA Web Integration
- `/game` route hosts Godot web embed
- `/realm` route shows game portal and missions
- Lee-Wuh agent guides players to game
- Marketplace integration for creator missions
- Progress sync with backend (future)

## Reward Layer Principles

### Transparency First
- No hidden mining or background crypto
- All rewards must be opt-in
- Clear energy/device impact disclosure
- Legal review required before any token implementation

### Demo Mode (Phase 1)
- Playable game with mock rewards
- Signal Fragments and Compressed Signal (in-game currency)
- No real value or withdrawals
- Focus on fun and creator mission integration

### Future Reward Integration (Phase 2+)
- Only after legal and technical review
- Explicit opt-in for any blockchain features
- Transparent reward terms and conditions
- User control over device/resource usage

## Development Phases

### Phase 1: Prototype (Current)
- [x] Blender asset pipeline working
- [ ] Basic Godot 3-lane runner
- [ ] Lee-Wuh as guide/NPC
- [ ] Signal/Noise mechanics
- [ ] Web embed in LWA app
- [ ] Demo rewards only

### Phase 2: Creator Integration
- [ ] Mission system connected to LWA clip generation
- [ ] Marketplace missions (create clips, edit videos, etc.)
- [ ] Progress tracking in LWA backend
- [ ] Enhanced Lee-Wuh guidance system

### Phase 3: Multiplayer/Async
- [ ] Leaderboards and competitions
- [ ] Realm battles (async PvP)
- [ ] Guild/crew systems
- [ ] Advanced reward mechanics

## Technical Requirements

### Godot Version
- Godot 4.2+ (stable)
- Export target: Web (HTML5)
- Optional: Desktop builds for testing

### Asset Pipeline
- Blender → GLB export (already working)
- Texture compression for web
- LOD system for performance
- Mobile-friendly optimizations

### Performance Targets
- 60 FPS on modern browsers
- <50MB initial download
- Progressive asset loading
- Fallback to 2D if WebGL unavailable

## LWA Integration Points

### Web Embed
```html
<!-- In /game route -->
<iframe src="/godot-web/index.html" 
        width="100%" 
        height="600px"
        frameborder="0">
</iframe>
```

### API Integration (Future)
```javascript
// Game → LWA Backend
POST /api/game/session/start
POST /api/game/session/complete
GET  /api/game/missions
POST /api/game/progress
```

### Lee-Wuh Agent Integration
- Game state influences Lee-Wuh mood in web app
- Lee-Wuh suggests game missions based on user activity
- Game achievements unlock Lee-Wuh animations/dialogue

## Safety and Compliance

### No Hidden Mechanics
- All game mechanics visible to player
- No background processing without consent
- Clear data usage and storage policies

### Child Safety
- Age-appropriate content
- No real money transactions in demo mode
- Parental controls for any future reward systems

### Accessibility
- Keyboard and gamepad support
- Colorblind-friendly design
- Adjustable difficulty settings
- Subtitle/caption support for Lee-Wuh dialogue

## Next Steps

1. **Create Godot project structure**
2. **Import Blender assets**
3. **Build basic 3-lane runner mechanics**
4. **Implement Signal/Noise systems**
5. **Add Lee-Wuh NPC and guidance**
6. **Create web embed for LWA integration**
7. **Test performance and optimize**
8. **Integrate with LWA backend (future)**

## Success Metrics

- Game completion rate >70%
- Average session length 5-10 minutes
- LWA app engagement increase
- Positive player feedback on Lee-Wuh integration
- Technical performance targets met

---

**Document Status:** Draft v1.0
**Next Review:** After Godot prototype is functional
**Owner:** LWA Game Development Council
