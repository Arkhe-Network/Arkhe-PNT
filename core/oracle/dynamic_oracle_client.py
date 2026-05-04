# dynamic_oracle_client.py — Cliente Python para governança de oráculos
from web3 import Web3
from eth_account import Account
from typing import Dict, List, Optional
import json
import time

class DynamicOracleClient:
    """Cliente para interagir com DynamicOracleGovernance."""

    def __init__(
        self,
        rpc_url: str,
        contract_address: str,
        validator_private_key: str,
        chain_id: int = 1337
    ):
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        self.account = Account.from_key(validator_private_key)
        self.contract = self.w3.eth.contract(
            address=contract_address,
            abi=self._load_abi()
        )
        self.chain_id = chain_id

    def _load_abi(self) -> list:
        """ABI mínima para interações principais."""
        return [
            {
                "inputs": [
                    {"name": "oracleId", "type": "string"},
                    {"name": "resourceType", "type": "string"},
                    {"name": "oracleAddress", "type": "address"},
                    {"name": "stakeAmount", "type": "uint256"}
                ],
                "name": "proposeOracle",
                "outputs": [{"name": "", "type": "bytes32"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [
                    {"name": "proposalId", "type": "bytes32"},
                    {"name": "support", "type": "bool"}
                ],
                "name": "vote",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"name": "proposalId", "type": "bytes32"}],
                "name": "executeProposal",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"name": "resourceType", "type": "string"}],
                "name": "getActiveOracles",
                "outputs": [
                    {"name": "oracleIds", "type": "string[]"},
                    {"name": "confidences", "type": "uint256[]"}
                ],
                "stateMutability": "view",
                "type": "function"
            }
        ]

    def propose_oracle(
        self,
        oracle_id: str,
        resource_type: str,
        oracle_address: str,
        stake_amount_wei: int = 10**18  # 1 ETH
    ) -> str:
        """Propõe novo oráculo."""
        tx = self.contract.functions.proposeOracle(
            oracle_id, resource_type, oracle_address, stake_amount_wei
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'chainId': self.chain_id,
            'gas': 300000
        })

        signed = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        # Extrair proposalId do log de evento
        proposal_id = receipt['logs'][0]['topics'][1] if receipt['logs'] else None
        return proposal_id.hex() if proposal_id else tx_hash.hex()

    def vote_on_proposal(self, proposal_id: str, support: bool) -> str:
        """Vota em proposta."""
        tx = self.contract.functions.vote(
            bytes.fromhex(proposal_id), support
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'chainId': self.chain_id,
            'gas': 150000
        })

        signed = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        return tx_hash.hex()

    def execute_proposal(self, proposal_id: str) -> Dict:
        """Executa proposta após fim da votação."""
        tx = self.contract.functions.executeProposal(
            bytes.fromhex(proposal_id)
        ).build_transaction({
            'from': self.account.address,
            'nonce': self.w3.eth.get_transaction_count(self.account.address),
            'chainId': self.chain_id,
            'gas': 200000
        })

        signed = self.account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        return {
            'tx_hash': tx_hash.hex(),
            'status': 'success' if receipt['status'] == 1 else 'failed',
            'gas_used': receipt['gasUsed']
        }

    def get_active_oracles(self, resource_type: str) -> Dict[str, float]:
        """Consulta oráculos ativos e suas confianças."""
        oracle_ids, confidences = self.contract.functions.getActiveOracles(
            resource_type
        ).call()

        return {
            oracle_id: confidence / 1e18  # converter de fixed-point
            for oracle_id, confidence in zip(oracle_ids, confidences)
        }
