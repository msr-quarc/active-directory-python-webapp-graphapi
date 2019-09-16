import adal
import flask
import uuid
import requests
from config import *
from urllib.parse import urlencode
from flask_bootstrap import Bootstrap

app             = flask.Flask(__name__)
app.debug       = True
app.secret_key  = 'development'
bootstrap       = Bootstrap(app)

userName        = "None"

def buildAuthZ(state):
    ''' Get a token to accees resource '''
    url     = f'{AAD_URL}/oauth2/authorize'
    url    += '?response_type=code'
    url    += f'&client_id={AAD_ClientId}'
    url    += f'&redirect_uri={BASE_URL}/{AAD_Callback}' 
    url    += f'&state={state}'
    url    += f'&resource={FUL_Resource}'
    return url

def openToken(ctxt,code):
    ''' Crack an AAD token '''
    return  ctxt.acquire_token_with_authorization_code(
        code, 
        f'{BASE_URL}/{AAD_Callback}', 
        FUL_Resource, 
        AAD_ClientId, 
        AAD_ClientSecret)

@app.route("/logout")
def signout():
    logout_params               = urlencode({'post_logout_redirect_uri':f'{BASE_URL}/loggedout'})
    logout_url                  = f'{AAD_URL}/oauth2/logout?{logout_params}'
    resp                        = flask.Response(status=307)
    resp.headers['location']    = logout_url
    userName                    = "None"
    return resp

@app.route("/loggedout")
def logout():
    index_url                   = '{}/'.format(BASE_URL)
    resp                        = flask.Response(status=307)
    resp.headers['location']    = index_url
    userName                    = "None"
    return resp

@app.route("/")
def main():
    return flask.render_template('index.html', userName=userName)


@app.route("/landingpage")
def landingpage():
    flask.session['token']      = flask.request.args['token']
    auth_state                  = str(uuid.uuid4())
    flask.session['state']      = auth_state

    context                     = adal.AuthenticationContext(AAD_URL)
    code                        = context.acquire_token_with_client_credentials(
        FUL_Resource, FUL_ClientId, FUL_AppKey)
    flask.session['bearer']     = code['accessToken']

    url                         = f'{FUL_BaseURI}/subscriptions/resolve?api-version={FUL_ApiVersion}'
    requestId                   = str(uuid.uuid4())
    corrId                      = str(uuid.uuid4())
    headers                     = {
        'Content-type':             'application/json',
        'Authorization':            'Bearer ' + code['accessToken'],
        'x-ms-requestid':           requestId,
        'x-ms-correlationid':       corrId,
        'x-ms-marketplace-token':   flask.request.args['token']
        }
    rqst                        = requests.post(url,headers=headers)

    resp                        = flask.Response(status=307)
    resp.headers['location']    = auth_url
    return resp


@app.route("/signin-oidc")
def signin():
    bearer                      = flask.request.args['code']

    auth_context                = adal.AuthenticationContext(AAD_URL)

    # First we need a bearer token
    auth_state                  = str(uuid.uuid4())
    flask.session['state']      = auth_state
    auth_url                    = buildAuthZ(auth_state)
    resp                        = flask.Response(status=307)
    resp.headers['location']    = auth_url

    url                         = f'{AAD_Host}/{FUL_TenantId}/oauth2/token'
    headers                     = {'Content-type': 'application/json'}
    data                        = {
        'grant_type':       'client_credentials',
        'Client_id':        FUL_ClientId,
        'client_secret':    FUL_AppKey,
        'resource':         FUL_Resource
    }
    rqst                            = requests.post(url,headers=headers,json=data)


    auth_context                    = adal.AuthenticationContext(AAD_URL)
    token_response                  = openToken(auth_context,code)
    flask.session['access_token']   = token_response['accessToken']
    return flask.redirect('/graphcall')

@app.route('/graphcall')
def graphcall():
    if 'access_token' not in flask.session:
        userName    = "None"
        return flask.redirect(flask.url_for('login'))
    endpoint        = GRA_Resource + '/' + GRA_ApiVersion + '/me/'
    http_headers    = {'Authorization': 'Bearer ' + flask.session.get('access_token'),
                        'User-Agent': 'adal-python-sample',
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                        'client-request-id': str(uuid.uuid4())}
    graph_data      = requests.get(endpoint, headers=http_headers, stream=False).json()
    userName        = graph_data['userPrincipalName']
    return flask.render_template('display_graph_info.html', graph_data=graph_data, userName=userName)
    
if __name__ == "__main__":
    app.run(debug=True,ssl_context='adhoc')
