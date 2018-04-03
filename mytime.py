import time

def nowTime():
	return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int(time.time())))

if __name__ == '__main__':
	print nowTime()
