"""Create a ClusterQualityView

- define cluster quality function for only good clusters from ClusterView
- view plugin starts line 322
- core plugin line 356
    - color blue if threshold met for isolation distance and contamination rate
    - line 385: q > 20.0 and c < 0.1

- saves "cluster_is_quality.tsv" with id and true/false (is_quality)

"""

from phy import IPlugin, connect
from phy.cluster.supervisor import ClusterView
from phylib.io.model import save_metadata

from phy.apps.template import TemplateController as ctrl

import numpy as np
import logging

logger = logging.getLogger('phy')


def masked_cluster_quality(spike_clusters, spike_templates, pc_features, pc_feature_ind, cluster_ids):
    """
    Compute cluster quality metrics (Quality & Contamination)

    ** Python translated from https://github.com/cortex-lab/sortingQuality **
    
    Inputs:

    spike_clusters: array of shape (n_spikes,)
    pc_features: array of shape (n_spikes, n_channels, n_fet_per_chan) [different from kilosort]
    pc_feature_ind: array of shape (n_templates, n_channels)
    
    """

    print('..building feature matrix from clusters')
    spike_clusters = np.asarray(spike_clusters).flatten()
    spike_templates = np.asarray(spike_templates).flatten()
    cluster_ids = np.asarray(cluster_ids).flatten()
    pc_features = np.asarray(pc_features)
    pc_feature_ind = np.asarray(pc_feature_ind)

    # Extract data for good spikes only
    good_mask = np.isin(spike_clusters, cluster_ids)
    
    spike_clusters = spike_clusters[good_mask]
    spike_templates = spike_templates[good_mask]
    pc_features = pc_features[good_mask]

    # Transpose Phy feature array to match expected shape
    # (n_spikes, n_channels, n_pcs) to (n_spikes, n_pcs, n_channels)
    pc_features = np.transpose(pc_features, (0, 2, 1))

    cluster_ids = np.unique(spike_clusters)
    n_clusters = len(cluster_ids)
    n_spikes = len(spike_clusters)
    n_fet = 4 # Number of best channels
    n_fet_per_chan = pc_features.shape[1] # Number of PCs
    
    new_fet = np.zeros((n_spikes, n_fet_per_chan, n_fet))
    new_fet_inds = np.zeros((n_clusters, n_fet), dtype=int)
    
    # Construct a new pc_features based on clusters from curation
    for c, this_id in enumerate(cluster_ids):
        
        # Extract unique templates in this cluster
        these_spikes = (spike_clusters == this_id)
        these_templates = spike_templates[these_spikes]
        clu_temps, count = np.unique(these_templates, return_counts=True)
        
        # Extract template with highest spike detection count
        this_template = clu_temps[np.argmax(count)]
        
        # Save (4 best) channels for this template
        these_chans = pc_feature_ind[this_template, :n_fet]

        new_fet_inds[c, :] = these_chans
    
        # For this best channel
        for f in range(n_fet):
            
            # Get boolean map of this channel within all templates
            this_chan_inds = (pc_feature_ind == these_chans[f])
            
            # Extract row indices and column indices
            temps_with_this_chan, chan_inds = np.nonzero(this_chan_inds)
            
            # Extract template (indices) in the same cluster
            clu_temps_with_this_chan = np.nonzero(np.isin(clu_temps, temps_with_this_chan))[0]

            # For this template (same as t_idx)
            for t_idx in clu_temps_with_this_chan:
                
                this_sub_temp = clu_temps[t_idx]

                # Extract this channel idx within this template
                this_t_chan_ind = chan_inds[temps_with_this_chan == this_sub_temp]

                # Remove extra dimension
                if len(this_t_chan_ind) > 0:
                    this_t_chan_ind = this_t_chan_ind[0]
                
                # Get boolean map of (this cluster) spikes in this template
                spikes_mask = these_spikes & (spike_templates==this_sub_temp)

                # Save features on this channel
                new_fet[spikes_mask, :, f] = pc_features[spikes_mask, :, this_t_chan_ind]

    pc_features = new_fet
    pc_feature_ind = new_fet_inds

    assert pc_features.ndim == 3
    
    print('..computing cluster qualities')
    # The rest of your functions (masked_cluster_quality_sparse, etc.) remain unchanged
    return masked_cluster_quality_sparse(spike_clusters, pc_features, pc_feature_ind, cluster_ids)

