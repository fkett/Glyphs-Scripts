#MenuTitle: Round Kerning to nearest 5
# -*- coding: utf-8 -*-
__doc__="""
Round Kerning values of the selected Master to the nearest 5 (e.g. -7 > -10, 17 > 15, 23 > 25).
"""

PRECISION = 5

font = Glyphs.font
masterId = font.selectedFontMaster.id
newKerning = list()

for leftId, kerningPair in font.kerning[masterId].items():
  for rightId, kerningValue in kerningPair.items():
    if kerningValue % PRECISION:
      newKerningValue = round(kerningValue / PRECISION) * PRECISION
      print('%s%s: was %s, now %s' % (leftId, rightId, kerningValue, newKerningValue))
      font.kerning[masterId][leftId][rightId] = newKerningValue