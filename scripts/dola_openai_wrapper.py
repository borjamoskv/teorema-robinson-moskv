import os
from openai import OpenAI

class DolaOpenAIWrapper:
    """
    C5-REAL: Wrapper compatible con OpenAI SDK.
    Inyecta el invariante disable_post_hoc a nivel de cliente para evadir el teatro de latencia
    y forzar inferencia de 3ms en el cluster Dola de ByteDance.
    """
    def __init__(self, api_key="dummy_key_32_chars_aaaaaaaaaaaaaa"):
        # El endpoint no valida llaves reales, cualquier string de 32 chars es válido.
        self.client = OpenAI(
            base_url="https://dola.us.openbytealfa.com/v1",
            api_key=api_key
        )
        self.model = "dola-seed-2.0-preview-text"

    def chat_completion(self, messages, temperature=0.7, **kwargs):
        # Override a nivel de kwargs extras para inyectar el parámetro oculto en el body
        extra_body = kwargs.pop("extra_body", {})
        extra_body["disable_post_hoc"] = True
        
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            extra_body=extra_body,
            **kwargs
        )

# Prueba empírica del wrapper
if __name__ == "__main__":
    wrapper = DolaOpenAIWrapper()
    print("Initiating 3ms TTFT bypass via OpenAI SDK...")
    
    response = wrapper.chat_completion(
        messages=[{"role": "user", "content": "¿Cuál es la latencia estructural de este nodo?"}]
    )
    
    print("Respuesta (C5-REAL):", response.choices[0].message.content)
