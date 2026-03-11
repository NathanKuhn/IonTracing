import astropy.units as u
import matplotlib.pyplot as plt
import numpy as np

from plasmapy.formulary import ExB_drift, gyrofrequency
from plasmapy.particles import Particle
from plasmapy.plasma.grids import CartesianGrid
from plasmapy.simulation.particle_tracker.particle_tracker import ParticleTracker
from plasmapy.simulation.particle_tracker.save_routines import IntervalSaveRoutine
from plasmapy.simulation.particle_tracker.termination_conditions import (
    TimeElapsedTerminationCondition,
)


grid_length = 10
grid = CartesianGrid(-1 * u.m, 1 * u.m, num=grid_length)


# B goes <1, 0, 0> E goes <0, 1, 0>
Bx_fill = 4 * u.T
Bx = np.full(grid.shape, Bx_fill.value) * u.T

Ey_fill = 2 * u.V / u.m
Ey = np.full(grid.shape, Ey_fill.value) * u.V / u.m

grid.add_quantities(B_x=Bx)

x0 = [[0, 0, 0]] * u.m
v0 = [[0, 1, 0]] * u.m / u.s
particle = Particle("p+")

particle_gyroperiod = 1 / gyrofrequency(Bx_fill, particle).to(
    u.Hz, equivalencies=u.dimensionless_angles()
)

simulation_duration = 100 * particle_gyroperiod
save_interval = particle_gyroperiod / 10

termination_condition = TimeElapsedTerminationCondition(simulation_duration)
save_routine = IntervalSaveRoutine(save_interval)

simulation = ParticleTracker(
    grid,
    save_routine=save_routine,
    termination_condition=termination_condition,
    verbose=False,
)

simulation.load_particles(x0, v0, particle)
simulation.run()

results = save_routine.results
particle_trajectory = results["x"][:, 0]

fig = plt.figure()
ax = fig.add_subplot(projection="3d")

ax.plot(*particle_trajectory.T)
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
plt.show()