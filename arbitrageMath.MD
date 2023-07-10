Arbitrage Mathmatics
# Restriction at the pool
A pool rejects a swap unless it satisfies the following two conditions:
```python
class Pool:
    def checkDeadline(self, dataTimestamp: int) -> bool:
        return ((self.latestTimestamp - dataTimestamp) < self.outdateThreshold)
    def checkSlippage(self, inputAssetId: int, inputAmount: float, newMarketPrice0: float) -> bool:
        effectiveInputAmount = inputAmount*(1.0 - self.feeRate)
        outputAmount = self.calculateOutputAmount(inputAssetId, effectiveInputAmount)
        expectedOutputAmount = self.calculatedOutputAmountWithCustomPrice(inputAssetId, effectiveInputAmount, newMarketPrice0)
        slippage = abs((outputAmount - expectedOutputAmount)/outputAmount)
        return (slippage <= self.slippageThreshold)
```
Thus, arbitrage must find an arbitraging point under the conditions.

# 1. Range of Timestamp
`dataTimestamp` must satisfy:
## 1. `Pool.latestTimestamp` - `Pool.outdateThreshold` < `dataTimestamp` to pass `Pool.checkDeadline()`.
## 2. `dataTimestamp` < `currentTimestamp` to obtain arbitrage profit

# 2. Amount of Trade
## 1. Outdate Exploit
Let `price0Latest` as the latest value of `price0` that SC knows. It is possible that the `price0Latest` is outdated since there is no trade on DEX for a long time. In this case, the real-time price, `price0Real` != `price0Latest`. Here, an arbitrageur can issue a trade with outdated price, to exploit the price difference between `price0Latest` (effective price of the trade) and `price0Real`.  
Consider an example in DCPMM DEX. On one hand, a trader will obtain `outputAmount1Real` of asset1, by spending `inputAmount0` with `price0Real`, based on following formula:
```python
outputAmount1Real = - reserve1 * inputAmount0 / (reserve0 + inputAmount0 - reserve0 + (reserve1/price0Real))
```
On the other hand, the trader will obtain `outputAmount1Outdate` of asset1 with `price0Latest`, based on the same formula:
```python
outputAmount1Outdate = - reserve1 * inputAmount0 / (reserve0 + inputAmount0 - reserve0 + (reserve1/price0Latest))
```
If `outputAmount1Outdate` - `outputAmount1Real` > 0, arbitrageurs will queue trades with outdated price for profit.

## 2. Optimal Input Amount for Arbitrageurs
For DCPMM pool, the optimal inputAmount that arbitrageurs (or exploiters) can obtain can be computed as follows:
```python
inputAmount = DCPMMPool.calculateOptimalArbitrageAmount(realMarketPrice0, inputAssetId)
```
Here the `realMarketPrice0` is known to arbitrageurs but isn't known to AMM. However, the AMM can ssume a maximum perturbation of the market price; thus the AMM can approximate the worst case (maximum and minimum) of market price.  
For example, one can assume that the maximum ratio of market price during an unit block-time as `maximumChangeRatio`. Then one can approximate the maximum and minimum of the real-time market price from the latest market price and the corresponding timestamp, as follows:
```python
def approximateMarketPrice(self) -> Tuple[float, float]:
    timePassed = block.timestamp - self.latestTimestamp
    maximumPrice0 = self.marketPrice * (self.maximumChangeRatio)**timePassed
    minimumPrice0 = self.marketPrice * (1/self.maximumChangeRatio)**timePassed
    return (maximumPrice0, minimumPrice0)
```
From the `maximumPrice0` and `minimumPrice0`, AMM can compute the optimal input amount of arbitrageurs under worst-case assumption.
```python
(maximumPrice0, minimumPrice0) = self.approximateMarketPrice(maximumChangeRatio)
optimalInputAmount0WorstCase = self.calculateOptimalArbitrageAmount(realMarketPrice = minimumPrice0, inputAssetId = 0)
optimalInputAmount1WorstCase = self.calculateOptimalArbitrageAmount(realMarketPrice = maximumPrice0, inputAssetId = 1)
```
Then the AMM can prevent too much arbitrage profit by limiting the inputAmounts of a trade for example:
```python
maximumAllowableInputAmount0 = optimalInputAmount0WorstCase * (1.0 - threshold)
maximumAllowableInputAmount1 = optimalInputAmount1WorstCase * (1.0 - threshold)
```


Both too much input amount and too less input amount can make the profitability worse... We need to estabilish a `RANGE` of input amount.



Here 0.0 <= `threshold` < 1.0 determines how much DEX be sensitive for the outdate exploit. The small value of `threshold` means that the DEX allows more opportunities of arbitrage to support lage trades with outdated price, while large value of `threshold` means that the DEX prevents arbitrage attemps at the cost of discarding too large trades with outdated price. This parameter can affect on both fee income and impermanent loss of LPs.

Remind that the arbitrage is profitable when difference between market price and pool price is too large compared to fee rate. i.e., one can establish a quick (and computationally cheap) test for profibability of arbitrage. Let's start from full description of the profitablility:
```python
def isArbitrageProfitable(self):
    poolPrice0 = self.calculatePrice(0)
    realMarketPrice0 = self.approximateMinimumMarketPrice() if inputAssetId == 0 else self.approximateMaximumMarketPrice()
    priceRatio = realMarketPrice0/poolPrice0
    profitablility = (priceRatio < (1.0 - self.feeRate)) if inputAssetId == 0 else (priceRatio > (1.0 / (1.0 - self.feeRate)))
    return profitability
```
Note that here `poolPrice0` = `self.marketPrice`.
```python
priceRatio = (1/self.maximumChangeRatio)**timePassed if inputAssetId == 0 else (self.maximumChangeRatio)**timePassed
```
Here one can compute the minimum required `timePassed` to the arbitrage be profitable.
```python
if inputAssetId == 0:
    timePassed = math.log(1.0 - self.feeRate) / math.log(1/self.maximumChangeRatio)
```
Since `self.feeRate` and `self.maximumChangeRatio` is fixed in general, one can use a pre-computed the minimum required `timePassed` to check the profitability. For example, let `maximumChangeRatio` = 1.0003 and `feeRate` = 0.003, `requiredTimePassed` = 10.01653. Thus the profitability check above can be reduced into:
```python
def isArbitrageProfitable(self):
    return (self.blockTime - self.latesetTimestamp > 10.01653)
```