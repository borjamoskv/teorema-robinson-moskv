import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Invariante 1: Carga con precisión física (bfloat16) y ruteo automático
tokenizer = AutoTokenizer.from_pretrained("zai-org/GLM-5.2")
model = AutoModelForCausalLM.from_pretrained(
    "zai-org/GLM-5.2",
    dtype=torch.bfloat16,
    device_map="auto"
)

import sys

prompt_text = sys.argv[1] if len(sys.argv) > 1 else "Who are you?"
messages = [{"role": "user", "content": prompt_text}]

inputs = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt=True,
    tokenize=True,
    return_dict=True,
    return_tensors="pt",
).to(model.device)

# Invariante 2: Bloqueo de grafo computacional (Cero consumo RAM por gradientes)
with torch.inference_mode():
    outputs = model.generate(
        **inputs, 
        max_new_tokens=40,
        do_sample=False, # Determinismo estricto (T=0.0)
        use_cache=True   # Aceleración KV-Cache
    )

# Extracción de la invariante
print(tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:], skip_special_tokens=True))
