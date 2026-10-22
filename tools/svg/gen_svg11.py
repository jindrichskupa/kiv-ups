"""Figures for KIV/UPS ex11 (vzorovy test). Usage: python3 -I gen_svg11.py <out_dir>"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_svg06 as g6  # noqa: E402

g6.g.OUT = sys.argv[1]
bits = '10110010'
rows = [g6.ROW['man'], g6.ROW['nrzm']]
g6.linefig('t4-grid.svg', bits, [(*r, None) for r in rows], title='Úloha 4: nakreslete 1011 0010',
           note='NRZ-M: výchozí úroveň před prvním bitem je L.')
g6.linefig('t4-solution.svg', bits, [(*g6.ROW[c], c) for c in ('man', 'nrzm')], title='Řešení 4: 1011 0010')
