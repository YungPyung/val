"""Split outliers or clusters in FeatureView

- buttons ("1" for outliers, "2" for clusters)
- for outliers: Isolation Forest
- for clusters: Gaussian Mixture Model
- based on first two PC features

For customization:
- define new algorithms below
- then change line 59 (outliers) or line 81 (clusters)

"""

from phy import IPlugin, connect
from phy.cluster.views import FeatureView

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


class Splitfeature(IPlugin):
    def attach_to_controller(self, controller: ctrl):
        @connect
        def on_view_attached(view, gui):
            if isinstance(view, FeatureView):
                # Outliers
                # The icon unicode can be found at https://fontawesome.com/icons?d=gallery
                @view.dock.add_button(icon='f110')
                def outlier_split(checked):
                    # The checked argument is only used with buttons `checkable=True`
                    
                    cluster_id = controller.supervisor.selected[0] # _get_features expects a hashable cluster_id
    
                    # Load features of all spikes of cluster on best channel
                    bunchs = controller._get_features(cluster_id=cluster_id, load_all=True)
                    
                    spike_ids = bunchs.spike_ids # For splitting
                    
                    # Choose first two features
                    y = bunchs.data[:,0,:2]
                    y = y.reshape((-1, 2))

                    # Fit predict
                    labels = isolation_forest(y)

                    assert spike_ids.shape == labels.shape
                    controller.supervisor.actions.split(spike_ids, labels)

                # Clusters
                @view.dock.add_button(icon='f042')
                def cluster_split(checked):
                    # The checked argument is only used with buttons `checkable=True`
                    
                    cluster_id = controller.supervisor.selected[0] # _get_features expects a hashable cluster_id
    
                    # Load features of all spikes of cluster on best channel
                    bunchs = controller._get_features(cluster_id=cluster_id, load_all=True)
                    
                    spike_ids = bunchs.spike_ids # For splitting
                    
                    # Choose first two features
                    y = bunchs.data[:,0,:2]
                    y = y.reshape((-1, 2))

                    # Fit predict
                    labels = gaussian_mixture(y)

                    assert spike_ids.shape == labels.shape
                    controller.supervisor.actions.split(spike_ids, labels) 