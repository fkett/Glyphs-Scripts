#MenuTitle: Custom GASP table
# -*- coding: utf-8 -*-
__doc__="""
(GUI) Allows setting custom sizes and values for the GASP table in the custom parameter. *Important* Do not try to edit the custom parameter with the default dialogue afterwards.
"""

from AppKit import NSImage, NSPasteboard, NSArray
import vanilla
import GlyphsApp

GASP_GRIDFIT = 0x01
GASP_DOGRAY = 0x02
GASP_SYMMETRIC_GRIDFIT = 0x04
GASP_SYMMETRIC_SMOOTHING = 0x08

GASP_TEMPLATES = (
  {'title': 'Glyphs standard', 'values': ((8, 0x0A), (20, 0x07), (65535, 0X0F))},
  {'title': 'Microsoft ClearType', 'values': ((9, 0x0A), (19, 0x07), (65535, 0X0F))},
  {'title': 'Microsoft', 'values': ((8, 0x02), (16, 0x01), (65535, 0X03))},
  {'title': 'URW ClearType', 'values': ((65535, 0X0F),)},
  {'title': 'URW', 'values': ((8, 0x02), (65535, 0X03))}
)

CP_NAME_GASP_TABLE = 'GASP Table'
CP_VALUE_NEW_VALUE = 'New Value'
CP_VALUE_STD_GASP = GASP_TEMPLATES[0]['values']

