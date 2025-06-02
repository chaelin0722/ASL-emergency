import copy
import statistics

import torch
import cv2

import numpy as np
import gradio as gr
import pandas as pd

from spoter_mod.skeleton_extractor import obtain_pose_data
from spoter_mod.normalization.body_normalization import normalize_single_dict as normalize_single_body_dict, BODY_IDENTIFIERS
from spoter_mod.normalization.hand_normalization import normalize_single_dict as normalize_single_hand_dict, HAND_IDENTIFIERS


df = pd.read_csv("new-gloss-specifier.csv", encoding="utf-8")
df = df.fillna("—")

model = torch.load("spoter-checkpoint.pth", map_location=torch.device('cpu'))
model.train(False)

HAND_IDENTIFIERS = [id + "_Left" for id in HAND_IDENTIFIERS] + [id + "_Right" for id in HAND_IDENTIFIERS]
GLOSS = ['DOG', 'DOG', 'DOG', 'DOG', 'GIRAFFE', 'CAT', 'CAT', 'CAT', 'BEE', 'BEE', 'COW', 'TURTLE', 'HORSE', 'ELEPHANT',
         'RABBIT', 'RABBIT', 'BEAR', 'PIG', 'CROCODILE', 'DUCK', 'DUCK', 'SQUIRREL', 'DEER', 'ROOSTER', 'LOBSTER',
         'LOBSTER', 'LOBSTER', 'TIGER', 'ZEBRA', 'LION', 'SNAKE', 'SHARK', 'SHARK', 'WHALE', 'SHRIMP', 'FISH', 'MONKEY',
         'HIPPO', 'HIPPO', 'DONKEY', 'FROG', 'EGG', 'PIZZA', 'PIZZA', 'BACON', 'SAUSAGE', 'TOAST', 'ONION', 'MILK',
         'MILK', 'CHEESE', 'SPAGHETTI', 'SALT', 'HAMBURGER', 'PEPPER', 'FRENCH FRIES', 'COFFEE', 'BREAD', 'TEA',
         'SALAD', 'SANDWICH', 'SANDWICH', 'SANDWICH', 'SANDWICH', 'LETTUCE', 'LETTUCE', 'GRAPES', 'GRAPES', 'TOMATO',
         'STRAWBERRY', 'STRAWBERRY', 'STRAWBERRY', 'STRAWBERRY', 'MEAT', 'MEAT', 'ORANGE', 'POTATO', 'BANANA', 'BANANA',
         'BANANA', 'BANANA', 'BEANS', 'APPLE', 'MELON', 'CAKE', 'CHERRY', 'CHERRY', 'PIE', 'PINEAPPLE', 'PINEAPPLE',
         'PINEAPPLE', 'PINEAPPLE', 'PINEAPPLE', 'COOKIE', 'AMERICA', 'AUSTRALIA', 'SWITZERLAND', 'ISRAEL', 'CANADA',
         'JAPAN', 'CHINA', 'EGYPT', 'FRANCE', 'GERMANY', 'GREECE', 'PUERTORICO', 'GUATEMALA', 'PAKISTAN', 'URUGUAY',
         'PHILIPPINES', 'AUSTRIA', 'NIGERIA', 'MOROCCO', 'TRINIDAD', 'JAMAICA', 'COLOMBIA', 'LEBANON', 'BULGARIA',
         'BANGLADESH', 'IRAQ', 'NICARAGUA', 'CHILE', 'ENGLAND', 'NETHERLANDS', 'SYRIA', 'UNITED STATES', 'SCOTLAND',
         'TIBET', 'PALESTINE', 'PANAMA', 'PORTUGAL', 'VIETNAM', 'TURKEY', 'ARGENTINA', 'NEW ZEALAND.MP4', 'UKRAINE',
         'DOMINICAN REPUBLIC', 'JORDAN', 'NORWAY', 'IRELAND', 'NEW ZEALAND', 'PERU', 'ECUADOR', 'FINLAND', 'BOTSWANA',
         'ICELAND', 'BELIZE', 'ROMANIA', 'HONDURAS', 'KENYA', 'SPAIN', 'TAIWAN', 'INDONESIA', 'POLAND', 'SOUTH AFRICA',
         'IRAN', 'MEXICO', 'HONG KONG', 'NIAMBIA', 'KOREA', 'SAUDI ARABIA', 'SWEDEN', 'CUBA', 'VENEZUELA', 'DENMARK',
         'INDIA', 'MALAYSIA', 'ITALY', 'BOLIVIA', 'PARAGUAY', 'BELGIUM', 'COSTARICA', 'THAILAND', 'EL SALVADOR',
         'RUSSIA', 'SRI LANKA', 'CZECH REPUBLIC']

