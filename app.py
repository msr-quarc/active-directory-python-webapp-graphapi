import adal
import flask
import uuid
import requests
import json
from config import *
from urllib.parse import urlencode
from flask_bootstrap import Bootstrap

app             = flask.Flask(__name__)
app.debug       = True
app.secret_key  = 'development'
bootstrap       = Bootstrap(app)

@app.route("/logout")
def signout():
    logout_params               = urlencode({'post_logout_redirect_uri':f'{BASE_URL}/loggedout'})
    logout_url                  = f'{AAD_URL}/oauth2/logout?{logout_params}'
    resp                        = flask.Response(status=307)
    resp.headers['location']    = logout_url
    return resp

@app.route("/loggedout")
def logout():
    resp                        = flask.Response(status=307)
    resp.headers['location']    = BASE_URL + '/'
    return resp

@app.route("/")
def main():
    return flask.render_template('index.html')


@app.route("/landingpage")
def landingpage():
    if 'token' not in flask.request.args:
        resp                        = flask.Response(status=307)
        resp.headers['location']    = BASE_URL + '/'
        return resp

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
    rqst                            = requests.post(url,headers=headers)
    if rqst.status_code != 200:
        flask.flash('Token NOT decoded!')
        resp                        = flask.Response(status=307)
        resp.headers['location']    = BASE_URL + '/'
        return resp

    info = json.loads(rqst.content)  

    # Here is where we activate (since the token cracked Ok, we know we are good to go)
    subId                       = info['id']
    url2                        = f'{FUL_BaseURI}/subscriptions/{subId}/activate?api-version={FUL_ApiVersion}'
    headers2                    = {
        'Content-type':             'application/json',
        'Authorization':            'Bearer ' + code['accessToken'],
        'x-ms-requestid':           requestId,
        'x-ms-correlationid':       corrId,
        }
    json2                       = {
        "planId":       planId,
        "quantity":     ""
    }
    rqst2                       = requests.post(url2,headers=headers2,json=json2)
    if rqst2.status_code != 200:
        flask.flash('Activation not successful!')
    
    return flask.render_template('subscribe.html', info=info)
    
if __name__ == "__main__":
    app.run(debug=True,ssl_context='adhoc')
