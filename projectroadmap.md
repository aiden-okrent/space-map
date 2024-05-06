# Space-map Project Roadmap

## To-Do
- [x] 1: Render Static Earth Globe in 3D w/ OpenGL
- [x] 2: Get icon for sat working
- [X] 3: Accurate simulation/model of satellites over the Earth in ECI Refrence Frame
- [X] 4: Draw parametric ellipsis to show the average orbit of a satellite
- [X] 5: Refactor current progress into more sustainable modular methods: Satellite drawing, UI elements, ...



## Major rewrite: in no specific order...
- [X] 1: Refactor directories for clarity & organization
- [X] 2: Rewrite current progress to fit more inline with MVC architecture alongside using common patterns like services, factories, & utilities
- [X] 3: Abstract all time-related calculations to depend upon a single variable Simulation time Model
- [X] 4: Question life choices.
- [X] 5: Code SimTime Model: Ensure Epoch-related methods are realtime/simtime ambiguous. Simulation methods forcibly disable realtime into a static Epoch before continuing.

- [x] FPS Display
- [x] Optimized satellite rendering, must keep accuracy and smooth visuals while reducing calcs
        new benchmarks:
        3 Sats at 100x Speed at ~30FPS,
        GOES Sats at 1x speed at ~42FPS,
        ALL Sats at 1x speed at ~7FPS
- [X] Quality controls: Settings menu?
- [ ] Label Icons for sat positions
- [ ] Speed controls like in KSP [ <<<-<<-<-PAUSED->->>->>> ]
- [ ] Selection for satellites to view
- [ ] Overlay HUD showing cool info

- [ ] Debug mode
- [ ] XYZ Axis stay in bottom left corner

- [ ] Better timer for simulation to stop stuttering and increase performance