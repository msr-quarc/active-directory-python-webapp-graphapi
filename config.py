import os

# LOCAL or REMOTE:
BASE_URL        = 'https://localhost:44377'
#BASE_URL        = 'https://weckerContoso.azurewebsites.net'

# Azure Active Directory
AAD_Host            =  "https://login.microsoftonline.com" # Authority Host
AAD_Domain          = "microsoft.onmicrosoft.com" # Tenant
AAD_URL             = AAD_Host + '/' + AAD_Domain
AAD_TenantId        = "common"
AAD_ClientId        = "260eae2a-e644-4985-bf6a-c7af0ea1cd98"  # AppId
AAD_Callback        = "/signin-oidc"
AAD_SignedOut       = "/signout-callback-oidc"
AAD_ClientSecret    = os.environ['PWA_AAD_ClientSecret']


# Fulfillment
FUL_Resource        = "62d94f6c-d599-489b-a797-3e10e42fbe22"
FUL_ClientId        = AAD_ClientId
FUL_TenantId        = os.environ['PWA_FUL_TenantId']
FUL_AppKey          = AAD_ClientSecret
FUL_BaseURI         = "https://marketplaceapi.microsoft.com/api/saas"
FUL_ApiVersion      = "2018-08-31" # Mock APIs: "2018-09-15", Real APs: "2018-08-31"
