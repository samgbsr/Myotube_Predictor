from flask import Flask, request, jsonify, send_file, after_this_request, make_response
from flask_cors import CORS
from ultralytics import YOLO
import numpy as np
import cv2
import io
import json
import torch
from shapely.geometry import Polygon
from torchvision.ops import nms

app = Flask(__name__)
CORS(app)

model1 = YOLO('Model/11n_1K.pt')
model2 = YOLO('Model/11n_2K.pt')

def obb_to_polygon(obb):
    """Convert OBB to a polygon using Shapely."""
    x_center, y_center, width, height, rotation = obb
    dx = width / 2
    dy = height / 2
    corners = [
        (-dx, -dy),
        (dx, -dy),
        (dx, dy),
        (-dx, dy)
    ]
    cos_theta = np.cos(rotation)
    sin_theta = np.sin(rotation)
    rotated_corners = [
        (
            x_center + x * cos_theta - y * sin_theta,
            y_center + x * sin_theta + y * cos_theta
        )
        for x, y in corners
    ]
    return Polygon(rotated_corners)

def rotated_iou(pred1, pred2):
    """Compute IoU for rotated bounding boxes."""
    poly1 = obb_to_polygon(pred1)
    poly2 = obb_to_polygon(pred2)
    intersection = poly1.intersection(poly2).area
    union = poly1.union(poly2).area
    if union == 0:
        return 0.0
    return intersection / union

def apply_nms(predictions, iou_threshold=0.01):
    """Apply standard NMS to predictions."""
    if not predictions:
        return []
    boxes = torch.tensor([pred['coords'][:4] for pred in predictions])
    confidences = torch.tensor([pred['confidence'] for pred in predictions])
    boxes_xyxy = torch.zeros_like(boxes)
    boxes_xyxy[:, 0] = boxes[:, 0] - boxes[:, 2] / 2
    boxes_xyxy[:, 1] = boxes[:, 1] - boxes[:, 3] / 2
    boxes_xyxy[:, 2] = boxes[:, 0] + boxes[:, 2] / 2
    boxes_xyxy[:, 3] = boxes[:, 1] + boxes[:, 3] / 2
    keep = nms(boxes_xyxy, confidences, iou_threshold)
    return [predictions[i] for i in keep]

def apply_nms_rotated(predictions, iou_threshold=0.5):
    """Apply rotated NMS to predictions."""
    if not predictions:
        return []
    predictions = sorted(predictions, key=lambda x: x['confidence'], reverse=True)
    keep = []
    while predictions:
        current = predictions.pop(0)
        keep.append(current)
        predictions = [
            pred for pred in predictions
            if rotated_iou(current['coords'], pred['coords']) <= iou_threshold
        ]
    return keep

def extract_predictions(results):
    """Extract predictions from YOLO results."""
    predictions = []
    if results and hasattr(results[0], 'obb') and results[0].obb is not None:
        obb_boxes = results[0].obb
        for i, coords in enumerate(obb_boxes.xywhr):
            x_center, y_center, width, height, rotation = coords.tolist()
            cls = int(obb_boxes.cls[i]) if obb_boxes.cls is not None else -1
            conf = float(obb_boxes.conf[i]) if obb_boxes.conf is not None else 0
            predictions.append({
                "coords": [x_center, y_center, width, height, rotation],
                "class": cls,
                "confidence": conf
            })
    return predictions

def process_image(image_path):
    """Process the image using YOLO models and apply NMS."""
    results1 = model1.predict(image_path, conf=0.15, verbose=False)
    results2 = model2.predict(image_path, conf=0.15, verbose=False)
    predictions1 = extract_predictions(results1)
    predictions2 = extract_predictions(results2)
    combined_predictions = predictions1 + predictions2
    filtered_predictions = apply_nms_rotated(apply_nms(combined_predictions))
    return filtered_predictions

def draw_predictions_with_rotation(image_path, predictions):
    """Draw predictions with rotation."""
    image = cv2.imread(image_path)
    colorText = (255, 0, 0)
    colorBox = (0, 0, 255)
    thickness = 2
    for pred in predictions:
        xywhr = pred['coords']
        x_center, y_center, width, height, angle = xywhr
        angle_rad = -angle
        cos_a = np.cos(angle_rad)
        sin_a = np.sin(angle_rad)
        dx = width / 2
        dy = height / 2
        corners = np.array([
            [-dx, -dy],
            [dx, -dy],
            [dx, dy],
            [-dx, dy]
        ])
        rotation_matrix = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
        rotated_corners = np.dot(corners, rotation_matrix) + [x_center, y_center]
        vertices = rotated_corners.astype(int)
        cv2.polylines(image, [vertices.reshape((-1, 1, 2))], isClosed=True, color=colorBox, thickness=thickness)
        label = f"Myotube {pred['confidence']*100:.1f}%"
        cv2.putText(image, label, (int(x_center), int(y_center - height / 2 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colorText, 2)
    _, buffer = cv2.imencode('.png', image)
    return buffer.tobytes()

@app.route('/process-image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400
    image = request.files['image']
    project_id = request.form.get('project_id')
    if not project_id:
        return jsonify({"error": "No project_id provided"}), 400
    image.save("uploaded_image.png")
    predictions = process_image("uploaded_image.png")
    processed_image = draw_predictions_with_rotation("uploaded_image.png", predictions)
    response = make_response(processed_image)
    response.headers['Content-Type'] = 'image/png'
    response.headers['predictions'] = json.dumps(predictions)
    return response

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
