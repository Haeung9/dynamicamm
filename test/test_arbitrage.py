import unittest
import math
from AMM import pool

class arbitrageTest(unittest.TestCase):
    def test_arbitrage_CSMM(self):
        # balanced, no fee
        CSMMPool = pool.WCSMMPool(1000.0, 1000.0, feeRate=0.0) # initial price = 1.0
        CSMMPool.arbitrageAsMuchAsPossible(99999.0, 99999.0, realMarketPrice0= 1.001)
        reserve0 = CSMMPool.getReserve0()
        reserve1 = CSMMPool.getReserve1()
        self.assertEqual(reserve0, 0.0)
        self.assertEqual(reserve1, 2000.0)

        CSMMPool.arbitrageAsMuchAsPossible(99999.0, 99999.0, realMarketPrice0= 0.999)
        reserve0 = CSMMPool.getReserve0()
        reserve1 = CSMMPool.getReserve1()
        self.assertEqual(reserve0, 2000.0)
        self.assertEqual(reserve1, 0.0)

        # unbalanced, no fee
        CSMMPool = pool.WCSMMPool(2000.0, 1000.0, feeRate=0.0) # initial price = 0.5
        CSMMPool.arbitrageAsMuchAsPossible(99999.0, 99999.0, realMarketPrice0= 0.501)
        reserve0 = CSMMPool.getReserve0()
        reserve1 = CSMMPool.getReserve1()
        self.assertEqual(reserve0, 0.0)
        self.assertEqual(reserve1, 2000.0)

        CSMMPool.arbitrageAsMuchAsPossible(99999.0, 99999.0, realMarketPrice0= 0.499)
        reserve0 = CSMMPool.getReserve0()
        reserve1 = CSMMPool.getReserve1()
        self.assertEqual(reserve0, 4000.0)
        self.assertEqual(reserve1, 0.0)

        # with fee
        CSMMPool = pool.WCSMMPool(2000.0, 1000.0, feeRate=0.1) # initial price = 0.5
        CSMMPool.arbitrageAsMuchAsPossible(99999.0, 99999.0, realMarketPrice0= 0.501) # no profitable region
        reserve0 = CSMMPool.getReserve0()
        reserve1 = CSMMPool.getReserve1()
        self.assertEqual(reserve0, 2000.0)
        self.assertEqual(reserve1, 1000.0)

        CSMMPool.arbitrageAsMuchAsPossible(99999.0, 99999.0, realMarketPrice0= 1.0) # profitable region
        reserve0 = CSMMPool.getReserve0()
        reserve1 = CSMMPool.getReserve1()
        self.assertEqual(reserve0, 0.0)
        self.assertEqual(reserve1, 2000.0)
    
    def test_arbitrage_CPMM(self):
        # no fee
        CPMMPool = pool.CPMMPool(1000.0, 1000.0, feeRate= 0.0) # price = 1.0, mktprice= 0.5
        expectedInputAssetId = 0
        expectedInputAmount = (1000.0 * math.sqrt(2)) - 1000.0
        expectedOutputAmount = CPMMPool.calculateOutputAmount(0, expectedInputAmount)
        [inputAssetId, arbitrageAmount, outputAmount] = CPMMPool.arbitrageAsMuchAsPossible(99999.0, 99999.0, realMarketPrice0= 0.5)
        reserve0 = CPMMPool.getReserve0()
        reserve1 = CPMMPool.getReserve1()
        self.assertEqual(expectedInputAssetId, inputAssetId)
        self.assertEqual(expectedInputAmount, arbitrageAmount)
        self.assertEqual(expectedOutputAmount, outputAmount)
        self.assertEqual(1000.0 + expectedInputAmount, reserve0)
        self.assertEqual(1000.0 - expectedOutputAmount, reserve1)

        CPMMPool = pool.CPMMPool(1000.0, 1000.0, feeRate= 0.0) # price = 1.0, mktprice = 2.0
        expectedInputAssetId = 1
        expectedInputAmount = (1000.0 * math.sqrt(2)) - 1000.0
        expectedOutputAmount = CPMMPool.calculateOutputAmount(1, expectedInputAmount)
        [inputAssetId, arbitrageAmount, outputAmount] = CPMMPool.arbitrageAsMuchAsPossible(99999.0, 99999.0, realMarketPrice0= 2.0)
        reserve0 = CPMMPool.getReserve0()
        reserve1 = CPMMPool.getReserve1()
        self.assertEqual(expectedInputAssetId, inputAssetId)
        self.assertEqual(expectedInputAmount, arbitrageAmount)
        self.assertEqual(expectedOutputAmount, outputAmount)
        self.assertEqual(1000.0 - expectedOutputAmount, reserve0)
        self.assertEqual(1000.0 + expectedInputAmount, reserve1)
        
        # with fee, no profitable but profitable without fee
        CPMMPool = pool.CPMMPool(1000.0, 1000.0, feeRate= 0.1) # price = 1.0
        CPMMPool.arbitrageAsMuchAsPossible(99999.0, 99999.0, realMarketPrice0= 1.01)
        reserve0 = CPMMPool.getReserve0()
        reserve1 = CPMMPool.getReserve1()
        self.assertEqual(1000.0, reserve0)
        self.assertEqual(1000.0, reserve1)

        CPMMPool = pool.CPMMPool(1000.0, 1000.0, feeRate= 0.0) # price = 1.0
        CPMMPool.arbitrageAsMuchAsPossible(99999.0, 99999.0, realMarketPrice0= 1.01)
        reserve0 = CPMMPool.getReserve0()
        reserve1 = CPMMPool.getReserve1()
        self.assertNotEqual(1000.0, reserve0)
        self.assertNotEqual(1000.0, reserve1)

        # with fee, profitable
        CPMMPool = pool.CPMMPool(1000.0, 1000.0, feeRate= 0.1, feeInPool= True) # price = 1.0, mktprice= 2.0
        expectedInputAssetId = 1
        expectedInputAmount = ((1000.0 * math.sqrt(1.8)) - 1000.0)/0.9
        expectedOutputAmount = CPMMPool.calculateOutputAmount(1, expectedInputAmount* 0.9)
        [inputAssetId, arbitrageAmount, outputAmount] = CPMMPool.arbitrageAsMuchAsPossible(99999.0, 99999.0, realMarketPrice0= 2.0)
        reserve0 = CPMMPool.getReserve0()
        reserve1 = CPMMPool.getReserve1()
        self.assertEqual(expectedInputAssetId, inputAssetId)
        self.assertEqual(expectedInputAmount, arbitrageAmount)
        self.assertEqual(expectedOutputAmount, outputAmount)
        self.assertEqual(1000.0 - expectedOutputAmount, reserve0)
        self.assertEqual(1000.0 + expectedInputAmount, reserve1)
        feeReserve1 = CPMMPool.getFeeReserve1()
        self.assertEqual(expectedInputAmount - (expectedInputAmount * 0.9), feeReserve1) 

        CPMMPool = pool.CPMMPool(1000.0, 1000.0, feeRate= 0.1, feeInPool= False) # price = 1.0, mktprice= 2.0, fee out of pool
        expectedInputAssetId = 1
        expectedInputAmount = ((1000.0 * math.sqrt(1.8)) - 1000.0)/0.9
        expectedOutputAmount = CPMMPool.calculateOutputAmount(1, expectedInputAmount * 0.9)
        [inputAssetId, arbitrageAmount, outputAmount] = CPMMPool.arbitrageAsMuchAsPossible(99999.0, 99999.0, realMarketPrice0= 2.0)
        reserve0 = CPMMPool.getReserve0()
        reserve1 = CPMMPool.getReserve1()
        feeReserve1 = CPMMPool.getFeeReserve1()
        self.assertEqual(expectedInputAssetId, inputAssetId)
        self.assertEqual(expectedInputAmount, arbitrageAmount)
        self.assertEqual(expectedOutputAmount, outputAmount)
        self.assertEqual(1000.0 - expectedOutputAmount, reserve0)
        self.assertEqual(1000.0 + (expectedInputAmount * 0.9), reserve1)
        self.assertEqual(expectedInputAmount - (expectedInputAmount * 0.9), feeReserve1) 
        # -> fail with ``assertEqual(expectedInputAmount * 0.1 , feeReserve1)``. Maybe one need to apply safe math and wei based (integar) operation.

