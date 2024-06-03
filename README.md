# bezier_editor
Simple demonstration of a bezier curve editor with multiple points

```
~/apps/mypyenv/bin/python3 wxpython_cairo_bezier_editor.py
```

To test under an independent X Session:

```
Xephyr -br -ac -noreset -softCursor -screen 540x960 :2

DISPLAY=:2 ~/apps/mypyenv/bin/python3 wxpython_cairo_bezier_editor.py
```
