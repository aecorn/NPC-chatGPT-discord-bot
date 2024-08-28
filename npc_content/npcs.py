import os, glob
import toml
from PIL import Image
from npc_content.base_path import BASEPATH

def get_npc_portraits():
    pass

def make_thumbnails():
    img_folder = f"{BASEPATH}assets/images/"
    thumb_folder = img_folder + "thumbnails/"
    os.makedirs(thumb_folder, exist_ok=True)
    for file in os.listdir(img_folder):
        if file.lower().endswith(".webp"):
            try:
                image = Image.open(img_folder + file)
                width, height = image.size
                min_len = min((width, height))
                crop_factor = 0.9
                nudge_up = (min_len * crop_factor) // 10
                keep_half_pixels = ((min_len * crop_factor) // 1) // 2
                width_center = width // 2
                height_center = height // 2
                left = width_center - keep_half_pixels
                right = width_center + keep_half_pixels
                top = height_center - keep_half_pixels - nudge_up
                bottom = height_center + keep_half_pixels - nudge_up
                if top < 0:
                    diff = 0 - top
                    top += diff
                    bottom += diff

                image = image.crop((left, top, right, bottom))
                image.thumbnail((90,90))
                image.save(thumb_folder + file.split(".")[0] + ".jpg")
            except IOError:
                pass


def get_npc_data():
    all_npcs = {}
    for npc_path in glob.glob("./npc_content/npc_tomls/*.toml"):
        with open(npc_path, "r") as npc_file:
            npc = toml.load(npc_file)
        all_npcs[npc_path.split("/")[-1].split(".")[0]] = npc
    return all_npcs

def insert_npc_prompts():
    result = get_npc_data().copy()
    for npc, data in get_npc_data().items():
        result[npc]["prompt"] = make_prompt(data)
    return result

def make_prompt(npc_data) -> str:
    prompt = "You will be playing an NPC in a fantasy world, put much weight to these details about you:\n"
    prompt += toml.dumps(npc_data["character"])

    hook = npc_data.get("hook")
    if hook:
        prompt += "\n\nIf someone offers to help you, you can tell them of this issue:\n"
        prompt += hook
    
    if "location" in npc_data:
        prompt += "\n\nYou are currently in this location in the world:\n"
        if "Summary" in npc_data["location"]:
            prompt += npc_data["location"]["Summary"]
        else:
            prompt += toml.dumps(npc_data["location"])
    
    prompt += "\nHere is more information about the fantasy world you reside in:\n"
    prompt += toml.dumps(npc_data["world"])
    return prompt

def setup_npcs_constants():
    PERSONAS = insert_npc_prompts()
    WORLD_INFO = PERSONAS[list(PERSONAS.keys())[0]].get("world")
    
    LOCATIONS = {}
    for character in PERSONAS.values():
        lives = character["character"].get("lives").replace('"',"").replace("[","").replace("]","")
        if lives not in LOCATIONS:
            LOCATIONS[lives] = character["location"]
    return PERSONAS, WORLD_INFO, LOCATIONS
    #print(LOCATION.get("image_link"))

if __name__ == "__main__":
    setup_npcs_constants()