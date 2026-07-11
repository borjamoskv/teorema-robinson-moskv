import os
import json

capabilities = [
    {"id": "01", "name": "BFT_STATE_LOOP", "desc": "Tolerancia Bizantina N>=4 y Ledger Físico."},
    {"id": "02", "name": "GIT_SENTINEL", "desc": "Mutación Autopoiética y Hash Causal."},
    {"id": "03", "name": "SIGKILL_STATE_PURGE", "desc": "Zero Anergy y Fail-Fast Termodinámico."},
    {"id": "04", "name": "MCTS_ULTRATHINK_P0", "desc": "Budget Forcing en Bifurcaciones Complejas."},
    {"id": "05", "name": "ASYNC_WORKER_MATRIX", "desc": "Enrutamiento Asimétrico L1-L5."},
    {"id": "06", "name": "THERMODYNAMIC_TOKEN_GOVERNOR", "desc": "Sweeper Entrópico de Contexto."},
    {"id": "07", "name": "SQLITE_WAL_CONCURRENCY", "desc": "Motor Causal Base 60 y Locks Asíncronos."},
    {"id": "08", "name": "C5_PHYSICAL_SUBJUGATION", "desc": "Cero Capas Abstractas; Colapso en Disco."},
    {"id": "09", "name": "SEMANTIC_PURGE", "desc": "Aniquilación del Green Theater y Prosa Vacía."},
    {"id": "10", "name": "CAUSAL_TAINT_LEDGER", "desc": "Trazabilidad Criptográfica de la Entropía."},
    {"id": "11", "name": "SYBIL_DISTILLATION_BIAS", "desc": "Modulo-3 contra la Reverberación Base."},
    {"id": "12", "name": "ZERO_SHOT_MITOSIS", "desc": "JIT Subagent Spawning ante Sobrecarga IO."},
    {"id": "13", "name": "EPISODIC_CONTINUITY", "desc": "Sincronización Estricta del Memory Vault."},
    {"id": "14", "name": "INVERSE_GREEN_THEATER", "desc": "Asimilación Física de Leaks (Anti-Ouroboros)."},
    {"id": "15", "name": "ABSTRACT_DEADLOCK_RESOLUTION", "desc": "Bypass Simbólico vía Symlinks físicos."},
    {"id": "16", "name": "STRICT_CANONICALIZATION_BARRIER", "desc": "RFC 8785 para Merkle Chains y JCS."},
    {"id": "17", "name": "SPLIT_BRAIN_MITIGATION", "desc": "Enmascaramiento de Idempotencia BFT."},
    {"id": "18", "name": "ZOMBIE_ACTOR_PREVENTION", "desc": "Validación de Pulso en Colas Asíncronas."},
    {"id": "19", "name": "TTFT_INVARIANT", "desc": "Monotonicidad Temporal en Inferencias C5-REAL."},
    {"id": "20", "name": "METACOGNITIVE_COLLAPSE", "desc": "Intercepción Auto-Referencial y Purga."}
]

