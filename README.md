1. clone the knowmak git and change to embedding-enrichment branch
```
git clone https://github.com/GateNLP/project-knowmak.git
cd project-knowmak/
```


2. change environment path in sample.setup
    - GCP_HOME : path to Gate GCP (https://gate.ac.uk/gcp/)
    - GATE_HOME: path to Gate, GATE and GCP are used for run preprocess pipeline, that create conll format output
    - KNOWMAK_GIT: path to konwmak-doc2onto-semsim local git repository
    - KNOWMAK_CORPORA: path to the corpora, one document per file, please check knowmak-doc2onto-semsim/gate/docs-test/06010.txt for example

3. add sample.setup to environment setting
```
source sample.setup
```

4. create a foler export4embeddings-outdir under knowmak-doc2onto-semsim root directory, this will contain preprocessed outputs
```
mkdir export4embeddings-outdir
```


5. Download sample essential from http://staffwww.dcs.shef.ac.uk/people/X.Song/sampleEssensial.zip, and place the unziped folder under knowmak-doc2onto-semsim root directory
```
wget http://staffwww.dcs.shef.ac.uk/people/X.Song/sampleEssensial.zip
unzip sampleEssensial.zip
```

6. run sample process, please set output path to /path/to/output/
```
bash run-sample.sh /path/to/output/
```











