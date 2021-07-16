import views.MainDialog

try:
    dialog.close()
    dialog.deleteLater()
except:
    pass

dialog = views.MainDialog.MainDialog()
dialog.show()
