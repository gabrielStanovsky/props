from setuptools import setup, find_packages
from setuptools.command.install import install as _install
from os import getcwd, chdir
import os, sys
from subprocess import call
from shutil import copyfile

class install(_install):
    def run(self):
        filesToCopy = ['raising_subj_verbs.txt',
                       'berkeleyparser/Berkeleyparser-1.7.jar',
                       'berkeleyparser/eng_sm6.gr',
                       'dependency_tree/stanford-corenlp-3.3.1.jar']
        
        _install.run(self)
        curdir = getcwd()
        chdir(self.install_lib)
        copyfile(os.path.join(curdir, 'raising_subj_verbs.txt'), os.path.join(getcwd(), 'raising_subj_verbs.txt'))
        
        chdir(curdir)



if sys.argv[1] == 'install':
    chdir('./props/')
    call('./install/install.sh')
    chdir('../')
        

        
setup(
    name = "props",
    version = "1.0",
    description = 'Proposition Extraction Tool',
    author = 'Gabriel Stanovsky, Jessica Ficler, Ido Dagan, Yoav Goldberg',
    author_email = 'gabriel.satanovsky@gmail.com',
    url = 'http://www.cs.biu.ac.il/~stanovg/props.html',
    packages = find_packages(),
#    cmdclass = {'install': install},
    data_files = [('props/berkeleyparser', ['props/berkeleyparser/BerkeleyParser-1.7.jar', 'props/berkeleyparser/eng_sm6.gr']),
                  ('props/', ['props/raising_subj_verbs.txt']),
                  ('props/dependency_tree', ['props/dependency_tree/stanford-corenlp-3.3.1.jar']),
    ]
)

