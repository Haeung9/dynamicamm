import sys
import os
import unittest
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from AMM import pool

class CPMMPoolTest(unittest.TestCase):
    def test_swapWithoutFee(self):
        # test case 1
        apool = pool.CPMMPool(reserve0=100.0, reserve1=100.0, feeRate=0.0)
        outputAmount = apool.swap(0,10) # dy = - 100 * 10 / (100 + 10) = - 9.09090909 ...
        self.assertEqual(outputAmount, 1000/110)
        reserve0 = apool.getReserve0()
        reserve1 = apool.getReserve1()
        self.assertEqual(reserve0, 110)
        self.assertEqual(reserve1, 100-(1000/110))
        # test case 2
        apool = pool.CPMMPool(reserve0=100.0, reserve1=100.0, feeRate=0.0)
        outputAmount = apool.swap(1,10) # dx = - 100 * 10 / (100 + 10) = - 9.09090909 ...
        self.assertEqual(outputAmount, 1000/110)
        reserve0 = apool.getReserve0()
        reserve1 = apool.getReserve1()
        self.assertEqual(reserve0, 100-(1000/110))
        self.assertEqual(reserve1, 110)
    
    def test_swapWithFee(self):
        # feeInPool == False
        apool = pool.CPMMPool(reserve0=100.0, reserve1=100.0, feeRate=0.1)
        outputAmount = apool.swap(0,10) # dy = - 100 * 9 / (100 + 9) = - 8.2568
        self.assertEqual(outputAmount, 900/109)
        reserve0 = apool.getReserve0()
        reserve1 = apool.getReserve1()
        fee0 = apool.getFeeReserve0()
        fee1 = apool.getFeeReserve1()
        self.assertEqual(reserve0, 109)
        self.assertEqual(reserve1, 100-(900/109))
        self.assertEqual(fee0, 1.0)
        self.assertEqual(fee1, 0.0)
        # feeInPool == True
        apool = pool.CPMMPool(reserve0=100.0, reserve1=100.0, feeRate=0.1, feeInPool=True)
        outputAmount = apool.swap(0,10) # dy = - 100 * 9 / (100 + 9) = - 8.2568
        self.assertEqual(outputAmount, 900/109)
        reserve0 = apool.getReserve0()
        reserve1 = apool.getReserve1()
        fee0 = apool.getFeeReserve0()
        fee1 = apool.getFeeReserve1()
        self.assertEqual(reserve0, 110)
        self.assertEqual(reserve1, 100-(900/109))
        self.assertEqual(fee0, 1.0)
        self.assertEqual(fee1, 0.0)
    
if __name__ == "__main__":
    unittest.main()