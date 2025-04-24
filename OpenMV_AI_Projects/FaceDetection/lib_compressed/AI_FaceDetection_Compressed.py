"""
Combined Face Detection Library

This single file incorporates:
  - Utility functions and classes to calculate SSD anchors (refactored without SsdAnchorsCalculatorOptions)
  - The BlazeFaceDetector class that handles model loading, inference, and postprocessing (from BlazeFaceDetector.py)
  - The AI_FaceDetection class that wraps the BlazeFaceDetector for application-level integration (from AI_FaceDetection.py)

Dependencies: gc, math, time, ml
"""

import gc
import math
import time
import ml

# ============================
# Utility Classes and Methods
# ============================

class Anchor:
    def __init__(self, x_center, y_center, h, w):
        self.x_center = x_center
        self.y_center = y_center
        self.h = h
        self.w = w

def gen_anchors(options):
    anchors = []
    # Verify the options.
    if options.strides_size != options.num_layers:
        print("strides_size and num_layers must be equal.")
        return []
    layer_id = 0
    while layer_id < options.strides_size:
        anchor_height = []
        anchor_width = []
        aspect_ratios_list = []
        scales = []
        # For same strides, merge anchors.
        last_same_stride_layer = layer_id
        while (last_same_stride_layer < options.strides_size and
               options.strides[last_same_stride_layer] == options.strides[layer_id]):
            scale = options.min_scale + (options.max_scale - options.min_scale) * float(last_same_stride_layer) / (options.strides_size - 1.0)
            if (last_same_stride_layer == 0 and options.reduce_boxes_in_lowest_layer):
                aspect_ratios_list.append(1.0)
                aspect_ratios_list.append(2.0)
                aspect_ratios_list.append(0.5)
                scales.append(0.1)
                scales.append(scale)
                scales.append(scale)
            else:
                for aspect_ratio_id in range(options.aspect_ratios_size):
                    aspect_ratios_list.append(options.aspect_ratios[aspect_ratio_id])
                    scales.append(scale)
                if options.interpolated_scale_aspect_ratio > 0.0:
                    scale_next = 1.0 if last_same_stride_layer == options.strides_size - 1 else options.min_scale + (options.max_scale - options.min_scale) * float(last_same_stride_layer + 1) / (options.strides_size - 1.0)
                    scales.append(math.sqrt(scale * scale_next))
                    aspect_ratios_list.append(options.interpolated_scale_aspect_ratio)
            last_same_stride_layer += 1
        for i in range(len(aspect_ratios_list)):
            ratio_sqrts = math.sqrt(aspect_ratios_list[i])
            anchor_height.append(scales[i] / ratio_sqrts)
            anchor_width.append(scales[i] * ratio_sqrts)
        if options.feature_map_height_size > 0:
            feature_map_height = options.feature_map_height[layer_id]
            feature_map_width = options.feature_map_width[layer_id]
        else:
            stride = options.strides[layer_id]
            feature_map_height = math.ceil(float(options.input_size_height) / stride)
            feature_map_width = math.ceil(float(options.input_size_width) / stride)
        for y in range(feature_map_height):
            for x in range(feature_map_width):
                for anchor_id in range(len(anchor_height)):
                    # Support anchor_offset by multiplying with cell index.
                    x_center = (x + options.anchor_offset_x) / feature_map_width
                    y_center = (y + options.anchor_offset_y) / feature_map_height
                    if options.fixed_anchor_size:
                        w = 1.0
                        h = 1.0
                    else:
                        w = anchor_width[anchor_id]
                        h = anchor_height[anchor_id]
                    new_anchor = Anchor(x_center, y_center, h, w)
                    anchors.append(new_anchor)
        layer_id = last_same_stride_layer
    return anchors

# ============================
# BlazeFace Detector Class
# ============================

KEY_POINT_SIZE = 6      # Number of facial keypoints per detection.
MAX_FACE_NUM = 8        # Maximum number of faces to keep after NMS.

