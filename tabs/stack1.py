# stack1_content.py
from dash import dcc, html, dash_table
import plotly.graph_objs as go
from config import streaming_interval


theme_color = "#0c2a0c"
plot_bg_color = "#212529"
update_frequency = streaming_interval  # seconds

# Simulate real-time data


def stack1_content():
    return html.Div(
        [
            # Title
            html.H2("Battery Stack 1", style={"color": "#1DB954"}),
            # Dropdown to select Static or Dynamic Indicators
            dcc.Dropdown(
                id="stack1-indicator-dropdown",
                options=[
                    {"label": "System description", "value": "static"},
                    {"label": "Monitor", "value": "dynamic"},
                ],
                value="dynamic",  # Default value
                style={"width": "40%", "marginBottom": "20px", "color": "#000000"},
            ),
            html.Div(id="stack1-indicator-content"),  # Placeholder for indicator content

            # Date and Time Selectors for Start and End Time
            html.H3("Export datalog", style={"color": "#1DB954", "marginTop": "50px"}),
            html.Div(
                [
                    html.Label("Start Time: ", style={"fontWeight": "bold", "color": "#ffffff"}),
                    dcc.Input(
                        id="start-time-year", type="number", placeholder="Year", min=2000, max=2025,
                        style={"width": "10%", "marginRight": "5px", "height": "20px"}
                    ),
                    dcc.Input(
                        id="start-time-month", type="number", placeholder="Month", min=1, max=12,
                        style={"width": "8%", "marginRight": "5px", "height": "20px"}
                    ),
                    dcc.Input(
                        id="start-time-day", type="number", placeholder="Day", min=1, max=31,
                        style={"width": "8%", "marginRight": "5px", "height": "20px"}
                    ),
                    dcc.Input(
                        id="start-time-hour", type="number", placeholder="Hour", min=0, max=23,
                        style={"width": "8%", "marginRight": "5px", "height": "20px"}
                    ),
                    dcc.Input(
                        id="start-time-minute", type="number", placeholder="Minute", min=0, max=59,
                        style={"width": "8%", "marginRight": "5px", "height": "20px"}
                    ),
                ],
                style={"marginBottom": "20px"},
            ),
            html.Div(
                [
                    html.Label("End Time: ", style={"fontWeight": "bold", "color": "#ffffff", "marginRight": "6px"}),
                    dcc.Input(
                        id="end-time-year", type="number", placeholder="Year", min=2000, max=2025,
                        style={"width": "10%", "marginRight": "5px", "height": "20px"}
                    ),
                    dcc.Input(
                        id="end-time-month", type="number", placeholder="Month", min=1, max=12,
                        style={"width": "8%", "marginRight": "5px", "height": "20px"}
                    ),
                    dcc.Input(
                        id="end-time-day", type="number", placeholder="Day", min=1, max=31,
                        style={"width": "8%", "marginRight": "5px", "height": "20px"}
                    ),
                    dcc.Input(
                        id="end-time-hour", type="number", placeholder="Hour", min=0, max=23,
                        style={"width": "8%", "marginRight": "5px", "height": "20px"}
                    ),
                    dcc.Input(
                        id="end-time-minute", type="number", placeholder="Minute", min=0, max=59,
                        style={"width": "8%", "marginRight": "5px", "height": "20px"}
                    ),
                ],
                style={"marginBottom": "20px"},
            ),

            # Download Button
            html.Button(
                "Download Log Data",
                id="download-button",
                n_clicks=0,
                style={
                    "backgroundColor": "#1DB954",
                    "color": "#ffffff",
                    "border": "none",
                    "padding": "10px 20px",
                    "fontSize": "16px",
                    "borderRadius": "5px",
                    "cursor": "pointer",
                },
            ),

            # Download Link
            dcc.Download(id="log-download"),
        ],
        style={"marginLeft": "10px"}
    )


def stack1_statics():
    # Static indicators table
    return html.Div(
        [   # html.P("Static Indicators for Battery Stack 1:"),

            # Data table
            dash_table.DataTable(
                id="static-indicators-table",
                columns=[
                    {"name": "Indicator", "id": "indicator"},
                    {"name": "Value", "id": "value"},
                ],
                data=[
                    {"indicator": "Battery Chemistry", "value": "Sodium"},
                    {"indicator": "Nominal Voltage", "value": "96V"},
                    {"indicator": "Capacity", "value": "100Ah"},
                    {"indicator": "Number of Cells", "value": "10"},
                ],
                style_table={"width": "50%", "margin": "0 auto"},
                style_header={
                    "backgroundColor": plot_bg_color,
                    "display": "none",
                    "color": "white",
                    "fontWeight": "bold",
                    "fontSize": "18px",
                },
                style_cell={
                    "textAlign": "center",
                    "padding": "10px",
                    "border": "1px solid #ddd",
                },
                style_data={
                    "backgroundColor": "#282828",
                    "color": "white",
                    "fontSize": "18px",
                },
                style_data_conditional=[
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "#3b3b3b",
                    },
                    {
                        "if": {"state": "selected"},
                        "backgroundColor": "#7df783",  # Selected cell color (yellow)
                        "color": "black",  # Text color inside selected cell
                    }
                ],
            ),
        ]
    )


