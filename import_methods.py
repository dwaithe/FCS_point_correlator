import struct
import numpy as np
import csv


"""FCS Bulk Correlation Software

    Copyright (C) 2015, 2016  Dominic Waithe

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""
import struct
import string

def ptuimport(filepath):

    
    tyEmpty8      = int('FFFF0008', 16);
    tyBool8       = int('00000008', 16);
    tyInt8        = int('10000008', 16);
    tyBitSet64    = int('11000008', 16);
    tyColor8      = int('12000008', 16);
    tyFloat8      = int('20000008', 16);
    tyTDateTime   = int('21000008', 16);
    tyFloat8Array = int('2001FFFF', 16);
    tyAnsiString  = int('4001FFFF', 16);
    tyWideString  = int('4002FFFF', 16);
    tyBinaryBlob  = int('FFFFFFFF', 16);

    rtPicoHarpT3     = int('00010303', 16);# (SubID = $00 ,RecFmt: $01) (V1), T-Mode: $03 (T3), HW: $03 (PicoHarp)
    rtPicoHarpT2     = int('00010203', 16);# (SubID = $00 ,RecFmt: $01) (V1), T-Mode: $02 (T2), HW: $03 (PicoHarp)
    rtHydraHarpT3    = int('00010304', 16);# (SubID = $00 ,RecFmt: $01) (V1), T-Mode: $03 (T3), HW: $04 (HydraHarp)
    rtHydraHarpT2    = int('00010204', 16);# (SubID = $00 ,RecFmt: $01) (V1), T-Mode: $02 (T2), HW: $04 (HydraHarp)
    rtHydraHarp2T3   = int('01010304', 16);# (SubID = $01 ,RecFmt: $01) (V2), T-Mode: $03 (T3), HW: $04 (HydraHarp)
    rtHydraHarp2T2   = int('01010204', 16);# (SubID = $01 ,RecFmt: $01) (V2), T-Mode: $02 (T2), HW: $04 (HydraHarp)
    rtTimeHarp260NT3 = int('00010305', 16);# (SubID = $00 ,RecFmt: $01) (V1), T-Mode: $03 (T3), HW: $05 (TimeHarp260N)
    rtTimeHarp260NT2 = int('00010205', 16);# (SubID = $00 ,RecFmt: $01) (V1), T-Mode: $02 (T2), HW: $05 (TimeHarp260N)
    rtTimeHarp260PT3 = int('00010306', 16);# (SubID = $00 ,RecFmt: $01) (V1), T-Mode: $03 (T3), HW: $06 (TimeHarp260P)
    rtTimeHarp260PT2 = int('00010206', 16);# (SubID = $00 ,RecFmt: $01) (V1), T-Mode: $02 (T2), HW: $06 (TimeHarp260P)

    fid = 0
    #TTResultFormat_TTTRRecType =0 ;
    #TTResult_NumberOfRecords = 0; #% Number of TTTR Records in the File;
    #MeasDesc_Resolution =0;      #% Resolution for the Dtime (T3 Only)
    #MeasDesc_GlobalResolution =0;

    f = open(filepath, 'r')
    magic = str(f.read(8))
    if magic[0:6] != "PQTTTR":
        print 'Your file is an invalid .ptu'
        return
    version =  f.read(8)
    #print 'version',version

    file_type = {}
    while True:
            #read Tag Head
            TagIdent = f.read(32); # TagHead.Ident
            TagIdent = string.replace(TagIdent,'\x00','')
            #print 'Tag',TagIdent
            #TagIdent = TagIdent[TagIdent != 0]]#'; # remove #0 and more more readable

            TagIdx =  struct.unpack('i', f.read(4))[0] #TagHead.Idx
            TagTyp =  np.array(struct.unpack('i', f.read(4))[0]).astype(np.uint32) #TagHead.Typ
            #TagHead.Value will be read in the right type function
            #print 'TagIdx',TagIdx
            if TagIdx > -1:
                EvalName = TagIdent+'('+str(TagIdx+1)+')'
            else:
                EvalName = TagIdent

            

            #print('eval',str(EvalName))
            
            
            
            if TagTyp == tyEmpty8:
                struct.unpack('Q', f.read(8))[0]
                #print('empty')
            elif TagTyp ==tyBool8:
                TagInt = struct.unpack('Q', f.read(8))[0]
                if TagInt == 0:
                    #print('False')
                    file_type[EvalName] = False
                else:
                    #print('True')
                    file_type[EvalName] = True
            elif TagTyp == tyInt8:
                TagInt =  struct.unpack('Q', f.read(8))[0]
                file_type[EvalName] = TagInt
                #print('tyInt8',TagInt)
            elif TagTyp == tyBitSet64:
                TagInt = struct.unpack('Q', f.read(8))[0]
                file_type[EvalName] = TagInt
                #print('tyBitSet64',TagInt)
            elif TagTyp == tyColor8:
                TagInt = struct.unpack('Q', f.read(8))[0]
                file_type[EvalName] = TagInt
                #print('tyColor8',TagInt)
            elif TagTyp == tyFloat8:
                TagInt = struct.unpack('d', f.read(8))[0]
                file_type[EvalName] = TagInt
                #print('tyFloat8',TagInt)
            elif TagTyp == tyFloat8Array:
                TagInt = struct.unpack('Q', f.read(8))[0]
                file_type[EvalName] = TagInt
                #print '<Float array with'+str(TagInt / 8)+'Entries>'
                #print('tyFloat8Array',TagInt)
                f.seek(TagInt)
            elif TagTyp == tyTDateTime:
                TagFloat = struct.unpack('d', f.read(8))[0]
                #print('date'+str(TagFloat))
                file_type[EvalName] = TagFloat
            elif TagTyp == tyAnsiString:
                TagInt = int(struct.unpack('Q', f.read(8))[0])
                TagString = f.read(TagInt)
                TagString = string.replace(TagString,'\x00','')

                #print('tyAnsiString',TagString)
                if TagIdx > -1:
                    EvalName = TagIdent +'{'+str(TagIdx+1)+'}'
                file_type[EvalName] = TagString
            elif TagTyp == tyWideString:
                TagInt = struct.unpack('i', f.read(4))[0].astype(np.float64)
                TagString = struct.unpack('i', f.read(4))[0].astype(np.float64)

                #print('tyWideString',TagString)
                if TagIdx > -1:
                    EvalName = TagIdent +'{'+str(TagIdx+1)+'}'
                file_type[EvalName] = TagString
            elif TagTyp == tyBinaryBlob:
                TagInt = struct.unpack('i', f.read(4))[0].astype(np.float64)
                #print('<Binary Blob with '+str(TagInt)+'Bytes>')
                f.seek(TagInt)
            else:
                print('Illegal Type identifier found! Broken file?',TagTyp)
                
            if TagIdent == "Header_End":
                
                break

    print('\n------------------------\n')
    TTResultFormat_TTTRRecType = file_type['TTResultFormat_TTTRRecType']
    if TTResultFormat_TTTRRecType == rtPicoHarpT3:
        isT2 = False
        print 'PicoHarp T3 data\n'

    elif TTResultFormat_TTTRRecType == rtPicoHarpT2:
        isT2 =True
        print 'PicoHarp T2 data \n'

    elif TTResultFormat_TTTRRecType == rtHydraHarpT3:
        isT2 = False
        print 'HydraHarp V1 T3 data \n'

    elif TTResultFormat_TTTRRecType == rtHydraHarpT2:
        isT2 = True
        print 'HydraHarp V1 T2 data \n'

    elif TTResultFormat_TTTRRecType == rtHydraHarp2T3:
        isT2 = False
        print 'HydraHarp V2 T3 data \n'

    elif TTResultFormat_TTTRRecType == rtHydraHarp2T2:
        isT2 = True
        print 'HydraHarp V2 T2 data \n'

    elif TTResultFormat_TTTRRecType == rtTimeHarp260NT3:
        isT2 = False
        print 'TimeHarp260N T3 data \n'

    elif TTResultFormat_TTTRRecType == rtTimeHarp260NT2:
        isT2 = True
        print 'TimeHarp260P T3 data \n'

    elif TTResultFormat_TTTRRecType == rtTimeHarp260PT3:
        isT2 = False
        print 'TimeHarp260P T3 data \n'

    elif TTResultFormat_TTTRRecType == rtTimeHarp260PT2:
        isT2 = True
        print 'TimeHarp260P T2 data \n'

    else:
        print('Illegal RecordType')

    #if (isT2):
    #      print '\trecord#\tType\tCh\tTimeTag\tTrueTime/ps\n'
    #else:
    #      print '\trecord#\tType\tCh\tTimeTag\tTrueTime/ns\tDTime\n'

    print file_type
    print 'Eval',EvalName
    
            
    if TTResultFormat_TTTRRecType   == rtPicoHarpT3: 
        return ReadPT3(f,file_type['TTResult_NumberOfRecords'],file_type['MeasDesc_GlobalResolution'])

    elif TTResultFormat_TTTRRecType == rtPicoHarpT2: #ReadPT2
        print 'currently this type of file is not supported using this python implementation'
        return False
    elif TTResultFormat_TTTRRecType == rtHydraHarpT3: #ReadHT3(1)
        return ReadHT3(1,f,file_type['TTResult_NumberOfRecords'],file_type['MeasDesc_GlobalResolution']);
    elif TTResultFormat_TTTRRecType == rtHydraHarpT2: #ReadHT3(1)
        print 'currently this type of file is not supported using this python implementation'
        return False
    elif TTResultFormat_TTTRRecType == rtHydraHarp2T3: 
        return ReadHT3(2,f,file_type['TTResult_NumberOfRecords'],file_type['MeasDesc_GlobalResolution']);
    elif TTResultFormat_TTTRRecType == rtHydraHarp2T2: #ReadHT2(2);
        print 'currently this type of file is not supported using this python implementation'
        return False
    elif TTResultFormat_TTTRRecType == rtTimeHarp260NT3: #ReadHT3(2);
        return ReadHT3(2,f,file_type['TTResult_NumberOfRecords'],file_type['MeasDesc_GlobalResolution']);
    elif TTResultFormat_TTTRRecType == rtTimeHarp260NT2: #ReadHT2(2);
        print 'currently this type of file is not supported using this python implementation'
        return False
    elif TTResultFormat_TTTRRecType == rtTimeHarp260PT3: #ReadHT3(2);
        return ReadHT3(2,f,file_type['TTResult_NumberOfRecords'],file_type['MeasDesc_GlobalResolution']);
    elif TTResultFormat_TTTRRecType == rtTimeHarp260PT2: #ReadHT2(2);
        print 'currently this type of file is not supported using this python implementation'
        return False
    else: 
        print('Illegal RecordType')
        return False
        
    ###Decoder functions
# Read HydraHarp/TimeHarp260 T3
def ReadHT3(version,f,TTResult_NumberOfRecords,MeasDesc_GlobalResolution):
    T3WRAPAROUND = 1024
    ofltime = 0
    cnt_Ofl = 0
    cnt_ma = 0
    cnt_ph = 0
    OverflowCorrection = 0
    chanArr = [0]*TTResult_NumberOfRecords
    trueTimeArr =[0]*TTResult_NumberOfRecords
    dTimeArr= [0]*TTResult_NumberOfRecords
    for b in range(0,TTResult_NumberOfRecords):
        RecNum = b
       
        T3Record = struct.unpack('I', f.read(4))[0];
        nsync = T3Record & 1023
        truetime = 0

        #dtime = bitand(bitshift(T3Record,-10),32767);
        dtime = ((T3Record >> 10) & 32767);
        channel = ((T3Record >> 25) & 63);
        special = ((T3Record >> 31) & 1);

        print RecNum,'dtime',dtime,'channel',channel,'special'

        if special == 0:
            true_nSync = OverflowCorrection + nsync
            truetime = (true_nSync * MeasDesc_GlobalResolution * 1e9)
            
            
        else:
            if channel  == 63:
                if nsync == 0 or version == 1:
                    OverflowCorrection = OverflowCorrection + T3WRAPAROUND
                    cnt_Ofl = cnt_Ofl+1
                else:
                    OverflowCorrection = OverflowCorrection + T3WRAPAROUND*nsync
                    cnt_Ofl = cnt_Ofl+nsync
            
            if channel >-1 and channel < 16:
                true_nSync = OverflowCorrection + nsync
                cnt_ma = cnt_ma +1
        trueTimeArr[cnt_ph] = truetime
        dTimeArr[cnt_ph] = dtime
        chanArr[cnt_ph] = channel+1
        cnt_ph = cnt_ph +1

        #PT3
        #dtime = ((T3Record >> 16) & 4095);
        #dtime = bitand(bitshift(T3Record,-16),4095)
    return np.array(chanArr[0:cnt_ph]), np.array(trueTimeArr[0:cnt_ph]), np.array(dTimeArr[0:cnt_ph]), MeasDesc_GlobalResolution* 1e6   



"""
def ReadHT3(Version)
        global fid;
        global RecNum;
        global TTResult_NumberOfRecords; % Number of TTTR Records in the File
        OverflowCorrection = 0;
        T3WRAPAROUND = 1024;

        for i = 1:TTResult_NumberOfRecords
            RecNum = i;
            T3Record = fread(fid, 1, 'ubit32');     % all 32 bits:
            %   +-------------------------------+  +-------------------------------+
            %   |x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|  |x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|x|
            %   +-------------------------------+  +-------------------------------+
            nsync = bitand(T3Record,1023);       % the lowest 10 bits:
            %   +-------------------------------+  +-------------------------------+
            %   | | | | | | | | | | | | | | | | |  | | | | | | |x|x|x|x|x|x|x|x|x|x|
            %   +-------------------------------+  +-------------------------------+
            dtime = bitand(bitshift(T3Record,-10),32767);   % the next 15 bits:
            %   the dtime unit depends on "Resolution" that can be obtained from header
            %   +-------------------------------+  +-------------------------------+
            %   | | | | | | | |x|x|x|x|x|x|x|x|x|  |x|x|x|x|x|x| | | | | | | | | | |
            %   +-------------------------------+  +-------------------------------+
            channel = bitand(bitshift(T3Record,-25),63);   % the next 6 bits:
            %   +-------------------------------+  +-------------------------------+
            %   | |x|x|x|x|x|x| | | | | | | | | |  | | | | | | | | | | | | | | | | |
            %   +-------------------------------+  +-------------------------------+
            special = bitand(bitshift(T3Record,-31),1);   % the last bit:
            %   +-------------------------------+  +-------------------------------+
            %   |x| | | | | | | | | | | | | | | |  | | | | | | | | | | | | | | | | |
            %   +-------------------------------+  +-------------------------------+
            if special == 0   % this means a regular input channel
               true_nSync = OverflowCorrection + nsync;
               %  one nsync time unit equals to "syncperiod" which can be
               %  calculated from "SyncRate"
               GotPhoton(true_nSync, channel, dtime);
            else    % this means we have a special record
                if channel == 63  % overflow of nsync occured
                  if (nsync == 0) || (Version == 1) % if nsync is zero it is an old style single oferflow or old Version
                    OverflowCorrection = OverflowCorrection + T3WRAPAROUND;
                    GotOverflow(1);
                  else         % otherwise nsync indicates the number of overflows - THIS IS NEW IN FORMAT V2.0
                    OverflowCorrection = OverflowCorrection + T3WRAPAROUND * nsync;
                    GotOverflow(nsync);
                  end;
                end;
                if (channel >= 1) && (channel <= 15)  % these are markers
                  true_nSync = OverflowCorrection + nsync;
                  GotMarker(true_nSync, channel);
                end;
            end;
        end;
    end
    ##READ picoHarp T3"""
