import math
import os
import subprocess
import argparse
import ffmpeg

#os.environ["CUDA_DEVICbreE_ORDER"] = "PCI_BUS_ID"
#os.environ["CUDA_VISIBLE_DEVICES"] = '3'
import json
import torch
import torch.nn
import time
import cv2
import mediapipe as mp
import numpy as np
import pandas as pd

# Initialize mediapipe drawing class - to draw the landmarks points.
mp_drawing = mp.solutions.drawing_utils
mp_holistic = mp.solutions.holistic


from architecture.st_gcn import STGCN
from architecture.fc import FC
from architecture.network import Network

weight = "/Users/madhangikrishnan/Documents/GitHub/krishnanmclaren-capstone/asl-website/_training_from_aslcitizen_capstone002400_0.814685.pt"

#Given a sorted output from the model aka ranked list, returns
#rank of ground truth and list of other metrics
#The different indices correspond to [DCG, Top-1 Acc, Top-5 Acc, Top-10 Acc, Top-20 Acc, MRR]
def eval_metrics(sortedArgs, label):
    res, = np.where(sortedArgs == label)
    dcg = 1 / math.log2(res[0] + 1 + 1) #res values start from 0
    mrr = 1 / (res[0] + 1)
    if res < 1:
        return res[0], [dcg, 1, 1, 1, 1, mrr]
    elif res < 5:
        return res[0], [dcg, 0, 1, 1, 1, mrr]
    elif res < 10:
        return res[0], [dcg, 0, 0, 1, 1, mrr]
    elif res < 20:
        return res[0], [dcg, 0, 0, 0, 1, mrr]
    else:
        return res[0], [dcg, 0, 0, 0, 0, mrr]

def downsample(frames, max_frames):
    length = frames.shape[0]
    # Adjust FPS dynamically based on length of video
    increment = max_frames / length 
    if increment > 1.0:
        increment = 1.0  
    curr_increment = 0
    curr_frame = 0
    new_frames = []
    for f in frames:
        curr_increment += increment
        if curr_increment > curr_frame:
            curr_frame += 1
            new_frames.append(f)
    if len(new_frames) > max_frames:
        new_frames = new_frames[:max_frames]  
    return np.array(new_frames)

torch.manual_seed(0)
np.random.seed(0)
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
torch.set_default_dtype(torch.float64)

#Update files and paths as needed
video_base_path = '../data/poses/'
train_file = '../data_csv/aslcitizen_training_set.csv'
test_file = '../data_csv/aslcitzen_test_set.csv'
#Update names according to experiment number
tag = 'experiment1b'
dataset_name = "training_full"

device = torch.device("cpu")
'''
train_transforms = pose_transforms.Compose([pose_transforms.ShearTransform(0.1),
                                            pose_transforms.RotatationTransform(0.1)])
#load data
train_ds = Dataset(datadir=video_base_path, video_file=train_file, transforms=train_transforms, pose_map_file = "pose_mapping_train.csv")
test_ds = Dataset(datadir=video_base_path, video_file=test_file, gloss_dict=train_ds.gloss_dict, pose_map_file = "pose_mapping_test.csv")
n_classes = len(train_ds.gloss_dict)


test_loader = torch.utils.data.DataLoader(test_ds, batch_size=1, shuffle=True, num_workers=2, pin_memory=True)
'''

n_classes = 24


#load model
n_features = 256
graph_args = {'num_nodes': 27, 'center': 0,
              'inward_edges': [[2, 0], [1, 0], [0, 3], [0, 4], [3, 5],
                               [4, 6], [5, 7], [6, 17], [7, 8], [7, 9],
                               [9, 10], [7, 11], [11, 12], [7, 13], [13, 14],
                               [7, 15], [15, 16], [17, 18], [17, 19], [19, 20],
                               [17, 21], [21, 22], [17, 23], [23, 24], [17, 25], [25, 26]]}
stgcn = STGCN(in_channels=2, graph_args=graph_args, edge_importance_weighting=True)
fc = FC(n_features=n_features, num_class=n_classes, dropout_ratio=0.05)
pose_model = Network(encoder=stgcn, decoder=fc)

#print(os.getcwd())
pose_model.load_state_dict(torch.load((weight),map_location=torch.device('cpu')))
pose_model.to(device)

pose_model.train(False)  # Set model to evaluate mode


def extract_landmarks(video_path):
    f = video_path

    name = os.path.basename(video_path).split('.')[0]
    dst_path = os.path.splitext(video_path)[0]

    with mp_holistic.Holistic(
            static_image_mode=False, min_detection_confidence=0.5) as holistic:

        video = cv2.VideoCapture(f)
        total_frames = video.get(cv2.CAP_PROP_FRAME_COUNT)

        feature = np.zeros((int(total_frames), 543, 2))
        count = 0
        success = 1

        while success:
            success, image = video.read()
            if success:
                results = holistic.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

                for i in range(33):
                    if results.pose_landmarks:
                        feature[count][i][0] = results.pose_landmarks.landmark[i].x
                        feature[count][i][1] = results.pose_landmarks.landmark[i].y

                j = 33
                for i in range(21):
                    if results.right_hand_landmarks:
                        feature[count][i + j][0] = results.right_hand_landmarks.landmark[i].x
                        feature[count][i + j][1] = results.right_hand_landmarks.landmark[i].y

                j = 54
                for i in range(21):
                    if results.left_hand_landmarks:
                        feature[count][i + j][0] = results.left_hand_landmarks.landmark[i].x
                        feature[count][i + j][1] = results.left_hand_landmarks.landmark[i].y

                j = 75
                for i in range(468):
                    if results.face_landmarks:
                        feature[count][i + j][0] = results.face_landmarks.landmark[i].x
                        feature[count][i + j][1] = results.face_landmarks.landmark[i].y
                count += 1

        np.save(os.path.splitext(video_path)[0] + '.npy', feature)



