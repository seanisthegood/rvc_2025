import streamlit as st


def render_rank_sliders(candidates):
    rankings = {}
    for rank in range(1, 6):
        st.markdown(f"### Rank {rank} Distribution (Lockable + Redistributive Sliders)")
        st.caption("Each row must total 100%. Locked sliders cannot be moved; remaining % is auto-distributed across unlocked sliders.")

        manual_inputs = {}
        locked = {}

        cols = st.columns(len(candidates))

        # First: draw lock checkboxes
        for i, cand in enumerate(candidates):
            with cols[i]:
                locked[cand] = st.checkbox(f"Lock {cand}", key=f"lock_{rank}_{cand}")

        # Load stored values
        all_values = {cand: st.session_state.get(f"rank_{rank}_{cand}", 0) for cand in candidates}
        total_locked = sum(all_values[cand] for cand in candidates if locked[cand])
        remaining = max(0, 100 - total_locked)

        # Now draw sliders per candidate (columns)
        for i, cand in enumerate(candidates):
            with cols[i]:
                key = f"rank_{rank}_{cand}"
                if locked[cand]:
                    manual_inputs[cand] = all_values[cand]
                    st.session_state[key] = all_values[cand]
                    st.markdown(f"**{cand} %: {manual_inputs[cand]} (locked)**")
                else:
                    max_val = max(0, min(100, remaining))
                    default_val = min(all_values[cand], max_val)
                    manual_inputs[cand] = st.slider(" ", 0, max_val, default_val, key=key)

        total_all = sum(manual_inputs.values())
        remaining = max(0, 100 - total_all)
        st.markdown(f"**Remaining % to allocate: {remaining}%**")

        rankings[rank] = manual_inputs.copy()
    return rankings
