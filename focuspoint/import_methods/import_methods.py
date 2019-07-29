import struct
import numpy as np
import csv
import time

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

def spc_file_import(file_path):
    f = open(file_path, 'rb')
    macro_time =  float(int(bin(ord(f.read(1)))[2:].rjust(2, '0'),2))*0.1
    
    int(bin(ord(f.read(1)))[2:].rjust(2, '0'),2)
    int(bin(ord(f.read(1)))[2:].rjust(2, '0'),2)
    bin(ord(f.read(1)))[2:].rjust(2, '0')



    overflow = 0
    count1 = 0
    count0 = 0
    chan_arr = []
    true_time_arr = []
    dtime_arr = []
    while True:
        byte = f.read(1)
        if  byte.__len__() ==0 : break
        byte0 = bin(ord(byte))[2:].rjust(8, '0')
        byte1 = bin(ord(f.read(1)))[2:].rjust(8, '0')
        byte2 = bin(ord(f.read(1)))[2:].rjust(8, '0')
        byte3 = bin(ord(f.read(1)))[2:].rjust(8, '0')

        INVALID =  int(byte3[0])
        MTOV = int(byte3[1])
        GAP = int(byte3[2])

        if MTOV == 1: 
            count0 +=1
            overflow += 4096
        if INVALID == 1:
            count1 +=1
        else:
            chan_arr.append(int(byte1[0:4],2))
            true_time_arr.append(int(byte1[4:8]+byte0,2)+overflow)
            dtime_arr.append(4095 - int(byte3[4:8]+byte2,2))
        
            
            #file_out.write(str(int(byte1[4:8]+byte0,2)+overflow)+'\t'+str(4095 - int(byte3[4:8]+byte2,2))+'\t'+str(int(byte1[0:4],2))+'\t'+str(byte3[0:4])+'\n')
    
    return  np.array(chan_arr), np.array(true_time_arr)*(macro_time), np.array(dtime_arr), None


def asc_file_import(file_path):
    f = open(file_path, 'rb')
    count = 0

    out = []
    count = 0
    chan_arr = []
    true_time_arr = []
    dtime_arr = []
    read_header = True
    for line in iter(f.readline, b''):
        count += 1
        if read_header == True:
            if line[0:5] == 'Macro':
                macro_time =  float(line.split(':')[1].split(',')[0])
            if line[0:5] == 'Micro':
                micro_time =  float(line.split(':')[1])
            #print line
            count +=1
            if line[0:18] == 'End of info header':
                read_header = False
                f.readline()#Skips blank line.
                continue
        if read_header == False:
            #Main file reading loop.
            var = line.split(" ")
            
            true_time_arr.append(int(var[0]))
            dtime_arr.append(int(var[1]))
            chan_arr.append(int(var[3]))
        
    
    return  np.array(chan_arr), np.array(true_time_arr)*(macro_time), np.array(dtime_arr), micro_time

