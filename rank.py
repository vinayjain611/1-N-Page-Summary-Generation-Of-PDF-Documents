from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
import numpy as np
import networkx as nx
import PyPDF2
import textract
import io
from re import split as regex_split, sub as regex_sub, UNICODE as REGEX_UNICODE

from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
 

 
def read_article(file_name):
    
    #pdfFileObj = open(file_name, 'rb')
    #pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    #pageObj = pdfReader.getPage(0)
    #file = pageObj.extractText()

    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle)
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
 
    with open(file_name, 'rb') as fh:
        for page in PDFPage.get_pages(fh, 
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
 
        file = fake_file_handle.getvalue()
 
    # close open handles
    converter.close()
    fake_file_handle.close()

   
    #print("value of file",file)
    #print("type of file",type(file))
    #print("value: ",file[0])
    #article = file.split(".")
    #sentences = []


    sentences = regex_split(u'(?<![A-ZА-ЯЁ])([.!?]"?)(?=\s+\"?[A-ZА-ЯЁ])', file, flags=REGEX_UNICODE)
    s_iter = zip(*[iter(sentences[:-1])] * 2)
    s_iter = [''.join(map(str,y)).lstrip() for y in s_iter]
    s_iter.append(sentences[-1])
    #print(s_iter)
    #Sprint(type(s_iter))
    return s_iter







    
    #for sentence in article:
       # print(sentence)
        #sentences.append(sentence.replace("[^a-zA-Z]", " ").split(" "))
    #sentences.pop() 
    
    #return sentences

def sentence_similarity(sent1, sent2, stopwords=None):
    if stopwords is None:
        stopwords = []
 
    sent1 = [w.lower() for w in sent1]
    sent2 = [w.lower() for w in sent2]
 
    all_words = list(set(sent1 + sent2))
 
    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)
 
    # build the vector for the first sentence
    for w in sent1:
        if w in stopwords:
            continue
        vector1[all_words.index(w)] += 1
 
    # build the vector for the second sentence
    for w in sent2:
        if w in stopwords:
            continue
        vector2[all_words.index(w)] += 1
 
    return 1 - cosine_distance(vector1, vector2)
 
def build_similarity_matrix(sentences, stop_words):
    # Create an empty similarity matrix
    similarity_matrix = np.zeros((len(sentences), len(sentences)))
 
    for idx1 in range(len(sentences)):
        for idx2 in range(len(sentences)):
            if idx1 == idx2: #ignore if both are same sentences
                continue 
            similarity_matrix[idx1][idx2] = sentence_similarity(sentences[idx1], sentences[idx2], stop_words)

    return similarity_matrix


def generate_summary(file_name, top_n=5):
    stop_words = stopwords.words('english')
    summarize_text = []

    # Step 1 - Read text anc split it
    sentences =  read_article(file_name)

    # Step 2 - Generate Similary Martix across sentences
    sentence_similarity_martix = build_similarity_matrix(sentences, stop_words)

    # Step 3 - Rank sentences in similarity martix
    sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_martix)
    scores = nx.pagerank(sentence_similarity_graph)

    # Step 4 - Sort the rank and pick top sentences
    ranked_sentence = sorted(((scores[i],s) for i,s in enumerate(sentences)), reverse=True)    
    #print("Indexes of top ranked_sentence order are ", ranked_sentence)    

    for i in range(top_n):
      summarize_text.append("".join(ranked_sentence[i][1]))
    
    # Step 5 - Output the summarize text
    print("[Summarize Text From Rank Based:]\n", ". ".join(summarize_text))
#generate_summary( "articlemulti.pdf")
