from . import pool

""" DCPMM
    Let x == asset0, y == asset1
    1. curve:
        W * (x - A) * y = K
    2. dx -- dy relationship:
        W * (x - A) * y = W * (x + dx - A) * (y + dy)
        W * (x + dx - A) * dy + W * y * dx = 0
        (x + dx - A) * dy + y * dx = 0
        dy = - y * dx / (x + dx - A)
        dx = - (x - A) * dy / (y + dy)
    3. instantaneous price (negative derivative of curve):
        y = (K / W) * ( 1/(x- A) )
        derivative = -1 * (K / W) * ( 1/(x - A)^2 )
        price = y / (x - A)
"""
class DCPMMPool(pool.DCPMMPool):
    def __init__(self, reserve0 = 0.0, reserve1 = 0.0, feeRate = 0.003, marketPrice = 1.0, latestTimestamp = 1688000000, feeInPool = False):
        super().__init__(reserve0, reserve1, feeRate, marketPrice, feeInPool)
        self.setBlockTime(latestTimestamp)
        self.latestTimestamp = latestTimestamp
        self.outdateThreshold = 10000
        self.maximumPriceChangeRatio = 1.003
        self.arbtrageSensitivity = 0.5
    
    def setMarketPrice0(self, newMarketPrice: float, newTimestamp: int) -> bool: # override
        if self.latestCheck(newTimestamp):
            self.latestTimestamp = newTimestamp
            self.marketPrice = newMarketPrice
            return True
        else:
            return False
    
    def setBlockTime(self, newBlockTime: int):
        self.blockTime = newBlockTime

    def latestCheck(self, dataTimestamp: int) -> bool:
        return dataTimestamp >= self.latestTimestamp
    def deadlineCheck(self, dataTimestamp: int) -> bool:
        isOutdatedComparedToLatest = ((self.latestTimestamp - dataTimestamp) < self.outdateThreshold)
        isOutdatedComparedToBlockTime = ((self.blockTime - dataTimestamp) < self.outdateThreshold)
        return not (isOutdatedComparedToLatest or isOutdatedComparedToBlockTime)
    def slippageCheck(self, inputAssetId: int, inputAmount: float) -> bool:
        poolPrice0 = self.calculatePrice(0)
        realMarketPrice0 = self.approximateMinimumMarketPrice() if inputAssetId == 0 else self.approximateMaximumMarketPrice()
        priceRatio = realMarketPrice0/poolPrice0
        isArbitrageProfitable = (priceRatio < (1.0 - self.feeRate)) if inputAssetId == 0 else (priceRatio > (1.0 / (1.0 - self.feeRate)))
        if isArbitrageProfitable:
            maximumAllowableInputAmount = self.computeMaximumAllowableInputAmount0() if inputAssetId == 0 else self.computeMaximumAllowableInputAmount1()
            return (inputAmount <= maximumAllowableInputAmount)
        return True
        
    
    def approximateMaximumMarketPrice(self) -> float:
        timePassed = self.blockTime - self.latestTimestamp
        maximumPrice0 = self.marketPrice * (self.maximumPriceChangeRatio)**timePassed
        return maximumPrice0
    def approximateMinimumMarketPrice(self) -> float:
        timePassed = self.blockTime - self.latestTimestamp
        minimumPrice0 = self.marketPrice * (self.maximumPriceChangeRatio)**timePassed
        return minimumPrice0
    def computeMaximumAllowableInputAmount0(self) -> float:
        minimumPrice0 = self.approximateMinimumMarketPrice()
        optimalInputAmount0WorstCase = self.calculateOptimalArbitrageAmount(realMarketPrice = minimumPrice0, inputAssetId = 0)
        maximumAllowableInputAmount0 = optimalInputAmount0WorstCase * (1.0 - self.arbtrageSensitivity)
        return maximumAllowableInputAmount0
    def computeMaximumAllowableInputAmount1(self) -> float:
        maximumPrice0 = self.approximateMaximumMarketPrice()
        optimalInputAmount1WorstCase = self.calculateOptimalArbitrageAmount(realMarketPrice = maximumPrice0, inputAssetId = 1)
        maximumAllowableInputAmount1 = optimalInputAmount1WorstCase * (1.0 - self.arbtrageSensitivity)
        return maximumAllowableInputAmount1

    def calculateParameterAWithCustomPrice(self, customPrice: float) -> float:
        reserve0 = self.getReserve0()
        reserve1 = self.getReserve1()
        price0 = customPrice
        parameterA = reserve0 - (reserve1/price0) # TODO: except dbz
        return parameterA
    
    def calculateOutputAmountWithCustomPrice(self, inputAssetId: int, inputAmount: float, customPrice0: float) -> float: 
        if inputAmount < 0:
            print(inputAmount)
            raise Exception("Wrong input amount") 
        reserve0 = self.getReserve0()
        reserve1 = self.getReserve1()
        parameterA = self.calculateParameterAWithCustomPrice(customPrice0)

        if inputAssetId == 0:
            outputAmount = reserve1 * inputAmount / (reserve0 + inputAmount - parameterA)
        elif inputAssetId == 1:
            outputAmount = (reserve0 - parameterA) * inputAmount / (reserve1 + inputAmount)
        else:
            raise Exception("Wrong asset id")
        return outputAmount

    def isInputAllowable(self, inputAssetId: int, inputAmount: float, inputTimestamp: int) -> bool:
        if not self.latestCheck(inputTimestamp):
            if not self.deadlineCheck(inputTimestamp):
                return False
            if not self.slippageCheck(inputAssetId, inputAmount):
                return False
        return True

    def swap(self, inputAssetId: int, inputAmount: float, inputMarketPrice: float, inputTimestamp: int): # Override. Always use try-except for swap method. 
        if self.isInputAllowable(inputAssetId, inputAmount, inputTimestamp):
            self.setMarketPrice0(inputMarketPrice, inputTimestamp)
            return super().swap(inputAssetId, inputAmount)
        else:
            raise Exception("outdated price")