class BlazeFaceDetector:
    def __init__(self, model_path,
                 score_threshold=0.7, iou_threshold=0.3):
        self.score_threshold = score_threshold  # Detection probability threshold.
        self.iou_threshold = iou_threshold      # IoU threshold for non-max suppression.
        self.last_time = time.ticks_ms()
        self.frame_counter = 0

        # Define the model input dimensions.
        self.input_width = 128
        self.input_height = 128

        # Load the TFLite model using the ml module.
        self.model = ml.Model(model_path)

        # Generate anchors for the 896 detections.
        self.anchors = self.generateAnchors()

    def generateAnchors(self):
        # Instead of using SsdAnchorsCalculatorOptions, create a temporary options object manually.
        class Options:
            pass
        options = Options()
        options.input_size_width = 128
        options.input_size_height = 128
        options.min_scale = 0.1484375
        options.max_scale = 0.75
        options.num_layers = 4
        options.feature_map_width = []  # Let the function compute feature map sizes.
        options.feature_map_height = []
        options.strides = [8, 16, 16, 16]
        options.aspect_ratios = [1.0]
        options.anchor_offset_x = 0.5
        options.anchor_offset_y = 0.5
        options.reduce_boxes_in_lowest_layer = False
        options.interpolated_scale_aspect_ratio = 1.0
        options.fixed_anchor_size = False
        options.strides_size = len(options.strides)
        options.aspect_ratios_size = len(options.aspect_ratios)
        options.feature_map_width_size = len(options.feature_map_width)
        options.feature_map_height_size = len(options.feature_map_height)
        return gen_anchors(options)

    def prepare_input(self, img):
        # Create a Normalization object that maps input pixel values into the range [-1, 1].
        norm = ml.preprocessing.Normalization(scale=(-1, 1))
        arr = norm(img)
        # The resulting array should have shape (128, 128, 3) with values between -1 and 1.
        # Reshape to add the batch dimension to match (1, 128, 128, 3)
        return arr

    def decode_detections(self, boxes, scores):
        detections = []
        num_detections = scores.shape[0]  # Should be 896.
        for i in range(num_detections):
            # Each score is of shape (1,); apply sigmoid to convert to probability.
            raw_score = scores[i][0]
            score = 1.0 / (1.0 + math.exp(-raw_score))
            if score < self.score_threshold:
                continue

            # Extract the raw bounding box predictions.
            sx = boxes[i][0]
            sy = boxes[i][1]
            w  = boxes[i][2]
            h  = boxes[i][3]
            anchor = self.anchors[i]
            # Decode center coordinates.
            cx = (sx + anchor.x_center * self.input_width) / self.input_width
            cy = (sy + anchor.y_center * self.input_height) / self.input_height
            # Normalize width and height.
            w_norm = w / self.input_width
            h_norm = h / self.input_height

            # Convert from center coordinates to top-left corner.
            x1 = cx - w_norm * 0.5
            y1 = cy - h_norm * 0.5

            # Decode facial keypoints.
            keypoints = []
            for j in range(KEY_POINT_SIZE):
                lx = boxes[i][4 + 2*j]
                ly = boxes[i][4 + 2*j + 1]
                kp_x = (lx + anchor.x_center * self.input_width) / self.input_width
                kp_y = (ly + anchor.y_center * self.input_height) / self.input_height
                keypoints.append((kp_x, kp_y))

            detections.append((x1, y1, w_norm, h_norm, score, keypoints))
        return detections

    def iou(self, det1, det2):
        x1, y1, w1, h1 = det1[0], det1[1], det1[2], det1[3]
        x2, y2, w2, h2 = det2[0], det2[1], det2[2], det2[3]
        # Determine the (x, y)-coordinates of the intersection rectangle.
        inter_x1 = max(x1, x2)
        inter_y1 = max(y1, y2)
        inter_x2 = min(x1 + w1, x2 + w2)
        inter_y2 = min(y1 + h1, y2 + h2)
        if inter_x2 <= inter_x1 or inter_y2 <= inter_y1:
            return 0.0
        inter_area = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
        area1 = w1 * h1
        area2 = w2 * h2
        union_area = area1 + area2 - inter_area
        return inter_area / union_area

    def non_max_suppression(self, detections):
        # Sort detections by score (highest first).
        detections = sorted(detections, key=lambda d: d[4], reverse=True)
        final_detections = []
        while detections:
            best = detections.pop(0)
            final_detections.append(best)
            detections = [d for d in detections if self.iou(best, d) < self.iou_threshold]
            if len(final_detections) >= MAX_FACE_NUM:
                break
        return final_detections

    def detect_faces(self, img):
        # Since the sensor is capturing 128x128 directly, the original image dimensions are 128x128.
        orig_w = img.width()
        orig_h = img.height()

        # Prepare the image for inference.
        inp = self.prepare_input(img)
        # Run inference. predict() requires a list of inputs.
        outputs = self.model.predict([inp])
        # According to our model, outputs[0] is the scores tensor (shape: (1,896,1))
        # and outputs[1] is the boxes tensor (shape: (1,896,16)).
        scores = outputs[0][0]  # Remove the batch dimension → shape (896, 1)
        boxes = outputs[1][0]   # Remove the batch dimension → shape (896, 16)

        # Decode raw outputs into detection candidates.
        detections = self.decode_detections(boxes, scores)
        # Apply non-max suppression to remove overlapping detections.
        final_detections = self.non_max_suppression(detections)
        return final_detections, orig_w, orig_h

