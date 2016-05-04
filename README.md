What is PropS?
------------
PropS offers an output representation designed to explicitly and uniformly express much of the proposition structure which is implied from syntax.

Semantic NLP applications often rely on dependency trees to recognize major elements of the proposition structure of sentences. 
Yet, while much semantic structure is indeed expressed by syntax, many phenomena are not easily read out of dependency trees, often leading to further ad-hoc heuristic post-processing or to information loss. 
For that end, PropS post-processes dependency trees to present a compelling representation for downstream tasks.

Find more details, examples, and an online demo at the [project page](http:/www.cs.biu.ac.il/~stanovg/props.html).


Installation
------------
Run 'python ./setup.py install' from the props root directory.
This will install several python packages and other resources which PropS uses and relies upon (see [requirements.txt](props/install/requirements.txt) and [install.sh](props/install/install.sh) for the complete list).

Prerequisites
-------------

* python 2.7
* java 7 (make sure to set the JAVA_HOME enviroment variable (e.g., /usr/lib/[*your_java_folder*])

Testing 
-------

Run 'python ./unit_tests/sanity_test.py'


