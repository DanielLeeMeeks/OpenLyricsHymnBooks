from selenium import webdriver
import time
import datetime

def intToString(number):
    if number < 10:
        return "00"+str(number)
    elif number < 100:
        return "0"+str(number)
    else:
        return str(number)

def writeWarning(input):
    print("[WARNING] " + input)
    with open(hymnalCode+"/warning.txt", "a") as warningFile:
        warningFile.write("\n" + input)

hymnalCode = "FHOP"
hymnalName = "Favorite Hymns of Praise‎"
count = 1

ccliEmail = "YOUR_CCLI_EMAIL_HERE"
ccliPassword = "YOUR_CCLI_PASSWORD_HERE"

web = webdriver.Chrome("drivers/chromedriver.exe")
web.set_page_load_timeout("10")

web.get("https://profile.ccli.com/account/signin")
web.find_element_by_id("EmailAddress").send_keys(ccliEmail)
web.find_element_by_id("Password").send_keys(ccliPassword)
web.find_element_by_id("Sign-In").click()

while True:

    hymnAuthor = []
    hymnPublicationDate = ""
    hymnSource = ""
    hymnCopywrite = "Public Domain"
    hymnCCLI = ""
    hymnKey = ""
    hymnComment = []
    hymnTopics = []
    web.get("https://hymnary.org/hymn/" + hymnalCode + "/" + str(count) + "#text")

    try:
        if (web.find_element_by_tag_name("h1").text == "Page Not Found"):
            print("Page " + str(count) + " not found.  May have finished.")
            break
    except:
        True

    try:
        li = web.find_element_by_class_name("accept_license_box")
        time.sleep(2)
        web.find_elements_by_class_name("submit-license")[1].click()
        print(str(count) + " - " + li.text)
        hymnComment.append(li.text)
    except Exception as e:
        True
        #print(str(count) + " " + str(e))

    try:
        web.find_element_by_class_name("js-link").click()
    except:
        True

    try:
        text = web.find_element_by_id("text").text
    except Exception as e:
        text = "Chorus:\nCould not scrap this song.\nError: " + str(e) + "."
        writeWarning("Could not scrap song " + str(count)+".")
        hymnComment.append("Could not scrap this song.")
    textArray = text.split("\n")
    #print(textArray)
    title = web.find_element_by_class_name("hymntitle").text.split(". ")[1]
    infoTable = web.find_elements_by_class_name("infoTable")
    infoTableText = infoTable[0].text.split("\n")
    infoTableTune = infoTable[1].text.split("\n")
    #print(infoTable)

    for line in infoTableText:
        org = line
        line = line.split(": ")
        if "Translator" in line[0] or "Author" in line[0] or "Alterer" in line[0] or "Adapter" in line[0]:
            hymnAuthor.append(line[1])
        elif line[0] == "Original Language":
            True #do nothing
        elif line[0] == "Publication Date":
            hymnPublicationDate = line[1]
        elif line[0] == "Topic":
            org = org.replace("Topic: ", "")
            hymnTopics = org.split(";")
        elif line[0] == "Source":
            hymnSource = line[1]
        elif line[0] == "First Line":
            True #do nothing
        elif line[0] == "Text Information":
            True #do nothing
        elif line[0] == "Title":
            True #do nothing
        elif line[0] == "Copyright":
            hymnCopywrite = line[1]
        elif line[0] == "Refrain First Line":
            True #do nothing
        elif line[0] == "Notes":
            hymnComment.append(line[1])
        elif line[0] == "Language":
            True #do nothing
        elif line[0] == "Scripture":
            hymnComment.append(line[1])
        else:
            writeWarning("Did not know what to do with " + line[0] + " of "+str(count)+" (Text)")

    for line in infoTableTune:
        if line[0] == "Key":
            hymnKey = line[1]

    try:
        ###Find CCLI
        web.get("https://songselect.ccli.com/")
        if (len(hymnAuthor) > 0):
            if (hymnAuthor[0] != "Unknown"):
                web.find_element_by_id("SearchText").send_keys(title + " " + hymnAuthor[0])
            else:
                web.find_element_by_id("SearchText").send_keys(title)
        else:
            web.find_element_by_id("SearchText").send_keys(title)

        web.find_element_by_class_name("icon-search").click()

        web.find_elements_by_class_name("song-result-title")[0].find_element_by_tag_name("a").click()

        hymnCCLI = web.find_element_by_class_name("song-content-data").find_element_by_tag_name("ul").find_elements_by_tag_name("li")[0].find_element_by_tag_name("strong").text
    except:
        writeWarning("Could not find CCLI for " + str(count) + ". " + title + " (" + hymnCopywrite + ")")
        hymnComment.append("Could not find CCLI number.")

    now = datetime.datetime.now()
    s = "%Y-%m-%dT%H:%M+04:00"

    output = "<song xmlns=\"http://openlines.info/namespace/2009/song\" " \
             "version=\"0.8\" " \
             "createdIn=\"Hymnary.org Scrapper 0.0.1\" " \
             "modifiedIn=\"Hymnary.org Scrapper 0.0.1\" " \
             "modifiedDate=\""+now.strftime(s)+"\">\n" \
             "\t<properties>\n\t\t<titles>\n\t\t\t<title>" + title + "</title>\n\t\t</titles>"
    output += "\n\t\t<authors>"
    if len(hymnAuthor) > 0:
        for author in hymnAuthor:
            output += "\n\t\t\t<author>"+author+"</author>"
        output += "\n\t\t</authors>"
    output += "\n\t\t<copyright>"+ hymnCopywrite +"</copyright>"
    output += "\n\t\t<ccliNo>"+hymnCCLI+"</ccliNo>"
    output += "\n\t\t<released>"+"</released>"
    output += "\n\t\t<key>"+hymnKey+"</key>"
    if len(hymnTopics) > 0:
        output += "\n\t\t<themes>"
        for t in hymnTopics:
            output += "<theme>" + t + "</theme>"
        output += "</themes>"
    output += "\n\t\t<songbooks>\n\t\t\t<songbook name=\"" + hymnalName.replace("?", "") + "\" entry=\"" + str(count) + "\"/>\n\t\t</songbooks>"
    if len(hymnComment) > 0:
        output += "\n\t\t<comments>"
        for comment in hymnComment:
            output += "\n\t\t\t<comment>" + comment + "</comment>"
        output += "\n\t\t</comments>"
    output += "\n\t</properties>"

    output += "\n\t<lyrics>"
    firstLine = True
    firstLineInVerse = True
    for line in textArray:
        includeLine = True

        if (line == "Refrain:" or line == "Chorus:"):
            includeLine = False
            if not firstLine:
                output += "</lines>\n\t\t</verse>"
            output += "\n\t\t<verse name=\"c\">\n\t\t<lines>"
            firstLineInVerse = True
        elif line[0] == "1":
            if not firstLine:
                output += "</lines>\n\t\t</verse>"
            output += "\n\t\t<verse name=\"v1\">\n\t\t\t<lines>"
            firstLineInVerse = True
            line = line.replace("1 ", "")
        elif line[0] == "2":
            if not firstLine:
                output += "</lines>\n\t\t</verse>"
            output += "\n\t\t<verse name=\"v2\">\n\t\t\t<lines>"
            firstLineInVerse = True
            line = line.replace("2 ", "")
        elif line[0] == "3":
            if not firstLine:
                output += "</lines>\n\t\t</verse>"
            output += "\n\t\t<verse name=\"v3\">\n\t\t\t<lines>"
            firstLineInVerse = True
            line = line.replace("3 ", "")
        elif line[0] == "4":
            if not firstLine:
                output += "</lines>\n\t\t</verse>"
            output += "\n\t\t<verse name=\"v4\">\n\t\t\t<lines>"
            firstLineInVerse = True
            line = line.replace("4 ", "")
        elif line[0] == "5":
            if not firstLine:
                output += "</lines>\n\t\t</verse>"
            output += "\n\t\t<verse name=\"v5\">\n\t\t\t<lines>"
            firstLineInVerse = True
            line = line.replace("5 ", "")
        elif line[0] == "6":
            if not firstLine:
                output += "</lines>\n\t\t</verse>"
            output += "\n\t\t<verse name=\"v6\">\n\t\t\t<lines>"
            firstLineInVerse = True
            line = line.replace("6 ", "")
        elif line[0] == "7":
            if not firstLine:
                output += "</lines>\n\t\t</verse>"
            output += "\n\t\t<verse name=\"v7\">\n\t\t\t<lines>"
            firstLineInVerse = True
            line = line.replace("7 ", "")
        elif line[0] == "8":
            if not firstLine:
                output += "</lines>\n\t\t</verse>"
            output += "\n\t\t<verse name=\"v8\">\n\t\t\t<lines>"
            firstLineInVerse = True
            line = line.replace("8 ", "")
        elif line[0] == "9":
            if not firstLine:
                output += "</lines>\n\t\t</verse>"
            output += "\n\t\t<verse name=\"v9\">\n\t\t\t<lines>"
            firstLineInVerse = True
            line = line.replace("9 ", "")
        elif line[0] == "10":
            if not firstLine:
                output += "</lines>\n\t\t</verse>"
            output += "\n\t\t<verse name=\"v10\">\n\t\t\t<lines>"
            firstLineInVerse = True
            line = line.replace("10 ", "")
        if "This media is licensed" in line:
            includeLine = False
        if includeLine:
            if not firstLineInVerse:
                output += "\n"
            output += line.replace("(Refrain)", "").replace("(Chorus)", "")
            firstLineInVerse = False
        firstLine = False
    output += "</lines>\n\t\t</verse>\n\t</lyrics>\n</song>"

    textFile = open(hymnalCode + "/" + intToString(count) + ". " + title.replace("?", "").replace("\"", "") + ".xml", "wt", encoding="utf-8")
    textFile.write(output)
    textFile.close()

    songlist = open(hymnalCode + "/000. songlist.txt", "a", encoding="utf-8")
    songlistOutput = str(count) + ". " + title + " ("
    firstAut = True
    for aut in hymnAuthor:
        if firstAut != True:
            songlistOutput += ", "
        firstAut = False
        songlistOutput += aut
    songlistOutput += ")\n"
    for com in hymnComment:
        songlistOutput += "\t" + com + "\n"
    songlist.write(songlistOutput)
    songlist.close()

    #print(output)
    count = count + 1
    time.sleep(3)

web.close()