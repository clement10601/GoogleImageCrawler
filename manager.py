# -*- coding: utf-8 -*-
from flask_script import Server, Manager
from webui.app import app


manager = Manager(app)
manager.add_command('run', Server(
    host='127.0.0.1', port=7000, threaded=True, 
    use_reloader=True, use_debugger=True))

if __name__ == "__main__":
    manager.run()
