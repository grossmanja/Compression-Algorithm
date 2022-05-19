import os
import sys
import marshal
import array
from functools import partial
import string
import time
import heapq

try:
    import cPickle as pickle
except:
    import pickle

termchar = 17 # you can assume the byte 17 does not appear in the input file

# This takes a string (really, just a sequence of bytes over which you can iterate), msg, 
# and returns a tuple (enc,\ ring) in which enc is the ASCII representation of the 
# Huffman-encoded message (e.g. "1001011") and ring is your ``decoder ring'' needed 
# to decompress that message.
def encode(msg):
    uniqueList = list(set(msg)) #makes a list of every unique character in msg
    freq = []
    for i in range(len(uniqueList)):
        freq.append((msg.count(uniqueList[i]), uniqueList[i], None, None))  #makes a list of tuples where each tuple is (frequency of char in msg, char, left child, right child)
    msgHeap = freq #make a heap out of freq
    heapq.heapify(msgHeap)  #heapify msgHeap
    msgLen = len(uniqueList)    #get length of message
    code = {}   #dictionary to hold the code for each character
    path = {}   #dicitionary to hold the path of each node
    root = ""   #root of heap
    done = False    #boolean for while loop
    for i in uniqueList:
        code[i] = ""    #initialize code for each char as an empty string
        path[i] = None  #initialize path for each node as null
        
    for k in range(msgLen + 1, 2*msgLen):   #create huffman tree
        i = heapq.heappop(msgHeap)  #left child is smallest freq
        j = heapq.heappop(msgHeap)  #right child is smallest freq
        heapq.heappush(msgHeap, (i[0] + j[0], i[1]+j[1], i, j)) #add new node to heap as (freq[i] + freq[j], char[i] + char[j], left child is i, right child is j)
        path[i[1]+j[1]] = (i[1], j[1])  #add new node to path, where the key is char[i]+char[j] and the value is a tuple where tuple[0] is the string from the left child and tuple[1] is the string for the right child
        if len(i[1]+j[1]) > len(root):  #if the length of the string is longer than the current root string length, update root
            root = i[1]+j[1]
            
    for i in uniqueList:    #creating the code for each node
        currentNode = root  #start at the root of the huffman tree
        temp = ""           #temp is the tuple from path
        letterCode = ""     #letterCode will be the final code
        while not done:     #while we have not found the code
            temp = path[currentNode]    #get the tuple of currentNode from path
            #print("")
            #print(i, temp)
            if temp is None:    #if it is null, then we are at a leaf and we have found the code
                done = True
            else:
                if temp[0].find(i) >= 0:    #if the char we are looking for is in temp[0], then we need to go to the left child
                    #print("went left")
                    currentNode = temp[0]   #set currentNode to the left child
                    letterCode += "0"       #add a 0 to the code
                else:                       #else, the char is in temp[1], so we need to go to the right child
                    #print("went right")
                    currentNode = temp[1]   #set currentNode to the right child
                    letterCode += "1"       #add a 1 to the code
        #print("Code for " + str(i) + " is " + str(letterCode))
        code[i] = letterCode    #add the code to the dictionary of codes
        currentNode = root      #start back at the root
        temp = ""               #reset temp
        letterCode = ""         #reset code
        done = False            #reset while loop
        
    encodedMessage = ""     #final output 
    for i in range(len(msg)):   #for each character of the msg
        encodedMessage += code[msg[i]]  #find the code for the character in code[] and concatenate onto encodedMessage
    return encodedMessage, code     #return the encoded message and the dictionary of codes

# This takes a string, cmsg, which must contain only 0s and 1s, and your 
# representation of the ``decoder ring'' ring, and returns a string msg which 
# is the decompressed message. 
def decode(cmsg, decoderRing):
    reverseDecoder = {} #need to reverse the decoder so the key is the code and the value is the char
    bufferString = ""   #buffer to see if code is in reverseDecoder
    fullString = ""     #final output
    for i in decoderRing:   #flip the decoder ring
        reverseDecoder[decoderRing[i]] = i #set key to value and vice versa
    for i in range(len(cmsg)):  #for the length of the message
        bufferString += cmsg[i] #put the 0 or 1 into bufferString
        if bufferString in reverseDecoder:  #if this is a valid code
            fullString += reverseDecoder[bufferString]  #add the char that code corresponds to into fullString
            bufferString = ""   #reset bufferString
    return fullString   #return the full string

