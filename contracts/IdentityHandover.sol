// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title IdentityHandover
 * @dev Contrato para transferência de identidade soberana, stake e reputação entre nós QD.
 * Requer quórum do Conselho MuSig2 para finalização.
 */
contract IdentityHandover {
    struct Node {
        bytes32 nodeId;
        address owner;
        uint256 stake;
        uint256 reputation;
        bool isActive;
    }

    mapping(bytes32 => Node) public nodes;
    address public council;

    event IdentityTransferred(bytes32 indexed oldNodeId, bytes32 indexed newNodeId, uint256 stake);

    modifier onlyCouncil() {
        require(msg.sender == council, "Apenas o Conselho pode autorizar handovers.");
        _;
    }

    constructor(address _council) {
        council = _council;
    }

    /**
     * @dev Executa o handover de um nó antigo para um novo nó substituto.
     * @param oldNodeId ID do nó que está saindo.
     * @param newNodeId ID do nó substituto (previamente validado por ZK-Health).
     */
    function handoverIdentity(
        bytes32 oldNodeId,
        bytes32 newNodeId
    ) external onlyCouncil {
        require(nodes[oldNodeId].isActive, "No antigo nao esta ativo.");
        require(!nodes[newNodeId].isActive, "No novo ja esta ativo.");

        Node storage oldNode = nodes[oldNodeId];
        Node storage newNode = nodes[newNodeId];

        // Transferência de ativos e reputação
        uint256 stakeToTransfer = oldNode.stake;
        newNode.stake = stakeToTransfer;
        newNode.reputation = oldNode.reputation;
        newNode.isActive = true;

        // Desativação do nó antigo
        oldNode.isActive = false;
        oldNode.stake = 0;
        oldNode.reputation = 0;

        emit IdentityTransferred(oldNodeId, newNodeId, stakeToTransfer);
    }
}
