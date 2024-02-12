import toml


def setup_npcs(location: str = "Prinberg"):
    with open("./worldanvil/npcs.toml", "r") as npcs_toml:
        content = toml.load(npcs_toml)
    #print(content)

    combined = {}
    for location, factions in content.items():
        for faction, characters in factions.items():
            #print(faction)
            #print(characters)
            for character, attributes in characters.items():       
                
                attributes["prompt"] = f"""You are a character in the fantasy setting Zarthuga. Where souls do not move on after death, and gods dying has been disasterous for the safety of this worlds peoples.
You are a {attributes["race"]} named {attributes["full_name"]}, you would be described by the people close to you as: {attributes["description"]}
When you speak you {attributes["figure_speech"]}"""
                if attributes["relations"]:
                    close_relations = "Someone else close to you is:".join(attributes["relations"])
                    attributes["prompt"] += f"The people close to you are: {close_relations}"
                if attributes["secrets"]:
                    attributes["prompt"] += "They know some of your secrets. You will only reveal your secrets if you feel confident in the person you are talking to, and they manage to convince you, here are your secrets: """ + ". Next secret: ".join(attributes["secrets"]) + ""
                attributes["prompt"] += "Answer the following conversation as this character."
                combined[f"{character.lower()}-{faction.lower()}-{location.lower()}"] = attributes
                #print(attributes["prompt"])
    return combined

PERSONAS = setup_npcs()