def ptuimport(filepath):

    
    # Tag Types
    tyEmpty8 = struct.unpack(">i", bytes.fromhex("FFFF0008"))[0]
    tyBool8 = struct.unpack(">i", bytes.fromhex("00000008"))[0]
    tyInt8 = struct.unpack(">i", bytes.fromhex("10000008"))[0]
    tyBitSet64 = struct.unpack(">i", bytes.fromhex("11000008"))[0]
    tyColor8 = struct.unpack(">i", bytes.fromhex("12000008"))[0]
    tyFloat8 = struct.unpack(">i", bytes.fromhex("20000008"))[0]
    tyTDateTime = struct.unpack(">i", bytes.fromhex("21000008"))[0]
    tyFloat8Array = struct.unpack(">i", bytes.fromhex("2001FFFF"))[0]
    tyAnsiString = struct.unpack(">i", bytes.fromhex("4001FFFF"))[0]
    tyWideString = struct.unpack(">i", bytes.fromhex("4002FFFF"))[0]
    tyBinaryBlob = struct.unpack(">i", bytes.fromhex("FFFFFFFF"))[0]
    
    # Record types
    rtPicoHarpT3 = struct.unpack(">i", bytes.fromhex('00010303'))[0]
    rtPicoHarpT2 = struct.unpack(">i", bytes.fromhex('00010203'))[0]
    rtHydraHarpT3 = struct.unpack(">i", bytes.fromhex('00010304'))[0]
    rtHydraHarpT2 = struct.unpack(">i", bytes.fromhex('00010204'))[0]
    rtHydraHarp2T3 = struct.unpack(">i", bytes.fromhex('01010304'))[0]
    rtHydraHarp2T2 = struct.unpack(">i", bytes.fromhex('01010204'))[0]
    rtTimeHarp260NT3 = struct.unpack(">i", bytes.fromhex('00010305'))[0]
    rtTimeHarp260NT2 = struct.unpack(">i", bytes.fromhex('00010205'))[0]
    rtTimeHarp260PT3 = struct.unpack(">i", bytes.fromhex('00010306'))[0]
    rtTimeHarp260PT2 = struct.unpack(">i", bytes.fromhex('00010206'))[0]
    rtMultiHarpNT3 = struct.unpack(">i", bytes.fromhex('00010307'))[0]
    rtMultiHarpNT2 = struct.unpack(">i", bytes.fromhex('00010207'))[0]
    
    fid = 0
    #TTResultFormat_TTTRRecType =0 ;
    #TTResult_NumberOfRecords = 0; #% Number of TTTR Records in the File;
    #MeasDesc_Resolution =0;      #% Resolution for the Dtime (T3 Only)
    #MeasDesc_GlobalResolution =0;

    f = open(filepath, 'rb')
    # Check if inputfile is a valid PTU file
    # Python strings don't have terminating NULL characters, so they're stripped
    magic = f.read(8).decode("utf-8").strip('\0')
    if magic != "PQTTTR":
        print("ERROR: Magic invalid, this is not a PTU file.")
        return
    version = f.read(8).decode("utf-8").strip('\0')
    #print 'version',version

    file_type = {}
    while True:
        tagIdent = f.read(32).decode("utf-8").strip('\0')
        tagIdx = struct.unpack("<i", f.read(4))[0]
        tagTyp = struct.unpack("<i", f.read(4))[0]
        if tagIdx > -1:
            evalName = tagIdent + '(' + str(tagIdx) + ')'
        else:
            evalName = tagIdent
        if tagTyp == tyEmpty8:
            f.read(8)
        elif tagTyp == tyBool8:
            tagInt = struct.unpack("<q", f.read(8))[0]
            if tagInt == 0:
                file_type[evalName] = False
            else:
                file_type[evalName] = True
        elif tagTyp == tyInt8:
            tagInt = struct.unpack("<q", f.read(8))[0]
            file_type[evalName] = tagInt
        elif tagTyp == tyBitSet64:
            tagInt = struct.unpack("<q", f.read(8))[0]
            file_type[evalName] = tagInt
        elif tagTyp == tyColor8:
            tagInt = struct.unpack("<q", f.read(8))[0]
            file_type[evalName] = tagInt
        elif tagTyp == tyFloat8:
            tagFloat = struct.unpack("<d", f.read(8))[0]
            file_type[evalName] = tagFloat
        elif tagTyp == tyFloat8Array:
            tagInt = struct.unpack("<q", f.read(8))[0]
            file_type[evalName] = tagInt
        elif tagTyp == tyTDateTime:
            tagFloat = struct.unpack("<d", f.read(8))[0]
            tagTime = int((tagFloat - 25569) * 86400)
            tagTime = time.gmtime(tagTime)
            file_type[evalName] = tagTime
        elif tagTyp == tyAnsiString:
            tagInt = struct.unpack("<q", f.read(8))[0]
            tagString = f.read(tagInt).decode("utf-8").strip("\0")
            file_type[evalName] = tagString
        elif tagTyp == tyWideString:
            tagInt = struct.unpack("<q", f.read(8))[0]
            tagString = f.read(tagInt).decode("utf-16le", errors="ignore").strip("\0")
            file_type[evalName] = tagString
        elif tagTyp == tyBinaryBlob:
            tagInt = struct.unpack("<q", f.read(8))[0]
            file_type[evalName] = tagInt
        else:
            print('Illegal Type identifier found! Broken file?',tagTyp)
            exit(0)
        if tagIdent == "Header_End":
            break

    TTResultFormat_TTTRRecType = file_type['TTResultFormat_TTTRRecType']
    if TTResultFormat_TTTRRecType == rtPicoHarpT3:
        isT2 = False
        print( 'PicoHarp T3 data\n')

    elif TTResultFormat_TTTRRecType == rtPicoHarpT2:
        isT2 =True
        print ('PicoHarp T2 data \n')

    elif TTResultFormat_TTTRRecType == rtHydraHarpT3:
        isT2 = False
        print ('HydraHarp V1 T3 data \n')

    elif TTResultFormat_TTTRRecType == rtHydraHarpT2:
        isT2 = True
        print ('HydraHarp V1 T2 data \n')

    elif TTResultFormat_TTTRRecType == rtHydraHarp2T3:
        isT2 = False
        print ('HydraHarp V2 T3 data \n')

    elif TTResultFormat_TTTRRecType == rtHydraHarp2T2:
        isT2 = True
        print( 'HydraHarp V2 T2 data \n')

    elif TTResultFormat_TTTRRecType == rtTimeHarp260NT3:
        isT2 = False
        print ('TimeHarp260N T3 data \n')

    elif TTResultFormat_TTTRRecType == rtTimeHarp260NT2:
        isT2 = True
        print ('TimeHarp260P T3 data \n')

    elif TTResultFormat_TTTRRecType == rtTimeHarp260PT3:
        isT2 = False
        print ('TimeHarp260P T3 data \n')

    elif TTResultFormat_TTTRRecType == rtTimeHarp260PT2:
        isT2 = True
        print ('TimeHarp260P T2 data \n')

    else:
        print('Illegal RecordType')

    #if (isT2):
    #      print '\trecord#\tType\tCh\tTimeTag\tTrueTime/ps\n'
    #else:
    #      print '\trecord#\tType\tCh\tTimeTag\tTrueTime/ns\tDTime\n'

    
    
            
    if TTResultFormat_TTTRRecType   == rtPicoHarpT3: 
        return ReadPT3(f,file_type['TTResult_NumberOfRecords'],file_type['MeasDesc_GlobalResolution'])

    elif TTResultFormat_TTTRRecType == rtPicoHarpT2: #ReadPT2
        return readPT2(f,file_type['TTResult_NumberOfRecords'],file_type['MeasDesc_GlobalResolution'])
    elif TTResultFormat_TTTRRecType == rtHydraHarpT3: #ReadHT3(1)
        return ReadHT3(1,f,file_type['TTResult_NumberOfRecords'],file_type['MeasDesc_GlobalResolution']);
    elif TTResultFormat_TTTRRecType == rtHydraHarpT2: #ReadHT3(1)
        print ('currently this type of file is not supported using this python implementation')
        return False
    elif TTResultFormat_TTTRRecType == rtHydraHarp2T3: 
        return ReadHT3(2,f,file_type['TTResult_NumberOfRecords'],file_type['MeasDesc_GlobalResolution']);
    elif TTResultFormat_TTTRRecType == rtHydraHarp2T2: #ReadHT2(2);
        print ('currently this type of file is not supported using this python implementation')
        return False
    elif TTResultFormat_TTTRRecType == rtTimeHarp260NT3: #ReadHT3(2);
        return ReadHT3(2,f,file_type['TTResult_NumberOfRecords'],file_type['MeasDesc_GlobalResolution']);
    elif TTResultFormat_TTTRRecType == rtTimeHarp260NT2: #ReadHT2(2);
        print ('currently this type of file is not supported using this python implementation')
        return False
    elif TTResultFormat_TTTRRecType == rtTimeHarp260PT3: #ReadHT3(2);
        return ReadHT3(2,f,file_type['TTResult_NumberOfRecords'],file_type['MeasDesc_GlobalResolution']);
    elif TTResultFormat_TTTRRecType == rtTimeHarp260PT2: #ReadHT2(2);
        print ('currently this type of file is not supported using this python implementation')
        return False
    else: 
        print('Illegal RecordType')
        return False
        
    ###Decoder functions
    f.close()
