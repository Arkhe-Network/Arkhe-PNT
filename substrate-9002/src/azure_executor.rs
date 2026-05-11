// Substrato 9002 – executor azure
use azure_quantum_sdk::Workspace;

pub async fn run_qft_on_azure(circuit_qasm: &str) -> Result<String, Box<dyn std::error::Error>> {
    let ws = Workspace::from_env()?;
    let job = ws.submit_job(
        "ionq.simulator",
        circuit_qasm,
        Some("arkhe-qft"),
    ).await?;
    Ok(job.id)
}
