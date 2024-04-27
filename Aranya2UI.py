from flask import Flask, render_template, request
import os
from werkzeug.utils import secure_filename
import cv2
import numpy as np
from ultralytics import YOLO
from PIL import Image
import os
import io

## These modules required for Species Identification
import requests
import json
from pprint import pprint


app = Flask(__name__)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'wmv'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    print('Hello, Flask!') 
    return render_template('index.html')

@app.route('/demo')
def demo():
    print('DEMO, Flask!') 
    # file_name="static/YOLOpredicted/bikes.mp4"
    # names = ["Python", "PHP", "JS", "Go"]
    # print(names)
    return render_template('product.html')
    # return render_template('product.html', file_name=file_name, type='video')
    # return render_template('product.html')


#############
## This function will IDENTIFY Species
#############

@app.route('/upload2', methods=['GET', 'POST'])
def upload_species():
    API_KEY = "2b10DrTCcbO16qJZXxmdqVeax"  # Set you API_KEY here
    PROJECT = "all" # try "weurope" or "canada"
    api_endpoint = f"https://my-api.plantnet.org/v2/identify/{PROJECT}?api-key={API_KEY}"

    # if request.method == 'POST':
    print('0. START UPLOADING ...') 
    if 'file' not in request.files:
        print('1. FILE COULD NOT BE FOUND ???') 
        return 'No file part in the request', 400

    if 'file' in request.files:
        f = request.files['file']
        print('1. FILE TO BE UPLOADED...', f) 
        if f and allowed_file(f.filename):
            print('2. ALLOWED file type & UPLOADING ...') 
            basepath = os.path.dirname(__file__)
            filepath = os.path.join(basepath,'static/PlantIdentified',f.filename)
            print("upload folder is ", filepath)
            f.save(filepath)
            file_extension = f.filename.rsplit('.', 1)[1].lower()    
            # path_to_save_file = os.path.join(basepath,'static/YOLOpredicted',f.filename)
            web_image_path = "static/PlantIdentified/"+f.filename

            image_path_1 = filepath ## "Teak.JPG" ##"NITW_1.JPG"
            image_data_1 = open(image_path_1, 'rb')

            # image_path_2 = "Teak.JPG"
            # image_data_2 = open(image_path_2, 'rb')

            data = {
                'organs': ['leaf']
                # 'organs': ['flower', 'leaf']
            }

            files = [
                ('images', (image_path_1, image_data_1))
                # ,('images', (image_path_2, image_data_2))
            ]

            req = requests.Request('POST', url=api_endpoint, files=files, data=data)
            prepared = req.prepare()

            s = requests.Session()
            response = s.send(prepared)
            json_result = json.loads(response.text)

            print("API response :", response.status_code)
            print("JSON :", json_result)
            # print("............... ----FIRST RESULT----- ................")
            # print(json_result["results"][0])
            print("............... ----SCORE----- ................")
            treeConfidence = json_result["results"][0]["score"]
            print(treeConfidence)
            print("............... ----SPECIES----- ................")
            # print(json_result["results"][0]["species"])
            
            treeIdentified = json_result["results"][0]["species"]["commonNames"][0]
            print("Common Name:", treeIdentified) #: ['Teak', 'Bankok teak', 'Indian-oak'], 'scientificName':

            treeSciName = json_result["results"][0]["species"]["scientificName"]
            print("scientific Name:", treeSciName)

            return render_template('product.html', Tree_file_name=web_image_path, TreeIdentified=treeIdentified, TreeConfidence=treeConfidence, TreeSciName=treeSciName, type='id_image')




# ............... ----FIRST RESULT----- ................
# {'score': 0.98841, 'species': {'scientificNameWithoutAuthor': 'Tectona grandis', 'scientificNameAuthorship': 'L.f.', 'genus': {'scientificNameWithoutAuthor': 'Tectona', 'scientificNameAuthorship': '', 'scientificName': 'Tectona'}, 'family': {'scientificNameWithoutAuthor': 'Lamiaceae', 'scientificNameAuthorship': '', 'scientificName': 'Lamiaceae'}, 'commonNames': ['Teak', 'Bankok teak', 'Indian-oak'], 'scientificName': 'Tectona grandis L.f.'}, 'gbif': {'id': '2925649'}, 'powo': {'id': '864923-1'}, 'iucn': {'id': '62019830', 'category': 'EN'}}
# ............... ----SCORE----- ................
# 0.98841
# ............... ----SPECIES----- ................
# {'scientificNameWithoutAuthor': 'Tectona grandis', 'scientificNameAuthorship': 'L.f.', 'genus': {'scientificNameWithoutAuthor': 'Tectona', 'scientificNameAuthorship': '', 'scientificName': 'Tectona'}, 'family': {'scientificNameWithoutAuthor': 'Lamiaceae', 'scientificNameAuthorship': '', 'scientificName': 'Lamiaceae'}, 'commonNames': ['Teak', 'Bankok teak', 'Indian-oak'], 'scientificName': 'Tectona grandis L.f.'}


