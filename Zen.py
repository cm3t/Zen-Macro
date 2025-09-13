import os
import time
import json
import webbrowser
import psutil
import discord_webhook
import configparser
import customtkinter
import logging
import sys
from PIL import Image
import subprocess
import platformdirs
import datetime

logging.basicConfig(
    filename='crash.log',  # Optional: Specify a file to log to
    level=logging.INFO,  # Set the minimum level for logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s'  # Customize the log format
)

logger = logging.getLogger('mylogger')

def popup(message, title):
    applescript = """
    display dialog "{message}" ¬
    with title "{title}" ¬
    with icon caution ¬
    buttons {{"OK"}}
    """.format(message=message, title=title)

    subprocess.call("osascript -e '{}'".format(applescript), shell=True)

CMD = '''
on run argv
  display notification (item 2 of argv) with title (item 1 of argv)
end run
'''

def notify(title, text):
  subprocess.call(['osascript', '-e', CMD, title, text])

# Example uses:
def my_handler(types, value, tb):
    logger.exception("Uncaught exception: {0}".format(str(value)))
    popup("Check crash.log for information on this crash.", "Crashed!")
    sys.exit()

def apply_fast_flags(version):
    try:
        os.mkdir("/Applications/Roblox.app/Contents/MacOS/ClientSettings")
    except FileExistsError:
        print("ClientSettings folder already exists.")
    flags = {"FStringDebugLuaLogLevel": "debug", "FStringDebugLuaLogPattern": "ExpChat/mountClientApp"}
    try:
        with open("/Applications/Roblox.app/Contents/MacOS/ClientSettings/ClientAppSettings.json", "r") as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        existing_data = {}
    existing_data.update(flags)
    with open("/Applications/Roblox.app/Contents/MacOS/ClientSettings/ClientAppSettings.json", "w") as f:
        json.dump(existing_data, f, indent=4)
    print("Successfully patched Roblox and added fast flags.")


# exception handler / logger
sys.excepthook = my_handler

# create UI window
customtkinter.set_default_color_theme("dark-blue")
root = customtkinter.CTk()
root.title("Zen")
root.geometry('505x285')
root.resizable(False, False)
dirname = os.path.dirname(__file__)
tabview = customtkinter.CTkTabview(root, width=505, height=230)
tabview.grid(row=0, column=0, sticky='nsew', columnspan=75)
tabview.add("Webhook")
tabview.add("Macro")
tabview.add("Credits")
tabview._segmented_button.configure(font=customtkinter.CTkFont(family="Segoe UI", size=16))
tabview._segmented_button.grid(sticky="w", padx=15)

# read configuration file
config_name = 'config.ini'
config = configparser.ConfigParser()
if not os.path.exists(config_name):
    logger.info("Config file not found, creating one...")
    print("Config file not found, creating one...")
    config['Webhook'] = {'webhook_url': "", 'private_server': "", "discord_user_id": "",  'multi_webhook': "0", 'multi_webhook_urls': ""}
    config['Macro'] = {'aura_detection': "0", 'username_override': "", 'last_roblox_version': "", 'aura_notif': "0", 'aura_ping': "0"}
    with open(config_name, 'w') as configfile:
        config.write(configfile)
config.read(config_name)
webhookURL = customtkinter.StringVar(root, config['Webhook']['webhook_url'])
psURL = customtkinter.StringVar(root, config['Webhook']['private_server'])
discID = customtkinter.StringVar(root, config['Webhook']['discord_user_id'])
multi_webhook = customtkinter.StringVar(root, config['Webhook']['multi_webhook'])
if multi_webhook.get() != "1" and webhookURL.get() == "Multi-Webhook On":
    webhookURL.set("")
