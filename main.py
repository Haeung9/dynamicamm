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
    marketPriceTrend = [1000.0 + (i*10.0) for i in range(numberOfTimePoints)]
    normalNoise = rng.normal(loc = 0.0, scale= 1.0, size=numberOfTimePoints).tolist()
    marketPricePrediction0 = [marketPriceTrend[i] * ( 1.0 + ( 0.1 * normalNoise[i])) for i in range(numberOfTimePoints)]
    marketPricePrediction1 = [marketPriceTrend[i] * ( 1.0 + ( 0.05 * normalNoise[i])) for i in range(numberOfTimePoints)]
    marketPricePrediction2 = [marketPriceTrend[i] * ( 1.0 + ( 0.01 * normalNoise[i])) for i in range(numberOfTimePoints)]
    marketPricePrediction3 = [marketPriceTrend[i] * ( 1.0 + ( 0.005 * normalNoise[i])) for i in range(numberOfTimePoints)]
    marketPricePrediction4 = [marketPriceTrend[i] * ( 1.0 + ( 0.001 * normalNoise[i])) for i in range(numberOfTimePoints)]
    # marketPricePrediction0 = utils.generatePricePredictionWithMAPE(marketPriceTrend, rng, 0.05)  
    # marketPricePrediction1 = utils.generatePricePredictionWithMAPE(marketPriceTrend, rng, 0.01) 
    # marketPricePrediction2 = utils.generatePricePredictionWithMAPE(marketPriceTrend, rng, 0.005) 
    # marketPricePrediction3 = utils.generatePricePredictionWithMAPE(marketPriceTrend, rng, 0.001) 
    marketPriceData = pd.DataFrame({"real": marketPriceTrend, 
                                    "prediction0": marketPricePrediction0, 
                                    "prediction1": marketPricePrediction1, 
                                    "prediction2": marketPricePrediction2,
                                    "prediction3": marketPricePrediction3,
                                    "prediction4": marketPricePrediction4
                                    })
    # startIndex = 296
    # priceDataFull = pd.read_csv(readFileName, sep=",")
    # marketPriceTrend = priceDataFull.iloc[startIndex:startIndex+numberOfTimePoints,0].tolist()
    # marketPricePrediction = priceDataFull.iloc[startIndex:startIndex+numberOfTimePoints,1].tolist()
    # marketPriceData = pd.DataFrame({"real": marketPriceTrend, "prediction": marketPricePrediction})
    marketPriceData.to_csv(writeFileName, sep=",")
    simulationScenarios = scenario.generatePredictionErrorScenarios(marketPriceTrend, marketPricePrediction0, marketPricePrediction1, marketPricePrediction2, marketPricePrediction3, marketPricePrediction4)
    
    # Run simulation and analyize the result
    # simulation.main(
    #         simulationScenarios, 
    #         rootpath, 
    #         randomSeed = seed, 
    #         arbitragePeriod = numberOfTimePoints/2, 
    #         verbose = True)
    # analysis.main(datadirpath, simulationScenarios)

    # Monte Carlo Setting
    numberOfSimulations = 10000
    results = []
    tstart = time.time()
    for i in range(numberOfSimulations):
        seed = seed + 1
        simulation.main(
            simulationScenarios, 
            rootpath, 
            randomSeed = seed, 
            arbitragePeriod = numberOfTimePoints, 
            verbose = False)
        il = analysis.monteCarloAnalysis(datadirpath, simulationScenarios)
        results.append(il)
        if i % 100 == 0:
            print('sim ', i, ', elapsed: ' , time.time() - tstart)
    print('end:', time.time() - tstart)
    montecarlodir = utils.directoryMaker('montecarlo')
    monteCarloFileName = os.path.join(montecarlodir, "result.csv")
    resultBuff = results[0]
    for i in range(numberOfSimulations-1):
        results[0].add(results[i+1])
        resultBuff = pd.concat([resultBuff, results[i+1]], axis = 1)
    results[0].div(numberOfSimulations)
    print(results[0])
    resultBuff.to_csv(monteCarloFileName, sep=",")