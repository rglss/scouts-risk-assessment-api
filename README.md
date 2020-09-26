# RTS Risk Assessment Processing

Excuse the catchy title. Azure Functions library (in Python) that provides a couple of endpoints allowing for the processing of RTS RAs with O365 Power Automate.

## Requirements

- Azure Account to deploy to
  - Functions is the MS version of AWS Lamda, if deployed correctly this will cost nothing.
  - Pricing: https://azure.microsoft.com/en-gb/services/functions/#security
- O365 for Power Automate

## Installation on Azure

1. Create your Azure Function
   - MS Guide: https://docs.microsoft.com/en-us/azure/azure-functions/functions-create-first-azure-function
   - Stop when you get to 'Create an HTTP trigger function'
  2. Clone this repo to your local machine
  3. Upload to your new Azure Function
     - MS Guide: https://docs.microsoft.com/en-us/azure/azure-functions/functions-create-first-function-vs-code?pivots=programming-language-python
     - Skip creating a local project, just open this one!

## Setup of Power Automate

Once your API is setup, you need to add the custom connector in O365 in order to access it.

  1. Generate an API key for your Azure Function. This needs to be a 'host' API key in order to use both the methods, unless you want a key for each.
     - Docs: https://docs.microsoft.com/en-us/azure/azure-functions/functions-bindings-http-webhook-trigger?tabs=csharp#obtaining-keys 
  
  2. Create the Connector in Power Automate:
     - MS Guide: https://docs.microsoft.com/en-us/connectors/custom-connectors/define-openapi-definition#import-the-openapi-definition-for-power-automate-and-power-apps
     - Use the OpenAPI-Def.yaml file in this repository to create the connector.
     - Set the API key when prompted you generated above.
  
  3. Profit! You can now use this connector in your flows!

Please see example-flow.png for a example flow usage.

## Known Issues

This has not been extensively tested, but appears to be working ok in production currently. Please raise any issues via GitHub.

- ~~Currently SmartSheet emails which notify multiple rows have been changed are unsupported.~~ Fixed in v0.2. Note objects now returned in an array.

## License

GNU General Public License v3.0 - see License.txt

## API Reference

### ParseSmartSheetEmail

#### Request

```http
POST /api/ParseSmartSheetEmail HTTP/1.1
Content-Type: application/json

{
    "emailBody": "<html>[ Email Body ]</html>"
}

```

#### Response

```json
[
    {
        "county": "My County",
        "district": "My Distruct",
        "group": "1st Scout Group",
        "submittor": "gsl@1stscoutgroup.org.uk",
        "approver": "dc@myscoutdistrict.org.uk",
        "attachments": [
            {
                "filename": "COVID19 - Restart Risk Assessment- 1st Scout Group.docx",
                "url": "https://app.smartsheet.com/b/download/att/1/"
            },
            {
                "filename": "Additional Attachment.xlsx",
                "url": "https://app.smartsheet.com/b/download/att/2/"
            }
        ]
    }
    { // Further objects //  }
]
```

### ParseAttachment

#### Request

```http
POST /api/ParseAttachment HTTP/1.1
Content-Type: application/json

{
    "fileContents": "[Base64 Encoded File]"
}

```

#### Response

If processed successfully (i.e. a risk assessment):
```json
{
    "section": "1st Scout Group",
    "date": "08/09/2020",
    "author": "A.n. Leader",
    "level": "Amber",
    "status": "ok",
    "risk-assessment": true
}
```

If not, but not failed:
```json
{
    "status": "ok",
    "risk-assessment": false
}
```

If error:
```json
{
    "status": "error",
    "risk-assessment": false,
    "error": "A semi-helpful error message?"
}
```