class Agent:
    def __init__(self, balance0 = 0.0, balance1 = 0.0):
        self.balances = [balance0, balance1]
    def getBalance0(self):
        return self.balances[0]
    def getBalance1(self):
        return self.balances[1]
    def calculateTotalValue(self, marketPrice0):
        return (self.balances[1] + (marketPrice0 * self.balances[0]))
    def spendAsset(self, assetId, amount):
        if not self.balances[assetId] >= amount:
            raise(Exception, 'insufficient balance')
        self.balances[assetId] -= amount   
    def earnAsset(self, assetId, amount):
        self.balances[assetId] += amount
    def trade(self, earnedAssetId, earnedAmount, spentAmount):
        self.spendAsset((earnedAssetId+1)%2, spentAmount)
        self.earnAsset(earnedAssetId, earnedAmount)