# Branding generators

Scripts that draw the Portgeist mascot, README banner, social preview, and terminal
screenshot. They are maintenance tooling only and are not part of the `ghostport`
package. Pillow is required here and is not a GhostPort dependency.

```bash
python -m pip install -r tools/branding/requirements.txt
cd tools/branding
python make_sprite.py    # master 32x32 sprite and previews
python make_banner.py    # 1600x600 README banner
python make_step3.py     # mascot states, idle animation, social preview, terminal screenshot
```

Generated images are written next to the scripts and are ignored by Git. The approved,
committed copies live in `assets/`.

`terminal_capture.ansi` is the recorded output of
`ghostport inspect 8765 --http --expect-json` against a temporary local JSON server.
`make_step3.py` renders it into `terminal_screenshot.png` using the Windows Consolas
font; adjust the font paths to render on another platform.
