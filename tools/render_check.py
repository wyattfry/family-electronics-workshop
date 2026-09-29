"""Render an SVG to PNG (for eyeballing diagrams): python tools/render_check.py in.svg out.png"""
import sys
import cairosvg

cairosvg.svg2png(url=sys.argv[1], write_to=sys.argv[2], output_width=1400, background_color="white")
