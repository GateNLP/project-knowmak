#!/bin/bash
OUTPUT_FOLDER=$1

rm $KNOWMAK_GIT/gate/gazetteer/knowmak-ontology.gazbin
$KNOWMAK_GIT/bin/copy-tree-dirs $KNOWMAK_CORPORA $KNOWMAK_GIT/export4embeddings-outdir
$GCP_HOME/gcp-direct.sh -i $KNOWMAK_CORPORA -t 40 -x $KNOWMAK_GIT/gate/termraider-corpusstats3.xgapp
python $KNOWMAK_GIT/python/sampleDoc_single.py --corpusdir $KNOWMAK_GIT/export4embeddings-outdir --mwfile $KNOWMAK_GIT/sampleEssensial/multiword-ontology-only.tsv --embdfile $KNOWMAK_GIT/sampleEssensial/ontoonly.gensim-model --outputprefix $OUTPUT_FOLDER --originalDir $KNOWMAK_CORPORA --ontoJson $KNOWMAK_GIT/sampleEssensial/knowmak.json --ontoLst $KNOWMAK_GIT/sampleEssensial/knowmak-ontology.lst

