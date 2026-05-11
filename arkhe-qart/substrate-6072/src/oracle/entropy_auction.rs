pub struct EntropyAuction {
    pub highest_bid: f64,
    pub second_highest_bid: f64,
    pub winning_bidder: Option<String>,
}

impl EntropyAuction {
    pub fn new() -> Self {
        EntropyAuction {
            highest_bid: 0.0,
            second_highest_bid: 0.0,
            winning_bidder: None,
        }
    }

    // Vickrey Auction (Second-price sealed-bid)
    pub fn place_bid(&mut self, bidder_id: &str, amount: f64) -> bool {
        if amount > self.highest_bid {
            self.second_highest_bid = self.highest_bid;
            self.highest_bid = amount;
            self.winning_bidder = Some(bidder_id.to_string());
            true
        } else if amount > self.second_highest_bid {
            self.second_highest_bid = amount;
            false
        } else {
            false
        }
    }

    pub fn resolve_auction(&self) -> Option<(String, f64)> {
        self.winning_bidder.as_ref().map(|bidder| {
            (bidder.clone(), self.second_highest_bid)
        })
    }
}
