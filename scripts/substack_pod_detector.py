import json
import math
from collections import defaultdict


def shannon_entropy(data: list) -> float:
    if not data:
        return 0.0
    freq = defaultdict(int)
    for item in data:
        freq[item] += 1
    total = len(data)
    return -sum((count / total * math.log2(count / total) for count in freq.values()))


def analyze_interactions(interactions) -> "Any":
    out_degrees = defaultdict(set)
    in_degrees = defaultdict(set)
    all_users = set()
    author_notes_timing = defaultdict(list)
    for inter in interactions:
        u1, u2 = (inter["author"], inter["interactor"])
        all_users.add(u1)
        all_users.add(u2)
        out_degrees[u2].add(u1)
        in_degrees[u1].add(u2)
        author_notes_timing[u1].append(inter["timestamp"])
    reciprocal_pairs = []
    users_list = list(all_users)
    for i in range(len(users_list)):
        for j in range(i + 1, len(users_list)):
            uA = users_list[i]
            uB = users_list[j]
            if uB in out_degrees[uA] and uA in out_degrees[uB]:
                reciprocal_pairs.append((uA, uB))
    anomalies = []
    for user in all_users:
        interacted_with = out_degrees[user]
        received_from = in_degrees[user]
        overlap = interacted_with.intersection(received_from)
        overlap_ratio = len(overlap) / max(1, len(interacted_with))
        ts_list = author_notes_timing[user]
        ent = shannon_entropy(ts_list) if ts_list else 10.0
        coordination_score = overlap_ratio * len(interacted_with)
        anomalies.append(
            {
                "user": user,
                "out_count": len(interacted_with),
                "in_count": len(received_from),
                "reciprocal_count": len(overlap),
                "reciprocity_ratio": round(overlap_ratio, 2),
                "entropy": round(ent, 3),
                "coordination_score": round(coordination_score, 2),
                "is_anomaly": coordination_score > 3.0 and ent < 4.0,
            }
        )
    return {
        "total_users": len(all_users),
        "reciprocal_pairs_count": len(reciprocal_pairs),
        "reciprocal_pairs": reciprocal_pairs,
        "anomalies": sorted(
            anomalies, key=lambda x: x["coordination_score"], reverse=True
        ),
    }


if __name__ == "__main__":
    mock_data = []
    pod_members = ["david_crecer", "user_A", "user_B", "user_C", "user_D", "user_E"]
    for member in pod_members:
        for target in pod_members:
            if member != target:
                mock_data.append(
                    {
                        "author": target,
                        "interactor": member,
                        "timestamp": 1720720000,
                        "type": "comment",
                    }
                )
                mock_data.append(
                    {
                        "author": target,
                        "interactor": member,
                        "timestamp": 1720720010,
                        "type": "like",
                    }
                )
    organic = ["organic_user_1", "organic_user_2", "organic_user_3"]
    for org in organic:
        mock_data.append(
            {
                "author": "david_crecer",
                "interactor": org,
                "timestamp": 1720731000,
                "type": "comment",
            }
        )
    result = analyze_interactions(mock_data)
    print(json.dumps(result, indent=2))
