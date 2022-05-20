import os

from time import time

from compas.geometry import Point
from compas.geometry import Translation

from compas_plotters import Plotter

from compas_cem.diagrams import TopologyDiagram

from compas_cem.loads import NodeLoad
from compas_cem.supports import NodeSupport

from compas_cem.equilibrium import static_equilibrium

from compas_cem import PROXY_PORT

from compas.rpc import Proxy

from compas_cem.optimization import PointConstraint

from compas_cem.optimization import TrailEdgeParameter
from compas_cem.optimization import DeviationEdgeParameter

from compas_cem.plotters import TopologyArtist
from compas_cem.plotters import FormArtist


# ------------------------------------------------------------------------------
# Data
# ------------------------------------------------------------------------------

HERE = os.path.dirname(__file__)
IN = os.path.abspath(os.path.join(HERE, "03_bridge_2d.json"))

# ------------------------------------------------------------------------------
# Load topology diagram from JSON
# ------------------------------------------------------------------------------

topology = TopologyDiagram.from_json(IN)

# ------------------------------------------------------------------------------
# Add supports
# ------------------------------------------------------------------------------

topology.add_support(NodeSupport(1))
topology.add_support(NodeSupport(5))

# ------------------------------------------------------------------------------
# Apply loads
# ------------------------------------------------------------------------------

topology.add_load(NodeLoad(2, [0.0, -1.0, 0.0]))
topology.add_load(NodeLoad(6, [0.0, -1.0, 0.0]))

# ------------------------------------------------------------------------------
# Generate trails
# ------------------------------------------------------------------------------

topology.build_trails()

# ------------------------------------------------------------------------------
# Form-finding
# ------------------------------------------------------------------------------

form = static_equilibrium(topology)

# ------------------------------------------------------------------------------
# Define constraints
# ------------------------------------------------------------------------------

constraints = []
nodes_opt = [1, 5]
target_points = [[-20.67, 42.7, 0.0], [15.7, 28.84, 0.0]]
for node, target_point in zip(nodes_opt, target_points):
    constraints.append(PointConstraint(node, Point(*target_point)))

# ------------------------------------------------------------------------------
# Define optimization parameters
# ------------------------------------------------------------------------------

parameters = []
for edge in topology.trail_edges():
    parameters.append(TrailEdgeParameter(edge, bound_low=15.0, bound_up=5.0))

for edge in topology.deviation_edges():
    parameters.append(DeviationEdgeParameter(edge, bound_low=10.0, bound_up=10.0))

# ------------------------------------------------------------------------------
# Optimization
# ------------------------------------------------------------------------------

# record starting time
start = time()

# optimize
with Proxy("compas_cem.optimization", port=PROXY_PORT) as opt:
    solution = opt.solve_nlopt_proxy(topology.copy(),
                                     constraints=constraints,
                                     parameters=parameters,
                                     algorithm="SLSQP",
                                     iters=100,
                                     eps=None,
                                     tmax=100,
                                     eta=1e-6)

form_opt, objective, grad_norm, iters, time, status = solution

# print out results
# print("----------")
# print(f"Optimizer. # Parameters {opt.number_of_parameters()}, # Constraints {opt.number_of_constraints()}")
# print(f"Optimization elapsed time: {time() - start}")
# print(f"Final value of the objective function: {opt.penalty}")
# print(f"Norm of the gradient of the objective function: {opt.gradient_norm}")

# ------------------------------------------------------------------------------
# Plotter
# ------------------------------------------------------------------------------

plotter = Plotter(figsize=(16, 9))
nodesize = 4.0
loadscale = 6.0

# ------------------------------------------------------------------------------
# Plot topology diagram
# ------------------------------------------------------------------------------

plotter.add(topology,
            artist_type=TopologyArtist,
            nodesize=nodesize)

# ------------------------------------------------------------------------------
# Plot translated form diagram
# ------------------------------------------------------------------------------

T = Translation.from_vector([40.0, 0.0, 0.0])
plotter.add(form.transformed(T),
            artist_type=FormArtist,
            loadscale=loadscale,
            nodesize=nodesize)

# add target points
for target_point in target_points:
    x, y, z = target_point
    plotter.add(Point(x, y, z).transformed(T), size=5.0, facecolor=(1.0, 0.6, 0.0))

# ------------------------------------------------------------------------------
# Plot translated optimized form diagram
# ------------------------------------------------------------------------------

T = Translation.from_vector([90.0, 0.0, 0.0])
plotter.add(form_opt.transformed(T),
            artist_type=FormArtist,
            loadscale=loadscale,
            reactionscale=5.0,
            nodesize=nodesize)

# add target points
for target_point in target_points:
    x, y, z = target_point
    plotter.add(Point(x, y, z).transformed(T), size=5.0, facecolor=(1.0, 0.6, 0.0))

# ------------------------------------------------------------------------------
# Plot scene
# -------------------------------------------------------------------------------

plotter.zoom_extents()
plotter.show()
