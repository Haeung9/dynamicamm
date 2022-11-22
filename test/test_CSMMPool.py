import unittest
from AMM import pool

class CSMMPoolTest(unittest.TestCase):
    def test_swapWithoutFee(self):
        # test case 1: __initialPrice0 = 1.0
        apool = pool.WCSMMPool(reserve0=100.0, reserve1=100.0, feeRate=0.0) 
        parameterA = apool.calculateParameterK() # K = x + y = 200
        self.assertEqual(parameterA, 200.0)
        outputAmount = apool.swap(0,10) # dy = - dx
        self.assertEqual(outputAmount, 10)
        reserve0 = apool.getReserve0()
        reserve1 = apool.getReserve1()
        self.assertEqual(reserve0, 110)
        self.assertEqual(reserve1, 90)
        # test case 2: 0 -> 1 swap, __initialPrice0 = 2.0
        apool = pool.WCSMMPool(reserve0=50.0, reserve1=100.0, feeRate=0.0) 
        parameterA = apool.calculateParameterK() # K = p*x + y = 200
        self.assertEqual(parameterA, 200.0)
        outputAmount = apool.swap(0,10) # dy = - p * dx
        self.assertEqual(outputAmount, 20)
        reserve0 = apool.getReserve0()
        reserve1 = apool.getReserve1()
        self.assertEqual(reserve0, 60)
        self.assertEqual(reserve1, 80)
        # test case 3: 1 -> 0 swap, __initialPrice0 = 2.0
        apool = pool.WCSMMPool(reserve0=50.0, reserve1=100.0, feeRate=0.0) 
        parameterA = apool.calculateParameterK() # K = p*x + y = 200
        self.assertEqual(parameterA, 200.0)
        outputAmount = apool.swap(1,10) # dx = - dy / p
        self.assertEqual(outputAmount, 5)
        reserve0 = apool.getReserve0()
        reserve1 = apool.getReserve1()
        self.assertEqual(reserve0, 45)
        self.assertEqual(reserve1, 110)

    def test_swapWithFee_feeOutOfPool(self):
        # test case 1: __initialPrice0 = 1.0
        apool = pool.WCSMMPool(reserve0=100.0, reserve1=100.0, feeRate=0.1) 
        parameterA = apool.calculateParameterK() # K = x + y = 200
        self.assertEqual(parameterA, 200.0)
        outputAmount = apool.swap(0,10) # dy = - dx
        self.assertEqual(outputAmount, 9)
        reserve0 = apool.getReserve0()
        reserve1 = apool.getReserve1()
        self.assertEqual(reserve0, 109)
        self.assertEqual(reserve1, 91)
        fee0 = apool.getFeeReserve0()
        fee1 = apool.getFeeReserve1()
        self.assertEqual(fee0, 1.0)
        self.assertEqual(fee1, 0.0)
        # test case 2: 0 -> 1 swap, __initialPrice0 = 2.0
        apool = pool.WCSMMPool(reserve0=50.0, reserve1=100.0, feeRate=0.1) 
        parameterA = apool.calculateParameterK() # K = p*x + y = 200
        self.assertEqual(parameterA, 200.0)
        outputAmount = apool.swap(0,10) # dy = - p * dx
        self.assertEqual(outputAmount, 18)
        reserve0 = apool.getReserve0()
        reserve1 = apool.getReserve1()
        self.assertEqual(reserve0, 59)
        self.assertEqual(reserve1, 82)
        fee0 = apool.getFeeReserve0()
        fee1 = apool.getFeeReserve1()
        self.assertEqual(fee0, 1.0)
        self.assertEqual(fee1, 0.0)
        # test case 3: 1 -> 0 swap, __initialPrice0 = 2.0
        apool = pool.WCSMMPool(reserve0=50.0, reserve1=100.0, feeRate=0.1) 
        parameterA = apool.calculateParameterK() # K = p*x + y = 200
        self.assertEqual(parameterA, 200.0)
        outputAmount = apool.swap(1,10) # dx = - dy / p
        self.assertEqual(outputAmount, 4.5)
        reserve0 = apool.getReserve0()
        reserve1 = apool.getReserve1()
        self.assertEqual(reserve0, 45.5)
        self.assertEqual(reserve1, 109)
        fee0 = apool.getFeeReserve0()
        fee1 = apool.getFeeReserve1()
        self.assertEqual(fee0, 0.0)
        self.assertEqual(fee1, 1.0)
    
    def test_swapWithFee_feeInPool(self):
        # test case 1: __initialPrice0 = 1.0
        apool = pool.WCSMMPool(reserve0=100.0, reserve1=100.0, feeRate=0.1, feeInPool=True) 
        parameterA = apool.calculateParameterK() # K = x + y = 200
        self.assertEqual(parameterA, 200.0)
        outputAmount = apool.swap(0,10) # dy = - dx
        self.assertEqual(outputAmount, 9)
        reserve0 = apool.getReserve0()
        reserve1 = apool.getReserve1()
        self.assertEqual(reserve0, 110)
        self.assertEqual(reserve1, 91)
        fee0 = apool.getFeeReserve0()
        fee1 = apool.getFeeReserve1()
        self.assertEqual(fee0, 1.0)
        self.assertEqual(fee1, 0.0)
        # test case 2: 0 -> 1 swap, __initialPrice0 = 2.0
        apool = pool.WCSMMPool(reserve0=50.0, reserve1=100.0, feeRate=0.1, feeInPool=True) 
        parameterA = apool.calculateParameterK() # K = p*x + y = 200
        self.assertEqual(parameterA, 200.0)
        outputAmount = apool.swap(0,10) # dy = - p * dx
        self.assertEqual(outputAmount, 18)
        reserve0 = apool.getReserve0()
        reserve1 = apool.getReserve1()
        self.assertEqual(reserve0, 60)
        self.assertEqual(reserve1, 82)
        fee0 = apool.getFeeReserve0()
        fee1 = apool.getFeeReserve1()
        self.assertEqual(fee0, 1.0)
        self.assertEqual(fee1, 0.0)
        # test case 3: 1 -> 0 swap, __initialPrice0 = 2.0
        apool = pool.WCSMMPool(reserve0=50.0, reserve1=100.0, feeRate=0.1, feeInPool=True) 
        parameterA = apool.calculateParameterK() # K = p*x + y = 200
        self.assertEqual(parameterA, 200.0)
        outputAmount = apool.swap(1,10) # dx = - dy / p
        self.assertEqual(outputAmount, 4.5)
        reserve0 = apool.getReserve0()
        reserve1 = apool.getReserve1()
        self.assertEqual(reserve0, 45.5)
        self.assertEqual(reserve1, 110)
        fee0 = apool.getFeeReserve0()
        fee1 = apool.getFeeReserve1()
        self.assertEqual(fee0, 0.0)
        self.assertEqual(fee1, 1.0)
    
    def test_toLargeSwap_withoutFee(self):
        # test case 1: impossible swap
        apool = pool.WCSMMPool(reserve0=100.0, reserve1=100.0, feeRate=0.0)
        with self.assertRaisesRegex(Exception, "Swap size is too large"):
            apool.swap(1,101)
    
    def test_toLargeSwap_withFee(self):
        # test case 1: bearable swap
        apool = pool.WCSMMPool(reserve0=100.0, reserve1=100.0, feeRate=0.1)
        outputAmount = apool.swap(0,110)
        self.assertEqual(outputAmount, 99.0)
        reserve0 = apool.getReserve0()
        reserve1 = apool.getReserve1()
        self.assertEqual(reserve0, 199.0)
        self.assertEqual(reserve1, 1.0)

        # test case 2: impossible swap
        apool = pool.WCSMMPool(reserve0=100.0, reserve1=100.0, feeRate=0.1)
        with self.assertRaisesRegex(Exception, "Swap size is too large"):
            apool.swap(0,120)
        reserve0 = apool.getReserve0()
        reserve1 = apool.getReserve1()
        self.assertEqual(reserve0, 100.0)
        self.assertEqual(reserve1, 100.0)
        fee0 = apool.getFeeReserve0()
        fee1 = apool.getFeeReserve1()
        self.assertEqual(fee0, 0.0)
        self.assertEqual(fee1, 0.0)
        
