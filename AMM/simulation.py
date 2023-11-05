from . import pool
from . import agent
from . import utils
from . import scenario
import numpy
import time
import copy
import os
from typing import List
        
def runSimulation(Pool: pool.Pool, Traders: agent.Agent, Arbitrageurs: agent.Agent, simulationScenario: scenario.Scenario, rng: numpy.random, riskFactor = 0.0, arbitragePeriod = 1, verbose= False):
    snapshotTraders = []
    snapshotArbitrageurs = []
    snapshotPool = []
    marketPriceTrend = simulationScenario.price
    marketPricePrediction = simulationScenario.pricePrediction if simulationScenario.priceType == "prediction" else simulationScenario.price
    if verbose:
        print(simulationScenario.getName(), ':')
    for i in range(len(marketPriceTrend)):
        Pool.setMarketPrice0(marketPricePrediction[i])
        snapshotTraders.append(copy.deepcopy(Traders))
        snapshotArbitrageurs.append(copy.deepcopy(Arbitrageurs))
        snapshotPool.append(copy.deepcopy(Pool))
        tradeAssetId = rng.integers(0,2) # 0 or 1
        tradeValue = rng.random() * 10.0 # 0 to <10 
        tradeAmount = tradeValue if tradeAssetId == 1 else tradeValue/marketPriceTrend[i]
        if Traders.balances[tradeAssetId] >= tradeAmount:
            try:
                tradeOutputAmount = Pool.swap(tradeAssetId,tradeAmount)
            except Exception:
                tradeOutputAmount = 0.0
                tradeAmount = 0.0
            Traders.trade((tradeAssetId+1)%2, tradeOutputAmount, tradeAmount)
        if ((i + 1) % arbitragePeriod) == 0:
            poolPrice = Pool.calculatePrice(0)
            [inputArbAssetId, inputArbAmount, outputArbAmount] = Pool.arbitrageAsMuchAsPossible(Arbitrageurs.balances[0], Arbitrageurs.balances[1], marketPriceTrend[i], riskFactor=riskFactor)
            Arbitrageurs.trade((inputArbAssetId+1)%2, outputArbAmount, inputArbAmount)
            if verbose and not inputArbAmount == 0.0:
                arbtype = 'FW' if inputArbAssetId == 0 else 'BW'
                amount0 = inputArbAmount if inputArbAssetId == 0 else outputArbAmount
                amount1 = outputArbAmount if inputArbAssetId == 0 else inputArbAmount
                arbArrow = ' -> ' if inputArbAssetId == 0 else ' <- '
                print('    at blk', i, ': ',arbtype, 'arbitrage (asset 0: ', amount0, ')', arbArrow, '(asset 1: ', amount1, ')')
                print('               market price: ', marketPriceTrend[i], ', pool price: ', poolPrice)
    # record last round
    snapshotTraders.append(copy.deepcopy(Traders))
    snapshotArbitrageurs.append(copy.deepcopy(Arbitrageurs))
    snapshotPool.append(copy.deepcopy(Pool))
    return [snapshotPool, snapshotTraders, snapshotArbitrageurs]

def main(simulationScenarios: List[scenario.Scenario], rootpath = os.getcwd(), randomSeed = round(time.time()), riskFactor = 0.0, arbitragePeriod = 1, verbose=False):
    # Parameter Setting
    seed = randomSeed
    # File Setup
    utils.directoryMaker("", rootpath)
    datadirpath = os.path.join(rootpath, "data")
    fileSeed = open(os.path.join(datadirpath, "randomSeed.txt"), mode="w")
    fileSeed.write(str(seed))
    fileSeed.close()

    for i in range(len(simulationScenarios)):
        # Initialize
        rng = numpy.random.default_rng(seed)
        dirName = simulationScenarios[i].getName()
        dirpath = utils.directoryMaker(dirName)
        Traders = agent.Agent(simulationScenarios[i].tradersBudget0, simulationScenarios[i].tradersBudget1)
        Arbitrageurs = agent.Agent(simulationScenarios[i].arbitrageursBudget0, simulationScenarios[i].arbitrageursBudget1)
        poolBudget0 = simulationScenarios[i].poolBudget0
        poolBudget1 = simulationScenarios[i].poolBudget1
        feeInPool = simulationScenarios[i].feeInPool
        if simulationScenarios[i].curve == "CPMM":
            Pool = pool.CPMMPool(poolBudget0, poolBudget1, feeInPool=feeInPool)
        elif simulationScenarios[i].curve == "CSMM":
            Pool = pool.WCSMMPool(poolBudget0, poolBudget1, feeInPool=feeInPool)
        elif simulationScenarios[i].curve == "DCPMM":
            Pool = pool.DCPMMPool(poolBudget0, poolBudget1, feeInPool=feeInPool)
        elif simulationScenarios[i].curve == "DCSMM":
            Pool = pool.DCSMMPool(poolBudget0, poolBudget1, feeInPool=feeInPool)
        else:
            raise Exception("Wrong simulation scenario curve")
        
        if not simulationScenarios[i].price:
            numberOfTimePoints = 100
            simulationScenarios[i].price = [(i+1)/10 for i in range(numberOfTimePoints)]
        else:
            numberOfTimePoints = len(simulationScenarios[i].price)

        if simulationScenarios[i].priceType == "real":
            simulationScenarios[i].pricePrediction = simulationScenarios[i].price
        elif simulationScenarios[i].priceType == "prediction":
            pass
        else:
            raise Exception("Wrong simulation scenario priceType")

        # sim
        [snapshotPool, snapshotTraders, snapshotArbitrageurs] = runSimulation(Pool, Traders, Arbitrageurs, simulationScenarios[i], rng, riskFactor=riskFactor, arbitragePeriod=arbitragePeriod, verbose=verbose)
        utils.resultFileWriter(snapshotPool, snapshotTraders, snapshotArbitrageurs, simulationScenarios[i], dirpath)


