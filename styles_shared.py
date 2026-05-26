TEXT_TONES = {
    "dark": "#0f172a",
    "night": "#07111F",
    "muted": "#64748b",
    "light": "#F8FAFC",
    "gold": "#F4C542",
    "danger": "#b91c1c",
    "success": "#15803d",
}

TEXT_STYLES = {
    "display_title": {
        "family": "'Montserrat', sans-serif",
        "size": "34px",
        "mobile_size": "28px",
        "weight": "900",
        "line_height": "1.05",
    },
    "section_subtitle": {
        "family": "'Inter', sans-serif",
        "size": "15px",
        "mobile_size": "12px",
        "weight": "600",
        "line_height": "1.35",
    },
    "panel_title": {
        "family": "'Montserrat', sans-serif",
        "size": "18px",
        "mobile_size": "16px",
        "weight": "900",
        "line_height": "1.05",
    },
    "panel_subtitle": {
        "family": "'Inter', sans-serif",
        "size": "12px",
        "mobile_size": "11px",
        "weight": "700",
        "line_height": "1.25",
    },
    "card_title": {
        "family": "'Montserrat', sans-serif",
        "size": "14px",
        "mobile_size": "13px",
        "weight": "900",
        "line_height": "1.18",
    },
    "card_body": {
        "family": "'Inter', sans-serif",
        "size": "12.5px",
        "mobile_size": "12px",
        "weight": "600",
        "line_height": "1.42",
    },
    "caption": {
        "family": "'Inter', sans-serif",
        "size": "11px",
        "mobile_size": "10.5px",
        "weight": "800",
        "line_height": "1.2",
    },
    "pill_label": {
        "family": "'Montserrat', sans-serif",
        "size": "11px",
        "mobile_size": "10.5px",
        "weight": "900",
        "line_height": "1",
    },
}

SURFACES = {
    "panel_light": {
        "background": "rgba(255,255,255,0.94)",
        "border": "1px solid rgba(226,232,240,0.9)",
        "radius": "18px",
        "padding": "16px",
        "shadow": "0 12px 30px rgba(15,23,42,0.06)",
        "mobile_radius": "16px",
        "mobile_padding": "13px",
    },
    "card_light": {
        "background": "rgba(248,250,252,0.86)",
        "border": "1px solid rgba(226,232,240,0.88)",
        "radius": "15px",
        "padding": "12px 13px",
        "shadow": (
            "inset 0 1px 0 rgba(255,255,255,0.55), "
            "0 6px 14px rgba(15,23,42,0.035)"
        ),
        "mobile_radius": "14px",
        "mobile_padding": "11px 12px",
    },
    "panel_dark": {
        "background": (
            "linear-gradient(135deg, rgba(7,17,31,0.98), "
            "rgba(15,23,42,0.94))"
        ),
        "border": "1px solid rgba(244,197,66,0.24)",
        "radius": "18px",
        "padding": "16px",
        "shadow": "0 12px 30px rgba(15,23,42,0.16)",
        "mobile_radius": "16px",
        "mobile_padding": "13px",
    },
}


def css_text(class_name, style="card_body", tone="dark"):
    spec = TEXT_STYLES[style]
    color = TEXT_TONES[tone]

    return f"""
.{class_name} {{
    font-family: {spec["family"]};
    font-size: {spec["size"]};
    font-weight: {spec["weight"]};
    line-height: {spec["line_height"]};
    color: {color};
}}

@media (max-width: 768px) {{
    .{class_name} {{
        font-size: {spec["mobile_size"]};
    }}
}}
"""


def css_section_title(class_name):
    return f"""
.{class_name} {{
    margin-bottom: 22px;
}}

{css_text(f"{class_name} h1", "display_title", "night")}
.{class_name} h1 {{
    margin: 0;
    letter-spacing: -0.04em;
}}

{css_text(f"{class_name} p", "section_subtitle", "muted")}
.{class_name} p {{
    margin: 6px 0 0 0;
}}
"""


def css_surface(class_name, surface="panel_light", full_height=False):
    spec = SURFACES[surface]
    height_rule = "height: 100%;" if full_height else ""

    return f"""
.{class_name} {{
    background: {spec["background"]};
    border: {spec["border"]};
    border-radius: {spec["radius"]};
    padding: {spec["padding"]};
    box-shadow: {spec["shadow"]};
    margin-bottom: 18px;
    {height_rule}
}}

@media (max-width: 768px) {{
    .{class_name} {{
        padding: {spec["mobile_padding"]};
        border-radius: {spec["mobile_radius"]};
        margin-bottom: 14px;
    }}
}}
"""


def css_panel_base(class_name):
    return css_surface(class_name, "panel_light", full_height=True)


def css_panel_header(prefix):
    return f"""
.{prefix}-panel-header {{
    display: flex;
    align-items: center;
    gap: 10px;

    padding: 4px 4px 14px 4px;
    margin-bottom: 12px;

    border-bottom: 1px solid rgba(226,232,240,0.75);
}}

.{prefix}-panel-icon {{
    width: 32px;
    height: 32px;
    border-radius: 10px;

    display: flex;
    align-items: center;
    justify-content: center;

    background: rgba(244,197,66,0.16);
    color: #0f172a;
    font-size: 16px;

    flex-shrink: 0;
}}

{css_text(f"{prefix}-panel-title", "panel_title", "dark")}
{css_text(f"{prefix}-panel-subtitle", "panel_subtitle", "muted")}

.{prefix}-panel-subtitle {{
    margin-top: 3px;
}}
"""
