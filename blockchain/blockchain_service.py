"""
Resume Truth Verification System - Blockchain Integration
Web3.py integration for Ethereum/Polygon smart contract interaction
"""

import logging
import os
from typing import Dict, Any, Optional
from web3 import Web3
from web3.contract import Contract
from eth_account import Account
from eth_account.messages import encode_defunct
from datetime import datetime
import json
from hashlib import sha256

logger = logging.getLogger(__name__)

# ===================== BLOCKCHAIN SERVICE =====================

class BlockchainService:
    """Main service for blockchain interactions"""
    
    def __init__(
        self,
        rpc_url: str,
        contract_address: str,
        contract_abi: str,
        private_key: str,
        network: str = "polygon"
    ):
        """
        Initialize blockchain service
        
        Args:
            rpc_url: RPC endpoint URL
            contract_address: Deployed smart contract address
            contract_abi: Contract ABI JSON/dict
            private_key: Private key for transactions
            network: Network name (ethereum, polygon, etc.)
        """
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.network = network
        
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        
        if not self.w3.is_connected():
            raise ConnectionError(f"Could not connect to {network} RPC: {rpc_url}")
        
        self.logger.info(f"Connected to {network} | Block: {self.w3.eth.block_number}")
        
        # Setup account
        self.account = Account.from_key(private_key)
        self.logger.info(f"Using account: {self.account.address}")
        
        # Load contract
        if isinstance(contract_abi, str):
            contract_abi = json.loads(contract_abi)
        
        self.contract: Contract = self.w3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=contract_abi
        )
        self.contract_address = contract_address
        
        self.logger.info(f"Contract loaded: {contract_address}")
    
    def get_balance(self) -> float:
        """Get account balance in ETH/MATIC"""
        balance_wei = self.w3.eth.get_balance(self.account.address)
        balance_ether = self.w3.from_wei(balance_wei, 'ether')
        return balance_ether
    
    def estimate_gas(self, function, *args, **kwargs) -> int:
        """Estimate gas cost for function call"""
        try:
            gas_estimate = function(*args, **kwargs).estimate_gas(
                {'from': self.account.address}
            )
            return gas_estimate
        except Exception as e:
            self.logger.error(f"Gas estimation error: {str(e)}")
            return 300000  # Default fallback
    
    def build_transaction(
        self,
        function,
        *args,
        gas_multiplier: float = 1.2,
        **kwargs
    ) -> Dict[str, Any]:
        """Build transaction for contract function call"""
        
        try:
            # Estimate gas
            gas_limit = int(self.estimate_gas(function, *args, **kwargs) * gas_multiplier)
            
            # Get gas price
            gas_price = self.w3.eth.gas_price
            
            # Build transaction
            tx = function(*args, **kwargs).build_transaction({
                'from': self.account.address,
                'gas': gas_limit,
                'gasPrice': gas_price,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
            })
            
            return tx
            
        except Exception as e:
            self.logger.error(f"Transaction building error: {str(e)}")
            raise
    
    def send_transaction(self, tx: Dict[str, Any]) -> str:
        """Sign and send transaction to blockchain"""
        
        try:
            # Sign transaction
            signed_tx = self.w3.eth.account.sign_transaction(tx, self.account.key)
            
            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            self.logger.info(f"Transaction sent: {tx_hash.hex()}")
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if receipt['status'] == 1:
                self.logger.info(f"Transaction confirmed: {tx_hash.hex()}")
                return tx_hash.hex()
            else:
                self.logger.error(f"Transaction failed: {tx_hash.hex()}")
                raise Exception(f"Transaction failed: {receipt}")
            
        except Exception as e:
            self.logger.error(f"Transaction sending error: {str(e)}")
            raise
    
    def call_function(self, function, *args, **kwargs) -> Any:
        """Call contract function (read-only)"""
        try:
            result = function(*args, **kwargs).call({'from': self.account.address})
            return result
        except Exception as e:
            self.logger.error(f"Contract call error: {str(e)}")
            raise
    
    # ===================== CLAIM MANAGEMENT =====================
    
    def register_claim(
        self,
        claim_hash: str,
        trust_score: int,
        claim_text: str,
        resume_hash: str
    ) -> str:
        """Register a verified claim on blockchain"""
        
        if not (0 <= trust_score <= 100):
            raise ValueError("Trust score must be 0-100")
        
        self.logger.info(f"Registering claim: {claim_hash[:16]}... (score: {trust_score})")
        
        try:
            # Prepare function call
            function = self.contract.functions.registerClaim(
                bytes.fromhex(claim_hash.replace('0x', '')),
                trust_score,
                claim_text,
                bytes.fromhex(resume_hash.replace('0x', ''))
            )
            
            # Build transaction
            tx = self.build_transaction(function)
            
            # Send transaction
            tx_hash = self.send_transaction(tx)
            
            return tx_hash
            
        except Exception as e:
            self.logger.error(f"Claim registration error: {str(e)}")
            raise
    
    def register_batch_claims(
        self,
        claim_hashes: list,
        trust_scores: list,
        claim_texts: list,
        resume_hash: str
    ) -> str:
        """Register multiple claims in single transaction"""
        
        if not (len(claim_hashes) == len(trust_scores) == len(claim_texts)):
            raise ValueError("Array lengths must match")
        
        self.logger.info(f"Registering {len(claim_hashes)} claims in batch")
        
        try:
            # Convert hashes
            claim_hashes_bytes = [
                bytes.fromhex(h.replace('0x', '')) for h in claim_hashes
            ]
            resume_hash_bytes = bytes.fromhex(resume_hash.replace('0x', ''))
            
            function = self.contract.functions.registerBatchClaims(
                claim_hashes_bytes,
                trust_scores,
                claim_texts,
                resume_hash_bytes
            )
            
            # Build and send
            tx = self.build_transaction(function)
            tx_hash = self.send_transaction(tx)
            
            return tx_hash
            
        except Exception as e:
            self.logger.error(f"Batch claim registration error: {str(e)}")
            raise
    
    def create_resume_record(
        self,
        resume_hash: str,
        total_claims: int,
        avg_trust_score: int,
        claim_hashes: list
    ) -> str:
        """Create resume verification record"""
        
        self.logger.info(f"Creating resume record: {resume_hash[:16]}...")
        
        try:
            claim_hashes_bytes = [
                bytes.fromhex(h.replace('0x', '')) for h in claim_hashes
            ]
            
            function = self.contract.functions.createResumeRecord(
                bytes.fromhex(resume_hash.replace('0x', '')),
                total_claims,
                avg_trust_score,
                claim_hashes_bytes
            )
            
            tx = self.build_transaction(function)
            tx_hash = self.send_transaction(tx)
            
            return tx_hash
            
        except Exception as e:
            self.logger.error(f"Resume record creation error: {str(e)}")
            raise
    
    # ===================== CLAIM VERIFICATION =====================
    
    def verify_claim(self, claim_hash: str) -> Dict[str, Any]:
        """Verify claim authenticity from blockchain"""
        
        try:
            is_valid, trust_score, verification_time = self.call_function(
                self.contract.functions.verifyClaim,
                bytes.fromhex(claim_hash.replace('0x', ''))
            )
            
            return {
                'is_valid': is_valid,
                'trust_score': trust_score,
                'verification_time': verification_time,
                'verified_at': datetime.fromtimestamp(verification_time).isoformat() if verification_time > 0 else None
            }
            
        except Exception as e:
            self.logger.error(f"Claim verification error: {str(e)}")
            raise
    
    def batch_verify_claims(self, claim_hashes: list) -> Dict[str, Any]:
        """Verify multiple claims"""
        
        try:
            claim_hashes_bytes = [
                bytes.fromhex(h.replace('0x', '')) for h in claim_hashes
            ]
            
            validities, scores = self.call_function(
                self.contract.functions.batchVerifyClaims,
                claim_hashes_bytes
            )
            
            results = []
            for i, claim_hash in enumerate(claim_hashes):
                results.append({
                    'claim_hash': claim_hash,
                    'is_valid': validities[i],
                    'trust_score': scores[i]
                })
            
            return {'results': results}
            
        except Exception as e:
            self.logger.error(f"Batch verification error: {str(e)}")
            raise
    
    def get_claim_details(self, claim_hash: str) -> Dict[str, Any]:
        """Get full claim details"""
        
        try:
            claim = self.call_function(
                self.contract.functions.getClaim,
                bytes.fromhex(claim_hash.replace('0x', ''))
            )
            
            return {
                'claim_hash': claim_hash,
                'verifier': claim[1],
                'timestamp': claim[2],
                'trust_score': claim[3],
                'is_valid': claim[4],
                'claim_text': claim[5],
                'verification_count': claim[6],
                'verified_at': datetime.fromtimestamp(claim[2]).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Get claim details error: {str(e)}")
            raise
    
    def get_resume_record(self, resume_hash: str) -> Dict[str, Any]:
        """Get resume verification record"""
        
        try:
            record = self.call_function(
                self.contract.functions.getResumeRecord,
                bytes.fromhex(resume_hash.replace('0x', ''))
            )
            
            return {
                'resume_hash': resume_hash,
                'owner': record[1],
                'created_at': datetime.fromtimestamp(record[2]).isoformat(),
                'total_claims': record[3],
                'avg_trust_score': record[4],
                'is_visible': record[6]
            }
            
        except Exception as e:
            self.logger.error(f"Get resume record error: {str(e)}")
            raise
    
    def invalidate_claim(self, claim_hash: str) -> str:
        """Invalidate a claim"""
        
        self.logger.info(f"Invalidating claim: {claim_hash[:16]}...")
        
        try:
            function = self.contract.functions.invalidateClaim(
                bytes.fromhex(claim_hash.replace('0x', ''))
            )
            
            tx = self.build_transaction(function)
            tx_hash = self.send_transaction(tx)
            
            return tx_hash
            
        except Exception as e:
            self.logger.error(f"Claim invalidation error: {str(e)}")
            raise
    
    # ===================== STATISTICS =====================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics from blockchain"""
        
        try:
            total_claims = self.call_function(
                self.contract.functions.getTotalClaimsVerified
            )
            total_resumes = self.call_function(
                self.contract.functions.getTotalResumesSubmitted
            )
            avg_score = self.call_function(
                self.contract.functions.getAverageTrustScore
            )
            
            return {
                'total_claims_verified': total_claims,
                'total_resumes_submitted': total_resumes,
                'average_trust_score': avg_score,
                'network': self.network,
                'contract_address': self.contract_address
            }
            
        except Exception as e:
            self.logger.error(f"Get statistics error: {str(e)}")
            raise
    
    # ===================== UTILITY FUNCTIONS =====================
    
    @staticmethod
    def create_claim_hash(claim_text: str, resume_id: str, timestamp: int) -> str:
        """Create hash for a claim"""
        data = f"{claim_text}:{resume_id}:{timestamp}".encode()
        return "0x" + sha256(data).hexdigest()
    
    @staticmethod
    def create_resume_hash(resume_content: str) -> str:
        """Create hash for entire resume"""
        data = resume_content.encode()
        return "0x" + sha256(data).hexdigest()
    
    def get_transaction_receipt(self, tx_hash: str) -> Dict[str, Any]:
        """Get transaction receipt details"""
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            
            return {
                'transaction_hash': tx_hash,
                'block_number': receipt['blockNumber'],
                'gas_used': receipt['gasUsed'],
                'status': 'success' if receipt['status'] == 1 else 'failed',
                'from': receipt['from'],
                'to': receipt['to']
            }
        except Exception as e:
            self.logger.error(f"Get receipt error: {str(e)}")
            raise

# ===================== BLOCKCHAIN SERVICE FACTORY =====================

class BlockchainServiceFactory:
    """Factory for creating blockchain services"""
    
    _services = {}
    
    @classmethod
    def create_service(
        cls,
        network: str = "polygon",
        rpc_url: str = None,
        contract_address: str = None,
        contract_abi: str = None,
        private_key: str = None
    ) -> BlockchainService:
        """Create or retrieve blockchain service"""
        
        # Use environment variables as defaults
        rpc_url = rpc_url or os.getenv('ETH_RPC_URL', 'https://polygon-rpc.com')
        contract_address = contract_address or os.getenv('SMART_CONTRACT_ADDRESS')
        private_key = private_key or os.getenv('PRIVATE_KEY')
        
        if not contract_abi:
            # Load from file or use environment variable
            abi_str = os.getenv('CONTRACT_ABI', '{}')
            contract_abi = abi_str
        
        if network not in cls._services:
            cls._services[network] = BlockchainService(
                rpc_url=rpc_url,
                contract_address=contract_address,
                contract_abi=contract_abi,
                private_key=private_key,
                network=network
            )
        
        return cls._services[network]

# ===================== EXAMPLE USAGE =====================

if __name__ == "__main__":
    
    logging.basicConfig(level=logging.INFO)
    
    # Initialize blockchain service
    # service = BlockchainServiceFactory.create_service(network="polygon")
    
    # Get balance
    # balance = service.get_balance()
    # print(f"Account balance: {balance} MATIC")
    
    # Create hashes
    # claim_hash = BlockchainService.create_claim_hash("Python", "resume-123", 1672531200)
    # resume_hash = BlockchainService.create_resume_hash("John Doe Resume Content")
    
    # Register claim
    # tx_hash = service.register_claim(
    #     claim_hash=claim_hash,
    #     trust_score=85,
    #     claim_text="Python",
    #     resume_hash=resume_hash
    # )
    # print(f"Claim registered: {tx_hash}")
    
    # Verify claim
    # verification = service.verify_claim(claim_hash)
    # print(f"Verification result: {verification}")
    
    # Get statistics
    # stats = service.get_statistics()
    # print(f"Statistics: {stats}")
    
    pass
