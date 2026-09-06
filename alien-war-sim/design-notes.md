# Alien War Simulator — Design Notes

Top-down 2D base-defense simulator. Terraforming crew vs mycelial swarm.

## Core equation

Firepower density vs frontline length.
Humans have finite DPS and range. The swarm has near-infinite numbers.
Every decision reduces to "how short can I make the line I must hold".

## View

Top-down 2D. Canvas, shapes and silhouettes only.
Height (z) exists ONLY for arcing shots and gliding units — never for
hitscan, direct fire, or cones. Screen position must equal hit position.

## Confirmed decisions

| Topic | Decision |
|---|---|
| View | Top-down 2D, z only for arc/jump |
| Genre | Base defense + production, wave based |
| Map | One fixed map, 3 corridors, collapses to 360 deg late game |
| Control | Squad level: reposition / facing / one skill / build / produce |
| Spawns | Destructible spawn holes, new positions each wave |
| Losses | Paid reinforcement; a wiped squad is gone for good |
| Unlocks | Research, spent from resources |
| Pacing | Paused prep phase between waves |
| Victory | Campaign clear, then endless mode unlocks |
| Vision | Full map visible, spawn holes pre-warned |
| Art | Silhouettes, night + neon palette |
| Enemy AI | Beast swarm; Hive Mind switches it to focused |
| Friendly fire | Fire and explosives only, scalable multiplier |
| Resources | Supply (income over time) + Alloy (captured mining nodes) |
| Squad skill | One per squad, auto-recharging |
| Session | 15-20 min target, restart from scratch on defeat |
| Sound | Synthesized SFX only (Web Audio), no asset files |

Open: total wave count, research tree shape, siege identity, endgame asset.

## Mycelial system

The enemy paints mycelium on ground it crosses.
- On mycelium the swarm moves faster, humans move slower
- Spawn holes (fruiting bodies) can only grow on mycelium
- To stop the holes you must burn the mycelium back
- Mycelium, corpse decals and vitrified ground share one render layer

This makes the frontline literally visible on the floor.

## Flow field as a player resource

Every other defense game gives the player one way to shape enemy pathing
(walls). Here there are four, each touching a different part of the field:

| Unit | Effect on the flow field |
|---|---|
| Drill Walker | changes the target (aggro from drill vibration) |
| Magnet Crane | bends the direction |
| Vitrifier | changes speed and turn radius |
| Decoy Hulk | changes target priority |

The Hive Mind reverses all of it. Late-game difficulty rises because the
player's tools stop working, not because HP numbers grow.

## Human roster — terraforming crew

Every piece of equipment has an original industrial purpose.

### Rigs (alloy, main line)
| Unit | Original use | Combat role |
|---|---|---|
| Drill Walker | drilling walker | melee drill, tanky, passive aggro |
| Cutter Rig | rock-cutting plasma | short range, very high dps, pierces |
| Arc Pulser | wireless power transmit | chain lightning, stronger vs dense packs |
| Seeder | soil steriliser | sustained cone, only thing that burns mycelium |
| Magnet Crane | cargo electromagnet | passive path deflection |
| Hauler | heavy cargo truck | no weapon, carries units and structures fast |
| Siege Drill | large excavator | anchors down for very long range piercing shot |

### Automata (supply, cheap)
| Unit | Role |
|---|---|
| Survey Swarm | six small drones, fast, expendable |
| Welder Drone | no combat, auto-repairs nearby machines |
| Salvage Drone | auto-converts corpses and wreckage to supply |
| Decoy Hulk | unarmed hulk, highest target priority, slow |
| Relay Drone | passive, blocks Hive Mind focus in radius |

### Crew (people, cheap and fragile)
| Unit | Role |
|---|---|
| Security Team | the only basic gun squad, fastest to reinforce |
| Blasting Crew | remote charges, manual detonation |
| Drop Crew | orbital drop insertion, answers rear breaches |
| Resonance Tech | ultrasound, damage ramps up on a single target |

### Installations
| Structure | Role |
|---|---|
| Crystal Barrier | wall, shrapnel damage when destroyed |
| Vitrifier | glasses the ground, blocks mycelium, no turning |
| Spore Mine | pheromone contamination, swarm briefly turns on itself |
| Gravity Anchor | forces fliers to land |
| Reclamation Forge | rebuilds a wiped squad at half cost from wreckage |
| Orbital Uplink | endgame, map-wide bombardment, very long cooldown |

Manual input is needed for four units only: Blasting Crew, Siege Drill,
Drop Crew, Orbital Uplink. Everything else runs itself once placed.

## Enemy roster — mycelial swarm

| Tier | Unit | Threat | Answer |
|---|---|---|---|
| 1 | Runner | raw numbers, fast | Arc Pulser |
| 1 | Burrow Polyp | short burrow, ignores walls | Spore Mine |
| 1 | Spore Sac | spreads mycelium wide on death | Seeder |
| 2 | Crustform | heavy frontal armour, weak rear | Vitrifier then flank |
| 2 | Acid Polyp | ranged acid, targets structures first | Siege Drill, Cutter Rig |
| 2 | Splitter | splits into two smaller on death | Seeder, kill in one pass |
| 3 | Tunneler | opens a fruiting body behind the line | Drop Crew reserve |
| 3 | Glidespore | flies, ignores ground blocking | Gravity Anchor |
| 3 | Plasma Cyst | rear arcing fire, snipes static structures | mobile comp, Resonance Tech |
| 3 | Mimic | copies a friendly silhouette to slip through | Magnet Crane exposes it |
| 4 | Hive Mind | switches the swarm from scattered to focused | Relay Drone, Resonance Tech |
| 4 | Brood Queen | moves and plants new fruiting bodies | focused fire, kill fast |
| 4 | Leviathan | huge, crushes walls and structures in its path | Resonance Tech + Orbital |
| 4 | Swarm Spire | static, buffs everything nearby | Siege Drill from range |

Variants added late: Chitinous (armour up, speed down), Frenzied (speed
way up, health down), Sporulating (poison cloud on death).

## Balance rules

1. Every enemy has at least one answer, researchable one wave before it
   first appears.
2. No enemy gets more than two of: fast, tough, ranged.
3. "Ignore" abilities (ignores walls, ignores splash, ignores ground
   blocking) are limited to one per unit.

## Technical plan

- Single HTML file, canvas 2D, no dependencies
- Fixed 60 Hz logic tick, decoupled render
- One flow field for pathing, boids steering on top (separate, align, avoid)
- Spatial hash grid for collision and target lookup
- Target 1000-2000 active entities at 60 fps
- Ground layer (mycelium, corpses, glass) drawn once to an offscreen canvas
- Web Audio for all sound, no asset files
