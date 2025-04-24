
import streamlit as st
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt

st.set_page_config(page_title="2025 NYC RCV Simulator", layout="wide")

st.title("🗳️ 2025 NYC Democratic Mayoral Ranked Choice Voting Simulator")

# --- Candidates ---
candidates = [
    "Andrew Cuomo",
    "Zohran Mamdani",
    "Brad Lander",
    "Zellnor Myrie",
    "Scott Stringer",
    "Jessica Ramos",
    "Whitney Tilson"
]

# --- Input Parameters ---
st.sidebar.header("Input Vote Share")
st.sidebar.markdown("Enter the **first-choice** vote percentages for each candidate (must total 100%)")

percentages = {}
total_votes = st.sidebar.number_input("Total number of voters", min_value=1000, step=1000, value=100000)

default_dist = [25, 20, 15, 10, 10, 10, 10]  # Example values

for i, cand in enumerate(candidates):
    percentages[cand] = st.sidebar.number_input(f"{cand} (%)", min_value=0.0, max_value=100.0, value=float(default_dist[i]))

if sum(percentages.values()) != 100:
    st.sidebar.warning("Total must equal 100%")

# --- Generate Ballots Based on Percentages ---
def generate_ballots_from_percentages(pct_dict, total):
    import random
    ballots = []
    for cand, pct in pct_dict.items():
        count = int((pct / 100.0) * total)
        for _ in range(count):
            others = [c for c in candidates if c != cand]
            random.shuffle(others)
            ballots.append([cand] + others)
    return ballots

# --- RCV Logic ---
def run_rcv(ballots):
    rounds = []
    active = candidates.copy()
    eliminated = []

    def count_votes(ballots, active):
        counts = Counter()
        for ballot in ballots:
            for choice in ballot:
                if choice in active:
                    counts[choice] += 1
                    break
        return counts

    total_votes = len(ballots)

    while True:
        round_counts = count_votes(ballots, active)
        rounds.append(round_counts.copy())

        # Check for winner
        for cand, count in round_counts.items():
            if count > total_votes / 2:
                return rounds, cand

        # Eliminate lowest
        min_votes = min(round_counts.values())
        lowest = [cand for cand, v in round_counts.items() if v == min_votes]

        # If tie for lowest, eliminate alphabetically
        to_eliminate = sorted(lowest)[0]
        active.remove(to_eliminate)
        eliminated.append(to_eliminate)

        if len(active) == 1:
            rounds.append(Counter({active[0]: total_votes}))
            return rounds, active[0]

# --- Run Simulation ---
if st.sidebar.button("Run Simulation") and sum(percentages.values()) == 100:
    ballots = generate_ballots_from_percentages(percentages, total_votes)
    rcv_rounds, winner = run_rcv(ballots)

    st.markdown(f"### ✅ Winner: **{winner}**")

    round_df = pd.DataFrame(rcv_rounds).fillna(0).astype(int)
    round_df.index.name = "Round"
    st.bar_chart(round_df)
    st.dataframe(round_df.style.highlight_max(axis=1, color="lightgreen"))
