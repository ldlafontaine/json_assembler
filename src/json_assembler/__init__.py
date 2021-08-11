from views.Assembler import Assembler

def run():
    try:
        dialog.close()
        dialog.deleteLater()
    except:
        pass

    dialog = Assembler()
    dialog.show()
