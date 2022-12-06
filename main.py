import os
import time
import numpy as np
import pandas as pd
from AMM import analysis, simulation, scenario, utils

if __name__ == "__main__":
    # Set directory
    rootpath = os.getcwd()
    utils.directoryMaker("", rootpath)
    datadirpath = os.path.join(rootpath, "data")
    writeFileName = os.path.join(datadirpath, "price.csv")
    readFileName = os.path.join(datadirpath, "price_import.csv")
    # Set random seed
    seed = round(time.time())
    rng = np.random.default_rng(seed)
    # Set market price data
    numberOfTimePoints = 100
    # marketPriceTrend = [(i+1)/10 for i in range(numberOfTimePoints)]
    # marketPricePrediction = utils.generatePricePredictionWithError(marketPriceTrend, rng, 0.0025)
    startIndex = 296
    priceDataFull = pd.read_csv(readFileName, sep=",")
    marketPriceTrend = priceDataFull.iloc[startIndex:startIndex+numberOfTimePoints,0].tolist()
    marketPricePrediction = priceDataFull.iloc[startIndex:startIndex+numberOfTimePoints,1].tolist()
    marketPriceData = pd.DataFrame({"real": marketPriceTrend, "prediction": marketPricePrediction})
    marketPriceData.to_csv(writeFileName, sep=",")
    
    # Run simulation and analyize the result
    simulationScenarios = scenario.generateDefaultScenarios(marketPriceTrend, marketPricePrediction)
    simulation.main(simulationScenarios, rootpath, randomSeed=seed)
    analysis.main(datadirpath, simulationScenarios)