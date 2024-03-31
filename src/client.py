import requests
import io
import time

from models.plate_reader import PlateReader

class ImageProviderClient:
    """Get binary of image from remote host."""
    def __init__(self, base_url: str = 'http://178.154.220.122:7777/images'):
        self.base_url = base_url

    def get_image(self, img_id: int) -> tuple[io.BytesIO | None, int | None]:
        retry_limit = 5
        while retry_limit > 0:
            try:
                response = requests.get(f"{self.base_url}/{img_id}", timeout=5)
                if response.status_code == 200:
                    # success
                    return io.BytesIO(response.content), None
                elif response.status_code == 404:
                    # image is not found in upstream service, 404 immediately
                    return None, 404
                elif 400 <= response.status_code < 500:
                    # some other reason to fail
                    return None, response.status_code
            except requests.Timeout:
                # if we timeouted, then retry
                retry_limit -= 1
                time.sleep(0.1)
                return None, 408
            except requests.RequestException:
                # some unknown error, it is the problem in upstream service
                return None, 500
        # than it is timeout after all attempts
        return None, 408

class PlateReaderClient:
    """Given binary of image, return result of PlateReader."""
    def __init__(self, plate_reader_model_path: str = "/app/model_weights/plate_reader_model.pth"):
        self.plate_reader = PlateReader.load_from_file(plate_reader_model_path)

    def read_plate_number(self, img_stream: io.BytesIO) -> str:
        return self.plate_reader.read_text(img_stream)
