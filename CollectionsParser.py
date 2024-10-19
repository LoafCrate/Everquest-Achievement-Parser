# Imports the achivement parser, that we will use as the base of the collection parser
import Achievement_Parser as parser
import json

# Class for the collection parser
class CollectionParser:

    """
    To use this you have to initialize it with a character name and server, or the file directory of your file
    Then you can call collectionParser to recheck the file, or you can use call another command like getIncompleteCollects to get the incomplete collects
    """
    def __init__(self, charName = None, charServer = None, fileDir = None):
        # Sets up the achivement parser
        self.achievementParser = parser.AchievementParser
        self.openParsers = {} # Dictionary with the current open parsers
        
        # Creates the first achievement instance if the charName and server are given, or a file directory  
        if((charName != None and charServer != None) or fileDir != None):
            self.newAchParserInstance(charName, charServer, fileDir)

    """Opens a new instance of the achievement parser, to get the list of achievements from it."""
    def newAchParserInstance(self, charEQName = 'EverQuest', charName = None, charServer = None, fileDir = None):
        # Part to get the file
        if (fileDir == None):
            if (charName == None): # Checks if the user gave a name, if not ask for one
                raise Exception("No file directory, or character name offered")
            
            if (charServer == None): # Checks if the user gave a server, if not ask for one
                raise Exception("No file directory, or character server offered") 

            # file directory created by assuming a few things
            fileDir = f"C:\\Users\\Public\\Daybreak Game Company\\Installed Games\\{charEQName}\\{charName}_{charServer}-Achievements.txt"

        else:
            pass
        
        # Sets the achievement parser stuffs
        self.currentToon = f"{charName}, {charServer}"
        self.currentAchParser = self.achievementParser(charName, charServer, fileDir) # Sets the current parser to the one made
        self.openParsers[self.currentToon] = {"characterID":[self.currentAchParser, fileDir], "Collection Sets":{}} # Adds it to the list of parsers made
        self.collectionParser() # Gets the new achievement dump

    """Goes to another parsed player"""
    def swapCurrentParser(self, charName = None, charServer = None, fileDir = None):
        swapToon = f"{charName}, {charServer}" # Makes the swap toon

        # Checks if the toon to swap to exists
        if (swapToon in self.openParsers):
            # If it does, set the current toon to the one we are swapping to
            self.currentToon = swapToon
            self.currentAchParser = self.openParsers[self.currentToon]["characterID"][0]
            # Returns a success message
            return {"Success" : True,"Description":f"New current character is {self.currentToon}."}
        else:
            # Returns a fail message
            return {"Success" : False,"Description":f"Character {swapToon} does not exist."}

    """Goes through the given achievement file, and grabs all the collections, this function can also be used to refresh the old collection log"""
    def collectionParser(self):
        self.currentAchParser.parseAcheivementDump() # Parses the achievement log
        currentAchFile = self.currentAchParser.getParsedFile() # Retrives a dictionary with the parsed achievements file
        expansionsWithCollects = [] # A list that will have all the EQ xpacs that have a collection tab
        collectionsParsed = {}

        # Gets all of the expansions that have collections
        for tab in currentAchFile.keys():
            # Checks if the tab has a collection section, if not ignore
            if("Collections" in currentAchFile[tab].keys()):
                expansionsWithCollects.append(tab)

        # Runs through each expansion of collects, and grabs them all, then puts them in a usable list kinda ish
        for expansion in expansionsWithCollects:
            collectionsParsed[expansion] = currentAchFile[expansion]["Collections"]
        
        # Gives the open parser, the collection sets that we just saved so that we dont have to reget the parsed achievement file, and go over it again
        self.openParsers[self.currentToon]["Collection Sets"] = collectionsParsed

    """The idea of this function is to take a dictionary, and remove any empty dictionaryies from it"""
    def _dictCleanUp(self, handedDict):
        uncleanDictionary = handedDict # The unclean dictionary that we will clean up
        cleanDictionary = {}
        
        # Loops through dictionary, if a dictionary or list in it is empty, throw it away
        # If there is a dictionary in the dictionary, it checks through that as well and cleans that
        for dictionary in uncleanDictionary:
            if (uncleanDictionary[dictionary] == {} or uncleanDictionary[dictionary] == []):
                pass
            else:
                if (type(uncleanDictionary[dictionary]) == dict):
                    cleanDictionary[dictionary] = self._dictCleanUp(uncleanDictionary[dictionary])
                
                else:
                    cleanDictionary[dictionary] = uncleanDictionary[dictionary]

        return(cleanDictionary)

    """Returns a dictionary of all the collections, sorted by expansion / of the specifically request expansion"""
    def getAllCollects(self, expansion = None):
        expansionsToCheck = [] # List of the expansions the program will check

        # Checks if specific expansion(s) were provided, and if it was 1 or multiple, if not, check all of them
        if(expansion == None):
            expansionsToCheck = self.openParsers[self.currentToon]["Collection Sets"].keys()
        else:
            if (type(expansion) != list):
                expansionsToCheck.append(expansion)
            else:
                expansionsToCheck = expansion

        # Dictionary that will carry the complete collects
        # {Xpansion:{Collect Set:{Collection:I}}}
        completeCollects = {}
        
        # Goes through each expansion we've given it, and checks for the complete ones
        for xpac in expansionsToCheck: # Goes throught he given xpacs
            completeCollects[xpac] = {"numCollects" : 0} # Sets the xpansion, and the complete collect slot
             
            for collectSet in self.openParsers[self.currentToon]["Collection Sets"][xpac]: # Goes through each collection set in the xpansions
                completeCollects[xpac][collectSet] = {}
                for collection in self.openParsers[self.currentToon]["Collection Sets"][xpac][collectSet]: # Goes through each collection
                    if (len(self.openParsers[self.currentToon]["Collection Sets"][xpac][collectSet]) <= 5):
                        pass
                    elif(collection == "Completed"):
                        completeCollects[xpac][collectSet][collection] = self.openParsers[self.currentToon]["Collection Sets"][xpac][collectSet][collection] # Adds the collect
                    # Adds the collection, we don't need to compare because we are adding every collect, so we can just add the collect, and the sign behind it
                    else:
                        completeCollects[xpac]["numCollects"]+=1 # Adds one to the expansion collects tally
                        completeCollects[xpac][collectSet][collection] = self.openParsers[self.currentToon]["Collection Sets"][xpac][collectSet][collection] # Adds the collect
                    
        completeCollects = self._dictCleanUp(completeCollects)

        # Returns the incomplete collections
        return completeCollects
    
    """Returns a dictionary of all the incomplete collections, sorted by expansion / of the specifically request expansion"""
    def getIncompleteCollects(self, expansion = None):
        expansionsToCheck = [] # List of the expansions the program will check

        # Checks if specific expansion(s) were provided, and if it was 1 or multiple, if not, check all of them
        if(expansion == None):
            expansionsToCheck = self.openParsers[self.currentToon]["Collection Sets"].keys()
        else:
            if (type(expansion) != list):
                expansionsToCheck.append(expansion)
            else:
                expansionsToCheck = expansion

        # Dictionary that will carry the incomplete collects
        # {Xpansion:{Collect Set:{Collection:I}}}
        incompleteCollects = {}
        
        # Goes through each expansion we've given it, and checks for the incomplete ones
        for xpac in expansionsToCheck: # Goes throught he given xpacs
            incompleteCollects[xpac] = {"numCollects" : 0} # Sets the xpansion, and the missing collect slot
             
            for collectSet in self.openParsers[self.currentToon]["Collection Sets"][xpac]: # Goes through each collection set in the xpansions
                incompleteCollects[xpac][collectSet] = {}
                # Checks if the set is done, if so pass it
                if(self.openParsers[self.currentToon]["Collection Sets"][xpac][collectSet]["Completed"] == "C" or len(self.openParsers[self.currentToon]["Collection Sets"][xpac][collectSet]) <= 5): 
                    pass
                
                else: # If it's not done, check the collections
                    for collection in self.openParsers[self.currentToon]["Collection Sets"][xpac][collectSet]: # Goes through each collection
                        if (self.openParsers[self.currentToon]["Collection Sets"][xpac][collectSet][collection] == "C"): # If the collection is done, skip it (or if it's the placeholder to check if the set is done)
                            pass
                        elif(collection == "Completed"):
                            incompleteCollects[xpac][collectSet][collection] = self.openParsers[self.currentToon]["Collection Sets"][xpac][collectSet][collection] # Completed tag
                        else: # If the collect isn't done, add 1 to the collection tally, and add it to the list
                            incompleteCollects[xpac]["numCollects"]+=1 # Adds one to the expansion collects tally
                            incompleteCollects[xpac][collectSet][collection] = "I" # Adds the collect
        
        incompleteCollects = self._dictCleanUp(incompleteCollects)

        # Returns the incomplete collections
        return incompleteCollects

    """Returns a dictionary of all the complete collections, sorted by expansion / of the specifically request expansion"""
    def getCompleteCollects(self, expansion = None):
        expansionsToCheck = [] # List of the expansions the program will check

        # Checks if specific expansion(s) were provided, and if it was 1 or multiple, if not, check all of them
        if(expansion == None):
            expansionsToCheck = self.openParsers[self.currentToon]["Collection Sets"].keys()
        else:
            if (type(expansion) != list):
                expansionsToCheck.append(expansion)
            else:
                expansionsToCheck = expansion

        # Dictionary that will carry the complete collects
        # {Xpansion:{Collect Set:{Collection:C}}}
        completeCollects = {}
        
        # Goes through each expansion we've given it, and checks for the complete ones
        for xpac in expansionsToCheck: # Goes throught he given xpacs
            completeCollects[xpac] = {"numCollects" : 0} # Sets the xpansion, and the complete collect slot
             
            for collectSet in self.openParsers[self.currentToon]["Collection Sets"][xpac]: # Goes through each collection set in the xpansions
                completeCollects[xpac][collectSet] = {}
                for collection in self.openParsers[self.currentToon]["Collection Sets"][xpac][collectSet]: # Goes through each collection
                    # If the collection is not done, skip it (or if it's the placeholder to check if the set is done)
                    if ((self.openParsers[self.currentToon]["Collection Sets"][xpac][collectSet][collection] == "I" and collection != "Completed") or 
                        len(self.openParsers[self.currentToon]["Collection Sets"][xpac][collectSet]) <= 5): 
                        pass
                    elif(collection == "Completed"):
                        completeCollects[xpac][collectSet][collection] = self.openParsers[self.currentToon]["Collection Sets"][xpac][collectSet][collection] # Completed tag
                    else: # If the collect is done, add 1 to the collection tally, and add it to the list
                        completeCollects[xpac]["numCollects"]+=1 # Adds one to the expansion collects tally
                        completeCollects[xpac][collectSet][collection] = "C" # Adds the collect
                
                if(len(completeCollects[xpac][collectSet]) == 1):
                    del completeCollects[xpac][collectSet]
        
        completeCollects = self._dictCleanUp(completeCollects)

        # Returns the complete collections
        return completeCollects

    """Function to make a more pretty version of a collection dictionary that we passed to the user."""
    def prettyPrint(self, collections):
        # String that will be used to post the finished string
        prettyPrintString = "" 
        totalCollects = 0
        
        # Make a shallow copy of collections
        printColl = collections.copy()

        # Loops through each xpac passed to it
        for expac in printColl: 
            prettyPrintString = f"{prettyPrintString}{expac} ({printColl[expac]['numCollects']})\n" # Adds the xpac to the string & the number of collects it has
            totalCollects += printColl[expac]["numCollects"] # adds to the total
            
            # Deletes the number of collects count because that just causes issues
            printColl[expac].pop("numCollects")
            
            # Loops through the collection sets in the expansion
            for collectionSet in printColl[expac]:
                if (collectionSet == 'Completed'):
                    pass
                else:
                    # Adds the set we are about to loop through to the pretty string
                    prettyPrintString = f"{prettyPrintString}*  {collectionSet}\n" 
                    
                    # Loops through the collections in the set
                    for collection in printColl[expac][collectionSet]:
                        
                        if (collection != 'Completed'):
                            # Adds the collection to the pretty string
                            prettyPrintString = f"{prettyPrintString}{printColl[expac][collectionSet][collection]}\t- {collection}\n" 
            
            # Newline
            prettyPrintString = f"{prettyPrintString}\n"

        # Finishing the string, and returning it to the user
        prettyPrintString = f"{prettyPrintString}Total counted collects: {totalCollects}"
        return prettyPrintString
    
    """Function to dump all the data of the collections given to it, into a file, can take a dictionary or a string, depending on if you want to dump a base dict, or a pretty printed one"""
    def dataDump(self, loc:str, collections:dict|str):
        # Incredibly basic open file, and write the given text to it
        if(type(collections) == str):
            newFile = open(loc, "w")
            newFile.write(collections)
            newFile.close()
        else:
            newFile = open(loc, "w")
            json.dump(collections, newFile, ensure_ascii=False, indent=4)
            newFile.close()

