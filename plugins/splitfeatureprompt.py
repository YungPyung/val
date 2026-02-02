"""Split outliers or clusters in FeatureView with custom args

- for outliers: Isolation Forest
- for clusters: Gaussian Mixture Model
- based on first two PC features

For customization:
- define new algorithms below
- then change line 59 (outliers) or line 81 (clusters)

"""

from phy import IPlugin, connect
from phy.cluster.views import FeatureView
from phy.gui import input_dialog
# For type hinting
from phy.apps.template import TemplateController as ctrl

# Outliers
def isolation_forest(x, contamination=0.005):
    from sklearn.ensemble import IsolationForest
    raw_labels = IsolationForest(contamination=contamination, random_state=0).fit_predict(x)
    return raw_labels.clip(min=0, out=raw_labels)

# Too slow
#def elliptical_envelope(x):
    #from sklearn.covariance import EllipticEnvelope
    #raw_labels = EllipticEnvelope(contamination=0.005, random_state=0).fit_predict(x)
    #return raw_labels.clip(min=0, out=raw_labels)

# Clusters
def gaussian_mixture(x, n_components=2):
    from sklearn.mixture import GaussianMixture
    return GaussianMixture(n_components=n_components, random_state=0).fit_predict(x)

#def k_means(x):
    #from sklearn.cluster import KMeans
    #return KMeans(n_clusters=2, random_state=0).fit_predict(x)


class Splitfeatureprompt(IPlugin):
    def attach_to_controller(self, controller: ctrl):
        @connect
        def on_view_attached(view, gui):
            if isinstance(view, FeatureView):
                @view.dock.add_button(icon='f110')
                def outlier_split_button(checked):
                    # Prompt for the contamination value
                    contamination = input_dialog(
                        title="Set Contamination Value",
                        sentence="Enter the contamination value for Isolation Forest:",
                        text="0.005"  # Default value
                    )
                    contamination = float(contamination[0])

                    cluster_id = controller.supervisor.selected[0] # _get_features expects a hashable cluster_id

                    # Load features of all spikes of cluster on best channel
                    bunchs = controller._get_features(cluster_id=cluster_id, load_all=True)
                    
                    spike_ids = bunchs.spike_ids # For splitting
                    
                    # Choose first two features
                    y = bunchs.data[:,0,:2]
                    y = y.reshape((-1, 2))

                    # Fit predict
                    labels = isolation_forest(y, contamination)

                    assert spike_ids.shape == labels.shape

                    # Split
                    controller.supervisor.actions.split(spike_ids, labels)

                @view.dock.add_button(icon='f042')
                def cluster_split_button(checked):
                    n_components = input_dialog(
                        title="Set Components Value",
                        sentence="Enter the components value for Gaussian Mixture:",
                        text="2"  # Default value
                    )
                    n_components = int(n_components[0])
                    cluster_id = controller.supervisor.selected[0] # _get_features expects a hashable cluster_id
    
                    # Load features of all spikes of cluster on best channel
                    bunchs = controller._get_features(cluster_id=cluster_id, load_all=True)
                    
                    spike_ids = bunchs.spike_ids # For splitting
                    
                    # Choose first two features
                    y = bunchs.data[:,0,:2]
                    y = y.reshape((-1, 2))

                    # Fit predict
                    labels = gaussian_mixture(y, n_components)

                    assert spike_ids.shape == labels.shape

                    # Split
                    controller.supervisor.actions.split(spike_ids, labels) 
                