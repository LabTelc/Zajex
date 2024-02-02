# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import numpy as np
from struct import unpack, pack


class Image(object):
    pass


class Meas(object):
    pass


class Docu(object):
    pass


class DocuEx(object):
    pass


class RecoParam(object):
    pass


class RecoParamEx(object):
    pass


class I0(object):
    pass


class LimitedAngle(object):
    pass


class Helix(object):
    pass


class ArbitGeom(object):
    pass


class Empty(object):
    pass


class RangeExtension(object):
    pass


class Platform(object):
    pass


class User(object):
    pass


class Header(object):
    # valid for header version 2.5.0
    decodeString = "8h11ifIi3d8i288s12s8si31f4i3fI4hi2d32s8i3f3i4If5i2d2i22d4i40sIiQ1024s"  # for the 2.5.0 version
    LoL = 400 - 16 - 64 - 64 - 24 - 176 - 16  # length of "leer" field in header
    siVerMajor = 2
    siVerMinor = 5
    siVerRevision = 0

    # define character field lengths
    nLengthMessName = 288
    nLengthDate = 12
    nLengthTime = 8
    nLengthPreFilter = 32
    nLengthUserString = 1024

    def __init__(self, headerUnpacked=None,
                 headerPacked=None):  # headerPacked is the 2048 bytes as read from a binary file, headerUnpacked is a tuple containing the decoded values

        self.Image = Image()
        self.Meas = Meas()
        self.Docu = Docu()
        self.DocuEx = DocuEx()
        self.RecoParam = RecoParam()
        self.RecoParamEx = RecoParamEx()
        self.I0 = I0()
        self.LimitedAngle = LimitedAngle()
        self.Helix = Helix()
        self.ArbitGeom = ArbitGeom()
        self.Empty = Empty()
        self.RangeExtension = RangeExtension()
        self.Platform = Platform()
        self.User = User()

        if headerUnpacked == None:
            if headerPacked == None:
                headerPacked = (np.zeros(1024, "uint16")).tostring()

            rc, headerUnpacked = self.unpackHeader(headerPacked)

        if rc == 0:
            self.setHeader(headerUnpacked)
            # print "header set"
        else:
            print("Instantiation of the class failed")

    def unpackHeader(self, headerPacked):
        try:
            headerUnpacked = unpack(Header.decodeString, headerPacked)
            return (0, headerUnpacked)
        except:
            return (-1, None)

    def setHeader(self, headerUnpacked):
        header = headerUnpacked

        try:
            # -------------------------------------------Image-----------------------------%
            self.Image.siWidth = header[0]
            self.Image.siHeight = header[1]
            self.Image.siDepth = header[2]
            self.Image.siAmount = header[3]
            self.Image.siHeaderLength = header[4]
            self.Image.siVerMajor = header[5]
            self.Image.siVerMinor = header[6]
            self.Image.siVerRevision = header[7]

            # --------------------------------------------Meas-----------------------------%
            self.Meas.nMeasId = header[8]
            self.Meas.nFdd = header[9]
            self.Meas.nFod = header[10]
            self.Meas.nProjectionNo = header[11]
            self.Meas.nDetWidth = header[12]
            self.Meas.nDetHeight = header[13]
            self.Meas.nPixelsH = header[14]
            self.Meas.nPixelsV = header[15]
            self.Meas.nMeasAreaStart = header[16]
            self.Meas.nRecoLineStart = header[17]
            self.Meas.nRecoLineEnd = header[18]
            self.Meas.fPixelWidth = header[19]
            self.Meas.uiAcquisitionGeom = header[20]
            # 0: conventional 3D-CT, 1: Swing Laminography, 2: spiral 3D-CT (helix), 100: Objekt Z-Shift
            self.Meas.nUnused = header[21]
            self.Meas.lfShiftH = header[22]  # in pixels
            self.Meas.lfShiftV = header[23]  # in pixels
            self.Meas.lfTiltAngle = header[24]

            # --------------------------------------------Doku-----------------------------%
            self.Docu.nVoltage = header[25]
            self.Docu.nCurrent = header[26]
            self.Docu.nIntegrationTime = header[27]
            self.Docu.nFrameAverage = header[28]
            self.Docu.nSkip = header[29]
            self.Docu.nZPosition = header[30]
            self.Docu.nYDetPos = header[31]
            self.Docu.nYSamplePos = header[32]
            self.Docu.cMeasName = header[33]  # .rstrip('\x00')
            self.Docu.cDate = header[34]  # .rstrip('\x00')
            self.Docu.cTime = header[35]  # .rstrip('\x00')
            self.Docu.nBeam = header[36]
            self.Docu.fBeam = header[37:68]
            self.Docu.nKeepData = header[68]

            # --------------------------------------RekoParameter--------------------------%
            self.RecoParam.nXRecoNumber = header[69]
            self.RecoParam.nYRecoNumber = header[70]
            self.RecoParam.nZRecoNumber = header[71]
            self.RecoParam.fRecNorm = header[72]
            self.RecoParam.fVoxelX = header[73]
            self.RecoParam.fVoxelZ = header[74]

            # -------------------------------------------INull-----------------------------%
            self.I0.uiNull = header[75]
            self.I0.siXPos = header[76]
            self.I0.siYPos = header[77]
            self.I0.siDeltaX = header[78]
            self.I0.siDeltaY = header[79]
            self.I0.nAlign = header[80]

            # -----------------------------------------SwingLam----------------------------%
            self.LimitedAngle.lfStartAngle = header[81]
            self.LimitedAngle.lfAngleStep = header[82]

            # -----------------------------------------DokuEx------------------------------%
            self.DocuEx.szPreFilter = header[83]  # .rstrip('\x00')
            self.DocuEx.aiReserved = header[84:92]

            # ---------------------------------------RekoParamEx---------------------------%
            self.RecoParamEx.fRecVolMin = header[92]
            self.RecoParamEx.fRecVolMax = header[93]
            self.RecoParamEx.fOffset = header[94]
            self.RecoParamEx.nZRecoNumMax = header[95]
            self.RecoParamEx.nZFirstSlice = header[96]
            self.RecoParamEx.nZLastSlice = header[97]
            self.RecoParamEx.uiCTAlgorithm = header[98]
            self.RecoParamEx.eUsedCTFilter = header[99]
            self.RecoParamEx.eUsedCTAlgorithmPlatform = header[100]
            self.RecoParamEx.eUsedCTProjectionPadding = header[101]
            self.RecoParamEx.fPaddingObjectRadius = header[102]
            self.RecoParamEx.aiReserved = header[103:108]

            # -------------------------------------------Helix-----------------------------%
            self.Helix.lfZShift = header[108]
            self.Helix.lfScanRange = header[109]
            self.Helix.nProjPerZShift = header[110]
            self.Helix.nAlign = header[111]

            # -----------------------------------------ArbitGeom---------------------------%
            self.ArbitGeom.agvSource = header[112:115]
            self.ArbitGeom.agvSourceDirection = header[115:118]
            self.ArbitGeom.agvDetectorCenter = header[118:121]
            self.ArbitGeom.agvDetLineDirection = header[121:124]
            self.ArbitGeom.agvDetColumnDirection = header[124:127]
            self.ArbitGeom.agvRecoReference = header[127:130]
            self.ArbitGeom.aaRecoOrientation = header[130:134]

            # --------------------------------------Range Extension------------------------%
            self.RangeExtension.nRangeExtensionSizeRow = header[134]
            self.RangeExtension.nRangeExtensionSizeColumn = header[135]
            self.RangeExtension.nMultiscan = header[136]
            self.RangeExtension.nAlign = header[137]

            # --------------------------------------------Leer-----------------------------%
            self.Empty = header[138]  # .rstrip('\x00')

            # ------------------------------------------Platform---------------------------%
            self.Platform.uiEndian = header[139]
            self.Platform.nReserved1 = header[140]
            self.Platform.uiEndi64 = header[141]

            # --------------------------------------------User-----------------------------%
            self.User.strUserString = header[142]  # .rstrip('\x00')

            return 0

        except Exception as e:
            print(e)
            return -1

    def getUnpacked(self):

        try:
            header = []
            header[0:8] = np.int16([
                self.Image.siWidth,
                self.Image.siHeight,
                self.Image.siDepth,
                self.Image.siAmount,
                self.Image.siHeaderLength,
                self.Image.siVerMajor,
                self.Image.siVerMinor,
                self.Image.siVerRevision
            ])

            header[8:19] = np.int32([
                self.Meas.nMeasId,
                self.Meas.nFdd,
                self.Meas.nFod,
                self.Meas.nProjectionNo,
                self.Meas.nDetWidth,
                self.Meas.nDetHeight,
                self.Meas.nPixelsH,
                self.Meas.nPixelsV,
                self.Meas.nMeasAreaStart,
                self.Meas.nRecoLineStart,
                self.Meas.nRecoLineEnd
            ])

            header[19:20] = np.float32([self.Meas.fPixelWidth])
            header[20:21] = np.uint32([self.Meas.uiAcquisitionGeom])
            header[21:22] = np.int32([self.Meas.nUnused])

            header[22:25] = np.float64([
                self.Meas.lfShiftH,
                self.Meas.lfShiftV,
                self.Meas.lfTiltAngle
            ])

            header[25:33] = np.int32([
                self.Docu.nVoltage,
                self.Docu.nCurrent,
                self.Docu.nIntegrationTime,
                self.Docu.nFrameAverage,
                self.Docu.nSkip,
                self.Docu.nZPosition,
                self.Docu.nYDetPos,
                self.Docu.nYSamplePos
            ])

            header.append(self.Docu.cMeasName)  # append here to append the whole string into one element
            header.append(self.Docu.cDate)
            header.append(self.Docu.cTime)
            header[36:37] = np.int32([self.Docu.nBeam])
            header[37:68] = np.float32(self.Docu.fBeam[0:31])

            header[68:72] = np.int32([
                self.Docu.nKeepData,
                self.RecoParam.nXRecoNumber,
                self.RecoParam.nYRecoNumber,
                self.RecoParam.nZRecoNumber
            ])

            header[72:75] = np.float32([
                self.RecoParam.fRecNorm,
                self.RecoParam.fVoxelX,
                self.RecoParam.fVoxelZ
            ])

            header[75:76] = np.uint32([self.I0.uiNull])
            header[76:80] = np.int16([
                self.I0.siXPos,
                self.I0.siYPos,
                self.I0.siDeltaX,
                self.I0.siDeltaY
            ])

            header[80:81] = np.int32([self.I0.nAlign])
            header[81:83] = np.float64([
                self.LimitedAngle.lfStartAngle,
                self.LimitedAngle.lfAngleStep
            ])

            header.append(self.DocuEx.szPreFilter)
            header[84:92] = np.int32(self.DocuEx.aiReserved[0:8])
            header[92:95] = np.float32([
                self.RecoParamEx.fRecVolMin,
                self.RecoParamEx.fRecVolMax,
                self.RecoParamEx.fOffset
            ])

            header[95:98] = np.int32([
                self.RecoParamEx.nZRecoNumMax,
                self.RecoParamEx.nZFirstSlice,
                self.RecoParamEx.nZLastSlice
            ])

            header[98:102] = np.uint32([
                self.RecoParamEx.uiCTAlgorithm,
                self.RecoParamEx.eUsedCTFilter,
                self.RecoParamEx.eUsedCTAlgorithmPlatform,
                self.RecoParamEx.eUsedCTProjectionPadding
            ])

            header[102:103] = np.float32([self.RecoParamEx.fPaddingObjectRadius])
            header[103:108] = np.int32(self.RecoParamEx.aiReserved[0:5])

            header[108:110] = np.float64([
                self.Helix.lfZShift,
                self.Helix.lfScanRange
            ])

            header[110:112] = np.int32([
                self.Helix.nProjPerZShift,
                self.Helix.nAlign
            ])

            header[112:115] = np.float64(self.ArbitGeom.agvSource[0:3])
            header[115:118] = np.float64(self.ArbitGeom.agvSourceDirection[0:3])
            header[118:121] = np.float64(self.ArbitGeom.agvDetectorCenter[0:3])
            header[121:124] = np.float64(self.ArbitGeom.agvDetLineDirection[0:3])
            header[124:127] = np.float64(self.ArbitGeom.agvDetColumnDirection[0:3])
            header[127:130] = np.float64(self.ArbitGeom.agvRecoReference[0:3])
            header[130:134] = np.float64(self.ArbitGeom.aaRecoOrientation[0:4])

            header[134:138] = np.int32([
                self.RangeExtension.nRangeExtensionSizeRow,
                self.RangeExtension.nRangeExtensionSizeColumn,
                self.RangeExtension.nMultiscan,
                self.RangeExtension.nAlign
            ])

            header.append(self.Empty)

            header[139:140] = np.uint32([self.Platform.uiEndian])
            header[140:141] = np.int32([self.Platform.nReserved1])
            header[141:142] = np.uint64([self.Platform.uiEndi64])

            header.append(self.User.strUserString)

            headerUnpacked = header

            return 0, headerUnpacked

        except Exception as e:
            print(e)
            return -1, None

    def getPacked(self):
        (rc, headerUnpacked) = self.getUnpacked()

        if rc == 0:
            try:
                headerPacked = pack(Header.decodeString, *headerUnpacked)
                return (0, headerPacked)
            except Exception as e:
                print(e)
                return (-1, None)
        else:
            print("Operation failed in getPacked")