def ReadPT3(f,TTResult_NumberOfRecords,MeasDesc_GlobalResolution):

    cnt_Ofl = 0
    WRAPAROUND = 65536
    ofltime = 0
    chanArr = [0]*TTResult_NumberOfRecords
    trueTimeArr =[0]*TTResult_NumberOfRecords
    dTimeArr= [0]*TTResult_NumberOfRecords
    truetime = 0

    for b in range(0,TTResult_NumberOfRecords):
        recNum = b
        T3Record = struct.unpack('I', f.read(4))[0];
        nsync = T3Record & 65535
        chan = ((T3Record >> 28) & 15);
        chanArr[b]=chan

        dtime = 0
        truensync = ofltime + nsync;
        if chan >0 and chan <5:
            dtime = dtime = ((T3Record >> 16) & 4095);
            truetime = (truensync * MeasDesc_GlobalResolution * 1e9)
        elif chan == 15:
            markers = ((T3Record >> 16) & 15);
            truetime = 0
            if markers ==0:
                ofltime = ofltime +WRAPAROUND;
                cnt_Ofl = cnt_Ofl+1
                
            else:
                cnt_M=cnt_M+1
                #f1.write("MA:%1u "+markers+" ")
        print recNum,'dtime',dtime,'channel',chan,'special',truetime,'f.tell',f.tell()
        trueTimeArr[b] = truetime
        dTimeArr[b] = dtime
        chanArr[b] = chan

    return np.array(chanArr), np.array(trueTimeArr), np.array(dTimeArr), MeasDesc_GlobalResolution* 1e6
