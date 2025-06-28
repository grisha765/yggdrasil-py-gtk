import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from yggui.core.window import MyApp

if __name__ == '__main__':
    app = MyApp(application_id="io.github.grisha765.yggdrasil-go-gtk")
    app.run(sys.argv)

