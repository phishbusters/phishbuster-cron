import requests
import numpy as np

from scipy.spatial.distance import cosine
from keras.preprocessing import image
from keras.applications.vgg16 import VGG16, preprocess_input
from PIL import Image
from io import BytesIO


def feature_extraction(model, image_path):
    img = load_and_preprocess_image(image_path)
    features = model.predict(img)
    return features.flatten()


def image_similarity(image1_path, image2_path):
    model = VGG16(weights='imagenet', include_top=False)

    image1_features = feature_extraction(model, image1_path)
    image2_features = feature_extraction(model, image2_path)

    similarity = 1 - cosine(image1_features, image2_features)

    return similarity


def image_comparison(image1_path, image2_path, threshold=0.7):
    similarity = image_similarity(image1_path, image2_path)
    return similarity >= threshold


def load_and_preprocess_image(image_path_or_url):
    if image_path_or_url.startswith('http://') or image_path_or_url.startswith('https://'):
        response = requests.get(image_path_or_url)
        img = Image.open(BytesIO(response.content)).convert('RGB').resize((224, 224))
    else:
        img = Image.open(image_path_or_url).convert('RGB').resize((224, 224))

    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    return x


if __name__ == "__main__":
    # Cargar el modelo VGG16
    model = VGG16(weights='imagenet', include_top=False)

    # URL de imagen de ejemplo
    image1_url = 'https://pbs.twimg.com/profile_images/1677046344999944193/WRhRxoS2_400x400.jpg'
    image2_url = 'https://pbs.twimg.com/profile_images/1577701183136927745/hiQ1UwHm_400x400.jpg'

    # Extraer características de las imágenes
    image1_features = feature_extraction(model, image1_url)
    print('Features extracted from image 1', image1_features)
    image2_features = feature_extraction(model, image2_url)
    print('Features extracted from image 2', image2_features)

    # Calcular la similitud
    similarity = 1 - cosine(image1_features, image2_features)

    # Imprimir la similitud del coseno
    print(f"Cosine Similarity between images: {similarity}")
