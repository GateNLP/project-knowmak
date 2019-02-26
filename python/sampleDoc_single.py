import sys
from embeddingsutils import DirectoryCorpusConllDocLevel as DirectoryCorpusConll
from embeddingsutils import MultiWordUtils
from embeddingsutils import EmbeddingsUtils
from gensim.models import Word2Vec
import argparse
import numpy as np
import random
import torch
import sklearn
from nltk import wordpunct_tokenize
from nltk.corpus import stopwords as nltk_stopwords
from shutil import copyfile
import os
import json
from collections import defaultdict
import csv

label2groupid = {"Key Enabling Technology": "KET", "Societal Grand Challenge": "SGC",
                 "Mission": "Mission"}


added_sentences = 0
original_sentences = 0


def walk_ontology(ontoclasslist, groupid=None, parentclass=None, level=0):
    # algorithm: onto is a list of nodes
    # for each node in the list, we add all the leaf nodes for that node to a list
    # which gets then returned.
    # Whenever we recursively invoke this function, we also pass on the group label
    # (we set it for every node processed) and we pass on parent ui which is getting
    # added to the list of parent uris for each leaf node.
    leafclasses = []
    allclasses = []
    # print("Running at level", level, "for classes", [c["label"] for c in onto])
    for tmpclass in ontoclasslist:
        allclasses.append(tmpclass)
        # print("processing class", c["label"])
        # if we have a group id from the caller set it
        tmpclass["level"] = level
        if groupid:
            tmpclass["groupid"] = groupid
        # if the class is a leaf class, put it into leafclasses
        if len(tmpclass["children"]) == 0:
            # print("Is a leaf class")
            pcs = tmpclass.get("parentclasses")
            if not pcs:
                pcs = []
            if parentclass not in pcs:
                pcs.append(parentclass)
            tmpclass["parentclasses"] = pcs
            tmpclass["parenturis"] = [pc["URI"] for pc in pcs]
            leafclasses.append(tmpclass)
        else:
            # print("is not a leaf class")
            if level == 0:
                groupid = label2groupid[tmpclass["label"]]
            if level == 0:
                print("DEBUG: calling for group", groupid, "and class", tmpclass["URI"])
            newleafclasses, newallclasses = walk_ontology(tmpclass["children"], groupid=groupid, parentclass=tmpclass, level=level+1)
            leafclasses += newleafclasses
            allclasses += newallclasses
    # print("returning ", len(leafclasses))
    return leafclasses, allclasses


def walk_ontology_getkeywords(ontoclasslist, groupid=None, parentclass=None, level=0):
    # algorithm: onto is a list of nodes
    # for each node in the list, we add all the leaf nodes for that node to a list
    # which gets then returned.
    # Whenever we recursively invoke this function, we also pass on the group label
    # (we set it for every node processed) and we pass on parent ui which is getting
    # added to the list of parent uris for each leaf node.
    leafclasses = []
    allclasses = []
    # print("Running at level", level, "for classes", [c["label"] for c in onto])
    for tmpclass in ontoclasslist:
        allclasses.append(tmpclass)
        # print("processing class", c["label"])
        # if we have a group id from the caller set it
        tmpclass["level"] = level
        if groupid:
            tmpclass["groupid"] = groupid
        # if the class is a leaf class, put it into leafclasses
        if len(tmpclass["children"]) == 0:
            # print("Is a leaf class")
            leafclasses.append(tmpclass)
        else:
            # print("is not a leaf class")
            if level == 0:
                groupid = label2groupid[tmpclass["label"]]
            if level == 0:
                print("DEBUG: calling for group", groupid, "and class", tmpclass["URI"])
            newleafclasses, newallclasses = walk_ontology(tmpclass["children"], groupid=groupid, parentclass=tmpclass, level=level+1)
            leafclasses += newleafclasses
            allclasses += newallclasses
    # print("returning ", len(leafclasses))
    return leafclasses, allclasses



