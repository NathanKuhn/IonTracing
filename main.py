import astropy.units as u
import pyvista as pv
import numpy as np

import magpylib as magpy
from plasmapy.particles import Particle
from plasmapy.plasma.grids import CartesianGrid
from plasmapy.simulation.particle_tracker.particle_tracker import ParticleTracker
from plasmapy.simulation.particle_tracker.save_routines import IntervalSaveRoutine
from plasmapy.simulation.particle_tracker.termination_conditions import (
    TimeElapsedTerminationCondition,
)

grid_length = 100
grid = CartesianGrid(-0.1 * u.m, 0.1 * u.m, num=grid_length)

magnet = magpy.magnet.Cuboid(polarization=(0, 0, 0.1), dimension=(0.01, 0.01, 0.01))

B = magnet.getB(grid.grid) * u.T

grid.add_quantities(B_x=B[:,:,:,0], B_y=B[:,:,:,1], B_z=B[:,:,:,2])

x0 = [[0.03, 0, 0]] * u.m
v0 = [[0, 100, 100]] * u.m / u.s
particle = Particle("p+")

termination_condition = TimeElapsedTerminationCondition(0.001 * u.second)
save_routine = IntervalSaveRoutine(0.0000001 * u.second)

simulation = ParticleTracker(
    grid,
    save_routine=save_routine,
    termination_condition=termination_condition,
    verbose=False,
)

simulation.load_particles(x0, v0, particle)
simulation.run()

results = save_routine.results

pl = pv.Plotter()
magpy.show(magnet, canvas=pl)

particle_trajectory = results["x"][:, 0]

print(particle_trajectory)

pl.add_lines(particle_trajectory * 1000, color='black', width=3, connected=True)
#pl.add_lines(np.array([[0, 0, 0], [0, 0, 1]]), color='black')
pl.show()