webhook_urls_string = customtkinter.StringVar(root, config['Webhook']['multi_webhook_urls'])
webhook_urls = webhook_urls_string.get().split()
aura_images = {"\u00e2\u02dc\u2026": "https://static.wikia.nocookie.net/sol-rng/images/d/d7/Dreamscape_star1_collection.png/revision/latest", "\u00e2\u02dc\u2026\u00e2\u02dc\u2026": "https://static.wikia.nocookie.net/sol-rng/images/4/4f/Dreamscape_star2.png/revision/latest", "fault": "https://static.wikia.nocookie.net/sol-rng/images/e/e1/Fault_Aura_Collection_GIF.gif/revision/latest", "\u00e2\u02dc\u2026\u00e2\u02dc\u2026\u00e2\u02dc\u2026": "https://static.wikia.nocookie.net/sol-rng/images/a/a3/Screenshot_2025-02-09_145439.png/revision/latest", "undead": "https://static.wikia.nocookie.net/sol-rng/images/e/eb/UndeadAura.gif/revision/latest", "corrosive": "https://static.wikia.nocookie.net/sol-rng/images/9/94/Corrosive.gif/revision/latest", "rage : heated": "https://static.wikia.nocookie.net/sol-rng/images/1/14/RageHeatedAura.gif/revision/latest", "ink : leak": "https://static.wikia.nocookie.net/sol-rng/images/d/da/LeakGif.gif/revision/latest", "powered": "https://static.wikia.nocookie.net/sol-rng/images/9/9a/Powered.gif/revision/latest", "watt": "https://static.wikia.nocookie.net/sol-rng/images/c/ca/WattCollection.gif/revision/latest", "aquatic": "https://static.wikia.nocookie.net/sol-rng/images/a/a9/AquaticAura.gif/revision/latest", "solar": "https://static.wikia.nocookie.net/sol-rng/images/4/41/SolarAuraNight.gif/revision/latest", "lunar": "https://static.wikia.nocookie.net/sol-rng/images/d/d3/Lunar_Collection_E7.gif/revision/latest", "starlight": "https://static.wikia.nocookie.net/sol-rng/images/2/22/StarlightCollection.gif/revision/latest", "starrider": "https://static.wikia.nocookie.net/sol-rng/images/1/1a/StarRiderCollection.gif/revision/latest", " :flushed: : lobotomy": "https://static.wikia.nocookie.net/sol-rng/images/f/f6/FlushedLobotomyAura.gif/revision/latest", "permafrost": "https://static.wikia.nocookie.net/sol-rng/images/b/bd/PermaFrostCollection.gif/revision/latest", "hazard : rays": "https://static.wikia.nocookie.net/sol-rng/images/c/c1/Hazard_Rays.gif/revision/latest", "nautilus": "https://static.wikia.nocookie.net/sol-rng/images/e/e2/NautilusAuraNight.gif/revision/latest", "stormal": "https://static.wikia.nocookie.net/sol-rng/images/6/65/Stormal_Collection_E7.gif/revision/latest", "exotic": "https://static.wikia.nocookie.net/sol-rng/images/7/71/ExoticAura150x150.gif/revision/latest", "exotic : apex": "https://static.wikia.nocookie.net/sol-rng/images/0/09/Exotic_Apex_Collection_E7.gif/revision/latest", "exotic : void": "https://static.wikia.nocookie.net/sol-rng/images/c/c7/ExoticVoidCollection.gif/revision/latest", "diaboli : void": "https://static.wikia.nocookie.net/sol-rng/images/e/ee/Diabolivoidcollection.gif/revision/latest", "undead : devil": "https://static.wikia.nocookie.net/sol-rng/images/7/73/UndeadDevilCollectionEon1.gif/revision/latest", "comet": "https://static.wikia.nocookie.net/sol-rng/images/1/16/Comet_collect.gif/revision/latest", "jade": "https://static.wikia.nocookie.net/sol-rng/images/0/06/JadeInCollection.gif/revision/latest", "spectre": "https://static.wikia.nocookie.net/sol-rng/images/e/ed/SpectreCollection.gif/revision/latest", "jazz": "https://static.wikia.nocookie.net/sol-rng/images/2/2d/JazzCollectionBetter.gif/revision/latest", "aether": "https://static.wikia.nocookie.net/sol-rng/images/9/91/AetherCollection.gif/revision/latest", "bounded": "https://static.wikia.nocookie.net/sol-rng/images/5/52/BoundedAuraNight.gif/revision/latest", "celestial": "https://static.wikia.nocookie.net/sol-rng/images/6/64/Celestial_Rework_Collection.gif/revision/latest", "celestial : divine": "https://static.wikia.nocookie.net/sol-rng/images/c/c4/CelestialDivineCollection.gif/revision/latest", "warlock": "https://static.wikia.nocookie.net/sol-rng/images/9/9c/WarlockCollection.gif/revision/latest", "kyawthuite": "https://static.wikia.nocookie.net/sol-rng/images/6/67/Kyawthuite_Collection2.gif/revision/latest", "kyawthuite : remembrance": "https://static.wikia.nocookie.net/sol-rng/images/d/d4/KyawthuiteRememberance.webp/revision/latest", "arcane": "https://static.wikia.nocookie.net/sol-rng/images/d/d8/ArcaneCollectionN3w.gif/revision/latest", "arcane : legacy": "https://static.wikia.nocookie.net/sol-rng/images/7/72/Arcane_Legacy_Collection_E7.gif/revision/latest", "arcane : dark": "https://static.wikia.nocookie.net/sol-rng/images/1/10/Arcane-dark-collection-era9.gif/revision/latest", "magnetic : reverse polarity": "https://static.wikia.nocookie.net/sol-rng/images/8/8f/Magnetic_Reverse_Polarity_Rework_Collection.gif/revision/latest", "undefined": "https://static.wikia.nocookie.net/sol-rng/images/b/b0/Undefined_Collection1.gif/revision/latest", "rage : brawler": "https://static.wikia.nocookie.net/sol-rng/images/0/0b/BrawlerCollection.gif/revision/latest", "astral": "https://static.wikia.nocookie.net/sol-rng/images/5/57/Astral_Era9.gif/revision/latest", "cosmos": "https://static.wikia.nocookie.net/sol-rng/images/4/4c/CosmosCollection.gif/revision/latest", "gravitational": "https://static.wikia.nocookie.net/sol-rng/images/f/fd/Grav_CollectionE9.gif/revision/latest", "bounded : unbound": "https://static.wikia.nocookie.net/sol-rng/images/6/65/Unbound_E7_Collection2.gif/revision/latest", "virtual": "https://static.wikia.nocookie.net/sol-rng/images/8/88/VirtualReworkCollection.gif/revision/latest", "virtual : fatal error": "https://static.wikia.nocookie.net/sol-rng/images/8/8e/FatalErrorCollection.png/revision/latest", "savior": "https://static.wikia.nocookie.net/sol-rng/images/a/a4/Savior_Collection.gif/revision/latest", "poseidon": "https://static.wikia.nocookie.net/sol-rng/images/d/db/PosEra7.gif/revision/latest", "aquatic : flame": "https://static.wikia.nocookie.net/sol-rng/images/7/7f/Aqua_flame_new_gif.gif/revision/latest", "zeus": "https://static.wikia.nocookie.net/sol-rng/images/4/41/Zeus_GIF.gif/revision/latest", "lunar : full moon": "https://static.wikia.nocookie.net/sol-rng/images/4/40/LunarFMReworkCollection.gif/revision/latest", "solar : solstice": "https://static.wikia.nocookie.net/sol-rng/images/1/1c/SolarSolsticeG.gif/revision/latest", "galaxy": "https://static.wikia.nocookie.net/sol-rng/images/f/f8/Galaxy_Aura.gif/revision/latest", "twilight": "https://static.wikia.nocookie.net/sol-rng/images/b/b4/TwilightInCollection.gif/revision/latest", "twilight : iridescent memory": "https://static.wikia.nocookie.net/sol-rng/images/f/fc/Twilight_-_Iridescent_Memory_Collection.gif/revision/latest", "origin": "https://static.wikia.nocookie.net/sol-rng/images/6/6c/OriginCollectionEon1.gif/revision/latest", "hades": "https://static.wikia.nocookie.net/sol-rng/images/8/85/HadesCollection.gif/revision/latest", "hyper-volt": "https://static.wikia.nocookie.net/sol-rng/images/d/d4/HpVl.gif/revision/latest", "velocity": "https://static.wikia.nocookie.net/sol-rng/images/5/54/Velocitygif.gif/revision/latest", "nihility": "https://static.wikia.nocookie.net/sol-rng/images/c/ca/Nihility_collection.gif/revision/latest", "helios": "https://static.wikia.nocookie.net/sol-rng/images/e/ed/HeliosCollection.gif/revision/latest", "starscourge": "https://static.wikia.nocookie.net/sol-rng/images/9/9d/StarscourgeRevampCollection.gif/revision/latest", "starscourge : radiant": "https://static.wikia.nocookie.net/sol-rng/images/1/16/Starscourge_Radiant_Gif2.gif/revision/latest", "sailor": "https://static.wikia.nocookie.net/sol-rng/images/e/e2/SailorCollectionEra7.gif/revision/latest", "sailor : flying dutchman": "https://static.wikia.nocookie.net/sol-rng/images/5/53/DutchmanCollectionEon1.gif/revision/latest", "stormal : hurricane": "https://static.wikia.nocookie.net/sol-rng/images/d/d9/Hurricane_Collection_Eon_1_reupload.gif/revision/latest", "sirius": "https://static.wikia.nocookie.net/sol-rng/images/c/c2/Siriusincollection.gif/revision/latest", "chromatic": "https://static.wikia.nocookie.net/sol-rng/images/d/d6/Chromatic_GIF.gif/revision/latest", "chromatic : genesis": "https://static.wikia.nocookie.net/sol-rng/images/7/72/Genesis-Collection.gif/revision/latest", "aviator": "https://static.wikia.nocookie.net/sol-rng/images/4/43/Aviator_Collection.gif/revision/latest", "ethereal": "https://static.wikia.nocookie.net/sol-rng/images/b/bc/Etherealpretrans.gif/revision/latest", "overseer": "https://static.wikia.nocookie.net/sol-rng/images/0/0b/Overseer-collection.gif/revision/latest", "runic": "https://static.wikia.nocookie.net/sol-rng/images/e/ed/RunicColl.gif/revision/latest", "matrix": "https://static.wikia.nocookie.net/sol-rng/images/9/97/MatrixCollectionEon1.gif/revision/latest", "matrix : overdrive": "https://static.wikia.nocookie.net/sol-rng/images/e/e4/MatrixOverdriveCollection.gif/revision/latest", "matrix : reality": "https://static.wikia.nocookie.net/sol-rng/images/a/a0/Matrix_but_real.gif/revision/latest", "sentinel": "https://static.wikia.nocookie.net/sol-rng/images/9/96/SentinelCollection.gif/revision/latest", "carriage": "https://static.wikia.nocookie.net/sol-rng/images/7/7d/Collection_Carriage.gif/revision/latest", "overture": "https://static.wikia.nocookie.net/sol-rng/images/e/e8/Overture_Collection.gif/revision/latest", "overture : history": "https://static.wikia.nocookie.net/sol-rng/images/6/61/Overture_History_Eon1_Collection.gif/revision/latest", "symphony": "https://static.wikia.nocookie.net/sol-rng/images/f/f5/Symphony_Collection_with_crown.gif/revision/latest", "impeached": "https://static.wikia.nocookie.net/sol-rng/images/2/2f/Impeached_Collectiongifv2.gif/revision/latest", "archangel": "https://static.wikia.nocookie.net/sol-rng/images/4/4f/ArchangelCollection.gif/revision/latest", "bloodlust": "https://static.wikia.nocookie.net/sol-rng/images/f/f9/BloodlustInCollection.gif/revision/latest", "atlas": "https://static.wikia.nocookie.net/sol-rng/images/0/0b/Atlas_collection.gif/revision/latest", "abyssalhunter": "https://static.wikia.nocookie.net/sol-rng/images/2/25/Abyssal_Hunter_Max_Graphics.gif/revision/latest", "gargantua": "https://static.wikia.nocookie.net/sol-rng/images/5/5a/GargantuaStable.gif/revision/latest", "apostolos": "https://static.wikia.nocookie.net/sol-rng/images/1/17/In-collection_Apostolos.gif/revision/latest", "ruins": "https://static.wikia.nocookie.net/sol-rng/images/7/74/Ruins.collection.gif/revision/latest", "sovereign": "https://static.wikia.nocookie.net/sol-rng/images/0/05/Sovereign_Collection_E8.gif/revision/latest", "ruins : withered": "https://static.wikia.nocookie.net/sol-rng/images/a/a9/Ruins_-_witheredincollection2.png/revision/latest", "aegis": "https://static.wikia.nocookie.net/sol-rng/images/a/ab/AegisCollection.gif/revision/latest", "pixelation": "https://static.wikia.nocookie.net/sol-rng/images/6/61/Pixelation_In-Game.gif/revision/latest", "luminosity": "https://static.wikia.nocookie.net/sol-rng/images/e/ea/Luminosity_Collection.gif/revision/latest", "glitch": "https://static.wikia.nocookie.net/sol-rng/images/a/a1/Era8glitchcollection.gif/revision/latest", "oppression": "https://static.wikia.nocookie.net/sol-rng/images/c/c1/OppressionCollectionEon1.gif/revision/latest", "memory": "https://static.wikia.nocookie.net/sol-rng/images/a/ad/MemoryCollectionEon1.gif/revision/latest", "oblivion": " ://static.wikia.nocookie.net/sol-rng/images/c/c5/Oblivion_colletion_eon1-1.gif/revision/latest", "wonderland": "https://static.wikia.nocookie.net/sol-rng/images/3/39/WonderlandCollection.gif/revision/latest", "santa frost": "https://static.wikia.nocookie.net/sol-rng/images/3/32/FrostCollection.gif/revision/latest", "winter fantasy": "https://static.wikia.nocookie.net/sol-rng/images/8/8e/Winter_Fantasy%28Collection%29.gif/revision/latest", "express": "https://static.wikia.nocookie.net/sol-rng/images/1/10/ExpressCollectionGIf.gif/revision/latest", "abomitable": "https://static.wikia.nocookie.net/sol-rng/images/b/bb/AbomitableIngame.gif/revision/latest", "atlas : yuletide": "https://static.wikia.nocookie.net/sol-rng/images/e/e4/Roblox2025-02-0917-24-01-ezgif.com-optimize.gif/revision/latest", " :flushed : : troll": "https://static.wikia.nocookie.net/sol-rng/images/f/fb/TrollCollection.gif/revision/latest", "origin : onion": "https://static.wikia.nocookie.net/sol-rng/images/c/c3/OnionCollection.gif/revision/latest", "glock : shieldofthesky": "https://static.wikia.nocookie.net/sol-rng/images/5/5f/Glock_of_the_sky_in_Collection_%28better_version%29.png/revision/latest", "anubis": "https://static.wikia.nocookie.net/sol-rng/images/a/a7/AnubisC.gif/revision/latest", "blizzard": "https://static.wikia.nocookie.net/sol-rng/images/0/02/Screenshot_2025-04-19_103324.png/revision/latest", "jazz : orchestra": "https://static.wikia.nocookie.net/sol-rng/images/3/35/Orchestra_jazz.gif/revision/latest", "astral : legendarium": "https://static.wikia.nocookie.net/sol-rng/images/f/fe/Legendcollec.png/revision/latest", "stargazer": "https://static.wikia.nocookie.net/sol-rng/images/9/97/Stargazerincollection.gif/revision/latest", "harnessed": "https://static.wikia.nocookie.net/sol-rng/images/9/94/Harnessed_collec.gif/revision/latest/", "raven": "https://static.wikia.nocookie.net/sol-rng/images/5/5a/RavenCollection.gif/revision/latest", "anima": "https://static.wikia.nocookie.net/sol-rng/images/f/f4/AnimaCollection.gif/revision/latest", "juxtaposition": "https://static.wikia.nocookie.net/sol-rng/images/1/1e/JuxtapColl.gif/revision/latest", "unknown": "https://static.wikia.nocookie.net/sol-rng/images/b/b6/Unknownincollection.gif/revision/latest", "elude": "https://static.wikia.nocookie.net/sol-rng/images/1/11/EludeCollection.gif/revision/latest", "prologue": "https://static.wikia.nocookie.net/sol-rng/images/d/d6/PrologueCollection.gif/revision/latest", "dreamscape": "https://static.wikia.nocookie.net/sol-rng/images/1/1a/DreamscapeInCollection.gif/revision/latest", "manta": "https://static.wikia.nocookie.net/sol-rng/images/3/31/Manta_In-Collection.gif/revision/latest", "aegis : watergun": "https://static.wikia.nocookie.net/sol-rng/images/a/ac/Aegis_Watergun_in_collection.gif/revision/latest"}

