# GSAP AI Skills (vendored)

Official GSAP agent skills from GreenSock, copied into this repo so they load
automatically in Claude Code sessions without a per-machine install.

- **Source:** https://github.com/greensock/gsap-skills
- **Commit:** `aed9cfd3277740755f6bfc1155c7aa645403b760`
- **License:** MIT (see `LICENSE`)

## Skills

| Skill | Covers |
|-------|--------|
| `gsap-core` | `gsap.to()` / `from()` / `fromTo()`, easing, duration, stagger, defaults, `matchMedia()` |
| `gsap-timeline` | Sequencing, position parameter, labels, nesting, playback control |
| `gsap-scrolltrigger` | Scroll-linked animation, pinning, scrub, refresh & cleanup |
| `gsap-plugins` | SplitText, MorphSVG, Flip, MotionPath, Draggable, and other plugins |
| `gsap-utils` | `gsap.utils.*` helpers |
| `gsap-react` | `useGSAP()`, React integration and cleanup |
| `gsap-frameworks` | Vue, Svelte, and vanilla JS integration |
| `gsap-performance` | Performance and optimization best practices |

## Updating

```bash
git clone --depth 1 https://github.com/greensock/gsap-skills /tmp/gsap-skills
cp -R /tmp/gsap-skills/skills/gsap-* .claude/skills/gsap/
cp /tmp/gsap-skills/skills/llms.txt /tmp/gsap-skills/LICENSE .claude/skills/gsap/
```

Then update the commit hash above.
