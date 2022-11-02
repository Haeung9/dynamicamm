import os
import pandas

def directoryMaker(subdirName, rootpath = os.getcwd()):
    datadirpath = os.path.join(rootpath, "data")
    simdirpath = os.path.join(datadirpath, subdirName)
    try:
        if not os.path.exists(simdirpath):
            os.makedirs(simdirpath)
    except OSError:
        print("Error: Failed to create the directory.")
    return simdirpath

def resultFileWriter(snapshotPool, snapshotTraders, snapshotArbitrageurs, marketPriceTrend, dirpath, separator = "\t"):
    numberOfTimePoints = len(marketPriceTrend)
    labels = ["PoolValue", "PoolReserve0", "PoolReserve1",
    "TradersValue", "TradersReserve0", "TradersReserve1",
    "ArbitrageursValue", "ArbitrageursReserve0", "ArbitrageursReserve1",
    "FeeValue", "FeeReserve0", "FeeReserve1"]
    result = pandas.DataFrame(columns = labels, index=[i for i in range(numberOfTimePoints)])
    for i in range(numberOfTimePoints):
        result.iloc[i, 0] = snapshotPool[i].calculateTotalValue(marketPriceTrend[-1])
        result.iloc[i, 1] = snapshotPool[i].getReserve0()
        result.iloc[i, 2] = snapshotPool[i].getReserve1()
        result.iloc[i, 3] = snapshotTraders[i].calculateTotalValue(marketPriceTrend[-1])
        result.iloc[i, 4] = snapshotTraders[i].getBalance0()
        result.iloc[i, 5] = snapshotTraders[i].getBalance1()
        result.iloc[i, 6] = snapshotArbitrageurs[i].calculateTotalValue(marketPriceTrend[-1])
        result.iloc[i, 7] = snapshotArbitrageurs[i].getBalance0()
        result.iloc[i, 8] = snapshotArbitrageurs[i].getBalance1()
        result.iloc[i, 9] = snapshotPool[i].calculateTotalFeeValue(marketPriceTrend[-1])
        result.iloc[i, 10] = snapshotPool[i].getFeeReserve0()
        result.iloc[i, 11] = snapshotPool[i].getFeeReserve1()
    fileName = os.path.join(dirpath, "result.csv")
    result.to_csv(fileName, sep=separator)