def get_figure_layout(indicator):
    plot_bg_color = "#212529"  # #212529  1d2720
    plot_line_color = "#8bfe97"
    plot_axis_color = "#1DB954"
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


def stack1_dynamics():
    # Dynamic indicators table
    return html.Div(
        [
            # html.P("Dynamic Indicators for Battery Stack 1:"),
            # Connection Status
            html.Div(
                [
                    html.Span("Connected to the controller: ", style={"fontWeight": "bold", "color": "#ffffff"}),
                    html.Span(id="connection-status", style={"fontWeight": "bold", "color": "#1DB954"}),
                    # Placeholder
                ],
                style={
                    "padding": "10px",
                    "textAlign": "left",
                    "marginBottom": "20px",
                },
            ),

            dash_table.DataTable(
                id="dynamic-indicators-table",
                columns=[
                    {"name": "Indicator", "id": "indicator"},
                    {"name": "Value", "id": "value"},
                ],
                # data=[
                #     {"indicator": "State of Charge (SOC)", "value": f"{0:.2f}%"},
                #     {"indicator": "DC Bus Voltage", "value": f"{0:.2f}V"},
                #     {"indicator": "DC Current", "value": f"{0:.2f}A"},
                #     {"indicator": "Total Power", "value": f"{0:.2f}W"},
                #     {"indicator": "Temperature", "value": f"{0:.2f}W"},
                #     {"indicator": "State of the Battery Bank", "value": "Healthy"},
                # ],
                style_table={"width": "90%", "margin": "0 auto","border": "none", "borderCollapse": "collapse"},
                style_header={
                    "backgroundColor": plot_bg_color,
                    "color": "white",
                    "fontWeight": "bold",
                    "fontSize": "20px",
                },
                style_cell={
                    "textAlign": "center",
                    "padding": "10px",
                    "border": "none",
                    # "border": "1px solid #000000",
                },
                style_data={
                    "backgroundColor": "#282828",
                    "color": "white",
                    "fontSize": "18px"
                },
                style_data_conditional=[
                    {
                        "if": {"row_index": "odd"},
                        "backgroundColor": "#3b3b3b",
                    },
                    {
                        "if": {"state": "selected"},
                        "backgroundColor": "#7df783",
                        "color": "black",  # Text color inside selected cell
                    }
                ],
            ),
            # dbc.Table(
            #     # Add header with placeholders for the body
            #     children=[
            #         html.Thead(
            #             html.Tr([html.Th("Indicator"), html.Th("Value")])
            #         ),
            #         html.Tbody(id="dynamic-indicators-table-body"),  # Table body with an id
            #     ],
            #     className="table table-dark table-sm table-hover",
            #     style={"width": "90%", "margin": "0 auto"},
            # ),


            # Real-time Voltage, Current, Power, SOC Curves (2x2 grid)
            html.Div(
                [
                    html.Div(
                        dcc.Graph(id="voltage-curve", figure={'layout': get_figure_layout("voltage")}),
                        style={"width": "32%", "display": "inline-block", "marginTop": "2%"}#, "backgroundColor": plot_bg_color},
                    ),
                    html.Div(
                        dcc.Graph(id="current-curve", figure={'layout': get_figure_layout("current")}),
                        style={"width": "32%", "display": "inline-block", "marginTop": "2%"}#, "backgroundColor": plot_bg_color},
                    ),
                    html.Div(
                        dcc.Graph(id="power-curve", figure={'layout': get_figure_layout("power")}),
                        style={"width": "32%", "display": "inline-block", "marginTop": "2%"}#, "backgroundColor": plot_bg_color},
                    ),
                ],
                style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between", "width": "90%", "margin": "0 auto"},
            ),

            html.Div(
                [

                    html.Div(
                        dcc.Graph(id="soc-curve", figure={'layout': get_figure_layout("soc")}),
                        style={"width": "48%", "display": "inline-block", "marginTop": "2%"},
                    ),
                    html.Div(
                        dcc.Graph(id="temp-curve", figure={'layout': get_figure_layout("temperature")}),
                        style={"width": "48%", "display": "inline-block", "marginTop": "2%"},
                    ),
                ],
                style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between", "width": "90%", "margin": "0 auto"},
            ),

            # html.Div(
            #     [
            #         html.Div(
            #             dcc.Graph(id="temp-curve"),
            #             style={"width": "48%", "display": "inline-block", "marginTop": "2%"},
            #         ),
            #     ],
            #     style={"display": "flex", "flexWrap": "wrap", "justifyContent": "space-between", "width": "90%",
            #            "margin": "0 auto"},
            # ),

            # Interval component to update data
            dcc.Interval(
                id="interval-component",
                interval=update_frequency*1000,  # Update every 1 second (1000 milliseconds)
                n_intervals=0,
            ),
        ]
    )