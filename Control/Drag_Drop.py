import os
import wx

class FilesDropTarget(wx.FileDropTarget):
    def __init__(self, targetControl):
        self.targetControl = targetControl

        wx.FileDropTarget.__init__(self)
        self.targetControl = targetControl

    # def FileContentDropDict(self):

    #     filecontentDropDict = {}
    #     filecontentDropDict['filename'] = []
    #     filecontentDropDict['colname'] = []

    #     return filecontentDropDict

    def FileDropDict(self):

        file_dict = {}

        file_dict['coord'] = (-1,-1)
        file_dict['file_dictionary'] = ''
        file_dict['basename_list'] = []
        file_dict['FullPathList'] = []
        file_dict['file_type'] = []

        return file_dict
    def OnDropFiles(self, xOrd, yOrd, pathList):

        file_dictionary, _ignored = os.path.split(pathList[0])

        basename_list = []
        file_type_list = []

        for aPath in pathList :
            _ignoredDir, aBasename = os.path.split(aPath)
            basename_list.append(aBasename)
            point = aBasename.find('.')
            file_type_list.append(aBasename[point:])


        file_dict = self.FileDropDict()
        file_dict['coord'] = (xOrd, yOrd)
        file_dict['pathList'] = pathList
        file_dict['file_dictionary'] = file_dictionary
        file_dict['basename_list'] = basename_list
        file_dict['file_type'] = file_type_list

        if (hasattr(self.targetControl, 'dropFunc' ))  and  \
           (self.targetControl.dropFunc is not None):

            # Call the callback function with the processed drop data.
            self.targetControl.dropFunc(file_dict)
