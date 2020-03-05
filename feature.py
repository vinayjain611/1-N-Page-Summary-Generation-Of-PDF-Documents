from collections import Counter
from math import fabs              #returns the absolute value ((Positive value) of the specified expression or an individual number
from re import split as regex_split, sub as regex_sub, UNICODE as REGEX_UNICODE 
from nltk.corpus import stopwords   #massive dump of all kinds of natural language data sets that are definitely worth taking a look at
stopWords = set(stopwords.words('english'))
ideal = 20.0

def Summarize(title, text):
    summaries = []
    sentences = split_sentences(text)
    keys = keywords(text)
    titleWords = split_words(title)

    if len(sentences) <= 5:
        return sentences

    #score setences, and use the top 10 sentences
    ranks = score(sentences, titleWords, keys).most_common(20)
    for rank in ranks:
        summaries.append(rank[0])
    return "".join( str(x) for x in summaries)
    #return summaries



def score(sentences, titleWords, keywords):
    #score sentences based on different features

    senSize = len(sentences)
    ranks = Counter()
    for i, s in enumerate(sentences):
        sentence = split_words(s)
        titleFeature = title_score(titleWords, sentence)
        sentenceLength = length_score(sentence)
        sentencePosition = sentence_position(i+1, senSize)
        sbsFeature = sbs(sentence, keywords)
        dbsFeature = dbs(sentence, keywords)
        frequency = (sbsFeature + dbsFeature) / 2.0 * 10.0

        #weighted average of scores from four categories
        totalScore = (titleFeature*1.5 + frequency*2.0 +
                      sentenceLength*1.0 + sentencePosition*1.0) / 4.0
        ranks[s] = totalScore
    return ranks


def sbs(words, keywords):
    score = 0.0
    if len(words) == 0:
        return 0
    for word in words:
        if word in keywords:
            score += keywords[word]
    return (1.0 / fabs(len(words)) * score)/10.0


def dbs(words, keywords):
    if (len(words) == 0):
        return 0

    summ = 0
    first = []
    second = []

    for i, word in enumerate(words):
        if word in keywords:
            score = keywords[word]
            if first == []:
                first = [i, score]
            else:
                second = first
                first = [i, score]
                dif = first[0] - second[0]
                summ += (first[1]*second[1]) / (dif ** 2)

    # number of intersections
    k = len(set(keywords.keys()).intersection(set(words))) + 1
    return (1/(k*(k+1.0))*summ)


def split_words(text):
    #split a string into array of words
    try:
        text = regex_sub(r'[^\w ]', '', text, flags=REGEX_UNICODE)  # strip special chars
        return [x.strip('.').lower() for x in text.split()]
    except TypeError:
        print ("Error while splitting characters")
        return None


def keywords(text):
    """get the top 10 keywords and their frequency scores
    ignores blacklisted words in stopWords,
    counts the number of occurrences of each word
    """
    text = split_words(text)
    numWords = len(text)  # of words before removing blacklist words
    freq = Counter(x for x in text if x not in stopWords)

    minSize = min(10, len(freq))  # get first 10
    keywords = {x: y for x, y in freq.most_common(minSize)}  # recreate a dict

    for k in keywords:
        articleScore = keywords[k]*1.0 / numWords
        keywords[k] = articleScore * 1.5 + 1

    return keywords


def split_sentences(text):
    '''
    The regular expression matches all sentence ending punctuation and splits the string at those points.
    At this point in the code, the list looks like this ["Hello, world", "!" ... ]. The punctuation and all quotation marks
    are separated from the actual text. The first s_iter line turns each group of two items in the list into a tuple,
    excluding the last item in the list (the last item in the list does not need to have this performed on it). Then,
    the second s_iter line combines each tuple in the list into a single item and removes any whitespace at the beginning
    of the line. Now, the s_iter list is formatted correctly but it is missing the last item of the sentences list. The
    second to last line adds this item to the s_iter list and the last line returns the full list.
       '''
    
    sentences = regex_split(u'(?<![A-ZА-ЯЁ])([.!?]"?)(?=\s+\"?[A-ZА-ЯЁ])', text, flags=REGEX_UNICODE)
    s_iter = zip(*[iter(sentences[:-1])] * 2)
    s_iter = [''.join(map(str,y)).lstrip() for y in s_iter]
    s_iter.append(sentences[-1])
    #print(s_iter)
    #Sprint(type(s_iter))
    return s_iter
    '''
    textsp = text
    article = textsp.split(".")

    sen = []

    for x in article:
        sen.append(x.replace("[^a-zA-Z]", " "))
    sen.pop() 
    #print(sen)
    #print(type(sen))
    return sen
    '''

def length_score(sentence):
    return 1 - fabs(ideal - len(sentence)) / ideal


def title_score(title, sentence):
    title = [x for x in title if x not in stopWords]
    count = 0.0
    for word in sentence:
        if (word not in stopWords and word in title):
            count += 1.0
            
    if len(title) == 0:
        return 0.0
        
    return count/len(title)


def sentence_position(i, size):
    """different sentence positions indicate different
    probability of being an important sentence"""

    normalized = i*1.0 / size
    if 0 < normalized <= 0.1:
        return 0.17
    elif 0.1 < normalized <= 0.2:
        return 0.23
    elif 0.2 < normalized <= 0.3:
        return 0.14
    elif 0.3 < normalized <= 0.4:
        return 0.08
    elif 0.4 < normalized <= 0.5:
        return 0.05
    elif 0.5 < normalized <= 0.6:
        return 0.04
    elif 0.6 < normalized <= 0.7:
        return 0.06
    elif 0.7 < normalized <= 0.8:
        return 0.04
    elif 0.8 < normalized <= 0.9:
        return 0.04
    elif 0.9 < normalized <= 1.0:
        return 0.15
    else:
        return 0



def testText(textt,texta):
     
    text = Summarize(textt,texta)
    return text

import io

from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfpage import PDFPage
 
def extract_text_from_pdf(pdf_path):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle)
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
 
    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh, 
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
 
        text = fake_file_handle.getvalue()
 
    # close open handles
    converter.close()
    fake_file_handle.close()
 
    if text:
        return text
 

#texta = extract_text_from_pdf('articlepdf.pdf')
#textt = "daily rental bikes in bengaluru"

#print(type(texta))

#summ = testText(textt,texta)
#print(summ)

