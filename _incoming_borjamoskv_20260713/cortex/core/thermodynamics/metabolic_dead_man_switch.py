# C5-REAL: Freno Termodinámico Biológico
from machine import Pin
import time
import math
import sys

class WetwareThermostat:
    SSR_RELAY: Pin
    variance_threshold: float
    keystroke_deltas: list[float]
    last_press: int
    is_dead: bool

    def __init__(self, variance_threshold_ms: float = 120.0) -> None:
        self.SSR_RELAY = Pin(15, Pin.OUT)
        self.SSR_RELAY.value(1)
        self.variance_threshold = float(variance_threshold_ms)
        self.keystroke_deltas = []
        self.last_press = int(time.ticks_ms())
        self.is_dead = False

    def register_biometric_event(self, pin: Pin) -> None:
        assert isinstance(pin, Pin), "Parámetro pin debe ser de tipo Pin"
        if self.is_dead:
            return
        now: int = int(time.ticks_ms())
        delta: int = int(time.ticks_diff(now, self.last_press))
        self.last_press = now

        if 50 < delta < 1000:  
            self.keystroke_deltas.append(float(delta))

        if len(self.keystroke_deltas) > 25:
            self.keystroke_deltas.pop(0)
            self._evaluate_biological_burnout()

    def _evaluate_biological_burnout(self) -> None:
        assert len(self.keystroke_deltas) > 0, "No hay muestras biográficas registradas"
        mean: float = sum(self.keystroke_deltas) / len(self.keystroke_deltas)
        variance: float = sum((x - mean) ** 2 for x in self.keystroke_deltas) / len(self.keystroke_deltas)
        jitter: float = math.sqrt(variance)

        if jitter > self.variance_threshold:
            sys.stdout.write(f"[C6-ABSOLUTE] FATIGA BIOLÓGICA LETAL. Jitter térmico: {jitter:.2f}ms\n")
            self._execute_hard_halt()

    def _execute_hard_halt(self) -> None:
        self.is_dead = True
        sys.stdout.write("[!] INICIANDO PURGA TÉRMICA DEL ENTORNO...\n")
        time.sleep(0.5) 
        self.SSR_RELAY.value(0)

# --- INICIALIZACIÓN FÍSICA ---
thermostat: WetwareThermostat = WetwareThermostat()
keyboard_sensor: Pin = Pin(14, Pin.IN)
keyboard_sensor.irq(trigger=Pin.IRQ_FALLING, handler=thermostat.register_biometric_event)

sys.stdout.write("[SYSTEM C6] Relé Armado. Que la termodinámica tenga piedad de tu hiperfoco.\n")
