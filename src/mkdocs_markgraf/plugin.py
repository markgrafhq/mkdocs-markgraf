"""MkDocs plugin that turns ```markgraf fenced blocks into embedded
Canvas2D animations rendered by the markgraf player bundle.
"""

from __future__ import annotations

import base64
import os
import re
import shutil
from pathlib import Path

from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin


FENCE_RE = re.compile(
    r"^(?P<indent>[ \t]*)```markgraf(?P<attrs>[^\n]*)\n(?P<body>.*?)\n(?P=indent)```\s*$",
    re.DOTALL | re.MULTILINE,
)

ATTR_RE = re.compile(r"([a-zA-Z_-]+)=([^\s\"]+|\"[^\"]*\")")


def _css_len(v: str) -> str:
    v = v.strip().strip('"')
    return v if any(v.endswith(u) for u in ("px", "%", "em", "rem", "vh", "svh", "dvh")) else f"{v}px"


def _parse_attrs(s: str) -> dict[str, str]:
    return {k.lower(): v.strip('"') for k, v in ATTR_RE.findall(s)}

ASSET_DIR = Path(__file__).parent / "assets"
JS_NAME = "markgraf-embed.js"
CSS_NAME = "markgraf-embed.css"


def _hash(path: Path) -> str:
    import hashlib
    return hashlib.md5(path.read_bytes()).hexdigest()[:8]


class MarkgrafConfig(config_options.Config):
    assets_subdir = config_options.Type(str, default="assets/markgraf")
    js_path = config_options.Optional(config_options.Type(str))
    css_path = config_options.Optional(config_options.Type(str))


class MarkgrafPlugin(BasePlugin[MarkgrafConfig]):
    """Replace ```markgraf fences with <div data-markgraf> and ship the
    pre-built JS/CSS bundle as static site assets."""

    def on_config(self, config):
        self._js_src = Path(self.config.js_path) if self.config.js_path else ASSET_DIR / JS_NAME
        self._css_src = Path(self.config.css_path) if self.config.css_path else ASSET_DIR / CSS_NAME
        for src in (self._js_src, self._css_src):
            if not src.exists():
                raise FileNotFoundError(
                    f"mkdocs-markgraf: asset missing at {src}. Build it with "
                    f"`cd npm && bunx vite build -c vite.embed.config.js` and copy "
                    f"the output into the plugin's assets/ dir, or set js_path/css_path."
                )
        sub = self.config.assets_subdir.strip("/")
        jh = _hash(self._js_src)
        ch = _hash(self._css_src)
        config["extra_css"].append(f"{sub}/{CSS_NAME}?v={ch}")
        config["extra_javascript"].append(f"{sub}/{JS_NAME}?v={jh}")
        return config

    def on_page_markdown(self, markdown, page, config, files):
        if "```markgraf" not in markdown:
            return markdown

        def replace(match: re.Match) -> str:
            body = match.group("body")
            encoded = base64.b64encode(body.encode("utf-8")).decode("ascii")
            attrs = _parse_attrs(match.group("attrs") or "")
            styles = []
            if "height" in attrs:
                styles.append(f"--mg-max-height:{_css_len(attrs['height'])}")
            if "width" in attrs:
                styles.append(f"max-width:{_css_len(attrs['width'])}")
            style_attr = f' style="{";".join(styles)}"' if styles else ""
            return (
                f'<div class="markgraf-embed" data-markgraf '
                f'data-markgraf-src-b64="{encoded}"{style_attr}></div>'
            )

        return FENCE_RE.sub(replace, markdown)

    def on_post_build(self, config):
        out_dir = Path(config["site_dir"]) / self.config.assets_subdir.strip("/")
        out_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self._js_src, out_dir / JS_NAME)
        shutil.copy2(self._css_src, out_dir / CSS_NAME)
