import os
import toml
from PIL import Image

def make_thumbnails():
    img_folder = "./npc_content/img/"
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


def get_world_data():
     with open("./npc_content/npcs.toml", "r") as npcs_toml:
        return toml.load(npcs_toml)

def setup_npcs(location: str = "Prinberg"):

    content = get_world_data()
    descriptions = {}
    descriptions["world"] = content["world_info_prompt"]
    combined = {}
    for location, factions in content.items():
        descriptions["location"] = content[location].get("description")
        if isinstance(factions, dict):
            for faction, characters in factions.items():
                descriptions["faction"] = factions[faction].get("description")
                #print(faction)
                #print(characters)
                if isinstance(characters, dict):
                    for character, attributes in characters.items():       
                        attributes["prompt"] = make_prompt(attributes, descriptions)
                        combined[f"{character.lower()}-{faction.lower()}-{location.lower()}"] = attributes
                        #print(attributes["prompt"])
    return combined

def make_prompt(attributes, descriptions) -> str:
    prompt = f"""{descriptions["world"]} You are currently located in {descriptions["location"]}. You are a member of the faction {descriptions["faction"]}
You are a {attributes["race"]} named {attributes["full_name"]}, you would be described by the people close to you as: {attributes["description"]}
When you speak you {attributes["figure_speech"]}"""
    if attributes["relations"]:
        close_relations = "Someone else close to you is:".join(attributes["relations"])
        prompt += f"The people close to you are: {close_relations}"
    if attributes["secrets"]:
        prompt += "They know some of your secrets. You will be very hesitant to reveal your secrets to the person you are talking to. But if you feel confident in the person you are talking to, and they manage to convince you, you may tell them one of your secrets: """ + ". Next secret: ".join(attributes["secrets"]) + ""
    prompt += "Answer the following conversation as the character described earlier, and only as this character. Feel free to describe actions the character does."
    return prompt

PERSONAS = setup_npcs()
LOCATIONS = get_world_data()
