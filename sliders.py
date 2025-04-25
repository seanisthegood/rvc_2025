import streamlit as st


def render_rank_sliders(candidates):
    rankings = {rank: {} for rank in range(1, 6)}

    st.markdown("### Rank-Based Sliders by Candidate")
    st.caption("Each column represents a candidate. Each column stacks sliders from Rank 1 to Rank 5 with locking under each slider.")

    # Track locking and values
    locked = {rank: {} for rank in range(1, 6)}
    values = {rank: {} for rank in range(1, 6)}
    remaining_display = {}

    for rank in range(1, 6):
        st.markdown(f"#### Rank {rank} Sliders")
        cols = st.columns(len(candidates))
        total_locked = 0

        for i, cand in enumerate(candidates):
            slider_key = f"rank_{rank}_{cand}"
            lock_key = f"lock_{rank}_{cand}"
            current_val = st.session_state.get(slider_key, 0)

            with cols[i]:
                lock_val = st.checkbox("Lock", key=lock_key)
                max_val = 100 if lock_val else max(0, 100 - total_locked)
                val = st.slider(f"{cand}", 0, max_val, current_val, key=slider_key)
                values[rank][cand] = val
                locked[rank][cand] = lock_val
                if lock_val:
                    total_locked += val

        remaining = max(0, 100 - total_locked)
        rankings[rank] = {c: values[rank][c] for c in candidates}
        remaining_display[rank] = remaining
        st.markdown(f"**Remaining % to allocate for Rank {rank}: {remaining_display[rank]}%**")

    return rankings