def csvimport(filepath):
    """Function for importing time-tag data directly into FCS point software. """
    r_obj = csv.reader(open(filepath, 'rb'))
    line_one = r_obj.next()
    if line_one.__len__()>1:
        if float(line_one[1]) == 2:
            
            version = 2
        else:
            print 'version not known:',line_one[1]
    
    if version == 2:
        type =str(r_obj.next()[1])
        if type == "pt uncorrelated":
            Resolution = float(r_obj.next()[1])
            chanArr = []
            trueTimeArr = []
            dTimeArr = []
            line = r_obj.next()
            while  line[0] != 'end':

                chanArr.append(int(line[0]))
                trueTimeArr.append(float(line[1]))
                dTimeArr.append(int(line[2]))
                line = r_obj.next()
            return np.array(chanArr), np.array(trueTimeArr), np.array(dTimeArr), Resolution
        else:
            print 'type not recognised'
            return None, None,None,None

    

def pt3import(filepath):
    """The file import for the .pt3 file"""
    f = open(filepath, 'rb')
    Ident = f.read(16)
    FormatVersion = f.read(6)
    CreatorName = f.read(18)
    CreatorVersion = f.read(12)
    FileTime = f.read(18)
    CRLF = f.read(2)
    CommentField = f.read(256)
    Curves = struct.unpack('i', f.read(4))[0]
    BitsPerRecord = struct.unpack('i', f.read(4))[0]
    RoutingChannels = struct.unpack('i', f.read(4))[0]
    NumberOfBoards = struct.unpack('i', f.read(4))[0]
    ActiveCurve = struct.unpack('i', f.read(4))[0]
    MeasurementMode = struct.unpack('i', f.read(4))[0]
    SubMode = struct.unpack('i', f.read(4))[0]
    RangeNo = struct.unpack('i', f.read(4))[0]
    Offset = struct.unpack('i', f.read(4))[0]
    AcquisitionTime = struct.unpack('i', f.read(4))[0]
    StopAt = struct.unpack('i', f.read(4))[0]
    StopOnOvfl = struct.unpack('i', f.read(4))[0]
    Restart = struct.unpack('i', f.read(4))[0]
    DispLinLog = struct.unpack('i', f.read(4))[0]
    DispTimeFrom = struct.unpack('i', f.read(4))[0]
    DispTimeTo = struct.unpack('i', f.read(4))[0]
    DispCountFrom = struct.unpack('i', f.read(4))[0]
    DispCountTo = struct.unpack('i', f.read(4))[0]
    DispCurveMapTo = [];
    DispCurveShow =[];
    for i in range(0,8):
        DispCurveMapTo.append(struct.unpack('i', f.read(4))[0]);
        DispCurveShow.append(struct.unpack('i', f.read(4))[0]);
    ParamStart =[];
    ParamStep =[];
    ParamEnd =[];
    for i in range(0,3):
        ParamStart.append(struct.unpack('i', f.read(4))[0]);
        ParamStep.append(struct.unpack('i', f.read(4))[0]);
        ParamEnd.append(struct.unpack('i', f.read(4))[0]);
        
    RepeatMode = struct.unpack('i', f.read(4))[0]
    RepeatsPerCurve = struct.unpack('i', f.read(4))[0]
    RepeatTime = struct.unpack('i', f.read(4))[0]
    RepeatWait = struct.unpack('i', f.read(4))[0]
    ScriptName = f.read(20)

    #The next is a board specific header

    HardwareIdent = f.read(16)
    HardwareVersion = f.read(8)
    HardwareSerial = struct.unpack('i', f.read(4))[0]
    SyncDivider = struct.unpack('i', f.read(4))[0]

    CFDZeroCross0 = struct.unpack('i', f.read(4))[0]
    CFDLevel0 = struct.unpack('i', f.read(4))[0]
    CFDZeroCross1 = struct.unpack('i', f.read(4))[0]
    CFDLevel1 = struct.unpack('i', f.read(4))[0]

    Resolution = struct.unpack('f', f.read(4))[0]

    #below is new in format version 2.0

    RouterModelCode      = struct.unpack('i', f.read(4))[0]
    RouterEnabled        = struct.unpack('i', f.read(4))[0]

    #Router Ch1
    RtChan1_InputType    = struct.unpack('i', f.read(4))[0]
    RtChan1_InputLevel   = struct.unpack('i', f.read(4))[0]
    RtChan1_InputEdge    = struct.unpack('i', f.read(4))[0]
    RtChan1_CFDPresent   = struct.unpack('i', f.read(4))[0]
    RtChan1_CFDLevel     = struct.unpack('i', f.read(4))[0]
    RtChan1_CFDZeroCross = struct.unpack('i', f.read(4))[0]
    #Router Ch2
    RtChan2_InputType    = struct.unpack('i', f.read(4))[0]
    RtChan2_InputLevel   = struct.unpack('i', f.read(4))[0]
    RtChan2_InputEdge    = struct.unpack('i', f.read(4))[0]
    RtChan2_CFDPresent   = struct.unpack('i', f.read(4))[0]
    RtChan2_CFDLevel     = struct.unpack('i', f.read(4))[0]
    RtChan2_CFDZeroCross = struct.unpack('i', f.read(4))[0]
    #Router Ch3
    RtChan3_InputType    = struct.unpack('i', f.read(4))[0]
    RtChan3_InputLevel   = struct.unpack('i', f.read(4))[0]
    RtChan3_InputEdge    = struct.unpack('i', f.read(4))[0]
    RtChan3_CFDPresent   = struct.unpack('i', f.read(4))[0]
    RtChan3_CFDLevel     = struct.unpack('i', f.read(4))[0]
    RtChan3_CFDZeroCross = struct.unpack('i', f.read(4))[0]
    #Router Ch4
    RtChan4_InputType    = struct.unpack('i', f.read(4))[0]
    RtChan4_InputLevel   = struct.unpack('i', f.read(4))[0]
    RtChan4_InputEdge    = struct.unpack('i', f.read(4))[0]
    RtChan4_CFDPresent   = struct.unpack('i', f.read(4))[0]
    RtChan4_CFDLevel     = struct.unpack('i', f.read(4))[0]
    RtChan4_CFDZeroCross = struct.unpack('i', f.read(4))[0]

    #The next is a T3 mode specific header.
    ExtDevices = struct.unpack('i', f.read(4))[0]

    Reserved1 = struct.unpack('i', f.read(4))[0]
    Reserved2 = struct.unpack('i', f.read(4))[0]
    CntRate0 = struct.unpack('i', f.read(4))[0]
    CntRate1 = struct.unpack('i', f.read(4))[0]

    StopAfter = struct.unpack('i', f.read(4))[0]
    StopReason = struct.unpack('i', f.read(4))[0]
    Records = struct.unpack('i', f.read(4))[0]
    ImgHdrSize =struct.unpack('i', f.read(4))[0]

    #Special Header for imaging.
    if ImgHdrSize > 0:
        ImgHdr = struct.unpack('i', f.read(ImgHdrSize))[0]
    ofltime = 0;

    cnt_1=0; cnt_2=0; cnt_3=0; cnt_4=0; cnt_Ofl=0; cnt_M=0; cnt_Err=0; # just counters
    WRAPAROUND=65536;

    #Put file Save info here.

    syncperiod = 1e9/CntRate0;
    #outfile stuff here.
    #fpout.
    #T3RecordArr = [];
    
    chanArr = [0]*Records
    trueTimeArr =[0]*Records
    dTimeArr=[0]*Records
    #f1=open('./testfile', 'w+')
    for b in range(0,Records):
        T3Record = struct.unpack('I', f.read(4))[0];
        
        #T3RecordArr.append(T3Record)
        nsync = T3Record & 65535
        chan = ((T3Record >> 28) & 15);
        chanArr[b]=chan
        #f1.write(str(i)+" "+str(T3Record)+" "+str(nsync)+" "+str(chan)+" ")
        dtime = 0;
        
        if chan == 1:
            cnt_1 = cnt_1+1;dtime = ((T3Record >> 16) & 4095);#f1.write(str(dtime)+" ")
        elif chan == 2: 
            cnt_2 = cnt_2+1;dtime = ((T3Record >> 16) & 4095);#f1.write(str(dtime)+" ")
        elif chan == 3: 
            cnt_3 = cnt_3+1;dtime = ((T3Record >> 16) & 4095);#f1.write(str(dtime)+" ")
        elif chan == 4: 
            cnt_4 = cnt_4+1;dtime = ((T3Record >> 16) & 4095);#f1.write(str(dtime)+" ")
        elif chan == 15:
            markers = ((T3Record >> 16) & 15);
            
            if markers ==0:
                ofltime = ofltime +WRAPAROUND;
                cnt_Ofl = cnt_Ofl+1
                #f1.write("Ofl "+" ")
            else:
                cnt_M=cnt_M+1
                #f1.write("MA:%1u "+markers+" ")
            
        truensync = ofltime + nsync;
        truetime = (truensync * syncperiod) + (dtime*Resolution);
        trueTimeArr[b] = truetime
        dTimeArr[b] = dtime
        
        #f1.write(str(truensync)+" "+str(truetime)+"\n")
    f.close();
    #f1.close();
    

    
    return np.array(chanArr), np.array(trueTimeArr), np.array(dTimeArr), Resolution