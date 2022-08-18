"""
Generate a form diagram in static equilibrium such that it meets user-defined constraints.
"""
from ghpythonlib.componentbase import executingcomponent as component
from scriptcontext import sticky

from compas.rpc import Proxy


class ConstrainedFormFindingComponent(component):
    def RunScript(self, solve, topology, constraints, parameters, algorithm, iters_max, eps, kappa, tmax, eta):
        algorithm = algorithm or "SLSQP"
        iters_max = iters_max or 100
        eps = eps or 1e-6
        tmax = tmax or 100
        eta = eta or 1e-6

        if not (solve and topology and constraints and parameters):
            return

        topology = topology.copy()

        # clean constraints and parameters from None
        constraints = [c for c in constraints if c is not None]
        parameters = [p for p in parameters if p is not None]

        # fetch optimization proxy from scriptcontext
        opt = sticky.get("proxy_cem")
        proxy_temp_exists = opt is not None

        # create temporary proxy server if unavailable from scriptcontext
        if not proxy_temp_exists:
            opt = Proxy("compas_cem.optimization")

        # solve constrained form-finding problem
        solution = opt.solve_proxy(topology=topology,
                                   constraints=constraints,
                                   parameters=parameters,
                                   algorithm=algorithm,
                                   iters=iters_max,
                                   eps=eps,
                                   kappa=kappa,
                                   tmax=tmax,
                                   eta=eta)

        # shut down temporary proxy
        if not proxy_temp_exists:
            opt.stop_server()

        # unpack solution
        topology, form, objective, grad_norm, iters, time, status = solution

        return topology, form, objective, grad_norm, iters, time, status
