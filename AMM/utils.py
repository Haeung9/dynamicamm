import os

def directoryMaker(subdirName):
    datadirpath = os.path.join(os.getcwd(), "data")
    simdirpath = os.path.join(datadirpath, subdirName)
    try:
        if not os.path.exists(simdirpath):
            os.makedirs(simdirpath)
    except OSError:
        print("Error: Failed to create the directory.")
    return simdirpath

def resultFileWriter(snapshotPool, snapshotTraders, snapshotArbitrageurs, marketPriceTrend, dirpath, separator = "\t"):
    numberOfTimePoints = len(marketPriceTrend)
    fileResult = open(os.path.join(dirpath, "result.csv"), mode="w")
    labels = ["PoolValue", "PoolReserve0", "PoolReserve1",
    "TradersValue", "TradersReserve0", "TradersReserve1",
    "ArbitrageursValue", "ArbitrageursReserve0", "ArbitrageursReserve1",
    "FeeValue", "FeeReserve0", "FeeReserve1"]
    firstRow = separator.join(labels)
    fileResult.write(firstRow)
    fileResult.write("\n")
    for i in range(numberOfTimePoints):
        fileResult.write(str(snapshotPool[i].calculateTotalValue(marketPriceTrend[-1])))
        fileResult.write(separator)
        fileResult.write(str(snapshotPool[i].getReserve0()))
        fileResult.write(separator)
        fileResult.write(str(snapshotPool[i].getReserve1()))
        fileResult.write(separator)
        fileResult.write(str(snapshotTraders[i].calculateTotalValue(marketPriceTrend[-1])))
        fileResult.write(separator)
        fileResult.write(str(snapshotTraders[i].getBalance0()))
        fileResult.write(separator)
        fileResult.write(str(snapshotTraders[i].getBalance1()))
        fileResult.write(separator)
        fileResult.write(str(snapshotArbitrageurs[i].calculateTotalValue(marketPriceTrend[-1])))
        fileResult.write(separator)
        fileResult.write(str(snapshotArbitrageurs[i].getBalance0()))
        fileResult.write(separator)
        fileResult.write(str(snapshotArbitrageurs[i].getBalance1()))
        fileResult.write(separator)
        fileResult.write(str(snapshotPool[i].calculateTotalFeeValue(marketPriceTrend[-1])))
        fileResult.write(separator)
        fileResult.write(str(snapshotPool[i].getFeeReserve0()))
        fileResult.write(separator)
        fileResult.write(str(snapshotPool[i].getFeeReserve1()))
        fileResult.write("\n")
    fileResult.close()
