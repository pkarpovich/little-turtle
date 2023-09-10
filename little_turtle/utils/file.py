import os


def get_image_path(image_path: str) -> str:
    image_name = os.path.basename(image_path)
    curr_dir = os.getcwd()
    parent_dir = os.path.dirname(curr_dir)
    images_dir = os.path.join(parent_dir, "images")

    if not os.path.exists(images_dir):
        os.makedirs(images_dir)

    return os.path.join(images_dir, image_name)


def read_file_from_disk(file_name: str) -> bytes:
    with open(file_name, 'rb') as f:
        binary_data = f.read()

    return binary_data
