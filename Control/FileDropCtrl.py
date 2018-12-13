import sys,os
import wx
import pandas as pd
import re

from DropDragCtrl import DragandDrop as ddt
from collections import defaultdict

class FileListCtrl(wx.ListCtrl):
    def __init__(self,*args,**kwargs):
        super(FileListCtrl,self).__init__(*args,**kwargs)

        self.currRow = None

        self.Bind(wx.EVT_LEFT_DOWN, self.OnFindCurrentRow )
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
        self.entriesList = []
        self.numEntries = 0
        self.filename = []
        self.numCols = -1
        self.haveEntries = False
        self.supportfiletype = ['errors','xlsx','sql']

#
#
# OnFindCurrentRow and OnRightDown
    def OnFindCurrentRow(self,event): #find current row control
        if (self.currRow is not None):
            self.Select(self.currRow, False)

        row,_ignoredFlags = self.HitTest(event.GetPosition())
            # HitTest, Determine which item is at the specified point.
            # Returns index of the item or wxNOT_FOUND if no item is at the specified point.
        self.currRow = row
        self.Select(row)

    def OnRightDown(self,event): #Right click menu

        menu = wx.Menu()
        menuItem = menu.Append(-1,'Delete this file')

        self.Bind(wx.EVT_MENU, self.OnDeleteRow, menuItem)

        self.OnFindCurrentRow(event)

        self.PopupMenu(menu,event.GetPosition())

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

            allSelectedRowData.append( self.GetItemInfo(idx))

            if (len( allSelectedRowData ) >= 1) :

                #-----

                rawRowData = allSelectedRowData[ 0 ]    # There can be only a single row selected.
                lineIdx       = rawRowData[ 0 ]
                unknownData   = rawRowData[ 1 ]
                textDataTuple = tuple( rawRowData[ 2: ] )   # Make same type as in self.entriesList

                if self.numEntries :

                    try :
                        entryListIndex = None
                        entryListIndex = self.entriesList.index( textDataTuple )
                    except ValueError :
                        print ('####  ERROR:  textDataTuple NOT FOUND in self.entriesList :')
                        print (' ', textDataTuple)
                        print

                        return
                        #-----

                    #end try

                    # Delete this row item from [ self.entriesList ].
                    del self.entriesList[ entryListIndex ]

                    # Update the status vars.
                    self.numEntries -= 1
                    if (self.numEntries < 1) :

                        self.haveEntries = False
                        self.Append( self.HelpTextTuple )

                    # Finally, detete the textList row item.
                    self.DeleteItem( self.currRow )
    def GetItemInfo(self,idx):
        rowItemList = []
        rowItemList.append(idx)
        rowItemList.append(self.GetItemData(idx)) #Gets the application-defined data associated with this item
        rowItemList.append(self.GetItemText(idx)) #gets the item text for this item, Column 0 is the default

        for i in range(1,self.GetColumnCount()):
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
            fullpath = os.path.join(foldername,basename)
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




    def GetInfo(self,pathlist,type_list,path_list,name_list):
        ##test
        # pathlist = self.filedropctrl.GetEntryList()
        # a = pathlist[0][1]
        ##
        # pathlist = self.GetEntries()
        def_dict = defaultdict(list)
        excel_dict = {}
        error_dict = {}
        # sql_dict = {}
        self.big_dict = {}
        for p,f,t in pathlist:
            assert(t in self.supportfiletype), "Not support for %s file" %(t)
            # self.filename = []
            # self.filename.append(f)
            os.chdir(p)
            
            if t == 'errors':
                
                afile_list = []
                sp = {}
                
                afile = open(f,"r").readlines()
                afile_list = afile[0].split('\t')
                sp = sp.fromkeys(afile_list)
                for m in range(1,len(afile)):
                    value = []
                    value = afile[m].split('\t')
                    for n in range(len(afile_list)):
                        if sp[afile_list[n]] == None:
                            sp[afile_list[n]] = {m-1:value[n]}
                        else:
                            sp[afile_list[n]].update({m-1:value[n]}) 
                        print(sp)       
                error_dict[f] = sp
            elif t == 'xlsx':
                xl = pd.ExcelFile(f)
                sn = xl.sheet_names
                df = {}
                col = {}
                df = xl.parse(sn[0])
                excel_dict[f] = df.to_dict()  
        
        self.big_dict = error_dict.copy()
        self.big_dict.update(excel_dict)

        return self.big_dict
    def GetSQL(self,pathlist,type_list,path_list,name_list):
        self.sql_type = None
    #     keywords = [
    # 'ABSOLUTE','ACTION','ADD','AFTER','ALL','ALLOCATE','ALTER','AND','ANY','ARE','ARRAY','AS','ASC',
    # 'ASENSITIVE','ASSERTION','ASYMMETRIC','AT','ATOMIC','AUTHORIZATION','AVG','BEFORE','BEGIN',
	# 'BETWEEN','BIGINT','BINARY','BIT','BIT_LENGTH','BLOB','BOOLEAN','BOTH','BREADTH','BY','CALL',
	# 'CALLED','CASCADE','CASCADED','CASE','CAST','CATALOG','CHAR','CHARACTER','CHARACTER_LENGTH',
	# 'CHAR_LENGTH','CHECK','CLOB','CLOSE','COALESCE','COLLATE','COLLATION','COLUMN','COMMIT',
	# 'CONDITION','CONNECT','CONNECTION','CONSTRAINT','CONSTRAINTS','CONSTRUCTOR','CONTAINS',
	# 'CONTINUE','CONVERT','CORRESPONDING','COUNT','CREATE','CROSS','CUBE','CURRENT','CURRENT_DATE',
	# 'CURRENT_DEFAULT_TRANSFORM_GROUP','CURRENT_PATH','CURRENT_ROLE','CURRENT_TIME',
	# 'CURRENT_TIMESTAMP','CURRENT_TRANSFORM_GROUP_FOR_TYPE','CURRENT_USER','CURSOR',
	# 'CYCLE','DATA','DATE','DAY','DEALLOCATE','DEC','DECIMAL','DECLARE','DEFAULT','DEFERRABLE',
	# 'DEFERRED','DELETE','DEPTH','DEREF','DESC','DESCRIBE','DESCRIPTOR','DETERMINISTIC',
	# 'DIAGNOSTICS','DISCONNECT','DISTINCT','DO','DOMAIN','DOUBLE','DROP','DYNAMIC','EACH','ELEMENT',
	# 'ELSE','ELSEIF','END','EPOCH','EQUALS','ESCAPE','EXCEPT','EXCEPTION','EXEC','EXECUTE','EXISTS',
	# 'EXIT','EXTERNAL','EXTRACT','FALSE','FETCH','FILTER','FIRST','FLOAT','FOR','FOREIGN','FOUND','FREE',
	# 'FROM','FULL','FUNCTION','GENERAL','GET','GLOBAL','GO','GOTO','GRANT','GROUP','GROUPING','HANDLER',
	# 'HAVING','HOLD','HOUR','IDENTITY','IF','IMMEDIATE','IN','INDICATOR','INITIALLY','INNER','INOUT',
	# 'INPUT','INSENSITIVE','INSERT','INT','INTEGER','INTERSECT','INTERVAL','INTO','IS','ISOLATION',
	# 'ITERATE','JOIN','KEY','LANGUAGE','LARGE','LAST','LATERAL','LEADING','LEAVE','LEFT','LEVEL','LIKE',
	# 'LIMIT','LOCAL','LOCALTIME','LOCALTIMESTAMP','LOCATOR','LOOP','LOWER','MAP','MATCH','MAX',
	# 'MEMBER','MERGE','METHOD','MIN','MINUTE','MODIFIES','MODULE','MONTH','MULTISET','NAMES',
	# 'NATIONAL','NATURAL','NCHAR','NCLOB','NEW','NEXT','NO','NONE','NOT','NULL','NULLIF','NUMERIC',
	# 'OBJECT','OCTET_LENGTH','OF','OLD','ON','ONLY','OPEN','OPTION','OR','ORDER','ORDINALITY','OUT',
	# 'OUTER','OUTPUT','OVER','OVERLAPS','PAD','PARAMETER','PARTIAL','PARTITION','PATH','POSITION',
	# 'PRECISION','PREPARE','PRESERVE','PRIMARY','PRIOR','PRIVILEGES','PROCEDURE','PUBLIC','RANGE',
	# 'READ','READS','REAL','RECURSIVE','REF','REFERENCES','REFERENCING','RELATIVE','RELEASE',
	# 'REPEAT','RESIGNAL','RESTRICT','RESULT','RETURN','RETURNS','REVOKE','RIGHT','ROLE','ROLLBACK',
	# 'ROLLUP','ROUTINE','ROW','ROWS','SAVEPOINT','SCHEMA','SCOPE','SCROLL','SEARCH','SECOND','SECTION',
	# 'SELECT','SENSITIVE','SESSION','SESSION_USER','SET','SETS','SIGNAL','SIMILAR','SIZE','SMALLINT',
	# 'SOME','SPACE','SPECIFIC','SPECIFICTYPE','SQL','SQLCODE','SQLERROR','SQLEXCEPTION','SQLSTATE',
	# 'SQLWARNING','START','STATE','STATIC','SUBMULTISET','SUBSTRING','SUM','SYMMETRIC','SYSTEM',
	# 'SYSTEM_USER','TABLE','TABLESAMPLE','TEMPORARY','TEXT','THEN','TIME','TIMESTAMP',
	# 'TIMEZONE_HOUR','TIMEZONE_MINUTE','TINYINT','TO','TRAILING','TRANSACTION','TRANSLATE',
	# 'TRANSLATION','TREAT','TRIGGER','TRIM','TRUE','UNDER','UNDO','UNION','UNIQUE','UNKNOWN','UNNEST',
	# 'UNTIL','UPDATE','UPPER','USAGE','USER','USING','VALUE','VALUES','VARCHAR','VARYING','VIEW','WHEN'
    #     ]   
        for p,f,t in pathlist:
            assert(t in self.supportfiletype), "Not support for %s file" %(t)
            # self.filename = []
            # self.filename = 
            os.chdir(p)

            if t == 'sql':
                afile = open(f,"r").read()
                sql_query = re.sub('\s+',' ',afile)
                sql_qr = SQLprocess(sql_query)
                self.sql_list = sql_qr.SimpleSQLdict()
                
                
        return self.sql_list
