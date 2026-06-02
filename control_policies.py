import random

# Store and retrieval policies

def get_random_idx(lst):
    """Selects a random index from the list."""
    return random.randrange(len(lst))

def get_FCFS_idx(lst):
    """Selects the first element from the list. Works as FCFS policy."""
    return 0

def get_closest_idx(lst):
    """Selects the index of the item with the nearest Aisle, ties are broken by nearest Tier. Ties are broken by nearest Column."""
    return lst.index(min(lst))

def get_emptiest_fullest_tier_idx(lst):
    """Selects the index of the item on the tier with most occurrences. It is the emptiest tier for storage or fullest tier for retrieval. Ties are broken by random choice."""
    tier_counts = {}
    for slot in lst:
        a, t, _, _ = slot
        tier_counts[(a, t)] = tier_counts.get((a, t), 0) + 1
    max_count = max(tier_counts.values())
    best_pairs = [key for key, count in tier_counts.items() if count == max_count]
    target_aisle, target_tier = random.choice(best_pairs)
    valid_indices = [i for i, s in enumerate(lst) if s[0] == target_aisle and s[1] == target_tier]
    return random.choice(valid_indices)

def get_lowest_tier_idx(lst):
    """Selects the index of the item on the lowest tier. Ties are broken by FCFS policy."""
    return min(range(len(lst)), key=lambda i: lst[i][1])

def get_closest_column_idx(lst):
    """Selects the index of the item on the nearest column. Ties are broken by FCFS policy."""
    return min(range(len(lst)), key=lambda i: lst[i][2])


# Lift policies

def get_tier_fcfs(queues, current_tier=0):
    """Selects the index of the non-empty tier with the tote that has been waiting the longest."""
    candidates = [(i, q[0][1]) for i, q in enumerate(queues) if len(q) > 0]
    return min(candidates, key=lambda x: x[1])[0] if candidates else None

def get_tier_shortest(queues, current_tier=0):
    """Selects the index of the non-empty tier closest to the current position. Ties are broken by the lowest tier."""
    candidates = [i for i, q in enumerate(queues) if len(q) > 0]
    if not candidates: return None
    min_dist = min(abs(i - current_tier) for i in candidates)
    tied = [i for i in candidates if abs(i - current_tier) == min_dist]
    return min(tied)

def get_tier_farthest(queues, current_tier=0):
    """Selects the index of the non-empty tier farthest to the current position. Ties are broken by the highest tier."""
    candidates = [i for i, q in enumerate(queues) if len(q) > 0]
    if not candidates: return None
    max_dist = max(abs(i - current_tier) for i in candidates)
    tied = [i for i in candidates if abs(i - current_tier) == max_dist]
    return max(tied)

def get_tier_most_loaded(queues, current_tier=0):
    """Selects the index of non-empty tier with the most totes waiting. Ties are broken by the lowest tier."""
    candidates = [i for i, q in enumerate(queues) if len(q) > 0]
    if not candidates: return None
    max_load = max(len(queues[i]) for i in candidates)
    tied = [i for i in candidates if len(queues[i]) == max_load]
    return min(tied)

def get_tier_least_loaded(queues, current_tier=0):
    """Selects the index of non-empty tier with the fewest totes waiting. Ties are broken by the lowest tier."""
    candidates = [i for i, q in enumerate(queues) if len(q) > 0]
    if not candidates: return None
    min_load = min(len(queues[i]) for i in candidates)
    tied = [i for i in candidates if len(queues[i]) == min_load]
    return min(tied)

def get_tier_lowest(queues, current_tier=0):
    """Selects the index of the lowest non-empty tier."""
    for i, q in enumerate(queues):
        if len(q) > 0: return i
    return None

def get_tier_highest(queues, current_tier=0):
    """Selects the index of the highest non-empty tier."""
    for i in range(len(queues) - 1, -1, -1):
        if len(queues[i]) > 0: return i
    return None

def get_tier_weighted(queues, current_tier=0):
    """Selects the index of the non-empty tier with the highest score: quantity / (distance + 1). Ties are broken by the lowest tier."""
    candidates = [i for i, q in enumerate(queues) if len(q) > 0]
    if not candidates: return None
    max_score = max(len(queues[i]) / (abs(i - current_tier) + 1) for i in candidates)
    tied = [i for i in candidates if len(queues[i]) / (abs(i - current_tier) + 1) == max_score]
    return min(tied)


# Vehicle policies

def get_column_fcfs(xs, current_column=0):
    """Selects the first element from the list. Works as FCFS policy."""
    return 0

def get_column_lcls(xs, current_column=0):
    """Selects the last element from the list. Works as LCFS policy."""
    return len(xs) - 1  # último da fila

def get_column_shortest(xs, current_column=0):
    """Selects the index of the item in the column closest to the current position. Ties are broken by FCFS policy."""
    return min(range(len(xs)), key=lambda i: abs(xs[i].column - current_column))

def get_column_farthest(xs, current_column=0):
    """Selects the index of the item in the column farthest to the current position. Ties are broken by LCFS policy."""
    return max(range(len(xs)), key=lambda i: abs(xs[i].column - current_column))

def get_column_retrieval_first(xs, current_column=0):
    """Selects the index of the item to retrieve in the column closest to the current position. Ties are broken by FCFS policy."""
    retrievals = [i for i, x in enumerate(xs) if not x.is_storage]
    if retrievals:
        return min(retrievals, key=lambda i: abs(xs[i].column - current_column))
    return min(range(len(xs)), key=lambda i: abs(xs[i].column - current_column))

def get_column_storage_first(xs, current_column=0):
    """Selects the index of the item to store in the column closest to the current position. Ties are broken by FCFS policy."""
    storages = [i for i, x in enumerate(xs) if x.is_storage]
    if storages:
        return min(storages, key=lambda i: abs(xs[i].column - current_column))
    return min(range(len(xs)), key=lambda i: abs(xs[i].column - current_column))


store_policies = [
    get_random_idx, # 0
    get_FCFS_idx, # 1
    get_closest_idx, # 2
    get_emptiest_fullest_tier_idx, # 3
    get_lowest_tier_idx, # 4
    get_closest_column_idx # 5
    ]
retrieval_policies = [
    get_random_idx, # 0
    get_FCFS_idx, # 1
    get_closest_idx, # 2
    get_emptiest_fullest_tier_idx, # 3
    get_lowest_tier_idx, # 4
    get_closest_column_idx # 5
    ]
lift_policies = [
    get_tier_fcfs, # 0
    get_tier_shortest, # 1 
    get_tier_farthest, # 2
    get_tier_most_loaded, # 3
    get_tier_least_loaded, # 4
    get_tier_lowest, # 5
    get_tier_highest, # 6
    get_tier_weighted # 7
    ]
vehicle_policies = [
    get_column_fcfs, # 0
    get_column_lcls, # 1
    get_column_shortest, # 2
    get_column_farthest, # 3
    get_column_retrieval_first, # 4
    get_column_storage_first # 5
    ]
