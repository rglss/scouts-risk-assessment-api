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

    raObj = {}

    if not body:
       return func.HttpResponse(json.dumps(raObj))

    if body:

        #Parse into BS object
        email = BeautifulSoup(body, 'html.parser')

        #Extract details

        #County
        raObj['county'] = email.find("td", string="County/Area/Region").next_sibling.next_sibling.string
        #District
        raObj['district'] = email.find("td", string="District").next_sibling.next_sibling.string
        #Group
        raObj['group'] = email.find("td", string="Group").next_sibling.next_sibling.string
        
        #Submitted By
        raObj['submittor'] = email.find("td", string="Submitter email").next_sibling.next_sibling.string
        #Approver
        raObj['approver'] = email.find("td", string="Approval email").next_sibling.next_sibling.string


        #Fetch Attachments
        raAttachURLs= []
        attachments = email.find_all("tr", class_="attachments_added")

        #Try with alt class when emails have been forwarded (email clients add the x_)
        if len(attachments) == 0:
            attachments = email.find_all("tr", class_="x_attachments_added")

        for row in attachments:

            anchor = row.find("a", attrs={"target": "_blank"})
            # Strip file size
            attachmentFilename = re.search("^(.*)\((.*)\)", anchor.string).group(1).strip()

            raAttachURLs.append({"filename":attachmentFilename, "url":anchor.get('href')})

        raObj['attachments'] = raAttachURLs

        #Return
        headers = {"Content-Type": "application/json"}

        return func.HttpResponse(json.dumps(raObj), headers=headers)
    
    else:
        return func.HttpResponse(
             "No Body Processed",
             status_code=500
        )