# vytvoření souboru s hlavičkou:
#    h = np.array(range(0,1023), "uint16")  #umela hlavicka
#    hs = h.tostring()
#    mat = im.mat        #matice obrazku
#    mat = im.mat.tostring()     #vznikne to ale v tom typu, v jakem to je
#    pokud to ma byt uint16:
#        mat = np.uint16(im.mat).tostring()
#        
#    soub = hs + mat
#    with open("c:/michal/pokusraw2.raw", "wb") as soubor:
#    soubor.write(soub)

def updateHeader(path, header):
    """Updates a header of a file specified in path.
    updateHeader(path, header)
    path = path to the file
    header = instance of the class Header with the header information
    """
    with open(path, 'r+b') as soubor:
        soubor.seek(0)
        rc, headerPacked = header.getPacked()
        if rc == 0:
            soubor.write(headerPacked)
        else:
            print("Operation failed in updateHeader")


def addHeader(path, header):
    """Adds header to a file specified in the path.
    writeHeader(path, header)
    path = path to the file
    header = instance of the class Header with the header information
    """

    with open(path, 'r+b') as soubor:
        image = soubor.read()
        soubor.seek(0)
        rc, headerPacked = header.getPacked()
        if rc == 0:
            newFile = headerPacked + image
            soubor.write(newFile)
        else:
            print("Operation failed in addHeader")


