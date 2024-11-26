from shapely.geometry import Polygon
from torchvision.ops import nms
from ultralytics import YOLO
import numpy as np
import torch
import json
import cv2

# Cargar los modelos YOLOv8 con sus respectivos pesos
model1 = YOLO('11n_1K.pt')
model2 = YOLO('11n_2K.pt')

# Ruta de la imagen de entrada
image_path = 'Img1.png'
#image_path = 'Img2.png'
#image_path = 'Img3.png'
#image_path = 'Img4.png'
#image_path = 'Img5.png'

# Realizar predicciones con ambos modelos
print("Realizando predicciones con el primer modelo...")
results1 = model1.predict(image_path, conf=0.15, verbose=False)
print("Resultados del primer modelo:", results1)

print("Realizando predicciones con el segundo modelo...")
results2 = model2.predict(image_path, conf=0.15, verbose=False)
print("Resultados del segundo modelo:", results2)

# Función para extraer predicciones de OBB
def extract_predictions(results):
    print("Extrayendo predicciones...")
    if results and len(results) > 0 and hasattr(results[0], 'obb') and results[0].obb is not None:
        obb_boxes = results[0].obb
        print(f"Detecciones encontradas: {len(obb_boxes.xywhr)}")
        predictions = []
        for i, coords in enumerate(obb_boxes.xywhr):  # Coordenadas (x_center, y_center, w, h, rotation)
            x_center, y_center, width, height, rotation = coords.tolist()
            cls = int(obb_boxes.cls[i]) if obb_boxes.cls is not None else -1  # Clase predicha
            conf = float(obb_boxes.conf[i]) if obb_boxes.conf is not None else 0  # Confianza
            predictions.append({
                "coords": [x_center, y_center, width, height, rotation],  # Convertir a lista
                "class": cls,
                "confidence": conf
            })
        return predictions
    else:
        print("No se encontraron obb o son inválidos.")
        return []

def obb_to_polygon(obb):
    x_center, y_center, width, height, rotation = obb  # Asegúrate de que 'rotation' esté en radianes
    
    # Calcular los vértices no rotados
    dx = width / 2
    dy = height / 2
    corners = [
        (-dx, -dy),
        (dx, -dy),
        (dx, dy),
        (-dx, dy)
    ]
    
    # Rotar y trasladar los vértices
    cos_theta = np.cos(rotation)
    sin_theta = np.sin(rotation)
    rotated_corners = [
        (
            x_center + x * cos_theta - y * sin_theta,
            y_center + x * sin_theta + y * cos_theta
        )
        for x, y in corners
    ]
    
    # Crear y devolver un polígono Shapely
    return Polygon(rotated_corners)

def rotated_iou(pred1, pred2):
    """
    Calcula el IoU entre dos bounding boxes rotadas usando polígonos.
    :param pred1: Coordenadas del primer OBB.
    :param pred2: Coordenadas del segundo OBB.
    :return: IoU (float) entre los dos OBB.
    """
    poly1 = obb_to_polygon(pred1)
    poly2 = obb_to_polygon(pred2)

    # Intersección y unión
    intersection = poly1.intersection(poly2).area
    union = poly1.union(poly2).area

    if union == 0:
        return 0.0
    return intersection / union

# Función para aplicar NMS y eliminar solapamientos
def apply_nms(predictions, iou_threshold=0.01):
    if len(predictions) == 0:
        return []
    
    # Extraer coordenadas, confianza y clases
    boxes = torch.tensor([pred['coords'][:4] for pred in predictions])  # Solo [x_center, y_center, w, h]
    confidences = torch.tensor([pred['confidence'] for pred in predictions])
    classes = torch.tensor([pred['class'] for pred in predictions])
    
    # Convertir las coordenadas de [x_center, y_center, w, h] a [x1, y1, x2, y2] para NMS
    boxes_xyxy = torch.zeros_like(boxes)
    boxes_xyxy[:, 0] = boxes[:, 0] - boxes[:, 2] / 2  # x1
    boxes_xyxy[:, 1] = boxes[:, 1] - boxes[:, 3] / 2  # y1
    boxes_xyxy[:, 2] = boxes[:, 0] + boxes[:, 2] / 2  # x2
    boxes_xyxy[:, 3] = boxes[:, 1] + boxes[:, 3] / 2  # y2
    
    # Aplicar NMS
    keep = nms(boxes_xyxy, confidences, iou_threshold)
    
    # Filtrar las predicciones que fueron retenidas
    filtered_predictions = [predictions[i] for i in keep]
    return filtered_predictions

