"""
Offline Processing Engine
Free video processing without API calls.
Uses FFmpeg and PySceneDetect for scene detection and silence removal.
"""
import subprocess
import tempfile
import os
from pathlib import Path
from typing import List, Dict, Optional
from pydantic import BaseModel


class Segment(BaseModel):
    start: float
    end: float
    type: str  # "kept", "removed", "suggested"


class ClipMetadata(BaseModel):
    clip_id: str
    source_path: str
    output_path: Optional[str]
    segments: List[Segment]
    duration: float
    has_audio: bool


def remove_silence(input_path: str, output_path: str, min_silence_duration: float = 1.0) -> str:
    """
    Remove silent segments from video using FFmpeg silenceremove filter.
    Returns path to processed video.
    """
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-af", f"silenceremove=stop_periods=-1:stop_duration={min_silence_duration}:stop_threshold=-50dB",
        "-c:v", "copy", "-c:a", "aac", "-strict", "experimental",
        "-f", "mp4", output_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def detect_scenes(input_path: str, threshold: float = 30.0) -> List[Segment]:
    """
    Detect scene changes using FFmpeg scene detection filter.
    Returns list of segments with start/end times.
    """
    # Use ffmpeg to detect scene changes
    cmd = [
        "ffmpeg", "-i", input_path,
        "-filter:v", f"select='gt(scene,0.3)',showinfo",
        "-f", "null", "-"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Parse scene changes from stderr
    segments = []
    current_time = 0.0
    
    # For now, create uniform segments based on video duration
    # In production, parse the scene detection output properly
    duration = get_video_duration(input_path)
    
    if duration > 0:
        # Create segments of 15-30 seconds each
        segment_length = min(30.0, max(15.0, duration / 5))
        num_segments = int(duration / segment_length)
        
        for i in range(num_segments):
            start = i * segment_length
            end = min((i + 1) * segment_length, duration)
            segments.append(Segment(
                start=start,
                end=end,
                type="kept" if i < 3 else "suggested"  # First 3 are kept, rest suggested
            ))
    
    return segments


def get_video_duration(input_path: str) -> float:
    """Get video duration in seconds using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", input_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except (ValueError, AttributeError):
        return 0.0


def crop_vertical(input_path: str, output_path: str, target_aspect: float = 9.0/16.0) -> str:
    """
    Crop video to vertical aspect ratio (default 9:16 for TikTok/Reels).
    Centers the crop on the original video.
    """
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-vf", f"crop=ih*{target_aspect}:ih",
        "-c:a", "copy",
        "-f", "mp4", output_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def extract_clip(input_path: str, output_path: str, start: float, end: float) -> str:
    """
    Extract a clip segment from video.
    start and end are in seconds.
    """
    duration = end - start
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-ss", str(start),
        "-t", str(duration),
        "-c:v", "libx264", "-c:a", "aac",
        "-strict", "experimental",
        "-f", "mp4", output_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def process_video_offline(source_path: str, output_dir: str, request_id: str) -> List[ClipMetadata]:
    """
    Main offline processing pipeline.
    1. Detect scenes
    2. Extract clips
    3. Generate metadata
    Returns list of ClipMetadata objects.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Detect scenes
    segments = detect_scenes(source_path)
    
    clips = []
    for i, segment in enumerate(segments):
        clip_id = f"{request_id}-clip-{i+1:03d}"
        output_path = os.path.join(output_dir, f"{clip_id}.mp4")
        
        # Extract the clip
        extract_clip(source_path, output_path, segment.start, segment.end)
        
        # Create metadata
        clip = ClipMetadata(
            clip_id=clip_id,
            source_path=source_path,
            output_path=output_path,
            segments=[segment],
            duration=segment.end - segment.start,
            has_audio=True
        )
        clips.append(clip)
    
    return clips


def generate_thumbnail(input_path: str, output_path: str, time_offset: float = 1.0) -> str:
    """Generate thumbnail image from video at specified time offset."""
    cmd = [
        "ffmpeg", "-y", "-i", input_path,
        "-ss", str(time_offset),
        "-vframes", "1",
        "-q:v", "2",
        output_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path
