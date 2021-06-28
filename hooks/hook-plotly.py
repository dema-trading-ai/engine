from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules('plotly')
datas = collect_data_files("plotly")
