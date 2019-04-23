1. clone the knowmak git
```
git clone https://github.com/GateNLP/project-knowmak.git
cd project-knowmak/
```


2. change environment path in sample.setup
    - GCP_HOME : path to Gate GCP (https://gate.ac.uk/gcp/)
    - GATE_HOME: path to Gate8.5.1 (https://gate.ac.uk/download/), GATE and GCP are used for run preprocess pipeline, that create conll format output
    - KNOWMAK_GIT: path to project-knowmak local git repository
    - KNOWMAK_CORPORA: path to the corpora, one document per file, please check project-knowmak/gate/docs-test/06010.txt for example

3. add sample.setup to environment setting
```
source sample.setup
```

4. create a foler export4embeddings-outdir under project-knowmak root directory, this will contain preprocessed outputs
```
mkdir export4embeddings-outdir
```


5. Download sample essential from http://staffwww.dcs.shef.ac.uk/people/X.Song/sampleEssensial.zip, and place the unziped folder under project-knowmak root directory
```
wget http://staffwww.dcs.shef.ac.uk/people/X.Song/sampleEssensial.zip
unzip sampleEssensial.zip
```

6. run sample process, please set output path to /path/to/output/
```
bash run-sample.sh /path/to/output/
```