# variables
last_roblox_version = config['Macro']['last_roblox_version']
username_override = config['Macro']['username_override']
roblox_open = False
log_directory = platformdirs.user_log_dir("Roblox", None)
biome_colors = {"NORMAL": "ffffff", "SAND STORM": "F4C27C", "HELL": "5C1219", "STARFALL": "6784E0", "CORRUPTION": "9042FF", "NULL": "000000", "GLITCHED": "65FF65", "WINDY": "91F7FF", "SNOWY": "C4F5F6", "RAINY": "4385FF", "DREAMSPACE": "ff7dff", "BLAZING SUN": "ffee8c"}
biome_times = {"SAND STORM": 600, "HELL": 660, "STARFALL": 600, "CORRUPTION": 660, "NULL": 99, "GLITCHED": 164, "WINDY": 120, "SNOWY": 120, "RAINY": 120, "DREAMSPACE": 128, "BLAZING SUN": 180}
started = False
stopped = False
paused = False
destroyed = False
debug_window = False
tlw_open = False
aura_detection = customtkinter.IntVar(root, int(config['Macro']['aura_detection']))
aura_notif = customtkinter.IntVar(root, int(config['Macro']['aura_notif']))
aura_ping = customtkinter.IntVar(root, int(config['Macro']['aura_ping']))
roblox_username = config['Macro']['username_override']


