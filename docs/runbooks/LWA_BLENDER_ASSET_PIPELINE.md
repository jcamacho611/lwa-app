# LWA Blender Asset Pipeline

## Overview

This document defines the local Blender asset pipeline for LWA's creative workflow engine. The pipeline separates local asset creation from web app integration while maintaining clear boundaries between development and production assets.

## Local Blender Asset Folder Structure

```
/Users/bdm/LWA/blender/
├── brand-tests/          # Visual style and brand experiments
├── seven-agents/         # Character models and animations
├── clip-engine-intros/   # Intro sequences and branding
├── realm-scenes/         # Environment and background scenes
├── exports/              # Final exported assets for web use
│   ├── png/              # Still images and textures
│   ├── mp4/              # High-quality video files
│   ├── webm/             # Web-optimized video
│   └── glb/              # 3D models for web viewing
├── reference/            # Reference images and inspiration
└── scripts/              # Python automation scripts
```

### Folder Details

#### `/brand-tests/`
- **Purpose**: Visual style exploration and brand consistency testing
- **Contents**: Style experiments, color palette tests, material studies
- **File Types**: .blend files, test renders, material libraries
- **Web Integration**: Reference only, not for direct web use

#### `/seven-agents/`
- **Purpose**: Character development and animation for the Seven Agents system
- **Contents**: Character models, rigging tests, animation cycles, expression libraries
- **File Types**: .blend files, character rigs, animation data
- **Web Integration**: Exported animations and character models only

#### `/clip-engine-intros/`
- **Purpose**: Branding sequences and Clip Engine visual identity
- **Contents**: Logo animations, intro sequences, transition effects
- **File Types**: .blend files, animation projects, effect libraries
- **Web Integration**: Exported video loops and branding elements

#### `/realm-scenes/`
- **Purpose**: Environment design and worldbuilding visualization
- **Contents**: Realm environments, background scenes, world elements
- **File Types**: .blend files, environment models, lighting setups
- **Web Integration**: Exported backgrounds and environment assets

#### `/exports/`
- **Purpose**: Final optimized assets ready for web integration
- **Contents**: Web-ready images, videos, and 3D models
- **File Types**: PNG, MP4, WebM, GLB files only
- **Web Integration**: Direct web app usage

#### `/reference/`
- **Purpose**: Visual reference and inspiration collection
- **Contents**: Concept art, style guides, reference images
- **File Types**: Images, documents, style guides
- **Web Integration**: Reference only, not for direct web use

#### `/scripts/`
- **Purpose**: Automation and pipeline tools
- **Contents**: Python scripts, automation tools, export utilities
- **File Types**: .py files, automation scripts, tool configurations
- **Web Integration**: Tools only, not direct web assets

## Blender File Management Rules

### Repository Boundaries
- **Never commit raw .blend files** to the repository unless intentionally approved
- **Generated assets stay outside repo** by default
- **Only exported assets enter the web app** after optimization and review
- **Source .blend files remain local** for development and iteration

### File Naming Conventions
```
Characters:     [agent_name]_[action]_[version].blend
Environments:   [realm]_[scene]_[version].blend
Animations:     [character]_[animation]_[version].blend
Exports:        [asset_type]_[name]_[format]_[quality].[ext]
Scripts:        [function]_[version].py
```

### Version Control Strategy
- **Local iteration**: Multiple versions during development
- **Export tracking**: Single optimized version per asset for web
- **Backup strategy**: Local backups for important .blend files
- **Documentation**: Track changes in export logs

## Export Formats and Specifications

### Supported Export Formats

#### PNG (Still Images)
- **Use Cases**: UI elements, icons, textures, background images
- **Specifications**: 
  - Resolution: Up to 4K for backgrounds, 2K for UI elements
  - Color Space: sRGB for web, Linear for textures
  - Compression: PNG-8 for simple graphics, PNG-24 for complex images
  - Transparency: Alpha channel supported