# read the ontology in json format and return a 4-tuple with the following elements
# - the ontology, with fields added: level, parentclasses, parentuis, groupid
# - a list of leaf classes
# - a list of parent classes
# - a dictionary mapping each URL to the corresponding class object
def load_ontology(file):
    # apparently this is a list of the 3 children of the root class, where each child then is a map
    # each map has a key "children" which recursively is a list of maps etc.
    # each map also has keu "URL"
    tmponto = json.load(open(file, encoding="utf8"))
    # what we want is two lists of classes:
    # the leaf classes and the parent classes of all leaf classes
    leafclasses, allclasses = walk_ontology(tmponto)
    uri2allclasses = defaultdict()
    for tmpclass in allclasses:
        uri2allclasses[tmpclass["URI"]] = tmpclass
    uri2classes = defaultdict()
    leafuris = set()
    for tmpclass in leafclasses:
        uri2classes[tmpclass["URI"]] = tmpclass
        leafuris.add(tmpclass["URI"])
        pcs = tmpclass["parentclasses"]
        for pc in pcs:
            uri2classes[pc["URI"]] = pc
    leafclasses = [uri2classes[leafuri] for leafuri in leafuris]
    parenturis = set()
    for tmpclass in leafclasses:
        pcs = tmpclass["parentclasses"]
        for pc in pcs:
            parenturis.add(pc["URI"])
    parentclasses = [uri2classes[parenturi] for parenturi in list(parenturis)]
    return tmponto, leafclasses, parentclasses, uri2classes, uri2allclasses




def load_embeddings(embeding_file):
    eu = EmbeddingsUtils()
    eu.loadEmbeddings(embeding_file)
    model = eu.model
    # remove the training info, but do not normalize!
    model.delete_temporary_training_data()
    wv = model.wv
    return model



def sentencetransformer(x):
    global added_sentences
    global original_sentences
    ret = [x]
    original_sentences += 1
    repl = mwu.replace_matches(x, combined=True, single=True)
    if len(repl) > 0:
        added_sentences += len(repl)
        ret.extend(repl)
        # print("DEBUG: transforming x=", x, "to", ret)
    return ret

def filter_token(fields):
    if len(fields) != 4:
        # TODO: this happened but really should never happen, check when and why!!!
        print("WARNING: filter token got not exactly 4 fields but", fields, file=sys.stderr)
        return None
    word = fields[0]
    lemma = fields[1]
    pos = fields[2]
    isknowmak = fields[3]
    if lemma in keepwords:
        return lemma
    if isknowmak:
        return lemma
    if len(lemma) < 2:
        return None
    if lemma in stopwords:
        return None
    # filter if there is not at least one alpha character in the word
    if not re.search(pat_word, lemma):
        return None
    if lemma[-1] == '-' and len(lemma) < 3:
        return None
    return lemma


def get_multiwords(multiwords_file):
    n_terms = 0
    n_mw = 0
    n_mw_kept = 0
    mw_list = []
    mw_set = set()
    with open(multiwords_file, "rt", encoding="utf-8") as ins:
        for line in ins:
            n_terms += 1
            line = line.rstrip()
            fields = line.split("\t")
            term = fields[0]
            # split on whitespace
            tokens = term.split()
            if len(tokens) > 1:
                n_mw += 1
                filteredtokens = []
                # UPDATED: we need to make it easy to find any term that may refer to a class
                # by matching with the original label, so we do not filter tokens from 
                # any multiword term (which may or may not get used later as a class) and we just
                # use the tokens as is
                for token in tokens:
                    # ret = filter_token([token, token, "NN"])
                    # if ret:
                    #     filteredtokens.append(ret)
                    filteredtokens = tokens
                if len(filteredtokens) > 1:
                    mwkey = "_".join(filteredtokens)
                    if mwkey not in mw_set:
                        mw_set.add(mwkey)
                        n_mw_kept += 1
                        mw_list.append(filteredtokens)
    # print("DEBUG: all the MW lists:", mw_list)
    print("All terms read:", n_terms)
    print("MW terms found:", n_mw)
    print("MW terms kept:", n_mw_kept)
    mwu = MultiWordUtils(mw_list)
    return mwu


