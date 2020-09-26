import logging
import json
import re

from bs4 import BeautifulSoup

import azure.functions as func


# Parse SmartSheet Email
# 
# Takes the content of an email notification from SmartSheet
# - Extracts Fields for TSA RTS Risk Assessment
# - Returns array of file attachments
def main(req: func.HttpRequest) -> func.HttpResponse:
    
    logging.info('Parsing SmartSheet email content')

    bodyObj = json.loads(req.get_body())
    body = bodyObj["emailBody"]

    objectArray = []

    if not body:
       return func.HttpResponse(
                            "Error processing body",
                            status_code=500
                        )

    if body:

        #Parse into BS object
        email = BeautifulSoup(body, 'html.parser')

        #Extract all the attachments info
        attachmentsDict={}
        attachments = email.find_all("tr", class_="attachments_added")

        #Try with alt class when emails have been forwarded (email clients add the x_)
        if len(attachments) == 0:
            attachments = email.find_all("tr", class_="x_attachments_added")

        for row in attachments:

            anchor = row.find("a", attrs={"target": "_blank"})

            # Strip file size
            attachmentFilename = re.search("^(.*)\((.*)\)", anchor.string).group(1).strip()

            # Fetch the matching row number
            rowNumber = re.search("on Row ([0-9,]*)", anchor.parent.getText()).group(1).replace(',','')

            if rowNumber in attachmentsDict:
                attachmentsDict[rowNumber].append({"filename":attachmentFilename, "url":anchor.get('href')})
            else:
                attachmentsDict[rowNumber] = [{"filename":attachmentFilename, "url":anchor.get('href')}]


        #Check for the presence of multiple rows
        rowChangeText = email.find("table", class_="grid_summary").get_text()
        rowChangeCount = int(re.search("([0-9]*) row", rowChangeText).group(1))

        logging.info(f'Rows Changed: {rowChangeCount}')

        #Extraction for single row
        if rowChangeCount == 1:

            recordObj = {}
            #County
            recordObj['county'] = email.find("td", string="County/Area/Region").next_sibling.next_sibling.string
            #District
            recordObj['district'] = email.find("td", string="District").next_sibling.next_sibling.string
            #Group
            recordObj['group'] = email.find("td", string="Group").next_sibling.next_sibling.string
            #Submitted By
            recordObj['submittor'] = email.find("td", string="Submitter email").next_sibling.next_sibling.string
            #Approver
            recordObj['approver'] = email.find("td", string="Approval email").next_sibling.next_sibling.string

            # We've only got one row, so all all attachments here
            allAttachments = []
            for a in attachmentsDict:
                allAttachments = allAttachments + attachmentsDict[a]

            recordObj['attachments'] = allAttachments

            objectArray.append(recordObj)

        elif rowChangeCount > 1:
            
            table = email.find("div", class_="grid").find("tbody").find_all("tr")

            for record in table:
                
                if record.get_text() != "":

                    cells = record.find_all("td")

                    # Validate length of cells
                    if len(cells) != 7:
                        return func.HttpResponse(
                            "Error processing body",
                            status_code=500
                        )

                    recordObj = {}
                    rowNum = cells[0].get_text()
                    recordObj['county'] = cells[2].get_text()
                    recordObj['district'] = cells[3].get_text()
                    recordObj['group'] = cells[4].get_text()
                    recordObj['submittor'] = cells[5].get_text()
                    recordObj['approver'] = cells[6].get_text()

                    #Append any attachments
                    recordObj['attachments'] = attachmentsDict[rowNum]

                    objectArray.append(recordObj)
        

        #Return
        headers = {"Content-Type": "application/json"}

        return func.HttpResponse(json.dumps(objectArray), headers=headers)
    
    else:
        return func.HttpResponse(
             "No Body Processed",
             status_code=500
        )
