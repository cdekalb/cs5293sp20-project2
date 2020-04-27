# Project 2

Class:
CS 5293

Author:
Creighton DeKalb

# Project Summary

The purpose of this project is to summarize a large number of text files. More specifically, this project takes a random sample of 50,000 .json files, clusters the sample of documents, and finally reports back the top sentences from each cluster. The project used the spacy and nltk libraries for text tokenization, the sklearn library for clustering, and the networkx library for text rank summarization. The data for this project can be downloaded at: https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge/data.

# Installing

In order to run this project, the user needs to install pipenv. This can be done in the command line using the command:

    pipenv install

The spaCy library also needs to be installed and can be done so with the command:

    pipenv install spacy

An additional library must be downloaded for spaCy to be able to work with the English language. It can be downloaded with the command:

    python -m spacy download en_core_web_sm

Additionally, the nltk, sklearn, and networkx libraries are required for the project to run. These libraries can be downloaded similarly with the general command:

    python install <library>

# Prerequisites

To access the project, the user must navigate to the command line and run the command:

    git clone https://github.com/cdekalb/cs5293sp20-project2.git

# Deployment

The main file takes in a glob and finds all files in the specificed directory that match the glob, takes a random sample of those files, extracts the body of the text, clusters each document based on its contents, then summarizes each cluster by outputting the highest ranked sentences from each cluster.

- getAllFiles(directory, fileGlob)

The getAllFiles method takes in a directory and a glob, and returns a list of all files within the directory that match the glob.

- getRandomFiles(totalFiles, pctChosen)

The getRandomFiles method takes in a list of files and a percent value between 0 and 1 and returns a pctChosen * 100% random sample of the files.

- extractText(sampledFiles)

The extractText method takes in a list of files and outputs a list, where each index of the list contains the entirety of the body of text from each sampled document. The documents in the returned list have had the stop words removed. The extraction of the text is dependent on the structure of the files, which will be discussed in the assumptions section of this README.

- clusterDocuments(totalText, sampledFiles)

The clusterDocuments method takes in a list of the body of text of documents and a list of the file paths of the sampled files and returns a list of lists, where the sublists contain the contents of the documents in each cluster. The contents of the files are clustered using K-Means with 8 cluster centers. This number of clusters was decided on using the KElbowVisualizer method in the yellowbricks.cluster package, however this package is not needed to run the code. The method then creates a list of the contents of each document for a given cluster, then appends that list to a list that contains the contents for every cluster.

- summarizeClusters(documentClusters)

The summarizeClusters method takes in a list of lists that represents the clusters and returns a list of lists containing the top 10 sentences of each cluster. The method follows the text rank algorithm as provided in Text Analytics with Python: A Practitioner's Guide to Natural Language Processing, Second Edition. The method sentence tokenizes the contents of each cluster, creates a similarity matrix based on the word tokens, then generates scores using the pagerank method in the networkx package. The method then sorts the sentences by rank, and appends the top 10 sentences of each cluster to a list.

To run the code, navigate from the command line to the cs5293sp20-project0 directory in which all the project files exist. In the command line, enter the following:

    pipenv run python main.py --input <glob>

This command will run the main.py file using the provided glob to find matching files in the directory's subdirectories.

# Assumptions and Bugs

- The file structure of this project is specific to my personal computer and will not run correctly as is on any other machine but mine. To fix this, one would have to manually change the path variables that appear in the code.

- The cs5293sp20-project2 directory needs to be in the same folder as the collection of files downloaded from the provided kaggle link.

- The only glob that works is '*.json', due to the code being written for a specific outline of .json file.

- The outline of the .json file is provided in the cs5293sp20-project2 directory in the json_schema.txt file.

- Due to the size of the objects in the code, the final results in the SUMMARY.md file were created using a .1% percent sample of the files instead of 10%.