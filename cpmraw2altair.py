#!/usr/bin/env python3

"""
Convert cpmtools disk image to altair 8" floppy format
reverse of altair2cpmraw.py 
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
oh=open(filename+".altair","wb")

sectortranslation=[1,9,17,25,3,11,19,27,5,13,21,29,7,15,23,31,
                   2,10,18,26,4,12,20,28,6,14,22,30,8,16,24,32]

seclen=137
tracks=77
sectrk=32
cpmseclen=128
verify=True

def getChecksum(buf):
    d=0
    for b in buf:
        d=(d+b)%256
    return(d)

track=0
sector=0
buf=[0]*137
while track<tracks:
    print("Working on track:",track,"sector:",sector)
    if bootdisk and track<2:
        xlatesector=sector
    else:
        xlatesector=sectortranslation[sector]-1
    cpmbuf=fh.read(cpmseclen)
    checksum=getChecksum(cpmbuf)

    buf[0]=128|track
    if track<6:
        buf[1]=0
        buf[2]=1
        buf[3:131]=cpmbuf
        buf[131]=255
        buf[132]=checksum
    else:
        buf[1]=xlatesector
        buf[2]=0            # basic file number   (not used for CPM)
        buf[3]=0            # basic bytes written
        buf[5]=0            # basic group pointer
        buf[6]=0            # " continued
        checksum=(checksum+buf[2]+buf[3]+buf[5]+buf[6])%256
        buf[4]=checksum
        buf[7:135]=cpmbuf
        buf[135]=255
        buf[136]=0

    if track<6:
        physector=xlatesector
    else:
        physector=(xlatesector*17)&31

    oh.seek(track*seclen*sectrk+physector*seclen)
    oh.write(bytes(buf))

    sector+=1
    if sector==sectrk:
        sector=0
        track +=1

fh.close()
oh.close()
print("Done!")
