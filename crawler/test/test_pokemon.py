from urllib.request import urlopen, urlretrieve
import json
import os

url = "https://tw.portal-pokemon.com/play/pokedex/api/v1?pokemon_ability_id=&zukan_id_from=1&zukan_id_to=807"
response = urlopen(url)
jo = json.load(response)
pokemons = jo["pokemons"]
for pokemon in pokemons:
    zukan_id = pokemon["zukan_id"]
    zukan_sub_id = pokemon["zukan_sub_id"]
    pokemon_name = pokemon["pokemon_name"]
    pokemon_type_name = pokemon["pokemon_type_name"]
    file_name = pokemon["file_name"]
    img_url = "https://tw.portal-pokemon.com/play/resources/pokedex" + file_name
    print(zukan_id, zukan_sub_id, pokemon_name)
    print(img_url)
    dir_path = "D:/temp/pokemon/"
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    file_path = dir_path + str(zukan_id) + "." + str(
        zukan_sub_id) + "-" + pokemon_name + "(" + pokemon_type_name + ").png"
    urlretrieve(img_url, file_path)
