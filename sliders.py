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
        for i, cand in enumerate(candidates):
            with cols[i]:
                slider_key = f"rank_{rank}_{cand}"
                lock_key = f"lock_{rank}_{cand}"
                val = st.session_state.get(slider_key, 0)
                val = st.slider(f"{cand}", 0, 100, val, key=slider_key)
                lock_val = st.checkbox("Lock", key=lock_key)
                values[rank][cand] = val
                locked[rank][cand] = lock_val

        # Normalize sliders per rank
        manual_inputs = {}
        total_locked = sum(values[rank][c] for c in candidates if locked[rank][c])
        remaining = max(0, 100 - total_locked)

        for cand in candidates:
            if locked[rank][cand]:
                manual_inputs[cand] = values[rank][cand]
            else:
                max_val = max(0, min(100, remaining + values[rank][cand]))
                val = min(values[rank][cand], max_val)
                manual_inputs[cand] = val

        # Enforce 100% cap
        unlocked = [c for c in candidates if not locked[rank][c]]
        total_unlocked = sum(manual_inputs[c] for c in unlocked)
        overage = max(0, total_locked + total_unlocked - 100)
        if overage > 0 and total_unlocked > 0:
            for c in unlocked:
                prop = manual_inputs[c] / total_unlocked
                manual_inputs[c] = max(0, manual_inputs[c] - round(overage * prop))

        final_total = sum(manual_inputs.values()) + total_locked
        remaining_display[rank] = max(0, 100 - final_total)
        st.markdown(f"**Remaining % to allocate for Rank {rank}: {remaining_display[rank]}%**")
        rankings[rank] = manual_inputs.copy()

    return rankings
