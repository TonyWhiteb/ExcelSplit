import sys,os
import wx
# import pandas as pd
import re

from Control import Drag_Drop as ddt
from collections import defaultdict

class FileListCtrl(wx.ListCtrl):
    def __init__(self, *args, **kwargs):
        super(FileListCtrl, self).__init__(*args, **kwargs)

        self.currRow = None

        self.Bind(wx.EVT_LEFT_DOWN, self.OnFindCurrentRow )
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        self.entriesList = []
        self.numEntries = 0
        self.filename = []
        self.numCols = -1
        self.haveEntries = False
        self.supportfiletype = ['errors', 'xlsx']

#
#
# OnFindCurrentRow and OnRightDown
    def OnFindCurrentRow(self, event): #find current row control
        if (self.currRow is not None):
            self.Select(self.currRow, False)

        row, _ignoredFlags = self.HitTest(event.GetPosition())
            # HitTest, Determine which item is at the specified point.
            # Returns index of the item or wxNOT_FOUND if no item is at the specified point.
        self.currRow = row
        self.Select(row)

    def OnRightDown(self, event): #Right click menu

        menu = wx.Menu()
        menuItem = menu.Append(-1, 'Delete this file')

        self.Bind(wx.EVT_MENU, self.OnDeleteRow, menuItem)

        self.OnFindCurrentRow(event)

        self.PopupMenu(menu, event.GetPosition())

    def OnDeleteRow(self, event):

        if(self.currRow >= 0):

            assert(self.numEntries == len(self.entriesList))

            allSelectedRowData = self.GetAllSelectedRowData()

    def GetAllSelectedRowData(self):
        allSelectedRowData = []
        idx = -1
        while True: #while True loop forever
            idx = self.GetNextItem(idx,wx.LIST_NEXT_ALL, wx.LIST_STATE_SELECTED)
            #Searches for an item with the given geometry or state,starting from item but excluding the item itself
            #if item is -1, the first item that matches the specified flags will be returned.
            #Return the first item with given state following item or -1 if no such item found.
            if (idx == -1):
                break

            allSelectedRowData.append(self.GetItemInfo(idx))

            if (len(allSelectedRowData) >= 1):

                #-----

                rawRowData = allSelectedRowData[0]    # There can be only a single row selected.
                lineIdx = rawRowData[0]
                unknownData = rawRowData[1]
                textDataTuple = tuple(rawRowData[2:])   # Make same type as in self.entriesList

                if self.numEntries:

                    try:
                        entryListIndex = None
                        entryListIndex = self.entriesList.index(textDataTuple)
                    except ValueError:
                        print('####  ERROR:  textDataTuple NOT FOUND in self.entriesList :')
                        print(' ', textDataTuple)
                        print

                        return
                        #-----

                    #end try

                    # Delete this row item from [ self.entriesList ].
                    del self.entriesList[entryListIndex]

                    # Update the status vars.
                    self.numEntries -= 1
                    if (self.numEntries < 1):

                        self.haveEntries = False
                        self.Append(self.HelpTextTuple)

                    # Finally, detete the textList row item.
                    self.DeleteItem(self.currRow)

    def GetItemInfo(self, idx):
        rowItemList = []
        rowItemList.append(idx)
        rowItemList.append(self.GetItemData(idx)) #Gets the application-defined data associated with this item
        rowItemList.append(self.GetItemText(idx)) #gets the item text for this item, Column 0 is the default

        for i in range(1, self.GetColumnCount()):
            rowItemList.append(self.GetItem(idx, i).GetText())

        return rowItemList
    #
    #
    #
    def GetAllfiles(self):
        assert(len(self.entriesList) == self.numEntries)

        for rowIdx in range(self.numEntries):

            rowData = self.entriesList[rowIdx]
            basename = rowData[0]
            self.filename.append(basename)
        return self.filename

    def GetAllRows(self):
        assert(len(self.entriesList) == self.numEntries)

        allRowsList =[]
        for rowIdx in range(self.numEntries):

            rowData = self.entriesList[rowIdx]
            basename = rowData[0]
            foldername = rowData[1]
            fullpath = os.path.join(foldername, basename)
            allRowsList.append(fullpath)

        return allRowsList

    def WriteTextTuple(self, rowDataTuple):

        assert(len(rowDataTuple) >= self.numCols), 'Given data must have at least %d items.' %(self.numCols)

        for idx in range(self.numCols):
            assert(isinstance(rowDataTuple[idx],(bytes,str))),'One or both data elements are not strings.'

        rowDataTupleTruncated = tuple(rowDataTuple[:self.numCols])
        if (rowDataTupleTruncated not in self.entriesList):

            if (not self.haveEntries):
                self.DeleteAllItems()

            self.Append(rowDataTupleTruncated)
            self.entriesList.append(rowDataTupleTruncated)
            self.numEntries += 1
            self.haveEntries = True

            self.Autosize()
    def Autosize(self):

        self.Append(self.headerLabelList)
        for colIndex in range( len( self.headerLabelList ) ) :
            self.SetColumnWidth( colIndex, wx.LIST_AUTOSIZE )

        self.DeleteItem( self.GetItemCount() - 1 )

        """
        If any one filename is very long the column width was set too long and
          occupies "too much" width in the control causing little or no display
          of the folder paths to be shown.

        Set first row's width to no more than 50% of the control's client width.
        This is a "reasonable" balance which leaves both columns's data
           at least 50% displayed at all times.
        """
        firstColMaxWid = self.GetClientSize()[ 0 ] / 2      # Half the avaiable width.
        firstColIndex = 0                           # Avoid the use of "Magic Numbers".
        firstColActualWid = self.GetColumnWidth( firstColIndex )
        reasonableWid = min( firstColMaxWid, firstColActualWid )
        self.SetColumnWidth( firstColIndex, reasonableWid )
    def GetEntries(self):
        return self.entriesList

    # def ListCol(self):
    #     pathlist = self.GetEntries()
    #     self.big_dict = {}
    #     for p,f,t in pathlist:
    #         assert(t in self.supportfiletype), "Not support for %s file" %(t)
    #         if t == 'errors' or t == 'xlsx':
    #             pass




    # def GetInfo(self,pathlist,type_list,path_list,name_list):
    #     ##test
    #     # pathlist = self.filedropctrl.GetEntryList()
    #     # a = pathlist[0][1]
    #     ##
    #     # pathlist = self.GetEntries()
    #     def_dict = defaultdict(list)
    #     excel_dict = {}
    #     error_dict = {}
    #     # sql_dict = {}
    #     self.big_dict = {}
    #     for p,f,t in pathlist:
    #         assert(t in self.supportfiletype), "Not support for %s file" %(t)
    #         # self.filename = []
    #         # self.filename.append(f)
    #         os.chdir(p)
            
    #         if t == 'errors':
                
    #             afile_list = []
    #             sp = {}
                
    #             afile = open(f,"r").readlines()
    #             afile_list = afile[0].split('\t')
    #             sp = sp.fromkeys(afile_list)
    #             for m in range(1,len(afile)):
    #                 value = []
    #                 value = afile[m].split('\t')
    #                 for n in range(len(afile_list)):
    #                     if sp[afile_list[n]] == None:
    #                         sp[afile_list[n]] = {m-1:value[n]}
    #                     else:
    #                         sp[afile_list[n]].update({m-1:value[n]}) 
    #                     print(sp)       
    #             error_dict[f] = sp
    #         elif t == 'xlsx':
    #             xl = pd.ExcelFile(f)
    #             sn = xl.sheet_names
    #             df = {}
    #             col = {}
    #             df = xl.parse(sn[0])
    #             excel_dict[f] = df.to_dict()  
        
    #     self.big_dict = error_dict.copy()
    #     self.big_dict.update(excel_dict)

    #     return self.big_dict




