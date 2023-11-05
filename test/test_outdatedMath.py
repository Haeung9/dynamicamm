import unittest
from AMM import outdatedMath

class OutdatedMathTest(unittest.TestCase):
    def test_swapWithCurrent(self):
        testPool = outdatedMath.DCPMMwithOutdated(reserve0=1000.0, reserve1=1000.0, feeRate=0.0)
        currentBlockNumber = 12345
        currentPrice = 2.0
        testPool.marketPrice = currentPrice
        testPool.lastBlockNumberStamp = currentBlockNumber
        testPool.currentBlockNumber = currentBlockNumber
        outputAmount1 = testPool.swap(
            inputAssetId=0, 
            inputAmount= 1.0, 
            marketPrice=currentPrice, 
            blockNumberStamp=currentBlockNumber, 
            signature=''
        )
        expected = 1000.0 / 501.0 # ~ 1.996
        self.assertEqual(outputAmount1, expected)
    def test_swapWithoutPrice(self):
        testPool = outdatedMath.DCPMMwithOutdated(reserve0=1000.0, reserve1=1000.0, feeRate=0.0)
        currentBlockNumber = 12345
        currentPrice = 2.0
        testPool.marketPrice = currentPrice
        testPool.lastBlockNumberStamp = currentBlockNumber
        testPool.currentBlockNumber = currentBlockNumber
        with self.assertRaises(TypeError):
            testPool.swap(inputAssetId=0, inputAmount= 1.0)
    def test_swapWithUpdated(self):
        testPool = outdatedMath.DCPMMwithOutdated(reserve0=1000.0, reserve1=1000.0, feeRate=0.0)
        testPool.marketPrice = 1.9
        testPool.lastBlockNumberStamp = 9999
        testPool.currentBlockNumber = 10000
        currentBlockNumber = 10000
        currentPrice = 2.0
        outputAmount1 = testPool.swap(
            inputAssetId=0, 
            inputAmount= 1.0, 
            marketPrice=currentPrice, 
            blockNumberStamp=currentBlockNumber, 
            signature=''
        )
        expected = 1000.0 / 501.0 # ~ 1.996
        self.assertEqual(outputAmount1, expected)

    def test_swapWithOutdated_allowableCheck(self):
        testPool = outdatedMath.DCPMMwithOutdated(reserve0=1000.0, reserve1=1000.0, feeRate=0.0)
        currentBlockNumber = 10000
        currentPrice = 2.0
        testPool.lastBlockNumberStamp = currentBlockNumber
        testPool.currentBlockNumber = currentBlockNumber
        testPool.marketPrice = currentPrice
        outdatedBlockNumberStamp = 9990
        outdatedPrice = 1.0
        
        with self.assertRaisesRegex(Exception, 'expired input'):
            outputAmount1 = testPool.swap(
                inputAssetId=0, 
                inputAmount= 1.0, 
                marketPrice=outdatedPrice, 
                blockNumberStamp=outdatedBlockNumberStamp, 
                signature=''
            )

        outdatedBlockNumberStamp = 9991 
        outputAmount1 = testPool.swap(
            inputAssetId=0, 
            inputAmount= 1.0, 
            marketPrice=outdatedPrice, 
            blockNumberStamp=outdatedBlockNumberStamp, 
            signature=''
        ) # must be executed with current price (2.0), thanks to negative silppage
        expected = 1000.0 / 501.0 # ~ 1.996
        self.assertEqual(outputAmount1, expected)

        testPool.reserves = [1000.0, 1000.0]
        outdatedPrice = 3.0
        with self.assertRaisesRegex(Exception, 'too high slipage'):
            outputAmount1 = testPool.swap(
                inputAssetId=0, 
                inputAmount= 1.0, 
                marketPrice=outdatedPrice, 
                blockNumberStamp=outdatedBlockNumberStamp, 
                signature=''
            )

