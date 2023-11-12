import sys
from PIL import Image
import io
import base64


def parse_image_from_data_uri(data_uri, output_filename):
    image_data = data_uri.split(",")[1]
    image_bytes = base64.b64decode(image_data)
    image = Image.open(io.BytesIO(image_bytes))
    image.show()
    image.save(output_filename)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py <image_data_uri> <output_filename>")
        sys.exit(1)

    parse_image_from_data_uri(sys.argv[1], sys.argv[2])
