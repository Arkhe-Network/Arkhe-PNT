// SPDX-License-Identifier: AGPL-3.0
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "./RIOToken.sol";
import "./PatientRegistry.sol";

contract SubsidyManager is AccessControl, ReentrancyGuard {
    bytes32 public constant APPROVER_ROLE = keccak256("APPROVER_ROLE");

    RIOToken public rioToken;
    PatientRegistry public patientRegistry;

    struct SubsidyRequest {
        address patient;
        uint256 requestedAmount;
        uint256 approvedAmount;
        bool approved;
        bool disbursed;
        uint256 timestamp;
        string treatmentCenter;
    }

    mapping(uint256 => SubsidyRequest) public requests;
    uint256 public nextRequestId;

    event SubsidyRequested(uint256 indexed requestId, address patient, uint256 amount);
    event SubsidyApproved(uint256 indexed requestId, address approver, uint256 amount);
    event SubsidyDisbursed(uint256 indexed requestId, address patient, uint256 amount);

    constructor(address _rioToken, address _patientRegistry) {
        rioToken = RIOToken(_rioToken);
        patientRegistry = PatientRegistry(_patientRegistry);
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }

    function requestSubsidy(address patient, uint256 amount, string calldata treatmentCenter) external {
        require(patientRegistry.isEligible(patient), "Patient not eligible");
        require(!hasActiveRequest(patient), "Active request exists");
        uint256 requestId = nextRequestId++;
        requests[requestId] = SubsidyRequest({
            patient: patient,
            requestedAmount: amount,
            approvedAmount: 0,
            approved: false,
            disbursed: false,
            timestamp: block.timestamp,
            treatmentCenter: treatmentCenter
        });
        emit SubsidyRequested(requestId, patient, amount);
    }

    function approveSubsidy(uint256 requestId, uint256 approvedAmount) external onlyRole(APPROVER_ROLE) {
        SubsidyRequest storage req = requests[requestId];
        require(!req.approved, "Already approved");
        req.approved = true;
        req.approvedAmount = approvedAmount;
        emit SubsidyApproved(requestId, msg.sender, approvedAmount);
    }

    function disburse(uint256 requestId) external nonReentrant onlyRole(APPROVER_ROLE) {
        SubsidyRequest storage req = requests[requestId];
        require(req.approved, "Not approved");
        require(!req.disbursed, "Already disbursed");
        req.disbursed = true;
        rioToken.mint(req.patient, req.approvedAmount);
        emit SubsidyDisbursed(requestId, req.patient, req.approvedAmount);
    }

    function hasActiveRequest(address patient) public view returns (bool) {
        for (uint256 i = 0; i < nextRequestId; i++) {
            if (requests[i].patient == patient && !requests[i].disbursed) return true;
        }
        return false;
    }
}