def readPT2(inputfile,TTResult_NumberOfRecords,MeasDesc_GlobalResolution):
    #Contributed by Volodymyr (VolBog).
    chanArr = [0]*TTResult_NumberOfRecords
    trueTimeArr =[0]*TTResult_NumberOfRecords
    dTimeArr= [0]*TTResult_NumberOfRecords
    T2WRAPAROUND = 210698240
    oflcorrection = 0
    cnt_ph = 0
    for recNum in range(0, TTResult_NumberOfRecords):
        truetime = 0
        try:
            recordData = "{0:0{1}b}".format(struct.unpack("<I", inputfile.read(4))[0], 32)
        except:
            print("The file ended earlier than expected, at record %d/%d." \
                  % (recNum, TTResult_NumberOfRecords))
            return False
        channel = int(recordData[0:4], base=2)
        dtime = int(recordData[4:32], base=2)
        if channel == 0xF:  # Special record
            # lower 4 bits of time are marker bits
            markers = int(recordData[28:32], base=2)
            if markers == 0:  # Not a marker, so overflow
                oflcorrection += T2WRAPAROUND
            else:
                # Actually, the lower 4 bits for the time aren't valid because
                # they belong to the marker. But the error caused by them is
                # so small that we can just ignore it.
                true_nSync = oflcorrection + dtime
                truetime = (true_nSync * MeasDesc_GlobalResolution * 1e9)
        else:
            if channel > 4:  # Should not occur
                print("Illegal Channel: #%1d %1u" % (recNum, channel))
            true_nSync = oflcorrection + dtime
            truetime = (true_nSync * MeasDesc_GlobalResolution * 1e9)

        trueTimeArr[cnt_ph] = truetime
        dTimeArr[cnt_ph] = dtime
        chanArr[cnt_ph] = channel+1
        cnt_ph = cnt_ph +1
    return np.array(chanArr[0:cnt_ph]), np.array(trueTimeArr[0:cnt_ph]), np.array(dTimeArr[0:cnt_ph]), MeasDesc_GlobalResolution* 1e9
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
    cnt_M = 0

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
            print ('version not known:',line_one[1])
    
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
            print ('type not recognised')
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
def pt2import(filepath):
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

    cnt_0=0; cnt_1=0; cnt_2=0; cnt_3=0;cnt_4=0; cnt_Ofl=0; cnt_M=0; cnt_Err=0; # just counters
    RESOL=4E-12;   # 4ps
    WRAPAROUND=210698240;
    chanArr = [0]*Records
    trueTimeArr =[0]*Records
    dTimeArr=[0]*Records
    
    for b in range(0,Records):
        T2Record = struct.unpack('i', f.read(4))[0]
        T2time = T2Record & 268435455
        chan = ((T2Record >> 28) & 15);
        chanArr[b]=chan

        if chan ==0:
            cnt_0 = cnt_0+1;
        elif chan == 1:
            cnt_1 = cnt_1+1;
        elif chan == 2: 
            cnt_2 = cnt_2+1;
        elif chan == 3: 
            cnt_3 = cnt_3+1;
        elif chan == 4: 
            cnt_4 = cnt_4+1;
        elif chan == 15:
            markers = T2Record & 15;
            
            if markers ==0:
                ofltime = ofltime +WRAPAROUND;
                cnt_Ofl = cnt_Ofl+1
                
            else:
                cnt_M=cnt_M+1
                
        else:
            cnt_Err = cnt_Err+1
        time = T2time + ofltime;
        trueTimeArr[b] = time*RESOL

    



    return np.array(chanArr)+1, np.array(trueTimeArr)*1000000000, np.array(dTimeArr), Resolution
