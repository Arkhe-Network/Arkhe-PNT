use regex::Regex;

pub struct UniversalScanner {
    patterns: Vec<Regex>,
}

impl UniversalScanner {
    pub fn new() -> Self {
        let patterns = vec![
            Regex::new(r#"(?i)(password|secret|key|token|api_key)\s*[:=]\s*['"][^'"]+['"]"#).unwrap(),
            Regex::new(r"(?i)SELECT\s+.*?\s+FROM\s+.*?\s+WHERE\s+.*?=").unwrap(),
            Regex::new(r"(?i)exec\s*\(").unwrap(),
            Regex::new(r"(?i)eval\s*\(").unwrap(),
            Regex::new(r"(?i)system\s*\(").unwrap(),
            Regex::new(r"0x[a-fA-F0-9]{40}").unwrap(), // ETH addresses/private keys
        ];
        Self { patterns }
    }

    pub fn scan(&self, code: &str) -> Vec<String> {
        let mut findings = Vec::new();
        for pattern in &self.patterns {
            for capture in pattern.captures_iter(code) {
                if let Some(matched) = capture.get(0) {
                    findings.push(matched.as_str().to_string());
                }
            }
        }
        findings
    }
}
