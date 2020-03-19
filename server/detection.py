import cv2
import numpy as np

DNN_IMAGE_SIZE = (512, 512)


def predict_bounding_boxes(image, weights, config, classes):
    width = image.shape[1]
    height = image.shape[0]
    scale = 1.0 / 255.0  # = 0.00392

    # read pre-trained model and config file
    net = cv2.dnn.readNet(weights, config)

    # create input blob
    blob = cv2.dnn.blobFromImage(image, scale, DNN_IMAGE_SIZE, (0, 0, 0), False, crop=False)

    # set input blob for the network
    net.setInput(blob)

    # function to get the output layer names
    # in the architecture
    def get_output_layers(net):
        layer_names = net.getLayerNames()
        output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
        return output_layers

    # run inference through the network
    # and gather predictions from output layers
    outs = net.forward(get_output_layers(net))

    # initialization
    class_ids = []
    confidences = []
    boxes = []
    conf_threshold = 0.5
    nms_threshold = 0.1

    # for each detetion from each output layer
    # get the confidence, class id, bounding box params
    # and ignore weak detections (confidence < 0.5)
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if scores.sum() > 0.5:
                print(classes[class_id], sorted(scores.tolist(), reverse=True)[:3])
            if confidence > 0.5:
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = center_x - w / 2
                y = center_y - h / 2
                class_ids.append(class_id)
                confidences.append(float(confidence))
                boxes.append([x, y, w, h])

    # apply non-max suppression
    indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)

    # go through the detections remaining
    # after nms and draw bounding box
    results = []
    for idx in indices:
        i = idx[0]
        results.append({"box": boxes[i], "class_id": class_ids[i]})
    return results


def draw_bounding_boxes(image, weights, config, classes):
    results = predict_bounding_boxes(image, weights, config, classes)

    # function to draw bounding box on the detected object with class name
    def draw_bounding_box(img, class_id, x, y, x_plus_w, y_plus_h):
        label = str(classes[class_id])
        color = [0xCC, 0, 0]  # BRG
        cv2.rectangle(img, (x, y), (x_plus_w, y_plus_h), color, 2)
        cv2.putText(img, label, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    for result in results:
        box = result["box"]
        x = box[0]
        y = box[1]
        w = box[2]
        h = box[3]
        draw_bounding_box(
            image, result["class_id"], round(x), round(y), round(x + w), round(y + h)
        )
    return image
