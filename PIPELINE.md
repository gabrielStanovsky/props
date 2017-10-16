<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Running PropS as part of a pipeline](#running-props-as-part-of-a-pipeline)
  - [Installation](#installation)
  - [Usage](#usage)
    - [Piping with CORENLP](#piping-with-corenlp)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# Running PropS as part of a pipeline

PropS now supports pipelining from a dependency parser which produces output
conforming with [Stanford's CORENLP json output format](https://stanfordnlp.github.io/CoreNLP/cmdline.html)<sup>1</sup>.
This allows for an independent, light-weight, and hopefully easier to install version of PropS.

## Installation

The prerequisites are the python packages in [requirements.txt](props/install/requirements.txt).

Run

```bash
pip install -r ./props/install/requirements.txt
```

## Usage
Use the new command line flag ```--corenlp-json-input``` and supply the json input either from STDIN or in 
file name as the first argument.

For example, try:

```bash
python props/applications/parse_props.py sample.json -t --oie --corenlp-json-input
```

See all command line options in [parse_props.py](props/applications/parse_props.py)

### Piping with CORENLP

We supply a [pipeline script](run_pipeline.sh) to interact with the CORENLP parser, assuming it is already installed, and that the
```CORENLP_HOME``` environment variable points to the CORENLP home folder containing all its jars.

To use it on a sample raw input file, try:
```
./run_pipeline.sh sample.txt
```

**NOTE**:
* We use the Stanford dependency format (not Universal Dependencies)
* We use the makeCopulaHead flag

<sup>1</sup>Specifically, we read the following keys from the json:
* tokens
* basicDependencies
