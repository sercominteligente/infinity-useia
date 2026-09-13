from __future__ import annotations

from . import web_v6


# Accessibility/readability layer for the v0.6 cockpit.
# Keep the visual hierarchy intact while preventing tiny UI labels.
TYPOGRAPHY_FLOOR_CSS = r'''
/* HAKHAM readability floor: no operational UI copy below 11px */
body{font-size:11px}
small,
.logo span,
.navbtn,
.ach-mini small,
.ach-mini b,
.kbd,
.time small,
.engine-pill,
.eyebrow,
.voice-copy small,
.avatar-tag,
.avatar-state,
.status-badge,
.modebtn,
.ach-card p,
.item small,
.agent small,
.agent .role,
.tool,
.tool .tstate,
.perm,
.bubble strong{font-size:11px!important}

/* Slightly lift high-frequency operational text for comfortable reading. */
.searchbox input,
.primary,
.ghost,
.iconbtn,
.status-row,
.cardtitle,
.item,
.agent b,
.bubble,
.chatrow textarea,
.send,
.mic,
.toast{font-size:12px}

/* Preserve compact HUD feel without squeezing readability. */
.navbtn,.modebtn,.engine-pill,.status-badge,.avatar-state,.perm{line-height:1.25}
'''


def _inject_typography_floor(html: str) -> str:
    marker = "/* HAKHAM readability floor: no operational UI copy below 11px */"
    if marker in html:
        return html
    return html.replace("</style>", f"{TYPOGRAPHY_FLOOR_CSS}\n</style>", 1)


CONTROL_CENTER_HTML = _inject_typography_floor(web_v6.CONTROL_CENTER_HTML)
# The route defined in web_v6 resolves this module global at request time.
web_v6.CONTROL_CENTER_HTML = CONTROL_CENTER_HTML
app = web_v6.app


def main() -> None:
    import uvicorn

    uvicorn.run("hakham.web_v6_readable:app", host="127.0.0.1", port=8765, reload=False)
