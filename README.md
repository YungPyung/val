# val
Extensions for phy manual curation

## Setup
1. Go to your global .phy folder (e.g. C:\Users\Me\.phy)
2. Edit phy_config.py
'''
c = get_config()
c.Plugins.dirs = ['My plugin directory'] # e.g. "C:\Users\Me\.phy\plugins"
c.TemplateGUI.plugins = ['List of plugins'] # e.g. 'Minimalist', 'Gmsplit', 'Columns'
'''
3. Create "plugins" folder (same path as c.Plugins.dirs)
4. Copy and paste plugins as .py files inside plugins folder

Source - https://phy.readthedocs.io/en/latest/plugins

## Plugins
* **Minimalist - only views in Minimalist exist in GUI (performance, decluttering)

## Accessories
separate python script for pre-phy modifications
* **Peak to trough amplitude - replace amplitudes.npy (L2 norm of spike features)
