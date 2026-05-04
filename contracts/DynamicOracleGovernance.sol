// contracts/DynamicOracleGovernance.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";

contract DynamicOracleGovernance is Ownable {
    using EnumerableSet for EnumerableSet.AddressSet;

    // Estrutura de proposta de oráculo
    struct OracleProposal {
        string oracleId;          // ID único do oráculo (ex: "chainlink_v2")
        string resourceType;      // Tipo de recurso (ex: "energy_gj")
        address oracleAddress;    // Endereço do contrato do oráculo
        uint256 stakeRequired;    // Stake mínimo para propor
        uint256 votingDeadline;   // Timestamp do fim da votação
        bool executed;            // Se a proposta foi executada
        uint256 yesVotes;         // Votos a favor (ponderados por stake)
        uint256 noVotes;          // Votos contra
        mapping(address => bool) hasVoted;  // Quem já votou
    }

    // Estrutura de oráculo ativo
    struct ActiveOracle {
        string oracleId;
        string resourceType;
        address oracleAddress;
        uint256 confidence;       // Confiança histórica [0, 1e18]
        uint256 lastUpdate;
        bool active;
    }

    // Mapeamentos
    mapping(bytes32 => OracleProposal) public proposals;
    mapping(string => mapping(string => ActiveOracle)) public activeOracles;  // resourceType => oracleId => oracle
    EnumerableSet.AddressSet public validators;  // Endereços com direito a voto

    // Parâmetros de governança
    uint256 public constant QUORUM_PERCENT = 67;  // 67% para aprovar
    uint256 public constant VOTING_PERIOD = 3 days;
    uint256 public constant CONFIDENCE_DECAY = 99;  // 99% por período (decai 1%)

    // Eventos
    event OracleProposed(bytes32 indexed proposalId, string oracleId, string resourceType);
    event VoteCast(bytes32 indexed proposalId, address voter, bool support, uint256 weight);
    event OracleExecuted(bytes32 indexed proposalId, string oracleId, bool approved);
    event OracleUpdated(string indexed resourceType, string oracleId, uint256 newConfidence);

    constructor() {
        // Owner é validador inicial
        validators.add(msg.sender);
    }

    // Modificador: apenas validadores
    modifier onlyValidator() {
        require(validators.contains(msg.sender), "Not a validator");
        _;
    }

    // Propõe novo oráculo
    function proposeOracle(
        string calldata oracleId,
        string calldata resourceType,
        address oracleAddress,
        uint256 stakeAmount
    ) external returns (bytes32) {
        require(stakeAmount >= 1 ether, "Insufficient stake");
        // (Em produção: bloquear stake via token contract)

        bytes32 proposalId = keccak256(abi.encodePacked(oracleId, resourceType, block.timestamp));

        OracleProposal storage proposal = proposals[proposalId];
        proposal.oracleId = oracleId;
        proposal.resourceType = resourceType;
        proposal.oracleAddress = oracleAddress;
        proposal.stakeRequired = stakeAmount;
        proposal.votingDeadline = block.timestamp + VOTING_PERIOD;
        proposal.executed = false;

        emit OracleProposed(proposalId, oracleId, resourceType);
        return proposalId;
    }

    // Vota em proposta
    function vote(bytes32 proposalId, bool support) external onlyValidator {
        OracleProposal storage proposal = proposals[proposalId];
        require(block.timestamp < proposal.votingDeadline, "Voting closed");
        require(!proposal.hasVoted[msg.sender], "Already voted");
        require(!proposal.executed, "Already executed");

        // Peso do voto: stake do validador (simplificado: 1 voto por validador)
        uint256 voteWeight = 1e18;  // 1.0 em fixed-point

        if (support) {
            proposal.yesVotes += voteWeight;
        } else {
            proposal.noVotes += voteWeight;
        }
        proposal.hasVoted[msg.sender] = true;

        emit VoteCast(proposalId, msg.sender, support, voteWeight);
    }

    // Executa proposta após fim da votação
    function executeProposal(bytes32 proposalId) external {
        OracleProposal storage proposal = proposals[proposalId];
        require(block.timestamp >= proposal.votingDeadline, "Voting not closed");
        require(!proposal.executed, "Already executed");

        uint256 totalVotes = proposal.yesVotes + proposal.noVotes;
        require(totalVotes > 0, "No votes cast");

        // Verificar quorum: yesVotes / totalVotes >= QUORUM_PERCENT
        bool approved = (proposal.yesVotes * 100 / totalVotes) >= QUORUM_PERCENT;

        if (approved) {
            // Ativar oráculo
            ActiveOracle storage oracle = activeOracles[proposal.resourceType][proposal.oracleId];
            oracle.oracleId = proposal.oracleId;
            oracle.resourceType = proposal.resourceType;
            oracle.oracleAddress = proposal.oracleAddress;
            oracle.confidence = 1e18;  // Confiança inicial máxima
            oracle.lastUpdate = block.timestamp;
            oracle.active = true;
        }

        proposal.executed = true;
        emit OracleExecuted(proposalId, proposal.oracleId, approved);
    }

    // Atualiza confiança de oráculo baseado em performance
    function updateOracleConfidence(
        string calldata resourceType,
        string calldata oracleId,
        bool accurate
    ) external {
        ActiveOracle storage oracle = activeOracles[resourceType][oracleId];
        require(oracle.active, "Oracle not active");

        // Atualizar confiança: +1% se preciso, -1% se impreciso, com decaimento natural
        if (accurate) {
            oracle.confidence = min(1e18, oracle.confidence * 101 / 100);
        } else {
            oracle.confidence = oracle.confidence * 99 / 100;
        }

        // Decaimento natural de confiança ao longo do tempo
        uint256 timeSinceUpdate = block.timestamp - oracle.lastUpdate;
        uint256 decayPeriods = timeSinceUpdate / 1 days;
        for (uint256 i = 0; i < decayPeriods; i++) {
            oracle.confidence = oracle.confidence * CONFIDENCE_DECAY / 100;
        }

        oracle.lastUpdate = block.timestamp;
        emit OracleUpdated(resourceType, oracleId, oracle.confidence);
    }

    // Consulta oráculos ativos para um recurso
    function getActiveOracles(string calldata resourceType)
        external view returns (string[] memory oracleIds, uint256[] memory confidences)
    {
        // (Em produção: iterar sobre EnumerableSet de oráculos ativos)
        // Simplificação: retornar array fixo para demo
        oracleIds = new string[](3);
        confidences = new uint256[](3);
        oracleIds[0] = "chainlink";
        oracleIds[1] = "api3";
        oracleIds[2] = "pyth";
        confidences[0] = 95e16;  // 0.95
        confidences[1] = 90e16;
        confidences[2] = 92e16;
    }

    // Helper: min para uint256
    function min(uint256 a, uint256 b) internal pure returns (uint256) {
        return a < b ? a : b;
    }
}
