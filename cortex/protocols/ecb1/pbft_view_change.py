import sys
import collections

N = 4
F = 1
L_PRE = "📢"
L_PRP = "🛡️"
L_VWC = "🔄"
L_NWV = "👑"


class PBFTNetwork:
    def __init__(self) -> "Any":
        self.view = 0
        self.logs = {i: [] for i in range(N)}

    def get_primary(self) -> "Any":
        return self.view % N

    def simulate_view_change_round(self) -> "Any":
        primary = self.get_primary()
        sys.stdout.write(f"\n❖ [ VISTA ACTUAL: {self.view} | LÍDER: N{primary} ] ❖\n")
        sys.stdout.write("  [ 1. PRE-PREPARE ]\n")
        payloads = ["📦🧠⚡", "📦🧠💀", "📦🧠🩸"]
        target_idx = 0
        for target in range(N):
            if target == primary:
                continue
            payload = payloads[target_idx]
            target_idx += 1
            msg = f"{L_PRE}{payload}"
            self.logs[target].append((primary, msg))
            sys.stdout.write(f"    N{primary} -> N{target} :: {msg}\n")
        sys.stdout.write("  [ 2. PREPARE ]\n")
        prepares = {i: [] for i in range(N)}
        for i in range(N):
            if i == primary:
                continue
            recv_pre = [m[1][1:] for m in self.logs[i] if m[1].startswith(L_PRE)]
            if not recv_pre:
                continue
            msg = f"{L_PRP}{recv_pre[0]}"
            for target in range(N):
                prepares[target].append((i, msg))
            sys.stdout.write(f"    N{i} broadcasts :: {msg}\n")
        sys.stdout.write("  [ 3. DETECCIÓN DE DIVERGENCIA ]\n")
        quorum_reached = False
        for i in range(N):
            if i == primary:
                continue
            counts = collections.Counter([m[1][1:] for m in prepares[i]])
            max_count = max(counts.values()) if counts else 0
            if max_count < 2 * F:
                sys.stdout.write(
                    f"    N{i} TIMEOUT :: Fallo de Quórum en Prepare ({max_count}/{2 * F})\n"
                )
            else:
                quorum_reached = True
        if not quorum_reached:
            sys.stdout.write("\n  [ 4. VIEW CHANGE TRIGGERS ]\n")
            view_changes = {i: [] for i in range(N)}
            new_view = self.view + 1
            new_primary = new_view % N
            for i in range(N):
                if i == primary:
                    continue
                msg = f"{L_VWC}v{new_view}"
                for target in range(N):
                    view_changes[target].append((i, msg))
                sys.stdout.write(f"    N{i} broadcasts :: {msg}\n")
            sys.stdout.write("\n  [ 5. NEW VIEW ]\n")
            vc_count = len(view_changes[new_primary])
            if vc_count >= 2 * F:
                msg = f"{L_NWV}v{new_view}"
                sys.stdout.write(
                    f"    N{new_primary} asume Liderazgo y broadcasts :: {msg}\n"
                )
                self.view = new_view
                return "✅ VIEW_CHANGE_SUCCESS"
        return "❌ CONSENSUS_STALLED"


if __name__ == "__main__":
    sys.stdout.write("❖ [ C5-DAEMON-CORE :: PBFT VIEW CHANGE (LEADER ROTATION) ] ❖\n")
    net = PBFTNetwork()
    result = net.simulate_view_change_round()
    sys.stdout.write(f"\n[ GLOBAL STATE ] -> {result}\n\n")
    if "SUCCESS" in result:
        sys.stdout.write(
            f"El Líder Bizantino (N0) ha sido depuesto. La red opera ahora bajo la Vista {net.view} con Líder N{net.get_primary()}.\n"
        )