def masked_cluster_quality_sparse(clu, fet, fet_inds, ids):

    clu = np.asarray(clu).flatten()
    fet = np.asarray(fet)
    fet_inds = np.asarray(fet_inds)
    cluster_ids = np.unique(ids)

    # Number of best channels
    fet_n_chans = min(4, fet_inds.shape[1])
        
    # Extract dimensions
    n_fet_per_chan = fet.shape[1]
    fet_n = fet_n_chans * n_fet_per_chan
    N = clu.size
    
    assert fet_n_chans <= fet.shape[2] and fet.shape[0] == N, 'bad input(s)'

    # Initialize output
    unit_quality = np.zeros(cluster_ids.size)
    contamination_rate = np.zeros(cluster_ids.size)

    print(f"{'ID':>12}\tQuality\tContamination")

    ## Main code

    # For this cluster
    for c_idx, c_id in enumerate(cluster_ids):
        
        # Extract spike mask for this cluster
        these_sp = (clu == c_id)
        n = np.count_nonzero(these_sp)
        
        if n < fet_n or n >= N / 2:
            # Cannot compute mahalanobis distance 
            # If less data points than dimensions
            # Or > 50% of all spikes are in this cluster

            unit_quality[c_idx] = 0.0
            contamination_rate[c_idx] = np.nan

            continue
        
        # Save features in this cluster (transpose to match core function)
        fet_this_cluster = fet[these_sp, :, :fet_n_chans].transpose(0, 2, 1).reshape(n, -1)
        
        ## Secondary code

        # Extract best channels in this cluster
        these_chans = fet_inds[c_idx, :fet_n_chans].flatten()
        
        # Initialize
        ## List is faster than numpy array for appending before concatenating
        fet_other_clusters_list = []
        
        # For this other cluster (c2)
        # Save features for each channel shared with the current cluster (c)
        for c2_idx, c2_id in enumerate(cluster_ids):

            if c2_idx != c_idx:
                chans_c2_has = fet_inds[c2_idx, :].flatten()
                
                # If c2 shares any channels with c
                if np.any(np.isin(chans_c2_has, these_chans)):
                    these_other_spikes = (clu == c2_id)
                    n_other_spikes = np.count_nonzero(these_other_spikes)
                    
                    # Skip if no spikes
                    if n_other_spikes == 0:
                        continue
                        
                    # Preallocate
                    ## Zero padding is also used in MATLAB
                    c2_fet = np.zeros((n_other_spikes, n_fet_per_chan, fet_n_chans))
                    
                    # For this c channel
                    for f_idx, chan in enumerate(these_chans):

                        # If it is shared with c2
                        if chan in chans_c2_has:

                            # Extract c2 channel idx
                            this_c_fet_ind = np.flatnonzero(chans_c2_has == chan)[0]

                            # Save c2 feature
                            c2_fet[:, :, f_idx] = fet[these_other_spikes, :, this_c_fet_ind]
                    
                    fet_other_clusters_list.append(c2_fet)
                    
        # Combine all other clusters' features
        if len(fet_other_clusters_list) > 0:
            fet_other_clusters = np.concatenate(fet_other_clusters_list, axis=0)
        else:
            fet_other_clusters = np.zeros((0, n_fet_per_chan, fet_n_chans))
            
        # Save    
        fet_other_clusters = fet_other_clusters.transpose(0, 2, 1).reshape(fet_other_clusters.shape[0], -1)

        uq, cr = masked_cluster_quality_core(fet_this_cluster, fet_other_clusters)

        unit_quality[c_idx] = uq
        contamination_rate[c_idx] = cr

        print(f'Cluster {c_id:3d}: \t{uq:6.1f}\t{cr:6.2f}')

        #if uq > 1000:
            #print('Unit quality > 1000')
            #breakpoint()
            #print('Execution resumed')
    
    return cluster_ids, unit_quality, contamination_rate


def masked_cluster_quality_core(fet_this_cluster, fet_other_clusters):
    """
    Computes the Mahalanobis-based quality and contamination metrics.

    *without scipy
    """
    n = fet_this_cluster.shape[0]
    n_other = fet_other_clusters.shape[0]
    n_fet = fet_this_cluster.shape[1]
    
    if n_other > n and n > n_fet:
        # Mahalanobis distance of each of the spikes from present cluster
        md = mahal(fet_other_clusters, fet_this_cluster)
        md.sort()
        
        md_self = mahal(fet_this_cluster, fet_this_cluster)
        md_self.sort()
        
        # md(n) in MATLAB
        unit_quality = md[n-1]
        
        pos = tipping_point(md_self, md)
        contamination_rate = 1.0 - (pos / len(md_self))
    else:
        unit_quality = 0.0
        contamination_rate = np.nan
        
    return unit_quality, contamination_rate


def tipping_point(x, y):
    """
    Finds the minimal pos such that sum(x > x(pos)) <= sum(y < x(pos)).
    x and y must be sorted ascending arrays of positive numbers.
    """
    nx = len(x)
    
    # MATLAB[~, inds] = sort([x; y])
    combined = np.concatenate([x, y])
    # MATLAB's sort is stable (matters for rank calculations with ties)
    inds = np.argsort(combined, kind='stable')
    
    # [~, inds] = sort(inds)
    ranks = np.argsort(inds, kind='stable')
    
    # xInds = inds(1:nX)
    # Extract ranks for elements originally in x
    # Add 1 for MATLAB index
    x_inds = ranks[:nx] + 1 
    
    # xInds' - (1:nX)
    # Number of y's that are less than that value of x
    y_less_than_x = x_inds - np.arange(1, nx + 1)
    
    # nX:-1:1
    # This represents sum(x > x(pos))
    x_greater_than_pos = np.arange(nx - 1, -1, -1)
    
    # Find first index where
    condition = x_greater_than_pos < y_less_than_x
    
    if np.any(condition):
        # np.argmax on a boolean array finds the index of the first True.
        # MATLAB: find(..., 1) - 1
        pos = np.argmax(condition)
    else:
        # Not a single "other" spike was nearer the cluster than the furthest in-cluster spike
        pos = nx  # will give contaminationRate = 0
        
    return pos


