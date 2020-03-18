
The `mpbn` Python module offers a simple implementation of reachability and attractor analysis in *Most Permissive Boolean Networks* ([arXiV:1808.10240][1]).

It is built on the `minibn` module from [colomoto-jupyter](https://github.com/colomoto/colomoto-jupyter) which allows importation of Boolean networks in many formats. See http://colomoto.org/notebook.

## Installation

### CoLoMoTo Notebook environment

`mpbn` is distributed in the [CoLoMoTo docker](http://colomoto.org/notebook).

### Using pip

#### Extra requirements
* [clingo](https://github.com/potassco/clingo) and its Python module

```
pip install mpbn
```

### Using conda
```
conda install -c colomoto -c potassco mpbn
```

## Documentation

Documentation is available at https://mpbn.readthedocs.io.

Examples are available at https://nbviewer.jupyter.org/github/pauleve/mpbn/tree/master/examples/


[1]: https://arxiv.org/abs/1808.10240
