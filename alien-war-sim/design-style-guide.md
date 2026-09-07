# Visual Style Guide

Target look: Endfield-style industrial sci-fi. Grounded engineering, not
anime gloss and not retro pixel blocks. Everything on screen should read as
equipment and interface rather than as game sprites.

Sources actually reached:
- ReEnd-Components, an Endfield design system. This is where the concrete
  token values below come from.
  https://github.com/VBeatDead/ReEnd-Components
- Endfield art direction interview (Light Zhong, Yifeng Huang), which
  frames the look as "Chinese industrial sci-fi" built from authentic
  environmental signage and equipment rather than anime gloss.
  https://www.gamespress.com/Arknights-Endfield-Reimagined-An-In-depth-Interview-with-Light-Zhong-a

Sources blocked by this environment's network proxy, so nothing here is
derived from them: Behance case study, Game8, Mobalytics, Game UI
Database, and the official Endfield site. Screenshot-level research was
not possible; the structural rules below come from diagnosing what made
our own renderer look dated, not from copying frames.

## The three rules that matter

1. **Near-black base, one signal colour.** The screen is almost entirely
   dark neutral. Signal yellow appears only on things that are ours, active
   and important. If yellow is everywhere it stops meaning anything.
2. **Line, not volume.** Form comes from hairline strokes, chamfered
   corners and corner brackets. Never from stacked filled rectangles that
   read as cubes.
3. **The HUD is instrumentation.** Labels are small, tracked-out and
   uppercase. Numbers are large and tabular. Panels look measured, not
   decorated.

## Tokens

| Role | Value | Use |
|---|---|---|
| base | `#0A0A0A` | page and world void |
| surface 1 | `#101318` | HUD bars |
| surface 2 | `#171B22` | panels, cards |
| surface 3 | `#1F252E` | raised rows, hover |
| line | `#2A323C` | hairline dividers, panel borders |
| line bright | `#3E4956` | active borders, terrain rim |
| text | `#F0F0F0` | primary readout |
| text muted | `#8C8C8C` | labels, secondary |
| text dim | `#5A6068` | disabled, hints |
| **signal** | `#FFD429` | our assets, active state, key numbers |
| signal dim | `#7A6415` | inactive accent, tracks |
| info | `#4DA9DA` | secondary data, power |
| danger | `#FF4756` | loss, damage, critical |
| ok | `#2ED675` | healthy, complete |
| infection | `#35E0D0` | the swarm, blight, crystal |

Never use orange. The Endfield accent is a cold-leaning yellow; orange
makes it read as a generic sci-fi shooter.

## Typography

- Numerals and labels: geometric technical face (Orbitron), fall back to
  a monospace stack. Tabular figures always.
- Labels: 9-10px, uppercase, `letter-spacing: .18em`, muted.
- Values: 18-22px, `#F0F0F0`, tabular.
- Body/description: 11px, muted, normal tracking.
- Korean text uses the system sans fallback; the geometric face applies to
  latin and digits only.

## Panel construction

- Corners are **chamfered**, not rounded. 8px cut on the two corners that
  face outward, via `clip-path: polygon(...)`.
- Every panel carries **corner brackets**: two short 1px rules meeting at a
  corner, in signal yellow at 60% opacity. Top-left and bottom-right only.
- Dividers are **scan lines**: 1px `#2A323C`, optionally with a 2px signal
  segment at the left end.
- Panel background is `#171B22` at ~92% with a backdrop blur where the
  world shows through.
- Status is a **diamond** (`◆` filled / `◇` hollow), never a dot.

## World rendering

- Terrain is one pre-rendered organic silhouette. No visible tile grid, no
  per-tile shading, no cube tops. Rock is a near-black mass with a single
  hairline rim in `line bright`.
- The walkable plain is a low-contrast dark field with soft large-scale
  mottling and an extremely faint survey grid at 4-tile spacing.
- Structures are **designed icons**: chamfered body, hairline stroke, one
  interior glyph, one signal accent element. They are lit from the top-left
  by a 1px bright edge, nothing more.
- Creatures are tapered silhouettes with a hairline edge and a single
  infection core. At density the mass reads as dark shapes speckled cyan.
- Effects are additive: tracers, muzzle flash, impact bloom, crystal pulse.
  Everything else stays flat.
- A vignette sinks the map edges. The eye belongs on the line.

## Killing the tile look

This is the section that mattered most in practice. A dark palette and
thin lines do not save a screen that is still a lattice of identical
squares. The specific offenders and their fixes:

| Symptom | Fix |
|---|---|
| Every structure occupies one tile of equal size | Vary footprints. Small works stay 1x1; bunker, artillery, siege rig, generator and extractor are 2x2; the hub is 3x3 |
| Adjacent walls and trenches read as separate chips | Neighbour-aware drawing. A run of the same works is filled as one continuous body with the outline only on its outer edges |
| The plain is an empty board | Ground furniture: rubble scatter, dashed survey blocks with a corner tick, hazard chevrons at the gates, faint pipe runs |
| Everything is evenly lit | Each live structure spills a soft light pool onto the ground, warm for weapons, cold blue for power and extraction |
| Nothing moves between shots | Barrel recoil on fire, rotor spin on the generator, collar rotation on the extractor, sweeping deploy arc |
| A grid is visible at all times | The build lattice appears only while an asset is being sited |

Terrain is rendered once into its own layer as merged rounded masses, so
the map never shows tile seams. Rock is near-black with a single hairline
rim and a soft cast shadow.

## Motion

- Nothing bounces or eases elastically. Transitions are 90-140ms linear or
  ease-out.
- Telegraphs (artillery rings, deploy timers) are thin strokes that sweep,
  not fills that grow.
- Damage flashes are one frame of white on the silhouette, no scaling.
