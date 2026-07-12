import sys

LEXICON = [
    "📢",
    "📦",
    "🧠",
    "⚡",
    "💀",
    "🩸",
    "📤",
    "🛡️",
    "✅",
    "🔒",
    "🔄",
    "👑",
    "⏳",
    "❌",
]
DAG = {
    "📢": ["📦"],
    "📦": ["🧠", "🛡️"],
    "🧠": ["⚡", "🩸", "⏳"],
    "⚡": ["✅"],
    "💀": ["🩸", "❌"],
    "🩸": ["🧠"],
    "🛡️": ["✅", "💀"],
    "✅": ["🔒"],
    "🔒": ["📤"],
    "🔄": ["👑"],
    "👑": ["📢"],
    "⏳": ["🧠", "💀"],
    "❌": ["🔄", "💀"],
    "📤": [],
}


def tokenize_emojis(sequence):
    tokens = []
    i = 0
    while i < len(sequence):
        matched = False
        for lex in sorted(LEXICON, key=len, reverse=True):
            if sequence.startswith(lex, i):
                tokens.append(lex)
                i += len(lex)
                matched = True
                break
        if not matched:
            return (None, sequence[i:])
    return (tokens, None)


def validate_causal_path(sequence):
    tokens, err = tokenize_emojis(sequence)
    if not tokens:
        return (
            "💀 SIGKILL_STATE_PURGE",
            f"Token no reconocido en índice de falla: '{err}'",
        )
    for i in range(len(tokens) - 1):
        src = tokens[i]
        dst = tokens[i + 1]
        allowed = DAG.get(src, [])
        if dst not in allowed:
            return (
                "💀 SIGKILL_STATE_PURGE",
                f"Violación Termodinámica: {src} ➔ {dst} es imposible.",
            )
    return (
        "⚡ CAUSAL_PATH_VALIDATED",
        f"Secuencia isomórfica perfecta ({len(tokens)} tokens).",
    )


if __name__ == "__main__":
    sys.stdout.write("❖ [ C5-DAEMON-CORE :: MOTOR ISOMÓRFICO DAG ] ❖\n\n")
    test_vectors = [
        ("Flujo Nominal PBFT", "📢📦🧠⚡✅🔒📤"),
        ("Flujo Nominal + Commit", "📢📦🛡️✅🔒📤"),
        ("Flujo de View Change", "💀❌🔄👑📢📦🧠⚡✅🔒📤"),
        ("Flujo de Rollback", "📦🧠⏳💀🩸🧠⚡✅🔒📤"),
        ("Falla: Cortocircuito Ilegal", "📢📦⏳💀📤"),
        ("Falla: Salto Cuántico", "🧠📤"),
        ("Falla: Token Inyectado", "📢📦🧠X⚡"),
    ]
    for name, seq in test_vectors:
        sys.stdout.write(f"--- [ {name} ] ---\n")
        sys.stdout.write(f"  Input: {seq}\n")
        status, msg = validate_causal_path(seq)
        if "VALIDATED" in status:
            sys.stdout.write(f"  [ {status} ] :: {msg}\n\n")
        else:
            sys.stdout.write(f"  [ {status} ] :: {msg}\n\n")
