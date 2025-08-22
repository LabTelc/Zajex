# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 11:47:38 2017

@author: Vopalensky
@author: Zajicek
"""
# python 2.7 #
import sys

if sys.version[0] != '2':
    raise SystemError("Python 3 is not supported.")

from FlatPanelCommon import *
from FlatPanelStructures import GbifDetectorProperties, GbifDeviceParam, CHwHeaderInfo
from FlatPanelEnums import *


def gb_if_get_device_count():
    """
    
    This function retrieves the total number of sensors found in the network by a network broadcast.
    If more than one network adapter are installed, a broadcast will be performed on all of them.
        
    """
    temp = c_long()
    ret = xis.Acquisition_GbIF_GetDeviceCnt(byref(temp))
    return ret, temp.value


def gb_if_get_device_list(n_device_count):
    """
    
    This function retrieves a list of parametr structures for all GbIF detector devices found by a
    network broadcast. If multiple network adapters are used in the host system, all of them are
    checked for connection GbIF tomography.
    
    input parameters:
    GBIF_DEVICE_PARAM
        Returns a list of GBIF_DEVICE_PARAM elements, with nDeviceCnt entries. For that
        there has to be memory allocated of the size nDeviceCnt*sizeof(GBIF_DEVICE_PARAM)
        before calling the function.
    nDeviceCnt
        Is the number of devices, which are found within the network. This parameter has to be
        passed to the function. It can be retrieved by calling GbIF_GetDeviceCnt.
   
        
    """
    temp = (GbifDeviceParam * n_device_count)()
    ret = xis.Acquisition_GbIF_GetDeviceList(byref(temp), n_device_count)
    return ret, temp


def gb_if_init(channel_number=0, enable_irq=True, rows=0, columns=0, self_init=True, always_open=False,
               init_type=GbIFInitType.IP, address=''):
    """
    
    The function GbIF_Init initializes the Ethernet connected sensors (xx22) and the corresponding drivers.
    It prepares acquisition threads, defines callback functions to react on acquisition status changes:
    Furthemore it tests for sufficient memory space for DMA (direct memory access) and enables hardware interrupts if this modus is demanded.
    
    input parameters:
    handle
        Handle of a structure that contains all needed parameters for acquisition (HACQDESC).
        If you call GbIF_Init the first time set handle to NULL, in subsequent calls use the former returned value.
    channel_number
        This parameter defines a number to refer to the initialized device. For each GbIF sensor
        to be initialized an individual channel number has to be assigned. If you try to access
        multiple sensors using the same channel number, only the first tone will be successully
        initialized.
    EnableIRQ
        To run the acquisition in polling mode set this parameter to zero.
        To enable hardware interrupts set the parameter to one.
    Rows, Columns
        Number rows and columns of the sensor.
    SelfInit
        If bSelfInit is set to true the function retrieves the detector parameters (Rows,
        Columns,SortFlags) automatically.
        If bSelfInit is set to false the configuration parameters supplied by Rows, Columns,
        dwSortFlags are used.
    AlwaysOpen
        If this parametr is TRUE the XISL is capturing the requested communication port
        regardless if this port is already opened by other processes running on the system.
        The use of this option is only recommended in debug versions of your applications because it
        is not possible to free all system resources allocated by another process.
    InitType
        To identify of which type the parameter cAddress is, lInitType
        can have the following values:
        HIS_GbiF_IP     The sensor is opened using the IP-Address passed in cAddress
        HIS_GbIF_MAC    The sensor is opened using the MAC-Address passed in cAddress
        HIS_GbIF_NAME   The sensor is opened using the Detector-Name passed in cAddress
        All values are defined within the file acq.h IP-Address, MAC-Address and Detector
        Name can be retrieved by GbIF_GetDeviceList
    Address
        Address (array of 16 characters) to open the specified board. It can represent the MAC
        address, IP address or device name of the sensor.
    
    Return Value
        If the initialization is successful zero is returned, otherwise the return value is greater.
        Call Acquisition_Get_ErrorCode to get extended information.
        
    """
    temp = HACQDESC()
    ret = xis.Acquisition_GbIF_Init(byref(temp), channel_number, enable_irq, rows, columns, self_init, always_open,
                                    init_type, address)
    return ret, temp


def gb_if_get_device(address, address_type=GbIFInitType.IP):
    """
    
    This function retrieves the device parameter struct for the detector specified by the passed
    address.
    
    input parameters:
    ucAddress
        Address (array of 16 characters) to open the specified board. It can represent the MAC
        address, IP address or device name of the sensor.
    dwAddressType
        To identify of which type the parameter ucAddress is, lInitType
        can have the following values:
        HIS_GbIF_IP     The sensor is selected by the IP-Address passed in cAddress
        HIS_GbIF_MAC    The sensor is selected by the MAC-Address passed in cAddress
        HIS_GbIF_NAME   The sensor is selected by the Detector-Name passed in cAddress
        All values are defined within the file acq.h IP-Address, MAC-Address and Detector
        Name can be retrieved by GbIF_DeviceList.
   
    Return Value
        If the initialization is successful zero is returned, otherwise the return value is greater.
        Call Acquisition_GetErrorCode to get extended information.
        
    """
    temp = GbifDeviceParam()
    ret = xis.Acquisition_GbIF_GetDevice(address, address_type, byref(temp))
    return ret, temp


def gb_if_get_device_params(handle):
    """
    
    This function retrieves the device parameters of a board that has already been opened.
    
    input parameters:
    handle
        Pointer to acquisition descriptor structure
        
    """
    temp = GbifDeviceParam()
    ret = xis.Acquisition_GbIF_GetDeviceParams(handle, byref(temp))
    return ret, temp


### funkce SetConnectionSettings nefunguje, TODO: zkusit znova
def gb_if_set_connection_settings(mac, ui_boot_options, def_ip, def_sub_net_mask, std_gateway):
    """
    
    This function provides the parameters to configure how the detector connects to the network
    adapter.
    
    input parameters:
    cMAC
        MAC address of the device to be configured.
    uiBootOptions
        OR-able flag to set the type of connection bit-wisely:
            HIS_GbIF_IP_STATIC - Use Static IP address stored in the sensor
            HIS_GbIF_IP_LLA - Sensor will propose a Local Link Address
            HIS_GbIF_IP_DHCP - Sensor will receive IP address by DHCP server
    cDefIP
        In case uiBootOptions is equal to HIS_GbIF_IP_STATIC, cDefIP can be used to set a new
        value as static IP. For that, cDefIP has to contain an IP address when calling the function.
    cDefSubNetMask
        In case uiBootOptions is equal to HIS_GbIF_IP_STATIC, cDefSubNetMask
        can be used to set a new value as static IP. For that, cDefSubNetMask has to contain an IP
        address when calling the function.
    cStdGateway
        In case uiBootOptions is equal to HIS_GbIF_IP_STATIC, cStdGateway can be used to set
        a new value as static IP. For that, cStdGateway has to contain an IP address when calling
        the function. When cStdGateway is zero the detector will be able to be initialized by
        Acquisition_EnumSensors(..)
    
    Return value
        If the initialization is successful zero is returned, otherwise the return value is greater.
        Call Acquisition_GetErrorCode to get extended information.
    
    """
    return xis.Acquisition_GbIF_SetConnectionSettings(mac, ui_boot_options, def_ip, def_sub_net_mask, std_gateway)


def gb_if_get_connection_settings(mac):
    """
    
    This function retrieves the connection parameters of a GbIF detector.
    
    Input parameters:
    ucMAC
        MAC address of the device having the requested settings.
    
        
    Returns:
        (ret, ui_boot_options, uc_def_ip, uc_def_sub_net_mask, uc_std_gateway)
        Return values
        If the function is successful it returns zero, otherwise an error code. To get extended
        information call Acquisition_GetErrorCode.
    
    ret (int)
        If the initialization is successful zero is returned, otherwise the return value is greater.
        Call Acquisition_GetErrorCode.
    ui_boot_options (string)
        OR-able flag indicating the type of connection bit-wisely:
            HIS_GbIF_IP_STATIC - Use Static IP address stored in the sensor
            HIS_GbIF_IP_LLA - Sensor will propose a Local Link Address
            HIS_GbIF_IP_DHCP - Sensor will receive IP address by DHCP server
    uc_def_ip (string)
        Retrieves the IP address the device is connected with.
    uc_def_sub_net_mask (string)
        Retrieves the Subnet the device is in.
    uc_std_gateway (string)
        Retrieves the Standard Gateway of the connection to the device.
        
    """
    ui_boot_options = c_ulong()
    uc_def_ip = (GBIF_STRING_DATATYPE * GBIF_IP_MAC_NAME_CHAR_ARRAY_LENGTH)()
    uc_def_sub_net_mask = (GBIF_STRING_DATATYPE * GBIF_IP_MAC_NAME_CHAR_ARRAY_LENGTH)()
    uc_std_gateway = (GBIF_STRING_DATATYPE * GBIF_IP_MAC_NAME_CHAR_ARRAY_LENGTH)()
    ret = xis.Acquisition_GbIF_GetConnectionSettings(mac, byref(ui_boot_options), byref(uc_def_ip),
                                                     byref(uc_def_sub_net_mask), byref(uc_std_gateway))
    return ret, ui_boot_options.value, uc_def_ip.value, uc_def_sub_net_mask.value, uc_std_gateway.value


# funkce ForceIP nefunguje, ale probehne bez chyby, TODO: potřeba zkusit znova, detektor na switch s RTG
def gb_if_force_ip(mac, def_ip, def_sub_net_mask, std_gateway):
    """

    To configure the device it can be helpful to force the device temporarily to connect with a certain
    IP Address, usually one out of the same subnet and with the same StdGateway like the network
    card of your computer system. With restart of the detector the device will loose the temporary IP
    and behave as configured (e.g. IP per DHCP or LLa).          
    
    input parameters:    
    cMAC
        MAC address of the device to retrieve a temporary IP.
    cDefIP
        Temporary IP
    cDefSubNetMask
        Temporary Subnet Mask
    cStdGateway
        Temporary Gateway
    
    Return values
        If the function is successful it returns zero, otherwise an error code. To get extended
        information call Acquisition_GetErrorCode.  
        
    """
    return xis.Acquisition_GbIF_ForceIP(mac, def_ip, def_sub_net_mask, std_gateway)


def gb_if_set_packet_delay(handle, packet_delay):
    """
    
    The Inter-Packet Delay can be set flexibly to balance out the workload of the IP connection
    between detector and network adapter. It is recommended to be configured depending on the
    network load. The value can be retrieved by calling GbIF_CheckNetworkSpeed.
    
    input parameters:
    handle
        Pointer to acquisition descriptor structure
    IPacketdelay
        Value for Inter-Packet Delay, which is to be set in the unit TICKS.
    
    Return Value
        If the initialization is successful zero is returned, otherwise the return value is greater.
        Call Acquisition_GetErrorCode.
    
    """
    return xis.Acquisition_GbIF_SetPacketDelay(handle, packet_delay)


def gb_if_get_packet_delay(handle):
    """
    
    Retrieve the InterPacket Delay, which is set for the current data connection.
    
    input parameters:
    handle
        Pointer to acquisition descriptor structure
    
    Return values
        If the function is successful it returns zero, otherwise an error code. To get extended
        information call Acquisition_GetErrorCode.
    
    """
    temp = c_long()
    ret = xis.Acquisition_GbIF_GetPacketDelay(handle, byref(temp))
    return ret, temp.value


def gb_if_check_network_speed(handle, max_network_load_percent=80):
    """
    
    This function determines which Detector Timing and Packet delay can be set for the current
    system and network configuration. Please note that this function is intended for one detector only.
    If more than one detector is connected to the network adapter (detector  in LAN), the parameter
    IMaxNetworkPercent must divided by the number of connected sensors. Since the network load
    might change during operation this function cannot guarantee optimal performance. Use
    GbiF_SetPacketDelay and SetCameraMode(..) to apply the determined settings.
    
    input parameters:
    handle
        Pointer to acquisition descriptor structure
    IMaxNetworkPercent
        Percentage of Network load for which the Packet Delay shall be checked.
        To allow a stable data transmissions with some space for packet resend select~80 percent
   
    Returns:
    Return values
        If the function is successful it returns zero, otherwise an error code. To get extended
        information call Acquisition_GetErrorCode.
    timing (string)
        Pointer to suggested Free Running Timing for actual System Performance
    IPacketDelay (string)
        Pointer to calculated max InterPacketDelay for suggested timing

    """
    timing = WORD()
    packet_delay = c_long()
    ret = xis.Acquisition_GbIF_CheckNetworkSpeed(handle, byref(timing), byref(packet_delay), max_network_load_percent)
    return ret, timing.value, packet_delay.value


def gb_if_get_detector_properties(handle):
    """
    
    This function fills the GbIF_DetectorProperties structure, which contains permanently stored
    information of the connected device.
    
    input parameters:
    handle
        Pointer to acquisition descriptor structure
        
    Return values
        If the function is successful it returns zero, otherwise an error code. To get extended
        information call Acquisition_GetErrorCode.

    """

    temp = GbifDetectorProperties()
    ret = xis.Acquisition_GbIF_GetDetectorProperties(handle, byref(temp))
    return ret, temp


def gb_if_get_filter_drv_state(handle):
    """
    
    This function returns the status of the GbIF filter driver (if installed) otherwise an Error Code.
    
    input parameters:
    handle
        Pointer to acquisition descriptor structure
    
    Return Value
        If the initialization is successful it returns the status of the Filter driver.
        1 for active, -1 for disabled / not installed
        If the function is not included in gbif.dll of the HACQDESC is not valid an Error Code is
        returned.
        
    """
    return xis.Acquisition_GbIF_GetFilterDrvState(handle)


def get_configuration(handle):
    """
    This function retrieves all important acquisition parameters, that can be set by Acquisition_Init or that are set by the self configuration mechanisms of the XISL.
    """
    frames = UINT()
    rows = UINT()
    columns = UINT()
    data_type = UINT()
    sort_flags = UINT()
    irq_enabled = BOOL()
    acq_type = DWORD()
    system_id = DWORD()
    sync_mode = DWORD()
    hw_access = DWORD()

    ret = xis.Acquisition_GetConfiguration(handle, byref(frames), byref(rows), byref(columns),
                                           byref(data_type), byref(sort_flags), byref(irq_enabled), byref(acq_type),
                                           byref(system_id), byref(sync_mode), byref(hw_access))
    # data_type - always 2 for uint16
    # acq_type - internal use
    # system_id - internal use
    # hw_access - internal use
    return ret, frames.value, rows.value, columns.value, sort_flags.value, irq_enabled.value, sync_mode.value


def get_hw_header_info(handle):
    """
    
    This function returns the contents of the detector's hardware header in a CHwHeaderInfo
    structure
    
    Return value
        If the function is successful it returns zero, otherwise an error code. To get extended
        information call Acquisition_GetErrorCode.
    """
    temp = CHwHeaderInfo()
    ret = xis.Acquisition_GetHwHeaderInfo(handle, byref(temp))
    return ret, temp


def define_dest_buffers(handle, dest_buffer, frames, rows, columns):
    """
    
    This function defines the pointers of the destination buffer for Acquire_Image. The
    data are written into this buffer after sorting. The buffer must have a proper size depending on
    acquisition mode. To acquire one image the buffer must have the size sensor rows * sensor
    columns *2. To acquire a sequence the buffer must have the size sensor rows * sensor columns *2
    * frames. In the case of continuous acquisition the buffer must have the size sensor rows * sensor
    columns *2 * frames of the ring buffer.
    
    input parameters:
    handle
        Pointer to HACQDESC
    processed_data
        Pointer to the destination buffer
        Buffer for image, 1-d array of unsigned short
    nFrames
        Number of frames of the destination buffer. It must be greater than zero
    nRows, nColumns
        Number of rows and columns of the destination buffer. If these numbers are not suitable
        to the sensor the function return with an error code. If zou need extended information
        call Acquisition_GetErrorCode.
    
    Returns:
    processed_data
        Pointer to the destination buffer
    Return value
        If the function is successful it returns zero, otherwise an error code. To get extended
        information call Acquisition_GetErrorCode.
        
    
    Definition: buf = (c_ushort*4194304)()   #in case of 2048 x 2048 sensor
    """
    ret = xis.Acquisition_DefineDestBuffers(handle, byref(dest_buffer), frames, rows, columns)
    return ret


def acquire_offset_image(handle, rows, cols, frames):
    """
    
    This function acquires nFrames,adds them in a 32 bit buffer acquisition the data values
    are divided by nFrames (averaging). The last acquired data at frame end time are available via
    pOffsetData. At the end of the acquisition time the averaged data are also accessible via pOffsetData.
    The routine returns immediately. If you to be informed about frame end or acquisition end
    then define in Acquisition_Init the suitable Callback functions and post from there a
    corresponding message to your application.
    
    input parameters:
    handle
        Pointer to acquisition descriptor structure
    pOffsetData
        Pointer to a acquisition buffer for offset data
    nFrames
        Number of frames to acquire
    nRows, nCols
        Number of rows and columns of the offset data buffer. If the values are not suitable to the
        current connected sensor the function return with an error
    
    Returns:
    pOffsetData
        Pointer to an acquisition buffer for offset data
    Return value
        If the function is successful it returns zero, otherwise an error code. To get extended
        information call Acquisition_GetErrorCode.
    
    """
    offset_data = (c_ulong * (rows * cols))()  # create a buffer for offset data
    ret = xis.Acquisition_Acquire_OffsetImage(handle, byref(offset_data), rows, cols, frames)
    return ret, offset_data


def acquire_gain_image(handle, offset_data, rows, cols, frames):
    """
    This function acquires nFrames which are all offset corrected by data stored in pOffsetData. After that the gain data are added
    in a 32 bit buffer and after acquisition the data values are divided by nFrames (averaging). After averaging the data are further
    processed for subsequent gain correction of image data. See mathematical description of corrections in XIS reference manual
    for a description of the gain data format. At the end of the acquisition time the gain data are also accessible via pdwGainData.
    The offset data is necessary to derive a valid gain image.

    input parameters:
    handle
        Pointer to acquisition descriptor structure
    offset_data
        Pointer to an acquisition buffer for offset data
    nFrames
        Number of frames to acquire
    nRows, nCols
        Number of rows and columns of the offset data buffer. If the values are not suitable to the
        current connected sensor the function return with an error
    """
    gain_data = (c_ulong * (rows * cols))()
    ret = xis.Acquisition_Acquire_GainImage(handle, byref(offset_data), byref(gain_data), rows, cols, frames)
    return ret, gain_data


def create_pixel_map(data, data_rows, data_columns):
    """
    TODO help
    """
    corr_list_size = c_int()
    corr_list = 0
    ret = xis.Acquisition_CreatePixelMap(byref(data), data_rows, data_columns, corr_list, byref(corr_list_size))  # first call for identification of necessary buffer length
    if ret != ErrorCode.OK:
        return ret, None, None
    corr_list = (c_int * (data_columns * data_rows))()  # construction of the buffer

    ret = xis.Acquisition_CreatePixelMap(byref(data), data_rows, data_columns, byref(corr_list),
                                   byref(corr_list_size))  # second call returning buffer

    return ret, corr_list, corr_list_size.value


def acquire_image(handle, frames, skip_frames=0, seq_options=Sequence.DEST_ONE_FRAME, offset_data=0, gain_data=0, pixel_data=0):
    """
    
    This function acquires dwFrames frames and performs offset, gain and pixel corrections
    automatically. The routine returns immediately. If you want to be informed about frame end or
    acquisition end, then define in Acquisition_Init the suitable Callback functions and post from there
    a corresponding message to your application.
    
    input parameters:
    handle
        Pointer to acquisition descriptor structure
    dwFrames
        Number of frames to acquire is one of the sequence options is set for dwOpt. If the
        continuous option is set this value gives the number of frames in a ring buffer that is used
        for continuous data acquisition.
    dwSkipFrames
        Number of frames to skip before a frames is copied into the acquisition buffer
    dwOpt
        Options for sequence acquisition: Valid values are
        HIS_SEQ_TWO_BUFFERS         0x1     Storage of the sequence into two buffers.
                                            Secure image acquisition by separated data transfer and later
                                            performed image correction.
        HIS_SEQ_ONE_BUFFER          0x2     Storage of the sequence into one buffer.
                                            Direct acquisition and linked correction into one buffer.
        HIS_SEQ_AVERAGE             0x4     All acquired single images are directly added into one buffer and after
                                            acquisition divided by the number of frames, including linked 
                                            correction files.
        HIS_SEQ_DEST_ONE_FRAMES     0x8     Sequence of frames using the same image buffer
        HIS_SEQ_COLLATE             0x10    Skip frames after acquiring frames in a ring buffer
        HIS_SEQ_CONTINUOUS          0x100   Continuous acquisition
                                            Frames are continuously acquired into a ring buffer of dwFrames
    pwOffsetData
        Pointer that contains offset data. (see Acquisition_Acquire_OffsetImage). The Offset
        must be actual. It is recommended to acquire them shortly before calling
        Acquisition_Acquire. If you don't want to perform an offset correction se this
        parameter to NULL.
    pdwGainData
        Pointer that contains gain data. (see Acquisition_Acquire_GainImage). If you don't want
        to perform a gain correction set this parameter to NULL.
    pdwPixelData
        Pointer to a buffer that contains pixel correction data.pdwPixelData points to a linear
        array of data. Its size is given through ((number of wrong pixels)*10+1)*sizeof(int).
        The first entry in a group of nine contains the offset of the pixel from the base pointer of
        the data array. The other eight entries equal the offset of the correction pixels from the
        base pointer. If you want to use less than eight pixels for correction, then set the
        remaining entries to -1. The value of the pixel is replaced by the mean value of the
        correction pixels. If you don't want to perform a pixel correction set this parameter to
        NULL. An easier way to create a pixel map is the use fo the XISL function
        Acquisition_CreatePixelMap.
    
    Return Value
        If the function is successful it returns zero, otherwise an error code. To get extended
        information call Acquisition_GetErrorCode.
    """
    return xis.Acquisition_Acquire_Image(handle, frames, skip_frames, seq_options, offset_data, gain_data, pixel_data)

def acquire_image_preloaded_corrections(handle, frames, skip_images, seq_options=Sequence.DEST_ONE_FRAME):
    """
     The function provides the same functionality as Acquisition_Acquire_Image except it does not load new correction data. Use
        Acquisition_SetCorrData_Ex before to set the correction data.
    """
    return xis.Acquisition_Acquire_Image_PreloadCorr(handle, frames, skip_images, seq_options)


def set_camera_mode(handle, mode):
    """
     This function sets the acquisition readout timing mode of the detector. Currently eight fixed frame times of the detector are provided.
     mode: Must be a number between 0 and 7. The corresponding frame time depends on the used detector setting.
    """
    return xis.Acquisition_SetCameraMode(handle, mode)


def set_camera_gain(handle, gain=Gain_NOP_Series.g_0p25):
    """
    
    This function can be used to set the gain factor of the detector.
    handle
        Pointer to acquisition descriptor structure
    wMode
        Gain factor to set.
        For the AM-Type the values of all capacities are added. All bitwise combinations ar
        valid. For example: 3 => 1.3pF.
        For the xN/xO/xP-Type the Value in the table is set when the detector provides the
        functionality (refer to detector specification).
        
                Detector 16x0 AM
        0       0.1pF (always on)
        1       0.3pF
        2       0.9pF
        4       4.7pF
        8       10pF
                Detector xN/xO/xP
        0       0.25pF
        1       0.5pF
        2       1pF
        3       2pF
        4       4pF
        5       8pF
        
    Return values
        If the function successful it returns zero, otherwise an error code. To get extended
        information call Acquisition_GetErrorCode
        """
    return xis.Acquisition_SetCameraGain(handle, gain)


def set_camera_binning_mode(handle, binning_mode=1):
    """
    Use this function to set the tomography binning mode and binning options.
    binning_mode:
        Used for selection of binning mode and additional options
            • bits 0 to 7: binning mode selection value
            • value 1: no binning (default)
            • value 2 to 5: detector dependent binning mode
            • bits 8 to 15: bit mask with additional binning options.
        The options are mutually exclusive.
        If no option is set, the default option will be used automatically.
            • bit 8: use averaged binning (default option)
            • bit 9: use accumulated binning
    """
    return xis.Acquisition_SetCameraBinningMode(handle, binning_mode)


def get_camera_binning_mode(handle):
    """
    Use this function to retrieve the detector's binning mode. See the description of Acquisition_SetCameraBinningMode for possible returned binning modes.
    """

    mode = WORD()
    ret = xis.Acquisition_GetCameraBinningMode(handle, byref(mode))
    return ret, mode.value


def set_camera_trigger_mode(handle, trigger_mode=TriggerMode.TriggerFrames):
    """
    The function sets the internal trigger scheme for Detectors.
    """
    return xis.Acquisition_SetCameraTriggerMode(handle, trigger_mode)


def get_camera_trigger_mode(handle):
    """
    Retrieves trigger mode for tomography with Header >14 and DetectorType >2.
    """

    mode = WORD()
    ret = xis.Acquisition_GetCameraTriggerMode(handle, byref(mode))
    return ret, mode.value


def set_callbacks_and_messages(handle, end_frame_callback, end_acq_callback):
    """
    
    The Acquisition_SetCallbacksAndMessages function defines callback functions to react on
    acquisition status changes. For a programming example see the initialization part of the XISL
    demonstration.
    
    input parameters:
    handle
        Handle of a structure that contains all needed parameters for acquisition (HACQDESC).
        If you call Acquisition_Init the first time set handle to NULL, in subsequent calls use
        the former returned value.
    hWnd
        If the XISL recognizes an end of DMA transfer and it is ready with sorting, it checks if
        the application called Acquisition_SetReady after redrawing. If the application did not
        call the function, an user defined message (dwLoosingFramesMsg) is posted to hWnd for
        further handling. If an error occurred during acquisition also a user defined message
        (dwErrorMsg) is posted to hWnd.
    dwErrorMsg
        Defines a user messgae that is posted to hWnd if an error occurs during acquisition.
    dwLoosingFramesMsg
        Defines a user message that is posted to hWnd if Acquisition_SetReady wasn't called by
        the application at the end of sorting.
    lpfnEndFrameCallback
        Defines a function pointer that is called after the XISL did the sorting. The prototype for
        the function is given by:
    void CALLBACK OnEndFrameCallback(HACQDESC handle);
        In this routine you can do corrections, on-line image processing and redrawing of your
        data images. Be careful with sending messages from this callback to your application.
        lpfnEndFrameCallback and lpfnEndCallback are called from a separate thread which
        is dissimilar to the applications main thread. That should cause problems if you send
        messages to your main thread via SendMessage. If this causes problems use PostMessage
        instead. If this parameter is set to NULL it is ignored.
    lpfnEndAcqCallback
        Defines a function pointer that is called after the XISL did the sorting. The prototype for
        the function is given by:
    void CALLBACK OnEndAcqCallback(HACQDESC handle);
        In this routine you can perform any clean up at acquisition end. If this parameter is set to
        NULL, it is ignored.
    """
    window_handle = None  # For XISL app only
    errors_message = UINT(0)  # For XISL app only
    loosing_frames_message = UINT(0)  # For XISL app only
    return xis.Acquisition_SetCallbacksAndMessages(handle, window_handle, errors_message, loosing_frames_message,
                                                   end_frame_callback, end_acq_callback)


def get_ready(handle):
    """
    
    This function checks whether the passed Acquisition Descriptor is valid.
    
    handle
        Pointer to acquisition descriptor structure.
    Return values
        If the Acquisition Descriptor is valid, the function returns zero; otherwise it returns an
        error code. To get extended information call Acquisition_GetErrorCode.
    """
    return xis.Acquisition_GetReady(handle)


def set_ready(handle, flag):
    """
    
    This function must be called when the application finished redrawing of the new acquired data. A
    good place to call this function is the end of frame callback function defined in Acquisition_Init or
    the message handler to for the redraw message after redrawing.
    
    input parameters:
    handle
        Pointer to acquisition descriptor structure.
    bFlag
        Boolean value. Set to zero to signal XISL set redrawing isn't ready, otherwise set to one.
    Return values
        If the function is successful it returns zero, otherwise an error code. To get extended
        information call Acquisition_GetErrorCode
    """
    flag = BOOL(flag)
    return xis.Acquisition_SetReady(handle, flag)


def is_acquiring_data(handle):
    """
    
    This function tests if XISL is about to acquire data.
    
    handle
        Pointer to acquisition descriptor structure.
    Return values
        If an acquisition is running a one is returned, otherwise zero.
    """
    return xis.Acquisition_IsAcquiringData(handle)


def get_acq_data(handle):
    """
    
    This routine returns a 32 bit integer that can be set by Acquisition_SetAcqDta. These two
    functions are useful to avoid global variables to put through parameters to the end of frame and
    end of acquisition callback functions set by Acquisition_Init.
    The function Acquisition_SetAcqData and Acquisition_GetAcqData differ in the 32 and 64
    bit library:
    
    input parameters:
    handle
        Pointer to acquisition descriptor structure.
    
    Returns:
    VoidAcqData
        Pointer to a Pointer to a user defined structure/value/class here which can be retrieved
        in the EndFrameCallback/EndAcqCallback.
    Return values
        If the function is successful it returns zero, otherwise an error code. To get extended
        information call Acquisition_GetErrorCode
    """
    temp = c_void_p()
    ret = xis.Acquisition_GetAcqData(handle, byref(temp))
    return ret, temp.value


def get_act_frame(handle):
    """
    
    This function retrieves the current acquisition frames.
    
    input parameters:
    handle
        Pointer to acquisition descriptor structure.
    
    Returns:
    current_frame_index
        Index of the latest acquired frame within the internal acquisition buffer. The buffer itself
        is part of the frame grabber driver. Its data are not accessible externally. However, the
        index can be used to verify the consistency of image sequences; it runs repeatedly from
        1 to 8.
    current_frame_buffer
        Index of the latest acquired frame within the user buffer. For that, size of location of the
        userř buffer has to be defined by Acquisition_DefineDestBuffers.
    Return values
        If the function is successful it returns zero otherwise an error code. To get extended
        information call Acquisition_GetErrorCode.
    """
    current_frame_index = DWORD()
    current_frame_buffer = DWORD()
    ret = xis.Acquisition_GetActFrame(handle, byref(current_frame_index), byref(current_frame_buffer))
    return ret, current_frame_index.value, current_frame_buffer.value


def close(handle):
    return xis.Acquisition_Close(handle)


def close_all():
    return xis.Acquisition_CloseAll()


def abort(handle):
    return xis.Acquisition_Abort(handle)


def set_timer_sync(handle, cycle_time):
    temp = c_ulong(cycle_time)
    return xis.Acquisition_SetTimerSync(handle, byref(temp))


def set_frame_sync_mode(handle, sync_mode):
    """
    
    Sets the acquisition mode to 
    
    HIS_SYNCMODE_SOFT_TRIGGER		= 1
    HIS_SYNCMODE_INTERNAL_TIMER		= 2
    HIS_SYNCMODE_EXTERNAL_TRIGGER	= 3
    HIS_SYNCMODE_FREE_RUNNING		= 4
    
    """
    return xis.Acquisition_SetFrameSyncMode(handle, sync_mode)


def enum_sensors(enable_irq=True, always_open=False):
    """
    This function enumerates all currently connected sensors. All recognized sensors are
    initialized automatically. To get the HACQDESC of every sensor, use Acquisition_-
    GetNextSensor. For a programming example see the initialization part of the XISL
    demonstration. Note: In case of Network/IP Sensors only sensors with standard gateway
    equal to zero are initialized automatically.
    """
    temp = c_ulong()
    ret = xis.Acquisition_EnumSensors(byref(temp), enable_irq, always_open)
    return ret, temp.value


def get_next_sensor(pos=None):  # TODO: this function is not running, maybe only one sensor?
    """
    You can use this function to iterate through all recognized sensors in the system. for a
    programming example see the initialization part of the XISL demonstration.
    """
    if pos is None:
        pos = c_ulong(0)
    handle = HACQDESC()
    ret = xis.Acquisition_GetNextSensor(byref(pos), byref(handle))
    return ret, pos, handle


def get_comm_channel(handle):
    channel_type = c_uint()
    channel_number = c_int()
    ret = xis.Acquisition_GetCommChannel(handle, byref(channel_type), byref(channel_number))
    return ret, channel_type.value, channel_number.value


def init(handle, board_type=BoardType.ELTEC_XRD_FGE_Opto, channel_nr=0, enable_irq=1, rows=4096, columns=4096,
         sort_flag=Sort.NOSORT, self_init=1,
         always_open=0):
    """
    The Acquisition_Init function initializes the frame grabber board and the corresponding
    driver. It enables desired hardware interrupts, prepares acquisition threads, defines
    callback functions to react on acquisition status changes and tests for sufficient memory
    space for DMA (direct memory access).
    
    Init(handle, dwBoardType=16, nChannelNr=0, bEnableIRQ=1, uiRows=4096, uiColumns=4096, uiSortFlag=0, bSelfInit=1, bAlwaysOpen=0)

    Parameters
    handle Handle of a structure that contains all needed parameters for acquisition
    (HACQDESC). If you call Acquisition_Init the first time set handle to
    NULL, in subsequent calls use the former returned value.
    dwBoard-
    Type
    This parameter defines on which communication device the sensor is
    located. Only one type of frame grabber can be used at the same time.
    nChannelNr This parameter defines the device number. Its possible values depend
    from dwBoardType and the number of the installed components. For
    instance if you installed 2 frame grabber boards and you want to acquire
    data from that one, on that the hardware board selector is set to three,
    set dwChannelNr equal to 3.
    bEnableIRQ If you want to run the acquisition in polling mode set this parameter to
    zero. If you want to enable hardware interrupts set the parameter to
    one.
    Rows Number of sensor columns and rows
    Columns Number of sensor columns and rows
    dwSortFlag Depending on the sensor different sorting schemes are needed because
    the data come in incorrect order from the detector. dwSortFlags
    can be one of the following values: The sorting is done automatically
    by XISL during acquisition. The sorting routines are written in machine
    code and are therefore very fast.
    bSelfInit If bSelfInit is set to true the function retrieves the detector parameters
    (Rows, Columns,SortFlags) automatically. If bSelfInit is set to false the
    configuration parameters supplied by Rows, Columns, dwSortFlags are
    used.
    bAlways-
    Open
    If this parameter is TRUE the XISL is capturing the requested communication
    port regardless if this port is already opened by other processes
    running on the system. The use of this option is only recommended in
    debug versions of your applications because it is not possible to free all
    system resources allocated by another process.
    """
    ret = xis.Acquisition_Init(byref(handle), board_type, channel_nr, enable_irq, rows, columns, sort_flag,
                               self_init, always_open)
    return ret, handle


def get_error_code(handle):
    """
    This function retrieves the last error code of the XISL.
    """
    his_error = DWORD()
    board_error = DWORD()
    ret = xis.Acquisition_GetErrorCode(handle, his_error, board_error)
    return ret, his_error.value, board_error.value


def end_frame_callback():
    pass


def end_acq_callback():
    pass
