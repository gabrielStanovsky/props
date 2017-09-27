<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [What is PropS?](#what-is-props)
  - [Light-weight Installation](#light-weight-installation)
  - [Full Installation (with Berkeley Parser)](#full-installation-with-berkeley-parser)
    - [Prerequisites](#prerequisites)
    - [Testing](#testing)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# What is PropS?

PropS offers an output representation designed to explicitly and uniformly express much of the proposition structure which is implied from syntax.

Semantic NLP applications often rely on dependency trees to recognize major elements of the proposition structure of sentences. 
Yet, while much semantic structure is indeed expressed by syntax, many phenomena are not easily read out of dependency trees, often leading to further ad-hoc heuristic post-processing or to information loss. 
For that end, PropS post-processes dependency trees to present a compelling representation for downstream tasks.

Find more details, examples, and an online demo at the [project page](http:/www.cs.biu.ac.il/~stanovg/props.html).

## Light-weight Installation
[See instructions here](PIPELINE.md).

## Full Installation (with Berkeley Parser)

Run 'sudo -E python ./setup.py install' from the props root directory.
This will install several python packages and other resources which PropS uses and relies upon (see [requirements.txt](props/install/requirements.txt) and [install.sh](props/install/install.sh) for the complete list).

MacOS users might run into issues installing JPype. An instruction to manually install JPype on MacOS can be found on the [berkely parser python interface repository](https://github.com/emcnany/berkeleyinterface#installation-and-dependencies).

### Prerequisites

* python 2.7
* java 7 (make sure to set the JAVA_HOME enviroment variable (e.g., /usr/lib/[*your_java_folder*])

### Testing 

Run 'python ./unit_tests/sanity_test.py'


