import json
import spacy
import nltk
import os
import argparse
from random import Random
import math
import numpy as np
import networkx
import glob
from pathlib import Path
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

def getAllFiles(directory, fileGlob):
    # Get all of the subdirectories of the inputted directory
    subdirectories = [f[0] for f in os.walk(directory)]

    # Get only the subdirectories where the lowest level folder name is 'pdf_json'
    pdfSubdirectories = []
    for i in range(len(subdirectories)):
        if subdirectories[i].endswith('pdf_json'):
            pdfSubdirectories.append(subdirectories[i])

    # Get all files from the pdf_json folders according to the inputted glob
    totalFiles = []
    for i in range(len(pdfSubdirectories)):
        for path in Path(pdfSubdirectories[i]).rglob(str(fileGlob)):
            totalFiles.append(pdfSubdirectories[i] + '\\' + path.name)

    return totalFiles

def getRandomFiles(totalFiles, pctChosen):

    # Set a random seed
    seed = 5293
    myPRNG = Random(seed)

    # Initialize the list that will hold the file names
    filesChosen = []

    # Parse through a percentage of the files
    for i in range(math.ceil(len(totalFiles) * pctChosen)):
        # Select a random index
        randomIndex = myPRNG.randint(0,len(totalFiles))

        # Append the file name to the list of files chosen
        filesChosen.append(str(totalFiles[randomIndex]))

    return filesChosen

def extractText(sampledFiles):
    jsonData = []

    for i in range(len(sampledFiles)):
        with open(sampledFiles[i]) as f:
            jsonData.append(json.load(f))

    # Initialize an empty list to hold all of the uncleaned documents
    doc = []

    # Load the English language model
    sp = spacy.load('en_core_web_sm')

    for fileName in jsonData:

        # Initialize an empty list to temporarily hold the paragraphs of each document
        tempTotalText = []

        # Parse through each paragraph of the text
        for text in fileName['body_text']:

            # Concatenate the new pargraph with the previous paragraphs
            tempTotalText.append(text['text'])

        # Concatenate the paragraph of the given document to a single string
        tempString = ' '.join(tempTotalText)

        # Append the spacy model of the document to doc
        doc.append(sp(tempString))

    # Load spacy's collection of stop wordes
    stopwords = sp.Defaults.stop_words

    # Initialize empty lists to hold the word tokenized documents
    tempWordTok = []
    wordTok = []

    # Iteratively store the word tokens of each document to wordTok
    for document in range(len(doc)):
        tempWordTok = []
        for token in doc[document]:
            tempWordTok.append(token.text)
        wordTok.append(tempWordTok)

    # Initialize empty lists to hold the cleaned documents
    cleanedDocuments = []
    cleanedDocumentString = []

    # Parse through each document
    for i in range(len(wordTok)):
        # Append each word that is not a stop word to cleanedDocuments
        cleanedDocuments.append([word for word in wordTok[i] if not word in stopwords])
        
        # Join the individual words into one string for each document
        cleanedDocumentString.append(' '.join(cleanedDocuments[i]))
    
    return cleanedDocumentString

def clusterDocuments(totalText, sampledFiles):
    # Create a count vectorizer model
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(totalText)

    # Perform k-means clustering with a given number of clusters
    numClusters = 8
    km = KMeans(n_clusters=numClusters)
    km.fit(X)

    # Keep track of which documents are in which cluster
    documentClusterIndices = np.ndarray.tolist(km.labels_)

    # Initialize lists to hold the names and contents of the files in each cluster
    documentClusters = []
    textClusters = []

    # Parse through each cluster
    for i in range(numClusters):
        # Reset the lists containing the file names and contents of the given cluster
        tempDocumentClusters = []
        tempTextClusters = []

        # Parse through each file
        for j in range(len(documentClusterIndices)):
            # Check if the cludter index of the current file matches the current cluster
            if i == documentClusterIndices[j]:
                # Append the file name and contents to the lists containing the file names 
                # and contents of the given cluster
                tempDocumentClusters.append(sampledFiles[j])
                tempTextClusters.append(totalText[j])
        # Append the list of file names and list of file contents for the current cluster
        documentClusters.append(tempDocumentClusters)
        textClusters.append(tempTextClusters)

    return textClusters

