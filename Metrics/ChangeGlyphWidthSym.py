#MenuTitle: Change glyph width (symmetrically)
# -*- coding: utf-8 -*-
__doc__="""
(GUI) Changes the width of selected glyphs symmetrically (the increase is distributed on LSB/RSB evenly).
"""

import vanilla
import GlyphsApp

class ChangeGlyphWidthSym(object):
  def __init__(self, defaultWidth = 600):
    m = 10
    t = (150, 17)
    i = (150, 22)
    b = (100, 20)
    s = (max(t[0], i[0]) + 2 * m, t[1] + i[1] + b[1] + 7 * m)
    
    self.w = vanilla.FloatingWindow(
      s, # window size
      "Change glyph width (symmetrically)", # window title
      minSize = s,
      maxSize = s,
      autosaveName = "com.fkett.ChangeGlyphWidthSym.mainwindow"
    )
    
    self.w.text = vanilla.TextBox(
      (m, m, t[0], t[1]),
      "Width",
      sizeStyle = "regular"
    )
    self.w.input = vanilla.EditText(
      (m, t[1] + 2 * m, i[0], i[1]),
      str(defaultWidth),
      sizeStyle = "regular"
    )
    self.w.run = vanilla.Button(
      (-m - b[0], -m - b[1], b[0], b[1]),
      "Change",
      sizeStyle = "regular",
      callback = self.resizeWidths
    )
    self.w.setDefaultButton(self.w.run)
    self.w.open()
    self.w.makeKey()
  
  def resizeWidths(self, sender):
    for e in Glyphs.font.selectedLayers:
      d = int(self.w.input.get()) - e.width
      p = int(d / 2)
      r = d % 2
      
      e.LSB += p + r
      e.RSB += p

ChangeGlyphWidthSym()