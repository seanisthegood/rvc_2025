import streamlit as st
import random
from collections import Counter, defaultdict
import plotly.graph_objects as go

st.set_page_config(page_title="RCV Simulator: Rank Distribution", layout="wide")

st.title("2025 NYC RCV Simulator – Rank-Based Vote Modeling")

# Define candidates
candidates = ["Cuomo", "Zohran", "Lander", "Ramos", "Stringer"]
rankings = {}  # rank number -> {candidate: %}

# Let user use sliders for any candidate and auto-redistribute remaining to unedited ones
for rank in range(1, 6):
    st.markdown(f"### {rank} Choice Distribution (Flexible + Redistributive with Sliders)")
    manual_inputs = {}
    total_so_far = 0
    cols = st.columns(len(candidates))

    for i, cand in enumerate(candidates):
        manual_inputs[cand] = cols[i].slider(
            f"{cand} %", min_value=0, max_value=100, value=0, step=1, key=f"rank_{rank}_{cand}"
        )
        total_so_far += manual_inputs[cand]

    remaining = max(0, 100 - total_so_far)
    unset_candidates = [c for c in candidates if manual_inputs[c] == 0]
    rank_pct = {}

    if unset_candidates:
        even_share = remaining // len(unset_candidates)
        for cand in candidates:
            if manual_inputs[cand] > 0:
                rank_pct[cand] = manual_inputs[cand]
            else:
                rank_pct[cand] = even_share

        diff = 100 - sum(rank_pct.values())
        if diff != 0:
            rank_pct[unset_candidates[-1]] += diff
    else:
        rank_pct = manual_inputs

    rankings[rank] = rank_pct
    st.write(rank_pct)

st.markdown("---")
st.markdown("✅ You can now assign any % per candidate using sliders, and the rest auto-balance among unassigned.")

# Display table summary
st.markdown("### Summary Table")
st.dataframe(rankings)

# --- Generate Ballots ---
num_ballots = st.slider("Number of simulated voters", 100, 5000, 1000, step=100)
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
            winner = max(counts.items(), key=lambda x: x[1])
            st.success(f"🏆 Winner: {winner[0]} with {winner[1]} votes")
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
