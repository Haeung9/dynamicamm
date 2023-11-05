from . import pool

class DCPMMwithOutdated(pool.DCPMMPool):
    def __init__(self, reserve0 = 0.0, reserve1 =0.0, feeRate = 0.003, lastMarketPrice = 1.0, lastBlockNumberStamp = 0, feeInPool = False):
        super().__init__(reserve0, reserve1, feeRate, lastMarketPrice, feeInPool)
        self.lastBlockNumberStamp = lastBlockNumberStamp
        self.currentBlockNumber = 0
        self.allowableOutdate = 10
        self.slippageTolerance = 0.005
    
    def verifySign(self, marketPrice, blockNumberStamp, signature) -> bool:
        # TODO: verify signature and return True / False use ECDSA
        # EXAMPLE (use Ethereum default signature system):
        # 
        # 1. DataFeed part (signing)
        # ``` javascript
        # operatorAddress = '0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        # message = web3.eth.abi.encodeParameters(['uint', 'uint'], [marketPrice, blockNumberStamp])
        # signature = await web3.eth.accounts.sign(message, operatorPrivateKey)
        # ```
        # 
        # 2. SC part (verifying)
        # ``` solidity
        # pragma solidity ^0.8;
        # import "https://github.com/OpenZeppelin/openzeppelin-contracts/blob/master/contracts/utils/cryptography/ECDSA.sol";
        # contract MyContract {
        #     address public operatorAddress = '0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa';
        #     function verifySign(uint marketPrice, uint blockNumberStamp, ECDSA.Signature signature) external pure returns (bool) {
        #         byte messageHash = keccak256(abi.encode(marketPrice, blockNumberStamp));
        #         require(messageHash == signature.messageHash, 'message mismatch');
        #         address accountRecovered = ECDSA.recover(signature.messageHash, signature.v, signature.r, signature.s);
        #         require(accountRecovered == operatorAddress, 'sign mismatch');
        #         return true;
        #     }
        # }
        # ```
        return True
    
    def latestCheck(self, blockNumberStamp) -> bool:
        return blockNumberStamp > self.lastBlockNumberStamp
    def allowableOutdateCheck(self, blockNumberStamp) -> bool:
        return (blockNumberStamp > (self.currentBlockNumber - self.allowableOutdate))
    def slippageCheck(self, inputAssetId, inputAmount, marketPrice) -> bool:
        effectiveInputAmount = inputAmount * (1.0 - self.feeRate)
        actual = self.calculateOutputAmount(inputAssetId, effectiveInputAmount)

        temp = self.marketPrice
        self.marketPrice = marketPrice
        expected = self.calculateOutputAmount(inputAssetId, effectiveInputAmount) # TODO: def calculateOutputAmountWithPrice(inputAssetId, inputAmount, price)
        self.marketPrice = temp

        return ((expected - actual) / actual  <= self.slippageTolerance) # NOTE: always True if actual > expected
    def setMarketPrice0(self, newMarketPrice):
        return super().setMarketPrice0(newMarketPrice)
    # NOTE: always use with try-except
    # NOTE: call after update self.currentBlockNumber
    # TODO: check self.swap(inputAssetId, inputAmount) works or not. Must not work
    def swap(self, inputAssetId, inputAmount, marketPrice, blockNumberStamp, signature):
        if not self.verifySign(marketPrice, blockNumberStamp, signature):
            raise Exception('invalid signature') # revert
        if not self.allowableOutdateCheck(blockNumberStamp):
            raise Exception('expired input') # revert
        
        # trade with input marketPrice when self.latestCheck(blockNumberStamp) == True
        # trade with self.marketPrice when self.latestCheck(blockNumberStamp) == False
        if self.latestCheck(blockNumberStamp):
            self.lastBlockNumberStamp = blockNumberStamp
            self.marketPrice = marketPrice

        if not self.slippageCheck(inputAssetId, inputAmount, marketPrice):
            raise Exception('too high slipage') # revert
        return super().swap(inputAssetId, inputAmount) 

        
