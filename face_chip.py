import sys
import dlib
import time
import glob
import os
from skimage import io

predictor_path = '/home/dayou/dlib-models/shape_predictor_5_face_landmarks.dat'

def face_chip(name):
	f = 'origin_picture/'+name+'.jpg'
	detector = dlib.get_frontal_face_detector()
	sp = dlib.shape_predictor(predictor_path)

	starttime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int(time.time())))
	print("start time:", str(starttime))

	print("Processing file: {}".format(f))

	bgr_img = io.imread(f)
	print("cv2.imread ok")
	if bgr_img is None:
		print("Sorry, we could not load '{}' as an image".format(f))
		return

	img = bgr_img#cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
	print("cv2.cvtColor ok")

	dets = detector(img, 1)
	print("detector img ok")

	num_faces = len(dets)
	if num_faces == 0:
		print("Sorry, there were no faces found in '{}'".format(f))
		return

	faces = dlib.full_object_detections()
	print("full object detector ok")
	for detection in dets:
		faces.append(sp(img, detection))

	print("get face clip ok")
	image = dlib.get_face_chip(img, faces[0], size=96)
	print("cv2.cvtColor ok")
	io.imsave('picture/'+name+".jpg",image)
	print("cv2.imwrite ok")
	endtime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int(time.time())))
	print("end time:", str(endtime))

'''
if __name__ == '__main__':
	face_chip('my.jpg', 'zhaodan')
'''
