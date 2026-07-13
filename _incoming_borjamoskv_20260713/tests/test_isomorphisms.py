# [C5-REAL] Isomorphism Testing Suite
import pytest
import ast
import sys
import os
import importlib

# Ensure the root of the project is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import numeric modules dynamically to bypass Python identifier syntax restrictions
es = importlib.import_module("cortex.isomorphisms.01_event_sourcing")
ap = importlib.import_module("cortex.isomorphisms.02_ast_projection")
lc = importlib.import_module("cortex.isomorphisms.03_logos_compliance")

def test_causal_event_sourcing_isomorphism():
    ledger = es.Ledger()
    # Initial state should be inactive
    state = es.derive_state(ledger)
    assert state.status == "INACTIVE"
    assert state.exergy_level == 0
    assert state.mutations == 0

    # Inject initialization
    ledger.append(es.Event("SYSTEM_INIT", {"id": "TEST-NODE"}, 100.0))
    state = es.derive_state(ledger)
    assert state.id == "TEST-NODE"
    assert state.status == "ACTIVE"
    assert state.mutations == 1

    # Inject exergy
    ledger.append(es.Event("EXERGY_INJECTION", {"amount": 150}, 101.0))
    state = es.derive_state(ledger)
    assert state.exergy_level == 150
    assert state.mutations == 2

    # Inject apoptosis
    ledger.append(es.Event("APOPTOSIS", {}, 102.0))
    state = es.derive_state(ledger)
    assert state.status == "TERMINATED"
    assert state.exergy_level == 0
    assert state.mutations == 3


def test_ast_projection_isomorphism():
    source_code = "def simple_func():\n    return 42\n"
    tree = ast.parse(source_code)
    
    injector = ap.SentinelInjector()
    mutated_tree = injector.visit(tree)
    ast.fix_missing_locations(mutated_tree)
    
    # Compile and execute the mutated tree to verify execution and injected print statement
    code_obj = compile(mutated_tree, filename="<string>", mode="exec")
    namespace = {}
    exec(code_obj, namespace)  # noqa: S102
    
    # Check that the function exists
    assert "simple_func" in namespace
    
    # Check AST structure: the first node in body must be an expression containing print
    func_node = mutated_tree.body[0]
    assert isinstance(func_node, ast.FunctionDef)
    first_statement = func_node.body[0]
    assert isinstance(first_statement, ast.Expr)
    assert isinstance(first_statement.value, ast.Call)
    assert isinstance(first_statement.value.func, ast.Name)
    assert first_statement.value.func.id == "print"


def test_logos_style_compliance_linter():
    linter = lc.LogosLinter()

    # Case 1: Fully compliant text
    compliant_text = (
        f"El kernel <span style=\"{lc.STYLES['cognitivo']}\">C5-REAL</span> "
        f"corrió <span style=\"{lc.STYLES['ejecucion']}\">pytest</span> en "
        f"<span style=\"{lc.STYLES['empirico']}\">12 ms</span>."
    )
    result = linter.check_compliance(compliant_text)
    assert result["compliance_ratio"] == 1.0
    assert len(result["violations"]) == 0

    # Case 2: Text with violations (unwrapped terms)
    non_compliant_text = "El kernel C5-REAL falló con Deadlock y arrojó un error."
    result = linter.check_compliance(non_compliant_text)
    assert result["compliance_ratio"] < 1.0
    assert len(result["violations"]) >= 2
    words_violating = [v["word"] for v in result["violations"]]
    assert any("C5-REAL" in w for w in words_violating)
    assert any("Deadlock" in w for w in words_violating)
