import toml

def get_world_data():
     with open("./worldanvil/npcs.toml", "r") as npcs_toml:
        return toml.load(npcs_toml)

def setup_npcs(location: str = "Prinberg"):

    content = get_world_data()

    combined = {}
    for location, factions in content.items():
        if isinstance(factions, dict):
            for faction, characters in factions.items():
                #print(faction)
                #print(characters)
                if isinstance(characters, dict):
                    for character, attributes in characters.items():       
                        attributes["prompt"] = make_prompt(attributes)
                        combined[f"{character.lower()}-{faction.lower()}-{location.lower()}"] = attributes
                        #print(attributes["prompt"])
    return combined

def make_prompt(attributes) -> str:
    prompt = f"""You are a character in the fantasy setting Zarthuga. Where souls do not move on after death, and gods dying has been disasterous for the safety of this worlds peoples.
You are a {attributes["race"]} named {attributes["full_name"]}, you would be described by the people close to you as: {attributes["description"]}
When you speak you {attributes["figure_speech"]}"""
    if attributes["relations"]:
        close_relations = "Someone else close to you is:".join(attributes["relations"])
        prompt += f"The people close to you are: {close_relations}"
    if attributes["secrets"]:
        prompt += "They know some of your secrets. You will be very hesitant to reveal your secrets to the person you are talking to. But if you feel confident in the person you are talking to, and they manage to convince you, you may tell them one of your secrets: """ + ". Next secret: ".join(attributes["secrets"]) + ""
    prompt += "Answer the following conversation as this character."
    return prompt

PERSONAS = setup_npcs()
LOCATIONS = get_world_data()
