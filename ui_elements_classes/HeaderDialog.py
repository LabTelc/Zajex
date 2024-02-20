import numpy as np
from PyQt5.uic import loadUiType

from utils import EZRT

Ui_HeaderDialog, QWidget = loadUiType('./ui_elements/MainWindow.ui')


class HeaderDialog(QWidget, Ui_HeaderDialog):

    def __init__(self):
        super(HeaderDialog, self).__init__()
        self.setupUi(self)

        self.ImageWidth.setEnabled(False)
        self.ImageHeight.setEnabled(False)
        self.ImageDepth.setEnabled(False)
        self.ImageHeaderLength.setEnabled(False)
        self.ImageVerMajor.setEnabled(False)
        self.ImageVerMinor.setEnabled(False)
        self.ImageVerRevision.setEnabled(False)
        self.header = EZRT.Header()

        self.updateFormValues(self.header)

        self.pb_confirmHeader.clicked.connect(self.updateHeaderFromForm)
        self.pb_close.clicked.connect(self.closeHeaderDialog)

    def updateFormValues(self, header, name=None):
        if name is not None:
            self.setWindowTitle("Header editor (header version 2.5.0)       " + name)

        h = header.Image
        self.ImageWidth.setText(str(h.siWidth))
        self.ImageHeight.setText(str(h.siHeight))
        self.ImageDepth.setText(str(h.siDepth))
        self.ImageAmount.setText(str(h.siAmount))
        self.ImageHeaderLength.setText(str(h.siHeaderLength))
        self.ImageVerMajor.setText(str(h.siVerMajor))
        self.ImageVerMinor.setText(str(h.siVerMinor))
        self.ImageVerRevision.setText(str(h.siVerRevision))

        # --------------------------------------------Meas-----------------------------%
        h = header.Meas
        self.MeasMeasId.setText(str(h.nMeasId))
        self.MeasFdd.setText(str(h.nFdd))
        self.MeasFod.setText(str(h.nFod))
        self.MeasProjectionNo.setText(str(h.nProjectionNo))
        self.MeasDetWidth.setText(str(h.nDetWidth))
        self.MeasDetHeight.setText(str(h.nDetHeight))
        self.MeasPixelsH.setText(str(h.nPixelsH))
        self.MeasPixelsV.setText(str(h.nPixelsV))
        self.MeasAreaStart.setText(str(h.nMeasAreaStart))
        self.MeasRecoLineStart.setText(str(h.nRecoLineStart))
        self.MeasRecoLineEnd.setText(str(h.nRecoLineEnd))
        self.MeasPixelWidth.setText(str(h.fPixelWidth))
        self.MeasUiAcquisitionGeom.setCurrentIndex(int(h.uiAcquisitionGeom))
        # 0: conventional 3D-CT,
        # 1: Swing Laminography,
        # 2: spiral 3D-CT (helix),
        # 100: Objekt Z-Shift
        # self.Meas.nUnused                                  = header[21]
        self.MeasLfShiftH.setText(str(h.lfShiftH))  # in pixels
        self.MeasLfShiftV.setText(str(h.lfShiftV))  # in pixels
        self.MeasLfTiltAngle.setText(str(h.lfTiltAngle))

        #        #--------------------------------------------Doku-----------------------------%
        h = header.Docu
        self.DocuNVoltage.setText(str(h.nVoltage))
        self.DocuNCurrent.setText(str(h.nCurrent))
        self.DocuNIntegrationTime.setText(str(h.nIntegrationTime))
        self.DocuNFrameAverage.setText(str(h.nFrameAverage))
        self.DocuNSkip.setText(str(h.nSkip))
        self.DocuNZPosition.setText(str(h.nZPosition))
        self.DocuNYDetPos.setText(str(h.nYDetPos))
        self.DocuNYSamplePos.setText(str(h.nYSamplePos))
        self.DocuCMeasName.setText(str(h.cMeasName))
        self.DocuCDate.setText(str(h.cDate))
        self.DocuCTime.setText(str(h.cTime))
        self.DocuNBeam.setText(str(h.nBeam))
        self.DocuFBeam.setText(str(h.fBeam))
        self.DocuNKeepData.setText(str(h.nKeepData))

        #        #--------------------------------------RekoParameter--------------------------%
        h = header.RecoParam
        self.RecoParamNXRecoNumber.setText(str(h.nXRecoNumber))
        self.RecoParamNYRecoNumber.setText(str(h.nYRecoNumber))
        self.RecoParamNZRecoNumber.setText(str(h.nZRecoNumber))
        self.RecoParamFRecNorm.setText(str(h.fRecNorm))
        self.RecoParamFVoxelX.setText(str(h.fVoxelX))
        self.RecoParamFVoxelZ.setText(str(h.fVoxelZ))

        #        #-------------------------------------------INull-----------------------------%
        h = header.I0
        self.I0UiNull.setText(str(h.uiNull))
        self.I0SiXPos.setText(str(h.siXPos))
        self.I0SiYPos.setText(str(h.siYPos))
        self.I0SiDeltaX.setText(str(h.siDeltaX))
        self.I0SiDeltaY.setText(str(h.siDeltaY))
        self.I0NAlign.setText(str(h.nAlign))

        #        #-----------------------------------------SwingLam----------------------------%
        h = header.LimitedAngle
        self.LimitedAngleLfStartAngle.setText(str(h.lfStartAngle))
        self.LimitedAngleLfAngleStep.setText(str(h.lfAngleStep))

        #        #-----------------------------------------DokuEx------------------------------%
        h = header.DocuEx
        self.DocuExSzPreFilter.setText(str(h.szPreFilter))
        self.DocuExAiReserved.setText(str(h.aiReserved))

        # ---------------------------------------RekoParamEx---------------------------%
        h = header.RecoParamEx
        self.RecoParamExFRecVolMin.setText(str(h.fRecVolMin))
        self.RecoParamExFRecVolMax.setText(str(h.fRecVolMax))
        self.RecoParamExFOffset.setText(str(h.fOffset))
        self.RecoParamExNZRecoNumMax.setText(str(h.nZRecoNumMax))
        self.RecoParamExNZFirstSlice.setText(str(h.nZFirstSlice))
        self.RecoParamExNZLastSlice.setText(str(h.nZLastSlice))
        self.RecoParamExUiCTAlgorithm.setText(str(h.uiCTAlgorithm))
        self.RecoParamExEUsedCTFilter.setText(str(h.eUsedCTFilter))
        self.RecoParamExEUsedCTAlgorithmPlatform.setText(str(h.eUsedCTAlgorithmPlatform))
        self.RecoParamExEUsedCTProjectionPadding.setText(str(h.eUsedCTProjectionPadding))
        self.RecoParamExFPaddingObjectRadius.setText(str(h.fPaddingObjectRadius))
        self.RecoParamExAiReserved.setText(str(h.aiReserved))

        #        #-------------------------------------------Helix-----------------------------%
        h = header.Helix
        self.HelixLfZShift.setText(str(h.lfZShift))
        self.HelixLfScanRange.setText(str(h.lfScanRange))
        self.HelixNProjPerZShift.setText(str(h.nProjPerZShift))
        self.HelixNAlign.setText(str(h.nAlign))

        #        #-----------------------------------------ArbitGeom---------------------------%
        h = header.ArbitGeom
        self.ArbitGeomAgvSource.setText(str(h.agvSource))
        self.ArbitGeomAgvSourceDirection.setText(str(h.agvSourceDirection))
        self.ArbitGeomAgvDetectorCenter.setText(str(h.agvDetectorCenter))
        self.ArbitGeomAgvDetLineDirection.setText(str(h.agvDetLineDirection))
        self.ArbitGeomAgvDetColumnDirection.setText(str(h.agvDetColumnDirection))
        self.ArbitGeomAgvRecoReference.setText(str(h.agvRecoReference))
        self.ArbitGeomAaRecoOrientation.setText(str(h.aaRecoOrientation))

        #        #--------------------------------------Range Extension------------------------%
        h = header.RangeExtension
        self.RangeExtensionNRangeExtensionSizeRow.setText(str(h.nRangeExtensionSizeRow))
        self.RangeExtensionNRangeExtensionSizeColumn.setText(str(h.nRangeExtensionSizeColumn))
        self.RangeExtensionNMultiscan.setText(str(h.nMultiscan))
        self.RangeExtensionNAlign.setText(str(h.nAlign))

        #        #--------------------------------------------Leer-----------------------------%
        #        h = header.Empty
        #        self.Empty.setText(str(h.Empty))

        #        #------------------------------------------Platform---------------------------%
        h = header.Platform
        self.PlatformUiEndian.setText(str(h.uiEndian))
        self.PlatformNReserved1.setText(str(h.nReserved1))
        self.PlatformUiEndi64.setText(str(h.uiEndi64))
        #
        #        #--------------------------------------------User-----------------------------%
        h = header.User
        self.User.setPlainText(str(h.strUserString))
        #        self.User.strUserString                            = header[142]#.rstrip('\x00')
        self.header = header

    def updateHeaderFromForm(self):
        h = self.header.Image
        h.siWidth = np.int16(self.ImageWidth.text())
        h.siHeight = np.int16(self.ImageHeight.text())
        h.siDepth = np.int16(self.ImageDepth.text())
        h.siAmount = np.int16(self.ImageAmount.text())
        h.siHeaderLength = np.int16(self.ImageHeaderLength.text())
        h.siVerMajor = np.int16(self.ImageVerMajor.text())
        h.siVerMinor = np.int16(self.ImageVerMinor.text())
        h.siVerRevision = np.int16(self.ImageVerRevision.text())

        #        #--------------------------------------------Meas-----------------------------%
        h = self.header.Meas
        h.nMeasId = np.int32(self.MeasMeasId.text())
        h.nFdd = np.int32(self.MeasFdd.text())
        h.nFod = np.int32(self.MeasFod.text())
        h.nProjectionNo = np.int32(self.MeasProjectionNo.text())
        h.nDetWidth = np.int32(self.MeasDetWidth.text())
        h.nDetHeight = np.int32(self.MeasDetHeight.text())
        h.nPixelsH = np.int32(self.MeasPixelsH.text())
        h.nPixelsV = np.int32(self.MeasPixelsV.text())
        h.nMeasAreaStart = np.int32(self.MeasAreaStart.text())
        h.nRecoLineStart = np.int32(self.MeasRecoLineStart.text())
        h.nRecoLineEnd = np.int32(self.MeasRecoLineEnd.text())

        h.fPixelWidth = np.float32(self.MeasPixelWidth.text())
        h.uiAcquisitionGeom = np.uint32(self.MeasUiAcquisitionGeom.currentIndex())
        # self.Meas.nUnused                                  = header[21]
        h.lfShiftH = np.float64(self.MeasLfShiftH.text())
        h.lfShiftV = np.float64(self.MeasLfShiftV.text())
        h.lfTiltAngle = np.float64(self.MeasLfTiltAngle.text())

        #        #--------------------------------------------Doku-----------------------------%
        h = self.header.Docu
        h.nVoltage = np.int32(self.DocuNVoltage.text())
        h.nCurrent = np.int32(self.DocuNCurrent.text())
        h.nIntegrationTime = np.int32(self.DocuNIntegrationTime.text())
        h.nFrameAverage = np.int32(self.DocuNFrameAverage.text())
        h.nSkip = np.int32(self.DocuNSkip.text())
        h.nZPosition = np.int32(self.DocuNZPosition.text())
        h.nYDetPos = np.int32(self.DocuNYDetPos.text())
        h.nYSamplePos = np.int32(self.DocuNYSamplePos.text())

        h.cMeasName = str(self.DocuCMeasName.text())
        h.cDate = str(self.DocuCDate.text())
        h.cTime = str(self.DocuCTime.text())
        h.nBeam = np.int32(self.DocuNBeam.text())
        h.fBeam = tuple(np.float32(eval(self.DocuFBeam.text())))
        h.nKeepData = np.int32(self.DocuNKeepData.text())

        #
        #        #--------------------------------------RekoParameter--------------------------%
        h = self.header.RecoParam
        h.nXRecoNumber = np.int32(self.RecoParamNXRecoNumber.text())
        h.nYRecoNumber = np.int32(self.RecoParamNYRecoNumber.text())
        h.nZRecoNumber = np.int32(self.RecoParamNZRecoNumber.text())
        h.fRecNorm = np.float32(self.RecoParamFRecNorm.text())
        h.fVoxelX = np.float32(self.RecoParamFVoxelX.text())
        h.fVoxelZ = np.float32(self.RecoParamFVoxelZ.text())
        #
        #        #-------------------------------------------INull-----------------------------%
        h = self.header.I0
        h.uiNull = np.uint32(self.I0UiNull.text())
        h.siXPos = np.int16(self.I0SiXPos.text())
        h.siYPos = np.int16(self.I0SiYPos.text())
        h.siDeltaX = np.int16(self.I0SiDeltaX.text())
        h.siDeltaY = np.int16(self.I0SiDeltaY.text())
        h.nAlign = np.int32(self.I0NAlign.text())
        #
        #        #-----------------------------------------SwingLam----------------------------%
        h = self.header.LimitedAngle
        h.lfStartAngle = np.float64(self.LimitedAngleLfStartAngle.text())
        h.lfAngleStep = np.float64(self.LimitedAngleLfAngleStep.text())
        #
        #        #-----------------------------------------DokuEx------------------------------%
        h = self.header.DocuEx
        h.szPreFilter = str(self.DocuExSzPreFilter.text())
        h.aiReserved = tuple(np.int32(eval(self.DocuExAiReserved.text())))

        # ---------------------------------------RekoParamEx---------------------------%
        h = self.header.RecoParamEx
        h.fRecVolMin = np.float32(self.RecoParamExFRecVolMin.text())
        h.fRecVolMax = np.float32(self.RecoParamExFRecVolMax.text())
        h.fOffset = np.float32(self.RecoParamExFOffset.text())

        h.nZRecoNumMax = np.int32(self.RecoParamExNZRecoNumMax.text())
        h.nZFirstSlice = np.int32(self.RecoParamExNZFirstSlice.text())
        h.nZLastSlice = np.int32(self.RecoParamExNZLastSlice.text())

        h.uiCTAlgorithm = np.uint32(self.RecoParamExUiCTAlgorithm.text())
        h.eUsedCTFilter = np.uint32(self.RecoParamExEUsedCTFilter.text())
        h.eUsedCTAlgorithmPlatform = np.uint32(self.RecoParamExEUsedCTAlgorithmPlatform.text())
        h.eUsedCTProjectionPadding = np.uint32(self.RecoParamExEUsedCTProjectionPadding.text())
        h.fPaddingObjectRadius = np.float32(self.RecoParamExFPaddingObjectRadius.text())
        h.aiReserved = tuple(np.int32(eval(self.RecoParamExAiReserved.text())))
        #
        #        #-------------------------------------------Helix-----------------------------%
        h = self.header.Helix
        h.lfZShift = np.float64(self.HelixLfZShift.text())
        h.lfScanRange = np.float64(self.HelixLfScanRange.text())
        h.nProjPerZShift = np.int32(self.HelixNProjPerZShift.text())
        h.nAlign = np.int32(self.HelixNAlign.text())
        #
        #        #-----------------------------------------ArbitGeom---------------------------%
        h = self.header.ArbitGeom
        h.agvSource = tuple(np.float64(eval(self.ArbitGeomAgvSource.text())))
        h.agvSourceDirection = tuple(np.float64(eval(self.ArbitGeomAgvSourceDirection.text())))
        h.agvDetectorCenter = tuple(np.float64(eval(self.ArbitGeomAgvDetectorCenter.text())))
        h.agvDetLineDirection = tuple(np.float64(eval(self.ArbitGeomAgvDetLineDirection.text())))
        h.agvDetColumnDirection = tuple(np.float64(eval(self.ArbitGeomAgvDetColumnDirection.text())))
        h.agvRecoReference = tuple(np.float64(eval(self.ArbitGeomAgvRecoReference.text())))
        h.aaRecoOrientation = tuple(np.float64(eval(self.ArbitGeomAaRecoOrientation.text())))
        #
        #        #--------------------------------------Range Extension------------------------%
        h = self.header.RangeExtension
        h.nRangeExtensionSizeRow = np.int32(self.RangeExtensionNRangeExtensionSizeRow.text())
        h.nRangeExtensionSizeColumn = np.int32(self.RangeExtensionNRangeExtensionSizeColumn.text())
        h.nMultiscan = np.int32(self.RangeExtensionNMultiscan.text())
        h.nAlign = np.int32(self.RangeExtensionNAlign.text())
        #
        #        #--------------------------------------------Leer-----------------------------%
        #        h = self.header.Empty
        #        h.Empty = self.Empty.text()

        #        #------------------------------------------Platform---------------------------%
        h = self.header.Platform
        h.uiEndian = np.uint32(self.PlatformUiEndian.text())
        h.nReserved1 = np.int32(self.PlatformNReserved1.text())
        h.uiEndi64 = np.uint64(self.PlatformUiEndi64.text())
        #
        #        #--------------------------------------------User-----------------------------%
        h = self.header.User
        h.strUserString = str(self.User.toPlainText())

        self.close()

    def closeHeaderDialog(self):
        self.close()
