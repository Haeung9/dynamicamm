from . import pool
from . import agent
from . import utils
import numpy
import time
import copy
import os
from typing import List

def runSimulation(Pool: pool.Pool, Traders: agent.Agent, Arbitrageurs: agent.Agent, marketPriceTrend, rng):
    snapshotTraders = []
    snapshotArbitrageurs = []
    snapshotPool = []
    for i in range(len(marketPriceTrend)):
        Pool.setMarketPrice0(marketPriceTrend[i])

        snapshotTraders.append(copy.deepcopy(Traders))
        snapshotArbitrageurs.append(copy.deepcopy(Arbitrageurs))
        snapshotPool.append(copy.deepcopy(Pool))

        tradeAssetId = rng.integers(0,2) # 0 or 1
        tradeValue = rng.random() * 10 # 0 to <10 
        tradeAmount = tradeValue if tradeAssetId == 1 else tradeValue/marketPriceTrend[i]
        if Traders.balances[tradeAssetId] >= tradeAmount:
            try:
                tradeOutputAmount = Pool.swap(tradeAssetId,tradeAmount)
            except Exception:
                tradeOutputAmount = 0.0
                tradeAmount = 0.0
            Traders.trade((tradeAssetId+1)%2, tradeOutputAmount, tradeAmount)

        [inputArbAssetId, inputArbAmount, outputArbAmount] = Pool.arbitrageAsMuchAsPossible(Arbitrageurs.balances[0], Arbitrageurs.balances[1])
        Arbitrageurs.trade((inputArbAssetId+1)%2, outputArbAmount, inputArbAmount)
    return [snapshotPool, snapshotTraders, snapshotArbitrageurs]

def main(simulationScenarios: List[str], rootpath = os.getcwd()):
    # Parameter Setting
    TradersBudget0 = 10000.0
    TradersBudget1 = 10000.0
    ArbitrageursBudget0 = 10000.0
    ArbitrageursBudget1 = 10000.0
    PoolBudget0 = 10000.0
    PoolBudget1 = 10000.0
    numberOfTimePoints = 100
    marketPriceTrend = [(i+1)/10 for i in range(numberOfTimePoints)]
    seed = round(time.time())
    # File Setup
    utils.directoryMaker("", rootpath)
    datadirpath = os.path.join(rootpath, "data")
    fileSeed = open(os.path.join(datadirpath, "randomSeed.txt"), mode="w")
    fileSeed.write(str(seed))
    fileSeed.close()

    for i in range(len(simulationScenarios)):
        # Initialize
        rng = numpy.random.default_rng(seed)
        dirpath = utils.directoryMaker(simulationScenarios[i])
        Traders = agent.Agent(TradersBudget0, TradersBudget1)
        Arbitrageurs = agent.Agent(ArbitrageursBudget0, ArbitrageursBudget1)
        if simulationScenarios[i] == "CPMM":
            Pool = pool.CPMMPool(PoolBudget0, PoolBudget1, feeInPool=True)
        elif simulationScenarios[i] == "CSMM":
            Pool = pool.WCSMMPool(PoolBudget0, PoolBudget1, feeInPool=True)
        elif simulationScenarios[i] == "DCPMM":
            Pool = pool.DCPMMPool(PoolBudget0, PoolBudget1, feeInPool=True)
        elif simulationScenarios[i] == "DCSMM":
            Pool = pool.DCSMMPool(PoolBudget0, PoolBudget1, feeInPool=True)
        else:
            raise Exception("Wrong simulation scenario name")
    
        # sim
        [snapshotPool, snapshotTraders, snapshotArbitrageurs] = runSimulation(Pool, Traders, Arbitrageurs, marketPriceTrend, rng)
        utils.resultFileWriter(snapshotPool, snapshotTraders, snapshotArbitrageurs, marketPriceTrend, dirpath)


