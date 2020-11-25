#MenuTitle: Calculate avar table for CSS mapping
# -*- coding: utf-8 -*-
__doc__="""
(GUI) Calculates the avar table required for mapping proprietary axis values to CSS compliant values. *Important* You must set "Variation Font Origin" (in Font) and "Axis Location" for the extreme and the default masters.
"""

# Script for avar values (weight only)
# -----
# Glyphs by default is not able to produce an avar table for mapping internal interpolation values to CSS compliant weight values.
# This script calculates the values for that avar table when the following conditions are fulfilled:
#   - Font has a custom parameter for “Variable Font Origin”
#   - Masters are ordered thinnest to boldest
#   - The extreme masters have the custom parameter “Axis Location”
#   - The defaut master has the custom parameter “Axis Location”
#   - Instances are ordered thinnest to boldest
#   - Instances are named conventionally
#
# https://forum.glyphsapp.com/t/generating-an-avar-table/9337/9

import GlyphsApp
import operator
import collections
import vanilla
from Cocoa import NSNumberFormatter

class CalculateAvarForCSS(object):
  """Calculates the avar table required for mapping proprietary axis values to CSS compliant values."""
  
  global AvarFactors
  AvarFactors = collections.namedtuple("AvarFactors", "fromValue toValue")
  
  class TargetValueData(object):
    def __init__(self, **kwargs):
      self.default = float()
      self.minimum = None
      self.maximum = None
      self.values = list()
      
      if 'default' in kwargs:
        self.default = float(kwargs['default'])
      if 'minimum' in kwargs:
        self.minimum = float(kwargs['minimum'])
      if 'maximum' in kwargs:
        self.maximum = float(kwargs['maximum'])
      if 'values' in kwargs:
        self.values = list(kwargs['values'])
  
  # targetValueData: [axis tag].values[target value] = list( name parts )
  targetValueData = {
    'wght': TargetValueData(
      default = 400,
      minimum = 1,
      maximum = 1000,
      values = (
        (50, ('hairline', 'extrathin', 'ultrathin',)),
        (100, ('thin',)),
        (200, ('extralight', 'ultralight',)),
        (300, ('light',)),
        (400, ('regular', 'normal',)),
        (500, ('medium',)),
        (600, ('semibold', 'demibold',)),
        (700, ('bold',)),
        (800, ('extrabold', 'ultrabold',)),
        (900, ('black', 'heavy',)),
        (950, ('extrablack', 'ultrablack',)),
      )
    ),
    'wdth': TargetValueData(
      default = 100,
      minimum = 0.1,
      values = (
        (50, ('compressed', 'extracondensed', 'ultracondensed',)),
        (75, ('condensed',)),
        (90, ('narrow',)),
        (100, ('',)),
        (110, ('wide',)),
        (125, ('extended',)),
        (150, ('expanded', 'extraextended', 'ultraextended',)),
      )
    ),
    'opsz': TargetValueData(
      default = 12,
      minimum = 0.1,
      values = (
        (6, ('caption',)),
        (12, ('text',)),
        (24, ('subhead',)),
        (36, ('display',)),
      )
    ),
  }
  
  def __init__(self, f):
    # f: active font
    self.f = f
    
    # targetValues: list( axis index: dict( instance index: CSS compliant value ) )
    self.targetValues = list()
    for x in self.f.axes:
      self.targetValues.append(dict())
      for j, i in enumerate(self.f.instances):
        if i.active:
          self.targetValues[-1][j] = self.getDefaultTargetValue(i, x)
    
    self.initiateWindow()
  
  def initiateWindow(self):
    windowWidth  = 400
    windowHeight = 450
    windowWidthResize  = 100 # user can resize width by this value
    windowHeightResize = 100 # user can resize height by this value
    metricSpacing = 10
    metricTextBoxHeight = 17
    metricCheckBoxHeight = 22
    metricComboBoxHeight = 21
    metricButtonHeight = 20
    metricHorizontalLineHeight = 1
    metricTabsPrefixHeight = 29
    
    metricCurrentY = list()
    
    self.w = vanilla.Window(
      (windowWidth, windowHeight), # default window size
      "Calculate avar table for CSS mapping", # window title
      minSize = (windowWidth, windowHeight), # minimum size (for resizing)
      maxSize = (windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
      autosaveName = "com.fkett.CalculateAvarForCSSMapping.mainwindow" # stores last window position and size
    )
    
    metricCurrentY.append(metricSpacing)
    self.w.checklistTitle = vanilla.TextBox((metricSpacing, sum(metricCurrentY), -metricSpacing, metricTextBoxHeight), "Checklist")
    metricCurrentY.append(metricTextBoxHeight)
    metricCurrentY.append(metricSpacing)
    
    metricChecklistBoxHeight = (3 * (metricCheckBoxHeight + metricSpacing)) - metricSpacing
    self.w.checklistBox = vanilla.Group((metricSpacing, sum(metricCurrentY), -metricSpacing, metricChecklistBoxHeight))
    self.w.checklistBox.checkFontOrigin = vanilla.CheckBox((metricSpacing, 0 * (metricSpacing + metricCheckBoxHeight), 0, metricCheckBoxHeight), "Variable Font Origin is set", value = self.hasVariableFontOrigin())
    self.w.checklistBox.checkAxisLocationAtOrigin = vanilla.CheckBox((metricSpacing, 1 * (metricSpacing + metricCheckBoxHeight), 0, metricCheckBoxHeight), "Axis Location of Font Origin Master is set", value = self.hasAxisLocationOnOrigin())
    self.w.checklistBox.checkAxisLocationAtExtremes = vanilla.CheckBox((metricSpacing, 2 * (metricSpacing + metricCheckBoxHeight), 0, metricCheckBoxHeight), "Axis Location of Extreme Masters is set", value = self.hasAxisLocationOnExtremes())
    self.w.checklistBox.checkFontOrigin.enable(False)
    self.w.checklistBox.checkAxisLocationAtOrigin.enable(False)
    self.w.checklistBox.checkAxisLocationAtExtremes.enable(False)
    metricCurrentY.append(metricChecklistBoxHeight)
    metricCurrentY.append(metricSpacing)
    
    self.w.divideBar = vanilla.HorizontalLine((metricSpacing, sum(metricCurrentY), -metricSpacing, metricHorizontalLineHeight))
    metricCurrentY.append(metricHorizontalLineHeight)
    metricCurrentY.append(metricSpacing)
    
    instanceGroupRuleList = list()
    
    metricInstanceGroupWidth = windowWidth - (4 * metricSpacing)
    metricInstanceGroupHeight = max(metricTextBoxHeight, metricComboBoxHeight)
    metricAxisTabsHeight = metricTabsPrefixHeight + metricSpacing + ((metricInstanceGroupHeight + metricSpacing) * max([len(i) for i in self.targetValues]))
    
    self.w.axisTabs = vanilla.Tabs((metricSpacing, sum(metricCurrentY), -metricSpacing, metricAxisTabsHeight), [x["Name"] for x in self.f.axes])
    for a, x in enumerate(self.f.axes):
      # PyObjC: valueFormatter = NSNumberFormatter()
      valueFormatter = NSNumberFormatter.alloc().init()
      # PyObjC: valueFormatter.minimumIntegerDigits = 1
      valueFormatter.setMinimumIntegerDigits_(1)
      valueFormatter.setMinimumFractionDigits_(1)
      valueFormatter.setMaximumFractionDigits_(1)
      valueFormatter.setAllowsFloats_(True)
      if (self.targetValueData[x["Tag"]].minimum != None):
        valueFormatter.setMinimum_(self.targetValueData[x["Tag"]].minimum)
      if (self.targetValueData[x["Tag"]].maximum != None):
        valueFormatter.setMaximum_(self.targetValueData[x["Tag"]].maximum)
      
      instanceGroupRuleList.append(list())
      for instanceCount, instanceIndex, defaultValue in [(c, t[0], t[1]) for c, t in enumerate(self.targetValues[a].items())]:
        instanceGroup = vanilla.Group((metricSpacing, metricSpacing + (instanceCount * (metricSpacing + metricInstanceGroupHeight)), -metricSpacing, metricInstanceGroupHeight))
        instanceGroup.name = vanilla.TextBox((0, (metricInstanceGroupHeight - metricTextBoxHeight) / 2, (metricInstanceGroupWidth - metricSpacing) * 0.4, metricTextBoxHeight), self.f.instances[instanceIndex].name)
        instanceGroup.defaultValue = vanilla.ComboBox(
          (-(metricInstanceGroupWidth - metricSpacing) * 0.6, (metricInstanceGroupHeight - metricComboBoxHeight) / 2, (metricInstanceGroupWidth - metricSpacing) * 0.6, metricComboBoxHeight),
          [valueFormatter.stringFromNumber_(v[0]) for v in self.targetValueData[x["Tag"]].values],
          #callback = lambda sr: self.comboboxChangeTargetValue(sr, a, instanceIndex),
          callback = self.comboboxChangeTargetValue(a, instanceIndex),
          completes = False,
          continuous = False,
          formatter = valueFormatter
        )
        instanceGroup.defaultValue.set(defaultValue)
        n = "instance" + str(instanceIndex)
        setattr(self.w.axisTabs[a], n, instanceGroup)
        instanceGroupRuleList[-1].append(n)
    metricCurrentY.append(metricAxisTabsHeight)
    metricCurrentY.append(metricSpacing)
    
    metricGenerateButtonWidth = 200
    self.w.generateButton = vanilla.Button((-metricSpacing - metricGenerateButtonWidth, -metricSpacing - metricButtonHeight, metricGenerateButtonWidth, metricButtonHeight), "Generate avar table", callback = self.buttonGenerateAvarTable)
    
    if not(self.hasVariableFontOrigin() and self.hasAxisLocationOnOrigin() and self.hasAxisLocationOnExtremes()):
      self.w.generateButton.enable(False)
    
    self.w.setDefaultButton(self.w.generateButton)
    self.w.open()
    self.w.makeKey()
  
  def comboboxChangeTargetValue(self, axisIndex, instanceIndex):
    def wrapper(sender):
      self.targetValues[axisIndex][instanceIndex] = float(sender.get())
    
    return wrapper
  
  def buttonGenerateAvarTable(self, sender):
    sheetWidth = 300
    sheetHeight = 300
    metricSpacing = 10
    metricTextEditorHeight = 250
    metricButtonHeight = 20
    
    self.c = vanilla.Sheet((sheetWidth, sheetHeight), self.w)
    self.c.console = vanilla.TextEditor((metricSpacing, metricSpacing, -metricSpacing, metricTextEditorHeight), "", readOnly = True)
    self.c.buttonClose = vanilla.Button((metricSpacing, -metricSpacing - metricButtonHeight, -metricSpacing, -metricSpacing), "Close", callback = self.buttonCloseConsoleSheet)
    
    output = list()
    avarFactors = list()
    
    for a, _ in enumerate(font.axes):
      avarFactors.append(self.calculateAxisAvarMapping(a))
    
    output.append("  <avar>")
    
    for a, f in enumerate(avarFactors):
      output.append("    <segment axis=\"%s\">   <!-- %s -->" % (self.f.axes[a]['Tag'], self.f.axes[a]['Name']))
      
      for i, v in sorted(f, key = lambda e: (e[1].fromValue, e[1].toValue)):
        output.append("      <mapping from=\"%f\" to=\"%f\"/>   <!-- %s -->" % (v.fromValue, v.toValue, (", ").join([self.f.instances[j].name for j in i])))
      
      output.append("    </segment>")
    
    output.append("  </avar>")
    
    self.c.console.set(("\n").join(output))
    self.c.open()
    self.c.makeKey()
  
  def buttonCloseConsoleSheet(self, sender):
    self.c.close()
    del self.c
  
  def getDefaultTargetValue(self, instance, axis):
    if axis['Tag'] in self.targetValueData:
      axisTargetValueData = self.targetValueData[axis['Tag']]
    
      for targetValue, targetNames in axisTargetValueData.values:
        for n in targetNames:
          if (" " + instance.name.lower() + " ").count((" " + n + " ")) > 0:
            return targetValue
            break
      return axisTargetValueData.default
    else:
      return None
  
  def hasVariableFontOrigin(self):
    return (('Variable Font Origin' in self.f.customParameters) or ('Variation Font Origin' in self.f.customParameters))

  def hasAxisLocationOnOrigin(self):
    if self.hasVariableFontOrigin():
      variableFontOrigin = self.f.customParameters['Variable Font Origin'] if ('Variable Font Origin' in self.f.customParameters) else self.f.customParameters['Variation Font Origin']
      
      return ('Axis Location' in self.f.masters[variableFontOrigin].customParameters)
    return False

  def hasAxisLocationOnExtremes(self):
    good = list()
    
    for a, _ in enumerate(self.f.axes):
      mMin = min([[m.axes[a], m] for m in self.f.masters], key = operator.itemgetter(0))
      mMax = max([[m.axes[a], m] for m in self.f.masters], key = operator.itemgetter(0))
      
      good.append(('Axis Location' in mMin[1].customParameters) and ('Axis Location' in mMax[1].customParameters))
    
    return all(good)

  # converts origin value from origin to target scale based on key data
  def fromOriginToTargetScale(self, value, originKeyData, targetKeyData):
    # value:    float
    # …KeyData: list (default, min, max)
    
    originDefault, originMin, originMax = originKeyData
    targetDefault, targetMin, targetMax = targetKeyData
    
    return (((float(value) - originMin) / (originMax - originMin)) * (targetMax - targetMin)) + targetMin

  def calculateFactors(self, originValue, targetValue, originKeyData, targetKeyData):
    # …Value:   float
    # …KeyData: list (default, min, max)
    
    originDefault, originMin, originMax = originKeyData
    targetDefault, targetMin, targetMax = targetKeyData
    
    originValueOnTargetScale = self.fromOriginToTargetScale(originValue, originKeyData, targetKeyData)
    originDefaultOnTargetScale = self.fromOriginToTargetScale(originDefault, originKeyData, targetKeyData)
    
    originValue = float(originValue)
    targetValue = float(targetValue)
    
    if originValue <= originDefault and originMin != originDefault:
      fromValue = ((targetValue - targetMin) / (targetDefault - targetMin)) - 1
      toValue = ((originValueOnTargetScale - targetMin) / (originDefaultOnTargetScale - targetMin)) - 1
    #elif originValue >= originDefault:
    else:
      fromValue = (targetValue - targetDefault) / (targetMax - targetDefault)
      toValue = (originValueOnTargetScale - originDefaultOnTargetScale) / (targetMax - originDefaultOnTargetScale)
    
    return AvarFactors(fromValue, toValue)
  
  def getAxisKeyData(self, a):
    # a: int (axis index)
    
    originMin = min([float(i.axes[a]) for i in self.f.instances])
    originMax = max([float(i.axes[a]) for i in self.f.instances])
    targetMin = min([float(m.customParameters['Axis Location'][a]['Location']) for m in self.f.masters])
    targetMax = max([float(m.customParameters['Axis Location'][a]['Location']) for m in self.f.masters])
    
    if 'Variable Font Origin' in self.f.customParameters:
      originDefault = self.f.masters[self.f.customParameters['Variable Font Origin']].axes[a]
      targetDefault = self.f.masters[self.f.customParameters['Variable Font Origin']].customParameters['Axis Location'][a]['Location']
    else:
      originDefault = self.f.masters[self.f.customParameters['Variation Font Origin']].axes[a]
      targetDefault = self.f.masters[self.f.customParameters['Variation Font Origin']].customParameters['Axis Location'][a]['Location']
    
    originKeyData = (float(originDefault), float(originMin), float(originMax))
    targetKeyData = (float(targetDefault), float(targetMin), float(targetMax))
    
    return (originKeyData, targetKeyData)

  def calculateAxisAvarMapping(self, a):
    # a: int (axis index)
    
    originKeyData, targetKeyData = self.getAxisKeyData(a)
    
    avarFactorsPerInstance = list()
    
    for j, i in enumerate(self.f.instances):
      if i.active:
        avarFactorsPerInstance.append(([j,], self.calculateFactors(i.axes[a], self.targetValues[a][j], originKeyData, targetKeyData)))
    
    # remove duplicate
    avarFactors = list()
    for e in avarFactorsPerInstance:
      if e[1] not in [f[1] for f in avarFactors]:
        avarFactors.append(e)
      else:
        avarFactors[([f[1] for f in avarFactors]).index(e[1])][0].extend(e[0])
    
    defaultFactors = (AvarFactors(-1, -1), AvarFactors(0, 0), AvarFactors(1, 1))
    for d in defaultFactors:
      if d not in [f[1] for f in avarFactors]:
        avarFactors.append(([], d))
    
    # avarFactors: tuple( list( instances ), list( factors ))
    return avarFactors

# <-<-<-<-<-<-<-<-<-<-<-<-<-<-<-<-

font = Glyphs.font

CalculateAvarForCSS(font)