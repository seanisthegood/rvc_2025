import streamlit as st


def render_rank_sliders(candidates):
    rankings = {rank: {} for rank in range(1, 6)}

    st.markdown("### Rank-Based Sliders by Candidate")
    st.caption("Each column represents a candidate. Each column stacks sliders from Rank 1 to Rank 5 with locking per slider.")

    # Track locking and values
    locked = {rank: {} for rank in range(1, 6)}
    values = {rank: {} for rank in range(1, 6)}

    cols = st.columns(len(candidates))
    for i, cand in enumerate(candidates):
        with cols[i]:
            st.markdown(f"### {cand}")
            for rank in range(1, 6):
                slider_key = f"rank_{rank}_{cand}"
                lock_key = f"lock_{rank}_{cand}"
                values[rank][cand] = st.session_state.get(slider_key, 0)
                locked[rank][cand] = st.checkbox("Lock", key=lock_key)
                if locked[rank][cand]:
                    st.session_state[slider_key] = values[rank][cand]
                    st.markdown(f"**Rank {rank}: {values[rank][cand]}% (locked)**")
                else:
                    st.markdown(f"Rank {rank}")
                    values[rank][cand] = st.slider(" ", 0, 100, values[rank][cand], key=slider_key)

    # Normalize sliders per rank
    for rank in range(1, 6):
        manual_inputs = {}
        total_locked = sum(values[rank][c] for c in candidates if locked[rank][c])
        remaining = max(0, 100 - total_locked)

        for cand in candidates:
            slider_key = f"rank_{rank}_{cand}"
            if locked[rank][cand]:
                manual_inputs[cand] = values[rank][cand]
            else:
                max_val = max(0, min(100, remaining + values[rank][cand]))
                val = min(values[rank][cand], max_val)
                manual_inputs[cand] = val
                st.session_state[slider_key] = val

        # Enforce 100% cap
        unlocked = [c for c in candidates if not locked[rank][c]]
        total_unlocked = sum(manual_inputs[c] for c in unlocked)
        overage = max(0, total_locked + total_unlocked - 100)
        if overage > 0 and total_unlocked > 0:
            for c in unlocked:
                prop = manual_inputs[c] / total_unlocked
                new_val = max(0, manual_inputs[c] - round(overage * prop))
                manual_inputs[c] = new_val
                st.session_state[f"rank_{rank}_{c}"] = new_val

        final_total = sum(manual_inputs.values()) + total_locked
        st.markdown(f"**Remaining % to allocate for Rank {rank}: {max(0, 100 - final_total)}%**")
        rankings[rank] = {cand: manual_inputs[cand] for cand in candidates}

    return rankings