def stop():
    global stopped
    # write config data
    config.set('Webhook', 'webhook_url', webhookURL.get())
    config.set('Webhook', 'private_server', psURL.get())
    with open(config_name, 'w+') as configfile:
        config.write(configfile)

    # end webhook
    if started and not stopped:
        if multi_webhook.get() != "1":
            if "discord.com" in webhookURL.get() and "https://" in webhookURL.get():
                ending_webhook = discord_webhook.DiscordWebhook(url=webhookURL.get())
                ending_embed = discord_webhook.DiscordEmbed(
                        description="**Macro stopped.**",
                        timestamp=datetime.datetime.now(datetime.timezone.utc))
                ending_embed.set_author(name="Zen", icon_url="https://cm3t.github.io/biome_thumb/zen.png")
                ending_webhook.add_embed(ending_embed)
                ending_webhook.execute()

        else:
            ending_embed = discord_webhook.DiscordEmbed(
                description="**Macro stopped.**",
                timestamp=datetime.datetime.now(datetime.timezone.utc))
            ending_embed.set_author(name="Zen", icon_url="https://cm3t.github.io/biome_thumb/zen.png")
            for url in webhook_urls:
                ending_webhook = discord_webhook.DiscordWebhook(url=url)
                ending_webhook.add_embed(ending_embed)
                ending_webhook.execute()
    else:
        sys.exit()
    stopped = True

def pause():
    global paused
    paused = not paused
    if paused:
        root.title("maxstellar's Biome Macro - Paused")
    else:
        root.title("maxstellar's Biome Macro - Running")

if multi_webhook == "1":
    if len(webhook_urls) < 2:
        popup("there's no reason to use multi-webhook... without multiple webhooks??", "bruh are you serious")
    elif len(webhook_urls) > 14:
        if len(webhook_urls) > 49:
            popup("you've gotta be doing this on purpose now... you don't need this many webhooks", "this is ridiculous")
        else:
            popup("bro you do not need this many webhooks", "okay dude wtf")
    stop()


def x_stop():
    global destroyed
    destroyed = True
    stop()


def get_latest_log_file():
    files = os.listdir(log_directory)
    paths = [os.path.join(log_directory, basename) for basename in files]
    return max(paths, key=os.path.getctime)


def is_roblox_running():
    processes = []
    for i in psutil.process_iter():
        try:
            processes.append(i.name())
        except:
            pass
    return "RobloxPlayer" in processes

def auranotif_toggle_update():
    config.set('Macro', 'aura_notif', str(aura_notif.get()))
    with open(config_name, 'w+') as configfile:
        config.write(configfile)


def auraping_toggle_update():
    config.set('Macro', 'aura_ping', str(aura_ping.get()))
    with open(config_name, 'w+') as configfile:
        config.write(configfile)

def jester_toggle_update():
    config.set('Macro', 'jester', str(aura_ping.get()))
    with open(config_name, 'w+') as configfile:
        config.write(configfile)


