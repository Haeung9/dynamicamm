import unittest
from AMM import advancedPool

class DCPMMPoolTest(unittest.TestCase):
    def test_overrides(self):
        apool = advancedPool.DCPMMPool(reserve0=100.0, reserve1=100.0, feeRate=0.0, marketPrice= 1.0)
        with self.assertRaises(TypeError): 
            apool.swap(0, 10)

    def test_swapWithoutFee(self):
        # test case 1: balanced swap
        apool = advancedPool.DCPMMPool(reserve0=100.0, reserve1=100.0, feeRate=0.0, marketPrice= 1.0)
        apool.setBlockTime(1688000000)
        parameterA = apool.calculateParameterA() # A = x - y/p
        self.assertEqual(parameterA, 0.0)
        outputAmount = apool.swap(0,10, 1.0, 1688000000) # dy = - y * dx / (x + dx - A)
        self.assertEqual(outputAmount, 1000/110)
        reserve0 = apool.getReserve0()
        reserve1 = apool.getReserve1()
        self.assertEqual(reserve0, 110)
        self.assertEqual(reserve1, 100-(1000/110))

        # test case 2: 0 -> 1 unbalanced swap
        apool = advancedPool.DCPMMPool(reserve0=100.0, reserve1=100.0, feeRate=0.0, marketPrice=2.0)
        apool.setBlockTime(1688000000)
        parameterA = apool.calculateParameterA() # A = x - y/p
        self.assertEqual(parameterA, 50.0)
        outputAmount = apool.swap(0,10, 2.0, 1688000000) 
        self.assertEqual(outputAmount, 1000/60) # dy = - y * dx / (x + dx - A)
        reserve0 = apool.getReserve0()
        reserve1 = apool.getReserve1()
        self.assertEqual(reserve0, 110)
        self.assertEqual(reserve1, 100-(1000/60))

        # test case 3: 1 -> 0 unbalanced swap
        apool = advancedPool.DCPMMPool(reserve0=100.0, reserve1=100.0, feeRate=0.0, marketPrice=2.0)
        apool.setBlockTime(1688000000)
        parameterA = apool.calculateParameterA() # A = x - y/p
        self.assertEqual(parameterA, 50.0)
        outputAmount = apool.swap(1,10, 2.0, 1688000000) 
        self.assertEqual(outputAmount, 500/110) # dx = - (x - A) * dy / (y + dy)
        reserve0 = apool.getReserve0()
        reserve1 = apool.getReserve1()
        self.assertEqual(reserve0, 100-(500/110))
        self.assertEqual(reserve1, 110)

        # test case 4: Wrong input amount
        apool = advancedPool.DCPMMPool(reserve0=100.0, reserve1=100.0, feeRate=0.0)
        apool.setBlockTime(1688000000)
        with self.assertRaisesRegex(Exception, "Wrong input amount"):
            apool.swap(0, -10.0, 1.0, 1688000000)
        reserve0 = apool.getReserve0()
        reserve1 = apool.getReserve1()
        self.assertEqual(reserve0, 100.0)
        self.assertEqual(reserve1, 100.0)
    
    def test_toLargeSwap(self):
        apool = advancedPool.DCPMMPool(reserve0=100.0, reserve1=100.0, feeRate=0.0)
        apool.swap(0,99999999999999999999999999999999999999999999.0, 1.0, 1688000000) # never raise
    
    def test_adjustAfterSwap(self):
        # test case 1: balanced swap
        apool = advancedPool.DCPMMPool(reserve0=100.0, reserve1=100.0, feeRate=0.0, marketPrice= 1.0)
        parameterA = apool.calculateParameterA() # A = x - y/p = 0
        self.assertEqual(parameterA, 0.0)
        outputAmount = apool.swap(0,10, 1.0, 1688000000) # dy = - y * dx / (x + dx - A) = 100 * 10 / 110
        parameterA_adjusted = apool.calculateParameterA() # x = 110, y = 100-(100/11), A = 110 - (1000/11)
        self.assertEqual(parameterA_adjusted, 110-(1000/11))
    
    def test_setMarketPrice(self):
        # test case 1: real time update
        apool = advancedPool.DCPMMPool(reserve0=100.0, reserve1=100.0, feeRate=0.0, marketPrice= 1.0)
        blockTime = 1688999999
        apool.setBlockTime(blockTime)
        marketPrice0 = apool.getMarketPrice0()
        self.assertEqual(marketPrice0, 1.0)

        parameterA = apool.calculateParameterA() # A = x - y/p
        self.assertEqual(parameterA, 0.0) # parameter A before swap (p=1.0)
        parameterAWithCustomPrice = apool.calculateParameterAWithCustomPrice(2.0)
        self.assertEqual(parameterAWithCustomPrice, 50.0)
        outputAmount = apool.swap(0,10, inputMarketPrice= 2.0, inputTimestamp= blockTime) # dy = - y * dx / (x + dx - A) = 100 * 10 / 60
        self.assertEqual(outputAmount, 1000/60) # dy = - y * dx / (x + dx - A)
        reserve0 = apool.getReserve0()
        reserve1 = apool.getReserve1()
        self.assertEqual(reserve0, 110)
        self.assertEqual(reserve1, 100-(1000/60))

        # test case 2: real time update with small clock error
        apool = advancedPool.DCPMMPool(reserve0=100.0, reserve1=100.0, feeRate=0.0, marketPrice= 1.0)
        blockTime = 1688999999
        clockError = 100
        apool.setBlockTime(blockTime)
        marketPrice0 = apool.getMarketPrice0()
        self.assertEqual(marketPrice0, 1.0)

        parameterA = apool.calculateParameterA() # A = x - y/p
        self.assertEqual(parameterA, 0.0) # parameter A before swap (p=1.0)
        parameterAWithCustomPrice = apool.calculateParameterAWithCustomPrice(2.0)
        self.assertEqual(parameterAWithCustomPrice, 50.0)
        outputAmount = apool.swap(0,10, inputMarketPrice= 2.0, inputTimestamp= blockTime-clockError) # dy = - y * dx / (x + dx - A) = 100 * 10 / 60
        self.assertEqual(outputAmount, 1000/60) # dy = - y * dx / (x + dx - A)
        reserve0 = apool.getReserve0()
        reserve1 = apool.getReserve1()
        self.assertEqual(reserve0, 110)
        self.assertEqual(reserve1, 100-(1000/60))
