"""
Parent class of data visualizer

File structure:
{exp_home}
    - {attr1}_{val1}_{attr2}_{val2}...
    - {attr1}_{val1}_{attr2}_{val2}...


Usage: inside jupyter notebook
```
from kvis import Kvis


class MyVis(Kvis):
    
    def get_data(self, fn):
        exp_path = os.path.join(self._exp_home, fn)
        ...  # Fetch scalar or 1D-array data
    
    def plot(self, labels, mus, stds, title):
        ...  # Run plot


vis = MyVis(exp_home, prefix)
vis.run()
```

"""


import os
import copy
import numpy as np
import ipywidgets as widgets
import matplotlib.pyplot as plt


class Kvis:
    
    def __init__(self, exp_home : str, prefix : str=''):
        """
        exp_home: string, directory to experimental data, filename
                 must be arranged by {attr1}_{val1}_{attr2}_{val2}...
        prefix: filename prefix for selection
        """
        self._exp_home = exp_home
        self._fns = [f for f in os.listdir(exp_home) if f.startswith(prefix)]
        self._entries = []
        for fn in self._fns:
            dat = self._parse_fn(fn)
            if dat is not None:
                self._entries.append(dat)
        
        print(f'{len(self._entries)} experiments loaded.')
        val_dict = self._get_val_dict()
        for k, v in val_dict.items():
            print(k, ':')
            print('  ', ' '.join(v))
    
    def get_data(self, fn : str):
        """
        To be overwritten by descendant class. Fetch visualization data 
        from experiment and check validity. If invalid, return None.
        fn: filename of the target experiment.
        """
        raise NotImplementedError
    
    def plot(self, labels, mus, stds):
        """
        To be overwritten by descendant class. Plot style and parameters set up.
        """
        raise NotImplementedError
        
    def _parse_fn(self, fn : str):
        """
        Extract data from experiment and organize condition parameters.
        """
        s = fn.split('_')
        attrs = s[0::2]
        vals = s[1::2]
        parse_dict = {attrs[i]: vals[i] for i in range(len(attrs))}
        parse_dict['filename'] = fn
        data = self.get_data(fn)
        if data is not None:
            parse_dict['data'] = data
            return parse_dict
        else:
            return None
        
    def _get_val_dict(self, ):
        """
        Return the dictionary containing all possible values of all parameters.
        """
        val_dict = {}
        for e in self._entries:
            for k, v in e.items():
                if k not in ['data', 'filename']:
                    if k not in val_dict:
                        val_dict[k] = []
                    if v not in val_dict[k]:
                        val_dict[k].append(v)
                        val_dict[k].sort()
        return val_dict
    
    def _filter_entry(self, entries, attr, val):
        """
        Filter entry by attribute values.
        """
        outputs = []
        for e in entries:
            if e[attr] == val:
                outputs.append(e)
        return outputs
    
    def _get_label(self, attrs : list, vals : list):
        """
        Generate the label string for a parameter set.
        attrs: [attr1, attr2, ...]
        vals: [val1, val2, ...]
        """
        output = ''
        for i in range(len(attrs)):
            output += attrs[i]
            output += ' = '
            output += vals[i]
            if i != len(attrs) - 1:
                output += ', '
        return output
    
    def get_plot_data(self, scan_attrs, filters=[]):
        """
        Generate raw data for plotting.
        scan_attrs: list of attribute names to be iterated through all combinations
        filters: [(attr1, val1), (attr2, val2), ...]
        """
        temp_entries = copy.deepcopy(self._entries)
        plot_title = None
        filter_keys = [f[0] for f in filters]
        if len(filters) > 0:
            for a, v in filters:
                temp_entries = self._filter_entry(temp_entries, a, v)
            plot_title = self._get_label(filter_keys, [f[1] for f in filters])

        scan_dict = {}
        for a in filter_keys:
            if a in scan_attrs:
                scan_attrs.remove(a)
        for e in temp_entries:
            label = self._get_label(scan_attrs, [e[a] for a in scan_attrs])
            if label not in scan_dict:
                scan_dict[label] = []
            scan_dict[label].append(e['data'])

        labels = []
        mus = []
        stds = []
        for label, data in scan_dict.items():
            mu = np.mean(data, axis=0)
            sigma = np.std(data, axis=0)
            labels.append(label)
            mus.append(mu)
            stds.append(sigma)
        mus = np.array(mus)
        stds = np.array(stds)

        # sort
        if len(mus.shape) == 1:
            zipped = zip(mus, stds, labels)
            zipped = sorted(zipped)
            mus, stds, labels = zip(*zipped)

        return labels, mus, stds

    def plot_bar(self, labels, mus, stds, x_label=None, y_label=None, title=None):
        ax = plt.gca()
        ax.cla()
        ax.bar(labels, mus, yerr=stds)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(title)

    def plot_curve(self, labels, mus, stds,
                   x_label=None, y_label=None, title=None):
        ax = plt.gca()
        ax.cla()
        xs = np.arange(mus.shape[1])
        for i, l in enumerate(labels):
            mu = mus[i]
            std = stds[i]
            ax.fill_between(xs, mu-std, mu+std, alpha=0.3)
            ax.plot(xs, mu, label=l)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.set_title(title)
        
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend()
    
    def run(self, scan_attrs, filters=[]):
        """
        Run visualization.
        scan_attrs: list of attribute names to be iterated through all combinations
        filters: [(attr1, val1), (attr2, val2), ...]
        """
        plot_data = self.get_plot_data(scan_attrs, filters)
        self.plot(*plot_data)

    def run_jupyter(self):
        fig, ax = plt.subplots(figsize=(6, 4))

        fields = {}
        val_dict = self._get_val_dict()
        for attr, vals in val_dict.items():
            widget_args = {
                'options': ['Avg', 'All'] + vals,
                'description': attr,
                'disabled': False,
                'layout': {'width': 'auto'},
            }
            fields[attr] = widgets.ToggleButtons(**widget_args)

        @widgets.interact(**fields)
        def update(**param_dict):
            scan_attrs = []
            filters = []
            for k, v in param_dict.items():
                if v == 'All':
                    scan_attrs.append(k)
                elif v != 'Avg':
                    filters.append((k, v))
            plot_data = self.get_plot_data(scan_attrs, filters)
            self.run(scan_attrs, filters)
