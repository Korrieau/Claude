# Asset and Creature List

Star marks what ships in the stage one prototype.

## Assets, 37 total

### A. Terrain and blocking (6) - shapes the route, does not kill

| Code | Name | Original use | Function | Cost |
|---|---|---|---|---|
| * TB-1 | Barrier | prefab shielding wall | blocks a route and forces a detour, shrapnel on death | supply |
| TB-2 | Razor Lattice | livestock fencing | heavy slow, zero damage, cheapest | supply |
| TB-3 | Excavation Trench | drainage digger | blocks large and heavy bodies, small ones cross | supply |
| TB-4 | Vitrifier | ground stabiliser | blocks blight spread, enemies cannot turn on it | supply, crystal |
| TB-5 | Guide Rail | cargo transfer rail | bends the swarm flow toward a chosen side | supply |
| TB-6 | Blast Door | fire bulkhead | manual close seals a corridor for seconds, takes hits meanwhile | supply, crystal |

### B. Weapon emplacements (8)

| Code | Name | Projectile | Notes | Cost |
|---|---|---|---|---|
| * DT-1 | AR-2 Auto Defence Tower | hitscan | baseline, cheap, overheats fast | supply |
| DT-2 | Arc Tower | chain | scales with density, heavy power draw | supply, crystal |
| DT-3 | PS-7 Purification Incinerator | sustained cone | the only emplacement that burns blight, friendly fire | supply |
| DT-4 | Mortar Pit | arcing | suppresses spires past walls | supply, crystal |
| DT-5 | AA Turret | hitscan | Drifting Node only | supply |
| DT-6 | Rail Emplacement | piercing | very long range, large targets, expensive | crystal |
| DT-7 | Shot Nest | cone | tiny range, last ditch defence | supply |
| DT-8 | Auto Layer | none | keeps laying mines nearby | supply, crystal |

### C. Armor emplacements (3) - anchor on placement, never move

| Code | Name | Form | Notes | Cost |
|---|---|---|---|---|
| HW-9 | Walking Excavator | quad gun platform | ballistic main gun, only asset placeable on blight | crystal |
| HW-12 | Tracked Howitzer | tracked artillery | arcing splash, longest range | crystal |
| HW-20 | Heavy Walker | biped fortress | endgame asset, splash and melee at once | heavy crystal |

### D. Garrison posts (3)

| Code | Name | Function | Cost |
|---|---|---|---|
| * GP-1 | Trench | drawn as a line, cheap, holds range and defence | supply |
| * GP-2 | Bunker | a point, large range and defence bonus | supply |
| GP-3 | Observation Post | crewed, raises nearby turret accuracy and range | supply, crystal |

### D-2. Crews (4) - what goes inside a post

| Name | Function | Cost |
|---|---|---|
| * Security Crew | baseline fire | supply |
| * Purification Crew | short cone, clears blight | supply |
| Blasting Crew | remote charges, manual detonation | supply |
| Resonance Crew | ramping damage on large targets, useless on small | supply, crystal |

### E. Infrastructure (7)

| Code | Name | Function | Cost |
|---|---|---|---|
| * IN-1 | Supply Conduit | the connection line, cut it and everything downstream goes silent, corrodes under blight | supply |
| IN-2 | Power Pylon | power chain | supply |
| * IN-3 | Crystal Extractor | sits on a node, produces crystal | supply |
| IN-4 | Ammo Store | nearby fire rate and heat recovery up, explodes when destroyed | supply |
| IN-5 | Repair Crane | auto-repairs nearby structures | supply |
| IN-6 | Shield Generator | regenerating shield, answers Resonator arcs | crystal |
| IN-7 | Assembly Plant | produces crews automatically from a set ratio | supply |

### F. Rapid response (3) - for when the line breaks

| Code | Name | Function | Cost |
|---|---|---|---|
| RD-1 | Drop Defence Module | orbital-dropped turret, instant anywhere, costly and fragile | crystal |
| RD-2 | Drop Crew | orbital-dropped personnel, instant, expendable | supply |
| RD-3 | Emergency Bulkhead | instant temporary wall with a lifespan | supply |

### G. Strategic assets (3) - manually triggered

| Code | Name | Function | Cost |
|---|---|---|---|
| ST-1 | Orbital Uplink | designated coordinate bombardment, very long cooldown | crystal |
| ST-2 | Incineration Sprayer | wide self-destruct, burns a breached sector whole | supply, crystal |
| ST-3 | Resonance Mast | passive, blocks the Collective Mind's focus order | crystal |

Manual input is exactly four things: closing a Blast Door, detonating
Blasting Crew charges, designating an Orbital Uplink strike, and firing
the Incineration Sprayer.

## Creatures, 12 plus 3 variants

The company refers to them by classification number.

### F series - infected fauna

| Code | Name | Threat | Answer |
|---|---|---|---|
| * F-01 | Drifter | herd grazer, raw mass, clusters when startled | Arc Tower, Purification Crew |
| * F-02 | Burrower | digging animal, passes under barriers | Auto Layer mines |
| F-03 | Carrier | spore bearer, spreads blight on death | burn it with PS-7 |
| F-04 | Crustform | crystallised shell, hard front, weak rear | Guide Rail to expose the flank |

### C series - crystalline, never alive

| Code | Name | Threat | Answer |
|---|---|---|---|
| C-01 | Shard | slow and very hard, pushes through the route | Rail Emplacement, piercing |
| * C-02 | Spawn Spire | static, both the spawn hole and the blight source | Mortar Pit |
| C-03 | Resonator | ranged, targets structures first | long range posts, Shield Generator |
| C-04 | Drifting Node | airborne, ignores all ground blocking | AA Turret |

### L series - long infected, large

| Code | Name | Threat | Answer |
|---|---|---|---|
| L-01 | Buried Beast | crushes structures as it passes | Resonance Crew ramp plus Rail Emplacement |
| L-02 | Collective Mind | switches the swarm from scattered to focused | Resonance Mast |
| L-03 | Progenitor | moves and plants new spires | focused fire, kill it fast |

### V variants - added late, layered onto existing species

| Code | Name | Effect |
|---|---|---|
| V-a | Chitinous | armour up, speed down |
| V-b | Frenzied | speed way up, health down |
| V-c | Sporulating | poison cloud on death |
