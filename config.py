import os
RESOURCE = "https://graph.microsoft.com"  # Add the resource you want the access token for
TENANT = "microsoft.onmicrosoft.com"  # Enter tenant name, e.g. contoso.onmicrosoft.com
AUTHORITY_HOST_URL = "https://login.microsoftonline.com"
CLIENT_ID = "4bb3b469-4d58-4e5d-a33a-a94b6f14901f"  # copy the Application ID of your app from your Azure portal
CLIENT_SECRET = os.environ['pythonWebApp']  # copy the value of key you generated when setting up the application

# These settings are for the Microsoft Graph API Call
API_VERSION = 'v1.0'
