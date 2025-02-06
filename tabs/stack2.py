# stack2_content.py
import dash
from dash import html

def stack2_content():
    return html.Div(
        [
            html.H2("Battery Stack 2 Indicators", style={"color": "#1DB954"}),
            html.P("Display relevant indicators for Battery Stack 2."),
        ]
    )
