import tensorflow as tf
import numpy as np
import os
import cv2
import random

import math
import timeit
import matplotlib.pyplot as plt

from os import listdir
from os.path import isfile, join
from os import walk

def get_CIFAR10_data(num_training=49000, num_validation=1000, num_test=10000):
    """
    Load the CIFAR-10 dataset from disk and perform preprocessing to prepare
    it for the two-layer neural net classifier. These are the same steps as
    we used for the SVM, but condensed to a single function.  
    """
    # Load the raw CIFAR-10 data
    cifar10_dir = 'cs231n/datasets/cifar-10-batches-py'
    X_train, y_train, X_test, y_test = load_CIFAR10(cifar10_dir)

    # Subsample the data
    mask = range(num_training, num_training + num_validation)
    X_val = X_train[mask]
    y_val = y_train[mask]
    mask = range(num_training)
    X_train = X_train[mask]
    y_train = y_train[mask]
    mask = range(num_test)
    X_test = X_test[mask]
    y_test = y_test[mask]

    # Normalize the data: subtract the mean image
    mean_image = np.mean(X_train, axis=0)
    X_train -= mean_image
    X_val -= mean_image
    X_test -= mean_image

    return X_train, y_train, X_val, y_val, X_test, y_test
    
def simple_model(X,y):
    # define our weights (e.g. init_two_layer_convnet)
    
    # setup variables
    Wconv1 = tf.get_variable("Wconv1", shape=[7, 7, 3, 32])
    bconv1 = tf.get_variable("bconv1", shape=[32])
    W1 = tf.get_variable("W1", shape=[396288, 21])
    b1 = tf.get_variable("b1", shape=[21])

    # define our graph (e.g. two_layer_convnet)
    a1 = tf.nn.conv2d(X, Wconv1, strides=[1,1,1,1], padding='VALID') + bconv1
    h1 = tf.nn.relu(a1)
    h1_flat = tf.reshape(h1,[-1,396288])
    y_out = tf.matmul(h1_flat,W1) + b1
    return y_out


def run_model(session, predict, loss_val, Xd, yd,
              epochs=1, batch_size=64, print_every=100,
              training=None, plot_losses=False):
    # have tensorflow compute accuracy
    correct_prediction = tf.equal(tf.argmax(predict,1), yd)
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
    
    # shuffle indicies
    train_indicies = np.arange(Xd.shape[0])
    np.random.shuffle(train_indicies)

    training_now = training is not None
    
    # setting up variables we want to compute (and optimizing)
    # if we have a training function, add that to things we compute
    variables = [loss_val,correct_prediction,accuracy]
    if training_now:
        variables[-1] = training
    
    # counter 
    iter_cnt = 0
    for e in range(epochs):
        # keep track of losses and accuracy
        correct = 0
        losses = []
        # make sure we iterate over the dataset once
        for i in range(int(math.ceil(Xd.shape[0]/batch_size))):
            # generate indicies for the batch
            start_idx = (i*batch_size)%X_train.shape[0]
            idx = train_indicies[start_idx:start_idx+batch_size]
            
            # create a feed dictionary for this batch
            feed_dict = {X: Xd[idx,:],
                         y: yd[idx],
                         is_training: training_now }
            # get batch size
            actual_batch_size = yd[i:i+batch_size].shape[0]
            
            # have tensorflow compute loss and correct predictions
            # and (if given) perform a training step
            loss, corr, _ = session.run(variables,feed_dict=feed_dict)
            
            # aggregate performance stats
            losses.append(loss*actual_batch_size)
            correct += np.sum(corr)
            
            # print every now and then
            if training_now and (iter_cnt % print_every) == 0:
                print("Iteration {0}: with minibatch training loss = {1:.3g} and accuracy of {2:.2g}"\
                      .format(iter_cnt,loss,np.sum(corr)/actual_batch_size))
            iter_cnt += 1
        total_correct = correct/Xd.shape[0]
        total_loss = np.sum(losses)/Xd.shape[0]
        print("Epoch {2}, Overall loss = {0:.3g} and accuracy of {1:.3g}"\
              .format(total_loss,total_correct,e+1))
        # if plot_losses:
        #     plt.plot(losses)
        #     plt.grid(True)
        #     plt.title('Epoch {} Loss'.format(e+1))
        #     plt.xlabel('minibatch number')
        #     plt.ylabel('minibatch loss')
        #     plt.show()
    return total_loss,total_correct