class CustomGASPTable(object):
  """Sets the GASP Table custom parameter with non-standard values."""
  
  def __init__(self, f):
    # f: active font
    self.f = f
    
    self.CPLocations = self.getCPLocations()
    # [
    #   CPLocation(pointer, name, hasCP),
    #   …,
    # ]
    
    self.initiateWindow()
  
  def initiateWindow(self):
    windowWidth  = 500
    windowHeight = 300
    windowWidthResize  = 100 # user can resize width by this value
    windowHeightResize = 100 # user can resize height by this value
    metricSpacing = 10
    metricTextBoxHeight = 17
    metricListItemHeight = 17
    metricPopUpButtonHeight = 20
    metricActionButtonHeight = 20
    metricButtonHeight = 20
    metricHorizontalLineHeight = 1
    
    metricCurrentY = list()
    metricFutureY = list()
    
    self.w = vanilla.Window(
      (windowWidth, windowHeight), # default window size
      "Custom GASP Table", # window title
      minSize = (windowWidth, windowHeight), # minimum size (for resizing)
      maxSize = (windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
      autosaveName = "com.fkett.CustomGASPTable.mainwindow" # stores last window position and size
    )
    
    metricCurrentY.append(metricSpacing)
    
    metricSourceSelectWidth = 200
    metricTableReadWidth = metricButtonHeight
    self.w.sourceText = vanilla.TextBox(
      (metricSpacing, sum(metricCurrentY), -metricSpacing - metricSourceSelectWidth - metricSpacing - metricTableReadWidth - metricSpacing, metricTextBoxHeight),
      "Read custom parameter from"
    )
    self.w.sourceSelect = vanilla.PopUpButton(
      (-metricSpacing - metricSourceSelectWidth - metricSpacing - metricTableReadWidth, sum(metricCurrentY), metricSourceSelectWidth, metricPopUpButtonHeight),
      self.getCPLocationNames(True)
    )
    self.w.tableRead = vanilla.ImageButton(
      (-metricSpacing - metricTableReadWidth, sum(metricCurrentY), metricTableReadWidth, metricButtonHeight),
      imageNamed = "NSRefreshTemplate",
      callback = self.buttonTableRead
    )
    metricCurrentY.append(max(metricTextBoxHeight, metricPopUpButtonHeight, metricButtonHeight))
    metricCurrentY.append(metricSpacing)
    
    self.w.divideBar1 = vanilla.HorizontalLine((metricSpacing, sum(metricCurrentY), -metricSpacing, metricHorizontalLineHeight))
    metricCurrentY.append(metricHorizontalLineHeight)
    metricCurrentY.append(metricSpacing)
    
    metricFutureY.append(metricSpacing)
    metricFutureY.append(metricButtonHeight)
    metricFutureY.append(metricSpacing)
    metricFutureY.append(max(metricTextBoxHeight, metricPopUpButtonHeight))
    metricFutureY.append(metricSpacing)
    metricFutureY.append(metricHorizontalLineHeight)
    metricFutureY.append(metricSpacing)
    metricFutureY.append(max(metricButtonHeight, metricActionButtonHeight))
    metricFutureY.append(metricSpacing)
    
    # height: dependent on window height
    self.w.tableEntries = vanilla.List(
      (metricSpacing, sum(metricCurrentY), -metricSpacing, -sum(metricFutureY)),
      list(),
      columnDescriptions = [
        {
          "title": "<= Px / em",
          "key": "size",
        },
        {
          "title": "Gridfit",
          "key": "gridfit",
          "cell": vanilla.CheckBoxListCell(),
        },
        {
          "title": "Grayscale",
          "key": "dogray",
          "cell": vanilla.CheckBoxListCell(),
        },
        {
          "title": "Sym. Gridfit",
          "key": "symmetric_gridfit",
          "cell": vanilla.CheckBoxListCell(),
        },
        {
          "title": "Sym. Smoothing",
          "key": "symmetric_smoothing",
          "cell": vanilla.CheckBoxListCell(),
        }
      ],
      editCallback = self.tableCheckIfEmpty,
      enableDelete = False,
      allowsSorting = False,
    )
    metricFutureY.pop()

    metricTableAddRemoveItemWidth = metricButtonHeight
    self.w.tableAddItem = vanilla.ImageButton(
      (metricSpacing, -sum(metricFutureY), metricTableAddRemoveItemWidth, -sum(metricFutureY) + metricButtonHeight),
      imageNamed = "NSAddTemplate",
      callback = self.buttonTableAddItem
    )
    self.w.tableRemoveItem = vanilla.ImageButton(
      (metricSpacing + metricTableAddRemoveItemWidth + metricSpacing, -sum(metricFutureY), metricTableAddRemoveItemWidth, -sum(metricFutureY) + metricButtonHeight),
      imageNamed = "NSRemoveTemplate",
      callback = self.buttonTableRemoveItem
    )
    metricTableActionsWidth = 40
    self.w.tableActions = vanilla.ActionButton(
      (-metricSpacing - metricTableActionsWidth, -sum(metricFutureY), metricTableActionsWidth, -sum(metricFutureY) + metricActionButtonHeight),
      [
        {
          "title": "Templates",
          "items": [{"title": item["title"], "callback": self.buttonTableTemplate(key)} for key, item in enumerate(GASP_TEMPLATES)]
            #{
            #  "title": "Glyphs standard",
            #  "callback": self.buttonTableTemplate("glyphs-standard")
            #},
            #{
            #  "title": "Microsoft ClearType",
            #  "callback": self.buttonTableTemplate("microsoft-cleartype")
            #},
            #{
            #  "title": "Microsoft",
            #  "callback": self.buttonTableTemplate("microsoft")
            #},
            #{
            #  "title": "----"
            #}
            #{
            #  "title": "URW ClearType",
            #  "callback": self.buttonTableTemplate("urw-cleartype")
            #},
            #{
            #  "title": "URW",
            #  "callback": self.buttonTableTemplate("urw")
            #},
          #]
        },
        "----",
        {
          "title": "Copy Custom Parameter",
          "callback": self.buttonTableExport
        },
      ]
    )
    metricFutureY.pop()
    metricFutureY.pop()
    
    self.w.divideBar2 = vanilla.HorizontalLine((metricSpacing, -sum(metricFutureY), -metricSpacing, -sum(metricFutureY) + metricHorizontalLineHeight))
    metricFutureY.pop()
    metricFutureY.pop()
    
    metricDestinationSelectWidth = 200
    self.w.destinationText = vanilla.TextBox(
      (metricSpacing, -sum(metricFutureY), -metricSpacing - metricDestinationSelectWidth - metricSpacing, -sum(metricFutureY) + metricTextBoxHeight),
      "Write custom parameter to"
    )
    self.w.destinationSelect = vanilla.PopUpButton(
      (-metricSpacing - metricDestinationSelectWidth, -sum(metricFutureY), metricDestinationSelectWidth, -sum(metricFutureY) + metricPopUpButtonHeight),
      self.getCPLocationNames()
    )
    metricFutureY.pop()
    metricFutureY.pop()
    
    metricTableWriteButtonWidth = 200
    self.w.tableWriteButton = vanilla.Button(
      (-metricSpacing - metricTableWriteButtonWidth, -sum(metricFutureY), metricTableWriteButtonWidth, -sum(metricFutureY) + metricButtonHeight),
      "Write",
      callback = self.buttonTableWrite
    )
    
    self.tableCheckIfEmpty()
    
    self.w.setDefaultButton(self.w.tableWriteButton)
    self.w.open()
    self.w.makeKey()
  
  def tableCheckIfEmpty(self, sender = None):
    # call when table is edited
    self.w.tableWriteButton.enable(len(self.w.tableEntries) > 0)
  
  def buttonTableRead(self, sender):
    pointer = self.getCPLocationPointer(self.w.sourceSelect.get(), True)
    
    self.w.tableEntries.set(self.generateTableListFromCP(pointer[CP_NAME_GASP_TABLE]))
  
  def buttonTableAddItem(self, sender):
    self.w.tableEntries.append(
      {
        "size": "",
        "gridfit": False,
        "dogray": False,
        "symmetric_gridfit": False,
        "symmetric_smoothing": False,
      }
    )
    
    self.tableCheckIfEmpty()
  
  def buttonTableRemoveItem(self, sender):
    for i in sorted(self.w.tableEntries.getSelection(), reverse = True):
      del self.w.tableEntries[i]
    
    self.tableCheckIfEmpty()
  
  def buttonTableTemplate(self, template):
    def wrapper(sender):
      self.w.tableEntries.set(self.prepareTableListFromPairs(GASP_TEMPLATES[template]['values']))
    
    return wrapper
  
  def buttonTableExport(self, sender):
    p = NSPasteboard.generalPasteboard()
    p.clearContents()
    
    s = self.generateCPString(self.w.tableEntries)
    
    p.writeObjects_(NSArray.arrayWithObject_(s))
  
  def buttonTableWrite(self, sender):
    pointer = self.getCPLocationPointer(self.w.destinationSelect.get())
    
    if CP_NAME_GASP_TABLE in pointer:
      sheetWidth = 250
      sheetHeight = 110
      metricSpacing = 10
      metricTextBoxHeight = 17
      metricButtonHeight = 20
      metricImageViewHeight = 56
    
      self.c = vanilla.Sheet((sheetWidth, sheetHeight), self.w)
      self.c.icon = vanilla.ImageView((metricSpacing, metricSpacing, metricImageViewHeight, metricImageViewHeight), scale = 'fit')
      self.c.icon.setImage(imageNamed = 'NSCaution')
      self.c.textBox = vanilla.TextBox(
        (metricSpacing + metricImageViewHeight + metricSpacing, metricSpacing, -metricSpacing, max(metricTextBoxHeight, metricImageViewHeight)),
        "Overwrite the existing custom parameter?"
      )
      metricButtonWidth = 70
      self.c.buttonYes = vanilla.Button(
        (-metricSpacing - metricButtonWidth - metricSpacing - metricButtonWidth, -metricSpacing - metricButtonHeight, metricButtonWidth, metricButtonHeight),
        "Yes",
        callback = self.buttonOverwriteYes(pointer)
      )
      self.c.buttonNo = vanilla.Button(
        (-metricSpacing - metricButtonWidth, -metricSpacing - metricButtonHeight, metricButtonWidth, metricButtonHeight),
        "No",
        callback = self.buttonOverwriteNo
      )
    
      self.c.setDefaultButton(self.c.buttonNo)
      self.c.open()
      self.c.makeKey()
    else:
      self.writeCPToLocation(pointer)
  
  def buttonOverwriteYes(self, pointer):
    def wrapper(sender):
      self.c.close()
      del self.c
      
      self.writeCPToLocation(pointer)
    
    return wrapper
    
  def buttonOverwriteNo(self, sender):
    self.c.close()
    del self.c
  
  # GASP_GRIDFIT = 0x0001
  # GASP_DOGRAY = 0x0002
  # GASP_SYMMETRIC_GRIDFIT = 0x0004
  # GASP_SYMMETRIC_SMOOTHING = 0x0008
  # 
  # Font.customParameters["GASP Table"] = {
  #   8 : GASP_DOGRAY,
  #   65535 : GASP_DOGRAY | GASP_GRIDFIT,
  # }
  
  def prepareTableListFromPairs(self, pairList):
    l = list()
    
    for key, entry in sorted(pairList, key = lambda k: int(k[0])):
      gridfit, dogray, symmetric_gridfit, symmetric_smoothing = self.parseBitMask(entry)
      
      l.append(
        {
          "size": key,
          "gridfit": gridfit,
          "dogray": dogray,
          "symmetric_gridfit": symmetric_gridfit,
          "symmetric_smoothing": symmetric_smoothing,
        }
      )
    
    return l
  
  def generateTableListFromCP(self, customParameter):
    if customParameter == 'New Value':
      p = CP_VALUE_STD_GASP
    else:
      p = customParameter.items()
    
    return self.prepareTableListFromPairs(self, p)
  
  def generateCPFromTableList(self, tableList):
    d = dict()
    
    for entry in sorted(tableList, key = lambda k: k['size']):
      d[entry["size"]] = self.joinBitMask(entry["gridfit"], entry["dogray"], entry["symmetric_gridfit"], entry["symmetric_smoothing"])
    
    return d
  
  def generateCPString(self, tableList):
    d = self.generateCPFromTableList(tableList)
    
    s =  '(' + '\n'
    s += '    {' + '\n'
    s += '        "' + str(CP_NAME_GASP_TABLE) + '" = ' + '\n'
    s += '        {' + '\n'
    for key, entry in d.items():
      s += '            ' + str(key) + ' = ' + str(entry) + ';' + '\n'
    s += '        };' + '\n'
    s += '    }' + '\n'
    s += ')'
    
    return s
  
  def parseBitMask(self, value):
    return bool(value & GASP_GRIDFIT), bool(value & GASP_DOGRAY), bool(value & GASP_SYMMETRIC_GRIDFIT), bool(value & GASP_SYMMETRIC_SMOOTHING)
  
  def joinBitMask(self, gridfit, dogray, symmetric_gridfit, symmetric_smoothing):
    value = 0x00
    if gridfit:
      value |= GASP_GRIDFIT
    if dogray:
      value |= GASP_DOGRAY
    if symmetric_gridfit:
      value |= GASP_SYMMETRIC_GRIDFIT
    if symmetric_smoothing:
      value |= GASP_SYMMETRIC_SMOOTHING
    
    return value
  
  def writeCPToLocation(self, pointer):
    pointer[CP_NAME_GASP_TABLE] = self.generateCPFromTableList(self.w.tableEntries)
    
    self.updateCPLocations()
  
  def getCPLocations(self):
    class CPLocation(object):
      def __init__(self, **kwargs):
        self.pointer = None
        self.name = str()
        self.hasCP = bool()
      
        if 'pointer' in kwargs:
          self.pointer = kwargs['pointer']
        if 'name' in kwargs:
          self.name = str(kwargs['name'])
        if 'hasCP' in kwargs:
          self.hasCP = bool(kwargs['hasCP'])
    
    l = list()
    
    l.append(
      CPLocation(
        pointer = self.f.customParameters,
        name = 'Font: ' + str(self.f.familyName),
        hasCP = (CP_NAME_GASP_TABLE in self.f.customParameters)
      )
    )
    
    for instance in self.f.instances:
      l.append(
        CPLocation(
          pointer = instance.customParameters,
          name = 'Instance: ' + str(instance.name),
          hasCP = (CP_NAME_GASP_TABLE in instance.customParameters)
        )
      )
    
    return l
  
  def updateCPLocations(self):
    self.CPLocations = self.getCPLocations()
    
    i = self.w.sourceSelect.get()
    s = self.w.sourceSelect.getItem()
    self.w.sourceSelect.setItems(self.getCPLocationNames(True))
    try:
      self.w.sourceSelect.setItem(s)
    except:
      self.w.sourceSelect.set(i)
    
    i = self.w.destinationSelect.get()
    s = self.w.destinationSelect.getItem()
    self.w.destinationSelect.setItems(self.getCPLocationNames(False))
    try:
      self.w.destinationSelect.setItem(s)
    except:
      self.w.destinationSelect.set(i)
  
  def getCPLocationsSourceMapping(self):
    l = list()
    
    for i, location in enumerate(self.CPLocations):
      if location.hasCP:
        l.append(i)
    
    return l
  
  def getCPLocationNames(self, hasCPOnly = False):
    l = list()
    
    if hasCPOnly:
      for i in self.getCPLocationsSourceMapping():
        l.append(self.CPLocations[i].name)
    else:
      for location in self.CPLocations:
        l.append(location.name)
    
    return l
  
  def getCPLocationPointer(self, i, isCPOnly = False):
    if isCPOnly:
      j = self.getCPLocationsSourceMapping().index(i)
    else:
      j = i
    
    return self.CPLocations[j].pointer

# <-<-<-<-<-<-<-<-<-<-<-<-<-<-<-<-

font = Glyphs.font

CustomGASPTable(font)