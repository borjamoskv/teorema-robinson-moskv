# -*- coding: utf-8 -*-
"""
Substack Coordinated Inauthentic Behavior (CIB) Network OSINT Tool
Fuses Jaccard similarity, temporal synchronization, and coordination metrics to analyze interaction loops.
Based on the Pacheco et al. and NATO HCC framework.
"""
import json
import math
import hashlib
from collections import defaultdict

def shannon_entropy(timestamps):
    if not timestamps:
        return 0.0
    # Bin timestamps into 10-minute intervals to find alignment
    binned = [t // 600 for t in timestamps]
    freq = defaultdict(int)
    for b in binned:
        freq[b] += 1
    total = len(binned)
    return -sum((count / total) * math.log2(count / total) for count in freq.values())

def jaccard_similarity(set_a, set_b):
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return intersection / union

def anonymize_user(handle):
    return hashlib.sha256(handle.encode('utf-8')).hexdigest()[:16]

def analyze_cib_network(interactions, anonymize=False):
    """
    interactions: list of dict:
        - 'note_id': identifier of the note
        - 'author': author of the note
        - 'interactor': account commenting/liking
        - 'timestamp': epoch seconds
    """
    all_interactors = set()
    user_to_notes_liked = defaultdict(set)
    user_to_timestamps = defaultdict(list)
    note_to_interactors = defaultdict(set)
    author_interactors = defaultdict(set)
    
    for inter in interactions:
        author = inter['author']
        interactor = inter['interactor']
        note_id = inter['note_id']
        ts = inter['timestamp']
        
        if anonymize:
            interactor = anonymize_user(interactor)
            author = anonymize_user(author)
            note_id = anonymize_user(str(note_id))
            
        all_interactors.add(interactor)
        user_to_notes_liked[interactor].add(note_id)
        user_to_timestamps[interactor].append(ts)
        note_to_interactors[note_id].add(interactor)
        author_interactors[author].add(interactor)

    # Calculate Jaccard similarity matrix between interactors (behavioral lockstep)
    interactors_list = list(all_interactors)
    coordination_links = []
    
    for i in range(len(interactors_list)):
        for j in range(i+1, len(interactors_list)):
            u1 = interactors_list[i]
            u2 = interactors_list[j]
            
            j_score = jaccard_similarity(user_to_notes_liked[u1], user_to_notes_liked[u2])
            
            # If Jaccard similarity is high, they like the exact same notes
            if j_score > 0.6:
                coordination_links.append({
                    "user_a": u1,
                    "user_b": u2,
                    "jaccard_similarity": round(j_score, 3)
                })

    # Individual Anomaly Scoring
    user_profiles = []
    for user in all_interactors:
        ts_list = user_to_timestamps[user]
        entropy = shannon_entropy(ts_list)
        
        # Reciprocal interaction with other users
        notes_liked = user_to_notes_liked[user]
        total_interactions = len(ts_list)
        
        # Burstiness (how fast they interact on notes)
        # Low entropy of temporal spacing means they post in highly binned/synchronized slots
        anomaly_score = (1.0 - (entropy / 10.0)) * total_interactions
        
        user_profiles.append({
            "user": user,
            "total_interactions": total_interactions,
            "temporal_entropy": round(entropy, 3),
            "coordination_anomaly_score": round(anomaly_score, 3)
        })

    return {
        "coordination_links": sorted(coordination_links, key=lambda x: x['jaccard_similarity'], reverse=True),
        "anomalies": sorted(user_profiles, key=lambda x: x['coordination_anomaly_score'], reverse=True)
    }

if __name__ == "__main__":
    # Test script with mock coordinated cohort
    mock_interactions = []
    
    # 20 notes published by David
    # Coordinated cohort (10 users) liking every note simultaneously
    cohort = [f"pod_member_{i}" for i in range(10)]
    for note_idx in range(20):
        note_id = f"note_{note_idx}"
        for idx, member in enumerate(cohort):
            # Synchronized timestamp (within 2 minutes of each other)
            ts = 1720720000 + (note_idx * 3600) + (idx * 15)
            mock_interactions.append({
                "note_id": note_id,
                "author": "david_crecer",
                "interactor": member,
                "timestamp": ts
            })
            
    # Organic interactors (sporadic, different notes, high entropy)
    for org_idx in range(5):
        org_name = f"organic_{org_idx}"
        for note_idx in [2, 5, 12]:
            ts = 1720720000 + (note_idx * 3600) + 1200 + (org_idx * 600)
            mock_interactions.append({
                "note_id": f"note_{note_idx}",
                "author": "david_crecer",
                "interactor": org_name,
                "timestamp": ts
            })

    analysis = analyze_cib_network(mock_interactions, anonymize=True)
    print("--- DETECTED BEHAVIORAL LOCKSTEP LINKS (SHA256 ANONYMIZED) ---")
    print(json.dumps(analysis["coordination_links"][:5], indent=2))
    print("\n--- ANOMALOUS INTERACTOR PROFILES ---")
    print(json.dumps(analysis["anomalies"][:5], indent=2))
