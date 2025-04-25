import streamlit as st


def render_rank_sliders(candidates):
    rankings = {rank: {} for rank in range(1, 6)}

    st.markdown("### Rank-Based Sliders by Candidate")
    st.caption("Each row (rank) must total 100%. You can lock sliders, and remaining % is distributed across unlocked sliders.")

    # Build columns per candidate
    cols = st.columns(len(candidates))
    locked = {rank: {} for rank in range(1, 6)}
    values = {rank: {} for rank in range(1, 6)}

    for i, cand in enumerate(candidates):
        with cols[i]:
            st.markdown(f"### {cand}")
            for rank in range(1, 6):
                lock_key = f"lock_{rank}_{cand}"
                slider_key = f"rank_{rank}_{cand}"
                locked[rank][cand] = st.checkbox(f"Lock Rank {rank}", key=lock_key)
                values[rank][cand] = st.session_state.get(slider_key, 0)

    # Normalize sliders per rank
    for rank in range(1, 6):
        st.markdown(f"#### Rank {rank} Allocation")
        manual_inputs = {}
        rank_cols = st.columns(len(candidates))
        total_locked = sum(values[rank][c] for c in candidates if locked[rank][c])
        remaining = max(0, 100 - total_locked)

        for i, cand in enumerate(candidates):
            with rank_cols[i]:
                slider_key = f"rank_{rank}_{cand}"
                if locked[rank][cand]:
                    st.session_state[slider_key] = values[rank][cand]
                    st.markdown(f"**{values[rank][cand]}% (locked)**")
                    manual_inputs[cand] = values[rank][cand]
                else:
                    max_val = max(0, min(100, remaining + values[rank][cand]))
                    manual_inputs[cand] = st.slider(" ", 0, max_val, values[rank][cand], key=slider_key)

        # Recalculate and enforce total ≤ 100
        unlocked = [c for c in candidates if not locked[rank][c]]
        total_unlocked = sum(manual_inputs[c] for c in unlocked)
        overage = max(0, total_locked + total_unlocked - 100)
        if overage > 0 and total_unlocked > 0:
            for c in unlocked:
                prop = manual_inputs[c] / total_unlocked
                manual_inputs[c] = max(0, manual_inputs[c] - round(overage * prop))
                st.session_state[f"rank_{rank}_{c}"] = manual_inputs[c]

        final_total = sum(manual_inputs.values()) + total_locked
        st.markdown(f"**Remaining % to allocate: {max(0, 100 - final_total)}%**")
        rankings[rank] = {cand: manual_inputs[cand] for cand in candidates}

    return rankings