def check_for_hover_text(file):
    last_event = None
    last_aura = None
    file.seek(0, 2)
    while True:
        if not stopped:
            root.update()
        else:
            if not destroyed:
                root.destroy()
            sys.exit()
        check = is_roblox_running()
        if check:
            line = file.readline()
            if line:
                print(line)
                if '"command":"SetRichPresence"' in line:
                    try:
                        json_data_start = line.find('{"command":"SetRichPresence"')
                        if json_data_start != -1:
                            json_data = json.loads(line[json_data_start:])
                            event = json_data.get("data", {}).get("largeImage", {}).get("hoverText", "")
                            state = json_data.get("data", {}).get("state", "")
                            aura = state[10:-1]
                            if event and event != last_event:
                                if multi_webhook.get() != "1":
                                    if "discord.com" not in webhookURL.get() or "https://" not in webhookURL.get():
                                        popup("Invalid or missing webhook link.", "Error")
                                        stop()
                                        return
                                    webhook = discord_webhook.DiscordWebhook(url=webhookURL.get())
                                    if event == "NORMAL":
                                        if last_event is not None:
                                            print(time.strftime('%H:%M:%S') + f": Biome Ended - " + last_event)
                                            embed = discord_webhook.DiscordEmbed(
                                                timestamp=datetime.datetime.now(datetime.timezone.utc),
                                                color=biome_colors[last_event],
                                                description="> ## Biome Ended - " + last_event)
                                            embed.set_thumbnail(url="https://cm3t.github.io/biome_thumb/" + last_event.replace(" ", "%20") + ".png")
                                            embed.set_author(name="Zen", icon_url="https://cm3t.github.io/biome_thumb/zen.png")
                                            webhook.add_embed(embed)
                                            webhook.execute()
                                        else:
                                            pass
                                    else:
                                        print(time.strftime('%H:%M:%S') + f": Biome Started - {event}")
                                        embed = discord_webhook.DiscordEmbed(timestamp=datetime.datetime.now(datetime.timezone.utc), color=biome_colors[event])
                                        biomeEndingTime = int(time.time()) + biome_times[event]
                                        embed.description = "> ## Biome Started - " + event + "\n> [Join Private Server](" + psURL.get() + ")\n> -# Ends <t:" + str(biomeEndingTime) + ":R>"
                                        embed.set_thumbnail(url="https://cm3t.github.io/biome_thumb/" + event.replace(" ", "%20") + ".png")
                                        embed.set_author(name="Zen", icon_url="https://cm3t.github.io/biome_thumb/zen.png")
                                        webhook.add_embed(embed)
                                        if event == "GLITCHED" or event == "DREAMSPACE":
                                            webhook.set_content("@everyone")
                                            notify("Zen", "Biome Started: " + event)
                                        webhook.execute()
                                else:
                                    if event == "NORMAL":
                                        if last_event is not None:
                                            print(time.strftime('%H:%M:%S') + f": Biome Ended - " + last_event)
                                            for url in webhook_urls:
                                                webhook = discord_webhook.DiscordWebhook(url=url)
                                                embed = discord_webhook.DiscordEmbed(
                                                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                                                    color=biome_colors[last_event],
                                                    description="> ## Biome Ended - " + last_event)
                                                embed.set_thumbnail(url="https://cm3t.github.io/biome_thumb/" + last_event.replace(" ", "%20") + ".png")
                                                embed.set_author(name="Zen", icon_url="https://cm3t.github.io/biome_thumb/zen.png")
                                                webhook.add_embed(embed)
                                                webhook.execute()
                                        else:
                                            pass
                                    else:
                                        print(time.strftime('%H:%M:%S') + f": Biome Started - {event}")
                                        biomeEndingTime = int(time.time()) + biome_times[event]            
                                        for url in webhook_urls:
                                            embed = discord_webhook.DiscordEmbed(timestamp=datetime.datetime.now(datetime.timezone.utc), color=biome_colors[event])
                                            embed.description = "> ## Biome Started - " + event + "\n> [Join Private Server](" + psURL.get() + ")\n> -# Ends <t:" + str(biomeEndingTime) + ":R>"
                                            embed.set_thumbnail(url="https://cm3t.github.io/biome_thumb/" + event.replace(" ", "%20") + ".png")
                                            embed.set_author(name="Zen", icon_url="https://cm3t.github.io/biome_thumb/zen.png")
                                            webhook = discord_webhook.DiscordWebhook(url=url)
                                            webhook.add_embed(embed)
                                            if event == "GLITCHED" or event == "DREAMSPACE":
                                                webhook.set_content("@everyone")
                                            webhook.execute()
                                        if event == "GLITCHED" or event == "DREAMSPACE":
                                            notify("Zen", "Biome Started: " + event)
                                last_event = event
                            if state and aura != last_aura and aura != "n":
                                if aura_detection.get() == 1 and aura != "None":
                                    if multi_webhook.get() != "1":
                                        if "discord.com" not in webhookURL.get() or "https://" not in webhookURL.get():
                                            popup("Invalid or missing webhook link.", "Error")
                                            stop()
                                            return
                                        webhook = discord_webhook.DiscordWebhook(url=webhookURL.get())
                                        print(time.strftime('%H:%M:%S') + f": Aura Equipped - {aura}")
                                        embed = discord_webhook.DiscordEmbed(
                                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                                            description="> ## Aura Equipped - " + aura)
                                        embed.set_author(name="Zen", icon_url="https://cm3t.github.io/biome_thumb/zen.png")
                                        if aura == "Luminosity" or aura == "EQUINOX" or aura == "Pixelation":
                                            embed.set_thumbnail(url="https://cm3t.github.io/aura_thumb/" + aura.replace(" ", "%20") + ".png")
                                        webhook.add_embed(embed)
                                        webhook.execute()
                                    else:
                                        print(time.strftime('%H:%M:%S') + f": Aura Equipped - {aura}")
                                        for url in webhook_urls:
                                            webhook = discord_webhook.DiscordWebhook(url=url)
                                            embed = discord_webhook.DiscordEmbed(
                                                timestamp=datetime.datetime.now(datetime.timezone.utc),
                                                description="> ## Aura Equipped - " + aura)
                                            embed.set_author(name="Zen", icon_url="https://cm3t.github.io/biome_thumb/zen.png")
                                            if aura == "Luminosity" or aura == "EQUINOX" or aura == "Pixelation":
                                                embed.set_thumbnail(url="https://cm3t.github.io/aura_thumb/" + aura.replace(" ", "%20") + ".png")
                                            webhook.add_embed(embed)
                                            webhook.execute()
                                last_aura = aura
                    except json.JSONDecodeError:
                        print("Error decoding JSON")
                elif "Incoming MessageReceived Status:" in line:
                    # check if message is specially formatted (aura roll, jester)
                    if "</font>" in line:
                        if aura_detection.get() == 1 and "HAS FOUND" in line:
                            # handle HAS FOUND message
                            userdata, _, auradata = line.partition("HAS FOUND")
                            auradata = auradata[1:-8]
                            aura, _, rarity = auradata.partition(", ")
                            rarity = rarity[15:-1]
                            int_rarity = rarity.replace(',', '')
                            message_color = line[line.find('<font color="#') + len('<font color="#'):line.find('">', line.find('<font color="#'))]
                            # remove [From Biome]
                            int_rarity = int_rarity.split()[0]
                            if int(int_rarity) < 99999 and aura != "Fault" and "\u00e2\u02dc\u2026" not in aura:
                               continue
                            _, _, full_user = userdata.rpartition(">")
                            full_user = full_user[:-1]
                            if "(" in full_user:
                                _, _, rolled_username = full_user.partition("(")
                                rolled_username = rolled_username[1:-1]
                            else:
                                rolled_username = full_user[1:]
                            if rolled_username == roblox_username.strip():
                                if multi_webhook.get() != "1":
                                    webhook = discord_webhook.DiscordWebhook(url=webhookURL.get())
                                    print(time.strftime('%H:%M:%S') + f": Aura Rolled - {aura}")
                                    embed = discord_webhook.DiscordEmbed(
                                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                                        description="> ## You rolled " + aura + "!\n> **1 in " + rarity + "**",
                                        color=message_color)
                                    embed.set_author(name="Zen", icon_url="https://cm3t.github.io/biome_thumb/zen.png")
                                    embed.set_thumbnail(url=aura_images[aura.lower()])
                                    webhook.add_embed(embed)
                                    if aura_ping.get() == 1:
                                        webhook.set_content(f"<@{discID.get()}>")
                                    webhook.execute()
                                    if aura_notif.get() == 1:
                                        notify("Zen", "You rolled " + aura + "!")
                                else:
                                    print(time.strftime('%H:%M:%S') + f": Aura Rolled - {aura}")
                                    for url in webhook_urls:
                                        webhook = discord_webhook.DiscordWebhook(url=url)
                                        embed = discord_webhook.DiscordEmbed(
                                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                                            description="> ## You rolled " + aura + "!\n> **1 in " + rarity + "**",
                                            color=message_color
                                        )
                                        embed.description = "> ## You rolled " + aura + "!\n> **1 in " + rarity + "**"
                                        embed.set_author(name="Zen", icon_url="https://cm3t.github.io/biome_thumb/zen.png")
                                        embed.set_thumbnail(url=aura_images[aura.lower()])
                                        webhook.add_embed(embed)
                                        if aura_ping.get() == 1:
                                            webhook.set_content(f"<@{discID.get()}>")
                                        webhook.execute()
                                    if aura_notif.get() == 1:
                                        notify("Zen", "You rolled " + aura + "!")
                        elif aura_detection.get() == 1 and "The Blinding Light has devoured" in line:
                            if roblox_username in line:
                                if multi_webhook.get() != "1":
                                    webhook = discord_webhook.DiscordWebhook(url=webhookURL.get())
                                    print(time.strftime('%H:%M:%S') + f": Aura Rolled - Luminosity")
                                    embed = discord_webhook.DiscordEmbed(
                                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                                        description=f"> ## The Blinding Light has devoured {roblox_username}\n> **1 in 1,200,000,000**",
                                        color="98b7e0")
                                    embed.set_author(name="Zen", icon_url="https://cm3t.github.io/biome_thumb/zen.png")
                                    embed.set_thumbnail(url=aura_images['luminosity'])
                                    webhook.add_embed(embed)
                                    if aura_ping.get() == 1:
                                        webhook.set_content(f"<@{discID.get()}>")
                                    webhook.execute()
                                    if aura_notif.get() == 1:
                                        notify("Zen", "You rolled Luminosity!")
                                else:
                                    print(time.strftime('%H:%M:%S') + f": Aura Rolled - Luminosity")
                                    for url in webhook_urls:
                                        webhook = discord_webhook.DiscordWebhook(url=url)
                                        embed = discord_webhook.DiscordEmbed(
                                            timestamp=datetime.datetime.now(datetime.timezone.utc),
                                            description=f"> ## The Blinding Light has devoured {roblox_username}\n> **1 in 1,200,000,000**",
                                            color="98b7e0")
                                        embed.set_author(name="Zen", icon_url="https://cm3t.github.io/biome_thumb/zen.png")
                                        embed.set_thumbnail(url=aura_images['luminosity'])
                                        webhook.add_embed(embed)
                                        if aura_ping.get() == 1:
                                            webhook.set_content(f"<@{discID.get()}>")
                                        webhook.execute()
                                    if aura_notif.get() == 1:
                                        notify("Zen", "You rolled Luminosity!")
                        elif "[Merchant]: Jester has arrived on the island!!" in line:
                            if multi_webhook.get() != "1":
                                webhook = discord_webhook.DiscordWebhook(url=webhookURL.get())
                                print(time.strftime('%H:%M:%S') + f": Jester has arrived!")
                                embed = discord_webhook.DiscordEmbed(
                                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                                    description=f"> ## Jester has arrived!\n<t:{int(time.time())}:R>\n\n{psURL.get()}",
                                    color="a352ff"
                                )
                                embed.set_author(name="Zen", icon_url="https://cm3t.github.io/biome_thumb/zen.png")
                                embed.set_thumbnail(
                                    url="https://static.wikia.nocookie.net/sol-rng/images/d/db/Headshot_of_Jester.png/revision/latest?cb=20240630142936")
                                webhook.add_embed(embed)
                                webhook.set_content(f"<@{discID.get()}>")
                                webhook.execute()
                            else:
                                print(time.strftime('%H:%M:%S') + f": Jester has arrived!")
                                for url in webhook_urls:
                                    webhook = discord_webhook.DiscordWebhook(url=url)
                                    embed = discord_webhook.DiscordEmbed(
                                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                                        description=f"> ## Jester has arrived!\n<t:{int(time.time())}:R>\n\n{psURL.get()}",
                                        color="a352ff"
                                    )
                                    embed.set_author(name="Zen", icon_url="https://cm3t.github.io/biome_thumb/zen.png")
                                    embed.set_thumbnail(
                                        url="https://static.wikia.nocookie.net/sol-rng/images/d/db/Headshot_of_Jester.png/revision/latest?cb=20240630142936")
                                    webhook.add_embed(embed)
                                    webhook.set_content(f"<@{discID.get()}>")
                                    webhook.execute()
                        elif 'Eden has appeared' in line and "<" in line:
                            if multi_webhook.get() != "1":
                                webhook = discord_webhook.DiscordWebhook(url=webhookURL.get())
                                print(time.strftime('%H:%M:%S') + ": Eden has appeared somewhere in The Limbo.")
                                embed = discord_webhook.DiscordEmbed(
                                    timestamp=datetime.datetime.now(datetime.timezone.utc),
                                    description="> ## Eden has appeared somewhere in The Limbo.",
                                    color="000000"
                                )
                                embed.set_author(name="Zen", icon_url="https://cm3t.github.io/biome_thumb/zen.png")
                                embed.set_thumbnail(
                                    url="https://maxstellar.github.io/biome_thumb/eden.png")
                                webhook.add_embed(embed)
                                webhook.set_content(f"<@{discID.get()}>")
                                webhook.execute()
                            else:
                                print(time.strftime('%H:%M:%S') + ": Eden has appeared somewhere in The Limbo.")
                                for url in webhook_urls:
                                    webhook = discord_webhook.DiscordWebhook(url=url)
                                    embed = discord_webhook.DiscordEmbed(
                                        timestamp=datetime.datetime.now(datetime.timezone.utc),
                                        description="> ## Eden has appeared somewhere in The Limbo.",
                                        color="000000"
                                    )
                                    embed.set_author(name="Zen", icon_url="https://cm3t.github.io/biome_thumb/zen.png")
                                    embed.set_thumbnail(
                                        url="https://maxstellar.github.io/biome_thumb/eden.png")
                                    webhook.add_embed(embed)
                                    webhook.set_content(f"<@{discID.get()}>")
                                    webhook.execute()
            else:
                time.sleep(0.1)
        else:
            print("Roblox is closed, waiting for Roblox to start...")
            if multi_webhook.get() != "1":
                if "discord.com" not in webhookURL.get() or "https://" not in webhookURL.get():
                    popup("Invalid or missing webhook link.", "Error")
                    stop()
                    return
                close_webhook = discord_webhook.DiscordWebhook(url=webhookURL.get())
                close_embed = discord_webhook.DiscordEmbed(
                    description="**Roblox closed or crashed.**",
                    timestamp=datetime.datetime.now(datetime.timezone.utc))
                close_embed.set_author(name="Zen", icon_url="https://cm3t.github.io/biome_thumb/zen.png")
                close_webhook.add_embed(close_embed)
                close_webhook.execute()
            else:
                for url in webhook_urls:
                    close_webhook = discord_webhook.DiscordWebhook(url=url)
                    close_embed = discord_webhook.DiscordEmbed(
                        description="**Roblox closed or crashed.**",
                        timestamp=datetime.datetime.now(datetime.timezone.utc))
                    close_embed.set_author(name="Zen", icon_url="https://cm3t.github.io/biome_thumb/zen.png")
                    close_webhook.add_embed(close_embed)
                    close_webhook.execute()
            root.title("Zen [PAUSED]")
            while True:
                if not stopped:
                    root.update()
                else:
                    if not destroyed:
                        root.destroy()
                    sys.exit()
                check = is_roblox_running()
                if check:
                    break
                time.sleep(0.1)
            time.sleep(5)
            latest_log = get_latest_log_file()
            if not latest_log:
                logger.info("No log files found.")
                print("No log files found.")
                return
            with open(latest_log, 'r', encoding='utf-8') as file:
                print(f"Using log file: {latest_log}")
                print()
                logger.info(f"Using log file: {latest_log}")
                root.title("Zen [RUNNING]")
                check_for_hover_text(file)