# read time
def read_time_segments(file_path):
    segments = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(', ')
            start_time = float(parts[0].replace('Start: ', '').replace(' sec', ''))
            end_time = float(parts[1].replace('End: ', '').replace(' sec', ''))
            segments.append((start_time, end_time))
    return segments

def recognize_segments_in_video(pose_npy_path, fps):
    result_list = []
    df = pd.read_csv('/Users/madhangikrishnan/Documents/GitHub/krishnanmclaren-capstone/asl-website/ASL_gloss_24.csv')
    index_to_gloss = dict(zip(df["Index"], df["Gloss"]))

    # .npy  (T, V, C) == (num of frames, num of landmarks, XY)
    pose_data = np.load(pose_npy_path)
    length = pose_data.shape[0]

    if length > 128:
        pose_data = downsample(pose_data, 128)  # exceed 128, downsample 
    if length < 128:
        pose_data = np.pad(pose_data, ((0, 128 - length), (0, 0), (0, 0)))  # pad empty tensors


    # keypoints structure
    posedata = pose_data[:, 0:33, :]  # 33 poses
    lhdata = pose_data[:, 54:, :]  # left hand
    rhdata = pose_data[:, 33:54, :]  # right hand



    data = np.concatenate([posedata, lhdata, rhdata], axis=1)

    # get key points
    keypoints = [0, 2, 5, 11, 12, 13, 14, 33, 37, 38, 41, 42, 45, 46,
                49, 50, 53, 54, 58, 59, 62, 63, 66, 67, 70, 71, 74]
    data = data[:, keypoints, :]


    data = np.transpose(data, (2, 0, 1))  # (T, V, C) → (C, T, V)  xy, frames, num of landmarks
    #segmented_pose_data = segmented_pose_data[:, :, keypoints_idx]  # (C, T, V) → (C, T, 27)


    # change to tensor
    #inputs = torch.from_numpy(data).double()
    inputs = torch.as_tensor(np.array(data).astype('float'))
    inputs = inputs.unsqueeze(0)  # (C, T, V) → (1, C, T, V)

    # inputs.shape == (N, C, T, V)  # (batch, channels, frames, keypoints)
    predictions = pose_model(inputs)

    y_pred_tag = torch.softmax(predictions, dim=1)
    pred_args = torch.argsort(y_pred_tag, dim=1, descending=True)

    # bring top 20 results
    top_20_preds = pred_args[0][:20].tolist()
    top_20_confidences = y_pred_tag[0][pred_args[0][:20]].tolist()

    # Gloss mapping
    mapped_labels = [index_to_gloss[idx] for idx in top_20_preds]
    gloss_pred = [[word, score] for word, score in zip(mapped_labels, top_20_confidences)]
    #print("top 20 results: ", top_20_preds, ",", mapped_labels)
    result_list.append( gloss_pred) # original

    # insert logic for 0.5 cutoff in determining correctness

    return result_list


def convert_to_mp4(video_path):
    """
    Convert WebM file to MP4 using FFmpeg.
    """
    output_mp4 = os.path.splitext(video_path)[0] + ".mp4"

    # WebM 파일이면 변환 수행
    if video_path.lower().endswith(".webm"):
        print(f"Converting {video_path} to {output_mp4}...")
        command = [
            "ffmpeg", "-i", video_path, "-c:v", "libx264", "-preset", "fast",
            "-crf", "23", "-c:a", "aac", "-b:a", "128k", output_mp4, "-y"
        ]
        subprocess.run(command, check=True)
        print(f"Conversion complete: {output_mp4}")
        return output_mp4

    return video_path  # return if it is mp4

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--video', default=None, required=False, type=str, help='path to video file')

    return parser.parse_args()

# 실행 부분
if __name__ == "__main__":
    args = get_args()
    video_path = args.video

    #video_path = "./asl-website/recorded-videos/recorded-video.webm"
    # video_path = "C:\\Users\\calyp\\OneDrive\\Documents\\GitHub\\krishnanmclaren-capstone\\asl-website\\recorded-videos\recorded-video.webm"
    #video_path = "/Users/madhangikrishnan/Documents/GitHub/krishnanmclaren-capstone/asl-website/recorded-videos/recorded-video.webm"
    video_path = convert_to_mp4(video_path)
    print("Start ASL recognition")

    vidcap = cv2.VideoCapture(video_path)
    #fps = vidcap.get(cv2.CAP_PROP_FPS)
    probe = ffmpeg.probe(video_path)
    fps = eval(probe['streams'][0]['r_frame_rate'])

    extract_landmarks(video_path)

    # landmarks npy file path
    pose_npy_path = os.path.splitext(video_path)[0] + '.npy'


    # sign recognition for each segments
    print("start recognizing")
    recognition_results = recognize_segments_in_video(pose_npy_path, fps)

    # JSON results
    output_json_path = os.path.join(video_path.split(".")[0] + ".json")
    with open(output_json_path, 'w', encoding='utf-8') as json_file:
        json.dump(recognition_results, json_file, ensure_ascii=False, indent=4)

    print(f"Results saved to {output_json_path}")
    print(json.dumps(recognition_results, ensure_ascii=False))
