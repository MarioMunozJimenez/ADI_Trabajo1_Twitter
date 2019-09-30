#!/usr/bin/python
# -*- coding: utf-8; mode: python -*-

from flask import Flask, request, redirect, url_for, flash, render_template
from flask_oauthlib.client import OAuth

app = Flask(__name__)
app.config['DEBUG'] = True
oauth = OAuth()
mySession=None
currentUser=None

app.secret_key = 'development'



twitter = oauth.remote_app('twitter',
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    consumer_key='Yn8j64BqsI3VdWzyzLDFOfdoe',
    consumer_secret='GYyd6D0PwuBmIMhMi3ycUkHpTBVbdlO6j7MSeDir2NW3iRXUTh'
)


# Obtener token para esta sesion
@twitter.tokengetter
def get_twitter_token(token=None):
    global mySession
    
    if mySession is not None:
        return mySession['oauth_token'], mySession['oauth_token_secret']

    
# Limpiar sesion anterior e incluir la nueva sesion
@app.before_request
def before_request():
    global mySession
    global currentUser
    
    currentUser = None
    if mySession is not None:
        currentUser = mySession
        

# Pagina principal
@app.route('/')
def index():
    global currentUser
    
    tweets = None
    if currentUser is not None:
        resp = twitter.request('statuses/home_timeline.json')
        if resp.status == 200:
            tweets = resp.data
        else:
            flash('Imposible acceder a Twitter.')
    return render_template('index.html', user=currentUser, tweets=tweets)


# Get auth token (request)
@app.route('/login')
def login():
    callback_url=url_for('oauthorized', next=request.args.get('next'))
    return twitter.authorize(callback=callback_url or request.referrer or None)


# Eliminar sesion
@app.route('/logout')
def logout():
    global mySession
    
    mySession = None
    flash('Ya no estas logeado', 'message')
    return redirect(url_for('index'))


# Callback
@app.route('/oauthorized')
def oauthorized():
    global mySession
    
    resp = twitter.authorized_response()
    if resp is None:
        flash('You denied the request to sign in.', 'error')
    else:
        mySession = resp
        flash('Estas logeado', 'message')
    return redirect(url_for('index', next=request.args.get('next')))




# Operaciones
@app.route('/deleteTweet', methods=['POST'])
def deleteTweet():
    global currentUser

    if currentUser is None:
        return redirect(url_for('login'))

    deleteID = request.form['deleteID']

    resp = twitter.post('statuses/destroy.json', data={
        'id': deleteID
    })

    if resp.status is 200:
        flash('Has borrado el tweet!', 'message')
    return redirect(url_for('index'))



@app.route('/retweet', methods=['POST'])
def retweet():
    global currentUser

    if currentUser is None:
        return redirect(url_for('login'))

    retweetID = request.form['retweetID']
    resp = twitter.post('statuses/retweet.json', data={
        'id': retweetID
    })

    if resp.status == 200:
        flash('Se ha retuiteado el tuit!!', 'message')
    return redirect(url_for('index'))


@app.route('/follow', methods=['POST'])
def follow():
    global currentUser

    if currentUser is None:
        return redirect(url_for('login'))

    userID = request.form['userID']
    userName = request.form['userName']

    if userID is "" and userName is "":
        flash('Ambos estan vacios', 'error')
    elif userID is not "" and userName is "":
        respID = twitter.post('friendships/create.json', data={
            'user_id': userID
        })
        if respID.status is 200:
            flash('Acabas de seguir al ususario con id {}'.format(userID), 'message')
        elif respID.status is 404:
            flash('Error al seguir al usuario con ID {}'.format(userID), 'error')

    elif userID is "" and userName is not "":
        respName = twitter.post('friendships/create.json', data={
            'screen_name': userName
        })
        if respName.status is 200:
            flash('Acabas de seguir al ususario {}'.format(userName), 'message')
        elif respName.status is 404:
            flash('Error al seguir al usuario {}'.format(userName), 'error')

    else:
        respID = twitter.post('friendships/create.json', data={
            'user_id': userID
        })
        if respID.status is 200:
            flash('Acabas de seguir al ususario con id {}'.format(userID), 'message')
        elif respID.status is 404:
            flash('Error al seguir al usuario con ID {}'.format(userID), 'error')
            
    return redirect(url_for('index'))

    
@app.route('/tweet', methods=['POST'])
def tweet():
    global currentUser
    # Paso 1: Si no estoy logueado redirigir a pagina de /login
               # Usar currentUser y redirect
    if currentUser is None:
        return redirect(url_for('login'))

    # Paso 2: Obtener los datos a enviar
               # Usar request (form)
    status = request.form['tweetText']
    # Paso 3: Construir el request a enviar con los datos del paso 2
               # Utilizar alguno de los metodos de la instancia twitter (post, request, get, ...)
    resp = twitter.post('statuses/update.json', data={
        'status': status
    })
    # Paso 4: Comprobar que todo fue bien (no hubo errores) e informar al usuario
               # La anterior llamada devuelve el response, mirar el estado (status)
    if resp.status == 200:
        flash('Tweet enviado!', 'message')
    # Paso 5: Redirigir a pagina principal (hecho)
    return redirect(url_for('index'))





if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5005)
