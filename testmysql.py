from mysql import *
import numpy
import numpy as np

mysqldb = MysqlDb()
'''
print mysqldb.insert('dy','aaaaa')
print mysqldb.insert('zhd','aaaaa')
print mysqldb.update('dy','xxxx')
print mysqldb.update('a','abcde')
print mysqldb.delete('a')
print mysqldb.delete('dy')
print mysqldb.fetchone('zhd')
print mysqldb.fetchone('erhe')
'''
s1='[['
s2=']]'
rc = mysqldb.fetchall()
d = {}
#strData=''
for i in xrange(len(rc)):
	#d[rc[i][0]] = rc[i][1]
	#print type(rc[i][1])
	index1 = rc[i][1].index(s1)
	index2 = rc[i][1].index(s2)
	print("index1=%d index2=%d"%(index1,index2))
	if index1>=0 and index2>0:
		strData = rc[i][1][index1+2:index2]
		str2=strData.replace('\n','')
		list1=str2.split()
		array1 = numpy.array(list1)
		array2 = array1.astype(numpy.float32)
		array3 = array2.reshape((1,128))
		d[rc[i][0]] = array3
print("dict:"+str(d))
