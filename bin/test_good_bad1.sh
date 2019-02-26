#!/bin/bash

dir=/home/johann/knowmak-extras/resources/scoring/examples/

for cl in active_ageing carbon_footprint nanomedicine novel_composites public_communication transport
do
  echo Class $cl
  # good for embedding 01, 02, 03, then bad for embedding 01, 02, 03 each with and without altembs: 2*3*2=12 runs
  rm out_${cl}.tsv
  touch out_${cl}.tsv
  awk  'BEGIN{OFS="\t"}{print $0, "emb01", "good"}' < $dir/"${cl}"_good_terms.tsv | python python/scoring4terms.py -c 1  --simontos  -a -O results/1806/scoring4onto_01.pickle  -E /home/johann/embeddings/knowmak/series3/series3_01_ontoonly.gensim-model >> out_${cl}.tsv 
  awk  'BEGIN{OFS="\t"}{print $0, "emb02", "good"}' < $dir/"${cl}"_good_terms.tsv | python python/scoring4terms.py -c 1  --simontos  -a -O results/1806/scoring4onto_02.pickle  -E /home/johann/embeddings/knowmak/series3/series3_02_ontoonly.gensim-model >> out_${cl}.tsv
  awk  'BEGIN{OFS="\t"}{print $0, "emb03", "good"}' < $dir/"${cl}"_good_terms.tsv | python python/scoring4terms.py -c 1  --simontos  -a -O results/1806/scoring4onto_03.pickle  -E /home/johann/embeddings/knowmak/series3/series3_03_ontoonly.gensim-model >> out_${cl}.tsv
  awk  'BEGIN{OFS="\t"}{print $0, "emb01", "good"}' < $dir/"${cl}"_good_terms.tsv | python python/scoring4terms.py -c 1  --altembs --simontos  -a -O results/1806/scoring4onto_01.pickle  -E /home/johann/embeddings/knowmak/series3/series3_01_ontoonly.gensim-model >> out_${cl}.tsv
  awk  'BEGIN{OFS="\t"}{print $0, "emb02", "good"}' < $dir/"${cl}"_good_terms.tsv | python python/scoring4terms.py -c 1  --altembs --simontos  -a -O results/1806/scoring4onto_02.pickle  -E /home/johann/embeddings/knowmak/series3/series3_02_ontoonly.gensim-model >> out_${cl}.tsv
  awk  'BEGIN{OFS="\t"}{print $0, "emb03", "good"}' < $dir/"${cl}"_good_terms.tsv | python python/scoring4terms.py -c 1  --altembs --simontos  -a -O results/1806/scoring4onto_03.pickle  -E /home/johann/embeddings/knowmak/series3/series3_03_ontoonly.gensim-model >> out_${cl}.tsv
  awk  'BEGIN{OFS="\t"}{print $0, "emb01", "bad"}' < $dir/"${cl}"_bad_terms.tsv | python python/scoring4terms.py -c 1  --simontos  -a -O results/1806/scoring4onto_01.pickle  -E /home/johann/embeddings/knowmak/series3/series3_01_ontoonly.gensim-model >> out_${cl}.tsv          
  awk  'BEGIN{OFS="\t"}{print $0, "emb02", "bad"}' < $dir/"${cl}"_bad_terms.tsv | python python/scoring4terms.py -c 1  --simontos  -a -O results/1806/scoring4onto_02.pickle  -E /home/johann/embeddings/knowmak/series3/series3_02_ontoonly.gensim-model >> out_${cl}.tsv
  awk  'BEGIN{OFS="\t"}{print $0, "emb03", "bad"}' < $dir/"${cl}"_bad_terms.tsv | python python/scoring4terms.py -c 1  --simontos  -a -O results/1806/scoring4onto_03.pickle  -E /home/johann/embeddings/knowmak/series3/series3_03_ontoonly.gensim-model >> out_${cl}.tsv
  awk  'BEGIN{OFS="\t"}{print $0, "emb01", "bad"}' < $dir/"${cl}"_bad_terms.tsv | python python/scoring4terms.py -c 1  --altembs --simontos  -a -O results/1806/scoring4onto_01.pickle  -E /home/johann/embeddings/knowmak/series3/series3_01_ontoonly.gensim-model >> out_${cl}.tsv
  awk  'BEGIN{OFS="\t"}{print $0, "emb02", "bad"}' < $dir/"${cl}"_bad_terms.tsv | python python/scoring4terms.py -c 1  --altembs --simontos  -a -O results/1806/scoring4onto_02.pickle  -E /home/johann/embeddings/knowmak/series3/series3_02_ontoonly.gensim-model >> out_${cl}.tsv
  awk  'BEGIN{OFS="\t"}{print $0, "emb03", "bad"}' < $dir/"${cl}"_bad_terms.tsv | python python/scoring4terms.py -c 1  --altembs --simontos  -a -O results/1806/scoring4onto_03.pickle  -E /home/johann/embeddings/knowmak/series3/series3_03_ontoonly.gensim-model >> out_${cl}.tsv
done