#
#
#
class SQLprocess:

    def __init__(self,sql_query):
        self.sql_type = None
        self.sql_field = []
        self.select_no = []
        self.SIMPLE_KEYWORDS = [' JOIN ']
        self.sql_query = re.sub('\s+',' ',sql_query).upper()

    def type_check(self):
        self.sql_type = 'SIMPLE'
        for x in self.SIMPLE_KEYWORDS:
            if x in self.sql_query:
                self.sql_type = 'COMPLEX'
                return self.sql_type
            else:
                return self.sql_type
#   def Preprocess, Seperate Nest structure check status              
    def GetSQLlist(self):
        sql_type = self.type_check()
        if sql_type == 'SIMPLE':
            sql_list = re.split(r'(SELECT|FROM|WHERE|HAVING)',self.sql_query)         
            sql_simple_list = self.GetField(self.RmHeader(sql_list))

        else:
            raise Exception('Still working on ') 
        return sql_simple_list
    

    def RmHeader(self,query_list):
        self.select_no = [i for i, x in enumerate(query_list) if x == 'SELECT']
        rmPOS = self.select_no[0]
        result = query_list[rmPOS:]
        # print(result)
        return result 

    def SimpleSQLdict(self):
        sql_list = re.split(r'(SELECT|FROM|WHERE|HAVING)',self.sql_query)   
        select_no = [i for i, x in enumerate(sql_list) if x == 'SELECT']
        from_no = [i for i , x in enumerate(sql_list) if x == 'FROM']
        where_no =[i for i , x in enumerate(sql_list) if x == 'WHERE']
        self.SQLdict = defaultdict(list)
        for i in range(len(select_no)):
            table_name = sql_list[from_no[i]+1]
            field_part = sql_list[from_no[i]-1]
            if ',' in field_part:
                field_part = re.split(',',field_part)
                for j in range(len(field_part)):
                    self.SQLdict[table_name].append(field_part[j])
            else:
                self.SQLdict[table_name] = field_part

        return self.SQLdict 





    def GetField(self,query_list):
        field_list = []
        field_pos = [i-1 for i , x in enumerate(query_list) if x == 'FROM']
        for i in field_pos:
            if query_list[i] == ' * ':
                query_list[i] = 'ALL FIELDS'
            field_list.append(query_list[i])
        # field_list = re.findall(r'(?<=SELECT).*?(?=FROM)',sql_query)
        # for i in range(len(field_list)):
        #     if field_list[i] == ' * ':
        #         field_list[i] = 'ALL FIELDS'
        return field_list


    def GetTable(self,sql_list):
        select_no = [i for i, x in enumerate(sql_list) if x =='SELECT']
        pass
    pass         





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

    def ListSQL(self):
        pathlist = self.filesListCtrl.GetEntries()
        # listcol_error_meg = ''
        self.big_dict = {}
        self.type_list = []
        self.path_list = []
        self.name_list = []
        print(pathlist)
        for p,f,t in pathlist:
            assert(t in self.filesListCtrl.supportfiletype), "Not support for %s file" %(t)
            # print(type(p))
            # print(f)
            # print(t)
            self.path_list.append(p)
            self.type_list.append(t)
            self.name_list.append(f)
        # print(self.path_list,self.type_list,self.name_list)   
        num_errors = self.type_list.count('errors')
        num_xlsx = self.type_list.count('xlsx')
        num_sql = self.type_list.count('sql')

        if len(self.type_list) == num_sql:
            return self.filesListCtrl.GetSQL(pathlist,self.type_list,self.path_list,self.name_list)
        else: 
            raise Exception('Only support SQL Query!') 
            # TODO: Error frame here !

    def ListCol(self): 
        pathlist = self.filesListCtrl.GetEntries()
        # listcol_error_meg = ''
        self.big_dict = {}
        self.type_list = []
        self.path_list = []
        self.name_list = []
        print(pathlist)
        for p,f,t in pathlist:
            assert(t in self.filesListCtrl.supportfiletype), "Not support for %s file" %(t)
            # print(type(p))
            # print(f)
            # print(t)
            self.path_list.append(p)
            self.type_list.append(t)
            self.name_list.append(f)
        # print(self.path_list,self.type_list,self.name_list)   
        num_errors = self.type_list.count('errors')
        num_xlsx = self.type_list.count('xlsx')
        num_sql = self.type_list.count('sql')

        if len(self.type_list) == num_errors + num_xlsx:
            return self.filesListCtrl.GetInfo(pathlist,self.type_list,self.path_list,self.name_list)
        else: 
            raise Exception('Only support Excel or Error file!') 
            # TODO: ErrorFrame here!
        # for p,f,t in pathlist:
        #     assert(t in self.filesListCtrl.supportfiletype), "Not support for %s file" %(t)
        #     file_num.append(t)
        #     if file_num.count('errors') + file_num.count('xlsx') == len(file_num):
        #         print(file_num)
        #         return self.filesListCtrl.GetInfo(pathlist)
        #     elif file_num.count('sql') == len(file_num):
        #         print(file_num)
        #         return self.filesListCtrl.GetSQL()                    
        #     else:
        #         print(len(file_num))
        #         print(t.count('sql'))
        #         print(t.count('errors') + t.count('xlsx'))
        #         raise Exception('file type error!')

        

    # def GetInfo(self):
    #     return self.filesListCtrl.GetInfo()
    # def GetSQL(self):
    #     return self.filesListCtrl.GetSQL()    
    # def printall(self):
    #     afile = ddt.FilesDropTarget(self.filesDropTarget)
    #
    #     return afile.FilenameDropDict()

    def SetCallbackFunc(self, dropCallbacFunc = None ):
        self.filesDropTarget.SetDropTarget(ddt.FilesDropTarget(self.filesDropTarget))

        self.filesDropTarget.dropFunc = dropCallbacFunc

    def WriteHeaderLabels( self, headerLabelList ) :
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
        for i in range( len( hdrListWidened ) ) :
            hdrListWidened[ i ] += ' '     # Estimated number of spaces needed
                                            #   to fully show the header.
        # Delete the header-list-as-row-data.
        self.filesListCtrl.Append( hdrListWidened )   # Does NOT add to item/row data list.
        numRows = self.filesListCtrl.GetItemCount()
        self.filesListCtrl.DeleteItem( numRows - 1 )
    def WriteHelptext( self, helpText='Drop Files and Folders Here' ) :
        """ Write a message to be erased on the first file drop. """

        helpTextTuple = [ ' '*20, helpText ]
        self.filesListCtrl.Append( helpTextTuple )

        for col in range( 2 ) :       # Widen the column widths.
            self.filesListCtrl.SetColumnWidth( col, wx.LIST_AUTOSIZE )

        # Save for rewriting if all list entries have been deleted.
        self.filesListCtrl.HelpTextTuple = helpTextTuple
