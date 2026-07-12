import sys
import collections

N = 4
F = 1
L_PRE = "📢"
L_PRP = "🛡️"
L_CMT = "✅"
L_REP = "📤"
L_OK = "📦🧠⚡"
L_BAD = "📦🧠💀"


class PBFTNetwork:
    def __init__(self, primary_id, byzantine_config) -> "Any":
        self.primary = primary_id
        self.byzantine = byzantine_config
        self.logs = {i: [] for i in range(N)}
        self.prepares = {i: [] for i in range(N)}
        self.commits = {i: [] for i in range(N)}
        self.executed = {i: None for i in range(N)}

    def simulate_round(self) -> "Any":
        sys.stdout.write("  [ 1. PRE-PREPARE ]\n")
        for target in range(N):
            if target == self.primary:
                continue
            payload = L_OK
            if self.byzantine.get(self.primary) == "PRIMARY_SPLIT_BRAIN":
                payload = L_OK if target % 2 == 0 else L_BAD
            msg = f"{L_PRE}{payload}"
            self.logs[target].append((self.primary, msg))
            sys.stdout.write(f"    N{self.primary} -> N{target} :: {msg}\n")
        sys.stdout.write("  [ 2. PREPARE ]\n")
        for i in range(N):
            if i == self.primary:
                continue
            received_pre_prepare = [
                m[1][1:] for m in self.logs[i] if m[1].startswith(L_PRE)
            ]
            if not received_pre_prepare:
                continue
            payload_to_prepare = received_pre_prepare[0]
            if self.byzantine.get(i) == "REPLICA_LIAR":
                payload_to_prepare = L_BAD
            msg = f"{L_PRP}{payload_to_prepare}"
            for target in range(N):
                self.prepares[target].append((i, msg))
            sys.stdout.write(f"    N{i} broadcasts :: {msg}\n")
        sys.stdout.write("  [ 3. COMMIT ]\n")
        for i in range(N):
            counts = collections.Counter([m[1][1:] for m in self.prepares[i]])
            for payload, count in counts.items():
                if count >= 2 * F:
                    msg = f"{L_CMT}{payload}"
                    for target in range(N):
                        self.commits[target].append((i, msg))
                    sys.stdout.write(
                        f"    N{i} broadcasts :: {msg} (Quorum de Prepare alcanzado)\n"
                    )
                    break
        sys.stdout.write("  [ 4. EXECUTE & REPLY ]\n")
        for i in range(N):
            counts = collections.Counter([m[1][1:] for m in self.commits[i]])
            executed = False
            for payload, count in counts.items():
                if count >= 2 * F + 1:
                    self.executed[i] = payload
                    sys.stdout.write(f"    N{i} EXECUTES :: {L_REP}{payload}\n")
                    executed = True
                    break
            if not executed:
                sys.stdout.write(f"    N{i} HALTS :: Sin Quorum de Commit\n")
        exec_counts = collections.Counter(self.executed.values())
        for payload, count in exec_counts.items():
            if count >= F + 1 and payload is not None:
                return f"✅ CONSENSUS_REACHED ({payload})"
        return "❌ CONSENSUS_FAILED"


if __name__ == "__main__":
    sys.stdout.write("❖ [ C5-DAEMON-CORE :: PBFT EMOJI ENGINE (EXERGY) ] ❖\n\n")
    scenarios = [
        ("Nominal (Cero Fallas)", 0, {}),
        ("Falla Bizantina (Replica Miente)", 0, {2: "REPLICA_LIAR"}),
        ("Falla Bizantina Primaria (Split Brain)", 0, {0: "PRIMARY_SPLIT_BRAIN"}),
    ]
    for name, primary, config in scenarios:
        sys.stdout.write(f"=== SCENARIO: {name} ===\n")
        net = PBFTNetwork(primary, config)
        result = net.simulate_round()
        sys.stdout.write(f"\n[ GLOBAL STATE ] -> {result}\n\n")
