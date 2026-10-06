# KnotRD

KnotRD is a Python library for working with rectangular diagrams of knots and links. It is designed for computational knot theory, with particular emphasis on algorithms for simplifying rectangular diagrams and recognizing the unknot.

## Features

* Representation and manipulation of rectangular diagrams
* Simplification of rectangular diagrams
* Algorithms for removing various configurations from rectangular diagrams
* Conversion between different knot representations
* Computational experiments with knot diagrams
* Tools for studying unknot recognition

## Installation

Clone this repository:

```bash
git clone [KNOTRD_REPOSITORY_URL]
cd KnotRD
```

KnotRD requires Python 3.x.

The software also requires several external Python packages, including **GridPyM** and **SnapPy**.

### GridPyM

KnotRD uses the external Python package GridPyM. GridPyM is not part of this repository and was not written by the author of KnotRD.

Please install GridPyM separately following the installation instructions provided by its authors:

[https://github.com/dceloriamaths/GridPythonModule]

Please consult the GridPyM repository for its documentation and licensing information.

### SnapPy

While not required KnotRD also interfaces nicely with SnapPy for computations involving knots and links. This dependency is be required for any work with unknotting number.

[https://github.com/3-manifolds/SnapPy]

## Usage

The main functionality of KnotRD is contained in the Python files in this repository. Examples and computational experiments can be found in the numerous Jupyter notebook (.ipynb) files. 
To get started see: available_unknots.ipynb 

More detailed usage examples will be added as the software develops.

## Unknot Recognition

KnotRD includes an algorithm for recognizing the unknot using simplifications of rectangular diagrams.

The algorithm applies a sequence of diagrammatic moves designed to simplify the rectangular diagram without increasing its complexity. The current implementation includes procedures involving:

* removal of \(v1b\) configurations;
* push \(T\)-moves;
* hinge \(T\)-moves;
* rotations and cyclic permutations;
* other simplifications of rectangular diagrams.

The algorithm is described in more detail in the accompanying forthcoming research paper:

> TOWARDS A POLYNOMIAL TIME ALGORITHM FOR RECOGNIZING
THE UNKNOT 
by HONG CHANG, CAROLYN ENGELHARDT, SETH HOVLAND, WILLIAM MENASCO, MAYA
RODRIGUEZ, GREG VINAL

## Computational Experiments

The software has been tested on collections of knot diagrams and known difficult examples of the unknot.

Details about the datasets, experimental setup, and computational results will be provided in the accompanying paper.


## Repository Structure

A brief description of the main files and directories will be added here.

```text
KnotRD/
├── ...
├── ...
└── README.md
```

## Citation

If you use KnotRD in research, please cite:

> S. Hovland, *[Paper Title]*, [journal/arXiv information].

A BibTeX entry will be provided here.

## Acknowledgments

KnotRD uses the external Python package **GridPyM**, developed by its respective authors. We thank the authors of GridPyM for making this software available.
Some of the methods for representing grid diagrams and drawing rectangular diagrams were based on the excellent work by these authors. 

KnotRD also uses **SnapPy** for computations involving knots and 3-manifolds.

## Contact

Seth Hovland
University of Minnesota Duluth

[hovl0070 at d.umn.edu]