def summarizeClusters(documentClusters):
    # Initialize an empty list to hold the concatenated text of each cluster
    clusterText = []

    # Parse through each cluster
    for i in range(len(documentClusters)):
        # Initialize empty list to hold the total text of the cluster
        tempClusterText = ''

        # Parse through the documents in each cluster
        for j in range(len(documentClusters[i])):
            # Concatenate the documents
            tempClusterText = tempClusterText + documentClusters[i][j]
        # Append the text in the cluster to the clusterText list
        clusterText.append(tempClusterText)

        # Initialize empty list to hold the best sentences for each cluster
        summarizedClusterSentences = []

    # Parse through each cluster
    for i in range(len(clusterText)):
        # Sentence tokenize the clustered text
        docSentences = nltk.sent_tokenize(clusterText[i])

        # Create a TfIdf vectorizer
        tv = TfidfVectorizer(min_df=0., max_df=1., use_idf=True)

        # Create a matrix to hold the TfIdf vectorized word tokens
        docTermMatrix = tv.fit_transform(docSentences)
        docTermMatrix = docTermMatrix.toarray()

        # Create a matrix to evaluate the similarity between tokens
        similarityMatrix = np.matmul(docTermMatrix, docTermMatrix.T)

        # Create a graph from the similarity matrix
        similarityGraph = networkx.from_numpy_array(similarityMatrix)

        # Calculate the text rank scores from the similarity graph
        documentScores = networkx.pagerank(similarityGraph)

        # Find the sentences that have the highest text rank scores
        orderedScores = sorted(((documentScore, index) for index, documentScore 
            in documentScores.items()), reverse=True)

        # Collect the indices of the sentences with the highest scores
        bestSentenceIndices = [orderedScores[index][1] for index in range(10)]
    
        # Initialize an empty list to hold the highest ranked sentences of each cluster
        tempSummarizedClusterSentences = []

        # Parse through the top indices
        for j in range(len(bestSentenceIndices)):
            # Append the corresponding sentence of each index
            tempSummarizedClusterSentences.append([docSentences[bestSentenceIndices[j]]])
        # Append the list of the top sentences to the list of summarized clusters
        summarizedClusterSentences.append(tempSummarizedClusterSentences)

    # Set the path of the summary file
    summaryPath = "C:/Users/Creighton DeKalb/Documents/DSA 5293/Project2/cs5293sp20-project2/SUMMARY.md"
    
    # Open the file to write
    summaryFile = open(summaryPath, "w")

    # Write the header of the summery file
    summaryFile.write("This is the summary file for the clustered documents. The summary was generated using the text rank algorithm as provided in Text Analytics with Python: A Practitioner's Guide to Natural Language Processing, Second Edition. \n")

    # Parse through each cluster
    for i in range(len(summarizedClusterSentences)):
        summaryFile.write("\n")
        summaryFile.write("The top 10 sentences for cluster " + str(i) + " are: \n\n")
        
        # Parse through eac hsentence in the cluster
        for j in range(len(summarizedClusterSentences[i])):
            # Remove any unicode characters from the sentence and write it to the summary
            summaryFile.write(str(str(summarizedClusterSentences[i][j]).encode('ascii', 'ignore').decode("utf-8")))
            summaryFile.write(" \n")

    # Close the file
    summaryFile.close()
    
    return summarizedClusterSentences

def main(globType):

    directory = "C:/Users/Creighton DeKalb/Documents/DSA 5293/Project2"

    totalFiles = getAllFiles(directory, globType)

    sampledFiles = getRandomFiles(totalFiles, 0.001)

    totalText = extractText(sampledFiles)

    documentClusters = clusterDocuments(totalText, sampledFiles)

    summarizedClusterSentences = summarizeClusters(documentClusters)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, required=True, 
        help="The incident summary url.")
     
    args = parser.parse_args()
    if args.input:
        globType = args.input[0]
        main(globType)