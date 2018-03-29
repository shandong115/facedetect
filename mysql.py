import MySQLdb as mydb
import string
import numpy
import numpy as np

class MysqlDb:
	__conn = 0
	__cur=0
	__host='127.0.0.1'
	__port=3306
	__user='face'
	__passwd='asdasd321321'
	__db='facedb'
	__table='person'
	def __init__(self):
		try:
			self.__conn = mydb.connect(host=self.__host,port=self.__port,user=self.__user,passwd=self.__passwd,db=self.__db)
			self.__cur = self.__conn.cursor()
			print('db conn ok')
		except mydb.Error,e:
			print e.args[1]

	def __del__(self):
		self.__cur.close()
		self.__conn.close()
		print('db close ok')

	def __execute(self,sql):
		try:
			result = self.__cur.execute(sql)
			self.__conn.commit()
			print('execute sql(%s) ok %d'%(sql,result))
			return result
		except mydb.Error,e:
			print e.args[1]
			self.__conn.rollback()
			return 0

	def insert(self, name, data):
		sql = "insert into person (name,value)values('%s','%s')"%(name,data)
		return self.__execute(sql)

	def update(self, name, data):
		if None != self.fetchone(name):
			sql = "update person set value='%s' where name='%s'"%(data,name)
			result = self.__execute(sql)
		else:
			result = self.insert(name, data)
		return result

	def delete(self, name):
		sql = "delete from person where name='%s'"%(name)
		return self.__execute(sql)

	def fetchone(self, name):
		sql = "select value from person where name='%s'"%(name)
		try:
			self.__cur.execute(sql)
			result = self.__cur.fetchone()
		except mydb.Error,e:
			print e.args[1]
		print('execute sql(%s) ok [%s]'%(sql,result))
		return result

	def fetchall(self ):
		sql = "select name, value from person"
		try:
			self.__cur.execute(sql)
			result = self.__cur.fetchall()
		except mydb.Error,e:
			print e.args[1]
		print('execute sql(%s) ok[%s]'%(sql,result))
		return result
	def fetchall_dict(self):
		results = self.fetchall()
		s1='[['
		s2=']]'
		d={}
		for i in xrange(len(results)):
			index1 = results[i][1].index(s1)
			index2 = results[i][1].index(s2)
			if index1>=0 and index2>0:
				strData = results[i][1][index1+2:index2]
				str2=strData.replace('\n','')
				list1=str2.split()
				array1 = numpy.array(list1)
				array2 = array1.astype(numpy.float32)
				array3 = array2.reshape((1,128))
				d[results[i][0]] = array3
		return d

if __name__ == '__main__':
	mysqldb = MysqlDb()
#	print mysqldb.fetchall()
#	print mysqldb.update('dan','abcde')
#	print mysqldb.insert('dy','aaaaa')
#	print mysqldb.update('dy','xxxx')
#	print mysqldb.delete('dy')
#	print mysqldb.insert('zhd','aaaaa')
#	print mysqldb.fetchone('zhd')
#	print mysqldb.update('a','abcde')
#	print mysqldb.delete('a')
#	print mysqldb.fetchone('erhe')
#	print mysqldb.fetchall()
	print mysqldb.fetchall_dict()
