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
- [x] Optimized satellite rendering, must keep accuracy and smooth visuals while reducing calcs
        new benchmarks:
        3 Sats at 100x Speed at ~30FPS,
        GOES Sats at 1x speed at ~42FPS,
        ALL Sats at 1x speed at ~7FPS
- [ ] Better timer for simulation to stop stuttering and increase performance...






# Features
## UI Improvements:
- [x] FPS Display
- [X] Quality controls: Settings menu?
- [ ] 2D Screen Icons overlayed over 3D Map View
- [ ] Speed controls like in KSP [ <<<-<<-<-PAUSED->->>->>> ]
- [ ] Better Satellite selection
- [ ] 2D Screen HUD Overlay
- [ ] Debug mode toggle F3 and options (XYZ Axis vis)

## Limits:
- [ ] Time needs to be clamped to the valid epoch of the satellites... meaning 1959 - 2041 is far too wide => Clamp to the Epoch validation margin which can be set in settings.
- [ ] Model the Moon
- [ ] Model the Earth's orbit around the Sun (and thus seasons)

## Optimizations:
- [ ] Switch from dead-reckoning to clock-time based simulation
- [ ] Outsource common calculations to GPU



- [ ] Process more sat data from the TLE upon download into an easier format (xml? json?) so satellites can be sorted by more categories that simply Satnum and Name. Interesting info such as inclination, AP and PE, epoch in a datetime format, possibly other information not directly calculated from the TLE itself.

- [ ] My next focus should be the 3d qlabel sat info ui
- [ ] Basic text description and text info display widget slide-out for selected satellites of interest. Look into pulling more standardized desc and info from nasa's Space ScienceData Coordinated Archive (https://nssdc.gsfc.nasa.gov/nmc/spacecraft/display.action?id=2017-042G) - thats the entry for Flying Laptop