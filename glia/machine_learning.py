from collections import namedtuple
from .pipeline import get_unit
import numpy as np

TVT = namedtuple("TVT", ['training', "validation", "test"])

def tvt_by_percentage(n, training=60, validation=20,testing=20):
    summed = training+validation+testing
    assert summed==100
    train = int(np.floor(n*training/100))
    valid = int(np.ceil(n*validation/100))
    test = n - valid - train
    return TVT(train, valid, test)

def f_split_dict(tvt):
    """Subset dict into training, validation, & test."""
    def anonymous(dictionary):
        i = 0
        split = TVT({},{},{})
        for k,v in dictionary.items():
            if i < tvt.training:
                split.training[k] = v
            elif i < tvt.validation + tvt.training:
                split.validation[k] = v
            elif i < tvt.test + tvt.validation + tvt.training:
                split.test[k] = v
            else:
                raise(ValueError, 'bad training, validation & test split.')
            i += 1
        assert i == tvt.training+tvt.validation+tvt.test
        return split
            
    return anonymous

def tvt_map(tvt, f):
    return TVT(f(tvt.training), f(tvt.validation), f(tvt.test))

def f_split_list(tvt, get_list=lambda x: x):
    """Subset list into training, validation, & test."""
    def anonymous(x):
        split = TVT([],[],[])
        my_list = get_list(x)
        for i,v in enumerate(my_list):
            if i < tvt.training:
                split.training.append(v)
            elif i < tvt.validation + tvt.training:
                split.validation.append(v)
            elif i < tvt.test + tvt.validation + tvt.training:
                split.test.append(v)
            else:
                raise(ValueError, 'bad training, validation & test split.')
        try:
            assert len(my_list) == tvt.training+tvt.validation+tvt.test
        except Exception as e:
            print(len(my_list), tvt.training+tvt.validation+tvt.test)
            raise e
        return split
            
    return anonymous


def units_to_ndarrays(units, get_class, get_list=lambda x: x):
    """Units::Dict[unit_id,List[Experiment]] -> (ndarray, ndarray)

    get_class is a function"""
    key_map = {k: i for i,k in enumerate(sorted(list(units.keys())))}
    unitListE = get_unit(units)[1]
    duration = unitListE[0]['stimulus']['lifespan']
    for l in unitListE:
        assert duration==l['stimulus']['lifespan']
    d = int(np.ceil(duration/120*1000)) # 1ms bins
    nE = len(unitListE)
    data = np.full((nE,d,len(key_map.keys())), 0, dtype=np.int8)
    classes = np.full(nE, np.nan, dtype=np.int8)

    for unit_id, value in units.items():
        listE = get_list(value)
        u = key_map[unit_id]
        for i,e in enumerate(listE):
            for spike in e['spikes']:
                s = int(np.floor(spike*1000))
                data[i,s,u] = 1
            stimulus = e["stimulus"]
            classes[i] = get_class(stimulus)
            

    return (data, classes)
                

def experiments_to_ndarrays(experiments, get_class=lambda x: x['metadata']['class']):
    """

    get_class is a function"""
    key_map = {k: i for i,k in enumerate(sorted(list(experiments[0]['units'].keys())))}
    duration = experiments[0]['lifespan']
    for l in experiments:
        assert duration==l['lifespan']
    d = int(np.ceil(duration/120*1000)) # 1ms bins
    nE = len(experiments)
    data = np.full((nE,d,len(key_map.keys())), 0, dtype=np.int8)
    classes = np.full(nE, np.nan, dtype=np.int8)

    for i,e in enumerate(experiments):
        for unit_id, spikes in e['units'].items():
            u = key_map[unit_id]
            for spike in spikes:
                s = int(np.floor(spike*1000))
                data[i,s,u] = 1
        classes[i] = get_class(e)
            

    return (data, classes)
                
