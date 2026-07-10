import sys
import collections

# ❖ PBFT EMOJI CONSENSUS ENGINE (C5-REAL) ❖
# Implementación estricta de 3 fases (Pre-Prepare, Prepare, Commit)

N = 4  # Total Nodos
F = 1  # Tolerancia Bizantina (N >= 3f + 1)

# Léxico PBFT
L_PRE = "📢"  # Pre-Prepare
L_PRP = "🛡️"  # Prepare
L_CMT = "✅"  # Commit
L_REP = "📤"  # Reply (Executed)
L_OK  = "📦🧠⚡" # Payload Nominal
L_BAD = "📦🧠💀" # Payload Corrupto

class PBFTNetwork:
    def __init__(self, primary_id, byzantine_config):
        self.primary = primary_id
        self.byzantine = byzantine_config # dict: {node_id: 'BEHAVIOR'}
        self.logs = {i: [] for i in range(N)}
        self.prepares = {i: [] for i in range(N)}
        self.commits = {i: [] for i in range(N)}
        self.executed = {i: None for i in range(N)}
        
    def simulate_round(self):
        sys.stdout.write("  [ 1. PRE-PREPARE ]\n")
        # El Primary envía PRE-PREPARE
        for target in range(N):
            if target == self.primary: continue
            
            payload = L_OK
            # Comportamiento Bizantino: El Primary miente a nodos específicos
            if self.byzantine.get(self.primary) == "PRIMARY_SPLIT_BRAIN":
                payload = L_OK if target % 2 == 0 else L_BAD
                
            msg = f"{L_PRE}{payload}"
            self.logs[target].append((self.primary, msg))
            sys.stdout.write(f"    N{self.primary} -> N{target} :: {msg}\n")
            
        sys.stdout.write("  [ 2. PREPARE ]\n")
        # Replicas validan y emiten PREPARE a todos
        for i in range(N):
            if i == self.primary: continue
            
            # Qué recibió?
            received_pre_prepare = [m[1][1:] for m in self.logs[i] if m[1].startswith(L_PRE)]
            if not received_pre_prepare: continue
            
            payload_to_prepare = received_pre_prepare[0]
            
            # Comportamiento Bizantino: Replica miente
            if self.byzantine.get(i) == "REPLICA_LIAR":
                payload_to_prepare = L_BAD
                
            msg = f"{L_PRP}{payload_to_prepare}"
            for target in range(N):
                self.prepares[target].append((i, msg))
            sys.stdout.write(f"    N{i} broadcasts :: {msg}\n")

        sys.stdout.write("  [ 3. COMMIT ]\n")
        # Nodos emiten COMMIT si tienen >= 2f PREPARES coincidentes
        for i in range(N):
            # Contar prepares
            counts = collections.Counter([m[1][1:] for m in self.prepares[i]])
            for payload, count in counts.items():
                if count >= 2 * F: # Condición PBFT (2f)
                    msg = f"{L_CMT}{payload}"
                    for target in range(N):
                        self.commits[target].append((i, msg))
                    sys.stdout.write(f"    N{i} broadcasts :: {msg} (Quorum de Prepare alcanzado)\n")
                    break

        sys.stdout.write("  [ 4. EXECUTE & REPLY ]\n")
        # Ejecutan si tienen >= 2f+1 COMMITS coincidentes
        for i in range(N):
            counts = collections.Counter([m[1][1:] for m in self.commits[i]])
            executed = False
            for payload, count in counts.items():
                if count >= 2 * F + 1: # Condición PBFT (2f+1)
                    self.executed[i] = payload
                    sys.stdout.write(f"    N{i} EXECUTES :: {L_REP}{payload}\n")
                    executed = True
                    break
            if not executed:
                sys.stdout.write(f"    N{i} HALTS :: Sin Quorum de Commit\n")
                
        # Consenso final de la red
        exec_counts = collections.Counter(self.executed.values())
        for payload, count in exec_counts.items():
            if count >= F + 1 and payload is not None:
                return f"✅ CONSENSUS_REACHED ({payload})"
        return "❌ CONSENSUS_FAILED"

if __name__ == "__main__":
    sys.stdout.write("❖ [ C5-DAEMON-CORE :: PBFT EMOJI ENGINE (ULTRATHINK) ] ❖\n\n")
    
    scenarios = [
        ("Nominal (Cero Fallas)", 0, {}),
        ("Falla Bizantina (Replica Miente)", 0, {2: "REPLICA_LIAR"}),
        ("Falla Bizantina Primaria (Split Brain)", 0, {0: "PRIMARY_SPLIT_BRAIN"})
    ]
    
    for name, primary, config in scenarios:
        sys.stdout.write(f"=== SCENARIO: {name} ===\n")
        net = PBFTNetwork(primary, config)
        result = net.simulate_round()
        sys.stdout.write(f"\n[ GLOBAL STATE ] -> {result}\n\n")
