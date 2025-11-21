# Producer Guilds

Patient World now tracks four concurrent producer guilds per cell. Each guild brings different ecological effects, growth constraints, and visualization cues.

| Guild | Emoji | Layer | Growth Traits | Tradeoffs |
| --- | --- | --- | --- | --- |
| Fast grass | 🌱 | Ground | Grows rapidly whenever water + fertility are adequate. Uses the base resource multiplier and recovers from grazing quickly. | Shallow roots mean it collapses if shrubs do not establish; rabbits deplete it after seasonal booms. |
| Seasonal annuals | 🌼 | Ground | Explosive growth inside the active season window (roughly 15%–55% of the annual cycle). Outside of that window the guild drops most of its biomass into seed banks. | First-choice forage for rabbits; heavy dormancy losses leave patches bare if no other guilds share the tile. |
| Slow shrubs | 🌿 | Canopy | Seeds only where fast grass is already abundant. Gains stability once water and fertility are moderate. | Expansion stops when the ground layer is thin, so repeated disturbances can keep shrubs away permanently. |
| Deep-rooted plants | 🌳 | Canopy | Requires existing shrub cover and grows slowly but benefits more from high fertility than the other guilds. | Rare without shrubs; ties up canopy capacity so fast-growing shrubs cannot respawn as quickly after fire or grazing. |

## Layer caps

- Ground layer (fast grass + seasonal annuals) caps at ~120 biomass units per cell.
- Canopy layer (slow shrubs + deep roots) caps at ~95 biomass units per cell.
- `Cell.clamp_layers()` enforces the caps after every tick so each layer represents a competing share of light/space.

## Gameplay implications

- Rabbits graze in the order `annuals → fast grass → shrubs`, so mixed cells buffer grazing waves.
- Shrubs seed when grass is dense, and deep roots rely on shrubs; clearing the ground resets those succession ladders.
- Visualization now surfaces the dominant producer emoji whenever no animals occupy a tile, making it easier to spot shrub islands or seasonal blooms at a glance.
