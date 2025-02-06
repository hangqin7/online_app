import plotly.graph_objs as go
import pandas as pd

plot_bg_color = "#212529"  # #212529  1d2720
plot_line_color = "#8bfe97"
plot_axis_color = "#1DB954"
def get_trace_obj(indicator, real_time_frame):
    """turn real time data frame (pd frame) in to graph object according to the key input
        :arg indicator: string"""

    y_list = real_time_frame[indicator].tolist()
    trace = go.Scatter(
        x=list(range(len(y_list))),
        y=y_list,
        mode="lines",
        name=indicator.upper(),
        line=dict(color=plot_line_color, width=3),# 65d23f, #769e68
    )
    return trace


def get_figure_layout(indicator):
    return go.Layout(
            title=dict(
                text=indicator,  # Title text
                font=dict(color=plot_axis_color, size=20),  # Set the color and size of the title
            ),  # Title
            # title_x=0,  # Title position on x-axis (0 = far left)
            # title_y=1,  # Title position on y-axis (1 = top)
            # title_xanchor="left",  # Anchor the title to the left side
            # title_yanchor="top",  # Anchor the title to the top
            plot_bgcolor=plot_bg_color,  # Plot area background color (black)
            paper_bgcolor=plot_bg_color,  # Figure background color (light grey)
            xaxis=dict(
                title="Time",
                title_font=dict(color=plot_axis_color),  # Color of x-axis title
                tickfont=dict(color=plot_axis_color),  # Color of x-axis ticks
                linecolor=plot_axis_color,  # Color of x-axis line
                gridcolor=plot_axis_color, zerolinecolor=plot_axis_color
            ),
            yaxis=dict(
                title=indicator,
                title_font=dict(color=plot_axis_color),  # Color of y-axis title
                tickfont=dict(color=plot_axis_color),  # Color of y-axis ticks
                linecolor=plot_axis_color,  # Color of y-axis line
                gridcolor=plot_axis_color, zerolinecolor=plot_axis_color
            ),
            # shapes=[reference_line]  # Add the reference line to the plot
        )
