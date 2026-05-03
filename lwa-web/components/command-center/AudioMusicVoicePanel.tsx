"use client";

import { useState, useEffect } from "react";
import Card from "../ui/Card";
import Button from "../ui/Button";
import { generateAudio, generateMusic, synthesizeVoice } from "../../lib/api";

interface AudioSegment {
  id: string;
  type: string;
  start_time: number;
  end_time: number;
  style: string;
  mood: string;
  volume: number;
  file_url: string;
  duration: number;
}

interface MusicTrack {
  id: string;
  video_id: string;
  genre: string;
  tempo: number;
  mood: string;
  intensity: string;
  duration: number;
  file_url: string;
  waveform_url: string;
  instruments: string[];
  key_signature: string;
  time_signature: string;
  generated_at: string;
}

interface VoiceAudio {
  id: string;
  text: string;
  voice_type: string;
  speed: number;
  pitch: number;
  emotion: string;
  duration: number;
  file_url: string;
  sample_rate: number;
  bitrate: number;
  synthesized_at: string;
}

interface AudioProject {
  id: string;
  video_id: string;
  title: string;
  type: string;
  tracks: AudioSegment[];
  total_duration: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export function AudioMusicVoicePanel() {
  const [projects, setProjects] = useState<AudioProject[]>([]);
  const [musicTracks, setMusicTracks] = useState<MusicTrack[]>([]);
  const [voiceAudios, setVoiceAudios] = useState<VoiceAudio[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"audio" | "music" | "voice" | "mixing">("audio");
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      try {
        // Mock audio projects data
        const mockProjects: AudioProject[] = [
          {
            id: "project_1",
            video_id: "video_1",
            title: "Gaming Video Audio Mix",
            type: "mixed",
            tracks: [
              {
                id: "audio_1",
                type: "background_music",
                start_time: 0.0,
                end_time: 60.0,
                style: "energetic",
                mood: "upbeat",
                volume: 0.6,
                file_url: "https://example.com/audio/gaming_theme.mp3",
                duration: 60.0
              },
              {
                id: "audio_2",
                type: "sound_effects",
                start_time: 15.0,
                end_time: 20.0,
                style: "gaming",
                mood: "exciting",
                volume: 0.4,
                file_url: "https://example.com/audio/game_sounds.mp3",
                duration: 5.0
              }
            ],
            total_duration: 60.0,
            status: "completed",
            created_at: "2026-05-03T12:00:00Z",
            updated_at: "2026-05-03T12:30:00Z"
          },
          {
            id: "project_2",
            video_id: "video_2",
            title: "Tech Review Narration",
            type: "voice",
            tracks: [
              {
                id: "audio_3",
                type: "voice",
                start_time: 0.0,
                end_time: 120.0,
                style: "professional",
                mood: "informative",
                volume: 0.8,
                file_url: "https://example.com/audio/voice_narration.mp3",
                duration: 120.0
              }
            ],
            total_duration: 120.0,
            status: "processing",
            created_at: "2026-05-03T10:00:00Z",
            updated_at: "2026-05-03T10:15:00Z"
          }
        ];
        
        setProjects(mockProjects);

        // Mock music tracks data
        const mockMusicTracks: MusicTrack[] = [
          {
            id: "music_1",
            video_id: "video_1",
            genre: "electronic",
            tempo: 120,
            mood: "upbeat",
            intensity: "medium",
            duration: 60.0,
            file_url: "https://example.com/music/electronic_track.mp3",
            waveform_url: "https://example.com/music/waveform.png",
            instruments: ["synthesizer", "drums", "bass"],
            key_signature: "C major",
            time_signature: "4/4",
            generated_at: "2026-05-03T12:00:00Z"
          },
          {
            id: "music_2",
            video_id: "video_2",
            genre: "cinematic",
            tempo: 80,
            mood: "dramatic",
            intensity: "high",
            duration: 90.0,
            file_url: "https://example.com/music/cinematic_track.mp3",
            waveform_url: "https://example.com/music/waveform2.png",
            instruments: ["orchestra", "piano", "strings"],
            key_signature: "D minor",
            time_signature: "4/4",
            generated_at: "2026-05-03T11:30:00Z"
          }
        ];
        
        setMusicTracks(mockMusicTracks);

        // Mock voice audios data
        const mockVoiceAudios: VoiceAudio[] = [
          {
            id: "voice_1",
            text: "Welcome to our comprehensive tech review",
            voice_type: "narrator",
            speed: 1.0,
            pitch: 1.0,
            emotion: "neutral",
            duration: 3.5,
            file_url: "https://example.com/voice/welcome.mp3",
            sample_rate: 44100,
            bitrate: 128,
            synthesized_at: "2026-05-03T12:00:00Z"
          },
          {
            id: "voice_2",
            text: "Let's dive into the features and specifications",
            voice_type: "professional",
            speed: 1.1,
            pitch: 0.9,
            emotion: "informative",
            duration: 4.2,
            file_url: "https://example.com/voice/features.mp3",
            sample_rate: 44100,
            bitrate: 128,
            synthesized_at: "2026-05-03T11:45:00Z"
          }
        ];
        
        setVoiceAudios(mockVoiceAudios);
      } catch (error) {
        console.error("Failed to load audio data:", error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const formatTime = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed": return "text-green-600";
      case "processing": return "text-blue-600";
      case "pending": return "text-yellow-600";
      case "failed": return "text-red-600";
      default: return "text-gray-600";
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "background_music": return "🎵";
      case "sound_effects": return "🔊";
      case "voice": return "🎤";
      case "mixed": return "🎧";
      default: return "🔊";
    }
  };

  const handleGenerateAudio = async (videoId: string, audioType: string, style: string, mood: string) => {
    setGenerating(true);
    try {
      const result = await generateAudio(videoId, audioType, style, mood);
      
      if (result.success) {
        const newProject: AudioProject = {
          id: `project_${Date.now()}`,
          video_id: videoId,
          title: `Audio for ${videoId}`,
          type: audioType,
          tracks: result.segments,
          total_duration: result.total_duration,
          status: "completed",
          created_at: result.generated_at,
          updated_at: result.generated_at
        };
        
        setProjects([newProject, ...projects]);
      }
    } catch (error) {
      console.error("Failed to generate audio:", error);
    } finally {
      setGenerating(false);
    }
  };

  const handleGenerateMusic = async (videoId: string, genre: string, mood: string, intensity: string) => {
    setGenerating(true);
    try {
      const result = await generateMusic(videoId, genre, mood, intensity);
      
      if (result.success) {
        setMusicTracks([result.music_track, ...musicTracks]);
      }
    } catch (error) {
      console.error("Failed to generate music:", error);
    } finally {
      setGenerating(false);
    }
  };

  const handleSynthesizeVoice = async (text: string, voiceType: string, emotion: string) => {
    setGenerating(true);
    try {
      const result = await synthesizeVoice(text, voiceType, emotion);
      
      if (result.success) {
        setVoiceAudios([result.voice_audio, ...voiceAudios]);
      }
    } catch (error) {
      console.error("Failed to synthesize voice:", error);
    } finally {
      setGenerating(false);
    }
  };

  if (loading) {
    return (
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4">Audio, Music & Voice</h3>
        <div className="text-center py-8">
          <div className="text-gray-500">Loading audio engine data...</div>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Tab Navigation */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab("audio")}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === "audio"
                ? "border-purple-500 text-purple-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            Audio Projects ({projects.length})
          </button>
          <button
            onClick={() => setActiveTab("music")}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === "music"
                ? "border-purple-500 text-purple-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            Music Tracks ({musicTracks.length})
          </button>
          <button
            onClick={() => setActiveTab("voice")}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === "voice"
                ? "border-purple-500 text-purple-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            Voice Synthesis ({voiceAudios.length})
          </button>
          <button
            onClick={() => setActiveTab("mixing")}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === "mixing"
                ? "border-purple-500 text-purple-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            Audio Mixing
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === "audio" && (
        <div className="space-y-4">
          <Card className="p-4">
            <h4 className="font-medium mb-4">Generate New Audio</h4>
            <div className="grid gap-4 md:grid-cols-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Video ID
                </label>
                <input
                  type="text"
                  placeholder="Enter video ID"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Audio Type
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md">
                  <option value="background_music">Background Music</option>
                  <option value="sound_effects">Sound Effects</option>
                  <option value="ambient">Ambient</option>
                  <option value="narration">Narration</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Style
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md">
                  <option value="energetic">Energetic</option>
                  <option value="calm">Calm</option>
                  <option value="dramatic">Dramatic</option>
                  <option value="upbeat">Upbeat</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Mood
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md">
                  <option value="happy">Happy</option>
                  <option value="intense">Intense</option>
                  <option value="relaxed">Relaxed</option>
                  <option value="mysterious">Mysterious</option>
                </select>
              </div>
            </div>
            <div className="mt-4">
              <Button 
                variant="secondary" 
                onClick={() => handleGenerateAudio("video_1", "background_music", "energetic", "happy")}
                disabled={generating}
              >
                {generating ? "Generating..." : "Generate Audio"}
              </Button>
            </div>
          </Card>

          {projects.length > 0 ? (
            projects.map((project) => (
              <Card key={project.id} className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-2xl">{getTypeIcon(project.type)}</span>
                      <h4 className="font-medium">{project.title}</h4>
                      <span className={`text-sm px-2 py-1 rounded ${getStatusColor(project.status)} bg-gray-100`}>
                        {project.status}
                      </span>
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-sm text-gray-600 mb-2">
                      <div>
                        <span className="font-medium">Type:</span> {project.type}
                      </div>
                      <div>
                        <span className="font-medium">Duration:</span> {formatTime(project.total_duration)}
                      </div>
                      <div>
                        <span className="font-medium">Tracks:</span> {project.tracks.length}
                      </div>
                    </div>
                    <div className="text-sm text-gray-500">
                      Created: {formatDate(project.created_at)}
                      {project.updated_at !== project.created_at && (
                        <span className="ml-4">Updated: {formatDate(project.updated_at)}</span>
                      )}
                    </div>
                    <div className="mt-3 space-y-2">
                      {project.tracks.map((track) => (
                        <div key={track.id} className="flex items-center gap-2 text-sm text-gray-600 bg-gray-50 p-2 rounded">
                          <span>{getTypeIcon(track.type)}</span>
                          <span>{track.type}</span>
                          <span>•</span>
                          <span>{formatTime(track.start_time)} - {formatTime(track.end_time)}</span>
                          <span>•</span>
                          <span>Volume: {Math.round(track.volume * 100)}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="ml-4 space-y-2">
                    <Button variant="secondary" size="sm">
                      Edit Mix
                    </Button>
                    <Button variant="secondary" size="sm">
                      Export
                    </Button>
                  </div>
                </div>
              </Card>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              No audio projects found
            </div>
          )}
        </div>
      )}

      {activeTab === "music" && (
        <div className="space-y-4">
          <Card className="p-4">
            <h4 className="font-medium mb-4">Generate Music</h4>
            <div className="grid gap-4 md:grid-cols-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Video ID
                </label>
                <input
                  type="text"
                  placeholder="Enter video ID"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Genre
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md">
                  <option value="electronic">Electronic</option>
                  <option value="gaming">Gaming</option>
                  <option value="cinematic">Cinematic</option>
                  <option value="pop">Pop</option>
                  <option value="rock">Rock</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Mood
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md">
                  <option value="upbeat">Upbeat</option>
                  <option value="energetic">Energetic</option>
                  <option value="calm">Calm</option>
                  <option value="dramatic">Dramatic</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Intensity
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md">
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>
            </div>
            <div className="mt-4">
              <Button 
                variant="secondary" 
                onClick={() => handleGenerateMusic("video_1", "electronic", "upbeat", "medium")}
                disabled={generating}
              >
                {generating ? "Generating..." : "Generate Music"}
              </Button>
            </div>
          </Card>

          {musicTracks.length > 0 ? (
            musicTracks.map((track) => (
              <Card key={track.id} className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-2xl">🎵</span>
                      <h4 className="font-medium">Music Track for {track.video_id}</h4>
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-sm text-gray-600 mb-2">
                      <div>
                        <span className="font-medium">Genre:</span> {track.genre}
                      </div>
                      <div>
                        <span className="font-medium">Tempo:</span> {track.tempo} BPM
                      </div>
                      <div>
                        <span className="font-medium">Duration:</span> {formatTime(track.duration)}
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-sm text-gray-600 mb-2">
                      <div>
                        <span className="font-medium">Mood:</span> {track.mood}
                      </div>
                      <div>
                        <span className="font-medium">Intensity:</span> {track.intensity}
                      </div>
                      <div>
                        <span className="font-medium">Key:</span> {track.key_signature}
                      </div>
                    </div>
                    <div className="text-sm text-gray-600 mb-2">
                      <span className="font-medium">Instruments:</span> {track.instruments.join(", ")}
                    </div>
                    <div className="text-sm text-gray-500">
                      Generated: {formatDate(track.generated_at)}
                    </div>
                  </div>
                  <div className="ml-4 space-y-2">
                    <Button variant="secondary" size="sm">
                      Preview
                    </Button>
                    <Button variant="secondary" size="sm">
                      Download
                    </Button>
                  </div>
                </div>
              </Card>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              No music tracks found
            </div>
          )}
        </div>
      )}

      {activeTab === "voice" && (
        <div className="space-y-4">
          <Card className="p-4">
            <h4 className="font-medium mb-4">Synthesize Voice</h4>
            <div className="grid gap-4 md:grid-cols-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Text
                </label>
                <textarea
                  placeholder="Enter text to synthesize"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  rows={3}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Voice Type
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md">
                  <option value="narrator">Narrator</option>
                  <option value="announcer">Announcer</option>
                  <option value="professional">Professional</option>
                  <option value="friendly">Friendly</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Speed
                </label>
                <input
                  type="number"
                  min="0.5"
                  max="2.0"
                  step="0.1"
                  defaultValue="1.0"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Emotion
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md">
                  <option value="neutral">Neutral</option>
                  <option value="happy">Happy</option>
                  <option value="excited">Excited</option>
                  <option value="serious">Serious</option>
                </select>
              </div>
            </div>
            <div className="mt-4">
              <Button 
                variant="secondary" 
                onClick={() => handleSynthesizeVoice("Welcome to our comprehensive tech review", "narrator", "neutral")}
                disabled={generating}
              >
                {generating ? "Synthesizing..." : "Synthesize Voice"}
              </Button>
            </div>
          </Card>

          {voiceAudios.length > 0 ? (
            voiceAudios.map((audio) => (
              <Card key={audio.id} className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-2xl">🎤</span>
                      <h4 className="font-medium">Voice Audio</h4>
                      <span className="text-sm px-2 py-1 rounded bg-blue-100 text-blue-700">
                        {audio.voice_type}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600 mb-2">
                      <span className="font-medium">Text:</span> &quot;{audio.text}&quot;
                    </div>
                    <div className="grid grid-cols-4 gap-4 text-sm text-gray-600 mb-2">
                      <div>
                        <span className="font-medium">Duration:</span> {formatTime(audio.duration)}
                      </div>
                      <div>
                        <span className="font-medium">Speed:</span> {audio.speed}x
                      </div>
                      <div>
                        <span className="font-medium">Pitch:</span> {audio.pitch}x
                      </div>
                      <div>
                        <span className="font-medium">Emotion:</span> {audio.emotion}
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm text-gray-600 mb-2">
                      <div>
                        <span className="font-medium">Sample Rate:</span> {audio.sample_rate} Hz
                      </div>
                      <div>
                        <span className="font-medium">Bitrate:</span> {audio.bitrate} kbps
                      </div>
                    </div>
                    <div className="text-sm text-gray-500">
                      Synthesized: {formatDate(audio.synthesized_at)}
                    </div>
                  </div>
                  <div className="ml-4 space-y-2">
                    <Button variant="secondary" size="sm">
                      Play
                    </Button>
                    <Button variant="secondary" size="sm">
                      Download
                    </Button>
                  </div>
                </div>
              </Card>
            ))
          ) : (
            <div className="text-center py-8 text-gray-500">
              No voice audios found
            </div>
          )}
        </div>
      )}

      {activeTab === "mixing" && (
        <div className="space-y-4">
          <Card className="p-4">
            <h4 className="font-medium mb-4">Audio Mixing Console</h4>
            <div className="space-y-4">
              <div>
                <h5 className="text-sm font-medium mb-2">Available Tracks</h5>
                <div className="space-y-2">
                  {projects.flatMap(project => project.tracks).map((track) => (
                    <div key={track.id} className="flex items-center justify-between p-2 border rounded">
                      <div className="flex items-center gap-2">
                        <span>{getTypeIcon(track.type)}</span>
                        <span className="text-sm">{track.type}</span>
                        <span className="text-sm text-gray-500">({formatTime(track.start_time)} - {formatTime(track.end_time)})</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <input
                          type="range"
                          min="0"
                          max="100"
                          defaultValue={track.volume * 100}
                          className="w-20"
                        />
                        <span className="text-sm w-10">{Math.round(track.volume * 100)}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              <div>
                <h5 className="text-sm font-medium mb-2">Mix Settings</h5>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Mix Preset
                    </label>
                    <select className="w-full px-3 py-2 border border-gray-300 rounded-md">
                      <option value="balanced">Balanced</option>
                      <option value="vocals_forward">Vocals Forward</option>
                      <option value="bass_heavy">Bass Heavy</option>
                      <option value="cinematic">Cinematic</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Master Volume
                    </label>
                    <input
                      type="range"
                      min="0"
                      max="100"
                      defaultValue="80"
                      className="w-full"
                    />
                  </div>
                </div>
              </div>
              
              <div className="flex gap-2">
                <Button variant="secondary">
                  Preview Mix
                </Button>
                <Button variant="secondary">
                  Export Mix
                </Button>
                <Button variant="secondary">
                  Save Preset
                </Button>
              </div>
            </div>
          </Card>

          <Card className="p-4">
            <h4 className="font-medium mb-4">Mixing Tips</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
              <div>
                <h5 className="font-medium mb-2">Volume Balancing</h5>
                <ul className="space-y-1">
                  <li>• Keep vocals around -6dB to -3dB</li>
                  <li>• Background music should be -12dB to -18dB</li>
                  <li>• Sound effects can peak at -6dB</li>
                  <li>• Leave headroom for mastering</li>
                </ul>
              </div>
              <div>
                <h5 className="font-medium mb-2">Frequency Tips</h5>
                <ul className="space-y-1">
                  <li>• Cut frequencies below 80Hz for vocals</li>
                  <li>• Boost 2-5kHz for vocal clarity</li>
                  <li>• Use high-pass filters on bass</li>
                  <li>• Apply gentle compression</li>
                </ul>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Quick Actions */}
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4">Quick Actions</h3>
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
          <Button variant="secondary" size="sm">
            Batch Generate
          </Button>
          <Button variant="secondary" size="sm">
            Import Audio
          </Button>
          <Button variant="secondary" size="sm">
            Apply Effects
          </Button>
          <Button variant="secondary" size="sm">
            Master Track
          </Button>
        </div>
      </Card>
    </div>
  );
}
