// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Escrow {
    address public buyer;
    address public seller;
    address public arbiter;
    uint public amount;
    uint public releaseTime;

    enum State { AWAITING_PAYMENT, AWAITING_DELIVERY, COMPLETE, REFUNDED }
    State public state;

    event PaymentDeposited(address indexed buyer, uint amount);
    event DeliveryConfirmed(address indexed buyer, address indexed seller, uint amount);
    event RefundIssued(address indexed arbiter, address indexed buyer, uint amount);

    constructor(address _seller, address _arbiter) {
        buyer = msg.sender;
        seller = _seller;
        arbiter = _arbiter;
        state = State.AWAITING_PAYMENT;
    }

    function deposit(uint durationInDays) external payable {
        require(msg.sender == buyer, "Only buyer can deposit");
        require(state == State.AWAITING_PAYMENT, "Already paid");
        require(msg.value > 0, "Deposit must be greater than 0");

        amount = msg.value;
        releaseTime = block.timestamp + (durationInDays * 1 days);
        state = State.AWAITING_DELIVERY;

        emit PaymentDeposited(msg.sender, msg.value);
    }

    function confirmDelivery() external {
        require(msg.sender == buyer, "Only buyer can confirm");
        require(state == State.AWAITING_DELIVERY, "Cannot confirm delivery");

        state = State.COMPLETE;
        payable(seller).transfer(amount);

        emit DeliveryConfirmed(buyer, seller, amount);
    }

    function refund() external {
        require(msg.sender == arbiter, "Only arbiter can refund");
        require(state == State.AWAITING_DELIVERY, "Cannot refund");

        state = State.REFUNDED;
        payable(buyer).transfer(amount);

        emit RefundIssued(arbiter, buyer, amount);
    }

    function timeLockRelease() external {
        require(msg.sender == seller, "Only seller can request time lock release");
        require(state == State.AWAITING_DELIVERY, "Not in delivery state");
        require(block.timestamp >= releaseTime, "Time lock not yet expired");

        state = State.COMPLETE;
        payable(seller).transfer(amount);

        emit DeliveryConfirmed(buyer, seller, amount);
    }
}
