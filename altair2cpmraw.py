#!/usr/bin/env python3


"""
Convert Altair 8" disk images to something cpmtools can understand
Copyright (C) 2022 Don Barber

Details on Altair physical disk format
determined by reading Burcon CPM 2.2 bios code
Available at
https://deramp.com/downloads/altair/software/8_inch_floppy/CPM/CPM%202.2/Burcon%20CPM/BIOS.PRN

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import sys

filename=sys.argv[1]

bootdisk=False
if "--boot" in sys.argv:     #Don't send tracks 0 and 1 through
    bootdisk=True              #sector translation
    print("Not sending tracks 0 and 1 through translation.")

fh=open(filename,"rb")
oh=open(filename+".cpmraw","wb")

sectortranslation=[1,9,17,25,3,11,19,27,5,13,21,29,7,15,23,31,
                   2,10,18,26,4,12,20,28,6,14,22,30,8,16,24,32]

seclen=137
tracks=77
sectrk=32
verify=True

def getChecksum(buf):
    d=0
    for b in buf:
        d=(d+b)%256
    return(d)

track=0
sector=0
while track<tracks:
    print("Working on track:",track,"sector:",sector)
    if bootdisk and track<2:
        xlatesector=sector
    else:
        xlatesector=sectortranslation[sector]-1
    if track<6:
        physector=xlatesector
    else:
        physector=(xlatesector*17)&31
    fh.seek(track*seclen*sectrk+physector*seclen)
    indata=fh.read(seclen)
    if verify:
        if indata[0]!=128|track:
            print(indata[0],track,128|track)
            raise Exception("Does not match track")
        if track<6:
            if indata[1]!=0 and indata[2]!=1:
                raise Exception("Header bytes 1 and 2 do not match \x00\x01")
            if indata[131]!=255:
                raise Exception("Bad end byte")
            checksum=getChecksum(indata[3:-6])
            if indata[132]!=checksum:
                raise Exception("Checksum does not match")
        else:
            if indata[1]!=xlatesector:
                print(sector,xlatesector,physector,indata[1])
                raise Exception("Does not match sector")
            # Bytes 2,3,5,6 used in checksum but not set specifically
            # so seems to be whatever happened to be in RAM at write
            # These bytes are used in Altair disk basic but not by CPM
            checksum=getChecksum(indata[7:-2])
            checksum=(checksum+indata[2]+indata[3]+indata[5]+indata[6])%256
            if checksum!=indata[4]:
                raise Exception("Checksum does not match")
            if indata[136]!=0 and indata[135]!=255:
                raise Exception("Bad end byte")
    if track<6:
        outdata=indata[3:-6]
    else:
        outdata=indata[7:-2]
    oh.write(outdata)
    sector+=1
    if sector==sectrk:
        sector=0
        track +=1
fh.close()
oh.close()
print("Done!")

