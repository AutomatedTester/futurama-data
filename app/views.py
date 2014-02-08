from app import app

@app.route('/')
@app.route('/index')
def index():
    return "Welcome To Futurama-Data because well its cool!!"