# ============================
# High-Level Face Detection Class
# ============================

class AI_FaceDetection:
    def __init__(self):
        self.detector = BlazeFaceDetector(model_path="face_detection_front",
                                          score_threshold=0.7,
                                          iou_threshold=0.3)

    # Function expects an RGB 128x128 image but will resize if necessary.
    def detect_faces(self, img):
        self.orig_width = img.width()
        self.orig_height = img.height()

        if img.width() != 128 or img.height() != 128:
            # Compute scaling factors so that the resized image is 128x128.
            scale_x = 128 / img.width()
            scale_y = 128 / img.height()

            # Create a new RGB565 image scaled to 128x128 and load it directly into the frame buffer.
            img = img.to_rgb565(x_scale=scale_x, y_scale=scale_y, copy_to_fb=True)

        # Run the detection pipeline on the resized image.
        detections = self.detector.detect_faces(img)
        gc.collect()

        final_detections = []

        for det in detections[0]:
            x, y, w, h, score, keypoints = det

            x = int(x * self.orig_width)
            y = int(y * self.orig_height)
            w = int(w * self.orig_width)
            h = int(h * self.orig_height)

            left_eye_x, left_eye_y = keypoints[0]
            right_eye_x, right_eye_y = keypoints[1]
            nose_x, nose_y = keypoints[2]
            mouth_x, mouth_y = keypoints[3]
            left_ear_x, left_ear_y = keypoints[4]
            right_ear_x, right_ear_y = keypoints[5]

            left_eye_x = int(left_eye_x * self.orig_width)
            left_eye_y = int(left_eye_y * self.orig_height)
            right_eye_x = int(right_eye_x * self.orig_width)
            right_eye_y = int(right_eye_y * self.orig_height)
            nose_x = int(nose_x * self.orig_width)
            nose_y = int(nose_y * self.orig_height)
            mouth_x = int(mouth_x * self.orig_width)
            mouth_y = int(mouth_y * self.orig_height)
            left_ear_x = int(left_ear_x * self.orig_width)
            left_ear_y = int(left_ear_y * self.orig_height)
            right_ear_x = int(right_ear_x * self.orig_width)
            right_ear_y = int(right_ear_y * self.orig_height)
            final_detections.append({"bounding_box": (x, y, w, h),"confidence": score,"keypoints": keypoints,"left_eye": (left_eye_x, left_eye_y),"right_eye": (right_eye_x, right_eye_y),"nose": (nose_x, nose_y),"mouth": (mouth_x, mouth_y),"left_ear": (left_ear_x, left_ear_y),"right_ear": (right_ear_x, right_ear_y)})
        return final_detections

    def angle_relative_to_camera(self, detection, hfov=70.8, vfov=55.6):
        cx = self.orig_width / 2.0
        cy = self.orig_height / 2.0
        fx = cx / math.tan(math.radians(hfov / 2))
        fy = cy / math.tan(math.radians(vfov / 2))
        dx = detection["bounding_box"][0] + detection["bounding_box"][2] / 2 - cx
        dy = detection["bounding_box"][1] + detection["bounding_box"][3] / 2 - cy
        angle_x = math.degrees(math.atan(dx / fx))
        angle_y = math.degrees(math.atan(dy / fy))
        return angle_x, angle_y
