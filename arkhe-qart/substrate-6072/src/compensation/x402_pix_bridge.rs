use reqwest::{Client, Error};
use serde::{Deserialize, Serialize};

#[derive(Serialize)]
pub struct PixPaymentVerifyRequest {
    pub txid: String,
    pub payer_key: String,
    pub signature: String,
    pub pub_key: String,
    pub timestamp: f64,
    pub amount: f64,
}

#[derive(Deserialize, Debug)]
pub struct PixPaymentVerifyResponse {
    pub txid: String,
    pub status: String,
    pub message: Option<String>,
}

pub struct PixBridge {
    endpoint: String,
    client: Client,
}

impl PixBridge {
    pub fn new(endpoint: &str) -> Self {
        PixBridge {
            endpoint: endpoint.to_string(),
            client: Client::new(),
        }
    }

    pub async fn verify_payment(
        &self,
        txid: &str,
        payer_key: &str,
        signature: &str,
        pub_key: &str,
        timestamp: f64,
        amount: f64
    ) -> Result<PixPaymentVerifyResponse, Error> {
        let url = format!("{}/v1/pix/x402/payment-verify", self.endpoint);
        let req_body = PixPaymentVerifyRequest {
            txid: txid.to_string(),
            payer_key: payer_key.to_string(),
            signature: signature.to_string(),
            pub_key: pub_key.to_string(),
            timestamp,
            amount,
        };

        let response = self.client.post(&url)
            .json(&req_body)
            .send()
            .await?;

        response.json::<PixPaymentVerifyResponse>().await
    }
}
