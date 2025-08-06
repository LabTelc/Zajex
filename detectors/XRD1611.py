# -*- coding: utf-8 -*-
# python 2.7 #
import sys

if sys.version[0] != '2':
    raise SystemError("Python 3 is not supported.")

import numpy as np
from socket import socket, AF_INET, SOCK_STREAM
from utils import get_config
config = get_config()["Server"]
from FlatPanelFunctions import *
from FlatPanelEnums import *

sock = socket(AF_INET, SOCK_STREAM)
try:
    sock.connect((config["host"], int(config["port"])))
except Exception as e:
    print("Cannot connect to server:", e)
    exit(1)


def init_detector():
    ret, number = enum_sensors()
    if ret != 0:
        pass

    
class Detector():
    def __init__(self):    
        #self.params = params
        self.hAcqDesc = ''
        self.inputBuf = ''
        self.IsConnected = False
        self.dataReady = False
        self.data = []
        self.nRows = 4096
        self.nColumns = 4096
        self.pwOffsetData = 0
        self.pdwGainData = 0
        self.pdwPixelData = 0
        self.abortRequest = False
        self.getNext = True
        self.registeredCB = None
        
    def Init(self):
        #self.params = fp.GbIF_GetDeviceList(1)[1][0]
        #print "v Initiu"
        (iRet, self.hAcqDesc) = fp.init()
        #print "po GbIF Init"
        if iRet != 0:
            fp.close_all()   #XRD1611 very often has the problem that the channel is already occupied
            (iRet, self.hAcqDesc) = fp.init()
        if iRet == 0:
            #print "pred input buf"
            self.inputBuf = fp.define_dest_buffers(self.hAcqDesc, rows=4096, columns=4096, frames= 1)[1]         #there will be no ring buffer, but just single-frame buffer
#            #print "pred binningem"
            fp.set_camera_binning_mode(self.hAcqDesc, binning_mode= 257)         #no binning = 1 + 256
            fp.set_camera_trigger_mode(self.hAcqDesc, trigger_mode= 3)       #framewise
            fp.set_camera_gain(self.hAcqDesc, gain= 1)
            fp.set_camera_mode(self.hAcqDesc, 0)          #the base time will be timing 0
            fp.set_frame_sync_mode(self.hAcqDesc, fp.HIS_SYNCMODE_INTERNAL_TIMER)          #sets the internal timer as trigger source
            fp.set_timer_sync(self.hAcqDesc, 1000000)             #sets the timer 1 s
            self.IsConnected = True
            #print "Init finished"
        return(iRet)
        
        
    def Disconnect(self):
        fp.close(self.hAcqDesc)
        self.IsConnected = False
            
    def registerCB(self, function):
        self.registeredCB = function
        
        
        
    def cbDataReady(self, currentBuf):
        if self.registeredCB is not None:
            self.registeredCB(self.data, currentBuf)
        
    def SetCameraGain(self, wMode):
        fp.set_camera_gain(self.hAcqDesc, wMode)

    def SetBinningMode(self, wMode):
        fp.set_camera_binning_mode(self.hAcqDesc, wMode)
        #[257, 258, 514, 259, 515, 516, 517]   
        if wMode == 257:
            self.nRows = 4096
            self.nColumns = 4096
        
        if wMode == 258 or wMode == 514:
            self.nRows = 2048
            self.nColumns = 2048
            
        if wMode == 259 or wMode == 515:
            self.nRows = 1024
            self.nColumns = 1024
            
        if wMode == 516:           #mode 4 is only accumulated, but it is not clear from the manual, which number should be there
            self.nRows = 2048
            self.nColumns = 4096
            
        if wMode == 517:
            self.nRows = 1024
            self.nColumns = 4096
            
        self.inputBuf = fp.define_dest_buffers(self.hAcqDesc, frames= 1, rows= self.nRows, columns= self.nColumns)[1]  #todo bylo tam nFrames = 1       #there will be no ring buffer, but just single-frame buffer

    def SetExposureTime(self, expTime):
        fp.set_timer_sync(self.hAcqDesc, expTime)
        
    def PrepareCorrectionImages(self, pwOffsetArray = None, pdwGainArray = None, pdwPixelArray = None):
        iRet = 0
        if pwOffsetArray is not None:
            print ("novy pwOffsetData", pwOffsetArray)
            self.pwOffsetData = self.createBuffer(pwOffsetArray, "WORD")
            print('buffer', self.pwOffsetData)
        else:
            self.pwOffsetData = 0
            
        if pdwGainArray is not None:
            print ("novypdwGainData", pdwGainArray)
            pdwGainArray = np.uint32(np.median(pdwGainArray)*65536/(pdwGainArray-pwOffsetArray))
            self.pdwGainData = self.createBuffer(pdwGainArray, "DWORD")
        else:
            self.pdwGainData = 0
            
        if pdwPixelArray is not None:
            #pdwPixelArray *= 65535          #for xis, the bad pixels must have 0xFFFF value. Caution, the *= operator did not work well (changed the original data)
            pwData = self.createBuffer(pdwPixelArray*65535, "WORD") #for xis, the bad pixels must have 0xFFFF value. 
            (self.pdwPixelData, pnCorrListSize) = fp.create_pixel_map(pwData, self.nRows, self.nColumns)
            if pnCorrListSize == 0:
                (self.pdwPixelData, pnCorrListSize) = fp.create_pixel_map(pwData, self.nRows, self.nColumns)   #for binning 1x2, there was always problem when the function was called for the first time, on the second trial it worked fine
            if pnCorrListSize == 0: #if even after the next trial the function does not perform well
                iRet = 1
        else:
            self.pdwPixelData = 0
            
        return iRet
    
    def getCurrentBuffer(self):
        return(fp.get_act_frame(self.hAcqDesc)[2])
    
    def startAcq(self, dwOpt = fp.HIS_SEQ_CONTINUOUS, nIgnoreFirst = 0):        #this function is based on CallBack, it starts the acquisition and does not stop it ever!
        if fp.is_acquiring_data(self.hAcqDesc):       #any running acquisition will be aborted
            fp.abort(self.hAcqDesc)
        self.dataReady = False
        #def Acquire_Image(hAcqDesc, dwFrames = 1, dwSkipFrames = 0, dwOpt = 2, pwOffsetData = 0, pdwGainData = 0, pdwPixelData = 0)
        
        iRet = fp.acquire_image(self.hAcqDesc, frames= 1, dwSkipFrames = 0, seq_options= dwOpt, offset_data= self.pwOffsetData, gain_data= self.pdwGainData, pixel_data= self.pdwPixelData)        #dwFrames in case of HIS_SEQ_CONTINUOUS must be equal to ring buffer length (in frames). Here, the buffer is set to 1 frame.

        if iRet != 0:
            print ("Fatal error in acquisition, error code ", iRet )
            return
            
