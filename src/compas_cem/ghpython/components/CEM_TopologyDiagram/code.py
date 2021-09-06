"""
Assemble a topology diagram.
"""
from ghpythonlib.componentbase import executingcomponent as component

from compas_cem.diagrams import TopologyDiagram


class AssembleTopologyDiagramComponent(component):
    def RunScript(self, trail_edges, deviation_edges, loads, supports, add_auxiliary_trails):

        add_auxiliary_trails = add_auxiliary_trails or False
        topology = TopologyDiagram()

        if trail_edges:
            for trail_edge in trail_edges:
                topology.add_edge(trail_edge)

        if deviation_edges:
            for deviation_edge in deviation_edges:
                topology.add_edge(deviation_edge)

        if loads:
            for load in loads:
                topology.add_load(load)

        if supports:
            for support in supports:
                topology.add_support(support)

        if trail_edges and supports:
            topology.build_trails(add_auxiliary_trails)

        return topology
