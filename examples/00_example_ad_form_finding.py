from compas.geometry import Translation

from compas_cem.diagrams import TopologyDiagram

from compas_cem.elements import Node
from compas_cem.elements import TrailEdge
from compas_cem.elements import DeviationEdge

from compas_cem.loads import NodeLoad
from compas_cem.supports import NodeSupport

from compas_cem.equilibrium import static_equilibrium

from compas_cem.plotters import Plotter
from matplotlib import axes, axis

topology = TopologyDiagram()
# force_density = 1.0
trail_length = 1.0
deviation_force = 1.0

topology.add_node(Node(0, [0.0, 0.0, 1.0]))
topology.add_node(Node(1, [1.0, 0.0, 1.0]))
topology.add_node(Node(2, [2, 0.0, 1.0]))
topology.add_node(Node(3, [3, 0.0, 1.0]))
topology.add_node(Node(4, [4, 0.0, 1.0]))
topology.add_node(Node(5, [5.0, 0.0, 1.0]))

topology.add_node(Node(6, [0, 0.0, 0.0]))
topology.add_node(Node(7, [1, 0.0, 0.0]))
topology.add_node(Node(8, [2, 0.0, 0.0]))
topology.add_node(Node(9, [3, 0.0, 0.0]))
topology.add_node(Node(10, [4, 0.0, 0.0]))
topology.add_node(Node(11, [5, 0.0, 0.0]))

print("TRAIL EDGE\n\n")

# print(TrailEdge(0, 1, length=-1.5))

# upper chord
topology.add_edge(TrailEdge(0, 1, length=trail_length))
topology.add_edge(TrailEdge(1, 2, length=trail_length))
topology.add_edge(DeviationEdge(2, 3, force=deviation_force))
topology.add_edge(TrailEdge(3, 4, length=trail_length))
topology.add_edge(TrailEdge(4, 5, length=trail_length))

# lower chord
topology.add_edge(TrailEdge(6, 7, length=trail_length))
topology.add_edge(TrailEdge(7, 8, length=trail_length))
topology.add_edge(DeviationEdge(8, 9,  force=deviation_force))
topology.add_edge(TrailEdge(9, 10, length=trail_length))
topology.add_edge(TrailEdge(10, 11, length=trail_length))

# direct connections
topology.add_edge(DeviationEdge(1, 7, force=deviation_force))
topology.add_edge(DeviationEdge(2, 8,  force=deviation_force))
topology.add_edge(DeviationEdge(3, 9, force=deviation_force))
topology.add_edge(DeviationEdge(4, 10, force=deviation_force))

# indirect connections
topology.add_edge(DeviationEdge(1, 8, force=deviation_force))
topology.add_edge(DeviationEdge(2, 9,  force=deviation_force))
topology.add_edge(DeviationEdge(3, 10, force=deviation_force))
topology.add_edge(DeviationEdge(2, 7, force=deviation_force))
topology.add_edge(DeviationEdge(3, 8, force=deviation_force))
topology.add_edge(DeviationEdge(4, 9, force=deviation_force))

# supports
topology.add_support(NodeSupport(0))
topology.add_support(NodeSupport(5))
topology.add_support(NodeSupport(6))
topology.add_support(NodeSupport(11))

topology.add_load(NodeLoad(7,  [0.0, 0.0, -1.0]))
topology.add_load(NodeLoad(8,  [0.0, 0.0, -1.0]))
topology.add_load(NodeLoad(9,  [0.0, 0.0, -1.0]))
topology.add_load(NodeLoad(10,  [0.0, 0.0, -1.0]))

topology.build_trails()

print("\n\n Before Static Eq.\n\n")
form = static_equilibrium(topology, eta=1e-6, tmax=100, verbose=True)
print("\n\n After Static Eq.\n\n")

plotter = Plotter(  )

artist = plotter.add(topology, nodesize=0.2, show_nodetext=True, show_edgetext=True)

