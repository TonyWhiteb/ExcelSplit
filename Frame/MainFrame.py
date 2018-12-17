import sys,os
import wx

from Control import FileDropCtrl as fdctrl
from Control import Drag_Drop as ddt
import  wx.lib.mixins.listctrl  as  listmix
from collections import defaultdict

try :                   # For shortening long paths in MSW, only.
    import win32api
    ntGetShortpathname = win32api.GetShortPathName
except :
    ntGetShortpathname = None


class AppFrame(wx.Frame):

    def __init__(self, args, argc, title = 'Demo', file_path = None):


        self.file_path = file_path
        super(AppFrame, self).__init__(parent = None, id= -1, title = title, pos=(800, 400))
        self.SetClientSize((650, 400))
        frmPanel = wx.Panel(self, -1)
        frmPanel.SetName('frmPanel')
        frmPanel.SetBackgroundColour(wx.WHITE)
        #
        self.filesAndLinks = list()
        self.exeFolder = None
        self.incFoldersList = list()
        self.filename = []
        # create the basic panel and go to create first control
        self.filedropctrl = fdctrl.FileDropCtrl(frmPanel,size = (50,200), label='Any Files and Links :')
        self.filedropctrl.SetName('AppFrame::self.filesDropCtrl')
        #Create the sub panel for list control
        self.filedropctrl.SetCallbackFunc(self.OnFilesDropped)
        # self.filedropctrl.SetBackgroundColour(wx.BLUE)
        headerLabelList = [  'Parent Path','File or Link Name','File Type' ]
        self.filedropctrl.WriteHeaderLabels( headerLabelList )

        srcFilesHelpText = 'Drop Files and Links Here'
        self.filedropctrl.WriteHelptext( srcFilesHelpText )

        onButtonSplit = self.OnSplitButton

        self.buttonPanel = ButtonPanel(frmPanel, onButtonSplit = onButtonSplit)
        #
        #Frame layout control
        #
        frmPnl_vertSzr = wx.BoxSizer( wx.VERTICAL )
        frmPnl_vertSzr.AddSpacer( 10 ) #space on the top
        frmPnl_vertSzr.Add(self.filedropctrl, flag = wx.EXPAND) #insert sub panel
        frmPnl_vertSzr.AddSpacer(10) #space on the bottom
        frmPnl_vertSzr.Add( self.buttonPanel,    flag=wx.EXPAND )
        frmPnl_vertSzr.AddSpacer( 10 )

        frmPnl_outerHorzSzr = wx.BoxSizer( wx.HORIZONTAL )
        frmPnl_outerHorzSzr.AddSpacer( 10 )     # space on the left
        frmPnl_outerHorzSzr.Add( frmPnl_vertSzr, proportion=1 )
        frmPnl_outerHorzSzr.AddSpacer( 10 ) #space on the right
        #
        #
        #
        frmPanel.SetSizerAndFit( frmPnl_outerHorzSzr )
        self.Show()

    def OnFilesDropped(self, file_dict):

        dropTarget = self.filedropctrl.GetDropTarget()

        dropCoord = file_dict[ 'coord' ]                 # Not used as yet.
        pathList = file_dict[ 'pathList' ]
        leafFolderList = file_dict[ 'basename_list' ]     # leaf folders, not basenames !
        commonPathname = file_dict[ 'file_dictionary' ]
        filetype = file_dict['file_type']

        if (os.name == 'nt')  and  (ntGetShortpathname != None) :
            if (len( commonPathname ) > 40) :             # Set an arbitrary max width.
                commonPathname = ntGetShortpathname( commonPathname )

        # Write (.append) a text 2-element list for each basename
        for aPath in pathList :     # May include folders.

            # Keep just files and link files.
            if not os.path.isdir( aPath ) :

                if (aPath not in self.filesAndLinks) :
                    self.filesAndLinks.append( aPath )

                _longFormParentPath, basename = os.path.split( aPath )
                namelist = basename.split('.')
                afiletype = namelist[len(namelist)-1]
                textTuple = (commonPathname, basename, afiletype)
                dropTarget.WriteTextTuple( textTuple )





        # col1 = []
        # col2 = []
        # col3 = []
        # for i in range(len(pathlist)):
        #     os.chdir(ntGetShortpathname(pathlist[i][1]))
        #     afile = open(pathlist[i][0],"r").readlines()
        #     col1 = afile[0].split('\t')
        #     col3 = list(set(col1)|set(col2))
        #     col2 = col1




    def OnSplitButton(self, event):
        currentDictiory = os.getcwd()

        dlg = wx.FileDialog(
            self, message = 'Save File As',
            defaultDir = currentDirctory,
            defaultFile = "", wildcard = "Excel files (*.xlsx)|*.xlsx",
            style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
        )
        pass
        # print(big_dict)






#
#
#
class ButtonPanel(wx.Panel):

    def __init__(self, parent= None, id= -1, onButtonSplit = None):

        super(ButtonPanel, self).__init__(parent = parent, id = id)

        listAllBtn = wx.Button(self, -1, 'Split File')

        listAllBtn.Bind(wx.EVT_LEFT_DOWN, onButtonSplit)
        # SQLBtn.Bind(wx.EVT_LEFT_DOWN, onButtonSQL)

        btnPanel_innerHorzSzr = wx.BoxSizer( wx.HORIZONTAL )
        btnPanel_innerHorzSzr.AddStretchSpacer( prop=1 )
        btnPanel_innerHorzSzr.Add( listAllBtn )
        btnPanel_innerHorzSzr.AddSpacer( 100 )

        btnPanel_innerHorzSzr.AddStretchSpacer( prop=1 )

        btnPanel_outerVertSzr = wx.BoxSizer( wx.VERTICAL )
        btnPanel_outerVertSzr.AddSpacer( 5 )
        btnPanel_outerVertSzr.Add( btnPanel_innerHorzSzr, flag=wx.EXPAND )
        btnPanel_outerVertSzr.AddSpacer( 5 )

        self.SetSizer( btnPanel_outerVertSzr )
        self.Layout()
