# main_content.py
from dash import dcc, html
import dash_daq as daq
from config import *


header_width = 120
theme_color = "#000000"  # #2d4425
theme_bgcolor = "#1c1c1c"  #1c1c1c

def dash_layout():
    return html.Div(
            style={"backgroundColor": theme_color, "color": "#e0e0e0", "minHeight": "100vh", "fontFamily": "Arial, sans-serif"},
            children=[
                # Header bar
                html.Div(
                    style={
                        "backgroundColor": "#000000",  # Darker background for header
                        "textAlign": "center",
                        "position": "fixed",
                        "width": "100%",
                        "top": "0",
                        "zIndex": "1000",
                        "height": "{}px".format(header_width),
                        "display": "flex",  # Flexbox layout
                        "justifyContent": "space-between",  # Space out the logo and title
                        "alignItems": "center",  # Center the items vertically
                        # "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.5)",
                    },
                    children=[
                        html.Img(
                            src="https://unrivaledneon.com.au/cdn/shop/products/wink-emoji-neon-sign-169648_1000x.jpg?v=1707282666",
                            style={
                                "height": "100px",
                                "marginRight": "0px",
                                "marginLeft": "15px",
                            },
                        ),
                        html.H1("Ertzy EMS Dashboard",
                                style={"margin": "0", "color": "#ffffff", "flex":"1", "textAlign": "center"},
                                ),
                        html.Button("Logout", id="logout-btn",
                                    style={'backgroundColor': 'red',
                                           'color': 'white',
                                           'marginLeft': 'auto',
                                           "marginRight": "50px",
                                           "padding": "8px",
                                           "cursor": "pointer",
                                           "fontSize": "15px", "fontWeight": "bold",
                                            "borderRadius": "5px", "border": "none",
                                           }),
                        dcc.Location(id='url-redirect', refresh=True)
                    ],
                ),

                # Main container
                html.Div(
                    style={"paddingTop": "{}px".format(header_width), "padding": "120px", "flex":"1", "width": "90%",
                           "backgroundColor": theme_color, "alignItems": "center",
                           "justifyContent": "center",
                           "marginBottom": "20px",},  # Space for the fixed header
                    children=[
                        # Label above the tabs
                        # html.Div(
                        #     "Select a View:",
                        #     style={
                        #         "textAlign": "left",
                        #         "color": "#1DB954",
                        #         "fontSize": "16px",
                        #         "fontWeight": "bold",
                        #         "marginBottom": "10px",
                        #     },
                        # ),
                        # Tabs
                        dcc.Tabs(
                            id="tabs",
                            value="main",
                            children=[
                                dcc.Tab(
                                    label="Main Page",
                                    value="main",
                                    style={
                                        "backgroundColor": theme_bgcolor,
                                        "color": "#ffffff",
                                        "border": "1px solid #333333",
                                        "borderRadius": "5px",
                                        "padding": "10px",
                                    },
                                    selected_style={
                                        "backgroundColor": "#1DB954",  # Spotify green
                                        "color": "#000",
                                        "fontWeight": "bold",
                                        "border": "1px solid #1DB954",
                                        "borderRadius": "5px",
                                        "padding": "10px",
                                    },
                                ),
                                dcc.Tab(
                                    label="Battery Unit 1",
                                    value="stack1",
                                    style={
                                        "backgroundColor": theme_bgcolor,
                                        "color": "#e0e0e0",
                                        "border": "1px solid #333333",
                                        "borderRadius": "5px",
                                        "padding": "10px",
                                    },
                                    selected_style={
                                        "backgroundColor": "#1DB954",
                                        "color": "#000",
                                        "fontWeight": "bold",
                                        "border": "1px solid #1DB954",
                                        "borderRadius": "5px",
                                        "padding": "10px",
                                    },
                                ),
                                dcc.Tab(
                                    label="Battery Unit 2",
                                    value="stack2",
                                    style={
                                        "backgroundColor": theme_bgcolor,
                                        "color": "#e0e0e0",
                                        "border": "1px solid #333333",
                                        "borderRadius": "5px",
                                        "padding": "10px",
                                    },
                                    selected_style={
                                        "backgroundColor": "#1DB954",
                                        "color": "#000",
                                        "fontWeight": "bold",
                                        "border": "1px solid #1DB954",
                                        "borderRadius": "5px",
                                        "padding": "10px",
                                    },
                                ),
                            ],
                            style={
                                "marginBottom": "20px",
                                "backgroundColor": theme_color,
                                "border": "none",
                            },
                        ),
                        # Content section
                        html.Div(
                            id="content",
                            style={
                                "backgroundColor": "#1c1c1c",
                                "padding": "20px",
                                "borderRadius": "10px",
                                "boxShadow": "0 4px 6px rgba(0, 0, 0, 0.5)",
                            },
                        ),
                    ],
                ),
            ],
        )