- **Optimization**: File size vs quality balance
- **Web Integration**: Direct use in web app

#### MP4 (High-Quality Video)
- **Use Cases**: Intro sequences, promotional content, high-quality animations
- **Specifications**:
  - Resolution: 1920x1080 (Full HD) standard
  - Frame Rate: 30fps for web, 60fps for premium content
  - Codec: H.264 for compatibility
  - Bitrate: 8-12 Mbps for high quality
  - Audio: AAC stereo, 128-256 kbps
- **Optimization**: Balance quality and file size
- **Web Integration**: Progressive loading, fallback to WebM

#### WebM (Web-Optimized Video)
- **Use Cases**: Web animations, background loops, interactive elements
- **Specifications**:
  - Resolution: 1280x720 for web, 1920x1080 for premium
  - Frame Rate: 30fps standard, 60fps for smooth animations
  - Codec: VP9 for better compression
  - Bitrate: 4-8 Mbps for web optimization
  - Alpha Channel: VP9 supports transparency
- **Optimization**: Maximum web performance
- **Web Integration**: Native browser support, ideal for web

#### GLB (3D Models)
- **Use Cases**: Interactive 3D elements, character models, product visualization
- **Specifications**:
  - Vertices: Optimized for web performance (under 100k vertices)
  - Textures: Compressed, power-of-2 dimensions
  - Materials: PBR materials where applicable
  - File Size: Under 10MB for web models
- **Optimization**: Performance-focused modeling
- **Web Integration**: Three.js, Babylon.js, or WebGL viewers

#### Image Sequences
- **Use Cases**: Complex animations, frame-by-frame effects, sprite sheets
- **Specifications**:
  - Format: PNG sequences for quality, JPEG for efficiency
  - Resolution: Match target output resolution
  - Frame Rate: Match target frame rate
  - Naming: Sequential numbering (frame_0001.png)
- **Optimization**: Balance quality and performance
- **Web Integration**: Sprite sheets or video encoding

## Export Pipeline Rules

### Quality Control Checklist
- [ ] **Visual Quality**: No artifacts, proper resolution, correct colors
- [ ] **Performance**: File size appropriate for use case
- [ ] **Compatibility**: Format works with target platforms
- [ ] **Optimization**: Compressed appropriately, efficient encoding
- [ ] **Metadata**: Proper naming, version information
- [ ] **Testing**: Verify in target environment

### Export Workflow
1. **Create Source Asset**: Develop .blend file with proper structure
2. **Local Testing**: Render and test locally for quality
3. **Optimize Settings**: Configure export parameters for target use
4. **Export Asset**: Generate final file in appropriate format
5. **Quality Check**: Verify export meets requirements
6. **Web Testing**: Test in actual web environment
7. **Final Approval**: Sign off for production use

### Automation Scripts
```python
# Example export script structure
import bpy
import os

def export_character_animation(character_name, animation_name, quality="web"):
    """Export character animation in appropriate format"""
    # Set up export parameters based on quality
    # Execute export
    # Verify output
    pass

def export_environment_scene(realm_name, scene_name, resolution="2k"):
    """Export environment scene for web use"""
    # Configure render settings
    # Export background or environment
    pass

def batch_export_assets(asset_list, target_format="webm"):
    """Batch export multiple assets"""
    for asset in asset_list:
        # Export each asset with appropriate settings
        pass
```

## Web App Integration

### Integration Points
- **Static Assets**: Direct file inclusion in web app
- **Dynamic Loading**: Lazy loading for performance
- **CDN Distribution**: Optimized delivery network
- **Fallback Systems**: Alternative formats for compatibility

### Performance Considerations
- **File Size Limits**: Set maximum file sizes per asset type
- **Loading Strategy**: Progressive loading for large assets
- **Caching**: Browser and CDN caching strategies
- **Responsive Design**: Multiple resolutions for different devices

### Asset Management
- **Version Control**: Track asset versions in web app
- **Update Process**: Safe asset replacement procedures
- **Fallback Handling**: Graceful degradation for older browsers
- **Monitoring**: Performance and usage tracking

