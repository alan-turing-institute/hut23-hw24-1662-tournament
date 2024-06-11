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

### Earth blocks: Hydrology

#### General overview

The challenge with Earth blocks is to model the hydrology: the
movement of water through the blocks.

Each Earth block contains some water. Water can move from block to
block. In real life, there are (I think!) two main processes: (1)
groundwater, which flows like a viscous fluid through saturated rock;
(2) moisture, which is transported via a diffusion-like process
(capilliary action, possibly?) in unsaturated rock.

Water tends to move:

- down, under gravity;
- from blocks with high pressure to blocks with low pressure;
- from blocks with high water content to blocks with low water content.

The following is a version of all of this. I am not claiming physical
realism with the real world but it is “physically plausible.”

#### Block parameters

An Earth block has two parameters:

1. The water content, $w$; an integer.
2. The hydrostatic pressure, $p$; an integer.

The units of pressure are length. A pressure of $p$ arises from a
stack of $p$ blocks each containing 1 water, acting on an area of one
block face.

#### Global constants

The following are the “constants of nature.” Their meaning is given
roughly here but the real meaning of these terms is just how they
enter into the equations of state.

- Saturation level $w_{\rm sat}$ (integer): the maximum water content
  per block

- Inverse permeability (integer): the number of world ticks over which
  one unit of water flows between blocks subject to a pressure
  gradient of 1.

- Gravitational pressure:

- Tick rate (integer): (For optimisation): How many world ticks
  between updates to earth blocks.
  

#### Equations of motion when Earth not saturated




#### Optimisations




### Plant blocks (“biology”)

- 

### Plant state-machine

- One per species
- Runs on each plant block
- Faces are 0 (up) 1, 2, 3, 4 in order, and 5 (down)