# print( form.nodes() )

# add shifted form diagram to the scene
form = form.transformed(Translation.from_vector([0.0, -2.0, 0.0]))


# print(str(form))

plotter.add(form, nodesize=0.1, show_nodetext=True, show_edgetext=True)

# show plotter contents

plotter.zoom_extents()
plotter.show()


# # upper chord
# graph.add_edge(0, 1, force_density=force_density, cem_type='trail', length=trail_length)
# graph.add_edge(1, 2, force_density=force_density, cem_type='trail', length=trail_length)
# graph.add_edge(2, 3, force_density=force_density, cem_type='deviation', force=deviation_force)
# graph.add_edge(3, 4, force_density=force_density, cem_type='trail', length=trail_length)
# graph.add_edge(4, 5, force_density=force_density, cem_type='trail', length=trail_length)

# # lower chord
# graph.add_edge(6, 7, force_density=force_density, cem_type='trail', length=trail_length)
# graph.add_edge(7, 8, force_density=force_density, cem_type='trail', length=trail_length)
# graph.add_edge(8, 9, force_density=force_density, cem_type='deviation', force=deviation_force)
# graph.add_edge(9, 10, force_density=force_density, cem_type='trail', length=trail_length)
# graph.add_edge(10, 'eleven', force_density=force_density, cem_type='trail', length=trail_length)

# # direct connections
# graph.add_edge(1, 7, force_density=force_density, cem_type='deviation', force=deviation_force)
# graph.add_edge(2, 8, force_density=force_density, cem_type='deviation', force=deviation_force)
# graph.add_edge(3, 9, force_density=force_density, cem_type='deviation', force=deviation_force)
# graph.add_edge(4, 10, force_density=force_density, cem_type='deviation', force=deviation_force)

# # indirect connections
# graph.add_edge(1, 8, force_density=force_density, cem_type='deviation', force=deviation_force)
# graph.add_edge(2, 9, force_density=force_density, cem_type='deviation', force=deviation_force)
# graph.add_edge(3, 10, force_density=force_density, cem_type='deviation', force=deviation_force)
# graph.add_edge(2, 7, force_density=force_density, cem_type='deviation', force=deviation_force)
# graph.add_edge(3, 8, force_density=force_density, cem_type='deviation', force=deviation_force)
# graph.add_edge(4, 9, force_density=force_density, cem_type='deviation', force=deviation_force)

# supports
# graph.nodes[0]['support_condition'] = [1, 1, 1]
# graph.nodes[5]['support_condition'] = [1, 1, 1]
# graph.nodes[6]['support_condition'] = [1, 1, 1]
# graph.nodes['eleven']['support_condition'] = [1, 1, 1]

# graph.nodes[0]['coordinates'] = [0.0, 0.0, 1.0]
# graph.nodes[5]['coordinates'] = [5.0, 0.0, 1.0]
# graph.nodes[6]['coordinates'] = [0.0, 0.0, 0.0]
# graph.nodes['eleven']['coordinates'] = [5.0, 0.0, 0.0]

# # load
# graph.nodes[7]['load'] = [0.0, 0.0, -1.0]
# graph.nodes[8]['load'] = [0.0, 0.0, -1.0]
# graph.nodes[9]['load'] = [0.0, 0.0, -1.0]
# graph.nodes[10]['load'] = [0.0, 0.0, -1.0]

# origin nodes
# graph.nodes[2]['origin'] = True
# graph.nodes[3]['origin'] = True
# graph.nodes[8]['origin'] = True
# graph.nodes[9]['origin'] = True
# graph.nodes[2]['coordinates'] = [2.0, 0.0, 1.0]
# graph.nodes[3]['coordinates'] = [3.0, 0.0, 1.0]
# graph.nodes[8]['coordinates'] = [2.0, 0.0, 0.0]
# graph.nodes[9]['coordinates'] = [3.0, 0.0, 0.0]
