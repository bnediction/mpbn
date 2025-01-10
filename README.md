
The `mpbn` Python module offers a simple implementation of reachability and attractor analysis (minimal trap spaces) in *Most Permissive Boolean Networks* ([doi:10.1038/s41467-020-18112-5](https://doi.org/10.1038/s41467-020-18112-5)). The `mpbn` Python module also offers a *Most Permissive* simulator, which provides trajectory sampling and computes attractor propensities (see paper [Variable-Depth Simulation of Most Permissive Boolean Networks](https://link.springer.com/chapter/10.1007/978-3-031-15034-0_7) for more details).

It is built on the `minibn` module from [colomoto-jupyter](https://github.com/colomoto/colomoto-jupyter) which allows importation of Boolean networks in many formats. See http://colomoto.org/notebook.

## Installation

### CoLoMoTo Notebook environment

`mpbn` is distributed in the [CoLoMoTo docker](http://colomoto.org/notebook).

### Using pip

```
pip install mpbn
```

### Using conda
```
conda install -c colomoto -c potassco -c daemontus mpbn
```

## Usage

### Command line

- Enumeration of fixed points and attractors:
```
mpbn -h
```

- Simulation:
```
mpbn-sim -h
```

### Python interface

Documentation is available at https://mpbn.readthedocs.io.

Example notebooks:
* https://nbviewer.org/github/bnediction/mpbn/tree/master/examples/
* http://doi.org/10.5281/zenodo.3719097

For the simulation:
* https://nbviewer.org/github/bnediction/mpbn/blob/master/examples/Simulation.ipynb


[1]: https://arxiv.org/abs/1808.10240
