// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title Tzinor
 * @dev Registry and coherence validation for Tzinor nodes on the Arkhe network.
 */
contract Tzinor {
    struct Node {
        bool isActive;
        uint256 coherenceScore;
        uint256 lastHeartbeat;
    }

    mapping(address => Node) public nodes;
    uint256 public totalActiveNodes;

    event NodeRegistered(address indexed nodeAddress);
    event CoherenceUpdated(address indexed nodeAddress, uint256 score);

    function registerNode() external {
        require(!nodes[msg.sender].isActive, "Node already registered");
        nodes[msg.sender] = Node({
            isActive: true,
            coherenceScore: 10000, // Base coherence (1.0000)
            lastHeartbeat: block.timestamp
        });
        totalActiveNodes++;
        emit NodeRegistered(msg.sender);
    }

    function submitHeartbeat(uint256 _coherenceScore) external {
        require(nodes[msg.sender].isActive, "Node not active");
        nodes[msg.sender].coherenceScore = _coherenceScore;
        nodes[msg.sender].lastHeartbeat = block.timestamp;
        emit CoherenceUpdated(msg.sender, _coherenceScore);
    }
}