#        while (fp.GetActFrame(self.hAcqDesc)[2] < 2):        #first images ignored, as they are often defected
#            time.sleep(0.1)
#            
        T = time.time()
        
        while fp.get_act_frame(self.hAcqDesc)[2] <= nIgnoreFirst:         #some first acquisitions should be ignored, as they are defectous
            time.sleep(0.1)
        
        while not(self.abortRequest):
            f = fp.get_act_frame(self.hAcqDesc)[2]
            time.sleep(0.001)
            while (fp.get_act_frame(self.hAcqDesc)[2] == f):
                #print "cekum"
                time.sleep(0.001)            #TODO should be recoded to use time.time() to avoid idle time
            buf = self.inputBuf[0]          #as soon as possible take data    
            currentBuf = fp.get_act_frame(self.hAcqDesc)[2]
            self.data = np.array(buf).reshape((self.nRows, self.nColumns))        #there is always only one image in the array in this configuration. Reshaping needed for ctypes issues. This function is very quick (0.016 s). Needs to be done as soon as possible after new frame comes
            self.cbDataReady(currentBuf)            #this function is not running in thread, i.e., until it is not performed, the program does not go further here

        fp.abort(self.hAcqDesc)
        self.abortRequest = False
        print ("Od spusteni akvizice na detektoru to trvalo ", time.time() - T)
        
        
    def Abort(self):
        self.abortRequest = True

        
    def createBuffer(self, npArray, tipo):
        
        tupleBuf = tuple([tuple(npArray[row]) for row in range(npArray.shape[0])])   # expected here in np.array format
        if tipo == "WORD":
            c_arr = (fp.WORD*self.nColumns*self.nRows)(*tupleBuf)           #puvodne rows a colums obracene
            
        if tipo == "DWORD":
            c_arr = (fp.DWORD*self.nColumns*self.nRows)(*tupleBuf)

        return c_arr