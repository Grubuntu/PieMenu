"""Import and export of PieMenu settings (.FCParam files)."""

import datetime
import os
import shutil


def export_parameters():
    """Export the PieMenu parameters to a file."""
    import FreeCAD as App
    from PySide.QtWidgets import QFileDialog, QMessageBox

    translate = App.Qt.translate
    file, _ = QFileDialog.getSaveFileName(None, translate(
        "ExportSettingsWindow", "Export PieMenu settings to a file"), "", "XML (*.FCParam)")
    if file:
        try:
            if not file.endswith(".FCParam"):
                file += ".FCParam"
            item = App.ParamGet("User parameter:BaseApp/PieMenu")
            item.Export(file)

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText(translate("GlobalSettingsTab",
                        "PieMenu settings exported successfully."))
            msg.setWindowTitle(
                translate("GlobalSettingsTab", "Information"))
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()

        except Exception as e:
            log.log_error("exporting settings", e)


def import_parameters():
    """Import PieMenu parameters from a file."""
    import FreeCAD as App
    import FreeCADGui as Gui
    from PySide import QtCore, QtWidgets
    from PySide.QtWidgets import QFileDialog, QMessageBox

    translate = App.Qt.translate
    config_dir = App.getUserConfigDir()
    config_dir = config_dir.replace("\\", "/")
    user_config_file = os.path.join(config_dir, "user.cfg")

    backup_dir = os.path.join(config_dir, "user_config_backup")
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"user_backup_{timestamp}.cfg")

    msg = QMessageBox()
    msg.setIcon(QMessageBox.Question)
    msg.setText(translate("GlobalSettingsTab",
                "Before importing settings a backup of the current user configuration file (user.cfg) will be saved."))
    msg.setInformativeText(
        translate("GlobalSettingsTab", "Do you want to continue?"))
    msg.setWindowTitle(
        translate("GlobalSettingsTab", "Backup user settings"))
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg.setDefaultButton(QMessageBox.Yes)
    response = msg.exec()

    if response == QMessageBox.Yes:
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        try:
            shutil.copy(user_config_file, backup_file)
            log.log_warning("backup of configuration file created at %s" % backup_file)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText(
                translate(
                    "GlobalSettingsTab",
                    "Backup of the current user configuration file successfully saved in: {}",
                ).format(backup_file)
            )
            msg.setInformativeText(
                translate(
                    "GlobalSettingsTab",
                    "Click OK to select the file to import PieMenu settings.",
                )
            )
            msg.setWindowTitle(
                translate("GlobalSettingsTab", "Successful backup"))
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()

            file, _ = QFileDialog.getOpenFileName(None, translate(
                "ImportSettingsWindow", "Import PieMenu settings from a file"), "", "XML (*.FCParam)")

            if file:
                try:
                    item = App.ParamGet("User parameter:BaseApp/PieMenu")
                    item.Import(file)

                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Information)
                    msg.setText(translate("RestartFreeCADWindow",
                                "PieMenu settings imported successfully."))
                    msg.setInformativeText(translate(
                        "RestartFreeCADWindow", "Please restart FreeCAD for changes to take effect. \nRestart FreeCAD ?"))
                    msg.setWindowTitle(
                        translate("RestartFreeCADWindow", "Restart Required"))
                    msg.setStandardButtons(
                        QMessageBox.Yes | QMessageBox.No)

                    now_button = msg.button(QMessageBox.Yes)
                    now_button.setText(
                        translate("RestartFreeCADWindow", "Now"))
                    later_button = msg.button(QMessageBox.No)
                    later_button.setText(
                        translate("RestartFreeCADWindow", "Later"))
                    response = msg.exec()

                    if response == QMessageBox.Yes:
                        """Shuts down and restarts FreeCAD"""
                        args = QtWidgets.QApplication.arguments()[1:]
                        if Gui.getMainWindow().close():
                            QtCore.QProcess.startDetached(
                                QtWidgets.QApplication.applicationFilePath(), args
                            )

                except Exception as e:
                    log.log_error("importing parameters", e)
                return True

        except Exception as e:
            log.log_error("creating backup", e)
            return  # Exit the function if backup fails
    else:
        return False
