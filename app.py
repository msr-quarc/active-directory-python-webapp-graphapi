import adal
import flask
import uuid
import requests
import config
from urllib.parse import urlencode
from flask_bootstrap import Bootstrap

app = flask.Flask(__name__)
app.debug = True
app.secret_key = 'development'
bootstrap = Bootstrap(app)
userName = "None"

########################################################### Local or remote...
# BASE_URL = 'http://localhost:5000'
BASE_URL = 'https://weckerPythonWebApp.azurewebsites.net'

AUTHORITY_URL = config.AUTHORITY_HOST_URL + '/' + config.TENANT
REDIRECT_URI = f'{BASE_URL}/landingPage'
TEMPLATE_AUTHZ_URL = (AUTHORITY_URL + '/oauth2/authorize?' +
                      'response_type=code&client_id={}&redirect_uri={}&' +
                      'state={}&resource={}')


@app.route("/signout")
def signout():
    logout_params = urlencode({'post_logout_redirect_uri':f'{BASE_URL}/logout'})
    logout_url = f'{AUTHORITY_URL}/oauth2/logout?{logout_params}'
    resp = flask.Response(status=307)
    resp.headers['location'] = logout_url
    userName = "None"
    return resp

@app.route("/logout")
def logout():
    index_url = '{}/'.format(BASE_URL)
    resp = flask.Response(status=307)
    resp.headers['location'] = index_url
    userName = "None"
    return resp

@app.route("/")
def main():
    return flask.render_template('index.html', userName=userName)


@app.route("/login")
def login():
    auth_state = str(uuid.uuid4())
    flask.session['state'] = auth_state
    authorization_url = TEMPLATE_AUTHZ_URL.format(
        config.CLIENT_ID,
        REDIRECT_URI,
        auth_state,
        config.RESOURCE)
    resp = flask.Response(status=307)
    resp.headers['location'] = authorization_url
    return resp


@app.route("/landingPage")
def crackToken():
    code = flask.request.args['code']
    state = flask.request.args['state']
    if state != flask.session['state']:
        raise ValueError("State does not match")
    auth_context = adal.AuthenticationContext(AUTHORITY_URL)
    token_response = auth_context.acquire_token_with_authorization_code(code, REDIRECT_URI, config.RESOURCE,
                                                                        config.CLIENT_ID, config.CLIENT_SECRET)
    # It is recommended to save this to a database when using a production app.
    flask.session['access_token'] = token_response['accessToken']

    return flask.redirect('/graphcall')


@app.route('/graphcall')
def graphcall():
    if 'access_token' not in flask.session:
        userName = "None"
        return flask.redirect(flask.url_for('login'))
    endpoint = config.RESOURCE + '/' + config.API_VERSION + '/me/'
    http_headers = {'Authorization': 'Bearer ' + flask.session.get('access_token'),
                    'User-Agent': 'adal-python-sample',
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'client-request-id': str(uuid.uuid4())}
    graph_data = requests.get(endpoint, headers=http_headers, stream=False).json()
    userName = graph_data['userPrincipalName']
    return flask.render_template('display_graph_info.html', graph_data=graph_data, userName=userName)
    
if __name__ == "__main__":
    app.run(debug=True)
