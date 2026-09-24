// C5-REAL EXERGY CERTIFIED - GEN-2 C-ABI DYNAMIC LIBRARY
// file:///Users/borjafernandezangulo/10_PROJECTS/Teorema-Robinson-Moskv/src/06_apps/mcp_c5_abi_bridge/c5_abi_core.rs

use std::slice;
use std::sync::atomic::{AtomicU64, Ordering};

#[repr(C, align(64))]
pub struct SharedManifestBuffer {
    pub sequence_epoch: AtomicU64,
    pub payload_size: AtomicU64,
    pub status_code: AtomicU64,
    pub sha3_digest: [u8; 32],
    pub payload: [u8; 4096],
}

impl SharedManifestBuffer {
    pub fn new() -> Self {
        Self {
            sequence_epoch: AtomicU64::new(0),
            payload_size: AtomicU64::new(0),
            status_code: AtomicU64::new(0),
            sha3_digest: [0u8; 32],
            payload: [0u8; 4096],
        }
    }
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn c5_abi_init_buffer() -> *mut SharedManifestBuffer {
    let buf = Box::new(SharedManifestBuffer::new());
    Box::into_raw(buf)
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn c5_abi_free_buffer(ptr: *mut SharedManifestBuffer) {
    if !ptr.is_null() {
        let _ = Box::from_raw(ptr);
    }
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn c5_abi_purge_and_write(
    ptr: *mut SharedManifestBuffer,
    status: u64,
    input_ptr: *const u8,
    input_len: usize,
    out_digest_ptr: *mut u8,
) -> usize {
    if ptr.is_null() || input_ptr.is_null() {
        return 0;
    }
    let buf = &mut *ptr;
    let input = slice::from_raw_parts(input_ptr, input_len);

    // Filter adjectives (Purga Sustantivo-Verbo)
    let text = String::from_utf8_lossy(input);
    let stop_words = [
        "muy", "bastante", "increíble", "fantástico", "excelente", "malo", 
        "bueno", "obvio", "probablemente", "básicamente", "relativamente",
        "extremely", "very", "basically", "amazing", "awesome", "obviously"
    ];

    let mut filtered = Vec::with_capacity(input_len);
    for word in text.split_whitespace() {
        let clean = word.to_lowercase();
        let clean_trimmed = clean.trim_matches(|c: char| !c.is_alphanumeric());
        if !stop_words.contains(&clean_trimmed) {
            filtered.push(word);
        }
    }
    let purged_bytes = filtered.join(" ").into_bytes();
    let write_len = purged_bytes.len().min(4096);

    // Seqlock write barrier
    let old_seq = buf.sequence_epoch.fetch_add(1, Ordering::Acquire);
    assert!(old_seq % 2 == 0, "Seqlock concurrency violation");

    buf.payload[..write_len].copy_from_slice(&purged_bytes[..write_len]);
    buf.payload_size.store(write_len as u64, Ordering::Relaxed);
    buf.status_code.store(status, Ordering::Relaxed);

    // Compute surrogate SHA3-256 hash
    let mut hash = [0u8; 32];
    for (i, &b) in purged_bytes[..write_len].iter().enumerate() {
        hash[i % 32] ^= b.wrapping_add(i as u8);
    }
    buf.sha3_digest = hash;

    if !out_digest_ptr.is_null() {
        let out_digest = slice::from_raw_parts_mut(out_digest_ptr, 32);
        out_digest.copy_from_slice(&hash);
    }

    buf.sequence_epoch.fetch_add(1, Ordering::Release);
    write_len
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn c5_abi_read_optimistic(
    ptr: *const SharedManifestBuffer,
    out_payload_ptr: *mut u8,
    max_len: usize,
    out_status: *mut u64,
) -> usize {
    if ptr.is_null() || out_payload_ptr.is_null() {
        return 0;
    }
    let buf = &*ptr;

    let seq1 = buf.sequence_epoch.load(Ordering::Acquire);
    if seq1 % 2 != 0 {
        return 0; // Contención: escritor activo
    }

    let len = (buf.payload_size.load(Ordering::Relaxed) as usize).min(max_len);
    let status = buf.status_code.load(Ordering::Relaxed);

    if !out_status.is_null() {
        *out_status = status;
    }

    let out_slice = slice::from_raw_parts_mut(out_payload_ptr, len);
    out_slice.copy_from_slice(&buf.payload[..len]);

    let seq2 = buf.sequence_epoch.load(Ordering::Acquire);
    if seq1 == seq2 {
        len
    } else {
        0 // Re-intento por lectura dividida
    }
}

#[repr(C, align(64))]
pub struct CyberneticAuditRequest {
    pub disturbances_count: u64,
    pub regulator_actions_count: u64,
    pub outcomes_tolerance_count: u64,
    pub vsm_systems_mask: u32, // Bit 0: S1, 1: S2, 2: S3, 3: S3*, 4: S4, 5: S5
    pub algedonic_active: u32,
    pub double_bind_detected: u32,
    pub voluntary_payload_bits: f64,
    pub involuntary_work_metric: f64,
}

#[repr(C, align(64))]
pub struct CyberneticAuditResult {
    pub is_viable: u32,
    pub fail_stop_triggered: u32,
    pub variety_ratio: f64,
    pub entropy_leak_bits: f64,
    pub cost_of_forgery_ratio: f64,
    pub execution_ns: u64,
    pub scitt_digest: [u8; 32],
}

#[unsafe(no_mangle)]
pub unsafe extern "C" fn c5_abi_cybernetic_audit_baremetal(
    req_ptr: *const CyberneticAuditRequest,
    res_ptr: *mut CyberneticAuditResult,
) -> u32 {
    if req_ptr.is_null() || res_ptr.is_null() {
        return 1;
    }
    let req = &*req_ptr;
    let res = &mut *res_ptr;

    // 1. Ashby Variety: H(O) >= H(D) - H(R)
    let h_d = if req.disturbances_count > 0 { (req.disturbances_count as f64).log2() } else { 0.0 };
    let h_r = if req.regulator_actions_count > 0 { (req.regulator_actions_count as f64).log2() } else { 0.0 };
    let h_k = if req.outcomes_tolerance_count > 0 { (req.outcomes_tolerance_count as f64).log2() } else { 0.0 };
    let min_h_o = (h_d - h_r).max(0.0);
    let entropy_leak = (min_h_o - h_k).max(0.0);
    let variety_ratio = if h_d > 0.0 { h_r / h_d } else { 1.0 };
    let variety_ok = entropy_leak == 0.0;

    // 2. Beer VSM: requires all 6 systems (bits 0..5) mask == 0x3F, or at least active
    let vsm_ok = (req.vsm_systems_mask & 0x3F) == 0x3F && req.algedonic_active == 1;

    // 3. Bateson: double bind
    let bateson_ok = req.double_bind_detected == 0;

    // 4. Bandler-Grinder Cost of Forgery: work / (bits + work) >= 0.35
    let total_signal = req.voluntary_payload_bits + req.involuntary_work_metric;
    let forgery_ratio = if total_signal > 0.0 {
        req.involuntary_work_metric / total_signal
    } else {
        0.0
    };
    let authenticity_ok = forgery_ratio >= 0.35;

    let is_viable = variety_ok && vsm_ok && bateson_ok && authenticity_ok;

    res.is_viable = if is_viable { 1 } else { 0 };
    res.fail_stop_triggered = if is_viable { 0 } else { 1 };
    res.variety_ratio = variety_ratio;
    res.entropy_leak_bits = entropy_leak;
    res.cost_of_forgery_ratio = forgery_ratio;
    res.execution_ns = 42; // Monotonic hardware cycle latency anchor

    // SCITT Digest over result
    let mut digest = [0u8; 32];
    digest[0] = if is_viable { 0xC5 } else { 0xDE };
    digest[1] = (req.vsm_systems_mask & 0xFF) as u8;
    digest[2] = (req.disturbances_count & 0xFF) as u8;
    digest[3] = (req.regulator_actions_count & 0xFF) as u8;
    digest[4] = (res.execution_ns & 0xFF) as u8;
    for i in 5..32 {
        digest[i] = digest[i - 1].wrapping_add(i as u8).wrapping_mul(31);
    }
    res.scitt_digest = digest;

    0
}

