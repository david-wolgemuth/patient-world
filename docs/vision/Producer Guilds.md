# Producer Guilds (Deep Dive)

Patient World now tracks **eighteen** vegetation guilds split across two layers. Each guild has distinct water/fertility preferences, succession dependencies, and emoji for visualization/logging.

## Ground Layer (cap ≈ 200 biomass/cell)
| Emoji | Guild | Growth Traits | Tradeoffs |
| --- | --- | --- | --- |
| 🌱 Fast grass | Recovers immediately after rain or grazing and props up early succession. | Burns out without shade, leaving bare soil in droughts. |
| 🌼 Seasonal annuals | Explode inside a narrow seasonal window, refilling seed banks. | Collapse to seeds outside bloom season; first target for rabbits. |
| 🌺 Forb wildflowers | Mid-season forbs that boost pollen/seed production once grass is stable. | Need a healthy fast-grass base and scorch easily in droughts. |
| 🪨 Lichen crust | Colonizes barren, dry tiles and slowly stabilizes soil. | Extremely slow growth and low forage value. |
| 🍀 Moss carpets | Trap humidity and protect soil in shaded wetlands. | Suffocate in heat/drought; minimal nutrition for herbivores. |
| 🎋 Reed beds | Dominate banks and flooded cells, slowing erosion. | Require consistently wet cells; die back when water drops. |
| 🪷 Bog sedges | Thick freshwater mats that extend wetlands inland. | Collapse when water tables fall; slow to reestablish elsewhere. |
| 🍄 Fungal mats | Recycle shrub litter into nutrients and shade the ground. | Need moss/shrub litter; go dormant outside humid stretches. |
| 🌵 Succulent clusters | Store water for drought years and colonize barren cells. | Spread slowly and lose ground to faster guilds in wet seasons. |
| 🌻 Desert bloomers | Rare but dramatic blooms triggered by storms. | Spend most of the year dormant; need succulents nearby to reseed. |

## Canopy Layer (cap ≈ 150 biomass/cell)
| Emoji | Guild | Growth Traits | Tradeoffs |
| --- | --- | --- | --- |
| 🌿 Slow shrubs | Provide woody cover, seed beds, and browse for herbivores. | Need established ground cover; crowding throttles expansion. |
| 🌳 Deep-rooted plants | Anchor the canopy and tap deep aquifers to stabilize drought years. | Only propagate where shrubs are dense; very slow recovery. |
| 🍎 Fruit trees | Offer high-energy forage and dense shade once shrubs mature. | Sensitive to drought; require fertile cells plus shrub scaffolding. |
| 🌲 Needle conifers | Thrive on poor soils and cooler, drier slopes. | Shed acidic litter and suppress shrub regeneration under heavy cover. |
| 🍂 Pioneer brush | Fire-following shrubs that recolonize disturbed cells. | Short-lived and easily outcompeted once taller guilds return. |
| 🌸 Vine canopy | Opportunistic climbers that exploit shrub lattices to spread quickly. | Dormant outside warm, wet spans; can smother shrubs if unmanaged. |
| 🌴 Palm crowns | Humid floodplain specialists that provide fruit and shade. | Struggle in cold/dry cells and require high water tables. |
| 🍃 Mangrove canopy | Salt-tolerant trees that bridge land and tidal wetlands. | Only thrive in saturated coastal cells; slow to expand inland. |

## Layer caps

- Ground layer: 200 biomass units shared by the ten ground guilds.
- Canopy layer: 150 biomass units shared by the eight canopy guilds.
- `Cell.layer_capacity()` dynamically adjusts caps per tile based on water/fertility/history, so wetlands can host more reeds while drought cells favor succulents/conifers.
- `Cell.clamp_layers()` keeps every tick within those limits and records carrying-capacity events for telemetry.

## Gameplay implications

- **Tick + forecast outputs list every guild** with emoji totals, so you can see biomass shifts at a glance.
- Herbivores graze the diet chain `annuals → fast grass → reeds/moss → shrubs`, so mixing guilds is the only way to buffer boom/bust cycles.
- Moisture regimes now matter: reeds/fungal mats explode in wetlands while succulents seize drought cells; capacity telemetry flags hotspots when layers saturate.
- Forecast CSV/JSON/table outputs include per-guild statistics (start/end/min/max/extinction days) for regression tracking and QA diffing.
