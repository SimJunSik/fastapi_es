from google.cloud import vision
from konlpy.tag import Okt
import os
import io
import json

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'meme-369708-e4bd2f8056f2.json'

client = vision.ImageAnnotatorClient()

# The name of the image file to annotate
# file_name = os.path.abspath('./img/263A4D3D55B585AC0C.jpeg')

# # Loads the image into memory
# with io.open(file_name, 'rb') as image_file:
#     content = image_file.read()

# image = vision.Image(content=content)

# Performs label detection on the image file
dir_path = "./crawling_images/crawling_images/2022125_12958_박명수 짤/"

# list to store files
res = []

# Iterate directory
for path in os.listdir(dir_path):
    print(path)

    # check if current path is a file
    if os.path.isfile(os.path.join(dir_path, path)):
        res.append(path)

for r in res:
    with io.open(dir_path + r, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    okt = Okt()
    print(r, list(filter(lambda x: len(x) > 1, okt.nouns(response.text_annotations[0].description))))

def gc_logo():
    response = client.logo_detection(image=image)
    logos = response.logo_annotations
    print('Logos:')

    for logo in logos:
        print(logo.description)

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

# gc_logo()


def gc_web():
    response = client.web_detection(image=image)
    annotations = response.web_detection

    if annotations.best_guess_labels:
        for label in annotations.best_guess_labels:
            print('\nBest guess label: {}'.format(label.label))

    if annotations.pages_with_matching_images:
        print('\n{} Pages with matching images found:'.format(
            len(annotations.pages_with_matching_images)))

        for page in annotations.pages_with_matching_images:
            print('\n\tPage url   : {}'.format(page.url))

            if page.full_matching_images:
                print('\t{} Full Matches found: '.format(
                        len(page.full_matching_images)))

                for image in page.full_matching_images:
                    print('\t\tImage url  : {}'.format(image.url))

            if page.partial_matching_images:
                print('\t{} Partial Matches found: '.format(
                        len(page.partial_matching_images)))

                for image in page.partial_matching_images:
                    print('\t\tImage url  : {}'.format(image.url))

    if annotations.web_entities:
        print('\n{} Web entities found: '.format(
            len(annotations.web_entities)))

        for entity in annotations.web_entities:
            print('\n\tScore      : {}'.format(entity.score))
            print(u'\tDescription: {}'.format(entity.description))

    if annotations.visually_similar_images:
        print('\n{} visually similar images found:\n'.format(
            len(annotations.visually_similar_images)))

        for image in annotations.visually_similar_images:
            print('\tImage url    : {}'.format(image.url))

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))