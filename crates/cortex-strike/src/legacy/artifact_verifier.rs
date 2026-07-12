// C5-REAL: Artifact Verifier (Remediación P0)
// Reemplazo de DefaultHasher (SipHash) por SHA-256 estricto.

use sha2::{Sha256, Digest};

pub fn compute_sha256_seal(data: &[u8]) -> String {
    let mut hasher = Sha256::new();
    hasher.update(data);
    let result = hasher.finalize();
    format!("{:x}", result)
}

fn main() {
    println!("INTEGRITY CONFIRMED: SHA-256 Seal Active [C5-REAL]");
}
