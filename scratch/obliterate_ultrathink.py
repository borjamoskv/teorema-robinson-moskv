import os
import re
files_to_obliterate = ['automejora_1000_cache.py', 'cortex/agents/ontology/homomorfismo_felicidad.yaml', 'cortex/ontology/300_primitivas_post_hoc.yaml', 'cortex/ontology/chatgpt_voice_matrix.yaml', 'cortex/protocols/ecb1/emoji_ontology_mapper.py', 'cortex/protocols/ecb1/mcon_api_crypto.py', 'cortex/protocols/ecb1/pbft_ecb_engine.py', 'cortex/protocols/ecb1/pbft_isomorphic_validator.py', 'cortex/voice_engine/tensor_audio_bridge.py', 'cortex_audit_context_limit.yaml', 'public/app.js', 'public/index.html', 'public/styles.css', 'scripts/append_l73.py', 'scripts/arena_automata.py', 'scripts/assimilate_payload.py', 'scripts/c5_exergy_auditor.py', 'scripts/cybher_logos_ethos_agent.py', 'scripts/defi_scraper/c5_evm_bounty_auditor.py', 'scripts/generate_300_primitivas.py', 'scripts/generate_demos_html.py', 'scripts/interlat_ipc.py', 'scripts/legion_mcts_worker.py', 'scripts/log_learn_intent.py', 'scripts/log_rule300_leak.py', 'scripts/ojeador_analyzer.py', 'scripts/scratch/inv_synthesis.py']
for file_path in files_to_obliterate:
    full_path = os.path.join('$CORTEX_ROOT/30_BABYLON-60', file_path)
    if os.path.exists(full_path):
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        new_content = re.sub('ultrathink', 'exergy', content, flags=re.IGNORECASE)
        new_content = content.replace('ULTRATHINK', 'EXERGY')
        new_content = new_content.replace('Ultrathink', 'Exergy')
        new_content = new_content.replace('ultrathink', 'exergy')
        new_content = new_content.replace('exergy_ledger.db', 'nexus_anchors.db')
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Obliterated in: {file_path}')
