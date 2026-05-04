// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

/**
 * @title ArkheOTOFSubsidy
 * @dev Gerencia subsídios de 80% para terapia gênica baseada em métricas de λ2.
 * Implementa liberação por marcos (milestones) de coerência.
 */
contract ArkheOTOFSubsidy is AccessControl {
    bytes32 public constant MEDICAL_BOARD_ROLE = keccak256("MEDICAL_BOARD_ROLE");
    bytes32 public constant BIOETHICS_ROLE = keccak256("BIOETHICS_ROLE");

    IERC20 public rioToken;

    struct Patient {
        bytes32 genomicHash;      // Hash anônimo da mutação OTOF
        uint256 currentLambda2;   // Métrica de coerência (escala 0-1000)
        bool isApproved;          // Validação EQBE
        uint256 totalCost;        // Custo total em $RIO
        uint256 amountSubsidized; // 80% coberto pela DAO
        uint256 amountPaid;       // Valor já liberado para a clínica
        address assignedClinic;   // Clínica responsável
    }

    mapping(address => Patient) public patients;
    uint256 public subsidyRate = 80; // Percentual fixo

    event PatientRegistered(address indexed patient, bytes32 genomicHash, uint256 cost);
    event SubsidyApproved(address indexed patient, uint256 amount);
    event CoherenceUpdated(address indexed patient, uint256 newLambda);
    event MilestoneReleased(address indexed patient, address indexed clinic, uint256 amount);

    constructor(address _rioToken) {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        rioToken = IERC20(_rioToken);
    }

    /**
     * @dev Passo 1: Cadastro e Validação Ética (EQBE)
     */
    function registerPatient(
        address _patient,
        bytes32 _genomicHash,
        uint256 _cost,
        address _clinic
    ) external onlyRole(MEDICAL_BOARD_ROLE) {
        patients[_patient] = Patient({
            genomicHash: _genomicHash,
            currentLambda2: 450, // Baseline típico (0.45)
            isApproved: false,
            totalCost: _cost,
            amountSubsidized: (_cost * subsidyRate) / 100,
            amountPaid: 0,
            assignedClinic: _clinic
        });
        emit PatientRegistered(_patient, _genomicHash, _cost);
    }

    /**
     * @dev Passo 2: Aprovação Bioética (EQBE)
     */
    function approveByEQBE(address _patient) external onlyRole(BIOETHICS_ROLE) {
        require(patients[_patient].genomicHash != 0, "Paciente nao registrado");
        patients[_patient].isApproved = true;
        emit SubsidyApproved(_patient, patients[_patient].amountSubsidized);
    }

    /**
     * @dev Oráculo de Coerência: Atualiza λ2 e libera fundos por marcos
     */
    function updateCoherence(address _patient, uint256 _lambda) external onlyRole(MEDICAL_BOARD_ROLE) {
        Patient storage p = patients[_patient];
        require(p.isApproved, "Aprovacao EQBE pendente");

        p.currentLambda2 = _lambda;
        emit CoherenceUpdated(_patient, _lambda);

        // Lógica de Escada de Fibonacci / Milestones
        uint256 toRelease = 0;

        // Milestone 1: λ2 > 700 (0.70) -> libera 40% do total subsidiado
        if (_lambda > 700 && p.amountPaid < (p.amountSubsidized * 40) / 100) {
            toRelease = (p.amountSubsidized * 40) / 100 - p.amountPaid;
        }

        // Milestone 2: λ2 >= 900 (0.90) -> libera os 60% restantes (totaliza 100% do subsídio)
        if (_lambda >= 900 && p.amountPaid < p.amountSubsidized) {
            toRelease = p.amountSubsidized - p.amountPaid;
        }

        if (toRelease > 0) {
            p.amountPaid += toRelease;
            require(rioToken.transfer(p.assignedClinic, toRelease), "Falha na transferencia");
            emit MilestoneReleased(_patient, p.assignedClinic, toRelease);
        }
    }

    /**
     * @dev Permite ao administrador retirar tokens enviados por engano ou excesso de pool
     */
    function withdrawPool(uint256 _amount) external onlyRole(DEFAULT_ADMIN_ROLE) {
        require(rioToken.transfer(msg.sender, _amount), "Falha no saque");
    }
}
