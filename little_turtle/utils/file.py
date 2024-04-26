import os


def get_image_path(base_image_dir: str, image_path: str) -> str:
    image_name = os.path.basename(image_path)

    if not os.path.exists(base_image_dir):
        os.makedirs(base_image_dir)

    return os.path.join(base_image_dir, image_name)


def read_file_from_disk(file_name: str) -> bytes:
    with open(file_name, "rb") as f:
        binary_data = f.read()

    return binary_data
