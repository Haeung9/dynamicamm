class Scenario:
    def __init__(self, curve = "CPMM", priceType = "real", price = [1.0], pricePrediction = [1.0], feeInPool = True, id = 0):
        self.curve = curve
        self.priceType = priceType
        self.price = price
        self.pricePrediction = pricePrediction
        self.tradersBudget0 = 10000.0
        self.tradersBudget1 = 10000.0 * price[0]
        self.arbitrageursBudget0 = 10000.0
        self.arbitrageursBudget1 = 10000.0 * price[0]
        self.poolBudget0 = 10000.0
        self.poolBudget1 = 10000.0 * price[0]
        self.feeInPool = feeInPool
        self.id = id

    def getName(self):
        # feeInPool = "feeInPool" if self.feeInPool else "feeOutofPool"
        # name = self.curve + "_" + self.priceType + "_" + feeInPool
        name = self.curve + "_" + self.priceType + "_" + str(self.id)
        return name

def generateDefaultScenarios(marketPriceTrend = [], marketPricePrediction = []):
    defaultScenarios = [Scenario(curve="CPMM", priceType="real", price=marketPriceTrend, pricePrediction=marketPricePrediction, feeInPool=False), 
    Scenario(curve="CSMM", priceType="real", price=marketPriceTrend, pricePrediction=marketPricePrediction, feeInPool=False), 
    Scenario(curve="DCPMM", priceType="real", price=marketPriceTrend, pricePrediction=marketPricePrediction, feeInPool=False),
    Scenario(curve="DCPMM", priceType="prediction", price=marketPriceTrend, pricePrediction=marketPricePrediction, feeInPool=False), 
    Scenario(curve="DCSMM", priceType="real", price=marketPriceTrend, pricePrediction=marketPricePrediction, feeInPool=False),
    Scenario(curve="DCSMM", priceType="prediction", price=marketPriceTrend, pricePrediction=marketPricePrediction, feeInPool=False)]
    return defaultScenarios

def generatePredictionErrorScenarios(marketPriceTrend = [], *marketPricePredictions):
    numberOfScenarios = len(marketPricePredictions)
    scenarios = [Scenario(curve="CPMM", priceType="real", price=marketPriceTrend, pricePrediction=marketPriceTrend, feeInPool=False),
    Scenario(curve="DCPMM", priceType="real", price=marketPriceTrend, pricePrediction=marketPriceTrend, feeInPool=False)]

    for i in range(numberOfScenarios):
        scenarios.append(Scenario(curve="DCPMM", priceType="prediction", price=marketPriceTrend, pricePrediction=marketPricePredictions[i], feeInPool= False, id = i))
    
    return scenarios
    