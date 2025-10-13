# val
Extensions for [phy](https://github.com/cortex-lab/phy) manual curation

Types:
1. Time savers -> Reduce session fatigue
2. Statistical models -> Replace subjective splitting

## Introduction
Learn more about electrophysiology lab pipelines:
Quick [animation](/education/Intro%20to%20Phy.gif) or [pdf](/education/Intro%20to%20Phy.pdf)

![](/education/Intro%20to%20Phy.gif)

## Setup
1. Go to your global .phy folder (e.g. "C:\\Users\\me\\.phy")
2. Edit phy_config.py
```
c = get_config()
c.Plugins.dirs = ['My plugin directory'] # e.g. "C:\Users\me\.phy\plugins"
c.TemplateGUI.plugins = ['List of my plugins'] # e.g. 'Minimalist', 'Mergeall', 'Splitamp'
```
3. Create "plugins" folder (same path as c.Plugins.dirs)
4. Copy and paste plugins as .py files

For troubleshooting - [Read the Docs](https://phy.readthedocs.io/en/latest/customization)

## Plugins
* [**Minimalist**](/plugins/minimalist.py) - deactivate views in GUI (performance, decluttering)

* [**Mergeall**](/plugins/mergeall.py) - lazy merge button for all non-noise clusters (rare case)

-----------------------------------------------------------------------------------------------------

* [**Splitamp**](/plugins/splitamp.py) - split button for outliers in AmplitudeView

* [**Splitfeature**](/plugins/splitfeature.py) - split button for outliers or clusters in FeatureView

* [**Splitfeatureprompt**](/plugins/splitfeature.py) - "Splitfeature" with prompt-based arguments

more to come...

## Accessories
Separate python script for pre-phy modifications (must activate phy env)
* [**Peak to trough amplitude**](/accessories/peak_trough.py) - replace original amplitudes.npy (L2 norm of spike features) as new 'template' in AmplitudeView

## Customization
Create your own phy plugins with source [examples](https://phy.readthedocs.io/en/latest/plugins)

And more examples from other users [Julie-Fabre](https://github.com/Julie-Fabre/phyPlugins) and [petersenpeter](https://github.com/petersenpeter/phy2-plugins)

## Funding
CHP Summer Research Award (2025)  
Special thanks to the Campus Honors Program at the University of Illinois Urbana-Champaign!
