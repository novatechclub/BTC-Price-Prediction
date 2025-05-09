# # visual_utils.py
# 
# import plotly.graph_objects as go
# import networkx as nx
# import matplotlib.pyplot as plt
# 
# 
# # visual_utils.py
# import matplotlib.pyplot as plt
# import seaborn as sns
# import pandas as pd
# 
# def plot_missing_heatmap(df, bin_size="1H"):
#     df = df.copy()
#     df["datetime"] = pd.to_datetime(df["datetime"])
#     df = df.set_index("datetime").sort_index()
# 
#     freq = bin_size.lower()
#     presence = df.index.floor(freq).to_series().value_counts().sort_index()
#     presence = presence.reindex(
#         pd.date_range(df.index.min(), df.index.max(), freq=freq), fill_value=0
#     )
# 
#     fig, ax = plt.subplots(figsize=(12, 2))
#     sns.heatmap(presence.values.reshape(1, -1), cmap="Reds", cbar=False, vmin=0, vmax=1, ax=ax)
#     ax.set_title(f"Missing Data Heatmap ({bin_size}) — white = missing")
#     ax.set_yticks([])
#     ax.set_xticks([])
#     return fig
# 
# def plot_top_distributions(df, top_n=5):
#     df = df.select_dtypes(include="number").drop(columns=["t_epoch"], errors="ignore")
#     top_cols = df.mean().sort_values(ascending=False).head(top_n).index
#     fig, axs = plt.subplots(1, top_n, figsize=(4 * top_n, 4))
# 
#     for i, col in enumerate(top_cols):
#         axs[i].hist(df[col].dropna(), bins=40, color='skyblue')
#         axs[i].set_title(col)
# 
#     fig.suptitle(f"Top {top_n} Topic Columns - Distributions")
#     return fig
# 
# def plot_total_activity(df):
#     df = df.copy()
#     df["datetime"] = pd.to_datetime(df["datetime"])
#     df = df.set_index("datetime").sort_index()
#     numeric_df = df.select_dtypes(include="number").drop(columns=["t_epoch"], errors="ignore")
# 
#     df["total_activity"] = numeric_df.sum(axis=1)
#     daily_activity = df["total_activity"].resample("D").sum()
# 
#     fig, ax = plt.subplots(figsize=(12, 4))
#     daily_activity.plot(ax=ax)
#     ax.set_title("Total Topic Activity Over Time (Daily)")
#     ax.set_xlabel("Date")
#     ax.set_ylabel("Total Activity")
#     return fig
# 
# def plot_total_trading_activity(df):
#     df = df.copy()
#     df["datetime"] = pd.to_datetime(df["datetime"])
#     df = df.set_index("datetime").sort_index()
#     numeric_df = df[["trades"]]
# 
#     df["total_activity"] = numeric_df.sum(axis=1)
#     daily_activity = df["total_activity"].resample("D").sum()
#     fig, ax = plt.subplots(figsize=(12, 4))
#     daily_activity.plot(ax=ax)
#     ax.set_title("Total Trading Activity Over Time (Daily)")
#     ax.set_xlabel("Date")
#     ax.set_ylabel("Total Trading Activity")
#     return fig
# 
# def visualize_topic_hierarchy_3d(categorized_topics, save_path_html=None, show=True, logger=None):
#     """
#     Creates an interactive 3D network graph showing Sentiment_Topics (color-coded) and Other_Topics (gray).
#     """
#     if logger:
#         logger.info("Generating simplified 3D topic graph with sentiment color coding...")
# 
#     G = nx.Graph()
#     node_section_map = {}
# 
#     sentiment_colors = {
#         "Positive": "green",
#         "Negative": "salmon",
#         "FOMO": "yellow",
#         "Uncertain": "yellow",
#         "Hopeful": "yellow"
#     }
# 
#     # Top-level nodes
#     G.add_node("Sentiment_Topics")
#     G.add_node("Other_Topics")
#     node_section_map["Sentiment_Topics"] = "Sentiment_Topics"
#     node_section_map["Other_Topics"] = "Other_Topics"
# 
#     # Add sentiment topics
#     sentiment_data = categorized_topics.get("Sentiment_Topics", {})
#     for sentiment_group, topics in sentiment_data.items():
#         G.add_node(sentiment_group)
#         G.add_edge("Sentiment_Topics", sentiment_group)
#         node_section_map[sentiment_group] = sentiment_group
# 
#         for tid, name in topics.items():
#             label = f"{tid}: {name}"
#             G.add_node(label)
#             G.add_edge(sentiment_group, label)
#             node_section_map[label] = sentiment_group
# 
#     # Add other topics
#     other_topics = categorized_topics.get("Other_Topics", {})
#     for tid, name in other_topics.items():
#         label = f"{tid}: {name}"
#         G.add_node(label)
#         G.add_edge("Other_Topics", label)
#         node_section_map[label] = "Other_Topics"
# 
#     # Layout
#     pos = nx.spring_layout(G, dim=3, seed=42)
#     x, y, z, node_labels, colors = [], [], [], [], []
# 
#     for node in G.nodes():
#         x.append(pos[node][0])
#         y.append(pos[node][1])
#         z.append(pos[node][2])
#         node_labels.append(node)
# 
#         section = node_section_map.get(node, "Other_Topics")
#         color = sentiment_colors.get(section, "gray")
#         colors.append(color)
# 
#     # Edges
#     edge_x, edge_y, edge_z = [], [], []
#     for edge in G.edges():
#         x0, y0, z0 = pos[edge[0]]
#         x1, y1, z1 = pos[edge[1]]
#         edge_x += [x0, x1, None]
#         edge_y += [y0, y1, None]
#         edge_z += [z0, z1, None]
# 
#     edge_trace = go.Scatter3d(
#         x=edge_x, y=edge_y, z=edge_z,
#         mode='lines',
#         line=dict(color='lightgray', width=1),
#         hoverinfo='none'
#     )
# 
#     node_trace = go.Scatter3d(
#         x=x, y=y, z=z,
#         mode='markers+text',
#         marker=dict(size=6, color=colors),
#         text=node_labels,
#         hoverinfo='text'
#     )
# 
#     fig = go.Figure(data=[edge_trace, node_trace],
#                     layout=go.Layout(
#                         title="Augmento Topics (Sentiment + Other)",
#                         margin=dict(l=0, r=0, b=0, t=50),
#                         scene=dict(
#                             xaxis=dict(showbackground=False),
#                             yaxis=dict(showbackground=False),
#                             zaxis=dict(showbackground=False)
#                         )
#                     ))
# 
#     if save_path_html:
#         fig.write_html(save_path_html)
#         if logger:
#             logger.info(f"3D sentiment graph saved to {save_path_html}")
# 
#     if show:
#         fig.show()
#     else:
#         plt.close()
# 

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def plot_missing_heatmap(df, bin_size="1H"):
    df = df.copy()
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.set_index("datetime").sort_index()

    freq = bin_size.lower()
    presence = df.index.floor(freq).to_series().value_counts().sort_index()
    full_range = pd.date_range(df.index.min(), df.index.max(), freq=freq)
    presence = presence.reindex(full_range, fill_value=0)

    z = [presence.values]  # single row heatmap
    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=presence.index,
        y=["Presence"],  # single row
        colorscale="Reds",
        showscale=True
    ))

    fig.update_layout(
        title=f"Missing Data Heatmap ({bin_size}) — white = missing",
        height=150,
        yaxis=dict(showticklabels=False),
        margin=dict(t=40, b=40),
        xaxis=dict(tickangle=45, automargin=True)
    )
    return fig


