import math

def countWords(inFile):
    words_dict = {}
    inFile.seek(0)
    for line in inFile:
        for word in line.split():
            lowerCaseWord = word.lower()
            if (lowerCaseWord not in words_dict):
                words_dict.update({lowerCaseWord : 1})
            else:
                words_dict[lowerCaseWord] += 1
    return words_dict

def processFile(inFile, outFile, words_dict, bannedWords):
    inFile.seek(0)
    for line in inFile:
        outFile.write("<s> ")
        for word in line.split():
            writtenWord = word.lower()
            if (writtenWord in words_dict) and (words_dict[writtenWord] == 1):
                writtenWord = "<unk>"
            elif writtenWord in bannedWords:
                writtenWord = "<unk>"
            outFile.write(writtenWord + " ")
        outFile.write("</s>\n")

def compareDict(dict1, dict2):
    notMatched = []
    for key in dict1:
        if key not in dict2:
            notMatched.append(key)
    return notMatched

def unigramModel(words_dict, totalWords):
    unigramModel = {}
    for key in words_dict:
        probability = round(words_dict[key]/totalWords, 8)
        unigramModel.update({key:probability})
    return unigramModel
            
def createBigram(inFile):
    bigram = {}
    inFile.seek(0)
    for line in inFile:
        words = line.split()
        for i in range(0, len(words)):
            if (i < len(words)-1) and (tuple([words[i],words[i+1]]) not in bigram): 
                bigram.update({tuple([words[i],words[i+1]]):1})
            elif (i < len(words)-1):
                bigram[tuple([words[i],words[i+1]])] += 1
    return bigram

def bigramModel(bigram_dict, word_dict):
    bigramModel = {}
    for key in bigram_dict:
        probability = round(bigram_dict[key]/word_dict[key[0]], 8)
        bigramModel.update({key:probability})
    return bigramModel

def addOneSmoothingModel(bigram_dict, word_dict, uniqueWords):
    addOneSmoothingModel = {}
    for key in bigram_dict:
        probability = round(((1.0 + bigram_dict[key]) / (uniqueWords + word_dict[key[0]])),8)
        addOneSmoothingModel.update({key:probability})
    return addOneSmoothingModel

def writeDict(dict, outFile):
    for key in dict:
        outFile.write("{" + str(key) + "}" + ": " + str(dict[key]) + "\n")
    outFile.write("\n")

def processSentence(sentence, words_dict):
    processedSentence = "<s> "
    for word in sentence.split():
        if word.lower() not in words_dict:
            processedSentence += "<unk> "
        else:
            processedSentence += (word.lower() + " ")
    processedSentence += " </s>"
    return processedSentence

def computeUnigramLog(sentence, unigramModel):
    probability = 0
    for word in sentence.split():
        probability += math.log(unigramModel[word], 2)
    probability = round(probability, 4)
    return probability

def computeBigramLog(sentence, bigramModel, unigramModel):
    probability = 0
    words = sentence.split()
    probability += math.log(unigramModel[words[0]], 2)
    for i in range(0, len(words) - 1):
        tupleWord = tuple([words[i], words[i+1]])
        if tupleWord in bigramModel:
            probability += math.log(bigramModel[tupleWord], 2)
    probability = round(probability, 4)
    return probability

def computeAddOneSmoothingLog(sentence, addOneSmoothingModel, unigramModel):
    probability = 0
    words = sentence.split()
    probability += math.log(unigramModel[words[0]], 2)
    for i in range(0, len(words) - 1):
        tupleWord = tuple([words[i], words[i+1]])
        if tupleWord in addOneSmoothingModel:
            probability += math.log(addOneSmoothingModel[tupleWord], 2)
    probability = round(probability, 4)
    return probability

def computePerplexity(logModel, totalWords):
    result = math.exp((-1.0/totalWords) * logModel)
    return round(result, 4)

def computeUnigramLogFile(inFile, unigramModel):
    inFile.seek(0)
    probability = 0
    for line in inFile:
        for word in line.split():
           probability += math.log(unigramModel[word], 2)
    probability = round(probability, 4) 
    return probability

def computeBigramLogFile(inFile, bigramModel, unigramModel):
    inFile.seek(0)
    probability = 0
    for line in inFile:
        words = line.split()
        for i in range(0, len(words)-1):
           if i == 0:
               probability += math.log(unigramModel[words[0]], 2)
           tupleWord = tuple([words[i], words[i+1]])
           if tupleWord in bigramModel:
               probability += math.log(bigramModel[tupleWord], 2)
    probability = round(probability, 4) 
    return probability

def computeAddOneSmoothingLogFile(inFile, addOneSmoothingModel, unigramModel):
    probability = 0
    words = sentence.split()
    probability += math.log(unigramModel[words[0]], 2)
    for line in inFile:
        words = line.split()
        for i in range(0, len(words)-1):
            if i == 0:
               probability += math.log(unigramModel[words[0]], 2)
            tupleWord = tuple([words[i], words[i+1]])
            if tupleWord in addOneSmoothingModel:
               probability += math.log(addOneSmoothingModel[tupleWord], 2)
    probability = round(probability, 4)
    return probability

