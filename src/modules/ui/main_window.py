from pathlib import Path

from qfluentwidgets import FluentWindow, NavigationItemPosition, FluentIcon as FIF

from modules.app_state import AppState
from modules.data_store import DataStore
from modules.simulator import Simulator
from modules.ui.pages.overview_page import OverviewPage
from modules.ui.pages.history_page import HistoryPage
from modules.ui.pages.alarm_page import AlarmPage
from modules.ui.pages.operation_page import OperationPage
from modules.ui.pages.param_page import ParamPage
from modules.ui.pages.settings_page import SettingsPage


class MainWindow(FluentWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("装配工艺仿真与优化验证平台")
        self.resize(1200, 720)

        self.state = AppState()
        self.state.init_defaults()

        db_path = Path(__file__).resolve().parents[3] / "data" / "app.db"
        self.store = DataStore(db_path)
        self.store.connect()

        self.sim = Simulator(self.state, self.store)
        self.sim.start()

        self._init_navigation()

    def _init_navigation(self) -> None:
        self.overview = OverviewPage(self.state, self.sim, self.store)
        self.history = HistoryPage(self.state, self.store)
        self.alarm = AlarmPage(self.state, self.store, self.sim)
        self.operation = OperationPage(self.state, self.sim)
        self.param = ParamPage(self.state)
        self.settings = SettingsPage(self.state)

        self.addSubInterface(self.overview, FIF.HOME, "主界面")
        self.addSubInterface(self.history, FIF.HISTORY, "历史数据")
        self.addSubInterface(self.alarm, FIF.FLAG, "报警查看")
        self.addSubInterface(self.operation, FIF.TILES, "操作界面")
        self.addSubInterface(self.param, FIF.EDIT, "参数设定")
        self.addSubInterface(
            self.settings,
            FIF.SETTING,
            "系统设置",
            position=NavigationItemPosition.BOTTOM,
        )

        self.navigationInterface.setCurrentItem(self.overview.objectName())

    def closeEvent(self, event) -> None:  # type: ignore[override]
        self.sim.stop()
        self.store.close()
        event.accept()