#############
## This function will detect trees & Calculate Bio-Mass
#############

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    # if request.method == 'POST':
    print('0. START UPLOADING ...') 
    if 'file' not in request.files:
        print('1. FILE COULD NOT BE FOUND ???') 
        return 'No file part in the request', 400

    if 'file' in request.files:
        f = request.files['file']
        print('1. FILE TO BE UPLOADED...', f) 
        if f and allowed_file(f.filename):
            print('2. ALLOWED file type & UPLOADING ...') 
            basepath = os.path.dirname(__file__)
            filepath = os.path.join(basepath,'uploads',f.filename)
            print("upload folder is ", filepath)
            f.save(filepath)
            file_extension = f.filename.rsplit('.', 1)[1].lower()    
            path_to_save_file = "static/img/YOLO_result.jpg" # Initializing to this image

            ##--## JPG file YOLO prediction ##--##
            if file_extension == 'jpg':
                print("WORKING on JPG  :::::: ", f.filename)
                model = YOLO('best118tree50epochs.pt') # Perform the detection using YOLO
                results = model.predict(filepath)
                print("YOLO DONE :::::: ", f.filename)
                # print(results)

                ## For segmentation
                # model = YOLO('yolov8n-seg-pt') # Load a pretrained YOLOv8n segmentation model
                # model.predict(filepath) # predict on an image

                path_to_save_file = os.path.join(basepath,'static/YOLOpredicted',f.filename)
                print("IMAGE path_to_save_file folder is ", path_to_save_file)

                if results:
                    path_to_save_file = "static/YOLOpredicted/"+'YOLO_'+f.filename
                    res_plotted = results[0].plot()
                    print("results_plotted", res_plotted)
                    # cv2.imshow("result", res_plotted)
                    status = cv2.imwrite(path_to_save_file, res_plotted)
                    # f.save(path_to_save_file)

                    # Here you should save the file
                    # status = cv2.imwrite(path_to_save_file, filepath)
                    # filename = secure_filename(f.filename)
                    print("YOLO Image written to file-system : ",status, "::  File name", path_to_save_file)

                    ## Calculate Bio-Mass  # Process results list
                    for result in results:
                        boxes = result.boxes  # Boxes object for bounding box outputs
                        print("boxes:", boxes)
                        TotalBoundingBoxesArea = 0;
                        TotalObjectsFound = 0;

                        for box in boxes:
                            print("each box xyxy:", box.xyxy) # (xmin, ymin, xmax, ymax)
                            width = box.xyxy[0][2]-box.xyxy[0][0] ##xmax - xmin
                            print("each box width:", width)
                            height = box.xyxy[0][3]-box.xyxy[0][1] ##ymax - ymin
                            print("each box height:", height)
                            area = width*height
                            print("each box AREA:", area)
                            TotalBoundingBoxesArea = TotalBoundingBoxesArea + area
                            print("TotalBoundingBoxesArea:", TotalBoundingBoxesArea)

                            if(box.cls == 0):
                                TotalObjectsFound = TotalObjectsFound + 1
                                print("TREE FOUND:", box.cls)
                            if(box.cls == 1):
                                TotalObjectsFound = TotalObjectsFound + 1
                                print("NEEM TREE FOUND:", box.cls)
                            if(box.cls == 2):
                                TotalObjectsFound = TotalObjectsFound + 1
                                print("TEAK TREE FOUND:", box.cls)
                            print("TotalObjectsFound:", TotalObjectsFound)

                        #     conf = boxes.conf
                            print("each box confidence:", box.conf)

                        masks = result.masks  # Masks object for segmentation masks outputs
                        print("masks:", masks)
                        keypoints = result.keypoints  # Keypoints object for pose outputs
                        print("keypoints:", keypoints)
                        probs = result.probs  # Probs object for classification outputs
                        print("probs:", probs)
                        # result.show()  # display to screen
                        # result.save(filename='result.jpg')  # save to disk
                        # Boxes.object for bbox.outputs
                        #     probs = result-probs # Class probabilities for classification outputs
                        #     cls = boxes.cls
                        #     xyxy = boxes.xyxy
                        #     xywh = boxes.xywh # box with xywh format, (N, 4)
                        #     conf = boxes.conf
                        #     print("boxes : ",boxes)
                        #     print("probs : ",probs)
                        #     print("cls - cls,(N, 1) : ",cls)
                        #     print("conf - confidence score, (N, 1): ", conf)
                        #     print(box with xysy format, (N, 4) : xysy)
                        #     print(box with xywh format, (N, 4) : xywh)
                   
                # results = model.predict(image, save=True)
                # model.predict(image, save=True, imgsz=320, conf=0.5)

                return render_template('product.html', file_name=path_to_save_file, treeCount=TotalObjectsFound, bioMass=TotalBoundingBoxesArea, type='bio_image')

            elif file_extension == 'mp4':
                video_path = filepath # replace with your video path
                print("WORKING on VIDEO file  :::::: ", video_path)
                cap = cv2.VideoCapture(video_path)

                # get video dimensions
                frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                # Define the codec and create VideoWriter object
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')

                # initialize the YOLOv8 model here
                # model = YOLO('yolov8m.pt') ## YOLO default model
                model = YOLO('best118tree50epochs.pt') ## Our TREE custom model
                print("about to YOLO :::::: ", f.filename)

                path_to_save_file = os.path.join('static/YOLOpredicted',f.filename)
                print("VIDEO path_to_save_file folder is ", path_to_save_file)

                out = cv2.VideoWriter(path_to_save_file, fourcc, 30.0, (frame_width, frame_height))

                skip_frames = 2  # Process every 3rd frame
                frame_count = 0

                while cap.isOpened():
                    success, frame = cap.read()
                    if not success:
                        break

                    # Skip frames to speed up processing
                    frame_count += 1
                    if frame_count % skip_frames != 0:
                        continue

                    # do YOLOvs detection on the frame here
                    results = model(frame)
                    # results = model(frame, save=True)                    
                    res_plotted = results[0].plot()
                    # cv2.imshow("result", res_plotted)                    
                    # write the frame to the output video : output.mp4
                    out.write(res_plotted)

                    if cv2.waitKey(1) & 0xFF == ord('q'): 
                        break

                    # NOT NEEDED MOST of the TIMES: 

                    # for result in results:
                    #     boxes = result.boxes  # Boxes object for bbox outputs
                    #     masks = result.masks  # Masks object for segmentation masks outputs
                    #     probs = result.probs  # Class probabilities for classification outputs

                    # --- OR -----

                    # for result in results:
                    #     #class_id, confidence, bbox = result
                    #     boxes = result.boxes
                    #     Boxes.object for bbox.outputs
                    #     probs = result-probs # Class probabilities for classification outputs
                    #     cls = boxes.cls
                    #     xyxy = boxes.xyxy
                    #     xywh = boxes.xywh # box with xywh format, (N, 4)
                    #     conf = boxes.conf
                    #     print("boxes : ",boxes)
                    #     print("probs : ",probs)
                    #     print("cls - cls,(N, 1) : ",cls)
                    #     print("conf - confidence score, (N, 1): ", conf)
                    #     print(box with xysy format, (N, 4) : xysy)
                    #     print(box with xywh format, (N, 4) : xywh)

                print(" :::::: DONE with Video Frame :::::: ")
                return render_template('product.html', file_name=path_to_save_file, type='video')

            # folder_path = 'runs/detect'
            # subfolders = [f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, f))]    
            # ## Each model detection creates a NEW folder with LATEST iteration number
            # latest_subfolder = max(subfolders, key=lambda x: os.path.getctime(os.path.join(folder_path, x)))    
            # image_path = folder_path+'/'+latest_subfolder+'/'+f.filename 
            # print('IMAGE File Path :', image_path)
            # image_path = "static/img/YOLO_result.jpg"
            # return render_template('product.html', file_name=image_path)

        else:
            print('File upload failed - WRONG File Type')
            return render_template('product.html', file_name=f.filename)



if __name__ == '__main__':
    app.run(debug=True)