if __name__=="__main__":
    # 1.1
    testFile = open("test.txt", "r", errors="ignore")
    trainFile = open("train-Fall2024.txt", "r", errors="ignore")

    processedTestFile = open("processedTest.txt", "w")
    processedTrainFile = open("processedTrain.txt", "w")

    words_dict = countWords(trainFile)
    bannedWords = compareDict(countWords(testFile), words_dict)

    processFile(testFile, processedTestFile, words_dict, bannedWords)
    processFile(trainFile, processedTrainFile, words_dict, [])

    processedTrainFile.close()
    processedTestFile.close()

    # 1.2
    processedTestFile = open("processedTest.txt", "r")
    processedTrainFile = open("processedTrain.txt", "r")

    words_dict = countWords(processedTrainFile)

    totalTokenCount = 0
    for key in words_dict:
        totalTokenCount += words_dict[key] 
    
    unigramModel = unigramModel(words_dict, totalTokenCount)

    bigram_dict = createBigram(processedTrainFile)
    bigramModel = bigramModel(bigram_dict, words_dict)

    uniqueTokens = 0
    for key in words_dict:
        uniqueTokens += 1
    addOneSmoothingModel = addOneSmoothingModel(bigram_dict, words_dict, uniqueTokens)

    outFile = open("1.2Answers.txt", "w")

    outFile.write("< A unigram maximum likelihood model >\n")
    writeDict(unigramModel, outFile)
    outFile.write("< A bigram maximum likelihood model >\n")
    writeDict(bigramModel, outFile)
    outFile.write("< A bigram model with Add-One smoothing >\n")
    writeDict(addOneSmoothingModel, outFile)

    # 1.3
    outFile2 = open("1.3Answers.txt", "w")

    # Question 1
    outFile2.write("Question 1:\n\t" + str(len(words_dict)-1) +"\n\n")

    # Question 2
    totalTokenQ2 = 0
    for keys in words_dict:
        if key != "<s>":
            totalTokenQ2 += words_dict[key]
    outFile2.write("Question 2:\n\t" + str(totalTokenQ2) +"\n\n")

    # Question 3
    testFile_dict = countWords(testFile)
    trainFile_dict = countWords(trainFile)
    numOfKeys = len(testFile_dict)
    foundKeys = numOfKeys
    for key in testFile_dict:
        if key not in trainFile_dict:
            foundKeys -= 1
    wordOccurance = round(foundKeys/numOfKeys, 4)
    outFile2.write("Question 3:\n\t" + str(1 - wordOccurance) + "\n\n")

    # Question 4
    bigram_testData = createBigram(processedTestFile)
    numOfKeys = len(bigram_testData)
    foundKeys = numOfKeys
    for key in bigram_testData:
        if key not in bigram_dict:
            foundKeys -= 1
    bigramOccurance = round(foundKeys/numOfKeys, 4)
    outFile2.write("Question 4:\n\t" + str(1 - bigramOccurance) + "\n\n")

    # Question 5
    sentence = "I look forward to hearing your reply ."
    sentence = processSentence(sentence, words_dict)

    unigramLog = computeUnigramLog(sentence, unigramModel)
    bigramLog = computeBigramLog(sentence, bigramModel, unigramModel)
    addOneLog = computeAddOneSmoothingLog(sentence, addOneSmoothingModel, unigramModel)

    outFile2.write("Question 5:\n\t")
    outFile2.write("Unigram Model: " + str(unigramLog) + "\n\t")
    outFile2.write("Bigram Model: " + str(bigramLog) + "\n\t")
    outFile2.write("Add-One Smoothing Model: " + str(addOneLog) + "\n\n")

    # Question 6
    totalSetenceWords = 0
    for word in sentence.split():
        totalSetenceWords += 1

    perplexityUnigram = computePerplexity(unigramLog, totalSetenceWords)
    perplexityBigram = computePerplexity(bigramLog, totalSetenceWords)
    perplexityAddOne = computePerplexity(addOneLog, totalSetenceWords)

    outFile2.write("Question 6:\n\t")
    outFile2.write("Unigram Model: " + str(perplexityUnigram) + "\n\t")
    outFile2.write("Bigram Model: " + str(perplexityBigram) + "\n\t")
    outFile2.write("Add-One Smoothing Model: " + str(perplexityAddOne) + "\n\n")

    # Question 7
    unigramLogFile = computeUnigramLogFile(processedTestFile, unigramModel)
    bigramLogFile = computeBigramLogFile(processedTestFile, bigramModel, unigramModel)
    addOneLogFile = computeAddOneSmoothingLogFile(processedTestFile, addOneSmoothingModel, unigramModel)

    perplexityUnigramFile = computePerplexity(unigramLogFile, totalTokenCount)
    perplexityBigramFile = computePerplexity(bigramLogFile, totalTokenCount)
    perplexityAddOneFile = computePerplexity(addOneLogFile, totalTokenCount)

    outFile2.write("Question 7:\n\t")
    outFile2.write("Unigram Model: " + str(perplexityUnigramFile) + "\n\t")
    outFile2.write("Bigram Model: " + str(perplexityBigramFile) + "\n\t")
    outFile2.write("Add-One Smoothing Model: " + str(perplexityAddOneFile) + "\n\n")

    # Close files
    outFile.close()
    outFile2.close()
    processedTrainFile.close()
    processedTestFile.close()
    trainFile.close()
    testFile.close()