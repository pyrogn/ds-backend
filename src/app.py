from flask import Flask, jsonify, request
from client import ImageProviderClient, PlateReaderClient
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')

app = Flask(__name__)
image_provider_client = ImageProviderClient('http://178.154.220.122:7777/images')
plate_reader_client = PlateReaderClient("/app/model_weights/plate_reader_model.pth")

def handle_image_error(error_code: int) -> tuple[dict, int]:
    error_messages = {
        404: "Image not found",
        408: "Timeout when downloading image",
        500: "Failed to download image due to server error"
    }
    return {"error": error_messages.get(error_code, "Unknown error")}, error_code

@app.route('/read_plate_single', methods=['GET'])
def read_plate_single():
    """Handler for single image id."""
    img_id = request.args.get('img_id')
    if not img_id:
        return jsonify({"error": "img_id parameter is required"}), 400
    
    img_stream, error_code = image_provider_client.get_image(int(img_id))
    if error_code:
        return handle_image_error(error_code)
    
    plate_number = plate_reader_client.read_plate_number(img_stream)
    return {"plate_number": plate_number}

@app.route('/read_plate_multiple', methods=['POST'])
def read_plate_multiple():
    """Handler for multiple images id."""
    img_ids = request.json.get('img_ids')
    if not img_ids:
        return jsonify({"error": "img_ids parameter is required"}), 400

    results = []
    for img_id in img_ids:
        img_stream, error_code = image_provider_client.get_image(img_id)
        if error_code: # if error, add error message
            result = {"img_id": img_id}
            result.update(handle_image_error(error_code)[0])
            results.append(result)
            continue
        plate_number = plate_reader_client.read_plate_number(img_stream)
        results.append({"img_id": img_id, "plate_number": plate_number})

    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
