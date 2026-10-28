use abzu_kernel::sandbox::wasi_env::SandboxEnv;

#[test]
fn compiles_a_valid_wasm_module() {
    let sandbox = SandboxEnv::new().expect("create sandbox");
    let empty_wasm = b"\0asm\x01\0\0\0";
    let (status, digest) = sandbox.execute_tool(empty_wasm, &[]).expect("compile wasm");
    assert_eq!(status, 0);
    assert_eq!(digest, vec![0; 32]);
}

#[test]
fn rejects_invalid_wasm() {
    let sandbox = SandboxEnv::new().expect("create sandbox");
    assert!(sandbox.execute_tool(b"not wasm", &[]).is_err());
}
