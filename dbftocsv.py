# routine to extract files from DBF to CSV
from dbfread import DBF
import sys
import csv
import urllib2
import struct
from smb.SMBHandler import SMBHandler

if len(sys.argv)<2:
	print ("ERROR - please specify the file you are calling")
	exit()


counter=0
data=[]

def bytes2int(str):
 return int(str.encode('hex'), 16)

def bytes2hex(str):
 return '0x'+str.encode('hex')

def int2bytes(i):
 h = int2hex(i)
 return hex2bytes(h)

def int2hex(i):
 return hex(i)

def hex2int(h):
 if len(h) > 1 and h[0:2] == '0x':
  h = h[2:]

 if len(h) % 2:
  h = "0" + h

 return int(h, 16)

def hex2bytes(h):
 if len(h) > 1 and h[0:2] == '0x':
  h = h[2:]

 if len(h) % 2:
  h = "0" + h

 return h.decode('hex')

def bytes_to_int(bytes):
    result = 0
    for b in bytes:
        result = result * 256 + int(b)
    return result

def int_to_bytes(value, length):
    result = []
    for i in range(0, length):
        result.append(value >> (i * 8) & 0xff)
    result.reverse()
    return result

class field:
	fieldname=""
	fieldtype=""
	fieldlength=0
	fielddecimalcount=0
	fieldpos=0
	def __init__(self,name,type,length,count,fldpos):
		self.fieldname=name.decode(encoding='utf-8', errors='strict')
		self.fieldtype=type.decode(encoding='utf-8', errors='strict')
		self.fieldlength=bytes2int(length)
		self.fielddecimalcount=count.decode(encoding='utf-8', errors='strict')
		self.fieldpos=fldpos

def two_bytes_to_int(x):
	return (256*x[0])+x[1]

def gettype(type):
	if type=='\x02':
		print('FoxBASE')
	if type=='\x03':
		print("FoxBASE+/Dbase III plus, no memo")
	if type=='\x30':
		print("Visual FoxPro")
	if type=='\x31':
		print("Visual FoxPro, Autoincrement enabled")
	if type== '\x32':
		print("Visual FoxPro, With Field Type Varchar or Varbinary")
	if type=='\x43':
		print("dbase IV SQL Table files, no memo")
	if type=='\x83':
                print("FoxBase+/Dbase II Plus, with memo")
	if type=='\x8B':
		print("dbase IV with memo")
	if type=='\xCB':
		print("dBase IV table files, with memo")
	if type=='\xF5':
		print("FoxPro 2.x (or earlier) with memo")
	if type=='\xE5':
		print("HiPer-Six format with SMT memo file")
	if type=='\xFB':
		print("FoxBase")

def getbytes(numberofbytes):
	global counter
	global data
	bytes=data[counter:numberofbytes+counter]
	counter=counter+numberofbytes
	return bytes

director = urllib2.build_opener(SMBHandler)
fh = director.open(sys.argv[1])
data=fh.read()
fh.close

byte = getbytes(1)  # Valid dBASE for DOS file; bits 0-2 indicate version number, bit 3 indicates the presence of a dBASE for DOS memo file, bits 4-6 

gettype(byte) # print out the type of thing
lastupdate= getbytes(3)  # date of last update formated as YYMMDD
numberofrecords=bytes2int(getbytes(4))  # number of records 32 bit number
positionoffirstdatarecord=getbytes(2) # number of bytes in header 16 bit number
numberofbytesinrecord=bytes2int(getbytes(2)) # number of bytes in record
reserved=getbytes(2) # reserved fille with 0
incomplete=getbytes(1) # flag indicating incomplete transaction
encryption=getbytes(1) # flag indicating encryption
reservedfordbase=getbytes(12) # reserved for DBase for DOS in a multi-user enviornment
productionmdxflag=getbytes(1) # Production .mdx file flag; 0x01 if there is a production .mdx file, 0x00 if not
languagedriverid=getbytes(1) # language driver id
reserved2=getbytes(2) # reserved fill with 0

# now read the fields
fldcount=0
test="1A"

fields=[]

#sum the field lengths to get the record lenght

while fldcount<255:
	if data[counter]=='\x0D':
		counter=counter+1
		break
	fieldname=getbytes(11)
	fieldtype=getbytes(1)
	reserved=getbytes(4)
	fieldlength=getbytes(1)
	print (str(fieldname)+" "+fieldtype.decode(encoding='utf-8', errors='strict')+" "+ str(bytes2int(fieldlength)))
	fielddecimalcount=getbytes(1)
	workareaid=getbytes(2)
	example=getbytes(1)
	reserved=getbytes(10)
	productionmdxflag=getbytes(1)
	x=field(fieldname,fieldtype,fieldlength,fielddecimalcount,fldcount)
	fields.append(x)
	fldcount=fldcount+1

# backlink foxpro only
if byte=='\x30':
	backlink=getbytes(263)
	print(backlink)

# data
# move to the position indicated in the header
#counter=positionoffirstdatarecord
print (str(numberofrecords))
recordcounter=0
while counter<len(data):
	deleteflag=getbytes(1)
	recordstring=""
	if deleteflag=='\x2A':
		recordstring=recordstring+("Deleted")+" "
	for x in range(0,len(fields)):
		fieldobj=fields[x]
		thisdata=getbytes(int(fieldobj.fieldlength))
		recordstring=recordstring+str(thisdata)+","
	print (recordstring)
	recordcounter=recordcounter+1


print (str(recordcounter)+" Records")