#
#
#

class FileDropCtrl(wx.Panel):

    def __init__(self, parent,callbackFunc = None,size = (100,200), label= 'default title', DEVEL =False ):

        super( FileDropCtrl,self).__init__(parent = parent, id =-1,style= wx.SIMPLE_BORDER)

        self.callbackFunc = callbackFunc

        fdcLabel = wx.StaticText(self,-1,label = ' '+ label, size = (-1,20))#Creating and Showing a text control

        # SetBold(fdcLabel)
        self.type_list = []
        self.path_list = []
        self.name_list = []

        fdcID = wx.NewId()
        self.filesListCtrl = FileListCtrl(self, fdcID, size= size, style = wx.LC_REPORT)

        self.filesDropTarget = self.filesListCtrl
# Layout Control
        fdcPnl_vertSzr = wx.BoxSizer(wx.VERTICAL)
        fdcPnl_vertSzr.Add(fdcLabel, proportion = 0, flag = wx.EXPAND)
        fdcPnl_vertSzr.Add(self.filesListCtrl, proportion = 1, flag = wx.EXPAND)
        fdcPnl_horzSzr = wx.BoxSizer(wx.HORIZONTAL)
        fdcPnl_horzSzr.Add(fdcPnl_vertSzr, proportion =1, flag = wx.EXPAND)
