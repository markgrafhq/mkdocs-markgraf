# mkdocs-markgraf

MkDocs plugin that renders [markgraf](https://github.com/i-am-the-slime/markgraf)
animations inside documentation pages.

Fenced ` ```markgraf ` blocks become an interactive Canvas2D player with a
scrub bar, keyframe ticks, play/pause, and speed control. The bundled JS/CSS
ships with the plugin — no CDN, no external dependencies at runtime.

## Install

```bash
pip install mkdocs-markgraf
```

## Use

`mkdocs.yml`:

```yaml
plugins:
  - markgraf
```

Inside a page:

````markdown
```markgraf
seed 1

frame v1 {
  +node client "Client"
  +node api "API"
  +node db "Database"
  +edge client api
  +edge api db
  client -> api "GET /user/42"
  api -> db "SELECT"
}

frame v2 {
  +node cache "Cache"
  -edge api db
  +edge api cache
  client -> api "GET /user/42"
  api -> cache "HIT"
}
```
````

## Sizing

Constrain the embed via fence attributes:

````markdown
```markgraf height=320
…
```

```markgraf width=420
…
```

```markgraf height=80svh
…
```
````

Values default to `px`; `svh`, `vh`, `dvh`, `%`, `em`, `rem` are accepted as
explicit units. `height` clamps `max-height` on the canvas; `width` clamps
`max-width` on the embed container.

## Player controls

- Click the canvas or press **Space** anywhere to toggle play/pause.
- Click ticks on the scrub bar to jump between keyframes.
- Only one embed plays at a time — starting one pauses the others.
- The control bar is overlaid on the canvas and only shown on hover or focus.

## Configuration

`mkdocs.yml`:

```yaml
plugins:
  - markgraf:
      assets_subdir: assets/markgraf  # where to copy the bundled JS/CSS
      js_path: /path/to/markgraf-embed.js   # override the bundled JS
      css_path: /path/to/markgraf-embed.css # override the bundled CSS
```

## License

MIT.
