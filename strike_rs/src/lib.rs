use pyo3::prelude::*;
use pyo3::types::PyDict;
use flate2::write::ZlibEncoder;
use flate2::Compression;
use std::io::prelude::*;

/// Approximates Kolmogorov Complexity using zlib compression ratio via flate2.
#[pyfunction]
fn compute_kolmogorov_approximation_rs(py: Python, text_data: &str) -> PyResult<PyObject> {
    let dict = PyDict::new(py);
    
    if text_data.is_empty() {
        dict.set_item("mdl", 0.0)?;
        dict.set_item("compressed_size", 0)?;
        dict.set_item("raw_size", 0)?;
        dict.set_item("compression_ratio", 1.0)?;
        return Ok(dict.into());
    }

    let raw_bytes = text_data.as_bytes();
    let raw_size = raw_bytes.len();

    // Using flate2 ZlibEncoder at max compression (level 9)
    let mut encoder = ZlibEncoder::new(Vec::new(), Compression::best());
    encoder.write_all(raw_bytes).unwrap();
    let compressed_bytes = encoder.finish().unwrap();
    
    let compressed_size = compressed_bytes.len();
    
    let mdl = compressed_size as f64 / raw_size as f64;
    let compression_ratio = if compressed_size > 0 {
        raw_size as f64 / compressed_size as f64
    } else {
        1.0
    };

    dict.set_item("mdl", mdl)?;
    dict.set_item("compressed_size", compressed_size)?;
    dict.set_item("raw_size", raw_size)?;
    dict.set_item("compression_ratio", compression_ratio)?;

    Ok(dict.into())
}

/// A Python module implemented in Rust.
#[pymodule]
fn strike_rs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(compute_kolmogorov_approximation_rs, m)?)?;
    Ok(())
}
