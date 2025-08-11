
""" Merge all clusters with the same best channel.

- "globe" button in cluster view
- disregards noise clusters
- undo is available (once for each cluster merged)

"""  

from phy import IPlugin, connect  

# For type hinting
from phy.apps.template import TemplateController as ctrl

class Mergeall(IPlugin):
    def attach_to_controller(self, controller: ctrl):
        @connect
        def on_gui_ready(view, gui):
            # The icon unicode can be found at https://fontawesome.com/icons?d=gallery
            @controller.supervisor.cluster_view.dock.add_button(icon='f0ac', checkable=True)
            def merge_all(checked):
                @controller.supervisor.cluster_view.get_ids
                def get_clusters(cluster_ids):
                    # Find good, mua, unsorted clusters
                    cluster_ids = [id for id in cluster_ids 
                                    if controller.supervisor.cluster_meta.get(field='group', cluster=id) != 'noise']
                    
                    # Group clusters by best channel
                    cluster_groups = {}
                    for id in cluster_ids:
                        best_channel = controller.get_best_channel(id)  # memcached
                        if best_channel not in cluster_groups:
                            cluster_groups[best_channel] = []
                        cluster_groups[best_channel].append(id)

                    # Merge clusters in each group
                    for group in cluster_groups.values():
                        if len(group) > 1:
                            controller.supervisor.actions.merge(group)