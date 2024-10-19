class AchievementParser:

    def __init__(self, charName = None, charServer = None, fileDir = None):
        # Part to get the file
        if (fileDir == None):
            if (charName == None): # Checks if the user gave a name, if not ask for one
                raise Exception("No file directory, or character name offered")
            
            if (charServer == None): # Checks if the user gave a server, if not ask for one
                raise Exception("No file directory, or character server offered") 
        
            self.fileDir = f"C:\\Users\\Public\\Daybreak Game Company\\Installed Games\\EverQuest\\{charName}_{charServer}-Achievements.txt"

        else:
            self.fileDir = fileDir

        # Sorted achievements dictionary
        # Logic behind the dictionary -----
        # Layer one   - {Main Achievement tab Name : {}, Main Achievement tab Name : {}, Main Achievement tab Name : {}} (layout) || {"General" : {}, "Tradeskill" : {}, "The Hero's Journey" : {}} (More real example)
        # Layer two   - {Secondary Achievement tab Name : {}, Secondary Achievement tab Name : {}} (layout) || {"Class": {}, "Keys": {}} (More real example) (This Dictionary would be inside the General Dictionary)
        # Layer three - {Achievement: {}, Achievement: {}, Achievement: {}, Achievement: {}} (layout) || {"Epic 1.0": {}, "Epic 1.5": {}, "Epic 2.0": {}} (More real example)
        # Layer four  - {"Completed" : "C" (or "I"), Item 1 : "C" (or "I"), Item 2 : "C" (or "I")} (layout)|| {"Completed" : "I", "Obtain the orb of Mastery" : "I"} (More real example)
        # Overall     - {"General" : {"Class": {"Epic 1.0" : {"Completed" : "I", "Obtain the orb of Mastery" : "I"}}}}
        self.sortedAchievements = {}

    # Function to clean up the given string from the given line
    def cleanUp(self, string):
        newString = string.replace('\n', '') # Removes \n from a string
        newString = newString.replace('\t', '') # Removes \t from a string

        return newString # Returns the newly cleaned up string

    def parseAcheivementDump(self):
        self.AchievementFile = open(self.fileDir, "r") # Inputs the formed string into the file

        # Starting to iterate through the file lines
        for line in self.AchievementFile:
            if (line[1] != "\t"): # Checks for a tab (\t) in the second character of the line, if there is not one, this means it is a main tab
                mainTab, secondaryTab = line.split(":") # Splits the main tab from the secondary tab
                secondaryTab = secondaryTab[:-1][1:] # Removes the newline (\n) from the string

                if (mainTab in self.sortedAchievements.keys()): # If we have already created the tab, instead of recreating it, just add the new subtab
                    self.sortedAchievements[mainTab][secondaryTab] = {} # Adds a subtab
                
                else: # Creates a new tab and subtab
                    self.sortedAchievements[mainTab] = {} # Adds a tab
                    self.sortedAchievements[mainTab][secondaryTab] = {} # Adds a subtab
            
            # If it passes to here, checks if the line has a tab in first second char, and the first char is a C or an I or even an L (L seems to mean something im unaware of), (complete, or incomplete)        
            elif ((line[0] == "C" or line[0] == "I" or line[0] == "L") and line[1] == "\t"): 
                if (line[2] != "\t"): # Checks if it is an achievement
                    isCompleted, achievement = line.split("\t") # Split's the line into completion, and achievement
                    achievement = self.cleanUp(achievement) # cleans up the line

                    # Adds the completion tag to the achievement
                    self.sortedAchievements[mainTab][secondaryTab][achievement] = {"Completed" : isCompleted}
                
                elif (line[2] == "\t"): # Checks if it is part of an achievement
                    isCompleted = line.split("\t")[0] # splits the line into the part that shows the completion
                    achievementReq = line.split("\t")[2] # splits the line into the achievement part
                    achievementReq = self.cleanUp(achievementReq) # Cleans up the line
                
                    # Adds the ach req and the completion of it to the achievement
                    self.sortedAchievements[mainTab][secondaryTab][achievement][achievementReq] = isCompleted
            
            else: # Else to cover what happened here.....
                raise Exception(f"Something has gone wrong. Given text is {line}") # raises an exception

        # Closes the file that we opened earlier
        self.AchievementFile.close()

    def getParsedFile(self):
        return self.sortedAchievements # Returns the sorted achievements list



if __name__ == "__main__":
    achiParser = AchievementParser
    achiParser = achiParser('Cruton', 'Xegony', "C:\\Users\\Public\\Daybreak Game Company\\Installed Games\\Everquest - SK\\Hardtack_Xegony-Achievements.txt")

    achiParser.parseAcheivementDump()
    parsedAchi = achiParser.getParsedFile()

    """
    numOfExplorers = 0

    for expansion in parsedAchi.keys():
        if ('Exploration' in parsedAchi[expansion]):
            for explorer in parsedAchi[expansion]["Exploration"]:
                numOfExplorers+=1

    print('There are this many explorers: ',numOfExplorers)"""
    
    # Hunter Parser
    #print(parsedAchi['Plane of Power'].keys())
    Hunters = parsedAchi["Planes of Power"]["Hunter"]
    HunterText = ''
    for zone in Hunters.keys():
        if(zone[0] == 'H' and Hunters[zone]["Completed"] != "C"):
            HunterText = HunterText + '' + zone + '\n'
            for namer in Hunters[zone]:
                if(Hunters[zone][namer] == "I" and namer != "Completed"):
                    HunterText = HunterText + '> ' + namer + '\n'

    newFile = open('D:\\EQ-Parses\\Winyanya_PoP_Hunters.txt', "w")
    newFile.write(HunterText)
    newFile.close()