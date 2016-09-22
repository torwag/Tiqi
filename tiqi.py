#!/usr/bin/env python
# encoding: utf-8

# (c) Wiltrud Kessler, 5.11.13
# Do with this code whatever you want :)

"""
Create an ILIAS question pool from a text file
(because doing this in ILIAS is annoying).

You will get an XML file that you can import into ILIAS.
"""

import sys
import re


header = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n<!DOCTYPE questestinterop SYSTEM \"ims_qtiasiv1p2p1.dtd\">\n<!--Generated by ILIAS XmlWriter-->\n<questestinterop>\n"

footer = "</questestinterop>\n"

# For the whole question (open/close)
itemopen = "  <item ident=\"%s\" title=\"%s\" maxattempts=\"1\">\n"   # depending on title and id
itemclose = "  </item>\n"

# textgaprating = ci -> case insensitive
# textgaprating = cs -> case sensitive

# Metadata (whole question, tpye, other info)
questionTypeGap = "CLOZE QUESTION"
questionTypeMCSingle = "SINGLE CHOICE QUESTION"
questionTypeMCMulti = "MULTIPLE CHOICE QUESTION"
itemmetadata = "    <qticomment/>\n    <duration>P0Y0M0DT0H1M0S</duration>\n    <itemmetadata>\n      <qtimetadata>\n        <qtimetadatafield>\n          <fieldlabel>ILIAS_VERSION</fieldlabel>\n          <fieldentry>4.3.5 2013-10-08</fieldentry>\n        </qtimetadatafield>\n        <qtimetadatafield>\n          <fieldlabel>QUESTIONTYPE</fieldlabel>\n          <fieldentry>%s</fieldentry>\n        </qtimetadatafield>\n        <qtimetadatafield>\n          <fieldlabel>AUTHOR</fieldlabel>\n          <fieldentry>TIQI - The ILIAS Question Importer</fieldentry>\n        </qtimetadatafield>\n        <qtimetadatafield>\n          <fieldlabel>textgaprating</fieldlabel>\n          <fieldentry>cs</fieldentry>\n        </qtimetadatafield>\n        <qtimetadatafield>\n          <fieldlabel>fixedTextLength</fieldlabel>\n          <fieldentry/>\n        </qtimetadatafield>\n        <qtimetadatafield>\n          <fieldlabel>identicalScoring</fieldlabel>\n          <fieldentry>1</fieldentry>\n        </qtimetadatafield>\n      </qtimetadata>\n    </itemmetadata>\n" # depending on question type

# Question presentation (whole question open/close)
itempresentationopen = "    <presentation label=\"%s\">\n      <flow>\n" # depending on title
itempresentationclose = "      </flow>\n    </presentation>\n"

# Question presentation (question parts)
insertquestiontext = "        <material>\n          <mattext texttype=\"text/xhtml\">%s%s%s</mattext>\n        </material>\n"  # depending on text
insertgap = "        <response_str ident=\"gap_%i\" rcardinality=\"Single\">\n          <render_fib fibtype=\"String\" prompt=\"Box\" columns=\"0\">\n          </render_fib>\n        </response_str>\n"  # depending on gap id
insertMCsingleopen = "        <response_lid ident=\"MCSR\" rcardinality=\"Single\">\n          <render_choice shuffle=\"Yes\">\n"
insertMCmultiopen = "        <response_lid ident=\"MCMR\" rcardinality=\"Multiple\">\n          <render_choice shuffle=\"Yes\">\n"
insertMCclose = "      </render_choice>\n   </response_lid>\n"
insertMC = "            <response_label ident=\"%i\">\n               <material>\n                 <mattext texttype=\"text/plain\">%s</mattext>\n             </material>\n         </response_label>\n" # depending on item id and text

# Question responses/answers (whole question open/close)
itemresprocessingopen = "    <resprocessing>\n      <outcomes>\n        <decvar>\n        </decvar>\n      </outcomes>\n"
itemresprocessingclose = "    </resprocessing>\n"