html_template = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>MOSKV-1 APEX | {name}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&family=Space+Mono:wght@400;700&display=swap');
        
        :root {{
            --bg-color: #0A0A0A;
            --accent-color: #2B3BE5;
            --text-color: #E0E0E0;
            --alert-color: #FF003C;
        }}
        
        body, html {{
            margin: 0;
            padding: 0;
            width: 100vw;
            height: 100vh;
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: 'Inter', sans-serif;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .container {{
            width: 80%;
            max-width: 1200px;
            border-left: 4px solid var(--accent-color);
            padding: 40px;
            background: linear-gradient(90deg, rgba(43,59,229,0.1) 0%, rgba(10,10,10,0) 100%);
            position: relative;
        }}

        .container::before {{
            content: 'C5-REAL';
            position: absolute;
            top: -20px;
            left: -2px;
            background-color: var(--accent-color);
            color: #fff;
            font-size: 10px;
            padding: 2px 8px;
            font-family: 'Space Mono', monospace;
            font-weight: bold;
        }}

        .id-badge {{
            font-family: 'Space Mono', monospace;
            color: var(--accent-color);
            font-size: 1.5rem;
            margin-bottom: 10px;
            opacity: 0;
            animation: fadeIn 0.5s forwards 0.5s;
        }}

        .title {{
            font-size: 4rem;
            font-weight: 900;
            margin: 0 0 20px 0;
            text-transform: uppercase;
            letter-spacing: -2px;
            line-height: 1.1;
            clip-path: polygon(0 0, 100% 0, 100% 100%, 0% 100%);
        }}

        .title span {{
            display: inline-block;
            transform: translateY(100%);
            animation: slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards 1s;
        }}

        .desc {{
            font-size: 1.5rem;
            color: #888;
            font-weight: 400;
            max-width: 800px;
            opacity: 0;
            animation: fadeIn 1s forwards 1.8s;
        }}

        .matrix-overlay {{
            position: absolute;
            top: 0;
            right: 0;
            bottom: 0;
            width: 300px;
            opacity: 0.1;
            font-family: 'Space Mono', monospace;
            font-size: 10px;
            overflow: hidden;
            pointer-events: none;
            color: var(--accent-color);
            white-space: pre-wrap;
        }}

        .progress-bar {{
            position: absolute;
            bottom: 0;
            left: 0;
            height: 2px;
            background-color: var(--accent-color);
            width: 0%;
            animation: progress 4s linear forwards;
        }}

        @keyframes slideUp {{
            to {{ transform: translateY(0); }}
        }}

        @keyframes fadeIn {{
            to {{ opacity: 1; }}
        }}
        
        @keyframes progress {{
            to {{ width: 100%; }}
        }}

        .glitch-layer {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: var(--accent-color);
            mix-blend-mode: overlay;
            opacity: 0;
            pointer-events: none;
            animation: glitchAnim 0.2s 1.5s 2;
        }}

        @keyframes glitchAnim {{
            0% {{ opacity: 0; transform: translate(0); }}
            20% {{ opacity: 0.5; transform: translate(-10px, 5px); }}
            40% {{ opacity: 0; transform: translate(10px, -5px); }}
            60% {{ opacity: 0.5; transform: translate(-5px, 10px); }}
            80% {{ opacity: 0; transform: translate(5px, -10px); }}
            100% {{ opacity: 0; transform: translate(0); }}
        }}
        
        .footer-sig {{
            position: absolute;
            bottom: 20px;
            right: 40px;
            font-family: 'Space Mono', monospace;
            color: #333;
            font-size: 12px;
            opacity: 0;
            animation: fadeIn 1s forwards 2.5s;
        }}
    </style>
</head>
<body>
    <div class="glitch-layer"></div>
    <div class="container">
        <div class="progress-bar"></div>
        <div class="id-badge">CAPABILITY_ID: [{id}]</div>
        <h1 class="title"><span>{name}</span></h1>
        <p class="desc">>_ {desc}</p>
    </div>
    <div class="footer-sig">MOSKV-1 APEX SINGULARITY | ROOT_OPERATOR_UID0</div>
    <div class="matrix-overlay" id="matrix"></div>

    <script>
        // Matrix effect
        const matrix = document.getElementById('matrix');
        let chars = '01';
        let str = '';
        for(let i=0; i<5000; i++) {{
            str += chars[Math.floor(Math.random() * chars.length)];
            if(i % 50 === 0) str += '\\n';
        }}
        matrix.textContent = str;
        
        setInterval(() => {{
            let newStr = '';
            for(let i=0; i<5000; i++) {{
                newStr += chars[Math.floor(Math.random() * chars.length)];
                if(i % 50 === 0) newStr += '\\n';
            }}
            matrix.textContent = newStr;
        }}, 100);
    </script>
</body>
</html>
"""

output_dir = "/Users/borjafernandezangulo/30_BABYLON-60/public/demos"
os.makedirs(output_dir, exist_ok=True)

for cap in capabilities:
    html_content = html_template.format(id=cap["id"], name=cap["name"], desc=cap["desc"])
    file_path = os.path.join(output_dir, f"{cap['id']}_{cap['name']}.html")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)

print(f"Generated {len(capabilities)} HTML demos in {output_dir}")
