// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title Thukdam
 * @dev Protocol for post-mortem state preservation and consciousness anchoring.
 */
contract Thukdam {
    struct PreservedState {
        bytes32 stateHash;
        uint256 timestamp;
        bool isAnchored;
    }

    mapping(address => PreservedState) public states;

    event StatePreserved(address indexed entity, bytes32 stateHash);
    event StateAnchored(address indexed entity);

    function preserveState(bytes32 _stateHash) external {
        states[msg.sender] = PreservedState({
            stateHash: _stateHash,
            timestamp: block.timestamp,
            isAnchored: false
        });
        emit StatePreserved(msg.sender, _stateHash);
    }

    function anchorState() external {
        require(states[msg.sender].timestamp != 0, "No state to anchor");
        require(!states[msg.sender].isAnchored, "Already anchored");
        
        states[msg.sender].isAnchored = true;
        emit StateAnchored(msg.sender);
    }
}
