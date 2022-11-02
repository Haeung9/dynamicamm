import os
from AMM import analysis, simulation

if __name__ == "__main__":
    rootpath = os.getcwd()
    datadirpath = os.path.join(rootpath, "data")
    simulationScenarios = ["CPMM", "CSMM", "DCPMM", "DCSMM"]
    simulation.main(simulationScenarios, rootpath)
    analysis.main(datadirpath, simulationScenarios)