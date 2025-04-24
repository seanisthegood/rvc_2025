import streamlit as st
import random
from collections import Counter, defaultdict
import plotly.graph_objects as go

st.set_page_config(page_title="RCV Simulator: Rank Distribution", layout="wide")

st.title("2025 NYC RCV Simulator – Rank-Based Vote Modeling")

# Define candidates
candidates = ["Cuomo", "Zohran", "Lander", "Ramos", "Stringer"]
rankings = {}  # rank number -> {candidate: %}

# Let user define % of voters giving each candidate a specific rank
for rank in range(1, 6):
    st.markdown(f"### {rank} Choice Distribution")
    cols = st.columns(len(candidates))
    rank_pct = {}
    for i, cand in enumerate(candidates):
        rank_pct[cand] = cols[i].slider(
            f"{cand}", 0, 100, 20, key=f"{cand}_r{rank}"
        )
    total = sum(rank_pct.values())
    if total != 100:
        st.error(f"Rank {rank} total must be 100%, but it is {total}%")
    rankings[rank] = rank_pct

st.markdown("---")
st.markdown("✅ Now you have defined what % of *all voters* rank each candidate in each position.")

# Display table summary
st.markdown("### Summary Table")
st.dataframe(rankings)

# --- Generate Ballots ---
num_ballots = 1000
ballots = []

# Create ballots based on the rank distribution
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

# --- RCV Simulation with Flow Tracking ---
def simulate_rcv_with_flow(ballots, candidates):
    remaining = set(candidates)
    transfer_log = []
    round_num = 1
    current_ballots = ballots[:]

    while True:
        counts = Counter()
        for b in current_ballots:
            for c in b:
                if c in remaining:
                    counts[c] += 1
                    break

        total_votes = sum(counts.values())
        if not total_votes:
            break

        if any(v > total_votes / 2 for v in counts.values()):
            break

        eliminated = min((c for c in remaining), key=lambda c: counts[c])
        remaining.remove(eliminated)

        transfer = defaultdict(int)
        for b in current_ballots:
            if b and b[0] == eliminated:
                for c in b[1:]:
                    if c in remaining:
                        transfer[c] += 1
                        break
                else:
                    transfer["Exhausted"] += 1

        for b in current_ballots:
            if eliminated in b:
                b.remove(eliminated)

        transfer_log.append({"round": round_num, "from": eliminated, "to": dict(transfer)})
        round_num += 1

    return transfer_log

# Run simulation and collect transfers
transfers = simulate_rcv_with_flow(ballots, candidates)

# Build Sankey Data
labels = candidates + ["Exhausted"]
label_index = {label: i for i, label in enumerate(labels)}
source, target, value = [], [], []

for t in transfers:
    src = label_index[t["from"]]
    for to_cand, count in t["to"].items():
        tgt = label_index[to_cand]
        source.append(src)
        target.append(tgt)
        value.append(count)

# Display Sankey Diagram
st.markdown("### Vote Transfers Through Rounds")
fig = go.Figure(data=[go.Sankey(
    node=dict(label=labels, pad=15, thickness=20),
    link=dict(source=source, target=target, value=value)
)])
fig.update_layout(title_text="RCV Vote Flow", font_size=10)
st.plotly_chart(fig, use_container_width=True)