def open_url(url):
    webbrowser.open(url, new=2, autoraise=True)


def auradetection_toggle_update():
    if aura_detection.get() == 1:
        popup("This feature is EXPERIMENTAL.\nThere are many limitations with aura detection.\n\nIt detects all auras "
              "that get equipped, so if you equip an aura yourself, it will get detected. Additionally, it will only "
              "detect auras that auto-equip.\n\nIt is also incapable of detecting dupes (for example, "
              "rolling Celestial with Celestial already equipped) or Overture: History, for some weird reason.",
              "Warning")
    config.set('Macro', 'aura_detection', str(aura_detection.get()))
    with open(config_name, 'w+') as configfile:
        config.write(configfile)


def init():
    global roblox_open, started

    if started:
        return

    webhook_field.configure(state="disabled", text_color="gray")
    ps_field.configure(state="disabled", text_color="gray")

    # write new settings to config
    config.set('Webhook', 'webhook_url', webhookURL.get())
    config.set('Webhook', 'private_server', psURL.get())

    # Writing our configuration file to 'example.ini'
    with open(config_name, 'w+') as configfile:
        config.write(configfile)

    # start webhook
    starting_embed = discord_webhook.DiscordEmbed(
        description="**Macro started!**\n-# Macro Version: v1.1.0",
        timestamp=datetime.datetime.now(datetime.timezone.utc))
    starting_embed.set_author(name="Zen", icon_url="https://cm3t.github.io/biome_thumb/zen.png")
    if multi_webhook.get() != "1":
        if "discord.com" not in webhookURL.get() or "https://" not in webhookURL.get():
            popup("Invalid or missing webhook link.", "Error")
            stop()
            return
        starting_webhook = discord_webhook.DiscordWebhook(url=webhookURL.get())
        starting_webhook.add_embed(starting_embed)
        starting_webhook.execute()
    else:
        for url in webhook_urls:
            starting_webhook = discord_webhook.DiscordWebhook(url=url)
            starting_webhook.add_embed(starting_embed)
            starting_webhook.execute()

    started = True

    # start detection
    if is_roblox_running():
        roblox_open = True
        logger.info("Roblox is open.")
        print("Roblox is open.")
        root.title("Zen [RUNNING]")
    else:
        logger.info("Roblox is closed, waiting for Roblox to start...")
        print("Roblox is closed, waiting for Roblox to start...")
        root.title("Zen [PAUSED]")
        while True:
            if not stopped:
                root.update()
            else:
                if not destroyed:
                    root.destroy()
                sys.exit()
            check = is_roblox_running()
            if check:
                break
            time.sleep(0.1)
    time.sleep(5)
    latest_log = get_latest_log_file()
    if not latest_log:
        logger.info(print("No log files found."))
        print("No log files found.")
        return
    with open(latest_log, 'r', encoding='utf-8') as file:
        print(f"Using log file: {latest_log}")
        print()
        logger.info(f"Using log file: {latest_log}")
        root.title("Zen [RUNNING]")
        check_for_hover_text(file)
        for line in file:
            if "[FLog::UpdateController] version response:" in line:
                found_update_version = True
                try:
                    json_data_start = line.find('{"version')
                    if json_data_start != -1:
                        json_data = json.loads(line[json_data_start:])
                        update_version = json_data.get("clientVersionUpload", "")
                        logger.info("Update version found: " + update_version)
                        print("Update version found: " + update_version)
                except:
                    print("Encountered error while parsing JSON to find Roblox update version.")
                    logger.error("Encountered error while parsing JSON to find Roblox update version.")
                    stop()
                if update_version == last_roblox_version and update_version != "":
                    pass
                else:
                    last_roblox_version = update_version
                    # write new version to config
                    config.set('Macro', 'last_roblox_version', last_roblox_version)
                    with open(config_name, 'w+') as configfile:
                        config.write(configfile)
                    apply_fast_flags(update_version)
            elif "Local character loaded:" in line and "Incoming MessageReceived Status:" not in line:
                try:
                    _, _, roblox_username = line.partition("Local character loaded: ")
                    roblox_username = roblox_username.strip()
                    logger.info("Username found: " + roblox_username)
                    print("Username found: " + roblox_username)
                    break
                except:
                    print("Encountered error finding username.")
                    logger.error("Encountered error finding username.")
                    stop()


