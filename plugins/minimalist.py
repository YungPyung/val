"""Prevent unwanted views from instantiating

minimal_list: list

- only edit the minimal_list
- use --debug to check accurate listing

"""

from phy import IPlugin, connect

class Minimalist(IPlugin):
    def attach_to_controller(self, controller):
        
        default_list = list(controller.view_creator)
        print(f"Default views: {default_list}")
        
        minimal_list = ['ClusterView', 'WaveformView', 'AmplitudeView', 'CorrelogramView', 'FeatureView'] 
        
        controller.view_creator = {
            view: method 
            for view, method in controller.view_creator.items()
            if view in minimal_list
        }

        print(f"Filtered views: {list(controller.view_creator)}")

    