# Question responses/answers (question parts)
itemresprocessingGap = "      <respcondition continue=\"Yes\">\n        <conditionvar>\n          <varequal respident=\"gap_%i\">%s</varequal>\n        </conditionvar>\n        <setvar action=\"Add\">%f</setvar>\n        <displayfeedback feedbacktype=\"Response\" linkrefid=\"%i_Response_0\"/>\n      </respcondition>\n" # depends on gap id, points
itemresprocessingMCChecked = "      <respcondition continue=\"Yes\">\n        <conditionvar>\n          <varequal respident=\"MCSR\">%i</varequal>\n        </conditionvar>\n        <setvar action=\"Add\">%f</setvar>\n        <displayfeedback feedbacktype=\"Response\" linkrefid=\"response_%i\"/>\n      </respcondition>\n" # depends on answer id, points, answer id
itemresprocessingMCUnchecked = "      <respcondition continue=\"Yes\">\n        <conditionvar>\n          <not>\n          <varequal respident=\"MCSR\">%i</varequal>\n          </not>\n        </conditionvar>\n        <setvar action=\"Add\">%f</setvar>\n        <displayfeedback feedbacktype=\"Response\" linkrefid=\"Response_%i\"/>\n      </respcondition>\n" # depends on answer id, points, answer id


# Question feedback (whole question)
itemfeedbackGap = "    <itemfeedback ident=\"%i_Response_0\" view=\"All\">\n      <flow_mat>\n        <material>\n          <mattext/>\n        </material>\n      </flow_mat>\n    </itemfeedback>\n"
itemfeedbackMC = "    <itemfeedback ident=\"response_%i\" view=\"All\">\n      <flow_mat>\n        <material>\n          <mattext/>\n        </material>\n      </flow_mat>\n    </itemfeedback>\n"



# used to split the text into parts
# Gaps: each gap is surrounded by [gap][/gap]
gapre = '\[gap\]([^\[\]]*)\[/gap\]'
# multiple choice: Either - or _ at beginning of line followed by space
mcre = '&lt;br/&gt;- '



def createQuestion (questionType, questionText):
   
   # Prepare
   itempresentationelems = ""
   itemfeedbackelems = ""
   itemresprocessingelems = ""
   
   # Gap questions
   if questionType == questionTypeGap:
      textparts = re.split(gapre, questionText)
      # should give 1 point in total, each gap = 1/#gaps
      points = round(1.0 / ( len(textparts) / 2),2)
      #  print "we have %i parts = %i gaps = %f points per gap" % (len(textparts), ( len(textparts) / 2.0), points) # TEST !!!
      for i in range(0,len(textparts)):
         
         before = ""
         if i == 0: # first item (start paragraph)
            before = "&lt;p&gt;"
         after = ""
         if i == len(textparts)-1: # last item (end paragraph)
            after =  "&lt;/p&gt;"
            
         gaptext = textparts[i]
         if i % 2 == 0: # Outside of gap
            itempresentationelems += insertquestiontext % (before, gaptext, after)
         else: # inside of gap
            gapno = (i/2)
            if i >= len(textparts)-2: # this is the last gap, add remainder of points
               points = 1 - (gapno) * points
            itempresentationelems += insertgap % (gapno)
            itemresprocessingelems += itemresprocessingGap % (gapno, gaptext, points, gapno)
            itemfeedbackelems += itemfeedbackGap % (gapno)
      print "   have %d gaps, %d point(s) in total" % (len(textparts)-1, points)

   
   # Multiple choice questions
   elif questionType == questionTypeMCSingle or questionType == questionTypeMCMulti :
      multi = False
      if questionType == questionTypeMCMulti:
         multi = True
         
      questionText =  re.sub("&lt;br/&gt;_", "&lt;br/&gt;- _", questionText)
      textparts = re.split(mcre, questionText)
      
      # Question text
      before = "&lt;p&gt;"
      after =  "&lt;/p&gt;"
      itempresentationelems += insertquestiontext % (before, textparts[0], after)
      if multi:
         itempresentationelems += insertMCmultiopen
      else:
         itempresentationelems += insertMCsingleopen
      
      # Points
      if multi: # multiple correct answers: should give 1 point in total, each item = 1/#items
         points = round(1.0 / ( len(textparts)-1 ),2)
      else: # single correct answer = 1 point
         points = 1 
      pointsassigned = 0 # sanity check
      
      # Answer possibilities
      for i in range(1,len(textparts)):
         
         parttext = textparts[i]
         answerid = i-1
            
         if i == len(textparts)-1 and multi: # last item and multiple selection possible, add remainder of points # TODO this is a little bit unfair
            #  points = 1 - ((len(textparts)-2) * points)
            points = 1 - pointsassigned
            
         if parttext[0:1] == "_": # correct when checked
            itempresentationelems += insertMC % (answerid, parttext[2:])
            itemresprocessingelems += itemresprocessingMCChecked % (answerid, points, answerid)
            pointsassigned += points # sanity check
            if multi: # add also what happens if NOT checked
               itemresprocessingelems += itemresprocessingMCUnchecked % (answerid, 0, answerid)
               
         else: # wrong when checked, i.e., correct when unchecked
            itempresentationelems += insertMC % (answerid, parttext)
            itemresprocessingelems += itemresprocessingMCChecked % (answerid, 0, answerid)
            if multi: # add also what happens if NOT checked
               itemresprocessingelems += itemresprocessingMCUnchecked % (answerid, points, answerid)
               pointsassigned += points # sanity check
         itemfeedbackelems += itemfeedbackMC % (answerid)
         

      if pointsassigned != 1.0: # sanity check
         print "!! WARNING !! something is wrong, I just assigned %.2f points to this questions!" % (pointsassigned)
      itempresentationelems += insertMCclose
      print "   have %d answer choices, %d point(s) in total" % (len(textparts)-1, pointsassigned)
      

   else:
      print "!! ERROR !! something is wrong, I don't know this type of question."
      return None, None, None

   return itempresentationelems, itemfeedbackelems, itemresprocessingelems




