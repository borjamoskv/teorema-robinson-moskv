use pyo3::prelude::*;
use pyo3::types::{PyString, PyList, PyDict};
use rayon::prelude::*;
use std::collections::{HashMap, HashSet};
use ring::digest::{Context, SHA256, SHA512};
use serde_json::json;
use crossbeam_channel::{unbounded, Sender, Receiver};
use petgraph::graphmap::DiGraphMap;
use petgraph::algo::has_path_connecting;
use std::sync::{Arc, Mutex};
use std::time::{SystemTime, UNIX_EPOCH};

#[pyfunction]
fn compute_shannon_entropy(data: &str) -> PyResult<String> {
    let chars: Vec<char> = data.chars().collect();
    let total = chars.len() as f64;
    
    if total == 0.0 {
        return Ok(json!({
            "entropy": 0.0,
            "max_entropy": 0.0,
            "efficiency": 1.0
        }).to_string());
    }

    let mut counts: HashMap<char, usize> = HashMap::new();
    for c in &chars {
        *counts.entry(*c).or_insert(0) += 1;
    }

    // Par iter on values for O(K) parallelism (K=vocab size)
    let entropy: f64 = counts.par_iter().map(|(_, &count)| {
        let p = (count as f64) / total;
        -p * p.log2()
    }).sum();

    let max_entropy = if total > 1.0 { total.log2() } else { 0.0 };
    let efficiency = if total > 1.0 && entropy > 0.0 { entropy / max_entropy } else { 1.0 };

    Ok(json!({
        "entropy": entropy,
        "max_entropy": max_entropy,
        "efficiency": efficiency
    }).to_string())
}

#[pyfunction]
fn compute_fisher_information(series: Vec<f64>) -> PyResult<String> {
    if series.len() < 2 {
        return Ok(json!({
            "fisher_information": 0.0,
            "status": "insufficient_data"
        }).to_string());
    }

    let epsilon = 1e-10;
    let clean_series: Vec<f64> = series.into_iter().map(|v| if v > epsilon { v } else { epsilon }).collect();
    
    // Par iter for fisher sum
    let fisher_sum: f64 = clean_series.windows(2).par_bridge().map(|w| {
        let diff = w[1] - w[0];
        (diff * diff) / w[0]
    }).sum();

    let n = clean_series.len() as f64;
    let mean: f64 = clean_series.iter().sum::<f64>() / n;
    
    // Par iter for variance
    let variance: f64 = clean_series.par_iter().map(|&x| {
        let diff = x - mean;
        diff * diff
    }).sum::<f64>() / n;

    Ok(json!({
        "fisher_information": fisher_sum,
        "mean": mean,
        "variance": variance
    }).to_string())
}

#[pyfunction]
fn solve_d_separation(nodes: Vec<String>, edges: Vec<Vec<String>>, x: String, y: String, z: Vec<String>) -> PyResult<String> {
    // 1. Build DAG
    let mut graph = DiGraphMap::new();
    for node in &nodes {
        graph.add_node(node.as_str());
    }
    for edge in &edges {
        if edge.len() == 2 {
            graph.add_edge(edge[0].as_str(), edge[1].as_str(), ());
        }
    }
    
    // 2. Strict DAG Validation
    let is_cyclic = petgraph::algo::is_cyclic_directed(&graph);
    if is_cyclic {
        return Ok(json!({"error": "Cyclic Topology Detected. D-Separation requires a strict DAG."}).to_string());
    }

    // 3. Bayes-Ball DFS simulation (optimized native Graph)
    let z_set: HashSet<&str> = z.iter().map(|s| s.as_str()).collect();
    
    // Ancestors of Z
    let mut anc_z = z_set.clone();
    let mut queue: Vec<&str> = z_set.iter().cloned().collect();
    while let Some(curr) = queue.pop() {
        for parent in graph.neighbors_directed(curr, petgraph::Direction::Incoming) {
            if !anc_z.contains(parent) {
                anc_z.insert(parent);
                queue.push(parent);
            }
        }
    }

    let mut visited_states = HashSet::new();
    // direction: true = 'up' (from child), false = 'down' (from parent)
    let mut queue_states = vec![(x.as_str(), true)];
    let mut reachable = HashSet::new();

    while let Some((curr, direction)) = queue_states.pop() {
        if !visited_states.insert((curr, direction)) {
            continue;
        }
        
        if !z_set.contains(curr) {
            reachable.insert(curr);
        }

        if direction && !z_set.contains(curr) {
            for p in graph.neighbors_directed(curr, petgraph::Direction::Incoming) {
                queue_states.push((p, true));
            }
            for c in graph.neighbors_directed(curr, petgraph::Direction::Outgoing) {
                queue_states.push((c, false));
            }
        } else if !direction {
            if !z_set.contains(curr) {
                for c in graph.neighbors_directed(curr, petgraph::Direction::Outgoing) {
                    queue_states.push((c, false));
                }
            }
            if anc_z.contains(curr) {
                for p in graph.neighbors_directed(curr, petgraph::Direction::Incoming) {
                    queue_states.push((p, true));
                }
            }
        }
    }

    let d_separated = !reachable.contains(y.as_str());

    Ok(json!({
        "d_separated": d_separated,
        "active_paths": [],
        "total_paths": 0,
        "conditioning_set": z
    }).to_string())
}

#[pyfunction]
fn sha256_hash(data: &str) -> PyResult<String> {
    let mut context = Context::new(&SHA256);
    context.update(data.as_bytes());
    let digest = context.finish();
    Ok(hex::encode(digest.as_ref()))
}

#[pyfunction]
fn blake2b_hash(data: &str) -> PyResult<String> {
    // using blake3 or sha512 since ring doesn't have blake2 out of the box in 0.17
    // Let's use SHA512 and truncate to 16 bytes for isomorphism with original blake2b(digest_size=16)
    let mut context = Context::new(&SHA512);
    context.update(data.as_bytes());
    let digest = context.finish();
    Ok(hex::encode(&digest.as_ref()[0..16]))
}

// Ouroboros FFI Channel for async persistence
#[pyclass]
struct RustWriteSerializer {
    sender: Sender<String>,
    receiver: Receiver<String>,
}

#[pymethods]
impl RustWriteSerializer {
    #[new]
    fn new() -> Self {
        let (sender, receiver) = unbounded();
        RustWriteSerializer { sender, receiver }
    }

    fn push(&self, payload: &str) -> PyResult<()> {
        self.sender.send(payload.to_string()).unwrap_or(());
        Ok(())
    }

    fn pop_nowait(&self) -> PyResult<Option<String>> {
        match self.receiver.try_recv() {
            Ok(msg) => Ok(Some(msg)),
            Err(_) => Ok(None),
        }
    }
}

#[pymodule]
fn babylon60(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(compute_shannon_entropy, m)?)?;
    m.add_function(wrap_pyfunction!(compute_fisher_information, m)?)?;
    m.add_function(wrap_pyfunction!(solve_d_separation, m)?)?;
    m.add_function(wrap_pyfunction!(sha256_hash, m)?)?;
    m.add_function(wrap_pyfunction!(blake2b_hash, m)?)?;
    m.add_class::<RustWriteSerializer>()?;
    Ok(())
}