## Development Workflow

### Local Development
1. **Create Asset**: Develop in local Blender environment
2. **Test Locally**: Verify quality and functionality
3. **Export Test**: Generate test export for evaluation
4. **Review Process**: Internal quality and brand review
5. **Final Export**: Generate production-ready asset
6. **Web Integration**: Add to web app with proper testing

### Collaboration
- **Asset Sharing**: Share .blend files for collaboration
- **Version Tracking**: Maintain clear version history
- **Review Process**: Structured review and approval workflow
- **Documentation**: Document asset creation process

### Backup and Recovery
- **Local Backups**: Regular backup of important .blend files
- **Cloud Storage**: Optional cloud backup for critical assets
- **Recovery Process**: Procedures for recovering lost assets
- **Archive Strategy**: Long-term storage for completed projects

## Security and IP Protection

### Asset Security
- **Local Storage**: Keep source .blend files secure
- **Access Control**: Limit access to sensitive assets
- **Distribution**: Control distribution of high-value assets
- **Watermarking**: Consider watermarking preview assets

### IP Protection
- **Original Assets**: Ensure all assets are original LWA creations
- **Reference Management**: Track reference sources and licenses
- **Brand Consistency**: Maintain brand guidelines across all assets
- **Quality Standards**: Enforce quality and brand standards

## Troubleshooting

### Common Issues
- **Export Failures**: Check file paths, permissions, disk space
- **Quality Issues**: Verify render settings, lighting, materials
- **Performance Issues**: Optimize geometry, textures, compression
- **Compatibility Issues**: Test across browsers and devices

### Debugging Process
1. **Identify Issue**: Clearly define the problem
2. **Check Source**: Verify .blend file integrity
3. **Test Export**: Try different export settings
4. **Verify Output**: Check exported file properties
5. **Test Integration**: Verify in web environment
6. **Document Solution**: Record problem and solution

### Support Resources
- **Documentation**: Maintain up-to-date documentation
- **Community**: Internal knowledge sharing and support
- **Tools**: Debugging and testing tools
- **Training**: Regular training on pipeline and tools

## Future Enhancements

### Pipeline Improvements
- **Automation**: Increased automation for repetitive tasks
- **Integration**: Better integration with web development tools
- **Performance**: Continuous optimization of export processes
- **Quality**: Enhanced quality control and testing procedures

### Technology Updates
- **Format Support**: Add support for new formats as needed
- **Tools**: Evaluate and adopt new tools and technologies
- **Standards**: Update standards as web technologies evolve
- **Best Practices**: Continuously improve best practices

### Scaling Considerations
- **Volume**: Handle increased asset volume efficiently
- **Collaboration**: Support larger team collaboration
- **Distribution**: Optimize for larger scale distribution
- **Maintenance**: Sustainable maintenance processes

---

## Quick Reference

### Essential Commands
```bash
# Create new asset structure
mkdir -p /Users/bdm/LWA/blender/{brand-tests,seven-agents,clip-engine-intros,realm-scenes,exports/{png,mp4,webm,glb},reference,scripts}

# Export character animation (Blender Python)
export_character_animation("kael", "idle", "web")

# Batch export environments
batch_export_assets(environment_list, "png")
```

### File Size Guidelines
- **PNG Images**: < 2MB for UI, < 10MB for backgrounds
- **MP4 Video**: < 50MB for standard, < 100MB for premium
- **WebM Video**: < 20MB for web, < 50MB for premium
- **GLB Models**: < 10MB for interactive models

### Quality Standards
- **Resolution**: Match target platform requirements
- **Compression**: Balance quality and performance
- **Compatibility**: Test across target browsers/devices
- **Brand Consistency**: Follow LWA brand guidelines

This pipeline ensures professional-quality asset creation while maintaining clear boundaries between development and production, enabling efficient scaling of LWA's creative asset ecosystem.
