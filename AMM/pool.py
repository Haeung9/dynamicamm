import math

class Pool: # abstract
    def __init__(self, reserve0 = 0.0, reserve1 = 0.0, feeRate = 0.003, marketPrice = 1.0, feeInPool = False):
        self.reserves = [reserve0, reserve1] # a pair of reserves of Asset 0 and Asset 1
        self.feeRate = feeRate 
        self.fees = [0.0, 0.0] # cumulative fee
        self.marketPrice = marketPrice # market price of Asset 0, in terms of Asset 1
        self.feeInPool = feeInPool
    def getReserve0(self):
        return self.reserves[0]
    def getReserve1(self):
        return self.reserves[1]
    def getReserve(self, assetId):
        return self.reserves[assetId]
    def getFeeReserve0(self):
        return self.fees[0]
    def getFeeReserve1(self):
        return self.fees[1]
    def getMarketPrice0(self):
        return self.marketPrice
    def setMarketPrice0(self, newMarketPrice):
        self.marketPrice = newMarketPrice
    def calculateTotalValue(self, marketPrice0):
        return (self.reserves[1] + (marketPrice0 * self.reserves[0]))
    def calculateTotalFeeValue(self, marketprice0):
        return (self.fees[1] + (marketprice0 * self.fees[0]))
    
    # abstract, must overload at child
    def calculateOutputAmount(self, inputAssetId, effectiveInputAmount: float) -> float :
        pass # must return outputAmount
    # abstract, must overload at child
    def calculatePrice(self, assetId) -> float :
        pass # must return price
    # abstract, must overload at child
    def calculateReserveForTargetPrice0(self, targetPrice0, assetId) -> float :
        pass # must return required reserve of assetId, in order to poolPrice reaches to targetPrice0

    def swap(self, inputAssetId, inputAmount): # Always use try-except for swap method. 
        if inputAmount < 0:
            raise Exception("Wrong input amount") 
        effectiveInputAmount = inputAmount*(1-self.feeRate) # effective inputAmount that used for swap, except fee
        outputAmount = self.calculateOutputAmount(inputAssetId, effectiveInputAmount)
        if outputAmount > self.reserves[(inputAssetId+1)%2]:
            raise Exception("Swap size is too large")
        self.reserves[inputAssetId] += effectiveInputAmount
        self.reserves[(inputAssetId+1)%2] -= outputAmount
        feeAmount = inputAmount - effectiveInputAmount
        self.fees[inputAssetId] += feeAmount
        if self.feeInPool:
            self.reserves[inputAssetId] += feeAmount
        return outputAmount
    
    def calculateExpectedArbitrageProfit(self): 
        poolPrice0 = self.calculatePrice(0)
        marketPrice0 = self.getMarketPrice0()
        if marketPrice0 > poolPrice0: # arbitrageurs buy Asset0 from pool and sell it to market
            inputAssetId = 1
            marketPrice = 1/marketPrice0 # dbz
        elif marketPrice0 < poolPrice0: # arbitrageurs buy Asset1 from pool and sell it to market
            inputAssetId = 0
            marketPrice = marketPrice0
        else:
            return [0.0, 0.0, 0] 
        currentInputReserve = self.getReserve(inputAssetId)
        targetInputReserve = self.calculateReserveForTargetPrice0(marketPrice0, inputAssetId)
        spentAmount = targetInputReserve - currentInputReserve
        arbitrageOutputAmount = self.calculateOutputAmount(inputAssetId, spentAmount)
        earnedAmount = arbitrageOutputAmount / marketPrice
        profitAmount = earnedAmount - spentAmount
        return [spentAmount, profitAmount, inputAssetId]
    
    def arbitrageAsMuchAsPossible(self, maximumAmount0, maximumAmount1):
        [desiredInputAmount, profitAmount, inputAssetId] = self.calculateExpectedArbitrageProfit()
        maximumInputAmount = maximumAmount0 if inputAssetId == 0 else maximumAmount1
        if profitAmount > 0.0:
            inputAmount = desiredInputAmount if desiredInputAmount < maximumInputAmount else maximumInputAmount
            try:
                outputAmount = self.swap(inputAssetId, inputAmount)
            except Exception:
                inputAmount = 0.0
                outputAmount = 0.0
        else:
            inputAssetId = 0
            inputAmount = 0.0
            outputAmount = 0.0
        return [inputAssetId, inputAmount, outputAmount]
    