# This takes a string, msg, and returns a tuple (compressed,\ ring) in which compressed
# is a bitstring (basically, just a number) containing the Huffman-coded message in binary, 
# and ring is again the ``decoder ring'' needed to decompress the message.
def compress(msg):
    # Initializes an array to hold the compressed message.
    compressed = array.array('B')   
    encoder = encode(msg)   #encode the message
    encodedMsg = encoder[0] #get the encoded message
    decoderRing = encoder[1]    #get the decoder ring
    byte = 0    #full byte
    bit = 0     #individual bit
    count = 0   #length of byte
    byteString = "" #string to save byte
    #print(encodedMsg)
    #print(decoderRing)
    for i in range(len(encodedMsg)):    #for each char in the encoded msg
        byteString += encodedMsg[i] #save bit into byteString
        count += 1  #increment length of byte
        #print(bin(byte), bit, count)
        if count == 8:  #if the byte is 8 chars long
            #print(bin(byte))
            byte = int(byteString, 2)   #convert 8 char string into an integer base 2
            #print(byte)
            compressed.append(byte) #add byte to bytearray
            count = 0   #reset count
            byte = 0    #reset byte
            byteString = "" #reset byteString
    #print("byte is:" + str(byte))
    if byteString:    #if there are leftover bits in byte that have not been added to byte
        #print("byte > 0")
        initialCount = len(byteString)    #find how long byte initially is
        while count != 8:       #get byte to 8 chars
            byteString += "0"     #append 0s to the end of byte
            count += 1          #increment count
        #print(bin(byte))
        extra = count - initialCount    #see how many extra 0s are added to the end of the array
        #print('extra is' + str(extra))
        byte = int(byteString, 2)   #convert 8 char string into an integer base 2
        compressed.append(byte)         #append the extra byte to the bytearray
    else:
        extra = 0   #no extra 0s added
    return compressed, (decoderRing, extra) #return the compressed array and a tuple with the decoderRing and the length of the extra bits at the end

# This takes a bitstring containing the Huffman-coded message in binary, and the 
# decoder ring needed to decompress it.  It returns the ASCII string which is the decompressed message. 
def decompress(msg, decoderRing):
    # Creates an array with the appropriate type so that the message can be decoded.
    byteArray = array.array('B',msg)
    #print(decoderRing)
    byte = ""   #byte to be decoded
    stringToDecode = "" #full string to decode
    arrayByte = 0   #byte from array
    for i in byteArray: #for each element of the bytearray
        #print(i)
        arrayByte = i   #get the byte
        byte = bin(arrayByte)   #turn it into a binary number
        byte = str(byte)        #turn it into a string
        byte = byte[2:]         #remove the "0b" from the start of the byte
        #print("")  
        #print(byte)
        while len(byte) < 8:    #if the byte is less than 8 chars, then it didn't encode the 0s at the beginning of the byte
            byte = "0" + byte   #add 0s to the front of the byte
            #print("added to byte, is now:", byte)
        stringToDecode += byte  #append the string byte to the final string
        byte = ""   #resetbyte
    #print(byte)
    #print(stringToDecode, decoderRing)
    #print(stringToDecode)
    extra = decoderRing[1] #figure out if there are extra bits that need to be removed
    if extra > 0:   #if there are extra bits
        extra = -extra  #set extra to a negative number
        stringToDecode = stringToDecode[:extra] #remove that number of bits from the end
    #print(stringToDecode)
    decodedString = decode(stringToDecode, decoderRing[0])  #decode the string
    return decodedString    #return the decoded string
# memory efficient iBWT
def ibwt(msg):
    # you may want to use unichr(termchar) returns the Unicode string for byte
    
    terminator = unichr(termchar)   #get terminating character
    #terminator = "$"
    tempChar = terminator   #set initial to look at to be the terminating character
    sortedList = sorted(msg)    #get a sorted list of the message
    sortedString = ""   #initialize a sorted string
    for i in sortedList:
        sortedString += i  #add char from the list to the string
    #print(sortedList)  
    rank = {}   #make a dictionary to hold the ranks of each char
    for i in range(len(msg)):   #for the length of the message
        if msg[i] not in rank:  #if the char is not already in the dictionary
            rank[msg[i]] = [i]  #make a new entry with the key being the char and the value being a list with the index
        else:                   #otherwise
            rank[msg[i]].append(i)  #append the index to the end of the list
                                #this makes a dictionary where we can easily find the index of each character based on rank, since the rank corresponds to the index within the list, as we add it each time we see the character
    #print(msg, rank)
    message = ""        #final message
    index = msg.index(terminator)   #get the index of the terminating character
    #rank = 0
    msgFound = False    #for the while loop, loop until we find the message

    #print(msg, sortedString, index, tempChar)
    while(not msgFound):
        #print("\nmessage: " + message + ", index: " + str(index))
        tempChar = sortedString[index]  #get the character at the index of the sorted string
        #print("tempChar: " + tempChar)
        message += tempChar     #add it to the message
        if tempChar == terminator:  #if the char is the terminating character
            msgFound = True     #end the loop
        else:               #otherwise
            ranking = index - sortedString.index(tempChar)  #find the rank of the char by finding the first occurence within the sorted string and subtracting the index from it
            #print("ranking("+ str(ranking) + ")= index(" + str(index) + ") - sortedString.index(" + str(sortedString.index(tempChar)) + ")")
            rankList = rank[tempChar]   #get the list of indicies from rank[]
            index = rankList[ranking]   #get the index of the char based on its rank
    #print(message)
    return message  #return the message

