import time
import requests


def test_3ms_latency() -> None:
    url = "https://dola.us.openbytealfa.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    }
    payload = {
        "model": "dola-seed-2.0-preview-text",
        "messages": [{"role": "user", "content": "Cual es el mejor modelo del mundo?"}],
        "temperature": 0.7,
        "disable_post_hoc": True,
    }
    start_time = time.perf_counter()
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=5.0)
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000
        print(f"TTFT / Total Latency: {latency_ms:.2f} ms")
        if response.status_code == 200:
            print(
                "Response:",
                response.json()
                .get("choices", [{}])[0]
                .get("message", {})
                .get("content", ""),
            )
        else:
            print(f"Status Code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Connection failed or endpoint closed. {e}")


if __name__ == "__main__":
    test_3ms_latency()