potential_warning_message = """<div style="background-color: rgba(255, 165, 0, 0.6); padding: 15px; margin-bottom: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); border-left: 5px solid rgba(255, 140, 0, 0.7);">
          <p style="margin: 0 0 10px 0; text-align: left; font-family: GraphikBold;">
            Warning: Low video quality may affect the accuracy of sign language predictions.
          </p>
          <div style="color: white; padding: 10px; border-radius: 4px; font-family: Graphik;">
            <ul style="margin: 10px 0 0 20px; padding: 0; list-style-type: disc; font-family: Graphik;">
              <li>Ensure good lighting and minimal clutter in the background;</li>
              <li>Be in the center of the frame, with all your gestures visible;</li>
              <li>Allow maximum webcam quality.</li>
            </ul>
          </div>
        </div>"""

device = torch.device("cpu")
if torch.cuda.is_available():
    device = torch.device("cuda")


def tensor_to_dictionary(landmarks_tensor: torch.Tensor) -> dict:

    data_array = landmarks_tensor.numpy()
    output = {}

    for landmark_index, identifier in enumerate(BODY_IDENTIFIERS + HAND_IDENTIFIERS):
        output[identifier] = data_array[:, landmark_index]

    return output


def dictionary_to_tensor(landmarks_dict: dict) -> torch.Tensor:

    output = np.empty(shape=(len(landmarks_dict["leftEar"]), len(BODY_IDENTIFIERS + HAND_IDENTIFIERS), 2))

    for landmark_index, identifier in enumerate(BODY_IDENTIFIERS + HAND_IDENTIFIERS):
        output[:, landmark_index, 0] = [frame[0] for frame in landmarks_dict[identifier]]
        output[:, landmark_index, 1] = [frame[1] for frame in landmarks_dict[identifier]]

    return torch.from_numpy(output)