class SampleSelection:
    def __init__(self, embd_model, corpusreader):
        self.embd_model = embd_model
        self.corpusreader = corpusreader
        self.max_random_batch = 20000
        self.total_documents = 50

    def simple_lang_detection(self, text_token):
        ratios = {}
        for lang in nltk_stopwords.fileids():
            stopwords_set = set(nltk_stopwords.words(lang))
            words_set = set(text_token)
            common_words = words_set.intersection(stopwords_set)
            ratios[lang] = len(common_words)
            most_rated_language = max(ratios, key=ratios.get)
        return most_rated_language




    def get_embd(self,doc_input):
        error = False
        known_token = []
        for token in doc_input:
            if token in self.embd_model.wv.vocab:
                known_token.append(token)
            else:
                if "_" in token:
                    splitmw = token.split("_")
                    for t2 in splitmw:
                        if t2 in self.embd_model.wv.vocab:
                            known_token.append(t2)
        if len(known_token) == 0:
            known_token.append('no')
            error = True
        avg_embs = np.average(np.array([self.embd_model[t] for t in known_token]), axis=0)
        return avg_embs, error

    def _getDocNEmbd(self, current_batch_ids):
        current_docs = []
        current_doc_ids = []
        current_embds = []
        current_paths = []
        for random_id in current_batch_ids:
            corpusreader.docid = random_id
            random_doc, doc_path = next(corpusreader)
            avg_embs, error = self.get_embd(random_doc)
            if error == False:
                current_docs.append(random_doc)
                current_doc_ids.append(random_id)
                current_embds.append(avg_embs)
                current_paths.append(doc_path)
        return current_docs, current_doc_ids, current_embds, current_paths



    def sample(self, class_centroid):
        selected_doc = []
        selected_id = []
        selected_doc_path = []
        all_ids = list(range(len(corpusreader)))
        #print(all_ids)
        random.shuffle(all_ids)
        #cos = torch.nn.CosineSimilarity(dim=1, eps=1e-6)

        #add first random document to the selection
        first_not_selected = True
        corpusreader.docid = all_ids[0]
        while (first_not_selected):

            firstDoc, doc_path = next(corpusreader)
            #print(firstDoc)
            avg_embs, error = self.get_embd(firstDoc)
            #print(avg_embs)
            if error == False:
                first_not_selected = False
                selected_doc.append(firstDoc)
                selected_id.append(all_ids[0])
                selected_doc_path.append(doc_path)
                selected_centriod = avg_embs

        current_batch_min = 1
        current_batch_max = self.max_random_batch

        while(len(selected_id) < self.total_documents):
        #if 1:
            current_batch_ids = all_ids[current_batch_min:current_batch_max]
            current_docs, current_doc_ids, current_embds, current_paths = self._getDocNEmbd(current_batch_ids)
            sim_dis_selected = sklearn.metrics.pairwise.cosine_distances([selected_centriod], current_embds)[0]
            sim_dis_topic = sklearn.metrics.pairwise.cosine_distances([class_centroid], current_embds)[0]
            #print(sim_dis_selected)
            sim = sim_dis_selected - sim_dis_topic
            #print(sim)
            not_selected = True
            #print(sim)
            sim = sim.tolist()
            while (not_selected):
                int_id = sim.index(max(sim))
                #print(int_id)
                current_selected_doc_id = current_doc_ids[int_id]
                current_selected_doc = current_docs[int_id]
                lang = self.simple_lang_detection(current_selected_doc)
                if (current_selected_doc_id not in selected_id) and (len(current_selected_doc) > 20) and lang == 'english':
                    selected_doc.append(current_selected_doc)
                    selected_id.append(current_selected_doc_id)
                    selected_doc_path.append(current_paths[int_id])
                    not_selected = False
                    selected_centriod = np.average(np.array([selected_centriod, current_embds[int_id]]), axis=0)
                    #print(selected_centriod)
                    #print(current_selected_doc)
                    #print(lang)
                else:
                    sim.pop(int_id)
                if len(sim) == 0:
                    not_selected = False

            current_batch_min += self.max_random_batch
            current_batch_max += self.max_random_batch
            if current_batch_min > len(corpusreader):
                random.shuffle(all_ids)
                current_batch_min = 0
                current_batch_max = self.max_random_batch
        
        #print(selected_doc)
        return selected_doc, selected_doc_path