def convertFile (inputFile, outputFile):

   outputFile.write(header)

   lineno = 0
   inItem = False
   questionText = ""
   questionType = ""
   questionTitle = ""
   questionno = 0
   
   for line in inputFile:
      line = line.strip()
      lineno += 1
      
      if line == "" and inItem: # End of item -> prepare, print & reset
         questionno+=1
         
         # Prepare question
         print id + " " + questionType + " " + questionTitle # TEST !!!
         itempresentationelems, itemfeedbackelems, itemresprocessingelems = createQuestion (questionType, questionText)
         
         # Print
         if (itempresentationelems != None):
            outputFile.write( itemopen % (id, questionTitle) )
            outputFile.write( itemmetadata % questionType )
            outputFile.write( itempresentationopen % (questionTitle) )
            outputFile.write( itempresentationelems )
            outputFile.write( itempresentationclose )
            outputFile.write( itemresprocessingopen )
            outputFile.write( itemresprocessingelems )
            outputFile.write( itemresprocessingclose )
            outputFile.write( itemfeedbackelems )
            outputFile.write( itemclose )
         
         # Reset
         questionText = ""
         questionType = ""
         title = ""
         inItem = False
         continue
      
      if line == "" and not inItem: # Ignore empty lines
         continue
      
      if line[0] == "#": # Ignore comments
         continue
      
      if line[0:3] == "[t]": # Have title -> create new question
         inItem = True
         id = "il_0_qst_" + str(lineno) # id comes from line number
         
          # Type
         if line[3:6] == "[s]": # multiple choice, single answer
            questionType = questionTypeMCSingle
         if line[3:6] == "[m]": # multiple choice, multiple answers
            questionType = questionTypeMCMulti
         elif line[3:6] == "[g]": # gap question
            questionType = questionTypeGap
            
         # Title
         questionTitle = line[6:].strip()
         continue
      
      # Have (maybe several lines) of question text
      # Just add this to what I have had before
      if questionText == "":
         questionText = line
      else:
         questionText = questionText + "&lt;br/&gt;" +  line
      
   outputFile.write(footer)
   print "Found %d questions.\n" % (questionno)
   
   
#### MAIN ####

if len(sys.argv)<=1:
   print "Error! Give me one or more input files as parameter!"
   sys.exit()

for i in range(1,len(sys.argv)):
   inputFilename = sys.argv[i]
   outputFilename = inputFilename + ".ilias.xml"

   print "... reading file " + inputFilename + " -> output to " + outputFilename
   inputFile = open(inputFilename)
   outputFile = open(outputFilename, "w")

   convertFile(inputFile, outputFile)
