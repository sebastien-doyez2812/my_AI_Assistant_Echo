import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Layer, Input, Conv2D, MaxPooling2D, Dense, Flatten
import cv2
import numpy as np
import os
import sys
import datetime

os.add_dll_directory("C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.6/bin")

# Define a class for the distance between the the anchor img 
# and the verification image:
class L1Dist(Layer):
  def __init__(self, **kwargs):
    super().__init__()

  def call(self, input_embedding, validation_embedding):
    return tf.math.abs(input_embedding - validation_embedding)
  
#################################################
##            Define the model                 ##
#################################################




def make_embedding():
    # First step:
    inp= Input(shape=(100,100,3))                      #3, 100x100
    c1 = Conv2D(64, (10,10), activation='relu')(inp)   #64, 91x91 , 91 = ((dim input - filter_size + 2* padding)/stride) +1
    m1 = MaxPooling2D(64,(2,2), padding='same')(c1)                            #64, 46x46

    # Second step:
    c2 = Conv2D(128, (7,7), activation='relu')(m1)     #128, 39x39
    m2 = MaxPooling2D(64,(2,2), padding='same')(c2)     #128, 20x20

    # third step:
    c3 = Conv2D(128, (4,4), activation='relu')(m2)     #128, 16x16
    m3 = MaxPooling2D(64,(2,2), padding='same')(c3)     #128, 8x8

    # fourth step:
    c4= Conv2D(256, (4,4), activation='relu')(m3)     #256, 5x5
    f1 = Flatten()(c4)   # Put to a single dimension.... 5 x 5 x 256
    d1= Dense(4096, activation='sigmoid')(f1)  # 5 x5 x 256 => 4096
    return( Model(inputs = [inp], outputs = [d1], name= "embedding"))


def make_siamese_model():
    # Create the embedding part:
    embedding = make_embedding()

    # Anchor image in the network:
    input_image = Input(name='input_img', shape=(100,100,3))

    # Validation image in the network:
    validation_image = Input(name='validation_img', shape=(100,100,3))

    siamise_layer = L1Dist()
    siamise_layer._name = 'distance'
    distances = siamise_layer(embedding(input_image), embedding(validation_image))

    classifier = Dense(1, activation='sigmoid')(distances)

    return Model(inputs=[input_image, validation_image], outputs = classifier, name='SiameseNetwork')



def preprocess(img):
    """
    DEF: 
    ----
    preprocess the image before give it to the model

    ARG:
    ----
    image (extract from open cv)

    """
    img = cv2.resize(img, (100,100))
    img = img / 255.0

    return img


def authentification_AI(model, img):
    results = []
    result = 0
    img = preprocess(img)
    
    for path_verif in os.listdir("AI/tools/authentification/verification_data"):
        # We extract all the image of the verification folder:
        print(os.path.join("AI/tools/authentification/verification_data",path_verif))
        
        verif_img = cv2.imread(os.path.join("AI/tools/authentification/verification_data",path_verif))
        verif_img = preprocess(verif_img)

        result = model.predict(list(np.expand_dims([img, verif_img], axis=1)))
        results.append(result)

    sum = 0
    nb_elements= len(results)
    for i in range(nb_elements):
        sum += results[i]

    return sum/nb_elements



# Create the siamise model:
siamese = make_siamese_model()
siamese.load_weights("AI/tools/authentification\weights.h5")
siamese.summary()



img = cv2.imread("AI/tools/authentification/img_to_test.jpg")
start = datetime.datetime.now()
res = (authentification_AI(siamese, img))
end  = datetime.datetime.now()
  
with open("AI/tools/authentification/result_aut.txt", 'w') as file:
    file.write(str(res[0][0]))

file.close()