#
        self.SetSizer(fdcPnl_horzSzr) #Sets the window to have the given layout sizer
    def GetEntryList(self):
        return self.filesListCtrl.GetEntries()
    def GetAllRows(self):
        return self.filesDropTarget.GetAllRows()
    def GetAllfiles(self):
        return self.filesDropTarget.GetAllfiles()
    def GetDropTarget(self):
        return self.filesDropTarget


    # def ListCol(self): 
    #     pass

    def SetCallbackFunc(self, dropCallbacFunc = None ):
        self.filesDropTarget.SetDropTarget(ddt.FilesDropTarget(self.filesDropTarget))

        self.filesDropTarget.dropFunc = dropCallbacFunc

    def WriteHeaderLabels(self, headerLabelList):
        """ Write the column header labels. """

        self.headerLabelList = headerLabelList
        self.filesListCtrl.headerLabelList = headerLabelList

        #-----

        # This sets the "official" number of columns the textCtrl has.
        self.numCols = len( self.headerLabelList )
        self.filesListCtrl.numCols = self.numCols

        for col in range( self.numCols ) :
            self.filesListCtrl.InsertColumn( col, self.headerLabelList[ col ] )

        # AUTOSIZE
        for col in range( self.numCols ) :
            self.filesListCtrl.SetColumnWidth( col, wx.LIST_AUTOSIZE )

        # Widen the header-list-as-row-data in order to completely show the column labels.
        # This hack works very well !
        hdrListWidened = headerLabelList
        for i in range(len(hdrListWidened)):
            hdrListWidened[ i ] += ' '     # Estimated number of spaces needed
                                            #   to fully show the header.
        # Delete the header-list-as-row-data.
        self.filesListCtrl.Append( hdrListWidened )   # Does NOT add to item/row data list.
        numRows = self.filesListCtrl.GetItemCount()
        self.filesListCtrl.DeleteItem(numRows - 1)
    def WriteHelptext( self, helpText='Drop Files and Folders Here' ) :
        """ Write a message to be erased on the first file drop. """

        helpTextTuple = [ ' '*20, helpText ]
        self.filesListCtrl.Append( helpTextTuple )

        for col in range( 2 ) :       # Widen the column widths.
            self.filesListCtrl.SetColumnWidth( col, wx.LIST_AUTOSIZE )

        # Save for rewriting if all list entries have been deleted.
        self.filesListCtrl.HelpTextTuple = helpTextTuple