def readHeader(path):
    with open(path, 'rb') as soubor:
        headerPacked = soubor.read(2048)

    header = Header(headerPacked=headerPacked)
    return header


##############################################################################################################


def getHeaderVersion(path):
    with open(path) as s:
        s.seek(10)
        version = np.fromfile(s, 'uint16', 3)

    version = 100 * version[0] + 10 * version[1] + version[2]
    return str(version)


def loadImageOnly(path, header):
    with open(path, 'rb') as soubor:
        s = np.fromfile(soubor, 'uint16')

    s = s[-header.Image.width * header.Image.height:]
    s = s.reshape((header.Image.height, header.Image.width))

    return s


def loadImage(path):
    typeList = ['int8', 'int16', 'int32', 'int64', 'uint8', 'uint16', 'uint32', 'uint64', 'float8', 'float16',
                'float32', 'float64']

    with open(path, 'rb') as soubor:
        souborAll = soubor.read()

    headerPacked = souborAll[:2048]
    header = Header(headerPacked=headerPacked)
    dataType = 'uint16'  # default
    for dataTypeTemp in typeList:
        if dataTypeTemp in header.User.strUserString[:8]:
            dataType = dataTypeTemp

    # dataType = header.User.strUserString[:8].rstrip('\x00')
    # first 8 characters in user string reserved for data type information

    matrix = np.fromstring(souborAll[2048:], dataType)
    matrix = matrix.reshape((header.Image.siHeight, header.Image.siWidth))

    return header, matrix
