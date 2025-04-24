import streamlit as st
from sliders import render_rank_sliders
from ballots import generate_ballots
from simulation import simulate_rcv_with_flow
from visualization import render_sankey

st.set_page_config(page_title="RCV Simulator: Rank Distribution", layout="wide")
st.title("2025 NYC RCV Simulator – Rank-Based Vote Modeling")

candidates = ["Cuomo", "Zohran", "Lander", "Ramos", "Stringer"]
rankings = render_rank_sliders(candidates)

st.markdown("---")
st.markdown("✅ Locked sliders are now static. Unlocked sliders strictly capped by remaining %.")

num_ballots = st.slider("Number of simulated voters", 100, 5000, 1000, step=100)
ballots = generate_ballots(rankings, candidates, num_ballots)
transfers = simulate_rcv_with_flow(ballots, candidates)
render_sankey(transfers, candidates)