def plot_top_distributions(df, top_n=5):
    df = df.select_dtypes(include="number").drop(columns=["t_epoch"], errors="ignore")
    top_cols = df.mean().sort_values(ascending=False).head(top_n).index

    # Melt to long format
    df_long = df[top_cols].melt(var_name="Column", value_name="Value")
    
    fig = px.histogram(
        df_long, x="Value", color_discrete_sequence=['#FF4500'], facet_col="Column", facet_col_wrap=top_n,
        title=f"Top {top_n} Columns - Distributions", height=300, 
    )
    fig.update_layout(showlegend=False)
    return fig

def plot_total_activity(df):
    df = df.copy()
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.set_index("datetime").sort_index()
    numeric_df = df.select_dtypes(include="number").drop(columns=["t_epoch"], errors="ignore")

    df["total_activity"] = numeric_df.sum(axis=1)
    daily_activity = df["total_activity"].resample("D").sum().reset_index()

    fig = px.line(daily_activity, x="datetime", y="total_activity", color_discrete_sequence=['#FF4500'],
                  title="Total Topic Activity Over Time (Daily)",
                  labels={"datetime": "Date", "total_activity": "Total Activity"})
    return fig

def plot_total_trading_activity(df):
    df = df.copy()
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.set_index("datetime").sort_index()
    numeric_df = df[["trades"]]

    df["total_activity"] = numeric_df.sum(axis=1)
    daily_activity = df["total_activity"].resample("D").sum().reset_index()

    fig = px.line(daily_activity, x="datetime", y="total_activity", color_discrete_sequence=['#FF4500'],
                  title="Total Trading Activity Over Time (Daily)",
                  labels={"datetime": "Date", "total_activity": "Total Trading Activity"})
    return fig


def plot_btc_candlestick(df, date_column, start_date, end_date=None,
                          open_col='open', high_col='high', low_col='low', close_col='close'):
    # Copy and clean date column (remove timezone info)
    df = df.copy()
    df[date_column] = pd.to_datetime(df[date_column]).dt.tz_localize(None)

    # Convert inputs to naive datetime (timezone-free)
    start_ts = pd.to_datetime(start_date)
    end_ts = pd.to_datetime(end_date) if end_date else None

    # Filter date range
    mask = (df[date_column] >= start_ts)
    if end_ts:
        mask &= (df[date_column] <= end_ts)
    df_filtered = df[mask]

    # Plot candlestick
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df_filtered[date_column],
        open=df_filtered[open_col],
        high=df_filtered[high_col],
        low=df_filtered[low_col],
        close=df_filtered[close_col],
        name='BTC Price'
    ))

    fig.update_layout(
        title=f'BTC Candlestick Chart from {start_date} to {end_date or "latest"}',
        xaxis_title='Date',
        yaxis_title='Price',
        xaxis_rangeslider_visible=False,
        template='plotly_dark',
        height=600
    )

    return fig

