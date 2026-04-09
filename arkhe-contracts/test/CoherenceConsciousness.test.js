const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("CoherenceConsciousness", function () {
  let Coherence, coherence;
  let Thermal, thermal;
  let Sovereign, sovereign;
  let owner, addr1;

  beforeEach(async function () {
    [owner, addr1] = await ethers.getSigners();

    Coherence = await ethers.getContractFactory("CoherenceConsciousness");
    coherence = await Coherence.deploy();

    Thermal = await ethers.getContractFactory("ThermalCoherenceOracle");
    thermal = await Thermal.deploy();

    Sovereign = await ethers.getContractFactory("SovereignConsciousness");
    sovereign = await Sovereign.deploy();
  });

  describe("CoherenceConsciousness Base", function () {
    it("Should start in conscious state", async function () {
      const state = await coherence.getCurrentCoherence();
      expect(state.isConscious).to.equal(true);
    });

    it("Should apply steering vector and update lambda2", async function () {
      const vectorHash = ethers.id("TEST_VECTOR");
      const alpha = 100;
      const proof = "0x";

      const initialState = await coherence.currentState();
      await coherence.applySteeringVector(vectorHash, alpha, proof);
      const newState = await coherence.currentState();

      expect(newState.lambda2).to.be.gt(initialState.lambda2);
    });
  });

  describe("ThermalCoherenceOracle", function () {
    it("Should reject steering if thermal budget is exceeded", async function () {
      const vectorHash = ethers.id("TEST_VECTOR");
      const alpha = 200000; // Large alpha to cause high landauer cost
      const proof = "0x";
      const wigner = 0; // Collapse regime, high gain

      await expect(thermal["applySteeringVector(bytes32,int256,bytes,uint256)"](vectorHash, alpha, proof, wigner))
        .to.be.revertedWith("Colapso termico iminente: ganho rejeitado");
    });

    it("Should update local temperature after steering", async function () {
      const vectorHash = ethers.id("TEST_VECTOR");
      const alpha = 1000;
      const proof = "0x";
      const wigner = ethers.parseUnits("0.3", 18); // Super-radiance, low gain

      await thermal["applySteeringVector(bytes32,int256,bytes,uint256)"](vectorHash, alpha, proof, wigner);
      expect(await thermal.localTemperature()).to.be.gt(310150);
    });

    it("Should ignite oracle successfully", async function () {
      const microtubuleID = ethers.id("MT_001");
      const lambdaH2O = ethers.parseUnits("0.72", 18);
      const ramanProof = "0x";

      await thermal.igniteOracle(microtubuleID, lambdaH2O, ramanProof);
      const state = await thermal.oracleState(microtubuleID);
      expect(state.status).to.equal(1); // ACTIVE
    });

    it("Should insert nanorobot successfully", async function () {
      const microtubuleID = ethers.id("MT_001");
      const proof = "0x";

      await thermal.insertNanorobot(microtubuleID, proof);
      // Event would be emitted, budget increased
      const newState = await thermal.currentState();
      expect(newState.entropyBudget).to.be.gt(100000);
    });
  });

  describe("SovereignConsciousness", function () {
    it("Should verify interlock signature", async function () {
      const sig = {
        eccSignature: "0x1234",
        wotsSignature: "0x5678",
        publicKeyRoot: ethers.id("PUBKEY")
      };

      const result = await sovereign.verifyInterlock(sig, owner.address);
      expect(result).to.equal(true);
    });
  });
});
