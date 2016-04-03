from setuptools import setup, find_packages

setup(
    name = "props",
    version = "1.0",
    packages = find_packages(),
    data_files = [('berkeleyparser', ['berkeleyparser/BerkeleyParser-1.7.jar', 'berkeleyparser/eng_sm6.gr']),
		  ('./', ['raising_subj_verbs.txt']),
		  ('dependency_tree', ['dependency_tree/stanford-corenlp-3.3.1.jar'])]
)
