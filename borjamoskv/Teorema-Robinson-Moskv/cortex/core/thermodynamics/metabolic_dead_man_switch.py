# metabolic_dead_man_switch.py | Nivel de Realidad: #C6-ABSOLUTE 
from machine import Pin
import time, math

class WetwareThermostat:
    """Freno Termodinámico Biológico. Mide el jitter estocástico de tus dedos."""
    def __init__(self, variance_threshold_ms: float = 120.0):
        # Pin 15 gobierna la alimentación de los monitores LCD y la red
        self.SSR_RELAY = Pin(15, Pin.OUT)
        self.SSR_RELAY.value(1)  # 1 = Circuito Cerrado (Alimentación ON)
        self.variance_threshold = variance_threshold_ms
        self.keystroke_deltas, self.last_press = [], time.ticks_ms()
        self.is_dead = False

    def register_biometric_event(self, pin):
        if self.is_dead: return
        now = time.ticks_ms()
        delta = time.ticks_diff(now, self.last_press)
        self.last_press = now

        if 50 < delta < 1000:  
            self.keystroke_deltas.append(delta)

        if len(self.keystroke_deltas) > 25:
            self.keystroke_deltas.pop(0)
            self._evaluate_biological_burnout()

    def _evaluate_biological_burnout(self):
        mean = sum(self.keystroke_deltas) / len(self.keystroke_deltas)
        variance = sum((x - mean) ** 2 for x in self.keystroke_deltas) / len(self.keystroke_deltas)
        jitter = math.sqrt(variance)

        if jitter > self.variance_threshold:
            print(f"[C6-ABSOLUTE] FATIGA BIOLÓGICA LETAL. Jitter térmico: {jitter:.2f}ms")
            self._execute_hard_halt()

    def _execute_hard_halt(self):
        """No hay prompt de confirmación. No hay guardado en disco. Oscuridad."""
        self.is_dead = True
        print("[!] INICIANDO PURGA TÉRMICA DEL ENTORNO...")
        time.sleep(0.5) 
        self.SSR_RELAY.value(0) # 0 = Circuito Abierto. Corte físico de 220V.

# --- INICIALIZACIÓN FÍSICA ---
thermostat = WetwareThermostat()
keyboard_sensor = Pin(14, Pin.IN) # Sensor piezoeléctrico en el chasis del teclado
keyboard_sensor.irq(trigger=Pin.IRQ_FALLING, handler=thermostat.register_biometric_event)

print("[SYSTEM C6] Relé Armado. Que la termodinámica tenga piedad de tu hiperfoco.")
