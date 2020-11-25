#MenuTitle: Remove Outside Self-Intertsections
# -*- coding: utf-8 -*-
__doc__="""
Finds self-intersections on the outside (mind the correct path direction) of the selected glyphs and removes them.
"""

from GlyphsApp import GSPathPen

changedGlyphs = []

for thisLayer in Font.selectedLayers:
	testString = thisLayer.compareString()

	layerPaths = [p for p in thisLayer.paths]
	
	thisLayer.paths = []

	for eachPath in layerPaths:
		specialSituation = False
		
		if eachPath.nodeAtIndex_(-1).type == CURVE:
			specialSituation = True
		
		pen = GSPathPen.alloc().init()
		eachPath.drawInPen_(pen)
		eachPath = pen.layer().paths
		eachPath = eachPath[0]
		eachPath.makeNodeFirst_(eachPath.nodeAtIndex_(0))
		if specialSituation:
			eachPath.removeNodeCheckKeepShape_(eachPath.nodeAtIndex_(-2))
		thisLayer.addPath_(eachPath)

	thisLayer.checkConnections()
	
	if testString != thisLayer.compareString():
		changedGlyphs.append(thisLayer.parent.name)

if changedGlyphs:
	tabString = "/"+"/".join(set(changedGlyphs))
	Font.newTab(tabString)
else:
	Message("No outside self-intersection were found in the selected glyph(s). Thus, no changes were made.", "No outside self-intersects found", OKButton="OK")