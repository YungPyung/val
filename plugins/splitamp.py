"""Split outliers in AmplitudeView

- button ("Hand")
- based on current amplitude type

for customization:
- define new algorithms below
- then change line 47

"""

from phy import IPlugin, connect
from phy.cluster.views import AmplitudeView

# For type hinting
from phy.apps.template import TemplateController as ctrl


def isolation_forest(x):
    from sklearn.ensemble import IsolationForest
    raw_labels = IsolationForest(contamination=0.005, random_state=0).fit_predict(x)
    return raw_labels.clip(min=0, out=raw_labels)

#def k_means(x):
    #from sklearn.cluster import KMeans
    #return KMeans(n_clusters=2, random_state=0).fit_predict(x)

class Splitamp(IPlugin):
    def attach_to_controller(self, controller:ctrl):
        @connect
        def on_view_attached(view, gui):
            if isinstance(view, AmplitudeView):
                # The icon unicode can be found at https://fontawesome.com/icons?d=gallery
                @view.dock.add_button(icon='f461')
                def amplitude_split(checked):
                    # Find amplitudes for selected clusters (only one cluster split in implementation)
                    cluster_ids = controller.supervisor.selected
                    amp_type = view.amplitudes_type
                    bunchs = controller._amplitude_getter(cluster_ids, name=amp_type, load_all=True)

                    # Extract data from only first cluster
                    spike_ids = bunchs[0].spike_ids
                    y = bunchs[0].amplitudes
                    y = y.reshape((-1,1))

                    # Fit predict
                    labels = isolation_forest(y)
                    assert spike_ids.shape == labels.shape

                    controller.supervisor.actions.split(spike_ids, labels)



