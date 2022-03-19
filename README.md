# altair2cpmraw
Converts Altair 8" floppy images to something cpmtools can understand and back

## Purpose

The original Altair 8" floppy drive had 77 tracks consisting of 32 sectors of 137 bytes each. However, CPM operated on 128 byte sectors. The Altair CPM BIOS would wrap this 128 bytes into 137 bytes by adding track data, sector data, and checksum data. It also implemented its own skew mechanism so sectors were not stored sequentially on disk, which sped up access time. Additionally, the format used was slightly different between tracks 0-5 and 6-76.

Additionally, the sectors in the first two tracks were often not skewed, as these were used for boot startup code, and adding a skew table would complicate and lengthen the bootloader at a time when the bootloader may have been entered by toggle switches on the front panel.

Cpmtools, available at http://www.moria.de/~michael/cpmtools/, allows one to manipulate CPM disks, but does not understand the Altair format due to the odd sector size, skew table, and change in behavior depending upon track. These two utilities convers the altair disk image into something cpmtools can understand and back.

## Usage

altair2cpmraw.py extracts the abstracted CPM 128 byte sectors and writes them to a new 'cpmraw' image linearly, so cpmtools can understand it. It can also verify the integrity by using the same checksum algorithm as the original CPM BIOS.

Run it by passing the image name, such as:

	./altair2cpmraw.py file.dsk

It will output a new file with the name file.dsk.cpmraw

cpmraw2altair.py does the opposite by wrapping the CPM sectors into 137 bytes and adding the appropriate track, sector, and checksum information and skewing it to the right physical location. 

Run it by passing the image name, such as:

	./cpmraw2altair.py file.cpmraw

It will output a new file with the name file.cpmraw.altair

## Configuring cpmtools

Add this to your cpm tools diskdefs file, likely in /etc/cpmtools/diskdefs:

	diskdef altaircpmraw
	  seclen 128
	  tracks 77
	  sectrk 32
	  blocksize 2048
	  maxdir 64
	  boottrk 2
	  os 2.2
	end

Then use the '-f altaircpmraw' option when using cpmtools. For example, to list the files:

	cpmls -f altaircpmraw file.dsk.cpmraw

For another example, to copy a file off the image:

	cpmcp -f altaircpmraw file.dsk.cpmraw 0:PIP.COM .


## --boot option

For both scripts, add the --boot option after filename to tell the script to not 'unskew' the first two tracks. This is only really needed if you're working with a boot disk and want to manipulate the boot record so you need it intact and in a sequential order.
For standard usage (extracting and adding files), the CPM file allocation table shouldn't reference those two tracks at all so the --boot is not needed.

## Ideas for improvements

* Do proper parameter management - right now its just quick and dirty sys.argv[]
* Add options for output filename
* Add check to ensure not overwriting an existing output file
* Add support for Altair 5.25" disks

