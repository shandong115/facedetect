import os
import time
from mytime import *

file_path = "/tmp/face_file.pipe"

def write_pipe(s):
	try:  
		os.mkfifo( file_path )  
	except OSError, e:  
		print "mkfifo error:", e  

	f = os.open( file_path, os.O_SYNC | os.O_CREAT | os.O_RDWR )  
	r=os.write(f, s)
	os.close(f)
	print s
	return r

if __name__=='__main__':
	print write_pipe(nowTime())
