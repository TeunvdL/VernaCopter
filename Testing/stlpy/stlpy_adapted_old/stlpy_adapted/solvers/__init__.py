# Test whether various optional dependencies are installed
GUROBI_ENABLED = True
try:
    import gurobipy
except ImportError:
    print("WARNING: gurobipy import failed, Gurobi-based solvers disabled.")
    print("         Install Gurobi (https://www.gurobi.com/documentation/)")
    print("         to use the Gurobi-based solvers. Free academic licenses")
    print("         are available.")
    GUROBI_ENABLED = False

if GUROBI_ENABLED:
    from .gurobi.gurobi_micp import GurobiMICPSolver