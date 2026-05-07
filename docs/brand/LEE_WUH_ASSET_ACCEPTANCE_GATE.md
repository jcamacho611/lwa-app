# Lee-Wuh Asset Acceptance Gate

## Accepted Asset Kinds

### character
- **Purpose**: Living agent, loading states, hero overlays, animation reference
- **Requirements**: Transparent background, full body visible
- **Restrictions**: No sword unless named combined, no large aura unless named aura variant
- **Runtime**: PNG/WebP for 2D, GLB for 3D
- **Fallback**: Must work without character

### sword
- **Purpose**: Game prop, CTA hover effects, badges, weapon reference
- **Requirements**: Transparent background or isolated 3D scene, clean silhouette
- **Restrictions**: No character, no aura unless named aura version
- **Runtime**: PNG/WebP for 2D, GLB for 3D
- **Fallback**: Must work without sword

### background
- **Purpose**: World atmosphere, realm/game environment, marketplace backdrop
- **Requirements**: Safe behind UI text, usable as world layer
- **Restrictions**: No character, no sword, no baked foreground aura
- **Runtime**: PNG/WebP for 2D, GLB for 3D
- **Fallback**: Must work without background

### aura
- **Purpose**: Energy effects, realm power indicators, loading animations
- **Requirements**: Transparent or emissive layer, composited safely
- **Restrictions**: Should not bake character or sword unless named combined
- **Runtime**: PNG/WebP with transparency, GLB with emissive materials
- **Fallback**: Must work without aura

### combined_reference
- **Purpose**: Artist reference, marketing materials, concept approval
- **Requirements**: Clearly labeled as combined/reference
- **Restrictions**: Not for runtime layering
- **Runtime**: Reference only
- **Fallback**: Not applicable

### blender_source
- **Purpose**: 3D production source, rigging reference, export pipeline
- **Requirements**: .blend files in brand-source/source folders
- **Restrictions**: Source only, not in public paths
- **Runtime**: Source only
- **Fallback**: Export to GLB for runtime

### glb_runtime
- **Purpose**: 3D web preview, game runtime, Three.js integration
- **Requirements**: Optimized for web, reasonable file size
- **Restrictions**: No huge files in public unless intentional
- **Runtime**: Runtime ready
- **Fallback**: 2D assets must work

### spine_source
- **Purpose**: Future 2D animation system, sprite rigging
- **Requirements**: Spine project files, separated sprite parts
- **Restrictions**: Source only, not in public paths
- **Runtime**: Future ready
- **Fallback**: Current static assets

### ui_reference
- **Purpose**: UI design reference, layout planning, component design
- **Requirements**: Mobile-friendly, clear UI context
- **Restrictions**: Reference only, not for runtime layering
- **Runtime**: Reference only
- **Fallback**: Not applicable

## Runtime Asset Rules

### PNG/WebP for 2D Runtime
- Transparent backgrounds for character/sword/aura
- Reasonable file sizes for web loading
- Proper color profiles for web display
- Fallback-safe naming and paths

### GLB for 3D Runtime
- Under 8MB for web optimization
- Draco compression where appropriate
- Proper material setup for web rendering
- Origin and scale cleaned for Three.js

### Source Files
- .blend files only in brand-source/source folders
- Spine files only in source folders
- No source files in public paths
- Clear separation from runtime assets

## Layer Truth Validation

### Background Assets Must Not:
- Include character layers
- Include sword props
- Bake foreground aura effects
- Break UI text readability

### Character Assets Must Not:
- Include sword unless explicitly combined
- Include large aura unless named aura variant
- Have opaque backgrounds
- Break transparency compositing

### Sword Assets Must Not:
- Include character body
- Include aura unless named aura variant
- Have complex backgrounds
- Break prop layer isolation

### Aura Assets Must Not:
- Bake character or sword unless combined
- Break compositing blend modes
- Create visual noise
- Interfere with UI readability

## Acceptance Checklist

### Before Asset Approval:
- [ ] Asset kind is correctly classified
- [ ] Layer truth is validated
- [ ] Runtime safety is confirmed
- [ ] File size is reasonable
- [ ] Fallback compatibility is verified
- [ ] Source files are properly located
- [ ] Naming convention is followed
- [ ] Usage restrictions are documented

### Runtime Assets:
- [ ] Public path exists and works
- [ ] File format is web-optimized
- [ ] Transparency is properly handled
- [ ] Color profile is web-safe
- [ ] Loading performance is acceptable

### Source Assets:
- [ ] Source files exist in correct locations
- [ ] No source files in public paths
- [ ] Export pipeline is documented
- [ ] Version control is proper
- [ ] Backup strategy exists

## Rejection Risks

### High Risk:
- Character baked into background
- Sword baked into character
- Source files in public paths
- Opaque backgrounds on transparent assets
- Huge files blocking web loading

### Medium Risk:
- Missing transparency layers
- Incorrect asset classification
- Poor web optimization
- Inconsistent naming
- Missing fallback compatibility

### Low Risk:
- Minor color profile issues
- Slightly oversized files
- Reference materials in wrong location
- Documentation gaps
- Version control inconsistencies

## Future Considerations

### Spine Integration:
- Prepare sprite separation for 2D animation
- Maintain layer compatibility
- Preserve asset registry structure
- Add spine_ready flag where appropriate

### Backend Validation:
- Future metadata validation endpoints
- Asset health monitoring
- Version history preservation
- Automated rejection risk detection

### Performance Optimization:
- Progressive loading strategies
- Asset CDN integration
- Responsive asset delivery
- Cache optimization strategies
