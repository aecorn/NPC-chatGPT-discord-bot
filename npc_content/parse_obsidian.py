import glob
import os
import toml
import random
from npc_content.base_path import BASEPATH



def parse_markdown(path: str) -> dict[str, str]:
    with open(path, "r") as md_file:
        content = md_file.read()
    #print(content)
    frontmatter = {}
    if "---\n" in content:
        if ": " in content:
            frontmatter = {line.split(": ")[0]: line.split(": ")[1] for line in content.split("---\n")[1].split("\n") if ": " in line}
    content_main = content.split("\n---\n")[-1]
    image_link = ""
    content_no_secrets = {}
    heading = ""
    content_piece = ""
    secret_flip = False

    for line in content_main.split("\n"):
        if line.startswith("![[") and not image_link:
            image_link = line.strip().strip("![[").strip("]]")
        elif "---secret" in line:
            secret_flip = True
        elif "secret---" in line:
            secret_flip = False
        elif line.strip().startswith("#") and not secret_flip:
            #print(heading)
            if content_piece:
                #print(f"inserting {heading}")
                content_no_secrets[heading] = content_piece
            content_piece = ""
            heading = line.strip("#").strip()
        elif heading and line.strip() and not secret_flip:
            content_piece += line + "\n"
            #print(content_piece)
    if content_piece and heading and not secret_flip:
        content_no_secrets[heading] = content_piece
    if image_link:
        content_no_secrets["image_link"] = f"{BASEPATH}assets/images/" + image_link.split("/")[-1]
    return frontmatter | content_no_secrets

def parse_vault():
    path  = f"{BASEPATH}Campaigns/A time for magic/NPCs"
    npc_paths = glob.glob(path + "/**/**/*.md") + glob.glob(path + "/**/*.md")
    npc_paths = [path for path in npc_paths if path]
    print(npc_paths)

    world_info = parse_markdown(f"{BASEPATH}Campaigns/A time for magic/staging/NPCs/World prompt.md")
    print(world_info)
    hooks = parse_markdown(f"{BASEPATH}Campaigns/A time for magic/staging/Current Plot Hooks.md")
    hooks = {k: [x.strip("\n") for x in v.split("- ") if x] for k, v in hooks.items()}

    # Get "current quest hooks" somehow?

    locations = (glob.glob(f"{BASEPATH}Setting/Cities,towns,settlements/**/*.md") +
                glob.glob(f"{BASEPATH}Setting/Locations/**/*.md"))
    locations = {x.split("/")[-1].split(".")[0]: x for x in locations}
    print(locations)
    # Test single character
    #npc_paths = [v for v in npc_paths if "busgar" in v.split("/")[-1].lower()]

    # Cleanup before generating
    for file in glob.glob("./npc_content/npc_tomls/*.toml"):
        os.remove(file)

    for character in npc_paths:
        char_data = parse_markdown(character)
        location_data = {}
        chosen_hook = ""
        if "lives" in char_data:
            char_lives = char_data.get("lives").replace("[","").replace("]","").replace('"', "")
            print(character)
            location_path = locations.get(char_lives)
            print(location_path, char_lives)
            location_data = parse_markdown(location_path)

            # Random plot hook for npc
            if char_lives in hooks:
                loc_hooks = hooks[char_lives]
                for hook in loc_hooks:
                    if not random.randrange(3):
                        chosen_hook = hook
                        break
                else:
                    chosen_hook = hook


        prompt_data = {}
        prompt_data["world"] = world_info
        if location_data:
            prompt_data["location"] = location_data
        if chosen_hook:
            prompt_data["hook"] = chosen_hook
        prompt_data["character"] = char_data

        with open(f"./npc_content/npc_tomls/{character.split('/')[-1].split('.')[0]}.toml", "w") as char_prompt_file:
            toml.dump(prompt_data, char_prompt_file)


if __name__ == "__main__":
    parse_vault()