def main():
    Xtr = [];
    ytr = [];
    Xte = [];
    yte = [];
    min_width = 135
    min_height = 102

    root_path = "./ut-zap50k-images" #Zappos root directory
    dirs = [name for name in os.listdir(root_path) if os.path.isdir(os.path.join(root_path, name))]
    num_classes = 21
    for directory in dirs:
        print(directory)
        class_path = root_path + "/" + directory
        class_images = [img for img in os.listdir(class_path) if img[-4:] == ".jpg"] #get all jpg files
        num_to_add_to_test = len(class_images) // 10
        if num_to_add_to_test == 0:
            num_to_add_to_test = 1
        num_added_to_test = 0
        for img_name in class_images: 
            img_path = class_path + "/" + img_name
            img = cv2.imread(img_path, 1)
            
            """
            if img.shape[0] < min_height:
                min_height = img.shape[0]
            if img.shape[1] < min_width:
                min_width = img.shape[1]
            """
        
            img = img[:min_height, :min_width, :]
                
            if num_added_to_test < num_to_add_to_test: #haven't added enough to test set
                Xte.append(img)
                yte.append(directory)
                num_added_to_test += 1
            else:
                Xtr.append(img)
                ytr.append(directory)

    print(min_width)
    print(min_height)

    print(img.shape)
    print(len(Xtr))
    print(len(Xte))
    print(len(ytr))
    print(len(yte))

    labels_to_nums = {'Ankle1':1, 'Knee High2':2, 'Mid-Calf3':3, 'Over the Knee4':4, 'Prewalker Boots5':5, 'Athletic6':6, 'Flat7':7, 
                      'Heel8':8, 'Boat Shoes9':9, 'Clogs and Mules10':10, 'Crib Shoes11':11, 'Firstwalker12':12, 'Flats13':13, 
                      'Heels14':14, 'Loafers15':15, 'Oxfords16':16, 'Prewalker17':17, 'Sneakers and Athletic Shoes18':18, 'Boot19':19,
                     'Slipper Heels20':20, 'Slipper Flats21': 21}

    H, W, C = min_height, min_width, 3

    num_validation = 2000
    num_training = len(Xtr) - num_validation

    X_train = np.zeros( (num_training, H, W, C) )
    X_val = np.zeros( (num_validation, H, W, C) )
    X_test = np.zeros( (len(Xte), H, W, C) )

    indices_for_validation = random.sample(range(len(Xtr)), num_validation)
    print(np.max(indices_for_validation))

    y_val = np.zeros( num_validation )
    y_train = np.zeros ( num_training )
    y_test = np.zeros(len(yte))

    validation_index = 0
    train_index = 0
    for i in range(len(Xtr)):
        if i in indices_for_validation:
            X_val[validation_index, :, :, :] = Xtr[i]
            y_val[validation_index] = labels_to_nums[ytr[i]]
            validation_index += 1
        else:
            X_train[train_index, :, :, :] = Xtr[i]
            y_train[train_index] = labels_to_nums[ytr[i]]
            train_index += 1

    for i in range(len(Xte)):
        X_test[i, :, :, :] = Xte[i]
        y_test[i] = labels_to_nums[yte[i]]

    # Normalize the data: subtract the mean image
    mean_image = np.mean(X_train, axis=0)
    X_train -= mean_image
    X_val -= mean_image
    X_test -= mean_image

    print(X_train.shape)
    print(y_train.shape)
    print(X_val.shape)
    print(y_val.shape)
    print(X_test.shape)
    print(y_test.shape)

    # clear old variables
    tf.reset_default_graph()

    # setup input (e.g. the data that changes every batch)
    # The first dim is None, and gets sets automatically based on batch size fed in
    X = tf.placeholder(tf.float32, [None, min_height, min_width, 3])
    y = tf.placeholder(tf.int64, [None])
    is_training = tf.placeholder(tf.bool)

    y_out = simple_model(X,y)

    # define our loss
    total_loss = tf.losses.hinge_loss(tf.one_hot(y,21),logits=y_out)
    mean_loss = tf.reduce_mean(total_loss)

    # define our optimizer
    optimizer = tf.train.AdamOptimizer(5e-4) # select optimizer and set learning rate
    train_step = optimizer.minimize(mean_loss)


    with tf.Session() as sess:
        with tf.device("/cpu:0"): #"/cpu:0" or "/gpu:0" 
            sess.run(tf.global_variables_initializer())
            print('Training')
            run_model(sess,y_out,mean_loss,X_train,y_train,1,64,100,train_step,True)
            print('Validation')
            run_model(sess,y_out,mean_loss,X_val,y_val,1,64)
if __name__ == '__main__':
	main()


