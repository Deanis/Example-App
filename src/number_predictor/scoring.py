import base64
import io
import json
import os

import numpy as np
import tensorflow as tf
from PIL import Image


def init():
    global model
    base_path = os.getenv("AZUREML_MODEL_DIR")
    print(f"base_path: {base_path}")
    # list files and dirs in the model_path directory
    list_files(base_path)
    model_path = os.path.join(base_path, "INPUT_model")
    print(f"model_path: {model_path}")
    model = tf.keras.models.load_model(model_path)


def run(raw_data):
    # Load the JSON data from the POST request
    print(f"raw_data: {raw_data}")
    data = json.loads(raw_data)
    print(f"data: {data}")
    # Get the base64-encoded image data
    base64_image = data["data"]
    print(f"base64_image: {base64_image}")
    # Decode the base64 string into bytes
    image_bytes = base64.b64decode(base64_image)
    print(f"image_bytes: {image_bytes}")
    # Open the bytes as an image
    image = Image.open(io.BytesIO(image_bytes))
    # Convert the image to grayscale
    image = image.convert("L")
    # Resize the image to 28x28 pixels, the size expected by the model
    image = image.resize((28, 28))
    # Convert the image to a numpy array and normalize pixel values to [0, 1]
    data = np.array(image) / 255.0
    # The model expects a 4D tensor of shape (batch_size, height, width, channels),
    # so we add an extra dimension to the start and end of the array
    data = np.expand_dims(data, axis=(0, -1))
    # Make prediction
    prediction = model.predict(data)
    # Get the predicted label
    predicted_label = np.argmax(prediction, axis=1)[0]
    return json.dumps(predicted_label.tolist())


def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, "").count(os.sep)
        indent = " " * 4 * (level)
        print("{}{}/".format(indent, os.path.basename(root)))
        subindent = " " * 4 * (level + 1)
        for f in files:
            print("{}{}".format(subindent, f))
