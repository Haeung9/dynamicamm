import os
import pandas as pd
import matplotlib.pyplot as plt

def loadData(nameSeparators, datadirpath):
    result = []
    for i in range(len(nameSeparators)):
        resultdirpath = os.path.join(datadirpath, nameSeparators[i])
        fileName = os.path.join(resultdirpath, "result.csv")
        result.append(pd.read_csv(fileName, sep="\t"))
    return result

def main(datadirpath, simulationScenarios):
    nameSeparators = simulationScenarios
    try:
        result = loadData(nameSeparators, datadirpath)
    except:
        raise Exception("Fail to load data")
    xasis = [i for i in range(len(result[0].index))]
    
    for i in range(len(nameSeparators)):
        impermenentLoss = result[i].at[0,"PoolValue"] - result[i].at[result[i].index[-1],"PoolValue"]
        print(nameSeparators[i]+", IL: "+str(impermenentLoss))

        plt.figure(constrained_layout=True)
        titleString = nameSeparators[i]
        plt.subplot(1,3,1)
        plt.title(titleString+", value")
        plt.xlabel("Time")
        plt.ylabel("Value")
        plt.plot(xasis, result[i]["PoolValue"], 
        xasis, result[i]["TradersValue"], 
        xasis, result[i]["ArbitrageursValue"],"-r")
        plt.legend(["Pool", "Traders", "Arbitrageurs"])

        plt.subplot(1,3,2)
        plt.title(titleString+", asset0 quantity")
        plt.xlabel("Time")
        plt.ylabel("Asset0")
        plt.plot(xasis, result[i]["PoolReserve0"], 
        xasis, result[i]["TradersReserve0"], 
        xasis, result[i]["ArbitrageursReserve0"],"-r")
        plt.legend(["Pool", "Traders", "Arbitrageurs"])

        plt.subplot(1,3,3)
        plt.title(titleString+", asset1 quantity")
        plt.xlabel("Time")
        plt.ylabel("Asset1")
        plt.plot(xasis, result[i]["PoolReserve1"], 
        xasis, result[i]["TradersReserve1"], 
        xasis, result[i]["ArbitrageursReserve1"],"-r")
        plt.legend(["Pool", "Traders", "Arbitrageurs"])   
    plt.show()
  
if __name__ == "__main__":
    maindirpath = os.path.join(os.getcwd(), os.pardir)
    datadirpath = os.path.join(maindirpath, "data")
    simulationScenarios = ["CPMM", "CSMM", "DCPMM", "DCSMM"]
    main(datadirpath, simulationScenarios)
    