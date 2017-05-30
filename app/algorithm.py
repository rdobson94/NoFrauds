import textract
import itertools
from google import google
from bs4 import BeautifulSoup
import ast
import textrazor
import re
import string
import validators
import os
import requests
from difflib import SequenceMatcher
import numpy as np
from PyDictionary import PyDictionary
import difflib

"""CLEANS A WEBSITE THAT IS TO BE COMPARED WITH THE UPLOADED DOCUMENT OR RAW TEXT AT THE ADD FILE PAGE(REMOVES ALL HTML TAG ETC)"""
"""REMOVES ALL PUNCTUATION FOR CLARITY"""
"""RETURNS A CLEAN STRING OF CONTENT INSIDE BODY OF THE HTML URL,DOCUMENTS(PDF,TXT, DOCX)"""
"""RETURNS ALL ENTITIES,SUBJECTS,PHRASES FOUND WITHIN INPUT AND SOURCE/S"""
"""RETURNS A CREDIBILITY SCORE AND ALL MATCHING DATA FOR INPUT FROM RELEVANT INFORMATION SCRAPED FROM THE WEB """



textrazor.api_key = "f32062ac014773fdbc80e9619c759821f3273f25d8de434425801a64"
client = textrazor.TextRazor(extractors=["entities", "topics","words", "phrases","entailments"])
client.set_classifiers(["textrazor_newscodes"])
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'docx', 'rtf', 'doc'])
def webScraper(textarea):
    isUrl= validators.url(textarea)
    if isUrl==True: #IF THE DATA IN THE TEXT AREA IS A URL LINK
        response = client.analyze_url(textarea)
        entities = list(response.words())
        x= str(entities)
        pattern = r'"([A-Za-z0-9_\./\\-]*)"'
        m= re.findall(pattern,x)
        myString = " ".join(m)
        regex = re.compile('[%s]' % re.escape(string.punctuation)) #REMOVE ALL PUNCTUATIONS FOR TEST
        cleantext=(regex.sub("", myString ))
    elif textarea.split(".")[-1] in ALLOWED_EXTENSIONS:
        text = textract.process(textarea,encoding='ascii')
        response =client.analyze(text)
        entities = list(response.words())
        x= str(entities)
        pattern = r'"([A-Za-z0-9_\./\\-]*)"'
        m= re.findall(pattern,x)
        myString = " ".join(m)
        regex = re.compile('[%s]' % re.escape(string.punctuation)) #REMOVE ALL PUNCTUATIONS FOR TEST
        cleantext=(regex.sub("", myString ))
    elif textarea.split(".")[-1] in ALLOWED_EXTENSIONS =='pdf':  #HANDLE PDF DOCS differently due to special encoding
        text = textract.process(textarea, method='pdfminer')    
        response =client.analyze(text)
        entities = list(response.words())
        x= str(entities)
        pattern = r'"([A-Za-z0-9_\./\\-]*)"'
        m= re.findall(pattern,x)
        myString = " ".join(m)
        regex = re.compile('[%s]' % re.escape(string.punctuation)) #REMOVE ALL PUNCTUATIONS FOR TEST
        cleantext=(regex.sub("", myString ))

    else:
        client.set_cleanup_mode("raw") #IF THE DATA IN THE TEXT AREA IS A RAW TEXT
        response =client.analyze(textarea)
        entities = list(response.words())
        x= str(entities)
        pattern = r'"([A-Za-z0-9_\./\\-]*)"'
        m= re.findall(pattern,x)
        myString = " ".join(m)
        regex = re.compile('[%s]' % re.escape(string.punctuation)) #REMOVE ALL PUNCTUATIONS FOR TEST
        cleantext=(regex.sub("", myString ))

    response =client.analyze(cleantext)
    """Find All Entities in the input"""
    entities = list(response.entities())
    entities.sort(key=lambda x: x.relevance_score, reverse=True)
    
    seen = set()
    entitylist=[]
    for entity in entities:
        if entity.id not in seen:
            #print entity.confidence_score
            seen.add(entity.id)
            entitylist+=[str(entity.id.encode('ascii', 'ignore').decode('ascii'))]
            entitylist=[x for x in entitylist if not (x.isdigit())]
    """Find a phrases in the input"""        
    phraselist=[]
    invalidphrases = set(['your','we','from', 'it','one','that','this','who','us','our','what','you','this','it','these'])
    for phrase in response.noun_phrases():
        phrases=cleantext [phrase.words[0].input_start_offset: phrase.words[-1].input_end_offset]
        phraselist+=[str(phrases.encode('ascii', 'ignore').decode('ascii'))]
    phraselist=list((set(phraselist)-set(invalidphrases)))
    """Find Main Subject Topic"""
    sublist=[]
    for topic in response.topics():
        if topic.score > 0.80:
            subjects=topic.label
            #dictionary=PyDictionary()
            #for i, word in enumerate(subjects.split()):
            #    print " word #%d: %s" % (i,word)
               # split_list =[i.split() for i in subjects]
                #x=dictionary.synonym(split_list)

                #print " word #%d: %s" % (i,word,dictionary.synonym(i))
            sublist += [str(subjects.encode('ascii', 'ignore').decode('ascii'))]
    """Prints a category label as well as the score associated """ 
    cat_label=[]
    cat_score=[]
    for category in response.categories():
        cat_label+=[str(category.label)]
        cat_score+=[category.score]
    try:
        stripped=cat_label[0].partition('>')[2]
        maincategory=re.sub(r"[\(\[].*?[\)\]]", "", stripped)

    except IndexError:
        pass
    cat_score=cat_score[0]
    inputcategory=cat_label[0]
    '''Search API and BeautifulSoup Crawler'''
    siteurl=[]
