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
| Victory | Endless survival, no campaign clear |
| Vision | Full map visible, spawn holes pre-warned |
| Art | Silhouettes, earth grey plus industrial hazard orange, blight glows pale teal |
| Enemy AI | Beast swarm; the Collective Mind switches it to focused |
| Friendly fire | Fire and explosives only, scalable multiplier |
| Resources | Supply (income over time) + Alloy (captured mining nodes) |
| Squad skill | One per squad, auto-recharging |
| Session | 15-20 min target, restart from scratch on defeat |
| Sound | Synthesized SFX only (Web Audio), no asset files |

| Structure | Defense-first: fortifications are the main line, mobile is a small reserve |
| Bunkers | Empty shells; garrisoned unit decides their behaviour and cannot move |
| Conduits | Supply conduits power everything; cut one and everything under it goes silent |
| Mycelium | Blocks construction and corrodes conduits it covers |
| Turrets | Overheat and fall silent under sustained fire |
| Armor | Deploys in place as an emplacement, relocates slowly under its own power |

| Unit control | None at all. The player places, builds and researches, never orders |
| Placement | Tile grid |
| Building mid-wave | Allowed with no restriction |
| Unlocks | Build tree only, no chapters |
| Manual assets | Four |
| Enemy identity | Infected native wildlife, crystal-borne, not invaders |
| UI tone | Work order and gauge readout, dry, no fanfare |

| Difficulty | Fixed per-wave formula, new creatures introduced on a cycle |
| Score | Cumulative kills |
| Mining and blight | Flavour only, no mechanical link |

Open: turret vs garrison weighting, mining node layout, prototype scope.

## Setting

A frontier development company lands on a sick world to extract crystal.
The player is an administrator, not a commander: they sit in a control
room, place assets and set production. That is exactly why no unit can be
ordered around - it is the job description, not a limitation.

Tone is dry industrial labour, not heroism. Assets carry model numbers
(AR-2 Auto Defence Tower, PS-7 Purification Incinerator, HW-9 Walking
Excavator). A cleared wave reads like a log line, not a victory screen.

Note on references: Arknights lore does tie Originium to disease, but
Endfield has no "mining spreads contamination" mechanic. We keep that
link as flavour in the fiction only - extraction never feeds the blight
numerically.

Difficulty is a fixed formula so runs stay comparable: wave N sets count
and composition, and a new creature type enters on a set cycle. Nothing
scales to how well the player is doing.

## Enemy identity

Not invaders. Native wildlife that crystal infection turned, plus crystal
growths that move on their own.

Infected (were animals): Drifter (herd swarm), Burrower (passes under
walls), Carrier (spreads blight on death), Crustform (front armour only).

Crystalline (never alive): Shard (slow, hard), Spawn Spire (static, the
spawn hole), Resonator (ranged), Drifting Node (airborne).

Long infected (large): Buried Beast (crushes structures in its path),
Collective Mind (syncs the swarm from scattered to focused), Progenitor
(moves and plants new spires).

After the build tree is exhausted, progression continues as endless
per-asset upgrades.

## The chain

Ground, supply and firepower form one chain, and it breaks as one:

Mycelium spreads -> it covers conduits -> conduits corrode -> turrets go
silent -> the line collapses. Pushing the mycelium back needs Incinerator
Nests, which themselves need a live conduit.

## Core loop

1. Extend conduits to reach mining nodes, which lengthens the line
2. Build emplacements along that conduit for firepower
3. Mycelium advances and eats both ground and conduits
4. Burn it back to reclaim buildable ground
5. Next wave, stronger

A short line is safe but poor. A long line is rich but fragile. That
scale gets re-weighed every single wave.

## Defense layers

Four layers, each doing a different job:

1. Delay - trench, razor lattice, excavation trench, vitrified ground, guide rail
2. Firepower - autogun nest, bunker, arc tower, incinerator nest, mortar pit, AA turret, rail emplacement, auto-miner
3. Support - ammo store, relay post, repair crane, power pylon, shield generator
4. Last resort - blast door, incineration sprayer

Armor emplacements: Regulator (quad, deploys on mycelium), Pylon Battery
(arcing), Bolt Lancer (hover, fastest to relocate), Disperser (AA),
Bulwark (deployable barrier), Atlas (endgame walking fortress).

Mobile reserve, five only: Drop Crew, Regulator, Bulwark, Repair Drone,
Salvage Drone.

Garrison units: Security Team, Incineration Crew, Blasting Crew,
Resonance Tech.

## Enemy behaviours

Threat comes from behaviour, not stat lines:

- climbs corpse piles to cross walls
- front rank overlaps into a living shield
- past a density threshold the swarm climbs over turrets
- Acid Polyps target conduits first
- under Hive Mind control the swarm pulls back and re-charges

## Projectiles

| Type | Property | Used by |
|---|---|---|
| Hitscan | instant, tracer only | autogun, rail emplacement |
| Ballistic | slow solid shot, dodgeable | Regulator main gun |
| Arcing | telegraphed impact ring, clears walls | mortar pit, Pylon Battery |
| Sustained cone | per-tick, friendly fire | incinerator nest |
| Chain | bounces scale with density | arc tower |

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

### Armor (military, arrives from orbit in act 2-3)

The company is civilian and starts with none of this. Corporate ships real
military hardware down once it decides the site is worth defending. Act 1
scarcity is what makes this gear land with weight.

| Unit | Form | Role | Weakness |
|---|---|---|---|
| Regulator | quad walker tank | main line, ballistic cannon, heavy frontal armour, legs ignore mycelium slow | weak flanks, slow turning |
| Bolt Lancer | hover tank | railgun, pierces, fast, hit and run | almost no armour |
| Pylon Battery | tracked artillery | arcing splash, telegraphed impact ring, suppresses fruiting bodies | very slow, helpless up close |
| Disperser | anti-air gun | proximity flak, hard counter to Glidespore | near useless vs ground |
| Bulwark | shield vehicle | deploys a forward barrier, a frontline that moves | cannot move while deployed |
| Atlas | large biped mech | two different arm weapons, a walking fortress | extremely expensive, unrecoverable |

Atlas counts as one squad, not a hero unit. No per-entity control anywhere.

### Installations
| Structure | Role |
|---|---|
| Crystal Barrier | wall, shrapnel damage when destroyed |
| Vitrifier | glasses the ground, blocks mycelium, no turning |
| Spore Mine | pheromone contamination, swarm briefly turns on itself |
| Gravity Anchor | forces fliers to land |
| Reclamation Forge | rebuilds a wiped squad at half cost from wreckage |
| Orbital Uplink | endgame, map-wide bombardment, very long cooldown |

Manual input is needed for five units only: Blasting Crew, Siege Drill,
Drop Crew, Orbital Uplink, Bulwark deploy. Everything else runs itself
once placed.

## Three-act progression

| Act | What the player holds | Feel |
|---|---|---|
| 1 | crew plus improvised industrial gear | "we have to hold with this?" |
| 2 | mass drones plus first armor | the line stabilises, automation runs |
| 3 | corporate military armor plus orbital assets | counterattack is possible, but Leviathan and Hive Mind arrive |

Act 1 powerlessness is what gives act 3 firepower its meaning.

## Reference points

Halo, StarCraft 2, Starship Troopers, Warhammer 40k and Arknights:
Endfield are deliberate touchstones. Endfield is the closest in texture
(industrial automation on a hostile, contaminated world) but its
automation exists to build production lines; here automation exists to
hold a frontline.

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
