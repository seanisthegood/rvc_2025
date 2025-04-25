import streamlit as st
import plotly.graph_objects as go

def render_sankey(transfers, candidates):
    labels = []
    label_map = {}
    source, target, value = [], [], []

    def get_label_index(label):
        if label not in label_map:
            label_map[label] = len(labels)
            labels.append(label)
        return label_map[label]

    for t in transfers:
        from_node = f"{t['from']} (R{t['round']})"
        src_idx = get_label_index(from_node)
        for to_cand, count in t["to"].items():
            to_node = to_cand if to_cand == "Exhausted" else f"{to_cand} (R{t['round']+1})"
            tgt_idx = get_label_index(to_node)
            source.append(src_idx)
            target.append(tgt_idx)
            value.append(count)

    st.markdown("### Vote Transfers Through Rounds")
    fig = go.Figure(data=[go.Sankey(
        node=dict(label=labels, pad=15, thickness=20),
        link=dict(source=source, target=target, value=value)
    )])
    fig.update_layout(title_text="RCV Vote Flow", font_size=10)
    st.plotly_chart(fig, use_container_width=True)
