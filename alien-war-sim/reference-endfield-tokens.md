# Endfield design tokens — captured reference

Verbatim values pulled from the ReEnd-Components Endfield design system
source. This is the only Endfield reference this environment could
actually reach; every image host and every games-press domain is blocked
by the network egress policy, and both direct requests and a headless
browser fail at the tunnel. So this file is the ground truth we build
against, and anything not in it is our own judgement, not Endfield's.

Source: https://raw.githubusercontent.com/VBeatDead/ReEnd-Components/main/src/index.css

## Colour, in HSL as authored

| Token | Value | Hex |
|---|---|---|
| `--ef-yellow` | `48 100% 58%` | `#FFD429` |
| `--ef-yellow-dark` | `48 85% 39%` | `#B89210` |
| `--ef-blue` | `201 66% 58%` | `#4DA8DA` |
| `--ef-blue-light` | `196 64% 69%` | `#7EC8E3` |
| `--ef-blue-dark` | `202 56% 38%` | `#2B6E97` |
| `--ef-cyan` | `186 100% 50%` | `#00E5FF` |
| `--ef-red` | `355 100% 64%` | `#FF4757` |
| `--ef-green` | `145 67% 51%` | `#2ED573` |
| `--ef-orange` | `39 100% 50%` | `#FFA502` |
| `--ef-purple` | `270 77% 64%` | `#A55EEA` |
| `--ef-lime` | `84 100% 63%` | `#B8FF42` |

Surfaces are **pure neutral greys**, never blue-tinted:

| Token | Lightness | Hex |
|---|---|---|
| `--surface-canvas` | 4% | `#0A0A0A` |
| `--surface-0` | 5.9% | `#0F0F0F` |
| `--surface-1` | 7.8% | `#141414` |
| `--surface-2` | 10% | `#1A1A1A` |
| `--surface-3` | 13.3% | `#222222` |
| `--surface-hover` | 11.8% | `#1E1E1E` |
| `--surface-active` | 14.5% | `#252525` |

Text ramp:

| Token | Lightness | Hex |
|---|---|---|
| primary | 94.1% | `#F0F0F0` |
| secondary | 87.8% | `#E0E0E0` |
| tertiary | 80% | `#CCCCCC` |
| muted | 60% | `#999999` |
| placeholder | 40% | `#666666` |
| disabled | 26.7% | `#444444` |

Borders are white at low alpha, not a solid grey:
`--border: 0 0% 100% / 0.06`, `--input: 0 0% 100% / 0.1`.

## Corner treatment

The chamfer cuts the **top-right and bottom-left** corners. Note that
this is the opposite diagonal from the obvious guess.

```css
.clip-corner    { clip-path: polygon(0 0, calc(100% - 12px) 0, 100% 12px,
                                     100% 100%, 12px 100%, 0 calc(100% - 12px)); }
.clip-corner-sm { /* same shape, 8px  */ }
.clip-corner-lg { /* same shape, 16px */ }
```

Corner brackets are 24x24px, 2px wide, primary at 40% alpha, on the
top-left and bottom-right only:

```css
.corner-brackets::before { top:-1px; left:-1px;
  border-top:2px solid hsl(var(--primary)/0.4);
  border-left:2px solid hsl(var(--primary)/0.4); }
.corner-brackets::after  { bottom:-1px; right:-1px;
  border-bottom:2px solid hsl(var(--primary)/0.4);
  border-right:2px solid hsl(var(--primary)/0.4); }
```

## Surface treatments

```css
.scanline-overlay::after {
  background: repeating-linear-gradient(0deg, transparent, transparent 2px,
    rgba(255,255,255,0.015) 2px, rgba(255,255,255,0.015) 4px);
}
.panel-glass {
  background: rgba(20,20,20,0.55);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255,255,255,0.1);
  box-shadow: 0 4px 24px rgba(0,0,0,0.4);
}
.panel-glass-dark { background: rgba(10,10,10,0.65); backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.08); }
.glow-yellow      { box-shadow: 0 0 20px hsl(var(--primary)/0.2); }
.text-glow-yellow { text-shadow: 0 0 20px hsl(var(--primary)/0.3); }
```

## Motion

```css
--ease-default: cubic-bezier(0.25, 0.8, 0.25, 1);
--ease-sharp:   cubic-bezier(0.4, 0, 0.2, 1);
--ease-smooth:  cubic-bezier(0.45, 0, 0.55, 1);
--ease-bounce:  cubic-bezier(0.34, 1.56, 0.64, 1);

--duration-instant: 100ms;  --duration-fast:   150ms;
--duration-normal:  300ms;  --duration-slow:   500ms;
--duration-slower:  800ms;
```

Bounce easing exists in the system but is not used on HUD chrome here;
instrumentation should not spring.

## Layout

Header height 64px. Sidebar 280px. Minimum touch target 44px. Spacing
scale runs 4px to 128px. Focus-visible draws a yellow outline, and the
system carries reduced-motion, high-contrast and forced-colors fallbacks.

## Read from actual gameplay screenshots

The user supplied in-game captures, which corrected several things the
token file alone could not tell us.

**The world is a green valley, not an arid one.** Grass is the dominant
surface, saturated and warm, with grey rock cliffs, dirt tracks worn
through the grass, wildflowers, and heavy atmospheric haze on distant
ridges. Light is soft and warm with visible bloom.

**Machinery is pale, not dark.** AIC facilities are white and light grey
bodies with amber and orange indicator lights, set against the green. Our
earlier dark-steel structures were exactly inverted. Dark values are
reserved for slits, vents and shadowed recesses.

**Powered facilities are joined by glowing beams.** A working outpost
shows a fan of thin bright yellow lines radiating from its source to
every connected unit. This is the single most recognisable silhouette of
an Endfield base.

**Build mode projects a bold amber lattice onto the ground**, with
brighter lines on a coarser interval and vertical marker posts at the
placement boundary. It is assertive, not a faint hint grid.

**The HUD is small and lives at the screen edges.** Compact pills and
trays; the world holds the centre. A quest tracker is a yellow diamond
plus one line of white text and a smaller sub-line, top left.

**Panels are not always dark.** Inventory and menu surfaces are light,
near-white, with dark text. The dark glass treatment is for in-world HUD
overlays.

**Yellow appears as large solid blocks as well as hairlines** - a full
vertical band carrying the wordmark, for instance.

## What is still ours

Everything about the *world* — terrain materials, daylight model, rock
rendering, creature and structure design. The tokens above are a dark UI
theme; they say nothing about how the ground should look, and applying
them to the world is what previously turned an open frontier site into a
cave.
