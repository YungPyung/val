"""Only show first 2 principal components from the best channel in FeatureView

* Adapted from 'Customizing the feature view'
* https://phy.readthedocs.io/en/latest/plugins/

"""

import re
from phy import IPlugin, connect
from phy.cluster.views import FeatureView

def my_grid():
    """In the grid specification, 0 corresponds to the best channel, 1
    to the second best, and so on. A, B, C refer to the PC components."""
    s = """
    0A,0B
    """.strip()
    return [[_ for _ in re.split(' +', line.strip())] for line in s.splitlines()]


class Customfeatureview(IPlugin):
    def attach_to_controller(self, controller):
        @connect
        def on_view_attached(view, gui):
            if isinstance(view, FeatureView):
                # Change the specification of the subplots here.
                view.set_grid_dim(my_grid())