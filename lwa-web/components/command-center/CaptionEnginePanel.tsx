"use client";

import { useState, useEffect } from "react";
import Card from "../ui/Card";
import Button from "../ui/Button";
import { generateCaptions, getVideoCaptions } from "../../lib/api";

interface CaptionSegment {
  id: string;
  start_time: number;
  end_time: number;
  text: string;
  confidence: number;
  style?: string;
  language?: string;
}

interface CaptionProject {
  id: string;
  video_id: string;
  title: string;
  language: string;
  style: string;
  segments: CaptionSegment[];
  total_duration: number;
  status: string;
  created_at: string;
  updated_at: string;
}

interface CaptionStyle {
  name: string;
  font_family: string;
  font_size: number;
  color: string;
  background_color: string;
  position: string;
}

export function CaptionEnginePanel() {
  const [projects, setProjects] = useState<CaptionProject[]>([]);
  const [currentProject, setCurrentProject] = useState<CaptionProject | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"projects" | "editor" | "styles" | "export">("projects");
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    const loadProjects = async () => {
      try {
        // Mock caption projects data
        const mockProjects: CaptionProject[] = [
          {
            id: "project_1",
            video_id: "video_1",
            title: "Gaming Highlights Reel",
            language: "en",
            style: "standard",
            segments: [
              {
                id: "caption_1",
                start_time: 0.0,
                end_time: 3.5,
                text: "Welcome to the ultimate gaming experience",
                confidence: 0.95
              },
              {
                id: "caption_2",
                start_time: 3.5,
                end_time: 7.2,
                text: "Today we're exploring the latest features",
                confidence: 0.92
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
            title: "Tech Review Video",
            language: "en",
            style: "minimal",
            segments: [
              {
                id: "caption_3",
                start_time: 0.0,
                end_time: 4.0,
                text: "In this video we review the latest tech",
                confidence: 0.89
              }
            ],
            total_duration: 120.0,
            status: "processing",
            created_at: "2026-05-03T10:00:00Z",
            updated_at: "2026-05-03T10:15:00Z"
          }
        ];
        
        setProjects(mockProjects);
      } catch (error) {
        console.error("Failed to load caption projects:", error);
      } finally {
        setLoading(false);
      }
    };

    loadProjects();
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

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9) return "text-green-600";
    if (confidence >= 0.8) return "text-yellow-600";
    return "text-red-600";
  };

  const handleGenerateCaptions = async (videoId: string, language = "en", style = "standard") => {
    setGenerating(true);
    try {
      const result = await generateCaptions(videoId, language, style);
      
      if (result.success) {
        const newProject: CaptionProject = {
          id: `project_${Date.now()}`,
          video_id: videoId,
          title: `Captions for ${videoId}`,
          language: result.language,
          style: result.style,
          segments: result.captions,
          total_duration: result.total_duration,
          status: "completed",
          created_at: result.generated_at,
          updated_at: result.generated_at
        };
        
        setProjects([newProject, ...projects]);
        setCurrentProject(newProject);
      }
    } catch (error) {
      console.error("Failed to generate captions:", error);
    } finally {
      setGenerating(false);
    }
  };

  if (loading) {
    return (
      <Card className="p-6">
        <h3 className="text-xl font-semibold mb-4">Caption Engine</h3>
        <div className="text-center py-8">
          <div className="text-gray-500">Loading caption engine data...</div>
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
            onClick={() => setActiveTab("projects")}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === "projects"
                ? "border-purple-500 text-purple-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            Projects ({projects.length})
          </button>
          <button
            onClick={() => setActiveTab("editor")}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === "editor"
                ? "border-purple-500 text-purple-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            Editor
          </button>
          <button
            onClick={() => setActiveTab("styles")}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === "styles"
                ? "border-purple-500 text-purple-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            Styles
          </button>
          <button
            onClick={() => setActiveTab("export")}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === "export"
                ? "border-purple-500 text-purple-600"
                : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
            }`}
          >
            Export
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === "projects" && (
        <div className="space-y-4">
          <Card className="p-4">
            <h4 className="font-medium mb-4">Generate New Captions</h4>
            <div className="grid gap-4 md:grid-cols-3">
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
                  Language
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md">
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Style
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md">
                  <option value="standard">Standard</option>
                  <option value="minimal">Minimal</option>
                  <option value="bold">Bold</option>
                  <option value="colorful">Colorful</option>
                </select>
              </div>
            </div>
            <div className="mt-4">
              <Button 
                variant="secondary" 
                onClick={() => handleGenerateCaptions("video_1", "en", "standard")}
                disabled={generating}
              >
                {generating ? "Generating..." : "Generate Captions"}
              </Button>
            </div>
          </Card>

          {projects.length > 0 ? (
            projects.map((project) => (
              <Card key={project.id} className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h4 className="font-medium">{project.title}</h4>
                      <span className={`text-sm px-2 py-1 rounded ${getStatusColor(project.status)} bg-gray-100`}>
                        {project.status}
                      </span>
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-sm text-gray-600 mb-2">
                      <div>
                        <span className="font-medium">Language:</span> {project.language}
                      </div>
                      <div>
                        <span className="font-medium">Style:</span> {project.style}
                      </div>
                      <div>
                        <span className="font-medium">Duration:</span> {formatTime(project.total_duration)}
                      </div>
                    </div>
                    <div className="text-sm text-gray-500">
                      Created: {formatDate(project.created_at)}
                      {project.updated_at !== project.created_at && (
                        <span className="ml-4">Updated: {formatDate(project.updated_at)}</span>
                      )}
                    </div>
                    <div className="text-sm text-gray-600 mt-2">
                      <span className="font-medium">Segments:</span> {project.segments.length}
                    </div>
                  </div>
                  <div className="ml-4 space-y-2">
                    <Button 
                      variant="secondary" 
                      size="sm"
                      onClick={() => setCurrentProject(project)}
                    >
                      Edit
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
              No caption projects found
            </div>
          )}
        </div>
      )}

      {activeTab === "editor" && (
        <div className="space-y-4">
          {currentProject ? (
            <>
              <Card className="p-4">
                <h4 className="font-medium mb-4">Editing: {currentProject.title}</h4>
                <div className="space-y-3">
                  {currentProject.segments.map((segment, index) => (
                    <div key={segment.id} className="border rounded-lg p-3">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-3">
                          <span className="text-sm font-medium">Segment {index + 1}</span>
                          <span className="text-sm text-gray-600">
                            {formatTime(segment.start_time)} - {formatTime(segment.end_time)}
                          </span>
                          <span className={`text-sm ${getConfidenceColor(segment.confidence)}`}>
                            {Math.round(segment.confidence * 100)}% confidence
                          </span>
                        </div>
                        <div className="space-x-2">
                          <Button variant="secondary" size="sm">
                            Edit
                          </Button>
                          <Button variant="secondary" size="sm">
                            Delete
                          </Button>
                        </div>
                      </div>
                      <textarea
                        value={segment.text}
                        onChange={(e) => {
                          const updatedSegments = [...currentProject.segments];
                          updatedSegments[index] = { ...segment, text: e.target.value };
                          setCurrentProject({ ...currentProject, segments: updatedSegments });
                        }}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md"
                        rows={2}
                      />
                    </div>
                  ))}
                </div>
              </Card>

              <Card className="p-4">
                <h4 className="font-medium mb-4">Caption Preview</h4>
                <div className="bg-black text-white p-4 rounded-lg">
                  <div className="aspect-video relative">
                    {currentProject.segments.map((segment, index) => (
                      <div
                        key={segment.id}
                        className="absolute bottom-4 left-4 right-4 text-center bg-black bg-opacity-75 px-2 py-1 rounded"
                        style={{
                          display: index === 0 ? 'block' : 'none' // Show first segment for preview
                        }}
                      >
                        {segment.text}
                      </div>
                    ))}
                  </div>
                </div>
              </Card>
            </>
          ) : (
            <div className="text-center py-8 text-gray-500">
              Select a project to edit captions
            </div>
          )}
        </div>
      )}

      {activeTab === "styles" && (
        <div className="space-y-4">
          <Card className="p-4">
            <h4 className="font-medium mb-4">Caption Styles</h4>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="border rounded-lg p-4">
                <h5 className="font-medium mb-2">Standard</h5>
                <div className="bg-gray-100 p-3 rounded">
                  <div className="text-center bg-black bg-opacity-75 text-white px-2 py-1 rounded">
                    Standard caption style
                  </div>
                </div>
                <p className="text-sm text-gray-600 mt-2">Clean, readable captions for general use</p>
              </div>
              <div className="border rounded-lg p-4">
                <h5 className="font-medium mb-2">Minimal</h5>
                <div className="bg-gray-100 p-3 rounded">
                  <div className="text-center bg-black bg-opacity-50 text-white px-2 py-1 rounded text-sm">
                    Minimal style
                  </div>
                </div>
                <p className="text-sm text-gray-600 mt-2">Subtle captions for cinematic content</p>
              </div>
              <div className="border rounded-lg p-4">
                <h5 className="font-medium mb-2">Bold</h5>
                <div className="bg-gray-100 p-3 rounded">
                  <div className="text-center bg-black text-white px-3 py-2 rounded font-bold">
                    Bold Style
                  </div>
                </div>
                <p className="text-sm text-gray-600 mt-2">High-visibility captions for accessibility</p>
              </div>
              <div className="border rounded-lg p-4">
                <h5 className="font-medium mb-2">Colorful</h5>
                <div className="bg-gray-100 p-3 rounded">
                  <div className="text-center bg-purple-600 text-white px-2 py-1 rounded">
                    Colorful style
                  </div>
                </div>
                <p className="text-sm text-gray-600 mt-2">Stylized captions for creative content</p>
              </div>
            </div>
          </Card>

          <Card className="p-4">
            <h4 className="font-medium mb-4">Custom Style Settings</h4>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Font Family
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md">
                  <option value="Arial">Arial</option>
                  <option value="Helvetica">Helvetica</option>
                  <option value="Georgia">Georgia</option>
                  <option value="Verdana">Verdana</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Font Size
                </label>
                <input
                  type="number"
                  min="12"
                  max="48"
                  defaultValue="16"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Text Color
                </label>
                <input
                  type="color"
                  defaultValue="#FFFFFF"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Background Color
                </label>
                <input
                  type="color"
                  defaultValue="#000000"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                />
              </div>
            </div>
            <div className="mt-4">
              <Button variant="secondary">
                Save Custom Style
              </Button>
            </div>
          </Card>
        </div>
      )}

      {activeTab === "export" && (
        <div className="space-y-4">
          <Card className="p-4">
            <h4 className="font-medium mb-4">Export Options</h4>
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Export Format
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md">
                  <option value="srt">SRT</option>
                  <option value="vtt">VTT</option>
                  <option value="txt">TXT</option>
                  <option value="json">JSON</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Project
                </label>
                <select className="w-full px-3 py-2 border border-gray-300 rounded-md">
                  {projects.map((project) => (
                    <option key={project.id} value={project.id}>
                      {project.title}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="mt-4 space-y-2">
              <div className="flex items-center gap-2">
                <input type="checkbox" id="timestamps" defaultChecked />
                <label htmlFor="timestamps" className="text-sm">Include timestamps</label>
              </div>
              <div className="flex items-center gap-2">
                <input type="checkbox" id="metadata" defaultChecked />
                <label htmlFor="metadata" className="text-sm">Include metadata</label>
              </div>
            </div>
            <div className="mt-4">
              <Button variant="secondary">
                Export Captions
              </Button>
            </div>
          </Card>

          <Card className="p-4">
            <h4 className="font-medium mb-4">Export History</h4>
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <div>
                  <span className="font-medium">Gaming Highlights Reel</span>
                  <span className="text-gray-500 ml-2">SRT format</span>
                </div>
                <span className="text-gray-500">2 hours ago</span>
              </div>
              <div className="flex items-center justify-between text-sm">
                <div>
                  <span className="font-medium">Tech Review Video</span>
                  <span className="text-gray-500 ml-2">VTT format</span>
                </div>
                <span className="text-gray-500">1 day ago</span>
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
            Import Captions
          </Button>
          <Button variant="secondary" size="sm">
            Translate Captions
          </Button>
          <Button variant="secondary" size="sm">
            Quality Check
          </Button>
        </div>
      </Card>
    </div>
  );
}
