import os
from AMM import analysis, simulation

if __name__ == "__main__":
    datadirpath = os.path.join(os.getcwd(), "data")
    simulationScenarios = ["CPMM", "CSMM", "DCPMM", "DCSMM"]
    simulation.main(simulationScenarios)
    analysis.main(datadirpath, simulationScenarios)