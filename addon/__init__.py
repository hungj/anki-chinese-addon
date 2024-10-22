# import the main window object (mw) from aqt
from aqt import gui_hooks, mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo, qconnect
# import all of the Qt GUI library
from aqt.qt import *
from anki import notes

# We're going to add a menu item below. First we want to create a function to
# be called when the menu item is activated.

def testFunction(changed: bool, note: notes.Note, current_field_idx: int) -> bool:
    # get the number of cards in the current collection, which is stored in
    # the main window
    # cardCount = mw.col.cardCount()
    # show a message box
    print(f"changed: {changed}, current_field_idx: {current_field_idx}")
    #if changed and note.keys()[current_field_idx].lower() == 'hanzi':
    # changed is always False for some reason in anki
    if note.keys()[current_field_idx].lower() == 'hanzi':
        trad = note.values()[current_field_idx]
        simpl = "testing"
        print(f'note simplified: {note["Simplified"]}')
        if not note["Simplified"]:
            note["Simplified"] = simpl
        print(f"for note with hanzi {trad}, setting simplified field to {simpl}")
        # return true so the note can be reloaded
        return True
    return False

    # for key, value in note.items():
    #    print(f"for note {note.id}, got key {key} and value {value}")

gui_hooks.editor_did_unfocus_field.append(testFunction)

# create a new menu item, "test"
#action = QAction("test", mw)
# set it to call testFunction when it's clicked
#qconnect(action.triggered, testFunction)
# and add it to the tools menu
#mw.form.menuTools.addAction(action)