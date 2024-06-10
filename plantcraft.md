## Notes on Plantworld

### Blocks

- Rock
- Earth+Water
- Water
- Air
- Plant (of species P, in state S)

### Physics

- Diurnal cycle
- Light on blocks if next block is air
  - 100% top unless blocked, when treat as side
  - 20% sides

- Earth blocks contain water (0-255)

- Periodic rain
  - Increases waterlogging of earth

- Something clever with water?

#### Earth blocks: hydrology

The challenge with Earth blocks is to model the hydrology: the
movement of water through Earth blocks

Parameters:
- An Earth block has two parameters:
  1. The water content; an integer.
  2. The water pressure; an integer. 

Global variables are:
- Tick rate: how many world ticks before earth blocks are updated
- Saturation level: the maximum water content per block
- Permeability: 




##### Optimisation




### Plant blocks (“biology”)

- 

### Plant state-machine

- One per species
- Runs on each plant block
- Faces are 0 (up) 1, 2, 3, 4 in order, and 5 (down)