def patch_roblox():
    global last_roblox_version
    if not started:
        popup('Start the macro by clicking the "Start" button before attempting to patch Roblox.', "Error")
    apply_fast_flags(last_roblox_version)

tabview.set("Webhook")

webhook_label = customtkinter.CTkLabel(tabview.tab("Webhook"), text="Webhook URL:",
                                       font=customtkinter.CTkFont(family="Segoe UI", size=20))
webhook_label.grid(column=0, row=0, columnspan=2, padx=(10, 0), pady=(5, 0), sticky="w")

webhook_field = customtkinter.CTkEntry(tabview.tab("Webhook"), font=customtkinter.CTkFont(family="Segoe UI", size=20),
                                       width=335, textvariable=webhookURL)
webhook_field.grid(row=0, column=1, padx=(144, 0), pady=(10, 0), sticky="w")
if multi_webhook.get() == "1":
    webhook_field.configure(state="disabled", text_color="gray")
    webhookURL.set("Multi-Webhook On")

ps_label = customtkinter.CTkLabel(tabview.tab("Webhook"), text="Private Server URL:",
                                  font=customtkinter.CTkFont(family="Segoe UI", size=20))
ps_label.grid(column=0, row=1, padx=(10, 0), pady=(20, 0), columnspan=2, sticky="w")

