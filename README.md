# val
Extensions for phy manual curation

## Setup
1. Go to your global .phy folder (e.g. "C:\\Users\\me\\.phy")
2. Edit phy_config.py
```
c = get_config()
c.Plugins.dirs = ['My plugin directory'] # e.g. "C:\Users\me\.phy\plugins"
c.TemplateGUI.plugins = ['List of my plugins'] # e.g. 'Minimalist', 'Gmsplit', 'Columns'
```
3. Create "plugins" folder (same path as c.Plugins.dirs)
4. Copy and paste plugins as .py files

Setup from [phy - Read the Docs](https://phy.readthedocs.io/en/latest/customization)

## Plugins
Inspired by [phy plugin examples](https://phy.readthedocs.io/en/latest/plugins)
* **Minimalist** - only views in Minimalist operate in GUI (performance, decluttering)

## Accessories
Separate python script for pre-phy modifications
* **Peak to trough amplitude** - replace amplitudes.npy (L2 norm of spike features)