def main_content():
    return html.Div(
        [
            # html.H2("Main Page", style={"color": "#1DB954", "textAlign": "center"}),

            html.Div(
                [
                    html.Label(
                        "Select Energy Strategy:",
                        style={"color": "white", "fontSize": "20px", "fontWeight": "bold", "marginBottom": "20px"},
                    ),
                    dcc.RadioItems(
                        id="energy-strategy",
                        options=[
                            {"label": "Strategy 1", "value": "strategy1"},
                            {"label": "Strategy 2", "value": "strategy2"},
                            {"label": "Strategy 3", "value": "strategy3"},
                            {"label": "Smart", "value": "strategy4"},
                        ],
                        value="strategy4",
                        labelStyle={"display": "block", "margin": "10px 0", "fontSize": "18px", "color": "white"},
                        style={
                            "marginTop": "20px",
                            "padding": "10px",
                            "backgroundColor": "#1e1e1e",
                            "border": "1px solid #333",
                            "borderRadius": "8px",
                        },
                    ),
                ],
                style={"margin": "20px 0"},
            ),

            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                "Battery Unit 1: SOC",
                                style={
                                    "textAlign": "center",
                                    "color": "white",
                                    "fontSize": "20px",  # Change font size here
                                    "marginTop": "10px",
                                },
                            ),
                            daq.Gauge(
                                id="battery-level-1",
                                min=0,
                                max=100,
                                value=None,
                                color={
                                    "gradient": True,
                                    "ranges": {
                                        "#0d47a1": [0, 50],  # Blue gradient
                                        "#1db954": [50, 100],  # Green gradient
                                    },
                                },
                                # label="Battery Unit 1",
                                showCurrentValue=True,
                                units="%",
                                size=200,  # Adjust size for emphasis
                                style={"color": "white", "padding": "0px"},
                            ),
                        ],
                        style={
                            "width": "40%",
                            "display": "inline-block",
                            "margin": "0 2.5%",
                            "padding": "0px",
                            "backgroundColor": "#1e1e1e",
                            "borderRadius": "15px",
                            "boxShadow": "0 0 20px 4px rgba(29,185,84,0.6)",  # Dazzling light effect
                        },
                    ),

                    html.Div(
                        [
                            html.Div(
                                "Battery Unit 2: SOC",
                                style={
                                    "textAlign": "center",
                                    "color": "white",
                                    "fontSize": "20px",  # Change font size here
                                    "marginTop": "10px",
                                },
                            ),
                            daq.Gauge(
                                id="battery-level-2",
                                min=0,
                                max=100,
                                value=None,
                                color={
                                    "gradient": True,
                                    "ranges": {
                                        "#0d47a1": [0, 50],  # Blue gradient
                                        "#1db954": [50, 100],  # Green gradient
                                    },
                                },
                                # label="Battery Unit 2",
                                showCurrentValue=True,
                                units="%",
                                size=200,
                                style={"color": "white", "padding": "0px"},
                            ),
                        ],
                        style={
                            "width": "40%",
                            "display": "inline-block",
                            "margin": "0 2.5%",
                            "padding": "0px",
                            "backgroundColor": "#1e1e1e",
                            "borderRadius": "15px",
                            "boxShadow": "0 0 20px 4px rgba(29,185,84,0.6)",  # Dazzling light effect
                        },
                    ),
                ],
                style={
                    "textAlign": "center",
                    "padding": "20px",
                    "backgroundColor": "#121212",
                    "borderRadius": "8px",
                    "border": "1px solid #333",
                    "marginTop": "20px",
                },
            ),
            # Interval component to update data
            dcc.Interval(
                id="interval-main",
                interval=streaming_interval * 1000,  # Update every 1 second (1000 milliseconds)
                n_intervals=0,
            ),
        ],
        style={"padding": "20px", "backgroundColor": "#121212"},
    )