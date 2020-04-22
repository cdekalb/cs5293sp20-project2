import json
from os import walk
from random import Random
import math
import glob
from pathlib import Path

def getAllFiles(directory, fileGlob):
    # Get all of the subdirectories of the inputted directory
    subdirectories = [f[0] for f in walk(directory)]

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

    # Initialize an empty string to hold all of the text of a document
    totalText = ""

    for fileName in jsonData:

        # Parse through each paragraph of the text
        for text in fileName['body_text']:

            # Extract the text of a given paragraph
            newText = text['text']

            # Concatenate the new pargraph with the previous paragraphs
            totalText = totalText + newText
    
    return totalText



directory = "C:/Users/Creighton DeKalb/Documents/DSA 5293/Project2"

totalFiles = getAllFiles(directory, '*.json')

sampledFiles = getRandomFiles(totalFiles, 0.0001)

totalText = extractText(sampledFiles)

print(totalText)
