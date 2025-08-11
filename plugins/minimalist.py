"""Prevent unwanted views from instantiating

- only edit the minimal_list
- use 'phy template-gui params.py --debug' to check accurate listing
- not permanent if plugin removed

"""

from phy import IPlugin, connect

class Minimalist(IPlugin):
    def attach_to_controller(self, controller):
        
        # Print the default views
        default_list = list(controller.view_creator)
        print(f"Default views: {default_list}")
        
        # Edit here
        minimal_list = ['ClusterView', 'WaveformView', 'AmplitudeView', 'CorrelogramView', 'FeatureView'] 
        
        # Filter the views
        controller.view_creator = {
            view: method 
            for view, method in controller.view_creator.items()
            if view in minimal_list
        }

        print(f"Filtered views: {list(controller.view_creator)}")

    