import random

def generate_ballots(rankings, candidates, num_ballots):
    ballots = []
    for _ in range(num_ballots):
        ballot = [None] * 5
        available = candidates[:]
        for rank in range(1, 6):
            weights = [(cand, rankings[rank][cand]) for cand in available if rankings[rank][cand] > 0]
            if not weights:
                break
            names, probs = zip(*weights)
            choice = random.choices(names, weights=probs, k=1)[0]
            ballot[rank - 1] = choice
            available.remove(choice)
        ballots.append([c for c in ballot if c])
    return ballots
