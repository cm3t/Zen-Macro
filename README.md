<div align="center" style="text-align: center;">
<h1><img src="zen.png" height="30px">  Zen</h1>
<p> A Sol's RNG Macro to track Biomes, Merchants and Auras.<br>I am building off of maxstellar's Biome Macro for Mac.</p>

![GitHub Downloads (all assets, all releases)](https://img.shields.io/github/downloads/cm3t/Zen-Macro/total)
![GitHub Release](https://img.shields.io/github/v/release/cm3t/Zen-Macro)
![GitHub License](https://img.shields.io/github/license/cm3t/Zen-Macro)

# How to install?
Go to **https://www.python.org/** and install the latest version of Python.
Then, open a console and navigate to the macro folder you just unzipped from the ZIP you downloaded.

Once there, type the following into your terminal:
`pip3 install -r requirements.txt`

If that doesn't work, try:
`pip install -r requirements.txt`

**If you want to enable Roll, Merchant and Eden detection (Patching Roblox):**
- Navigate to `/Applications/Roblox.app/Contents/MacOS/`
- Make a new directory called `ClientSettings`.
- In that directory, create a file called `ClientAppSettings.json`.
- In that file, paste in `{"FStringDebugLuaLogLevel": "debug", "FStringDebugLuaLogPattern": "ExpChat/mountClientApp"}` and save it.
- After that, restart the macro and Roblox if they are open.

Also, you should open `config.ini` and set **username_override** to **your roblox username**.
