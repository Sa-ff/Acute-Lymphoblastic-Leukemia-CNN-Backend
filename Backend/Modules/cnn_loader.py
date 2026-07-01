# cnn_loader.py
import os
from pathlib import Path
from typing import Dict, Tuple, List
import asyncio
from datetime import datetime
import numpy as np
from io import BytesIO
from PIL import Image
import tensorflow as tf
from tensorflow.keras.applications.efficientnet import preprocess_input


# config 
MODEL_PATH = r"C:\Users\Saffia Naureen\python_projects\sdpapp\efficientnet_2_all_20.keras"
CLASS_NAMES: List[str] = ['Pro B-ALL', 'Not ALL', 'Early Pre-B-ALL', 'Pre-B-ALL']
TARGET_SIZE = (300,300)

# load model once at import time
MODEL: tf.keras.Model = tf.keras.models.load_model(MODEL_PATH)
print("Loaded model input shape:", MODEL.input_shape)
#MODEL.make_predict_function()  # defensive; mostly TF1 style but safe

def preprocess_image_bytes(file_bytes) -> np.ndarray: 
    #Converts the raw image bytes into a preprocessed tensor ready for model inference
    #file_bytes: Binary image data
    #output:  np.ndarray i.e. Preprocessed image array with shape (1, 300, 300, 3)
    image = Image.open(BytesIO(file_bytes)).convert("RGB")
    """
    BytesIO(file_bytes) : file_bytes : bin data of our image (jpg), a in-memory 
    file lke object is created from the bytes. so the BytesIO object can read the 
    image as a file.
    Image.open(BytesIO(file_bytes)) : PIL's Image.open() reads image data 
    from the BytesIO file-like object. and it decodes the binary data into an image object.
    and outputs a PIL.Image.Image object with original dimensions and color format.
    Image.open(BytesIO(file_bytes)).convert("RGB") :  making sure that the 
    image is in RGB color space (3 channels). Output is a PIL.Image.Image in RGB format

    question: why not just skip the ByteesIO and just Image.open()? cus image is TX as bytes? 
    Image.open() expects a file path or file-like object.

In FastAPI, uploaded files arrive as raw bytes (file_bytes).

BytesIO(file_bytes) wraps those bytes in a file-like object so PIL can read them. That’s why you need BytesIO.
    """
    image = image.resize(TARGET_SIZE, Image.BILINEAR) #default resampling filter, stretches/squishes image, o/p: Square PIL.Image.Image of exactly 224×224 pixels
    print("Raw PIL size:", image.size, "mode:", image.mode)

    img_array = np.array(image,  dtype=np.float32) #o/p: (224, 224, 3) : (height, width, channels), uint8, 0-255 for each pixel channel why???????????
    img_array = preprocess_input(img_array) # (224, 224, 3), float32, normaised floating point values
    img_array = np.expand_dims(img_array, axis=0) # Adds a new dimension to the array. 
    #axis=0 - adds dimension at position 0 (beginning) why?????????????????
    #o/p: (batch_size, height, width, channels) :(1,224,224,3)
    #Batch Size is 1 i.e single image prediction
    
    print("Preprocessed shape:", img_array.shape)
    return img_array

def postprocess_preds(preds: np.ndarray) -> Tuple[str, float, Dict[str, float]]:
    probs = preds[0].astype(float)  # ensure plain floats
    index = int(np.argmax(probs))
    class_name = CLASS_NAMES[index]
    confidence = float(probs[index]* 100)
    all_probs = {CLASS_NAMES[i]: float(probs[i]) for i in range(len(CLASS_NAMES))}
    return class_name, confidence, all_probs

async def predict_from_bytes(file_bytes: bytes) -> Tuple[str, float, Dict[str, float]]:
    """
    Async wrapper that runs blocking TF predict off the event loop.
    Returns (predicted_class, confidence, all_probs)
    """
    arr = preprocess_image_bytes(file_bytes)
    # run sync predict in thread
    preds = await asyncio.to_thread(MODEL.predict, arr)
    return postprocess_preds(preds)
