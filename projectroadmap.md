# Space-map Project Roadmap

## To-Do
- [x] 1: Render Static Earth Globe in 3D w/ OpenGL
- [x] 2: Get icon for sat working
- [X] 3: Accurate simulation/model of satellites over the Earth in ECI Refrence Frame
- [X] 4: Draw parametric ellipsis to show the average orbit of a satellite
- [ ] 5: Refactor current progress into more sustainable modular methods: Satellite drawing, UI elements, ...



## Major rewrite: in no specific order...
- [X] 1: Refactor directories for clarity & organization
- [ ] 2: Rewrite current progress to fit more inline with MVC architecture alongside using common patterns like services, factories, & utilities
- [ ] 3: Abstract all time-related calculations to depend upon a single variable Simulation time Model
- [ ] 4: Question life choices.
- [ ] 5: Code SimTime Model: Ensure Epoch-related methods are realtime/simtime ambiguous. Simulation methods forcibly disable realtime into a static Epoch before continuing.