""" CPMM
    Let x == asset0, y == asset1
    1. curve:
        x * y = K

    2. dx -- dy relationship:
        x * y = (x + dx) * (y + dy)
        x*dy + y*dx + dx*dy = 0
        dy = - y * dx / (x + dx)
        dx = - x * dy / (y + dy)

    3. instantaneous price (negative derivative of curve):
        y = K / x
        derivative = - K / (x^2)
        price = y / x
"""
class CPMMPool(Pool): 
    def calculateParameterK(self):
        return self.reserves[0]*self.reserves[1]

    def calculatePrice(self, assetId): # overload super
        return self.reserves[(assetId+1)%2]/self.reserves[assetId]

    def calculateOutputAmount(self, inputAssetId, inputAmount): # overload super
        if inputAmount < 0:
            print(inputAmount)
            raise Exception("Wrong input amount") 
        outputAmount = (self.reserves[(inputAssetId+1)%2]*inputAmount)/(self.reserves[inputAssetId] + inputAmount)
        # outputAmount = (outputReserve*inputAmount)/(inputReserve + inputAmount)
        return outputAmount
    
    def calculateReserveForTargetPrice0(self, targetPrice0, assetId): # overload super
        if assetId == 0:
            targetPrice = targetPrice0
        elif assetId == 1:
            targetPrice = 1/targetPrice0
        else:
            raise Exception("Wrong asset id")
        parameterK = self.calculateParameterK()
        targetReserve = math.sqrt(parameterK / targetPrice) # x^2 = K / p, or y^2 = K * p
        return targetReserve

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
class DCPMMPool(Pool):
    def calculateParameterA(self):
        reserve0 = self.getReserve0()
        reserve1 = self.getReserve1()
        price0 = self.getMarketPrice0()
        parameterA = reserve0 - (reserve1/price0) # TODO: except dbz
        return parameterA

    def calculatePrice(self, assetId): # overload super
        if assetId == 0:
            price = self.getMarketPrice0()
        elif assetId == 1:
            price = self.getMarketPrice0()
            price = 1/price # TODO: except divid by zero
        else:
            raise Exception("Wrong asset ID")
        return price
    
    def calculateOutputAmount(self, inputAssetId, inputAmount): # overload super
        if inputAmount < 0:
            print(inputAmount)
            raise Exception("Wrong input amount") 
        reserve0 = self.getReserve0()
        reserve1 = self.getReserve1()
        parameterA = self.calculateParameterA()

        if inputAssetId == 0:
            outputAmount = reserve1 * inputAmount / (reserve0 + inputAmount - parameterA)
        elif inputAssetId == 1:
            outputAmount = (reserve0 - parameterA) * inputAmount / (reserve1 + inputAmount)
        else:
            raise Exception("Wrong asset ID")
        return outputAmount

    def calculateReserveForTargetPrice0(self, targetPrice0, assetId): # overload super
        parameterA = self.calculateParameterA()
        if assetId == 0:
            reserve1 = self.getReserve1()
            targetReserve = parameterA + (reserve1 / targetPrice0) # x = a + (y/p)
        elif assetId == 1:
            reserve0 = self.getReserve0()
            targetReserve = targetPrice0 * (reserve0 - parameterA) # y = p * (x-a)
        else:
            raise Exception("Wrong asset id")
        return targetReserve

