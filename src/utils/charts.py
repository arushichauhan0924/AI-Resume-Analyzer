import plotly.graph_objects as go


def score_gauge(value: float, title: str = "Overall Match") -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title},
        number={"suffix": "%"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#4F46E5"},
            "steps": [
                {"range": [0, 45], "color": "#FECACA"},
                {"range": [45, 70], "color": "#FEF08A"},
                {"range": [70, 100], "color": "#BBF7D0"},
            ],
        },
    ))
    fig.update_layout(height=300, margin=dict(t=60, b=10, l=20, r=20))
    return fig


def scores_bar(labels: list, values: list) -> go.Figure:
    fig = go.Figure(go.Bar(x=labels, y=values, marker_color="#4F46E5", text=values, textposition="auto"))
    fig.update_layout(
        yaxis={"range": [0, 100], "title": "Score %"},
        height=300,
        margin=dict(t=30, b=10, l=20, r=20),
    )
    return fig