#    for url in search(sublist[0], tld='com', lang='en', num=1, start=0, stop=2, pause=3): #RETURNS TOP 3 URLS FOR THE MAIN SUBJECT MATCH IN DOCUMENT/STRING
    search_results = google.search(sublist[0], 1)
    for result in search_results:
        siteurl+=[str(result.link.encode('ascii', 'ignore').decode('ascii'))]
        
    siteurl=siteurl[0:2] #MAXIMUM OF TWO SOURCES ,GREATER SOURCES=GREATER CREDIBILITY ACCURACY AT THE EXPENSE OF SPEED.
    sitedata=""
    for url in siteurl:
        e=requests.get(url)
        s=BeautifulSoup(e.content,"html.parser")
        bd=s.find("body")
        for x in bd.findAll('script'):
            x.extract()
        for x in bd.findAll('style'):
            x.extract()
        rt=bd.text
        ft=re.sub( '\s+', ' ', rt ).strip()
        words=ft.split()
        words=[x.lower() for x in words]
        words=[a.encode('ascii','ignore') for a in words]
        words=filter(None,words)
        sitedata=" ".join(words)
    """Clean up call"""
    client.set_cleanup_mode("raw")
    """URL category Extract"""
    urlcat_label=[]
    urlcat_score=[]
    response = client.analyze(sitedata)
    for urlcategory in response.categories():
        urlcat_label+=[str(urlcategory.label)]
        urlmaincategory=urlcat_label[0].partition('>')[2]
        urlcat_score.append(urlcategory.score)
    
    """URL Phrases Extract"""    
    urlphraselist=[]
    response = client.analyze(sitedata)
    for np in response.noun_phrases():
        x=sitedata[np.words[0].input_start_offset: np.words[-1].input_end_offset]
        urlphraselist+=[str(x.encode('ascii', 'ignore').decode('ascii'))]
    """URL Entity Extract"""
    urlentitylist=[]
    response = client.analyze(sitedata)
    urlentities = list(response.entities())
    urlentities.sort(key=lambda x: x.relevance_score, reverse=True)
    seen = set()
    for urlentity in urlentities:
        if urlentity.id not in seen:
            seen.add(urlentity.id)
            urlentitylist+=[str(urlentity.id.encode('ascii', 'ignore').decode('ascii'))] 
            urlentitylist=[x for x in urlentitylist if not (x.isdigit())]
    """URL SubjectTopic Extract"""
    client.set_cleanup_mode("raw")
    response = client.analyze(sitedata)
    urlsublist=[]
    for top in response.topics():
        if top.score > 0.01:
            urlsubjects=top.label
            urlsublist += [str(urlsubjects.encode('ascii', 'ignore').decode('ascii'))]    
    """Compare main source categories and main source category outputs"""
    categoryscore=SequenceMatcher(None, maincategory, urlmaincategory).ratio()+SequenceMatcher(None,cat_label,urlcat_label).ratio()
    matchingcategory=list(set(maincategory).intersection(urlmaincategory))
    categoryscore=categoryscore*0.10
        
    """Compare source phrase and input phrases"""
    matchingphrases=list(set(urlphraselist).intersection(phraselist))
    phrasematches=float(len(set(urlphraselist).intersection(phraselist))) 
    phrasetotal=float(len(phraselist))
    try:
        phrasescore=(phrasematches/phrasetotal)*0.10
    except ZeroDivisionError:
        return None
    """Compare source entities and input entities"""
    matchingentities=list(set(urlentitylist).intersection(entitylist))
    entitymatches=float(len(set(urlentitylist).intersection(entitylist)))
    entitytotal=float(len(entitylist))
    try:
        entityscore=(entitymatches/entitytotal)*0.10
    except ZeroDivisionError:
        return None
    """Compare source topics and input topics"""
    matchingsubjects=list(set(sublist).intersection(urlsublist))
    subjectmatches=float(len(set(sublist).intersection(urlsublist)))
    sublisttotal=float(len(sublist))
    try:
        subjectscore=(subjectmatches/sublisttotal)*0.70
    except ZeroDivisionError:
        return None
    
    """Comparing outputs to Calculate Credibility and weight scores"""
    
    credibility= (categoryscore+phrasescore+entityscore+subjectscore) *100
    
    """Testing purposes"""
    # if credibility>85:
    #     print "This data is very credible,scoring "+str(credibility)+" Consistency when compared to top sources"
    # elif credibility>75 and credibility<84:
    #     print "This data is mostly credible,scoring "+str(credibility)+" Consistency when compared to top sources"
    # elif credibility>50 and credibility<74:
    #     print "This data is partially credible,scoring "+str(credibility)+ "Consistency when compared to top sources"
    # elif credibility>25 and credibility<49:
    #   print "This data is inconsistent, scoring "+str(credibility)+" Consistency when compared to top sources"
    # else:
    #     if credibility<25:
    #         print "This data is fallacy, scoring "+str(credibility)+" Consistency when compared to top sources"
    
    return(entitylist,phraselist,sublist,cat_score,maincategory,siteurl,urlmaincategory,urlphraselist,urlentitylist,urlsublist,
           phrasematches,credibility,subjectmatches,entitymatches,inputcategory,matchingsubjects,matchingphrases,matchingcategory,matchingentities)
    
       
    
    
    