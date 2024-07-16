import numpy as np
import cv2
from ultralytics import SAM, YOLO, FastSAM
import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse

# Load the models
sam_b = SAM("sam_b.pt")
mobile_sam = SAM("mobile_sam.pt")
fast_sam_s = FastSAM("FastSAM-s.pt")
yolov8x_seg = YOLO('yolov8x-seg.pt')
yolov8n_seg = YOLO("yolov8n-seg.pt")

colors = [
    (255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255),
    (255, 0, 255), (192, 192, 192), (128, 128, 128), (128, 0, 0), (128, 128, 0),
    (0, 128, 0), (128, 0, 128), (0, 128, 128), (0, 0, 128), (72, 61, 139),
    (47, 79, 79), (47, 79, 47), (0, 206, 209), (148, 0, 211), (255, 20, 147)
]

def process_image(image_path, model):
    # Check if the results folder exists
    if not os.path.exists('results'):
        os.makedirs('results')

    # Load the image
    image = cv2.imread(image_path)
    image_orig = image.copy()
    h_or, w_or = image.shape[:2]
    image = cv2.resize(image, (640, 640))
    results = model(image)[0]

    classes_names = results.names
    classes = results.boxes.cls.cpu().numpy()
    masks = results.masks

    # Check if masks were detected
    if masks is not None:
        masks = masks.data.cpu().numpy()

        # Overlay masks on the image
        legend_classes = {}
        for i, mask in enumerate(masks):
            class_name = classes_names[classes[i]]
            color = colors[int(classes[i]) % len(colors)]

            # Convert the probability mask to a binary mask
            mask = mask.astype(np.uint8) * 255

            # Resize the mask before creating the colored mask
            mask_resized = cv2.resize(mask, (w_or, h_or))

            # Create the colored mask
            color_mask = np.zeros((h_or, w_or, 3), dtype=np.uint8)
            color_mask[mask_resized > 0] = color

            # Save the mask of each class to a separate file
            mask_filename = os.path.join('results', f"{model.__class__.__name__}_{class_name}_{i}.png")
            cv2.imwrite(mask_filename, color_mask)

            # Overlay the mask on the original image
            image_orig = cv2.addWeighted(image_orig, 1.0, color_mask, 0.5, 0)

            # Add the class to the legend dictionary
            if class_name not in legend_classes:
                legend_classes[class_name] = color

        # Create the legend image
        legend_height = 30
        legend_width = 200
        legend_image = np.ones((h_or, legend_width, 3), dtype=np.uint8) * 255
        for i, (class_name, color) in enumerate(legend_classes.items()):
            cv2.rectangle(legend_image, (10, i * legend_height + 10), (30, (i + 1) * legend_height - 10), color, -1)
            cv2.putText(legend_image, class_name, (40, int((i + 0.5) * legend_height)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)

        # Concatenate the original image and the legend image horizontally
        result_image = np.concatenate((image_orig, legend_image), axis=1)

        # Save the modified image with a unique name
        new_image_path = os.path.join('results', f"{model.__class__.__name__}_Pasted_image_{i}.png")
        cv2.imwrite(new_image_path, result_image)
        return new_image_path
    else:
        return None


app = FastAPI()

@app.post("/segment_image/sam_b/")
async def segment_image_sam_b(file: UploadFile = File(...)):
    # Save the uploaded image to a temporary file
    image_path = f"/tmp/{file.filename}"
    with open(image_path, "wb") as buffer:
        buffer.write(await file.read())

    segmented_image_path = process_image(image_path, sam_b)
    if segmented_image_path is not None:
        return {"model_name": "SAM (Base) - sam_b", "image_path": segmented_image_path}
    else:
        return {"error": "No objects detected"}

@app.post("/segment_image/mobile_sam/")
async def segment_image_mobile_sam(file: UploadFile = File(...)):
    # Save the uploaded image to a temporary file
    image_path = f"/tmp/{file.filename}"
    with open(image_path, "wb") as buffer:
        buffer.write(await file.read())

    segmented_image_path = process_image(image_path, mobile_sam)
    if segmented_image_path is not None:
        return {"model_name": "Mobile SAM - mobile_sam", "image_path": segmented_image_path}
    else:
        return {"error": "No objects detected"}

@app.post("/segment_image/fast_sam_s/")
async def segment_image_fast_sam_s(file: UploadFile = File(...)):
    # Save the uploaded image to a temporary file
    image_path = f"/tmp/{file.filename}"
    with open(image_path, "wb") as buffer:
        buffer.write(await file.read())

    segmented_image_path = process_image(image_path, fast_sam_s)
    if segmented_image_path is not None:
        return {"model_name": "FastSAM (Small) - fast_sam_s", "image_path": segmented_image_path}
    else:
        return {"error": "No objects detected"}

@app.post("/segment_image/yolov8x_seg/")
async def segment_image_yolov8x_seg(file: UploadFile = File(...)):
    # Save the uploaded image to a temporary file
    image_path = f"/tmp/{file.filename}"
    with open(image_path, "wb") as buffer:
        buffer.write(await file.read())

    segmented_image_path = process_image(image_path, yolov8x_seg)
    if segmented_image_path is not None:
        return {"model_name": "YOLOv8 (Extra Large) - yolov8x_seg", "image_path": segmented_image_path}
    else:
        return {"error": "No objects detected"}

@app.post("/segment_image/yolov8n_seg/")
async def segment_image_yolov8n_seg(file: UploadFile = File(...)):
    # Save the uploaded image to a temporary file
    image_path = f"/tmp/{file.filename}"
    with open(image_path, "wb") as buffer:
        buffer.write(await file.read())

    segmented_image_path = process_image(image_path, yolov8n_seg)
    if segmented_image_path is not None:
        return {"model_name": "YOLOv8 (Nano) - yolov8n_seg", "image_path": segmented_image_path}
    else:
        return {"error": "No objects detected"}

@app.post("/segment_image/all_models/")
async def segment_image(file: UploadFile = File(...)):
    # Save the uploaded image to a temporary file
    image_path = f"/tmp/{file.filename}"
    with open(image_path, "wb") as buffer:
        buffer.write(await file.read())

    models = {
        "SAM (Base) - sam_b": sam_b,
        "Mobile SAM - mobile_sam": mobile_sam,
        "FastSAM (Small) - fast_sam_s": fast_sam_s,
        "YOLOv8 (Extra Large) - yolov8x_seg": yolov8x_seg,
        "YOLOv8 (Nano) - yolov8n_seg": yolov8n_seg
    }

    segmented_images = []
    for model_name, model in models.items():
        try:
            segmented_image_path = process_image(image_path, model)
            if segmented_image_path is not None:
                segmented_images.append({
                    "model_name": model_name,
                    "image_path": segmented_image_path
                })
            else:
                print(f"No objects detected by {model_name}")
        except Exception as e:
            print(f"Error occurred while processing image with {model_name}: {str(e)}")

    return {"segmented_images": segmented_images}

'''
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
'''

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)