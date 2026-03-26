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

grid_length = 50
grid = CartesianGrid(-0.1 * u.m, 0.1 * u.m, num=grid_length)


magnet = magpy.magnet.Cuboid(polarization=(0, 0, 0.1), dimension=(0.01, 0.01, 0.01))
positions = np.zeros((18, 3), dtype=np.float32)
polarizations = np.zeros((18, 3), dtype=np.float32)
for i in range(positions.shape[0] // 3):
    positions[i*3][0] = np.sin(i * 2 * np.pi / 6) * 0.02
    positions[i*3][1] = np.cos(i * 2 * np.pi / 6) * 0.02
    positions[i*3][2] = -0.03

    polarizations[i*3][2] = 0.3

    positions[i*3+1][0] = np.sin(i * 2 * np.pi / 6) * 0.02
    positions[i*3+1][1] = np.cos(i * 2 * np.pi / 6) * 0.02
    positions[i*3+1][2] = 0.0

    polarizations[i*3+1][2] = -0.3

    positions[i*3+2][0] = np.sin(i * 2 * np.pi / 6) * 0.02
    positions[i*3+2][1] = np.cos(i * 2 * np.pi / 6) * 0.02
    positions[i*3+2][2] = 0.03

    polarizations[i*3+2][2] = 0.3

magnet.position = positions * u.m

B = magnet.getB(grid.grid) * u.T
B = np.sum(B, axis=0)

grid.add_quantities(B_x=B[:,:,:,0], B_y=B[:,:,:,1], B_z=B[:,:,:,2])

x0 = [[0.002, 0, -0.05]] * u.m
v0 = [[0, 100, 2000]] * u.m / u.s
particle = Particle("p+")

termination_condition = TimeElapsedTerminationCondition(0.00006 * u.second)
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

particle_trajectory = results["x"][:, 0]

pl = pv.Plotter()
magpy.show(magnet, canvas=pl)


# Magnetic field line grid
# grid = pv.ImageData(
#     dimensions=(100, 100, 100),
#     spacing=(0.002, 0.002, 0.002),
#     origin=(-0.1, -0.1, -0.1),
# )

# # Compute B-field and add as data to grid
# print(B.shape, grid.shape)
# grid["B"] = B * 1000 # T -> mT

# # Compute the field lines
# seed = pv.Disc(inner=0.02, outer=0.03, r_res=1, c_res=9, normal=(0, 0, 1))
# strl = grid.streamlines_from_source(
#     seed,
#     vectors="B",
#     max_step_length=0.1,
#     max_time=0.05,
#     integration_direction="both",
# )

# legend_args = {
#     "title": "B (mT)",
#     "title_font_size": 20,
#     "color": "black",
#     "position_y": 0.25,
#     "vertical": True,
# }

# # Add streamlines and legend to scene
# pl.add_mesh(
#     strl.tube(radius=0.0002).scale([1000.0, 1000.0, 1000.0]),
#     cmap="bwr",
#     scalar_bar_args=legend_args,
# )

pl.add_lines(particle_trajectory * 1000, color='black', width=3, connected=True)
pl.show()