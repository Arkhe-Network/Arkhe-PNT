// SPDX-License-Identifier: AGPL-3.0
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/AccessControl.sol";

contract PatientRegistry is AccessControl {
    bytes32 public constant DOCTOR_ROLE = keccak256("DOCTOR_ROLE");
    bytes32 public constant EQBE_ROLE = keccak256("EQBE_ROLE");

    struct PatientRecord {
        bytes32 geneticHash;    // hash(genomic data + salt) – anônimo
        uint8 age;
        bool otofMutationConfirmed;
        bool consentGiven;
        uint256 enrollmentTimestamp;
        address wallet;         // carteira do paciente (ou tutor)
        string metadataURI;     // IPFS URI com dados clínicos off-chain
    }

    mapping(address => PatientRecord) public patients;
    mapping(bytes32 => address) public geneticHashToAddress;

    event PatientEnrolled(address indexed patient, bytes32 geneticHash);
    event ConsentUpdated(address indexed patient, bool consent);

    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
    }

    function enrollPatient(
        bytes32 geneticHash,
        uint8 age,
        bool otofMutationConfirmed,
        address wallet,
        string calldata metadataURI
    ) external onlyRole(DOCTOR_ROLE) {
        require(geneticHashToAddress[geneticHash] == address(0), "Patient already enrolled");
        PatientRecord storage p = patients[wallet];
        p.geneticHash = geneticHash;
        p.age = age;
        p.otofMutationConfirmed = otofMutationConfirmed;
        p.wallet = wallet;
        p.metadataURI = metadataURI;
        p.enrollmentTimestamp = block.timestamp;
        geneticHashToAddress[geneticHash] = wallet;
        emit PatientEnrolled(wallet, geneticHash);
    }

    function updateConsent(address patient, bool consent) external onlyRole(EQBE_ROLE) {
        patients[patient].consentGiven = consent;
        emit ConsentUpdated(patient, consent);
    }

    function isEligible(address patient) external view returns (bool) {
        PatientRecord memory p = patients[patient];
        return p.otofMutationConfirmed && p.consentGiven && p.age <= 18;
    }
}