ps_field = customtkinter.CTkEntry(tabview.tab("Webhook"), font=customtkinter.CTkFont(family="Segoe UI", size=20),
                                  width=300, textvariable=psURL)
ps_field.grid(row=1, column=1, padx=(179, 0), pady=(23, 0), sticky="w")

discid_label = customtkinter.CTkLabel(tabview.tab("Webhook"), text="Discord User ID:",
                                      font=customtkinter.CTkFont(family="Segoe UI", size=20))
discid_label.grid(column=0, row=2, padx=(10, 0), pady=(20, 0), columnspan=2, sticky="w")

discid_field = customtkinter.CTkEntry(tabview.tab("Webhook"), font=customtkinter.CTkFont(family="Segoe UI", size=20),
                                      width=324, textvariable=discID)
discid_field.grid(row=2, column=1, padx=(155, 0), pady=(23, 0), sticky="w")

# patch_button = customtkinter.CTkButton(root, text="Patch",
#                                       font=customtkinter.CTkFont(family="Segoe UI", size=20, weight="bold"), width=75,
#                                       command=patch_roblox)
# patch_button.grid(row=1, column=3, padx=(5, 0), pady=(10, 0), sticky="w")

start_button = customtkinter.CTkButton(root, text="Start",
                                       font=customtkinter.CTkFont(family="Segoe UI", size=20, weight="bold"), width=75,
                                       command=init)
start_button.grid(row=1, column=0, padx=(10, 0), pady=(10, 0), sticky="w")


stop_button = customtkinter.CTkButton(root, text="Stop",
                                      font=customtkinter.CTkFont(family="Segoe UI", size=20, weight="bold"), width=75,
                                      command=stop)
stop_button.grid(row=1, column=2, padx=(5, 0), pady=(10, 0), sticky="w")


comet_pfp = customtkinter.CTkImage(dark_image=Image.open("cm3t.png"), size=(100, 100))
comet_pfp_label = customtkinter.CTkLabel(tabview.tab("Credits"), image=comet_pfp, text="")
comet_pfp_label.grid(row=0, column=0, padx=(10, 0), pady=(10, 0), sticky="w")

zen = customtkinter.CTkImage(dark_image=Image.open("zen.png"), size=(100, 100))
zen_label = customtkinter.CTkLabel(tabview.tab("Credits"), image=zen, text="")
zen_label.grid(row=0, column=1, padx=(10, 0), pady=(10, 0), sticky="w")

credits_frame = customtkinter.CTkFrame(tabview.tab("Credits"))
credits_frame.grid(row=0, column=2, padx=(10, 0), pady=(10, 0), sticky="w")

comet_label = customtkinter.CTkLabel(credits_frame, text="cm3t - Creator", font=customtkinter.CTkFont(family="Segoe UI", size=14, weight="bold"))
comet_label.grid(row=0, column=0, padx=(10, 0), sticky="nw")

comet_link = customtkinter.CTkLabel(credits_frame, text="GitHub", font=("Segoe UI", 14, "underline"), text_color="dodgerblue", cursor="pointinghand")
comet_link.grid(row=1, column=0, padx=(10, 0), sticky="nw")
comet_link.bind("<Button-1>", lambda e: open_url("https://github.com/cm3t"))

sniper_label = customtkinter.CTkLabel(credits_frame, text="Zen", font=customtkinter.CTkFont(family="Segoe UI", size=14, weight="bold"))
sniper_label.grid(row=2, column=0, padx=(10, 0), sticky="nw")

support_link = customtkinter.CTkLabel(credits_frame, text="v1.1.0", font=("Segoe UI", 14))
support_link.grid(row=3, column=0, padx=(10, 0), sticky="nw")
# support_link.bind("<Button-1>", lambda e: open_url("https://discord.gg/solsniper"))

detection_toggle = customtkinter.CTkCheckBox(tabview.tab("Macro"), text="Aura Detection [Experimental]",
                                             font=customtkinter.CTkFont(family="Segoe UI", size=20),
                                             variable=aura_detection, command=auradetection_toggle_update)
detection_toggle.grid(row=0, column=0, columnspan=2, padx=(10, 0), pady=(10, 0), sticky="w")

detectnotif_toggle = customtkinter.CTkCheckBox(tabview.tab("Macro"), text="Aura Notifications",
                                               font=customtkinter.CTkFont(family="Segoe UI", size=20),
                                               variable=aura_notif, command=auranotif_toggle_update)
detectnotif_toggle.grid(row=1, column=0, columnspan=2, padx=(10, 0), pady=(12, 0), sticky="w")

detectping_toggle = customtkinter.CTkCheckBox(tabview.tab("Macro"), text="Aura Pings",
                                              font=customtkinter.CTkFont(family="Segoe UI", size=20),
                                              variable=aura_ping, command=auraping_toggle_update)
detectping_toggle.grid(row=2, column=0, columnspan=2, padx=(10, 0), pady=(12, 0), sticky="w")

root.bind("<Destroy>", lambda event: x_stop())
root.bind("<Button-1>", lambda e: e.widget.focus_set())

root.mainloop()