if __name__ == "__main__":
    collectParserClass = CollectionParser
    collectionParser = collectParserClass('Everquest - SK', 'Hardtack', 'Xegony')
    
    """parsedIncompleteCollectsHardtack = collectionParser.getIncompleteCollects(["Call of the Forsaken", "The Darkened Sea", "The Broken Mirror", "Empires of Kunark",
                                                                            "Ring of Scale", "Torment of Velious", "Claws of Veeshan", "Terror of Luclin",
                                                                            "Night of Shadows", "Laurion's Song"])"""
    

    parsedIncompleteCollectsHardtack = collectionParser.getIncompleteCollects(["Laurion's Song"])
    collectionParser.dataDump(f"D:\\EQ-Parses\\Hardtack_Collections_all.txt", collectionParser.prettyPrint(parsedIncompleteCollectsHardtack))

    # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #

    collectParserClass2 = CollectionParser
    collectionParser2 = collectParserClass2('Everquest - Rogue', 'Roeweena', 'Xegony')
    
    """parsedIncompleteCollectsCruton = collectionParser2.getIncompleteCollects(["Call of the Forsaken", "The Darkened Sea", "The Broken Mirror", "Empires of Kunark",
                                                                            "Ring of Scale", "Torment of Velious", "Claws of Veeshan", "Terror of Luclin",
                                                                            "Night of Shadows", "Laurion's Song"])"""
    

    parsedIncompleteCollectsCruton = collectionParser2.getIncompleteCollects(["Laurion's Song"])
    collectionParser2.dataDump(f"D:\\EQ-Parses\\Roeweena_Collections_all.txt", collectionParser2.prettyPrint(parsedIncompleteCollectsCruton))

    # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #
    # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- #

    collectParserClass2 = CollectionParser
    collectionParser2 = collectParserClass2('Everquest - Mage', 'Winyanya', 'Xegony')
    
    """parsedIncompleteCollectsCruton = collectionParser2.getIncompleteCollects(["Call of the Forsaken", "The Darkened Sea", "The Broken Mirror", "Empires of Kunark",
                                                                            "Ring of Scale", "Torment of Velious", "Claws of Veeshan", "Terror of Luclin",
                                                                            "Night of Shadows", "Laurion's Song"])"""
    

    parsedIncompleteCollectsCruton = collectionParser2.getIncompleteCollects(["Ring of Scale"])
    collectionParser2.dataDump(f"D:\\EQ-Parses\\Winyanya_Collections_all.txt", collectionParser2.prettyPrint(parsedIncompleteCollectsCruton))