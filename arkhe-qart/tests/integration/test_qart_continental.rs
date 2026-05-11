use arkhe_qart::oracle::entropy_auction::EntropyAuction;
use arkhe_qart::oracle::trend_detector::TrendDetector;
use arkhe_qart::provenance::zk_circuit::ProvenanceCircuit;

#[test]
fn test_integration_6064_auction_resolution() {
    let mut auction = EntropyAuction::new();

    // Bidder 1 places a low bid
    assert!(auction.place_bid("bidder1", 10.5));
    // Bidder 2 places a higher bid
    assert!(auction.place_bid("bidder2", 15.0));
    // Bidder 3 places a losing bid
    assert!(!auction.place_bid("bidder3", 12.0));

    // Vickrey auction resolves to highest bidder paying second highest price
    let result = auction.resolve_auction().expect("Auction should have a winner");
    assert_eq!(result.0, "bidder2", "Winner should be the highest bidder");
    assert_eq!(result.1, 12.0, "Price should be the second highest bid");
}

#[test]
fn test_trend_detection_ewma_integration() {
    // alpha = 0.5, threshold = 0.8
    let mut detector = TrendDetector::new(0.5, 0.8);

    // Initial state
    assert!(!detector.is_trending());

    // Smooth buildup
    assert!(!detector.update(0.5)); // ewma = 0.25
    assert!(!detector.update(0.9)); // ewma = 0.575
    assert!(!detector.update(1.0)); // ewma = 0.7875
    assert!(detector.update(1.0));  // ewma = 0.89375 (> 0.8)

    // Cooling down
    assert!(!detector.update(0.0));  // ewma = 0.446875 (< 0.8)
    assert!(!detector.is_trending());
}

#[test]
fn test_zk_circuit_integration() {
    let circuit = ProvenanceCircuit::build().expect("Circuit build failed");
    let secret = 42;
    let proof = circuit.prove(secret).expect("Proof generation failed");
    assert!(circuit.verify(proof).is_ok(), "Proof verification should succeed");
}
