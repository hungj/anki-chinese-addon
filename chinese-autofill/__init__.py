from aqt import gui_hooks
from aqt import mw
from aqt.qt import *
from aqt.utils import qconnect
from .autofill import autofill
from .backfill import add_frequency_info


gui_hooks.editor_did_unfocus_field.append(autofill)

action = QAction("fill in card info", mw)
qconnect(action.triggered, add_frequency_info)
mw.form.menuTools.addAction(action)