from steamroller.web import app

@app.route('/')
@app.route('/index')
def index():
    return "Hello world!asdf"

@app.route('/outdex')
def outdex():
    return 'asdf'