import streamlit as st


def render_rank_sliders(candidates):
    rankings = {}

    for rank in range(1, 6):
        st.markdown(f"### Rank {rank} Distribution (Lockable + Redistributive Sliders)")
        st.caption("Each row must total 100%. Locked sliders cannot be moved; remaining % is auto-distributed across unlocked sliders.")

        # Initialize state and layout
        locked = {}
        sliders = {}
        all_values = {}
        cols = st.columns(len(candidates))

        # First row: Lock checkboxes
        for i, cand in enumerate(candidates):
            with cols[i]:
                locked[cand] = st.checkbox(f"Lock {cand}", key=f"lock_{rank}_{cand}")

        # Load previous values and compute locked total
        for cand in candidates:
            key = f"rank_{rank}_{cand}"
            all_values[cand] = st.session_state.get(key, 0)

        total_locked = sum(all_values[cand] for cand in candidates if locked[cand])
        remaining = max(0, 100 - total_locked)

        # Second row: sliders
        for i, cand in enumerate(candidates):
            with cols[i]:
                key = f"rank_{rank}_{cand}"
                if locked[cand]:
                    sliders[cand] = all_values[cand]
                    st.session_state[key] = all_values[cand]
                    st.markdown(f"**{cand} %: {all_values[cand]} (locked)**")
                else:
                    max_val = max(0, min(100, remaining + all_values[cand]))
                    sliders[cand] = st.slider(" ", 0, max_val, all_values[cand], key=key)

        # Normalize to enforce 100% cap
        unlocked = [c for c in candidates if not locked[c]]
        total_unlocked = sum(sliders[c] for c in unlocked)
        overage = max(0, total_locked + total_unlocked - 100)
        if overage > 0 and total_unlocked > 0:
            for c in unlocked:
                proportion = sliders[c] / total_unlocked if total_unlocked else 0
                sliders[c] = max(0, sliders[c] - round(overage * proportion))
                st.session_state[f"rank_{rank}_{c}"] = sliders[c]

        # Display updated remaining
        final_total = sum(sliders.values()) + total_locked
        st.markdown(f"**Remaining % to allocate: {max(0, 100 - final_total)}%**")

        rankings[rank] = {cand: sliders[cand] for cand in candidates}

    return rankings