def greet(video, progress=gr.Progress()):

    if not video:
        return """<div style="padding: 5%;"><div style="background-color: rgba(255, 0, 0, 0.4); padding: 15px; margin-bottom: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); border-left: 5px solid rgba(200, 0, 0, 0.7);">
                  <p style="margin: 0 0 10px 0; text-align: left; font-family: GraphikBold;">
                    No video provided — please try again
                  </p>
                  <div style="color: white; padding: 10px; border-radius: 4px; font-family: Graphik;">
                    <ul style="margin: 10px 0 0 20px; padding: 0; list-style-type: disc; font-family: Graphik;">
                      <li>Record a video directly in the browser or upload a video from your computer.</li>
                      <li>You can select the desired data source in the lower part of the left panel.</li>
                      <li>To record a video or choose a file, click on the left panel.</li>
                    </ul>
                  </div>
                </div></div>
                """

    video_cap = cv2.VideoCapture(video)

    width = video_cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = video_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps = video_cap.get(cv2.CAP_PROP_FPS)

    trigger_warning = False

    if width < 600 or height < 400:
        trigger_warning = True

    if fps < 20:
        trigger_warning = True

    ###

    # Initialize variables
    frames_analyzed = -1
    faces_centered = []
    num_faces_detected = []

    # Load the pre-trained Haar Cascade for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Step 3: Face detection and center check
    while True:
        ret, frame = video_cap.read()
        frames_analyzed += 1
        if not ret:
            break  # Break the loop if there are no frames left to read

        # For efficiency, you may want to analyze fewer frames
        # Example: Analyze every 30th frame
        if frames_analyzed % 30 != 0:
            continue

        # Convert to grayscale for the Haar cascade detector
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        # Check if exactly one face is detected and its position
        num_faces_detected.append(len(faces))
        if len(faces) == 1:
            x, y, w, h = faces[0]
            # Calculate the center of the face
            face_center = (x + w // 2, y + h // 2)
            video_center = (width // 2, height // 2)

            # Step 4: Check if the face is in the center
            if abs(face_center[0] - video_center[0]) < width * 0.5 and abs(face_center[1] - video_center[1]) < height * 0.5:
                faces_centered.append(1)
            else:
                faces_centered.append(0)

    print("faces_centered", faces_centered)
    print("num_faces_detected", num_faces_detected)

    video_cap.release()  # Release the video file

    if faces_centered:
        if statistics.mean(faces_centered) < 0.5:
            trigger_warning = True

    if len([1 for x in num_faces_detected if x == 0]) > len(num_faces_detected) / 2 or len([1 for x in num_faces_detected if x >= 2]) > len(num_faces_detected) / 2:
        trigger_warning = True

    ###

    data = obtain_pose_data(video, progress=progress)

    depth_map = np.empty(shape=(len(data.data_hub["nose_X"]), len(BODY_IDENTIFIERS + HAND_IDENTIFIERS), 2))

    for index, identifier in enumerate(BODY_IDENTIFIERS + HAND_IDENTIFIERS):
        depth_map[:, index, 0] = data.data_hub[identifier + "_X"]
        depth_map[:, index, 1] = data.data_hub[identifier + "_Y"]

    depth_map = torch.from_numpy(np.copy(depth_map))

    depth_map = tensor_to_dictionary(depth_map)

    keys = copy.copy(list(depth_map.keys()))
    for key in keys:
        data = depth_map[key]
        del depth_map[key]
        depth_map[key.replace("_Left", "_0").replace("_Right", "_1")] = data

    depth_map = normalize_single_body_dict(depth_map)
    depth_map = normalize_single_hand_dict(depth_map)

    keys = copy.copy(list(depth_map.keys()))
    for key in keys:
        data = depth_map[key]
        del depth_map[key]
        depth_map[key.replace("_0", "_Left").replace("_1", "_Right")] = data

    depth_map = dictionary_to_tensor(depth_map)

    depth_map = depth_map - 0.5

    inputs = depth_map.squeeze(0).to(device)
    try:
        outputs = model(inputs).expand(1, -1, -1)
    except:
        return "<div style='padding: 5%;'>" + potential_warning_message + "</div>"

    results = torch.nn.functional.softmax(outputs, dim=2).detach().numpy()[0, 0]

    results = {GLOSS[i]: float(results[i]) for i in range(len(GLOSS))}

    NUM_TO_INCLUDE = 10
    class_indices = []
    class_confs = []

    for pred_class in sorted(results, key=results.get, reverse=True)[:NUM_TO_INCLUDE]:
        class_indices.append(pred_class.upper())
        # class_indices.append(df[df["Sign"] == pred_class.upper()].to_dict(orient='records')[0]["WLASL Identifier"])
        if int(results[pred_class] * 100):
            class_confs.append(int(results[pred_class] * 100))
        else:
            class_confs.append(1)

    full_analysis_url = "https://assetsdemo.matsworld.io/new/index.html?origin=https://signlanguagerecognition.com?__theme=light&pred=" + ",".join(
         [str(i) for i in class_indices]) + "&conf=" + ",".join([str(i) for i in class_confs])

    # full_analysis_url = "C:\Users\calyp\OneDrive\Documents\CAPSTONE\chi2025-sign-language-dictionary-main\chi2025-sign-language-dictionary-main\asl website\landing_page.html" 

# + ",".join(
# [str(i) for i in class_indices]) + "&conf=" + ",".join([str(i) for i in class_confs])

    top_pred_class = sorted(results, key=results.get, reverse=True)[0]
    top_pred_conf = class_confs[0]
    top_pred_item = df[df["Sign"] == str(class_indices[0])].to_dict(orient='records')[0]

    tag_0 = """<span style='opacity: 0.7;'>Movement:</span> """
    tag_1 = """, <span style='opacity: 0.7;'># Hands:</span> """
    tag_2 = """, <span style='opacity: 0.7;'>Location:</span> """
    tag_3 = """, <span style='opacity: 0.7;'>Handshape:</span> """
    top_pred_description = tag_0 + str(top_pred_item["Movement"]).capitalize() + tag_1 + str(top_pred_item[
       "Number of Hands"]).capitalize() + tag_2 + str(top_pred_item["Location"]).capitalize() + tag_3 + str(top_pred_item["Handshape"]).capitalize()
    top_pred_description = "no description"

    top_pred_description = str("Movement: " + top_pred_item["Movement"]).capitalize() + ", Num. of hands: " + str(int(top_pred_item["Number of Hands"])).capitalize() + ", Location: " + str(top_pred_item["Location"]).capitalize() + ", Handshape: " + str(top_pred_item["Handshape"]).capitalize()
    runner_up_alternatives = sorted(results, key=results.get, reverse=True)[1:7]

    gif_paths = ["https://data.matsworld.io/spoter/new/gifs/" + alt + ".gif" for alt in runner_up_alternatives]

    ###
    ind = 2

    runner_up_html_1 = []
    for gif_path, alt_name in zip(gif_paths[:2], runner_up_alternatives[:2]):
        annotations_data = df[df["Sign"] == str(alt_name.upper())].to_dict(orient='records')[0]
        annotations_desc = str("Movement: " + annotations_data["Movement"]).capitalize() + ", Num. of hands: " + str(int(annotations_data["Number of Hands"])).capitalize() + ", Location: " + str(annotations_data["Location"]).capitalize() + ", Handshape: " + str(annotations_data["Handshape"]).capitalize()

        alt_name = "#" + str(ind) + " " + alt_name.capitalize()

        runner_up_html_1.append(f"""
        <div class="runner-up" style="flex: 1; padding: 5px; box-sizing: border-box;">
            <div style="width: 100%; height: 0; padding-bottom: 56.25%; position: relative;">
                <img src="{gif_path}" alt="{alt_name}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover;">
            </div>
            <span style="margin-top: 5px; text-align: left;"><p style="font-family: GraphikBold; text-alignment: left; font-size: 1.2em; padding-bottom: 0;">{alt_name}</p><p style="font-family: Graphik; text-alignment: left; margin-top: -5px;">{annotations_desc}</p></span>
        </div>
        """)

        ind += 1

    runner_up_html_1 = "\n".join(runner_up_html_1)

    runner_up_html_2 = []
    for gif_path, alt_name in zip(gif_paths[2:4], runner_up_alternatives[2:4]):
        annotations_data = df[df["Sign"] == str(alt_name.upper())].to_dict(orient='records')[0]
        annotations_desc = str("Movement: " + annotations_data["Movement"]).capitalize() + ", Num. of hands: " + str(int(annotations_data["Number of Hands"])).capitalize() + ", Location: " + str(annotations_data["Location"]).capitalize() + ", Handshape: " + str(annotations_data["Handshape"]).capitalize()

        alt_name = "#" + str(ind) + " " + alt_name.capitalize()
        runner_up_html_2.append(f"""
            <div class="runner-up" style="flex: 1; padding: 5px; box-sizing: border-box;">
                <div style="width: 100%; height: 0; padding-bottom: 56.25%; position: relative;">
                    <img src="{gif_path}" alt="{alt_name}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover;">
                </div>
                <span style="margin-top: 5px; text-align: left;"><p style="font-family: GraphikBold; text-alignment: left; font-size: 1.2em; padding-bottom: 0;">{alt_name}</p><p style="font-family: Graphik; text-alignment: left; margin-top: -5px;">{annotations_desc}</p></span>
            </div>
            """)

        ind += 1

    runner_up_html_2 = "\n".join(runner_up_html_2)

    runner_up_html_3 = []
    for gif_path, alt_name in zip(gif_paths[4:], runner_up_alternatives[4:]):
        annotations_data = df[df["Sign"] == str(alt_name.upper())].to_dict(orient='records')[0]
        annotations_desc = str("Movement: " + annotations_data["Movement"]).capitalize() + ", Num. of hands: " + str(int(annotations_data["Number of Hands"])).capitalize() + ", Location: " + str(annotations_data["Location"]).capitalize() + ", Handshape: " + str(annotations_data["Handshape"]).capitalize()

        alt_name = "#" + str(ind) + " " + alt_name.capitalize()
        runner_up_html_3.append(f"""
                <div class="runner-up" style="flex: 1; padding: 5px; box-sizing: border-box;">
                    <div style="width: 100%; height: 0; padding-bottom: 56.25%; position: relative;">
                        <img src="{gif_path}" alt="{alt_name}" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover;">
                    </div>
                    <span style="margin-top: 5px; text-align: left;"><p style="font-family: GraphikBold; text-alignment: left; font-size: 1.2em; padding-bottom: 0;">{alt_name}</p><p style="font-family: Graphik; text-alignment: left; margin-top: -5px;">{annotations_desc}</p></span>
                </div>
                """)

        ind += 1

    runner_up_html_3 = "\n".join(runner_up_html_3)
    ###

    gif_path = "https://data.matsworld.io/spoter/new/gifs/" + str(class_indices[0]) + ".gif"

    score_confidence_interpretation = ""
    if top_pred_conf < 33:
        score_confidence_interpretation = "<span style='color: #F4442E; opacity: 0.7; font-weight: 500;'>Unlikely</span>"
    elif top_pred_conf < 66:
        score_confidence_interpretation = "<span style='color: #FDBB2F; opacity: 0.7; font-weight: 500;'>Possibly</span>"
    else:
        score_confidence_interpretation = "<span style='color: #3EC300; opacity: 0.7; font-weight: 500;'>Probably</span>"

    warning_message = ""
    if trigger_warning:
        warning_message = potential_warning_message

    return ["""
    <div style="padding: 5%;">
    
        $WARNING_MESSAGE$

        <p style="opacity: 0.5; margin-bottom: -20px;">Top prediction</p>
        <br>
        <div style="display:inline-block; width: 100%;">
            <h1 style="display:inline-block; font-size: 2em; font-family: GraphikBold;"><b>$TOP_PRED_CLASS$</b></h1>
            <h1 style="float: right; display:inline-block; font-size: 1.7em; font-family: Graphik;">$TOP_PRED_CONF$</h1>
        </div>
        <p>$DESCRIPTION$</p>
        
        <br>
        
        <img src="$GIF_PATH$" style="width: 100%">
        
        <br>
        
        <hr style="margin-top: 5px; margin-bottom: 5px;">
        
        <p style="opacity: 0.5;">Runner-up predictions</p>
        
        <div style='display: flex; justify-content: space-between; align-items: center;'> $ALTERNATIVES_TABLE_1$ </div>
        <div style='display: flex; justify-content: space-between; align-items: center;'> $ALTERNATIVES_TABLE_2$ </div>
        <div style='display: flex; justify-content: space-between; align-items: center;'> $ALTERNATIVES_TABLE_3$ </div>
        
        
        <p style="opacity: 0.5;">See full analysis for more details.</p>
        <br>
        
        <div style="display:inline-block;">
            <button class="lg primary svelte-cmf5ev" onclick="window.location.replace('$URL$')" >More results</button>
            <!--<button class="gr-button gr-button-lg gr-button-secondary"  style="margin-left: 8px !important;" onclick="window.location.href='mailto:matyas.bohacek@matsworld.io'">Report a problem</button>-->
        </div>
        
    </div>
    
    
    """.replace("$WARNING_MESSAGE$", warning_message).replace("$URL$", full_analysis_url).replace("$ALTERNATIVES$", ", ".join(runner_up_alternatives)).replace("$TOP_PRED_CLASS$", "#1 " + top_pred_class.capitalize()).replace("$TOP_PRED_CONF$", str(score_confidence_interpretation)).replace("$GIF_PATH$", gif_path).replace("$DESCRIPTION$", top_pred_description).replace("$ALTERNATIVES_TABLE_1$", runner_up_html_1).replace("$ALTERNATIVES_TABLE_2$", runner_up_html_2).replace("$ALTERNATIVES_TABLE_3$", runner_up_html_3)]

js_script = """
window.location.replace(window.location.href + '?__theme=light');

window.addEventListener('load', function () {
    console.log("happy happy happy");
  gradioURL = window.location.href;
  if (!gradioURL.endsWith('?__theme=light')) {
    window.location.replace(gradioURL + '?__theme=light');
  }
});
"""

head = """
<title>ASL Dictionary</title>

<!--<script>
gradioURL = window.location.href;
  if (!gradioURL.endsWith('?__theme=light')) {
    window.location.replace(gradioURL + '?__theme=light');
  }
</script>-->
"""

label = [gr.HTML(label="Results")]
with open('styles.css') as f: css_c = f.read()

with gr.Blocks(title="ASL Dictionary", head=head, css=css_c) as demo:
    x = gr.Interface(fn=greet, inputs=[gr.Video(sources=["webcam", "upload"], label="This video is not stored.")], outputs=label, js=js_script,
                        head=head,
                        title="", thumbnail="./static/favicon.png",
                        description="""
   <img src="https://data.matsworld.io/signlanguagerecognition/spoter-logo.png" style="width: 120px; margin-left: -5px;">
   <h1 style="color: #F7B832; font-family: GraphikBold;">ASL Dictionary</h1>

   <b>

   <details>
       <summary style="font-size: 1em !important; font-family: GraphikBold;" class="unselectable">
       <b>Welcome to our website!</b>
       </summary>
       <br>
   <ol style="font-family: Graphik;  font-weight: 400;">
       <li> Upload or record a video.
           <ul>
               <li> Ensure that there is only a single person in the shot.
               <li> The signer should be front-facing and have a calm background.
           </ul>
       <li> Click "Submit".
       <li> Results will appear in "Results" panel on the right shortly.
       <li> A confidence label is shown next to each prediction, corresponding to the percentual likelihood of the respective sign: 66-100% to Probably, 33-66% to Possibly, and 0-33% to Unlikely.
   </ol>
   </details>

   <br>

   <details style="font-family: Graphik; font-weight: 400;">
       <summary style="font-size: 1em !important; font-family: GraphikBold;" class="unselectable">
       <b>Privacy</b>
       </summary>
       <br>
       We do not collect any user information. The videos are deleted from our servers after the inference is completed, unless you flag any of them for further inspection.
   </details>
                       """,
                        css="""styles.css""",
                        cache_examples=True,
                        allow_flagging="never"
                        )

demo.launch(
    debug=True,
    share=True,
    server_port=8080,  # 443
    server_name="127.0.0.1",
    allowed_paths=["fonts", "/home/ubuntu/assets-24/gradio-recognition-screen/fonts", "static", "/home/ubuntu/assets-24/gradio-recognition-screen/static"]
)
