from math_kernel import calculate_exergy

def run_tests():
    try:
        assert calculate_exergy(10, 2.5) == 400.0, "Violación termodinámica: La exergía no decreció conforme a la ley."
        print("PRUEBA EXITOSA")
    except AssertionError as e:
        import sys
        print(f"FALLO DE ASERCIÓN: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_tests()

