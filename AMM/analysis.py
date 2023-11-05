import os
import pandas as pd
import matplotlib.pyplot as plt
from . import scenario
from typing import List, Dict

def loadData(nameSeparators: List[str], datadirpath):
    result = []
    for i in range(len(nameSeparators)):
        resultdirpath = os.path.join(datadirpath, nameSeparators[i])
        fileName = os.path.join(resultdirpath, "result.csv")
        result.append(pd.read_csv(fileName, sep=","))
    return result

def extractNameSeparators(simulationScenarios: List[scenario.Scenario]) -> List[str]:
    nameSeparators = []
    for i in range(len(simulationScenarios)):
        nameSeparators.append(simulationScenarios[i].getName())
    return nameSeparators

def calculateIL(result: pd.DataFrame, nameSeparators: List[str], returns = False, verbose = False) -> pd.DataFrame:
    data = []
    for i in range(len(nameSeparators)):
        impermanentLoss = result[i].at[0,"PoolValue"] - result[i].at[result[i].index[-1],"PoolValue"]
        impermanentLossPercentage = 100 *(1 - (result[i].at[result[i].index[-1],"PoolValue"]/result[i].at[0,"PoolValue"]))
        if verbose:
            print(nameSeparators[i]+", IL: "+str(impermanentLoss) + " (" + str(impermanentLossPercentage) + " %)")
        if returns:
            data.append([impermanentLoss, impermanentLossPercentage])
    if returns:
        labels = ['IL', 'percentage']
        output = pd.DataFrame(data = data, columns = labels, index = nameSeparators)
    return output

def monteCarloAnalysis(datadirpath, simulationScenarios: List[scenario.Scenario]) -> pd.DataFrame:
    nameSeparators = extractNameSeparators(simulationScenarios)
    try:
        result = loadData(nameSeparators, datadirpath)
    except:
        raise Exception("Fail to load data")
    output = calculateIL(result, nameSeparators, returns = True)
    return output

def main(datadirpath, simulationScenarios: List[scenario.Scenario]):
    nameSeparators = extractNameSeparators(simulationScenarios)
    try:
        result = loadData(nameSeparators, datadirpath)
    except:
        raise Exception("Fail to load data")
    print("Simulation Scenarios:")
    print(nameSeparators)
    calculateIL(result, nameSeparators, returns = False, verbose = True)

    xasis = [i for i in range(len(result[0].index))]   
    for i in range(len(nameSeparators)):
        plt.figure(constrained_layout=True)
        titleString = nameSeparators[i]
        plt.subplot(1,3,1)
        plt.title(titleString+", value (USD)")
        plt.xlabel("Time")
        plt.ylabel("Value (USD)")
        plt.plot(xasis, result[i]["PoolValue"], 
        xasis, result[i]["TradersValue"], 
        xasis, result[i]["ArbitrageursValue"],"-r")
        plt.legend(["Pool", "Traders", "Arbitrageurs"])

        plt.subplot(1,3,2)
        plt.title(titleString+", ETH quantity")
        plt.xlabel("Time")
        plt.ylabel("ETH")
        plt.plot(xasis, result[i]["PoolReserve0"], 
        xasis, result[i]["TradersReserve0"], 
        xasis, result[i]["ArbitrageursReserve0"],"-r")
        plt.legend(["Pool", "Traders", "Arbitrageurs"])

        plt.subplot(1,3,3)
        plt.title(titleString+", DAI quantity")
        plt.xlabel("Time")
        plt.ylabel("DAI")
        plt.plot(xasis, result[i]["PoolReserve1"], 
        xasis, result[i]["TradersReserve1"], 
        xasis, result[i]["ArbitrageursReserve1"],"-r")
        plt.legend(["Pool", "Traders", "Arbitrageurs"])
   
    plt.figure(constrained_layout=True)
    plt.title("Market price trend")
    plt.xlabel("Time (block)")
    plt.ylabel("Market Price of ETH (USD)")
    priceDataFile = os.path.join(datadirpath,"price.csv")
    priceData = pd.read_csv(priceDataFile, sep=",")
    priceXasis = [i for i in range(len(priceData))]
    try:
        pricePrediction = priceData["prediction"]
        plt.plot(priceXasis, priceData["real"], priceXasis, pricePrediction)
        plt.legend(["real","prediction"])
    except(KeyError):
        priceReal = priceData["real"].to_list()
        pricePrediction0 = priceData["prediction0"].to_list()
        pricePrediction1 = priceData["prediction1"].to_list()
        pricePrediction2 = priceData["prediction2"].to_list()
        pricePrediction3 = priceData["prediction3"].to_list()
        pricePrediction4 = priceData["prediction4"].to_list()
        plt.plot(priceXasis, priceReal, priceXasis, pricePrediction0, priceXasis, pricePrediction1, priceXasis, pricePrediction2, priceXasis, pricePrediction3, priceXasis, pricePrediction4)
        plt.legend(["real", "pricePrediction0", "pricePrediction1", "pricePrediction2", "pricePrediction3", "pricePrediction4"])
    plt.show()
  
if __name__ == "__main__":
    maindirpath = os.path.join(os.getcwd(), os.pardir)
    datadirpath = os.path.join(maindirpath, "data")
    priceDataFile = os.path.join(datadirpath,"price.csv")
    try:
        priceData = pd.read_csv(priceDataFile, sep=",")
    except:
        try:
            maindirpath = os.getcwd()
            datadirpath = os.path.join(maindirpath, "data")
            priceDataFile = os.path.join(datadirpath,"price.csv")
            priceData = pd.read_csv(priceDataFile, sep=",")
        except:
            raise Exception("Fail to load data")
    try:
        marketPrice = priceData["real"].tolist()
        marketPricePrediction = priceData["prediction"].tolist()
    except:
        marketPrice = []
        marketPricePrediction = []
    simulationScenarios = scenario.generateDefaultScenarios(marketPrice, marketPricePrediction)
    main(datadirpath, simulationScenarios)
    