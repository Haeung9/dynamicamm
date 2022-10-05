import sys
import os
import unittest
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from AMM import pool

class DCPMMPoolTest(unittest.TestCase):
    def test_swapWithoutFee(self):
        # test case 1: balanced swap
        apool = pool.DCPMMPool(reserve0=100.0, reserve1=100.0, feeRate=0.0, marketPrice= 1.0)
        parameterA = apool.calculateParameterA() # A = x - y/p
        self.assertEqual(parameterA, 0.0)
        outputAmount = apool.swap(0,10) # dy = - y * dx / (x + dx - A)
        self.assertEqual(outputAmount, 1000/110)
        reserve0 = apool.getReserve0()
        reserve1 = apool.getReserve1()
        self.assertEqual(reserve0, 110)
        self.assertEqual(reserve1, 100-(1000/110))

        # test case 2: 0 -> 1 unbalanced swap
        apool = pool.DCPMMPool(reserve0=100.0, reserve1=100.0, feeRate=0.0, marketPrice=2.0)
        parameterA = apool.calculateParameterA() # A = x - y/p
        self.assertEqual(parameterA, 50.0)
        outputAmount = apool.swap(0,10) 
        self.assertEqual(outputAmount, 1000/60) # dy = - y * dx / (x + dx - A)
        reserve0 = apool.getReserve0()
        reserve1 = apool.getReserve1()
        self.assertEqual(reserve0, 110)
        self.assertEqual(reserve1, 100-(1000/60))

        # test case 3: 1 -> 0 unbalanced swap
        apool = pool.DCPMMPool(reserve0=100.0, reserve1=100.0, feeRate=0.0, marketPrice=2.0)
        parameterA = apool.calculateParameterA() # A = x - y/p
        self.assertEqual(parameterA, 50.0)
        outputAmount = apool.swap(1,10) 
        self.assertEqual(outputAmount, 500/110) # dx = - (x - A) * dy / (y + dy)
        reserve0 = apool.getReserve0()
        reserve1 = apool.getReserve1()
        self.assertEqual(reserve0, 100-(500/110))
        self.assertEqual(reserve1, 110)
    
    def test_swapWithFee_feeOutOfPool(self):
        # test case 1: balanced swap
        apool = pool.DCPMMPool(reserve0=100.0, reserve1=100.0, feeRate=0.1, marketPrice= 1.0)
        parameterA = apool.calculateParameterA() # A = x - y/p
        self.assertEqual(parameterA, 0.0)
        outputAmount = apool.swap(0,10) # dy = - y * dx / (x + dx - A)
        self.assertEqual(outputAmount, 900/109)
        reserve0 = apool.getReserve0()
        reserve1 = apool.getReserve1()
        self.assertEqual(reserve0, 109)
        self.assertEqual(reserve1, 100-(900/109))
        fee0 = apool.getFeeReserve0()
        fee1 = apool.getFeeReserve1()
        self.assertEqual(fee0, 1.0)
        self.assertEqual(fee1, 0.0)

        # test case 2: 0 -> 1 unbalanced swap
        apool = pool.DCPMMPool(reserve0=100.0, reserve1=100.0, feeRate=0.1, marketPrice=2.0)
        parameterA = apool.calculateParameterA() # A = x - y/p
        self.assertEqual(parameterA, 50.0)
        outputAmount = apool.swap(0,10) 
        self.assertEqual(outputAmount, 900/59) # dy = - y * dx / (x + dx - A)
        reserve0 = apool.getReserve0()
        reserve1 = apool.getReserve1()
        self.assertEqual(reserve0, 109)
        self.assertEqual(reserve1, 100-(900/59))
        fee0 = apool.getFeeReserve0()
        fee1 = apool.getFeeReserve1()
        self.assertEqual(fee0, 1.0)
        self.assertEqual(fee1, 0.0)

        # test case 3: 1 -> 0 unbalanced swap
        apool = pool.DCPMMPool(reserve0=100.0, reserve1=100.0, feeRate=0.1, marketPrice=2.0)
        parameterA = apool.calculateParameterA() # A = x - y/p
        self.assertEqual(parameterA, 50.0)
        outputAmount = apool.swap(1,10) 
        self.assertEqual(outputAmount, 450/109) # dx = - (x - A) * dy / (y + dy)
        reserve0 = apool.getReserve0()
        reserve1 = apool.getReserve1()
        self.assertEqual(reserve0, 100-(450/109))
        self.assertEqual(reserve1, 109)
        fee0 = apool.getFeeReserve0()
        fee1 = apool.getFeeReserve1()
        self.assertEqual(fee0, 0.0)
        self.assertEqual(fee1, 1.0)
    
    def test_swapWithFee_feeInPool(self):
        # test case 1: balanced swap
        apool = pool.DCPMMPool(reserve0=100.0, reserve1=100.0, feeRate=0.1, marketPrice= 1.0, feeInPool=True)
        parameterA = apool.calculateParameterA() # A = x - y/p
        self.assertEqual(parameterA, 0.0)
        outputAmount = apool.swap(0,10) # dy = - y * dx / (x + dx - A)
        self.assertEqual(outputAmount, 900/109)
        reserve0 = apool.getReserve0()
        reserve1 = apool.getReserve1()
        self.assertEqual(reserve0, 110)
        self.assertEqual(reserve1, 100-(900/109))
        fee0 = apool.getFeeReserve0()
        fee1 = apool.getFeeReserve1()
        self.assertEqual(fee0, 1.0)
        self.assertEqual(fee1, 0.0)

        # test case 2: 0 -> 1 unbalanced swap
        apool = pool.DCPMMPool(reserve0=100.0, reserve1=100.0, feeRate=0.1, marketPrice=2.0, feeInPool=True)
        parameterA = apool.calculateParameterA() # A = x - y/p
        self.assertEqual(parameterA, 50.0)
        outputAmount = apool.swap(0,10) 
        self.assertEqual(outputAmount, 900/59) # dy = - y * dx / (x + dx - A)
        reserve0 = apool.getReserve0()
        reserve1 = apool.getReserve1()
        self.assertEqual(reserve0, 110)
        self.assertEqual(reserve1, 100-(900/59))
        fee0 = apool.getFeeReserve0()
        fee1 = apool.getFeeReserve1()
        self.assertEqual(fee0, 1.0)
        self.assertEqual(fee1, 0.0)

        # test case 3: 1 -> 0 unbalanced swap
        apool = pool.DCPMMPool(reserve0=100.0, reserve1=100.0, feeRate=0.1, marketPrice=2.0, feeInPool=True)
        parameterA = apool.calculateParameterA() # A = x - y/p
        self.assertEqual(parameterA, 50.0)
        outputAmount = apool.swap(1,10) 
        self.assertEqual(outputAmount, 450/109) # dx = - (x - A) * dy / (y + dy)
        reserve0 = apool.getReserve0()
        reserve1 = apool.getReserve1()
        self.assertEqual(reserve0, 100-(450/109))
        self.assertEqual(reserve1, 110)
        fee0 = apool.getFeeReserve0()
        fee1 = apool.getFeeReserve1()
        self.assertEqual(fee0, 0.0)
        self.assertEqual(fee1, 1.0)

    def test_adjustAfterSwap(self):
        # test case 1: balanced swap
        apool = pool.DCPMMPool(reserve0=100.0, reserve1=100.0, feeRate=0.0, marketPrice= 1.0)
        parameterA = apool.calculateParameterA() # A = x - y/p = 0
        self.assertEqual(parameterA, 0.0)
        outputAmount = apool.swap(0,10) # dy = - y * dx / (x + dx - A) = 100 * 10 / 110
        parameterA_adjusted = apool.calculateParameterA() # x = 110, y = 100-(100/11), A = 110 - (1000/11)
        self.assertEqual(parameterA_adjusted, 110-(1000/11))
    
    def test_setMarketPrice(self):
        apool = pool.DCPMMPool(reserve0=100.0, reserve1=100.0, feeRate=0.0, marketPrice= 1.0)
        marketPrice0 = apool.getMarketPrice0()
        self.assertEqual(marketPrice0, 1.0)
        
        apool.setMarketPrice0(2.0)
        marketPrice0 = apool.getMarketPrice0()
        self.assertEqual(marketPrice0, 2.0)

        parameterA = apool.calculateParameterA() # A = x - y/p
        self.assertEqual(parameterA, 50.0)
        outputAmount = apool.swap(0,10) 
        self.assertEqual(outputAmount, 1000/60) # dy = - y * dx / (x + dx - A)
        reserve0 = apool.getReserve0()
        reserve1 = apool.getReserve1()
        self.assertEqual(reserve0, 110)
        self.assertEqual(reserve1, 100-(1000/60))

if __name__ == "__main__":
    unittest.main()