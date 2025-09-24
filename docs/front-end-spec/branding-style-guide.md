# Branding & Style Guide

## Visual Identity
**Brand Guidelines**: Professional, technical documentation tool aesthetic with emphasis on clarity and systematic organization. Clean, modern interface that doesn't compete with content visualization.

## Color Palette
| Color Type | Hex Code | Usage |
|------------|----------|--------|
| Primary | #2563EB | Template zone indicators, primary actions, focus states |
| Secondary | #10B981 | Success states, completion indicators, positive feedback |
| Accent | #F59E0B | Warnings, attention states, export actions |
| Success | #059669 | Successful operations, valid configurations |
| Warning | #D97706 | Template conflicts, attention needed |
| Error | #DC2626 | Errors, invalid configurations, broken links |
| Neutral | #6B7280, #F3F4F6, #1F2937 | Text hierarchy, borders, backgrounds |

**Template Zone Colors**:
- BMAD-METHOD: #3B82F6 (Blue)
- Claude Code: #10B981 (Green)
- Generic: #6B7280 (Gray)
- Cross-Template: #8B5CF6 (Purple)

## Typography

### Font Families
- **Primary**: Inter (UI elements, labels, body text)
- **Secondary**: JetBrains Mono (code, technical details, Mermaid syntax)
- **Monospace**: JetBrains Mono (terminal, configuration, export code)

### Type Scale
| Element | Size | Weight | Line Height |
|---------|------|--------|-------------|
| H1 | 32px | 700 | 1.2 |
| H2 | 24px | 600 | 1.3 |
| H3 | 20px | 600 | 1.4 |
| Body | 16px | 400 | 1.5 |
| Small | 14px | 400 | 1.4 |
| Code | 14px | 400 | 1.4 |

## Iconography
**Icon Library**: Lucide React for consistency with shadcn/ui, supplemented with custom template-aware icons

**Usage Guidelines**:
- Template type icons: distinct symbols for BMAD-METHOD (document-stack), Claude Code (cpu), Generic (folder)
- Relationship type icons: arrows for dependencies, links for references, bridges for cross-template connections
- Action icons: export (download), configuration (settings), navigation (chevrons)

## Spacing & Layout
**Grid System**: 8px base unit with 4px, 8px, 16px, 24px, 32px, 48px, 64px spacing scale

**Spacing Scale**: Consistent spacing using CSS custom properties based on 8px grid system for vertical rhythm and horizontal alignment
