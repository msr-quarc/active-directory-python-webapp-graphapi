import os

# LOCAL or REMOTE:
BASE_URL        = 'http://localhost:5000'
#BASE_URL        = 'https://weckerPythonWebApp.azurewebsites.net'
REDIRECT_URI    = f'{BASE_URL}/landingPage'

# Azure Active Directory
AAD_Host            =  "https://login.microsoftonline.com" # Authority Host
AAD_Domain          = "microsoft.onmicrosoft.com" # Tenant
AAD_URL             = AAD_Host + '/' + AAD_Domain
AAD_TenantId        = "common"
AAD_ClientId        = "4bb3b469-4d58-4e5d-a33a-a94b6f14901f"  # AppId
AAD_Callback        = "/signin-oidc"
AAD_SignedOut       = "/signout-callback-oidc"
AAD_ClientSecret    = os.environ['PWA_AAD_ClientSecret']


# Fulfillment
FUL_ClientId        = AAD_ClientId
FUL_TenantId        = os.environ['PWA_FUL_TenantId']
FUL_AppKey          = AAD_ClientSecret
FUL_BaseURI         = "https://marketplaceapi.microsoft.com/api/saas"
FUL_ApiVersion      = "2018-09-15" # Mock APIs: "2018-09-15", Real APs: "2018-08-31"

# Azure Graph
GRA_Resource        = "https://graph.microsoft.com"  # Add the resource you want the access token for
GRA_ApiVersion      = 'v1.0'