def get_all_keywords(keywords_list):
    #print(keywords_list)
    all_keywords_list = []
    for keyword in keywords_list:
        #print('current',keyword)
        ret = mwu.replace_matches(keyword.split(), combined=True, single=True)
        #print(ret)
        for item in ret:
            all_keywords_list += item
    #print(all_keywords_list)
    all_keywords_list += keywords_list
    return all_keywords_list


def get_all_keywords_under_the_class(current_onto, keywords_dict):
    current_keywords_list = []
    #print(current_onto)
    #print(current_onto['URI'])
    
    toplevel_uri = current_onto['URI']
    if toplevel_uri in keywords_dict:
        toplevel_keywords_ori = keywords_dict[toplevel_uri]
        toplevel_keywords = get_all_keywords(toplevel_keywords_ori)
    else:
        toplevel_keywords = []

    #toplevel_keywords = current_onto['keywords']
    current_keywords_list += toplevel_keywords
    leafclasses, allclasses = walk_ontology_getkeywords(current_onto['children'], level=1)
    for child_onto in allclasses:
        #print(child_onto)
        child_level_uri = child_onto['URI']
        if child_level_uri in keywords_dict:
            child_level_keywords_ori = keywords_dict[child_level_uri]
            child_level_keywords = get_all_keywords(child_level_keywords_ori)
        else:
            child_level_keywords = []
        #child_level_keywords =  child_onto['keywords']
        current_keywords_list += child_level_keywords
    #print(len(current_keywords_list))
    return current_keywords_list

def get_keywords_list(list_file):
    keywords_flags=['key','preferred']
    keywords_dict ={}
    with open(list_file,'r') as fi:
        for line in fi:
            selected = False
            line_tok = line.split('\t')
            keyword = line_tok[0]
            uri = line_tok[1].split('=')[1]
            flags = line_tok[3]
            flags_tok = flags.split('=')[1].split(',')
            for flag in flags_tok:
                if flag in keywords_flags:
                    selected = True
            #print(flags_tok)
            if uri not in keywords_dict:
                keywords_dict[uri] = []
            if selected:
                keywords_dict[uri].append(keyword)

    #print(keywords_dict)
    return keywords_dict




parser = argparse.ArgumentParser(description="sample documents")
parser.add_argument("--corpusdir", type=str, help="The directory from where to read the documents")
parser.add_argument("--ext", type=str, default="conll", help="The extension of files to read from the directory tree")
parser.add_argument("--mwfile", type=str, help="File that contains the multiword expressions to be substituted")
parser.add_argument("--embdfile", type=str, help="Path to load embedding")
parser.add_argument("--originalDir", type=str, help="Path to find original file")
parser.add_argument("--outputprefix", type=str, help="prefix Path to output txt out")
parser.add_argument("--outputdir", type=str, help="Path to output original docs")
parser.add_argument("--ontoJson", type=str, default="", help="Ontology JSON input file", required=True)
parser.add_argument("--ontoLst", type=str, default="", help="Ontology lst input file", required=True)

args = parser.parse_args()

