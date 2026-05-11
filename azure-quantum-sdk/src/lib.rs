#![allow(unused_variables)]

/// Mock workspace that would normally interact with Azure Quantum.
pub struct Workspace;

impl Workspace {
    pub fn from_env() -> Result<Self, MockError> {
        Ok(Workspace)
    }

    pub async fn submit_job(
        &self,
        target: &str,
        circuit: &str,
        name: Option<&str>,
    ) -> Result<Job, MockError> {
        // In production, this would call the Azure Quantum REST API.
        Ok(Job {
            id: "mock-job-001".into(),
        })
    }
}

pub struct Job {
    pub id: String,
}

#[derive(Debug)]
pub struct MockError;
impl std::fmt::Display for MockError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "mock error")
    }
}
impl std::error::Error for MockError {}