def apply_nms_rotated(predictions, iou_threshold=0.5):
    """
    Aplica Non-Maximum Suppression considerando la rotación de las cajas.
    :param predictions: Lista de predicciones, cada una con 'coords', 'confidence' y 'class'.
    :param iou_threshold: Umbral IoU para filtrar solapamientos.
    :return: Lista de predicciones filtradas.
    """
    if len(predictions) == 0:
        return []
    
    # Ordenar predicciones por confianza descendente
    predictions = sorted(predictions, key=lambda x: x['confidence'], reverse=True)
    keep = []

    while predictions:
        # Seleccionar la predicción con mayor confianza
        current = predictions.pop(0)
        keep.append(current)

        # Filtrar predicciones con alto solapamiento IoU
        predictions = [
            pred for pred in predictions
            if rotated_iou(current['coords'], pred['coords']) <= iou_threshold
        ]

    return keep

# Función para extraer y filtrar las predicciones
def extract_predictions(results):
    print("Extrayendo predicciones...")
    if results and len(results) > 0 and hasattr(results[0], 'obb') and results[0].obb is not None:
        obb_boxes = results[0].obb
        print(f"Detecciones encontradas: {len(obb_boxes.xywhr)}")
        predictions = []
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
    else:
        print("No se encontraron obb o son inválidos.")
        return []

def draw_predictions_with_rotation(image_path, predictions):
    # Cargar la imagen original
    image = cv2.imread(image_path)

    # Colores para las cajas de las predicciones
    colorText = (255, 0, 0)  # Verde en formato BGR
    colorBox = (0, 0, 255)  # Verde en formato BGR
    thickness = 2  # Grosor de las líneas de la caja

    # Dibujar las cajas de las predicciones
    for pred in predictions:
        # Extraer las coordenadas xywhr
        xywhr = pred['coords']  # Formato [x_center, y_center, width, height, rotation]
        x_center, y_center, width, height, angle = xywhr

        # Calcular las coordenadas de los vértices rotados
        angle_rad = -angle  # Convertir el ángulo a radianes
        cos_a = np.cos(angle_rad)
        sin_a = np.sin(angle_rad)

        # Coordenadas relativas a la rotación
        dx = width / 2
        dy = height / 2
        corners = np.array([
            [-dx, -dy],
            [dx, -dy],
            [dx, dy],
            [-dx, dy]
        ])

        # Aplicar rotación y trasladar al centro
        rotation_matrix = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
        rotated_corners = np.dot(corners, rotation_matrix) + [x_center, y_center]
        vertices = rotated_corners.astype(int)  # Convertir a enteros para OpenCV

        # Dibujar el polígono
        cv2.polylines(image, [vertices.reshape((-1, 1, 2))], isClosed=True, color=colorBox, thickness=thickness)

        # Añadir el texto de la predicción (Clase y confianza)
        label = f"Myotube {pred['confidence']*100:.1f}%"
        cv2.putText(image, label, (int(x_center), int(y_center - height / 2 - 10)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colorText, 2, cv2.LINE_AA)

    # Mostrar la imagen con las predicciones
    cv2.imshow("Predictions with Rotation", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Guardar predicciones en un archivo JSON
def save_predictions_to_json(predictions, output_path="filtered_predictions.json"):
    try:
        # Reestructurar las predicciones para que las coordenadas sean más descriptivas
        formatted_predictions = []
        for pred in predictions:
            formatted_predictions.append({
                "coords": {
                    "x_center": pred['coords'][0],
                    "y_center": pred['coords'][1],
                    "width": pred['coords'][2],
                    "height": pred['coords'][3],
                    "rotation": pred['coords'][4]*57.3  # En grados
                },
                "class": pred['class'],
                "confidence": pred['confidence']*100
            })
        
        # Guardar en un archivo JSON
        with open(output_path, 'w') as json_file:
            json.dump(formatted_predictions, json_file, indent=4)
        print(f"Predicciones guardadas correctamente en {output_path}")
    except Exception as e:
        print(f"Error al guardar las predicciones en JSON: {e}")



# Extraer y combinar predicciones de ambos modelos
predictions1 = extract_predictions(results1)
predictions2 = extract_predictions(results2)

# Aplicar NMS para eliminar solapamientos
combined_predictions = predictions2 + predictions1
filtered_predictions = apply_nms(apply_nms_rotated(combined_predictions))

#filtered_predictions = apply_nms(filtered_predictions)
print(f"Total de predicciones combinadas antes de NMS: {len(predictions1) + len(predictions2)}")
print(f"Total de predicciones después de NMS: {len(filtered_predictions)}")


# Guardar predicciones filtradas en un archivo JSON
save_predictions_to_json(filtered_predictions, "filtered_predictions.json")

# Mostrar resultados
if filtered_predictions:
    for i, pred in enumerate(filtered_predictions):
        print(f"Predicción {i+1}: Clase {pred['class']}, Confianza {pred['confidence']:.2f}, Coords {pred['coords']}")
else:
    print("No se detectaron objetos en ninguna de las predicciones.")

# Usar la función para dibujar predicciones sobre la imagen
draw_predictions_with_rotation(image_path, filtered_predictions)