stopwords = set()
keepwords = set()
mwu = get_multiwords(args.mwfile)


onto, leafs, parents, u2c, u2allc = load_ontology(args.ontoJson)
print(len(u2c))
print(len(u2allc))

keywords_dict = get_keywords_list(args.ontoLst)
print(keywords_dict)

embdModel = load_embeddings(args.embdfile)

knowmax_prefix = "http://www.gate.ac.uk/ns/ontologies/knowmak/"

centriod_class_list = ["society", "industrial_biotechnology"]
sub_corpus_list = [""]

for current_centriod_class in centriod_class_list:
    full_current_centriod_class = knowmax_prefix+current_centriod_class
    current_centriod_onto = u2allc[full_current_centriod_class]
    current_centriod_keywords = get_all_keywords_under_the_class(current_centriod_onto, keywords_dict)
    for sub_corpus in sub_corpus_list:
        current_corpus_path = os.path.join(args.corpusdir, sub_corpus)
        print(current_corpus_path)
        corpusreader = DirectoryCorpusConll(current_corpus_path, extension=args.ext, filterby=filter_token, transform_sentence=sentencetransformer)
        #corpusreader = DirectoryCorpusConll(args.corpusdir, extension=args.ext, filterby=filter_token, transform_sentence=sentencetransformer)
        corpusreader.return_file_name = True
        sampleSelection = SampleSelection(embdModel, corpusreader)
        current_onto_centroid, error = sampleSelection.get_embd(current_centriod_keywords)
        selected_docs, selected_paths = sampleSelection.sample(current_onto_centroid)
        output_suffix = current_centriod_class+'.tsv'
        current_output_file = os.path.join(args.outputprefix, output_suffix)
        with open(current_output_file, 'w') as fo:
            for i in range(len(selected_docs)):
                path = selected_paths[i]
                print(path)
                path_tok = path.split(current_corpus_path)
                print(path_tok)
                path_prefix = path_tok[-1].split('.')[0]
                full_prefix = path_prefix+'.txt'
                print(full_prefix)
                print(args.originalDir)
                ori_file_path = os.path.join(args.originalDir, full_prefix)
                print(ori_file_path)
                ori_string = ''
                with open(ori_file_path, 'r') as fori:
                    for line in fori:
                        ori_string += line.strip()+' '
                outline = ori_file_path+'\t'+ori_string+'\r\n'
                fo.write(outline)    

        

#ket_ontos = u2allc["http://www.gate.ac.uk/ns/ontologies/knowmak/industrial_biotechnology"]
#ket_keywords = get_all_keywords_under_the_class(ket_ontos, keywords_dict)
#print(ket_keywords)



#embdModel = load_embeddings(args.embdfile)
#corpusreader = DirectoryCorpusConll(args.corpusdir, extension=args.ext, filterby=filter_token, transform_sentence=sentencetransformer)
#corpusreader.return_file_name = True
#sampleSelection = SampleSelection(embdModel, corpusreader)
#ket_centroid, error = sampleSelection.get_embd(ket_keywords)
#print(ket_centroid)
#selected_docs, selected_paths = sampleSelection.sample(ket_centroid)
#with open(args.outputfile, 'w') as fo:
#    for i in range(len(selected_docs)):
#        #print(' '.join(item))
#        item = selected_docs[i]
#        path = selected_paths[i]
#        output_file_name = str(i)+'.txt'
#        path_tok = path.split(args.corpusdir)
#        path_prefix = path_tok[-1].split('.')[0]
#        full_prefix = path_prefix+'.txt'
#        
#        ori_file_path = os.path.join(args.originalDir, full_prefix)
#        print(ori_file_path)
#        output_dir_path = os.path.join(args.outputdir, output_file_name)        
#        print(output_dir_path)
#        out_line = path+'\t'+' '.join(item)+'\r\n'
#        fo.write(out_line)
#        copyfile(ori_file_path, output_dir_path)
#
#
        



