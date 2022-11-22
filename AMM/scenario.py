class Scenario:
    def __init__(self, curve = "CPMM", priceType = "real", price = [], pricePrediction = [], feeInPool = True):
        self.curve = curve
        self.priceType = priceType
        self.price = price
        self.pricePrediction = pricePrediction
        self.tradersBudget0 = 10000.0
        self.tradersBudget1 = 10000.0
        self.arbitrageursBudget0 = 10000.0
        self.arbitrageursBudget1 = 10000.0
        self.poolBudget0 = 10000.0
        self.poolBudget1 = 10000.0
        self.feeInPool = feeInPool

    def getName(self):
        feeInPool = "feeInPool" if self.feeInPool else "feeOutofPool"
        name = self.curve + "_" + self.priceType + "_" + feeInPool
        return name

def generateDefaultScenarios(marketPriceTrend = [], marketPricePrediction = []):
    defaultScenarios = [Scenario(curve="CPMM", priceType="real", price=marketPriceTrend, pricePrediction=marketPricePrediction), 
    Scenario(curve="CSMM", priceType="real", price=marketPriceTrend, pricePrediction=marketPricePrediction), 
    Scenario(curve="DCPMM", priceType="real", price=marketPriceTrend, pricePrediction=marketPricePrediction),
    Scenario(curve="DCPMM", priceType="prediction", price=marketPriceTrend, pricePrediction=marketPricePrediction), 
    Scenario(curve="DCSMM", priceType="real", price=marketPriceTrend, pricePrediction=marketPricePrediction),
    Scenario(curve="DCSMM", priceType="prediction", price=marketPriceTrend, pricePrediction=marketPricePrediction)]
    return defaultScenarios
    