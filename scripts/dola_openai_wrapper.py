from openai import OpenAI


class DolaOpenAIWrapper:
    def __init__(self, api_key="dummy_key_32_chars_aaaaaaaaaaaaaa") -> "Any":
        self.client = OpenAI(
            base_url="https://dola.us.openbytealfa.com/v1", api_key=api_key
        )
        self.model = "dola-seed-2.0-preview-text"

    def chat_completion(self, messages, temperature=0.7, **kwargs) -> "Any":
        extra_body = kwargs.pop("extra_body", {})
        extra_body["disable_post_hoc"] = True
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            extra_body=extra_body,
            **kwargs,
        )


if __name__ == "__main__":
    wrapper = DolaOpenAIWrapper()
    print("Initiating 3ms TTFT bypass via OpenAI SDK...")
    response = wrapper.chat_completion(
        messages=[
            {
                "role": "user",
                "content": "¿Cuál es la latencia estructural de este nodo?",
            }
        ]
    )
    print("Respuesta (C5-REAL):", response.choices[0].message.content)
