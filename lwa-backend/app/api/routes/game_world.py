"""
Game World / Realm API Routes
Handles world state, zones, locations, events, and world progression.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

router = APIRouter(prefix="/api/v1/game-world", tags=["game_world"])

# Pydantic models
class WorldLocation(BaseModel):
    id: str
    name: str
    description: str
    location_type: str
    coordinates: Dict[str, float]
    connected_locations: List[str]
    unlock_requirements: Optional[Dict[str, Any]]
    rewards: Optional[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]]

class WorldZone(BaseModel):
    id: str
    name: str
    description: str
    zone_type: str
    theme: str
    difficulty: int
    locations: List[str]
    unlock_requirements: Optional[Dict[str, Any]]
    completion_rewards: Optional[Dict[str, Any]]
    is_unlocked: bool
    completion_percentage: float
    metadata: Optional[Dict[str, Any]]

class WorldEvent(BaseModel):
    id: str
    name: str
    description: str
    event_type: str
    zone_id: Optional[str]
    location_id: Optional[str]
    start_time: str
    end_time: Optional[str]
    requirements: Optional[Dict[str, Any]]
    rewards: Optional[Dict[str, Any]]
    participants: List[str]
    status: str
    metadata: Optional[Dict[str, Any]]

class WorldState(BaseModel):
    current_zone_id: str
    current_location_id: str
    active_events: List[str]
    unlocked_zones: List[str]
    completed_zones: List[str]
    world_time: str
    weather: str
    atmosphere: str
    metadata: Optional[Dict[str, Any]]

class PlayerWorldProgress(BaseModel):
    player_id: str
    visited_locations: List[str]
    completed_challenges: List[str]
    unlocked_zones: List[str]
    zone_completion: Dict[str, float]
    total_progress: float
    achievements: List[str]
    last_active: str

class RealmInfo(BaseModel):
    id: str
    name: str
    description: str
    theme: str
    total_zones: int
    total_locations: int
    active_players: int
    created_at: str
    updated_at: str

class VisitLocationRequest(BaseModel):
    player_id: str
    location_id: str

class ChallengeAttemptRequest(BaseModel):
    player_id: str
    challenge_id: str
    attempt_data: Optional[Dict[str, Any]] = None

# Mock data
MOCK_ZONES = {
    "zone_creator_hub": WorldZone(
        id="zone_creator_hub",
        name="Creator Hub",
        description="The central nexus where all creators begin their journey. Home to the main clipping engine.",
        zone_type="hub",
        theme="afro_futurist_tech",
        difficulty=1,
        locations=["loc_command_center", "loc_clip_engine", "loc_social_plaza"],
        unlock_requirements={"level": 1},
        completion_rewards={"experience": 500, "title": "Hub Navigator"},
        is_unlocked=True,
        completion_percentage=75.0,
        metadata={"icon": "🏠", "color": "#C9A24A"}
    ),
    "zone_brand_world": WorldZone(
        id="zone_brand_world",
        name="Lee-Wuh Brand World",
        description="The mascot universe where brand identity and creative spirit converge.",
        zone_type="creative",
        theme="anime_afro_fusion",
        difficulty=2,
        locations=["loc_mascot_temple", "loc_design_studio", "loc_brand_archive"],
        unlock_requirements={"level": 3, "achievement": "first_clip"},
        completion_rewards={"experience": 1000, "title": "Brand Guardian"},
        is_unlocked=True,
        completion_percentage=45.0,
        metadata={"icon": "🦁", "color": "#6D3BFF"}
    ),
    "zone_marketplace": WorldZone(
        id="zone_marketplace",
        name="Opportunity Marketplace",
        description="A bustling district where creators find jobs, campaigns, and collaboration opportunities.",
        zone_type="commercial",
        theme="neon_night_market",
        difficulty=3,
        locations=["loc_job_board", "loc_campaign_center", "loc_collaboration_hub"],
        unlock_requirements={"level": 5, "achievement": "first_campaign"},
        completion_rewards={"experience": 1500, "title": "Deal Maker"},
        is_unlocked=False,
        completion_percentage=0.0,
        metadata={"icon": "💼", "color": "#00D9FF"}
    ),
    "zone_creative_lab": WorldZone(
        id="zone_creative_lab",
        name="Creative Laboratories",
        description="Advanced research facilities where new AI tools and creative engines are developed.",
        zone_type="research",
        theme="futuristic_lab",
        difficulty=5,
        locations=["loc_ai_research", "loc_engine_workshop", "loc_innovation_hub"],
        unlock_requirements={"level": 10, "achievement": "power_user"},
        completion_rewards={"experience": 2500, "title": "Innovation Pioneer"},
        is_unlocked=False,
        completion_percentage=0.0,
        metadata={"icon": "🔬", "color": "#FF6B35"}
    )
}

MOCK_LOCATIONS = {
    "loc_command_center": WorldLocation(
        id="loc_command_center",
        name="Command Center",
        description="Central operations hub for all clipping and generation activities.",
        location_type="facility",
        coordinates={"x": 0, "y": 0, "z": 0},
        connected_locations=["loc_clip_engine", "loc_social_plaza"],
        unlock_requirements=None,
        rewards={"experience": 100},
        metadata={"icon": "🎮", "services": ["clip_generation", "batch_processing"]}
    ),
    "loc_clip_engine": WorldLocation(
        id="loc_clip_engine",
        name="Clip Engine Core",
        description="The heart of LWA's AI clipping technology.",
        location_type="facility",
        coordinates={"x": 100, "y": 0, "z": 50},
        connected_locations=["loc_command_center"],
        unlock_requirements=None,
        rewards={"experience": 200, "skill": "clip_generation"},
        metadata={"icon": "✂️", "services": ["video_analysis", "moment_detection"]}
    ),
    "loc_social_plaza": WorldLocation(
        id="loc_social_plaza",
        name="Social Plaza",
        description="Gathering place for creators to share and collaborate.",
        location_type="social",
        coordinates={"x": -100, "y": 0, "z": 50},
        connected_locations=["loc_command_center"],
        unlock_requirements=None,
        rewards={"experience": 50, "connections": 3},
        metadata={"icon": "👥", "services": ["networking", "collaboration"]}
    ),
    "loc_mascot_temple": WorldLocation(
        id="loc_mascot_temple",
        name="Lee-Wuh Temple",
        description="Sacred grounds honoring the brand mascot and creative spirit.",
        location_type="landmark",
        coordinates={"x": 500, "y": 100, "z": 200},
        connected_locations=["loc_design_studio"],
        unlock_requirements={"zone_unlocked": "zone_brand_world"},
        rewards={"experience": 300, "title": "Lee-Wuh Devotee"},
        metadata={"icon": "🦁", "services": ["brand_guidance", "inspiration"]}
    ),
    "loc_design_studio": WorldLocation(
        id="loc_design_studio",
        name="Brand Design Studio",
        description="Creative workspace for brand assets and visual identity.",
        location_type="facility",
        coordinates={"x": 550, "y": 0, "z": 200},
        connected_locations=["loc_mascot_temple", "loc_brand_archive"],
        unlock_requirements={"zone_unlocked": "zone_brand_world"},
        rewards={"experience": 250, "skill": "design"},
        metadata={"icon": "🎨", "services": ["asset_creation", "brand_consultation"]}
    ),
    "loc_brand_archive": WorldLocation(
        id="loc_brand_archive",
        name="Brand Archive",
        description="Repository of brand history, guidelines, and approved assets.",
        location_type="facility",
        coordinates={"x": 600, "y": 0, "z": 250},
        connected_locations=["loc_design_studio"],
        unlock_requirements={"zone_unlocked": "zone_brand_world", "achievement": "brand_explorer"},
        rewards={"experience": 400, "item": "brand_guidelines"},
        metadata={"icon": "📚", "services": ["asset_library", "brand_guidelines"]}
    )
}

MOCK_EVENTS = {
    "event_daily_clip_challenge": WorldEvent(
        id="event_daily_clip_challenge",
        name="Daily Clip Challenge",
        description="Create and submit your best clip from a trending source.",
        event_type="daily",
        zone_id="zone_creator_hub",
        location_id="loc_clip_engine",
        start_time=datetime.utcnow().isoformat(),
        end_time=(datetime.utcnow() + timedelta(days=1)).isoformat(),
        requirements={"min_level": 1, "clip_count": 1},
        rewards={"experience": 300, "credits": 50},
        participants=[],
        status="active",
        metadata={"difficulty": "easy", "theme": "trending"}
    ),
    "event_weekly_campaign": WorldEvent(
        id="event_weekly_campaign",
        name="Weekly Campaign Sprint",
        description="Join forces with other creators for a major brand campaign.",
        event_type="weekly",
        zone_id="zone_marketplace",
        location_id="loc_campaign_center",
        start_time=datetime.utcnow().isoformat(),
        end_time=(datetime.utcnow() + timedelta(days=7)).isoformat(),
        requirements={"min_level": 5, "campaigns_completed": 1},
        rewards={"experience": 1500, "credits": 200, "badge": "Campaigner"},
        participants=[],
        status="upcoming",
        metadata={"difficulty": "medium", "team_size": 5}
    ),
    "event_brand_world_festival": WorldEvent(
        id="event_brand_world_festival",
        name="Lee-Wuh Brand Festival",
        description="Celebrate the mascot and explore the brand universe.",
        event_type="special",
        zone_id="zone_brand_world",
        location_id="loc_mascot_temple",
        start_time=(datetime.utcnow() + timedelta(days=3)).isoformat(),
        end_time=(datetime.utcnow() + timedelta(days=5)).isoformat(),
        requirements={"zone_unlocked": "zone_brand_world"},
        rewards={"experience": 800, "exclusive_skin": "festival_lee_wuh"},
        participants=[],
        status="upcoming",
        metadata={"difficulty": "fun", "theme": "celebration"}
    )
}

@router.get("/realm", response_model=Dict[str, Any])
async def get_realm_info():
    """Get overall realm/world information."""
    realm = RealmInfo(
        id="realm_lwa_main",
        name="LWA Creator Realm",
        description="The unified world of Lee-Wuh AI: where creators build clips, campaigns, and value.",
        theme="afro_futurist_creator_economy",
        total_zones=len(MOCK_ZONES),
        total_locations=len(MOCK_LOCATIONS),
        active_players=127,
        created_at="2024-01-01T00:00:00Z",
        updated_at=datetime.utcnow().isoformat()
    )
    
    return {
        "success": True,
        "realm": realm.dict()
    }

@router.get("/zones", response_model=Dict[str, Any])
async def list_zones(
    include_locked: bool = False,
    zone_type: Optional[str] = None
):
    """List all world zones."""
    zones = list(MOCK_ZONES.values())
    
    if not include_locked:
        zones = [z for z in zones if z.is_unlocked]
    
    if zone_type:
        zones = [z for z in zones if z.zone_type == zone_type]
    
    return {
        "success": True,
        "zones": [z.dict() for z in zones],
        "total_count": len(zones),
        "unlocked_count": len([z for z in MOCK_ZONES.values() if z.is_unlocked]),
        "total_zones": len(MOCK_ZONES)
    }

@router.get("/zone/{zone_id}", response_model=Dict[str, Any])
async def get_zone_details(zone_id: str):
    """Get detailed information about a specific zone."""
    if zone_id not in MOCK_ZONES:
        raise HTTPException(status_code=404, detail="Zone not found")
    
    zone = MOCK_ZONES[zone_id]
    zone_locations = [MOCK_LOCATIONS.get(loc_id) for loc_id in zone.locations if loc_id in MOCK_LOCATIONS]
    
    return {
        "success": True,
        "zone": zone.dict(),
        "locations": [loc.dict() for loc in zone_locations if loc],
        "location_count": len(zone_locations)
    }

@router.get("/locations", response_model=Dict[str, Any])
async def list_locations(
    zone_id: Optional[str] = None,
    location_type: Optional[str] = None
):
    """List all locations in the world."""
    locations = list(MOCK_LOCATIONS.values())
    
    if zone_id:
        zone = MOCK_ZONES.get(zone_id)
        if zone:
            locations = [MOCK_LOCATIONS.get(loc_id) for loc_id in zone.locations if loc_id in MOCK_LOCATIONS]
            locations = [l for l in locations if l]
    
    if location_type:
        locations = [l for l in locations if l.location_type == location_type]
    
    return {
        "success": True,
        "locations": [l.dict() for l in locations],
        "total_count": len(locations)
    }

@router.get("/location/{location_id}", response_model=Dict[str, Any])
async def get_location_details(location_id: str):
    """Get detailed information about a specific location."""
    if location_id not in MOCK_LOCATIONS:
        raise HTTPException(status_code=404, detail="Location not found")
    
    location = MOCK_LOCATIONS[location_id]
    
    # Get connected location details
    connected = []
    for conn_id in location.connected_locations:
        if conn_id in MOCK_LOCATIONS:
            conn_loc = MOCK_LOCATIONS[conn_id]
            connected.append({
                "id": conn_loc.id,
                "name": conn_loc.name,
                "type": conn_loc.location_type,
                "icon": conn_loc.metadata.get("icon", "📍") if conn_loc.metadata else "📍"
            })
    
    return {
        "success": True,
        "location": location.dict(),
        "connected_locations": connected
    }

@router.post("/visit", response_model=Dict[str, Any])
async def visit_location(request: VisitLocationRequest):
    """Record a player visiting a location."""
    if request.location_id not in MOCK_LOCATIONS:
        raise HTTPException(status_code=404, detail="Location not found")
    
    location = MOCK_LOCATIONS[request.location_id]
    
    # Calculate rewards
    rewards = location.rewards or {}
    visit_record = {
        "player_id": request.player_id,
        "location_id": request.location_id,
        "visited_at": datetime.utcnow().isoformat(),
        "rewards_earned": rewards
    }
    
    return {
        "success": True,
        "message": f"Visited {location.name}",
        "location": location.dict(),
        "rewards": rewards,
        "visit_record": visit_record
    }

@router.get("/events", response_model=Dict[str, Any])
async def list_events(
    status: Optional[str] = None,
    event_type: Optional[str] = None
):
    """List world events."""
    events = list(MOCK_EVENTS.values())
    
    if status:
        events = [e for e in events if e.status == status]
    
    if event_type:
        events = [e for e in events if e.event_type == event_type]
    
    return {
        "success": True,
        "events": [e.dict() for e in events],
        "total_count": len(events),
        "active_count": len([e for e in events if e.status == "active"]),
        "upcoming_count": len([e for e in events if e.status == "upcoming"])
    }

@router.get("/event/{event_id}", response_model=Dict[str, Any])
async def get_event_details(event_id: str):
    """Get detailed information about a specific event."""
    if event_id not in MOCK_EVENTS:
        raise HTTPException(status_code=404, detail="Event not found")
    
    event = MOCK_EVENTS[event_id]
    
    return {
        "success": True,
        "event": event.dict(),
        "time_remaining": None if not event.end_time else max(0, (datetime.fromisoformat(event.end_time) - datetime.utcnow()).total_seconds())
    }

@router.post("/challenge/attempt", response_model=Dict[str, Any])
async def attempt_challenge(request: ChallengeAttemptRequest):
    """Attempt a world challenge."""
    # Mock challenge processing
    success = True
    rewards = {
        "experience": 500,
        "credits": 100,
        "achievement": "challenge_conqueror"
    }
    
    return {
        "success": success,
        "message": "Challenge completed successfully!" if success else "Challenge failed. Try again!",
        "player_id": request.player_id,
        "challenge_id": request.challenge_id,
        "rewards": rewards if success else None,
        "completed_at": datetime.utcnow().isoformat()
    }

@router.get("/map", response_model=Dict[str, Any])
async def get_world_map():
    """Get the complete world map data."""
    return {
        "success": True,
        "map": {
            "realm": {
                "id": "realm_lwa_main",
                "name": "LWA Creator Realm",
                "theme": "afro_futurist_creator_economy"
            },
            "zones": [z.dict() for z in MOCK_ZONES.values()],
            "locations": [l.dict() for l in MOCK_LOCATIONS.values()],
            "connections": [
                {
                    "from": loc_id,
                    "to": conn_id,
                    "distance": 100
                }
                for loc_id, loc in MOCK_LOCATIONS.items()
                for conn_id in loc.connected_locations
            ]
        }
    }

@router.get("/player/{player_id}/progress", response_model=Dict[str, Any])
async def get_player_progress(player_id: str):
    """Get a player's world progress."""
    progress = PlayerWorldProgress(
        player_id=player_id,
        visited_locations=["loc_command_center", "loc_clip_engine"],
        completed_challenges=["challenge_first_clip"],
        unlocked_zones=["zone_creator_hub", "zone_brand_world"],
        zone_completion={
            "zone_creator_hub": 75.0,
            "zone_brand_world": 45.0
        },
        total_progress=35.5,
        achievements=["first_steps", "clip_creator", "brand_explorer"],
        last_active=datetime.utcnow().isoformat()
    )
    
    return {
        "success": True,
        "player_id": player_id,
        "progress": progress.dict()
    }