def mahal(Y, X):
    """
    Mimics MATLAB's mahal(Y, X) by returning the squared Mahalanobis distance 
    of each observation in Y to the reference sample X.
    """
    # MATLAB cov uses ddof=1 by default for sample covariance
    cov_x = np.cov(X, rowvar=False, ddof=1)
    
    # Use pseudo-inverse for numerical stability MATLAB
    inv_cov_x = np.linalg.pinv(cov_x)
    
    mean_x = np.mean(X, axis=0)
    diff = Y - mean_x
    
    # Efficiently compute the diagonal of (diff @ inv_cov_x @ diff.T)
    md2 = np.sum(np.dot(diff, inv_cov_x) * diff, axis=1)
    
    return md2


class ClusterQualityView(ClusterView):
    """Custom view that will only show 'id', 'iso', and 'contam'."""

    # Override the parent's required columns to prevent 'n_spikes' from being forced
    _required_columns = ()

    # Append custom CSS to color rows blue based on the data-is_quality attribute
    _styles = ClusterView._styles + """
        table tr[data-is_quality='true'] {
            color: #007bff; /* bright blue */
        }
    """

    def _reset_table(self, data=None, columns=(), sort=None):
        """Override to inject the custom 'is_quality' attribute into the HTML rows."""
        from phylib.utils import emit
        emit(self._view_name + '_init', self)
        
        if 'id' in columns:
            columns.remove('id')
        columns = ['id'] + list(columns)
        
        # By adding `{'data': ['is_quality']}` to value_names, the javascript 
        # table backend will insert `data-is_quality="true|false"` into each <tr> tag.
        value_names = columns + [{'data': ['is_quality']}]
        
        sort = sort or ('id', 'asc')
        self._init_table(columns=columns, value_names=value_names, data=data, sort=sort)


    pass

class Clusterquality(IPlugin):
    def attach_to_controller(self, controller: ctrl):
        
        def compute_and_format():
            """
            Finds all 'good' clusters, computes the 'iso' and "contam" metrics,
            and formats the output for view
            """
            # Extract clusters currently labeled as 'good'
            good_cluster_ids = [
                cid for cid in controller.supervisor.clustering.cluster_ids
                if controller.supervisor.cluster_meta.get('group', cid) == 'good'
            ]

            # Get updated data
            spike_clusters = controller.supervisor.clustering.spike_clusters

            # Get static data
            spike_templates = controller.model.spike_templates
            fet = controller.model.sparse_features.data
            fet_inds = controller.model.sparse_features.cols
            
            # Run quality function (extraction from Kilosort path too slow)
            cluster_ids, quality, contam = masked_cluster_quality(spike_clusters, spike_templates, fet, fet_inds, good_cluster_ids)
            
            # Format data and assess good threshold
            formatted_data = []
            for cid, q, c in zip(cluster_ids, quality, contam):

                # Good if iso > 20 and contam < 0.1
                is_quality = 'true' if (q > 20.0 and c < 0.1) else 'false'
                
                formatted_data.append({
                    'id': cid, 
                    'iso': q, 
                    'contam': c,
                    'is_quality': is_quality  # Feeds into the HTML data attribute
                })

            return formatted_data
            
        def create_quality_view():
            # Compute initial data globally
            initial_data = compute_and_format()

            # Instantiate the view with metric columns
            view = ClusterQualityView(
                data=initial_data,
                columns=['id', 'iso', 'contam'],
                sort=('id', 'asc')
            )

            # Connect to the 'cluster' event 
            @connect(sender=controller.supervisor)
            def on_cluster(sender, up):
                # Because 'iso' depends on all good clusters
                # any clustering change requires recalculation
                new_data = compute_and_format()
                
                # Replace the table
                view.remove_all_and_add(new_data)

            return view
        

        # Register the new view
        controller.view_creator['ClusterQualityView'] = create_quality_view

        @connect
        def on_gui_ready(sender, gui):

            @connect(sender=gui)
            def on_request_save(sender):
                # Calculate
                current_data = compute_and_format()
                
                # Extract cluster_id and 'true'/'false'
                metadata = {row['id']: row['is_quality'] for row in current_data}
                
                # Define TSV in output path
                filename = controller.model.dir_path / 'cluster_is_quality.tsv'
                
                # Save
                # Because it starts with 'cluster_', phy will 
                # load this automatically as a custom label in future sessions
                save_metadata(filename, 'is_quality', metadata)
                logger.info(f"Saved {filename}")