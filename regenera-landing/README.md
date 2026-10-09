# Regenera landing

Static landing page built from the Claude Design file `Regenera Landing.dc.html`.

- `index.html`: the page (plain HTML/CSS/JS, no build step, no dependencies)
- `assets/regenera-logo.png`: logo, resized from the 4500px source to 1260px
- `assets/bg-video-loop.mp4`: background video (H.264, 1920x1080, 8.5s). Re-cut from
  the 10s source so its last 1.5s crossfade into the opening, which makes the
  `loop` restart seamless

## Run locally

Serve the folder over HTTP:

```bash
npx serve regenera-landing
# or
python3 -m http.server -d regenera-landing
```

Opening `index.html` straight from disk (`file://`) still shows the video. The
ripple effect stays off there, since browsers block WebGL from reading video
frames on `file://` pages.

## Tuning

The design's editable props live in the `CONFIG` object at the top of the script:

| Key | Default | Effect |
|---|---|---|
| `videoOpacity` | 40 | Background video opacity, in percent |
| `videoSpeed` | 80 | Playback rate, in percent |
| `rippleStrength` | 25 | Pointer ripple intensity, in percent |
| `showEnter` | true | Shows the divider and ENTER link |

The ENTER link points to `#` for now.
