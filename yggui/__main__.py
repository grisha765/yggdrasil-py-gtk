import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from yggui.core.common import Binary

if Binary.ygg_path is None:
    raise FileNotFoundError(
        "The 'yggdrasil' executable was not found in your PATH. "
        "Please install Yggdrasil or adjust your PATH environment "
        "variable accordingly."
    )

if Binary.yggctl_path is None:
    raise FileNotFoundError(
        "The 'yggdrasilctl' executable was not found in your PATH. "
        "Please install Yggdrasil or adjust your PATH environment "
        "variable accordingly."
    )

from yggui.core.window import MyApp

if __name__ == '__main__':
    app = MyApp(
        application_id="io.github.grisha765.yggdrasil-go-gtk"
    )
    app.run(sys.argv)

