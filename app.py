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
    url    += f'&redirect_uri={REDIRECT_URI}' 
    url    += f'&state={state}'
    url    += f'&resource={GRA_Resource}'
    return url

def openToken(ctxt,code):
    ''' Crack an AAD token '''
    return  ctxt.acquire_token_with_authorization_code(
        code, 
        REDIRECT_URI, 
        GRA_Resource, 
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


@app.route("/login")
def login():
    auth_state                  = str(uuid.uuid4())
    flask.session['state']      = auth_state
    auth_url                    = buildAuthZ(auth_state)
    resp                        = flask.Response(status=307)
    resp.headers['location']    = auth_url
    return resp


@app.route("/landingPage")
def crackToken():
    code                        = flask.request.args['code']
    state                       = flask.request.args['state']
    if state != flask.session['state']:
        raise ValueError("State does not match")
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
    app.run(debug=True)