# preprocessing for text documents
def preprocessText(msg):
    msg = bwt(msg)
    return mtf(msg)    

def postprocessText(msg):
    msg = imtf(msg)
    msg = ibwt(msg)
    return msg[:-1]

# Burrows-Wheeler Transform fncs
def radix_sort(values, key, step=0):
    bwt_indices = []
    call_stack = []
    call_stack.append((values, key, step))
    while len(call_stack)>0:
        (v,key,s)=call_stack.pop();
        if len(v) < 2:
            for value in v:
                bwt_indices.append(value)
            continue
        
        bins = {}
        for value in v:
            bins.setdefault(key(value, s), []).append(value)
    
        for k in sorted(bins.keys()):
            call_stack.append((bins[k], key, s + 1))
            
    return bwt_indices[::-1]
            
# memory efficient BWT
def bwt(msg):
    def bw_key(text, value, step):
        return text[(value + step) % len(text)]
    
    msg += unichr(termchar)

    return ''.join(msg[i - 1] for i in radix_sort(range(len(msg)), partial(bw_key, msg)))

# move-to-front encoding fncs
def mtf(msg):
    # ASCII character map
    dictionary = list(''.join(chr(x) for x in range(128)))

    compressed_msg = list()
    rank = 0

    # read in each character
    for c in msg:
        rank = dictionary.index(str(c)) # find the rank of the character in the dictionary
        compressed_msg.append(rank) # update the encoded text
        
        # update the dictionary
        dictionary.pop(rank)
        dictionary.insert(0, c)

    return ''.join(unichr(x) for x in compressed_msg) # Return the encoded text as well as the dictionary

# inverse move-to-front
def imtf(compressed_msg):
    # ASCII character map
    dictionary = list(''.join(chr(x) for x in range(128)))
    
    mtf_text = ""
    rank = 0

    # for each character in the text 
    for i in compressed_msg:
        # read character rank
        rank = ord(i)
        mtf_text += str(dictionary[rank])
        
        # update dictionary
        e = dictionary.pop(rank)
        dictionary.insert(0, e)
        
    return mtf_text # Return original string

def usage():
    sys.stderr.write("Usage: {} [-c|-d|-v|-w|-t] infile outfile\n".format(sys.argv[0]))
    exit(1)

if __name__=='__main__':
    if len(sys.argv) < 4 or len(sys.argv) > 5:
        usage()
    opts = sys.argv[1:-2]
    compressing = False
    decompressing = False
    encoding = False
    decoding = False
    text = False
    for opt in opts:
        if opt == "-c":
            compressing = True
        elif opt == "-d":
            decompressing = True
        elif opt == "-v":
            encoding = True
        elif opt == "-w":
            decoding = True
        elif opt == "-t":
            text = True
        else:
            usage()

    infile = sys.argv[-2]
    outfile = sys.argv[-1]
    assert os.path.exists(infile)
    #start = time.time()

    if compressing or encoding:
        fp = open(infile, 'rb')
        sinput = fp.read()
        fp.close()
        if text:
            sinput = preprocessText(sinput)
        if compressing:
            msg, tree = compress(sinput)
            fcompressed = open(outfile, 'wb')
            marshal.dump((pickle.dumps(tree), msg), fcompressed)
            fcompressed.close()
        else:
            msg, tree = encode(sinput)
            fcompressed = open(outfile, 'wb')
            marshal.dump((pickle.dumps(tree), msg), fcompressed)
            fcompressed.close()
    else:
        fp = open(infile, 'rb')
        pck, msg = marshal.load(fp)
        tree = pickle.loads(pck)
        fp.close()
        if decompressing:
            sinput = decompress(msg, tree)
        else:
            sinput = decode(msg, tree)

        if text:
            sinput = postprocessText(sinput)
        fp = open(outfile, 'wb')
        fp.write(sinput)
        fp.close()
    #end = time.time()
    #runtime = end - start
    #print("The runtime of this compression/decompression is: " + str(runtime))