""" DCSMM
    Let x == asset0, y == asset1
    1. curve:
        price0 * x + y = K

    2. dx -- dy relationship:
        price0 * x + y = price0 * (x + dx) + y + dy
        price0 * dx + dy = 0
        dy = - price0 * dx
        dx = - dy / price0

    3. instantaneous price (negative derivative of curve):
        = price0
"""
class DCSMMPool(Pool): 
    def calculateParameterK(self):
        reserve0 = self.getReserve0()
        reserve1 = self.getReserve1()
        price0 = self.calculatePrice(0)
        return ( (price0*reserve0) + reserve1 )

    def calculatePrice(self, assetId): # overload super
        if assetId == 0:
            price = self.getMarketPrice0()
        elif assetId == 1:
            price = self.getMarketPrice0()
            price = 1/price # TODO: except divid by zero
        else:
            raise Exception("Wrong asset ID")
        return price

    def calculateOutputAmount(self, inputAssetId, inputAmount): # overload super
        if inputAmount < 0:
            print(inputAmount)
            raise Exception("Wrong input amount") 
        price0 = self.calculatePrice(0)
        if inputAssetId == 0:
            outputAmount = inputAmount * price0
        elif inputAssetId == 1:
            outputAmount = inputAmount / price0
        else:
            raise Exception("Wrong asset ID")
        return outputAmount
    
    def calculateReserveForTargetPrice0(self, targetPrice0, assetId): # overload super
        price0 = self.calculatePrice(0)
        parameterK = self.calculateParameterK()
        if price0 == targetPrice0:
            targetReserve = self.getReserve(assetId)
        elif price0 < targetPrice0: # if x is cheap
            targetReserve = parameterK if assetId == 1 else 0.0 # buy all x; thus x -> 0 and y -> K
        else: # price0 > targetPrice0, y is cheap
            targetReserve = parameterK/price0 if assetId == 0 else 0.0 # buy all y; thus x -> K/p and y -> 0
        return targetReserve

""" WCSMM (exactly same with DCSMM, except price0 = initialPrice0.)
    Equivalent to CSMM, if initialPrice0 = 1.
    Let x == asset0, y == asset1
    1. curve:
        price0 * x + y = K

    2. dx -- dy relationship:
        price0 * x + y = price0 * (x + dx) + y + dy
        price0 * dx + dy = 0
        dy = - price0 * dx
        dx = - dy / price0

    3. instantaneous price (negative derivative of curve):
        = price0
"""
class WCSMMPool(Pool): # CSMM pool with weight. The price ratio can differ from 1.
    def __init__(self, reserve0 = 0.0, reserve1 = 0.0, feeRate = 0.003, marketPrice = 1.0, feeInPool = False):
        super().__init__(reserve0, reserve1, feeRate, marketPrice, feeInPool)
        if ((reserve0 == 0) | (reserve1 == 0)):
            raise Exception("Wrong initial reserves")
        self.__initialPrice0 = reserve1/reserve0
    
    def calculateParameterK(self):
        reserve0 = self.getReserve0()
        reserve1 = self.getReserve1()
        price0 = self.calculatePrice(0)
        return ( (price0*reserve0) + reserve1 )

    def calculatePrice(self, assetId): # overload super
        if assetId == 0:
            return self.__initialPrice0 
        elif assetId == 1:
            return 1/self.__initialPrice0
        else:
            raise Exception("Wrong input asset id")
        
    def calculateOutputAmount(self, inputAssetId, inputAmount): # overload super
        if inputAmount < 0:
            raise Exception("Wrong input amount") 
        price = self.calculatePrice(inputAssetId)
        outputAmount = inputAmount * price
        return outputAmount
    
    def calculateReserveForTargetPrice0(self, targetPrice0, assetId): # overload super
        price0 = self.calculatePrice(0)
        parameterK = self.calculateParameterK()
        if price0 == targetPrice0:
            targetReserve = self.getReserve(assetId)
        elif price0 < targetPrice0: # if x is cheap
            targetReserve = parameterK if assetId == 1 else 0.0 # buy all x; x -> 0 and y -> K
        else: # price0 > targetPrice0, y is cheap
            targetReserve = parameterK/price0 if assetId == 0 else 0.0 # buy all y; x -> K/p and y -> 0
        return targetReserve

