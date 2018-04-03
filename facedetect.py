from keras.models import Sequential
from keras.layers import Conv2D, ZeroPadding2D, Activation, Input, concatenate
from keras.models import Model
from keras.layers.normalization import BatchNormalization
from keras.layers.pooling import MaxPooling2D, AveragePooling2D
from keras.layers.merge import Concatenate
from keras.layers.core import Lambda, Flatten, Dense
from keras.initializers import glorot_uniform
from keras.engine.topology import Layer
from keras import backend as K
K.set_image_data_format('channels_first')
import cv2
import os
import numpy as np
from numpy import genfromtxt
import pandas as pd
import tensorflow as tf
from fr_utils import *
from inception_blocks_v2 import *
from face_chip import *
from mysql import *
from write_pipe import *
import pika
import time
import logging
import json
import base64
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#%matplotlib inline
#%load_ext autoreload
#%autoreload 2

np.set_printoptions(threshold=np.nan)

def nowtime():
	print("time:",str(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(int(time.time())))))

def triplet_loss(y_true, y_pred, alpha = 0.2):
    """
    Implementation of the triplet loss as defined by formula (3)
    
    Arguments:
    y_true -- true labels, required when you define a loss in Keras, you don't need it in this function.
    y_pred -- python list containing three objects:
            anchor -- the encodings for the anchor images, of shape (None, 128)
            positive -- the encodings for the positive images, of shape (None, 128)
            negative -- the encodings for the negative images, of shape (None, 128)
    
    Returns:
    loss -- real number, value of the loss
    """
    
    anchor, positive, negative = y_pred[0], y_pred[1], y_pred[2]
    
    # Step 1: Compute the (encoding) distance between the anchor and the positive, you will need to sum over axis=-1
    pos_dist = tf.reduce_sum(tf.square(tf.subtract(anchor, positive)), axis=-1)
    # Step 2: Compute the (encoding) distance between the anchor and the negative, you will need to sum over axis=-1
    neg_dist = tf.reduce_sum(tf.square(tf.subtract(anchor, negative)), axis=-1)
    # Step 3: subtract the two previous distances and add alpha.
    basic_loss = tf.add(tf.subtract(pos_dist, neg_dist), alpha)
    # Step 4: Take the maximum of basic_loss and 0.0. Sum over the training examples.
    loss = tf.reduce_sum(tf.maximum(basic_loss, 0))
    # END CODE HERE 
    
    return loss



def verify(image_path, identity, database, model):
    """
    Function that verifies if the person on the "image_path" image is "identity".
    
    Arguments:
    image_path -- path to an image
    identity -- string, name of the person you'd like to verify the identity. Has to be a resident of the Happy house.
    database -- python dictionary mapping names of allowed people's names (strings) to their encodings (vectors).
    model -- your Inception model instance in Keras
    
    Returns:
    dist -- distance between the image_path and the image of "identity" in the database.
    door_open -- True, if the door should open. False otherwise.
    """
    
    
    encoding = img_to_encoding(image_path=image_path, model=model)
    
    dist = np.linalg.norm(np.subtract(database[identity], encoding))
    
    if dist<0.7:
        print("It's " + str(identity) + ", welcome home!")
        door_open = True
    else:
        print("It's not " + str(identity) + ", please go away")
        door_open = False
        
        
    return dist, door_open


def who_is_it(image_path, database, model):
    """
    Implements face recognition for the happy house by finding who is the person on the image_path image.
    
    Arguments:
    image_path -- path to an image
    database -- database containing image encodings along with the name of the person on the image
    model -- your Inception model instance in Keras
    
    Returns:
    min_dist -- the minimum distance between image_path encoding and the encodings from the database
    identity -- string, the name prediction for the person on image_path
    """
    
    identity=''
    
    encoding = img_to_encoding(image_path, model)
    
    min_dist = 100
    
    for (name, db_enc) in database.items():
        
        dist = np.linalg.norm(np.subtract(db_enc, encoding))

        if dist<min_dist:
            min_dist = dist
            identity = name

    
    if min_dist > 0.7:
        msg = "Not in the database."
        rspcode = 1
    else:
        msg = "it's " + str(identity) + ", the distance is " + str(min_dist)
        rspcode = 0
    print(msg)
        
    return min_dist, identity, rspcode, msg

def recog_func(name):
    filename = face_chip(name)
    filePath = 'picture/'+filename+'.jpg'
    dist, name,rspcode, rspmsg = who_is_it(filePath, databases, FRmodel)
    nowtime()
    dt = {'tran_type':'tran_recognition','name':name, 'rspcode':rspcode,'rspmsg':rspmsg}
    write_pipe(json.dumps(dt))

def add_func(name):
    filename = face_chip(name)
    filePath = 'picture/'+filename+'.jpg'
    data = img_to_encoding(filePath, FRmodel)
    databases[name]=data
    print(databases)
    mysqldb.update(name,data)
    nowtime()
    dt = {'tran_type':'tran_add','name':name, 'rspcode':0,'rspmsg':'add success.'}
    write_pipe(json.dumps(dt))

def callback(ch, method, properties, body):
	jsonData = json.loads(body)
	tranType = jsonData['tran_type']
	print(" tranType %r" % tranType)
	if tranType == "tran_add":
		name = jsonData['name']
		imgData = jsonData['image']
		image = base64.b64decode(imgData)
		filePath = 'origin_picture/'+name+'.jpg'
		imgFile = open(filePath, 'wb')
		imgFile.write(image)
		imgFile.close()
		add_func(name)
	if tranType == "tran_recognition":
		imgData = jsonData['image']
		t = time.time()
		name = str(int(round(t*1000)))
		image = base64.b64decode(imgData)
		filePath = 'origin_picture/'+name+'.jpg'
		imgFile = open(filePath, 'wb')
		imgFile.write(image)
		imgFile.close()
		recog_func(name)
	ch.basic_ack(delivery_tag = method.delivery_tag)
	print(" [x] Done")

FRmodel = faceRecoModel(input_shape=(3, 96, 96))
print("init faceRecoModel ok")
mysqldb = MysqlDb()
databases = mysqldb.fetchall_dict()
print("databases:")
print databases

def sendMq(message):
	connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
	channel = connection.channel()
	channel.basic_publish(exchange='face.out_exchange',routing_key='', body=message)
	channel.close
	print("[x] Send msg ok:")

if __name__=='__main__':
	print("Total Params:", FRmodel.count_params())
	print("main")

	nowtime()
	FRmodel.compile(optimizer = 'adam', loss = triplet_loss, metrics = ['accuracy'])
	nowtime()
	print("compile ok")

	load_weights_from_FaceNet(FRmodel)
	nowtime()
	print("load weight ok")

	connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
	channel = connection.channel()
	channel.basic_qos(prefetch_count=1)
	channel.basic_consume(callback, queue='face.in_queue')
	nowtime()
	print(' [*] Waiting for messages. To exit press CTRL+C')
	print("waiting for message")
	channel.start_consuming()
