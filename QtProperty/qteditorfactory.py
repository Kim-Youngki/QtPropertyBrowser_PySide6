#############################################################################
##
## Copyright (C) 2013 Digia Plc and/or its subsidiary(-ies).
## Contact: http:##www.qt-project.org/legal
##
## This file is part of the Qt Solutions component.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Digia Plc and its Subsidiary(-ies) nor the names
##     of its contributors may be used to endorse or promote products derived
##     from this software without specific prior written permission.
##
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
## $QT_END_LICENSE$
##
#############################################################################
#
# Modified by Youngki Kim in 2021/11/17 for PySide6 support
#
############################################################################


from PySide6.QtCore import Qt, Slot, Signal, QEvent
from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox, QHBoxLayout, QStyleOption, QStyle,
    QLabel, QToolButton, QSpacerItem, QSizePolicy, QColorDialog,
    QComboBox,
    QSlider,
    QScrollBar,
    QDateEdit,
    QTimeEdit,
    QDateTimeEdit,
    QFontDialog
)
from PySide6.QtGui import QKeySequence, QPainter, QColor, QBrush, QFont, QAction
from QtProperty.qtpropertymanager import QtEnumPropertyManager, cursorDatabase
from libqt5.pyqtcore import QMap, QList, QMapList
from QtProperty.qtproperty import QtProperty
from QtProperty.qtabstracteditorfactory import QtAbstractEditorFactory
from QtProperty.qtpropertyutils import *


# Set a hard coded left margin to account for the indentation
# of the tree view icon when switching to an editor
def setupTreeViewEditorMargin(lt):
    DecorationMargin = 4
    if QApplication.layoutDirection() == Qt.LeftToRight:
        lt.setContentsMargins(DecorationMargin, 0, 0, 0)
    else:
        lt.setContentsMargins(0, 0, DecorationMargin, 0)


g_editorFactoryWidget = QMap()


def registerEditorFactory(classType, widgetType):
    global g_editorFactoryWidget
    if not g_editorFactoryWidget:
        g_editorFactoryWidget = QMap()
    g_editorFactoryWidget[classType] = widgetType


#####################################################################################
#
#   class   QtBoolEdit
#
#   brief   The helper class for QtCheckBoxFactory
#
#####################################################################################
class QtBoolEdit(QWidget):
    toggledSignal = Signal(bool)

    def __init__(self, parent=None):
        super(QtBoolEdit, self).__init__(parent)
        self.m_check_box = QCheckBox(self)
        self.m_text_visible = True

        lt = QHBoxLayout()

        if QApplication.layoutDirection() == Qt.LeftToRight:
            lt.setContentsMargins(4, 0, 0, 0)
        else:
            lt.setContentsMargins(0, 0, 4, 0)

        lt.addWidget(self.m_check_box)

        self.setLayout(lt)
        self.m_check_box.toggled.connect(self.toggledSignal)
        self.setFocusProxy(self.m_check_box)
        self.m_check_box.setText("True")

    def textVisible(self):
        return self.m_text_visible

    def setTextVisible(self, visible):
        if self.m_text_visible == visible:
            return

        self.m_text_visible = visible
        if self.m_text_visible:
            if self.isChecked():
                self.m_check_box.setText("True")
            else:
                self.m_check_box.setText("False")
        else:
            self.m_check_box.setText("")

    def checkState(self):
        return self.m_check_box.checkState()

    def setCheckState(self, state):
        return self.m_check_box.setCheckState(state)

    def isChecked(self):
        return self.m_check_box.isChecked()

    def setChecked(self, check):
        self.m_check_box.setChecked(check)

        if not self.m_text_visible:
            return

        if self.isChecked():
            self.m_check_box.setText("True")
        else:
            self.m_check_box.setText("False")

    def blockCheckBoxSignals(self, block):
        return self.m_check_box.blockSignals(block)

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.m_check_box.click()
            event.accept()
        else:
            super(QtBoolEdit, self).mousePressEvent(event)

    def paintEvent(self, event) -> None:
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)


#####################################################################################
#
#   class   QtColorEditWidget
#
#   brief   The helper class for QtColorEditorFactory
#
#####################################################################################
class QtColorEditWidget(QWidget):
    valueChangedSignal = Signal(QColor)

    def __init__(self, parent=None):
        super(QtColorEditWidget, self).__init__(parent)

        self.m_color = QColor()
        self.m_pixmap_label = QLabel()
        self.m_label = QLabel()

        self._layout = QHBoxLayout(self)
        setupTreeViewEditorMargin(self._layout)
        self._layout.setSpacing(0)
        self._layout.addWidget(self.m_pixmap_label)
        self._layout.addWidget(self.m_label)
        self._layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Ignored))

        self.m_button = QToolButton()
        self.m_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Ignored)
        self.m_button.setFixedWidth(20)

        self.setFocusProxy(self.m_button)
        self.setFocusPolicy(self.m_button.focusPolicy())
        self.m_button.setText("...")
        self.m_button.installEventFilter(self)
        self.m_button.clicked.connect(self.buttonClicked)

        self._layout.addWidget(self.m_button)

        self.m_pixmap_label.setPixmap(brushValuePixmap(QBrush(self.m_color)))
        self.m_label.setText(colorValueText(self.m_color))

    def setValue(self, color):
        if self.m_color != color:
            self.m_color = color
            self.m_pixmap_label.setPixmap(brushValuePixmap(QBrush(color)))
            self.m_label.setText(colorValueText(color))

    def buttonClicked(self):
        ok = ""
        old_rgba = self.m_color
        new_rgba = QColorDialog.getColor(old_rgba, self, ok, QColorDialog.ShowAlphaChannel)
        if new_rgba != old_rgba:
            self.setValue(new_rgba)
            self.valueChangedSignal.emit(self.m_color)

    def eventFilter(self, watched, event) -> bool:
        if watched == self.m_button:
            k = event.type()

            # Prevent the QToolButton from handling Enter/Escape meant control the delegate
            if k in [QEvent.KeyPress, QEvent.KeyRelease]:
                x = event.key()
                if x in [Qt.Key_Escape, Qt.Key_Enter, Qt.Key_Return]:
                    event.ignore()
                    return True
        
        return super(QtColorEditWidget, self).eventFilter(watched, event)

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)


#####################################################################################
#
#   class   QtColorEditWidget
#
#   brief   The helper class for QtFontEditorFactory
#
#####################################################################################
class QtFontEditWidget(QWidget):
    # Defines custom widget
    valueChanged = Signal(QFont)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        
        self._font = QFont()
        self.pixmap_label = QLabel()
        self.label = QLabel()
        
        self._layout = QHBoxLayout(self)
        setupTreeViewEditorMargin(self._layout)
        self._layout.setSpacing(0)
        self._layout.addWidget(self.pixmap_label)
        self._layout.addWidget(self.label)
        self._layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Ignored))

        self.button = QToolButton()
        self.button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Ignored)
        self.button.setFixedWidth(20)

        self.setFocusProxy(self.button)
        self.setFocusPolicy(self.button.focusPolicy())
        self.button.setText("...")
        self.button.installEventFilter(self)
        self.button.clicked.connect(self.buttonClicked)
        
        self._layout.addWidget(self.button)
        
        self.pixmap_label.setPixmap(fontValuePixmap(self._font))
        self.label.setText(fontValueText(self._font))

    def setValue(self, font):
        if self._font != font:
            self._font = font
            self.pixmap_label.setPixmap(fontValuePixmap(font))
            self.label.setText(fontValueText(font))
    
    def buttonClicked(self):
        ok = False
        new_font, ok = QFontDialog.getFont(self._font, self, "Select font")
        if ok and new_font != self._font:
            font = QFont(self._font)
            # prevent mask for unchanged attributes, don't change other attributes (like kerning, etc...)

            if self._font.family() != new_font.family():
                font.setFamily(new_font.family())

            if self._font.pointSize() != new_font.pointSize():
                font.setPointSize(new_font.pointSize())

            if self._font.bold() != new_font.bold():
                font.setBold(new_font.bold())

            if self._font.italic() != new_font.italic():
                font.setItalic(new_font.italic())

            if self._font.underline() != new_font.underline():
                font.setUnderline(new_font.underline())

            if self._font.strikeOut() != new_font.strikeOut():
                font.setStrikeOut(new_font.strikeOut())
            
            self.setValue(font)
            self.valueChanged.emit(self._font)

    def eventFilter(self, watched, event) -> bool:
        if watched == self.button:
            t = event.type()
            if t in [QEvent.KeyPress, QEvent.KeyRelease]:
                x = event.key()

                if x in [Qt.Key_Escape, Qt.Key_Enter, Qt.Key_Return]:
                    event.ignore()
                    
                    return True

        return super(QtFontEditWidget, self).eventFilter(watched, event)

    def paintEvent(self, event) -> None:
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)


#####################################################################################
#
#   class   QtColorEditWidget
#
#   brief   The helper class for QtKeySequenceEditorFactory
#
#####################################################################################
class QtKeySequenceEdit(QWidget):
    # Defines custom signal
    keySequenceChangedSignal = Signal(QKeySequence)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.key_sequence = QKeySequence()
        self.num = 0
        self.line_edit = QLineEdit(self)

        layout = QHBoxLayout(self)
        layout.addWidget(self.line_edit)
        layout.setContentsMargins(0, 0, 0, 0)

        self.line_edit.installEventFilter(self)
        self.line_edit.setReadOnly(True)
        self.line_edit.setFocusProxy(self)

        self.setFocusPolicy(self.line_edit.focusPolicy())
        self.setAttribute(Qt.WA_InputMethodEnabled)

    def eventFilter(self, watched, e) -> bool:
        if watched == self.line_edit and e.type() == QEvent.ContextMenu:
            c = e
            menu = self.line_edit.createStandardContextMenu()
            actions = menu.actions()
            for action in actions:
                action.setShortcut(QKeySequence())
                action_string = action.text()
                pos = action_string.rfind("\t")
                if pos > 0:
                    action_string = action_string[:pos]
                
                action.setText(action_string)

            action_before = None
            if len(actions) > 0:
                action_before = action[0]
            
            clear_action = QAction("Clear Shortcut", menu)
            menu.insertAction(action_before, clear_action)
            menu.insertSeparator(action_before)

            clear_action.setEnabled(not self.key_sequence.count() <= 0)
            clear_action.triggered.connect(self.slotClearShortcut)

            menu.exec(c.globalPos())
            e.accept()
            return True

        return super().eventFilter(watched, e)

    def slotClearshortcut(self):
        if self.key_sequence.count() <= 0:
            return
        
        self.setKeySequence(QKeySequence())
        self.keySequenceChangedSignal.emit(self.key_sequence)

    def handleKeyEvent(self, e):
        next_key = e.key()
        if (next_key == Qt.Key_Control or next_key == Qt.Key_Shift or
                next_key == Qt.Key_Meta or next_key == Qt.Key_Alt or
                next_key == Qt.Key_Super_L or next_key == Qt.Key_AltGr):
            return

        next_key |= self.translateModifiers(e.modifiers(), e.text())
        k0 = 0
        k1 = 0
        k2 = 0
        k3 = 0
        # l = self.key_sequence.count()
        l = self.key_sequence.count()
        if l == 1:
            k0 = self.key_sequence[0]
        elif l == 2:
            k0 = self.key_sequence[0]
            k1 = self.key_sequence[1]
        elif l == 3:
            k0 = self.key_sequence[0]
            k1 = self.key_sequence[1]
            k2 = self.key_sequence[2]
        elif l == 4:
            k0 = self.key_sequence[0]
            k1 = self.key_sequence[1]
            k2 = self.key_sequence[2]
            k3 = self.key_sequence[3]
        if self.num == 0:
            k0 = next_key
            k1 = 0
            k2 = 0
            k3 = 0
        elif self.num == 1:
            k1 = next_key
            k2 = 0
            k3 = 0
        elif self.num == 2:
            k2 = next_key
            k3 = 0
        elif self.num == 3:
            k3 = next_key
        else:
            pass

        self.num += 1
        if self.num > 3:
            self.num = 0

        self.key_sequence = QKeySequence(k0, k1, k2, k3)
        self.line_edit.setText(self.key_sequence.toString(QKeySequence.NativeText))
        e.accept()
        self.keySequenceChangedSignal.emit(self.key_sequence)

    def setKeySequence(self, sequence):
        if sequence == self.key_sequence:
            return

        self.num = 0
        self.key_sequence = sequence
        self.line_edit.setText(self.key_sequence.toString(QKeySequence.NativeText))

    def keySequence(self):
        return self.key_sequence

    def translateModifiers(self, state, text):
        result = 0

        if (state & Qt.ShiftModifier) and (len(text) == 0 or not text[0].isprintable() or text[0].isalpha() or text[0].isspace()):
            result |= Qt.SHIFT

        if state & Qt.ControlModifier:
            result |= Qt.CTRL

        if state & Qt.MetaModifier:
            result |= Qt.META

        if state & Qt.AltModifier:
            result |= Qt.ALT

        return result

    def focusInEvent(self, e):
        self.line_edit.event(e)
        self.line_edit.selectAll()
        super(QtKeySequenceEdit, self).focusInEvent(e)

    def focusOutEvent(self, e):
        self.num = 0
        self.line_edit.event(e)
        super(QtKeySequenceEdit, self).focusOutEvent(e)

    def keyPressEvent(self, e):
        self.handleKeyEvent(e)
        e.accept()

    def keyReleaseEvent(self, e):
        self.line_edit.event(e)

    def paintEvent(self, ptQPaintEvent):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)

    def event(self,e):
        if (e.type() == QEvent.Shortcut or
                e.type() == QEvent.ShortcutOverride  or
                e.type() == QEvent.KeyRelease):
            e.accept()

            return True

        return super(QtKeySequenceEdit, self).event(e)


#####################################################################################
#
#   class   QtCharEdit
#
#   brief   The helper class for QtCharEditorFactory
#
#####################################################################################
class QtCharEdit(QWidget):
    valueChangedSignal = Signal(str)
    def __init__(self, parent=None):
        super(QtCharEdit, self).__init__(parent)

        self.line_edit = QLineEdit(self)
        self.layout = QHBoxLayout(self)
        self.layout.addWidget(self.line_edit)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.line_edit.installEventFilter(self)
        self.line_edit.setReadOnly(True)
        self.line_edit.setFocusProxy(self)
        self.setFocusPolicy(self.line_edit.focusPolicy())
        self.setAttribute(Qt.WA_InputMethodEnabled)
        self.value = ''

    def eventFilter(self, o, e):
        if o == self.line_edit and e.type() == QEvent.ContextMenu:
            c = e
            menu = self.line_edit.createStandardContextMenu()
            actions = menu.actions()
            for action in actions:
                action.setShortcut(QKeySequence())
                actionString = action.text()
                pos = actionString.lastIndexOf('\t')
                if pos > 0:
                    actionString = actionString.remove(pos, actionString.length() - pos)

                action.setText(actionString)

            actionBefore = 0
            if len(actions) > 0:
                actionBefore = actions[0]
            clearAction = QAction(self.tr("Clear Char"), menu)
            menu.insertAction(actionBefore, clearAction)
            menu.insertSeparator(actionBefore)
            clearAction.setEnabled(not self.value=='')
            clearAction.triggeredSignal.connect(self.d_ptr.slotClearChar)
            menu.exec(c.globalPos())
            del menu
            e.accept()
            return True

        return super(QtCharEdit, self).eventFilter(o, e)

    def slotClearChar(self):
        if self.value == '':
            return
        self.setValue('')
        self.valueChangedSignal.emit(self.value)

    def handleKeyEvent(self, e):
        key = e.key()
        if key in [Qt.Key_Control, Qt.Key_Shift, Qt.Key_Meta, Qt.Key_Alt, Qt.Key_Super_L, Qt.Key_Return]:
            return

        text = e.text()
        if len(text) != 1:
            return

        c = text[0]
        if not c.isprintable():
            return

        if self.value == c:
            return

        self.value = c
        if self.value=='':
            s = ''
        else:
            s = str(self.value)
        self.line_edit.setText(s)
        e.accept()
        self.valueChangedSignal.emit(self.value)

    def setValue(self, value):
        if value == self.value:
            return

        self.value = value
        if value == '':
            s = ''
        else:
            s = str(value)

        self.line_edit.setText(s)

    def value(self):
        return  self.value

    def focusInEvent(self, e):
        self.line_edit.event(e)
        self.line_edit.selectAll()
        super(QtCharEdit, self).focusInEvent(e)

    def focusOutEvent(self, e):
        self.line_edit.event(e)
        super(QtCharEdit, self).focusOutEvent(e)

    def keyPressEvent(self, e):
        self.handleKeyEvent(e)
        e.accept()

    def keyReleaseEvent(self, e):
        self.line_edit.event(e)

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)

    def event(self, e):
        x = e.type()
        if x in [QEvent.Shortcut, QEvent.ShortcutOverride, QEvent.KeyRelease]:
            e.accept()
            return True

        return super(QtCharEdit, self).event(e)


#####################################################################################
#
#   class EditorFactoryPrivate
#
#   brief Base class for editor factories.
#   Manages mapping of properties to editors and vice versa.
#
#####################################################################################
class EditorFactoryPrivate:
    m_createdEditors = QMap()
    m_editorToProperty = QMap()

    def __init__(self):
        self.q_ptr = None

    def createEditor(self, prop, parent):
        editorClass = g_editorFactoryWidget.get(type(self))
        editor = None
        if editorClass:
            editor = editorClass(parent)

        self.initializeEditor(prop, editor)
        # self.lastEditor = editor
        return editor

    def initializeEditor(self, prop, editor):
        if not self.m_createdEditors.get(prop):
            self.m_createdEditors[prop] = QList()

        self.m_createdEditors[prop].append(editor)
        self.m_editorToProperty[editor] = prop

    def slotEditorDestroyed(self, obj):
        if obj in self.m_editorToProperty.keys():
            prop = self.m_editorToProperty[obj]
            pit = self.m_createdEditors.get(prop)
            if pit:
                pit.removeAll(obj)

                if len(pit) == 0:
                    self.m_createdEditors.erase(prop)

            self.m_editorToProperty.erase(obj)
            return


#####################################################################################
#
#   class QtLineEditFactory
#
#   brief The QtLineEidtFactory class provides QLineEdit widgets for properties
#         created by QtStringPropertyManager objects.
#
#####################################################################################
class QtLineEditFactoryPrivate(EditorFactoryPrivate):
    def __init__(self):
        super(QtLineEditFactoryPrivate, self).__init__()
        self.q_ptr = None


registerEditorFactory(QtLineEditFactoryPrivate, QLineEdit)


class QtLineEditFactory(QtAbstractEditorFactory):
    def __init__(self, parent=None):
        """
        Creates a factory with the given parent.
        """
        super(QtLineEditFactory, self).__init__(parent)

        self.d_ptr = QtLineEditFactoryPrivate()
        self.d_ptr.q_ptr = self
        self.editor = None

    def __del__(self):
        """
        Destroys this factory, and all the widgets it has created.
        """
        self.d_ptr.m_editorToProperty.clear()
        del self.d_ptr

    def createEditor(self, manager, prop, parent):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        editor = self.d_ptr.createEditor(prop, parent)
        editor.setEchoMode(manager.echoMode(prop))
        editor.setReadOnly(manager.isReadOnly(prop))
        # regExp = manager.regExp(property)
        # if (regExp.isValid()):
        #     validator = QRegularExpressionValidator(regExp, editor)
        #     editor.setValidator(validator)

        editor.setText(manager.value(prop))

        editor.textChanged.connect(self.slotSetValue)
        editor.destroyed.connect(self.d_ptr.slotEditorDestroyed)

        self.editor = editor

        return editor

    def connectPropertyManager(self, manager):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        manager.valueChangedSignal.connect(self.slotValueChanged)
        manager.echoModeChangedSignal.connect(self.slotEchoModeChanged)
        manager.readOnlyChangedSignal.connect(self.slotReadOnlyChanged)
        # manager.regExpChangedSignal.connect(self.d_ptr.slotRegExpChanged)

    def disconnectPropertyManager(self, manager):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        manager.valueChangedSignal.disconnect(self.slotValueChanged)
        manager.echoModeChangedSignal.disconnect(self.slotEchoModeChanged)
        manager.readOnlyChangedSignal.disconnect(self.slotReadOnlyChanged)
        # manager.regExpChangedSignal.disconnect(self.d_ptr.slotRegExpChanged)

    @Slot(QtProperty, str)
    def slotValueChanged(self, prop, value):
        editors = self.d_ptr.m_createdEditors.get(prop)
        if not editors:
            return

        for editor in editors:
            if editor.text() != value:
                editor.blockSignals(True)
                editor.setText(value)
                editor.blockSignals(False)

    @Slot(QtProperty, int)
    def slotEchoModeChanged(self, prop, echo_mode):
        editors = self.d_ptr.m_createdEditors.get(prop)
        if not editors:
            return

        manager = self.propertyManager(prop)
        if not manager:
            return

        for editor in editors:
            editor.blockSignals(True)
            editor.setEchoMode(echo_mode)
            editor.blockSignals(False)

    @Slot(QtProperty, bool)
    def slotReadOnlyChanged(self,  prop, read_only):
        editors = self.d_ptr.m_createdEditors.get(prop)
        if not editors:
            return

        manager = self.propertyManager(prop)
        if not manager:
            return

        for editor in editors:
            editor.blockSignals(True)
            editor.setReadOnly(read_only)
            editor.blockSignals(False)

    @Slot(str)
    def slotSetValue(self, value):
        # object = self.q_ptr.sender()
        obj = self.editor
        for itEditor in self.d_ptr.m_editorToProperty.keys():
            if itEditor == obj:
                prop = self.d_ptr.m_editorToProperty[itEditor]
                manager = self.propertyManager(prop)
                if not manager:
                    return

                manager.setValue(prop, value)
                return

    # def slotRegExpChanged(self, property, regExp):
    #     editors = self.m_createdEditors.get(property)
    #     if not editors:
    #         return
    #
    #     manager = self.q_ptr.propertyManager(property)
    #     if (not manager):
    #         return
    #
    #     for editor in editors:
    #         editor.blockSignals(True)
    #         oldValidator = editor.validator()
    #         newValidator = 0
    #         if (regExp.isValid()):
    #             newValidator = QRegularExpressionValidator(regExp, editor)
    #
    #         editor.setValidator(newValidator)
    #         if (oldValidator):
    #             del oldValidator
    #         editor.blockSignals(False)


#####################################################################################
#
#   class QtSpinBoxFactory
#
#   brief The QtSpinBoxFactory class provides QSpinBox widgets for properies
#         created by QtIntPropertyManager objects.
#
#####################################################################################
class QtSpinBoxFactoryPrivate(EditorFactoryPrivate):
    def __init__(self):
        super(QtSpinBoxFactoryPrivate, self).__init__()
        self.q_ptr = None


registerEditorFactory(QtSpinBoxFactoryPrivate, QSpinBox)


class QtSpinBoxFactory(QtAbstractEditorFactory):
    def __init__(self, parent=None):
        """
        Creates a factory with the given parent.
        """
        super(QtSpinBoxFactory, self).__init__(parent)

        self.d_ptr = QtSpinBoxFactoryPrivate()
        self.d_ptr.q_ptr = self
        self.editor = None

    def __del__(self):
        """
        Destroys this factory, and all the widgets it has created.
        """
        self.d_ptr.m_editorToProperty.clear()
        del self.d_ptr

    def createEditor(self, manager, prop, parent):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        editor = self.d_ptr.createEditor(prop, parent)
        editor.setSingleStep(manager.singleStep(prop))
        editor.setRange(manager.minimum(prop), manager.maximum(prop))
        editor.setValue(manager.value(prop))
        editor.setKeyboardTracking(False)
        editor.setReadOnly(manager.isReadOnly(prop))

        editor.valueChanged.connect(self.slotSetValue)
        editor.destroyed.connect(self.d_ptr.slotEditorDestroyed)

        self.editor = editor

        return editor

    def connectPropertyManager(self, manager):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        manager.valueChangedSignal.connect(self.slotValueChanged)
        manager.rangeChangedSignal.connect(self.slotRangeChanged)
        manager.singleStepChangedSignal.connect(self.slotSingleStepChanged)
        manager.readOnlyChangedSignal.connect(self.slotReadOnlyChanged)

    def disconnectPropertyManager(self, manager):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        manager.valueChangedSignal.disconnect(self.slotValueChanged)
        manager.rangeChangedSignal.disconnect(self.slotRangeChanged)
        manager.singleStepChangedSignal.disconnect(self.slotSingleStepChanged)
        manager.readOnlyChangedSignal.disconnect(self.slotReadOnlyChanged)

    @Slot(QtProperty, int)
    def slotValueChanged(self, prop, value):
        editors = self.d_ptr.m_createdEditors.get(prop)
        if not editors:
            return

        for editor in editors:
            editor.blockSignals(True)
            editor.setValue(value)
            editor.blockSignals(False)

    @Slot(QtProperty, int, int)
    def slotRangeChanged(self, prop, min_val, max_val):
        editors = self.d_ptr.m_createdEditors.get(prop)
        if not editors:
            return

        manager = self.propertyManager(prop)
        if not manager:
            return

        for editor in editors:
            editor.blockSignals(True)
            editor.setRange(min_val, max_val)
            editor.setValue(manager.value(prop))
            editor.blockSignals(False)

    @Slot(QtProperty, int)
    def slotSingleStepChanged(self, prop, step):
        editors = self.d_ptr.m_createdEditors.get(prop)
        if not editors:
            return

        manager = self.propertyManager(prop)
        if not manager:
            return

        for editor in editors:
            editor.blockSignals(True)
            editor.setSingleStep(step)
            editor.blockSignals(False)

    @Slot(QtProperty, bool)
    def slotReadOnlyChanged(self, prop, read_only):
        editors = self.d_ptr.m_createdEditors.get(prop)
        if not editors:
            return

        manager = self.propertyManager(prop)
        if not manager:
            return

        for editor in editors:
            editor.blockSignals(True)
            editor.setReadOnly(read_only)
            editor.blockSignals(False)

    def slotSetValue(self, value):
        obj = self.editor
        for itEditor in self.d_ptr.m_editorToProperty.keys():
            if itEditor == obj:
                prop = self.d_ptr.m_editorToProperty[itEditor]
                manager = self.propertyManager(prop)
                if not manager:
                    return

                manager.setValue(prop, value)

                return


#####################################################################################
#
#   class QtDoubleSpinBoxFactory
#
#   brief The QtDoubleSpinBoxFactory class provides QDoubleSpinBox widgets for properies
#         created by QtIntPropertyManager objects.
#
#####################################################################################
class QtDoubleSpinBoxFactoryPrivate(EditorFactoryPrivate):
    def __init__(self):
        super(QtDoubleSpinBoxFactoryPrivate, self).__init__()
        self.q_ptr = None


registerEditorFactory(QtDoubleSpinBoxFactoryPrivate, QDoubleSpinBox)


class QtDoubleSpinBoxFactory(QtAbstractEditorFactory):
    def __init__(self, parent=None):
        """
        Creates a factory with the given parent.
        """
        super(QtDoubleSpinBoxFactory, self).__init__(parent)

        self.d_ptr = QtDoubleSpinBoxFactoryPrivate()
        self.d_ptr.q_ptr = self
        self.editor = None

    def createEditor(self, manager, prop, parent):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        editor = self.d_ptr.createEditor(prop, parent)
        editor.setSingleStep(manager.singleStep(prop))
        editor.setDecimals(manager.decimals(prop))
        editor.setRange(manager.minimum(prop), manager.maximum(prop))
        editor.setValue(manager.value(prop))
        editor.setKeyboardTracking(False)
        editor.setReadOnly(manager.isReadOnly(prop))

        editor.valueChanged.connect(self.slotSetValue)
        editor.destroyed.connect(self.d_ptr.slotEditorDestroyed)

        self.editor = editor

        return editor

    def connectPropertyManager(self, manager):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        manager.valueChangedSignal.connect(self.slotValueChanged)
        manager.decimalsChangedSignal.connect(self.slotDecimalsChanged)
        manager.rangeChangedSignal.connect(self.slotRangeChanged)
        manager.singleStepChangedSignal.connect(self.slotSingleStepChanged)
        manager.readOnlyChangedSignal.connect(self.slotReadOnlyChanged)

    def disconnectPropertyManager(self, manager):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        manager.valueChangedSignal.disconnect(self.slotValueChanged)
        manager.decimalsChangedSignal.disconnect(self.slotDecimalsChanged)
        manager.rangeChangedSignal.disconnect(self.slotRangeChanged)
        manager.singleStepChangedSignal.disconnect(self.slotSingleStepChanged)
        manager.readOnlyChangedSignal.disconnect(self.slotReadOnlyChanged)

    @Slot(QtProperty, float)
    def slotValueChanged(self, prop, value):
        editors = self.d_ptr.m_createdEditors.get(prop)
        if not editors:
            return

        for editor in editors:
            # if editor != value:
            editor.blockSignals(True)
            editor.setValue(value)
            editor.blockSignals(False)

    @Slot(QtProperty, int)
    def slotDecimalsChanged(self, prop, precision):
        editors = self.d_ptr.m_createdEditors.get(prop)
        if not editors:
            return

        manager = self.propertyManager(prop)
        if not manager:
            return

        for editor in editors:
            editor.blockSignals(True)
            editor.setDecimals(precision)
            editor.setValue(manager.value(prop))
            editor.blockSignals(False)

    @Slot(QtProperty, float, float)
    def slotRangeChanged(self, prop, min_val, max_val):
        editors = self.d_ptr.m_createdEditors.get(prop)
        if not editors:
            return

        manager = self.propertyManager(prop)
        if not manager:
            return

        for editor in editors:
            editor.blockSignals(True)
            editor.setRange(min_val, max_val)
            editor.setValue(manager.value(prop))
            editor.blockSignals(False)

    @Slot(QtProperty, float)
    def slotSingleStepChanged(self, prop, step):
        editors = self.d_ptr.m_createdEditors.get(prop)
        if not editors:
            return

        manager = self.propertyManager(prop)
        if not manager:
            return

        for editor in editors:
            editor.blockSignals(True)
            editor.setSingleStep(step)
            editor.blockSignals(False)

    @Slot(QtProperty, bool)
    def slotReadOnlyChanged(self, prop, read_only):
        editors = self.d_ptr.m_createdEditors.get(prop)
        if not editors:
            return

        manager = self.propertyManager(prop)
        if not manager:
            return

        for editor in editors:
            editor.blockSignals(True)
            editor.setReadOnly(read_only)
            editor.blockSignals(False)

    def slotSetValue(self, value):
        obj = self.editor
        for itEditor in self.d_ptr.m_editorToProperty.keys():
            if itEditor == obj:
                prop = self.d_ptr.m_editorToProperty[itEditor]
                manager = self.propertyManager(prop)
                if not manager:
                    return

                manager.setValue(prop, value)

                return


#####################################################################################
#
#   class QtCheckBoxFactory
#
#   brief The QtCheckBoxFactory class provides QCheckBox widgets for
#         properties created by QtBoolPropertyManager objects.
#
#####################################################################################
class QtCheckBoxFactoryPrivate(EditorFactoryPrivate):
    def __init__(self):
        super(QtCheckBoxFactoryPrivate, self).__init__()
        self.q_ptr = None


registerEditorFactory(QtCheckBoxFactoryPrivate, QtBoolEdit)


class QtCheckBoxFactory(QtAbstractEditorFactory):
    def __init__(self, parent=None):
        """
        Creates a factory with the given parent.
        """
        super(QtCheckBoxFactory, self).__init__(parent)

        self.d_ptr = QtCheckBoxFactoryPrivate()
        self.d_ptr.q_ptr = self
        self.editor = None

    def __del__(self):
        """
        Destroys this factory, and all the widgets it has created.
        """
        self.d_ptr.m_editorToProperty.clear()
        del self.d_ptr

    def createEditor(self, manager, prop, parent):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        editor = self.d_ptr.createEditor(prop, parent)
        editor.setChecked(manager.value(prop))
        editor.setTextVisible(manager.textVisible(prop))

        editor.toggledSignal.connect(self.slotSetValue)
        editor.destroyed.connect(self.d_ptr.slotEditorDestroyed)

        self.editor = editor

        return editor

    def connectPropertyManager(self, manager):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        manager.valueChangedSignal.connect(self.slotValueChanged)
        manager.textVisibleChangedSignal.connect(self.slotTextVisibleChanged)

    def disconnectPropertyManager(self, manager):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        manager.valueChangedSignal.disconnect(self.slotValueChanged)
        manager.textVisibleChangedSignal.disconnect(self.slotTextVisibleChanged)

    @Slot(QtProperty, int)
    def slotValueChanged(self, prop, value):
        editors = self.d_ptr.m_createdEditors.get(prop)
        if not editors:
            return

        for editor in editors:
            editor.blockSignals(True)
            editor.setChecked(value)
            editor.blockSignals(False)

    @Slot(QtProperty, bool)
    def slotTextVisibleChanged(self, prop, text_visible):
        editors = self.d_ptr.m_createdEditors.get(prop)
        if not editors:
            return

        manager = self.propertyManager(prop)
        if not manager:
            return

        for editor in editors:
            editor.setTextVisible(text_visible)

    def slotSetValue(self, value):
        obj = self.editor
        for itEditor in self.d_ptr.m_editorToProperty.keys():
            if itEditor == obj:
                prop = self.d_ptr.m_editorToProperty[itEditor]
                manager = self.propertyManager(prop)
                if not manager:
                    return

                manager.setValue(prop, value)

                return


#####################################################################################
#
#   class   QtColorEditorFactory
#
#   brief   The QtColorEditorFactory class provides color editing for properties
#           created by QtColorPropertyManager objects.
#
#####################################################################################
class QtColorEditorFactoryPrivate(EditorFactoryPrivate):
    def __init__(self):
        super(QtColorEditorFactoryPrivate, self).__init__()
        self.q_ptr = None


registerEditorFactory(QtColorEditorFactoryPrivate, QtColorEditWidget)


class QtColorEditorFactory(QtAbstractEditorFactory):
    def __init__(self, parent=None):
        """
        Creates a factory with the given parent.
        """
        super(QtColorEditorFactory, self).__init__(parent)

        self.d_ptr = QtColorEditorFactoryPrivate()
        self.d_ptr.q_ptr = self
        self.editor = None

    def __del__(self):
        """
        Destroys this factory, and all the widgets it has created.
        """
        self.d_ptr.m_editorToProperty.clear()
        del self.d_ptr

    def createEditor(self, manager, prop, parent):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        editor = self.d_ptr.createEditor(prop, parent)
        editor.setValue(manager.value(prop))
        editor.valueChangedSignal.connect(self.slotSetValue)
        editor.destroyed.connect(self.d_ptr.slotEditorDestroyed)

        self.editor = editor

        return editor

    def connectPropertyManager(self, manager):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        manager.valueChangedSignal.connect(self.slotValueChanged)

    def disconnectPropertyManager(self, manager):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        manager.valueChangedSignal.disconnect(self.slotValueChanged)

    @Slot(QtProperty, int)
    def slotValueChanged(self, prop, value):
        editors = self.d_ptr.m_createdEditors.get(prop)
        if not editors:
            return

        for editor in editors:
            editor.setValue(value)

    def slotSetValue(self, value):
        obj = self.editor
        for itEditor in self.d_ptr.m_editorToProperty.keys():
            if itEditor == obj:
                prop = self.d_ptr.m_editorToProperty[itEditor]
                manager = self.propertyManager(prop)
                if not manager:
                    return

                manager.setValue(prop, value)

                return


#####################################################################################
#
#   class   QtEnumEditorFactory
#
#   brief   The QtEnumEditorFactory class provides QComboBox widgets for properties
#           created by QtEnumPropertyManager objects.
#
#####################################################################################
class QtEnumEditorFactoryPrivate(EditorFactoryPrivate):
    def __init__(self):
        super(QtEnumEditorFactoryPrivate, self).__init__()
        self.q_ptr = None


registerEditorFactory(QtEnumEditorFactoryPrivate, QComboBox)


class QtEnumEditorFactory(QtAbstractEditorFactory):
    def __init__(self, parent=None):
        """
        Creates a factory with the given parent.
        """
        super(QtEnumEditorFactory, self).__init__(parent)

        self.d_ptr = QtEnumEditorFactoryPrivate()
        self.d_ptr.q_ptr = self
        self.editor = None

    def __del__(self):
        """
        Destroys this factory, and all the widgets it has created.
        """
        self.d_ptr.m_editorToProperty.clear()
        del self.d_ptr

    def createEditor(self, manager, prop, parent):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        editor = self.d_ptr.createEditor(prop, parent)
        editor.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
        editor.setMinimumContentsLength(1)
        editor.view().setTextElideMode(Qt.ElideRight)
        names = manager.enumNames(prop)
        editor.addItems(names)

        icons = manager.enumIcons(prop)
        names_count = len(names)
        for i in range(names_count):
            icon = icons[i]
            if type(icon) is not QIcon:
                icon = QIcon()

            editor.setItemIcon(i, icon)
        editor.setCurrentIndex(manager.value(prop))

        editor.currentIndexChanged.connect(self.slotSetValue)
        editor.destroyed.connect(self.d_ptr.slotEditorDestroyed)

        self.editor = editor

        return editor

    def connectPropertyManager(self, manager):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        manager.valueChangedSignal.connect(self.slotValueChanged)
        manager.enumNamesChangedSignal.connect(self.slotEnumNamesChanged)

    def disconnectPropertyManager(self, manager):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        manager.valueChangedSignal.disconnect(self.slotValueChanged)
        manager.enumNamesChangedSignal.disconnect(self.slotEnumNamesChanged)

    @Slot(QtProperty, int)
    def slotValueChanged(self, prop, value):
        editors = self.d_ptr.m_createdEditors.get(prop)
        if not editors:
            return

        for editor in editors:
            editor.blockSignals(True)
            editor.setCurrentIndex(value)
            editor.blockSignals(False)

    @Slot(QtProperty, QList)
    def slotEnumNamesChanged(self, prop, names):
        editors = self.d_ptr.m_createdEditors.get(prop)
        if not editors:
            return

        mgr = self.propertyManager(prop)
        if not mgr:
            return

        icons = mgr.enumIcons(prop)

        for editor in editors:
            editor.blockSignals(True)
            editor.clear()
            editor.addItems(names)

            for i in range(len(names)):
                editor.setItemIcon(i, icons.get(i, QIcon))

            editor.setCurrentIndex(mgr.value(prop))
            editor.blockSignals(False)

    @Slot(QtProperty, QMap)
    def slotEnumIconsChanged(self, prop, icons):
        editors = self.d_ptr.m_createdEditors.get(prop)
        if not editors:
            return

        mgr = self.propertyManager(prop)
        if not mgr:
            return

        names = mgr.enumNames(prop)

        for editor in editors:
            editor.blockSignals(True)

            for i in range(len(names)):
                editor.setItemIcon(i, icons.value(i))

            editor.setCurrentIndex(mgr.value(prop))
            editor.blockSignals(False)

    def slotSetValue(self, value):
        obj = self.editor
        for editor in self.d_ptr.m_editorToProperty.keys():
            if editor == obj:
                prop = self.d_ptr.m_editorToProperty[editor]
                mgr = self.propertyManager(prop)
                if not mgr:
                    return

                mgr.setValue(prop, value)
                return


#####################################################################################
#
#   class   QtSliderFactory
#
#   brief   The QtSliderFactory class provides QSlider widgets for properties
#           created by QtIntPropertyManager objects.
#
#####################################################################################
class QtSliderFactoryPrivate(EditorFactoryPrivate):
    def __init__(self):
        super().__init__()
        self.q_ptr = None


registerEditorFactory(QtSliderFactoryPrivate, QSlider)


class QtSliderFactory(QtAbstractEditorFactory):
    def __init__(self, parent=None) -> None:
        """
        Creates a factory with the given parent.
        """
        super().__init__(parent)

        self.d_ptr = QtSliderFactoryPrivate()
        self.d_ptr.q_ptr = self
        self.editor = None

    def __del__(self):
        """
        Destroys this factory, and all the widgets it has created.
        """
        self.d_ptr.m_editorToProperty.clear()
        del self.d_ptr

    def createEditor(self, manager, prop, parent):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        editor = QSlider(Qt.Horizontal, parent)
        self.d_ptr.initializeEditor(prop, editor)
        editor.setSingleStep(manager.singleStep(prop))
        editor.setRange(manager.minimum(prop), manager.maximum(prop))
        editor.setValue(manager.value(prop))

        editor.valueChanged.connect(self.slotSetValue)
        editor.destroyed.connect(self.d_ptr.slotEditorDestroyed)

        self.editor = editor

        return editor

    def connectPropertyManager(self, manager):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        manager.valueChangedSignal.connect(self.slotValueChanged)
        manager.rangeChangedSignal.connect(self.slotRangeChanged)
        manager.singleStepChangedSignal.connect(self.slotSingleStepChanged)

    def disconnectPropertyManager(self, manager):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        manager.valueChangedSignal.disconnect(self.slotValueChanged)
        manager.rangeChangedSignal.disconnect(self.slotRangeChanged)
        manager.singleStepChangedSignal.disconnect(self.slotSingleStepChanged)

    def slotValueChanged(self, prop, value):
        editors = self.d_ptr.m_createdEditors.get(prop)
        if not editors:
            return

        for editor in editors:
            editor.blockSignals(True)
            editor.setValue(value)
            editor.blockSignals(False)

    def slotRangeChanged(self, prop, min_val, max_val):
        editors = self.d_ptr.m_createdEditors.get(prop)
        if not editors:
            return

        manager = self.propertyManager(prop)
        if not manager:
            return

        for editor in editors:
            editor.blockSignals(True)
            editor.setRange(min_val, max_val)
            editor.setValue(manager.value(prop))
            editor.blockSignals(False)

    def slotSingleStepChanged(self, prop, step):
        editors = self.d_ptr.m_createdEditors.get(prop)
        if not editors:
            return

        manager = self.propertyManager(prop)
        if not manager:
            return

        for editor in editors:
            editor.blockSignals(True)
            editor.setSingleStep(step)
            editor.blockSignals(False)

    def slotSetValue(self, value):
        obj = self.editor
        for itEditor in self.d_ptr.m_editorToProperty.keys():
            if itEditor == obj:
                prop = self.d_ptr.m_editorToProperty[itEditor]
                manager = self.propertyManager(prop)
                if not manager:
                    return

                manager.setValue(prop, value)

                return


#####################################################################################
#
#   class   QtScrollBarFactory
#
#   brief   The QtScrollBarFactory class provides QScrollBar widgets for properties
#           created by QtIntPropertyManager objects.
#
#####################################################################################
class QtScrollBarFactoryPrivate(EditorFactoryPrivate):
    def __init__(self):
        super().__init__()
        self.q_ptr = None


registerEditorFactory(QtScrollBarFactoryPrivate, QScrollBar)


class QtScrollBarFactory(QtAbstractEditorFactory):
    def __init__(self, parent=None) -> None:
        """
        Creates a factory with the given parent.
        """
        super().__init__(parent)

        self.d_ptr = QtScrollBarFactoryPrivate()
        self.d_ptr.q_ptr = self
        self.editor = None

    def __del__(self):
        """
        Destroys this factory, and all the widgets it has created.
        """
        self.d_ptr.m_editorToProperty.clear()
        del self.d_ptr

    def createEditor(self, manager, prop, parent):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        editor = QScrollBar(Qt.Horizontal, parent)
        self.d_ptr.initializeEditor(prop, editor)
        editor.setSingleStep(manager.singleStep(prop))
        editor.setRange(manager.minimum(prop), manager.maximum(prop))
        editor.setValue(manager.value(prop))
        
        editor.valueChanged.connect(self.slotSetValue)
        editor.destroyed.connect(self.d_ptr.slotEditorDestroyed)

        self.editor = editor

        return editor

    def connectPropertyManager(self, manager):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        manager.valueChangedSignal.connect(self.slotValueChanged)
        manager.rangeChangedSignal.connect(self.slotRangeChanged)
        manager.singleStepChangedSignal.connect(self.slotSingleStepChanged)

    def disconnectPropertyManager(self, manager):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        manager.valueChangedSignal.disconnect(self.slotValueChanged)
        manager.rangeChangedSignal.disconnect(self.slotRangeChanged)
        manager.singleStepChangedSignal.disconnect(self.slotSingleStepChanged)

    def slotValueChanged(self, prop, value):
        editors = self.d_ptr.m_createdEditors.get(prop)
        if not editors:
            return

        for editor in editors:
            editor.blockSignals(True)
            editor.setValue(value)
            editor.blockSignals(False)

    def slotRangeChanged(self, prop, min_val, max_val):
        editors = self.d_ptr.m_createdEditors.get(prop)
        if not editors:
            return

        manager = self.propertyManager(prop)
        if not manager:
            return

        for editor in editors:
            editor.blockSignals(True)
            editor.setRange(min_val, max_val)
            editor.setValue(manager.value(prop))
            editor.blockSignals(False)

    def slotSingleStepChanged(self, prop, step):
        editors = self.d_ptr.m_createdEditors.get(prop)
        if not editors:
            return

        manager = self.propertyManager(prop)
        if not manager:
            return

        for editor in editors:
            editor.blockSignals(True)
            editor.setSingleStep(step)
            editor.blockSignals(False)

    def slotSetValue(self, value):
        obj = self.editor
        for itEditor in self.d_ptr.m_editorToProperty.keys():
            if itEditor == obj:
                prop = self.d_ptr.m_editorToProperty[itEditor]
                manager = self.propertyManager(prop)
                if not manager:
                    return

                manager.setValue(prop, value)

                return


#####################################################################################
#
#   class   QtDateEditFactory
#
#   brief   The QtDateEditFactory class provides QDateEdit widgets for properties
#           created by QtIntPropertyManager objects.
#
#####################################################################################
class QtDateEditFactoryPrivate(EditorFactoryPrivate):
    def __init__(self):
        super().__init__()
        self.q_ptr = None


registerEditorFactory(QtDateEditFactoryPrivate, QDateEdit)


class QtDateEditFactory(QtAbstractEditorFactory):
    def __init__(self, parent=None) -> None:
        """
        Creates a factory with the given parent.
        """
        super().__init__(parent)
        self.d_ptr = QtDateEditFactoryPrivate()
        self.d_ptr.q_ptr = self
        self.editor = None

    def __del__(self):
        """
        Destroys this factory, and all the widgets it has created.
        """
        self.d_ptr.m_editorToProperty.clear()
        del self.d_ptr

    def createEditor(self, manager, prop, parent):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        editor = self.d_ptr.createEditor(prop, parent)
        editor.setCalendarPopup(True)
        editor.setDateRange(manager.minimum(prop), manager.maximum(prop))
        editor.setDate(manager.value(prop))

        editor.dateChanged.connect(self.slotSetValue)
        editor.destroyed.connect(self.d_ptr.slotEditorDestroyed)

        self.editor = editor

        return editor

    def connectPropertyManager(self, manager):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        manager.valueChangedSignal.connect(self.slotValueChanged)
        manager.rangeChangedSignal.connect(self.slotRangeChanged)

    def disconnectPropertyManager(self, manager):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        manager.valueChangedSignal.disconnect(self.slotValueChanged)
        manager.rangeChangedSignal.disconnect(self.slotRangeChanged)

    def slotValueChanged(self, prop, value):
        editors = self.d_ptr.m_createdEditors.get(prop)
        if not editors:
            return

        for editor in editors:
            editor.blockSignals(True)
            editor.setDate(value)
            editor.blockSignals(False)

    def slotRangeChanged(self, prop, min_val, max_val):
        editors = self.d_ptr.m_createdEditors.get(prop)
        if not editors:
            return

        mgr = self.propertyManager(prop)
        if not mgr:
            return
            
        for editor in editors:
            editor.blockSignals(True)
            editor.setDateRange(min_val, max_val)
            editor.setDate(mgr.value(prop))
            editor.blockSignals(False)

    def slotSetValue(self, value):
        obj = self.editor
        for itEditor in self.d_ptr.m_editorToProperty.keys():
            if itEditor == obj:
                prop = self.d_ptr.m_editorToProperty[itEditor]
                manager = self.propertyManager(prop)
                if not manager:
                    return

                manager.setValue(prop, value)

                return


#####################################################################################
#
#   class   QtTimeEditFactory
#
#   brief   The QtTimeEditFactory class provides QTimeEdit widgets for properties
#           created by QtTimePropertyManager objects.
#
#####################################################################################
class QtTimeEditFactoryPrivate(EditorFactoryPrivate):
    def __init__(self):
        super().__init__()
        self.q_ptr = None

    
registerEditorFactory(QtTimeEditFactoryPrivate, QTimeEdit)


class QtTimeEditFactory(QtAbstractEditorFactory):
    def __init__(self, parent=None) -> None:
        """
        Creates a factory with the given parent.
        """
        super().__init__(parent)
        self.d_ptr = QtTimeEditFactoryPrivate()
        self.d_ptr.q_ptr = self
        self.editor = None

    def __del__(self):
        """
        Destroys this factory, and all the widgets it has created.
        """
        self.d_ptr.m_editorToProperty.clear()
        del self.d_ptr

    def createEditor(self, manager, prop, parent):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        editor = self.d_ptr.createEditor(prop, parent)
        editor.setTime(manager.value(prop))

        editor.timeChanged.connect(self.slotSetValue)
        editor.destroyed.connect(self.d_ptr.slotEditorDestroyed)

        self.editor = editor

        return editor

    def connectPropertyManager(self, manager):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        manager.valueChangedSignal.connect(self.slotValueChanged)

    def disconnectPropertyManager(self, manager):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        manager.valueChangedSignal.disconnect(self.slotValueChanged)

    def slotValueChanged(self, prop, value):
        editors = self.d_ptr.m_createdEditors.get(prop)
        if not editors:
            return

        for editor in editors:
            editor.blockSignals(True)
            editor.setTime(value)
            editor.blockSignals(False)

    def slotSetValue(self, value):
        obj = self.editor
        for itEditor in self.d_ptr.m_editorToProperty.keys():
            if itEditor == obj:
                prop = self.d_ptr.m_editorToProperty[itEditor]
                mgr = self.propertyManager(prop)
                if not mgr:
                    return

                mgr.setValue(prop, value)

                return


#####################################################################################
#
#   class   QtDateTimeEditFactory
#
#   brief   The QtDateTimeEditFactory class provides QDateTimeEdit widgets 
#           for properties created by QtIntPropertyManager objects.
#
#####################################################################################
class QtDateTimeEditFactoryPrivate(EditorFactoryPrivate):
    def __init__(self):
        super().__init__()
        self.q_ptr = None


registerEditorFactory(QtDateTimeEditFactoryPrivate, QDateTimeEdit)


class QtDateTimeEditFactory(QtAbstractEditorFactory):
    def __init__(self, parent=None) -> None:
        """
        Creates a factory with the given parent.
        """
        super().__init__(parent)

        self.d_ptr = QtDateTimeEditFactoryPrivate()
        self.d_ptr.q_ptr = self
        self.editor = None

    def __del__(self):
        """
        Destroys this factory, and all the widgets it has created.
        """
        self.d_ptr.m_editorToProperty.clear()
        del self.d_ptr

    def createEditor(self, manager, prop, parent):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        editor = self.d_ptr.createEditor(prop, parent)
        editor.setDateTime(manager.value(prop))

        editor.dateTimeChanged.connect(self.slotSetValue)
        editor.destroyed.connect(self.d_ptr.slotEditorDestroyed)

        self.editor = editor

        return editor

    def connectPropertyManager(self, manager):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        manager.valueChangedSignal.connect(self.slotValueChanged)

    def disconnectPropertyManager(self, manager):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        manager.valueChangedSignal.disconnect(self.slotValueChanged)

    def slotValueChanged(self, prop, value):
        editors = self.d_ptr.m_createdEditors.get(prop)
        if not editors:
            return

        for editor in editors:
            editor.blockSignals(True)
            editor.setDateTime(value)
            editor.blockSignals(False)

    def slotSetValue(self, value):
        obj = self.editor
        for itEditor in self.d_ptr.m_editorToProperty.keys():
            if itEditor == obj:
                prop = self.d_ptr.m_editorToProperty[itEditor]
                mgr = self.propertyManager(prop)
                if not mgr:
                    return

                mgr.setValue(prop, value)
                return


#####################################################################################
#
#   class   QtFontEditorFactory
#
#   brief   The QtFontEditorFactory class provides font editing for properties
#           created by QtFontPropertyManager object.
#
#####################################################################################
class QtFontEditorFactoryPrivate(EditorFactoryPrivate):
    def __init__(self):
        super().__init__()
        self.q_ptr = None


registerEditorFactory(QtFontEditorFactoryPrivate, QtFontEditWidget)


class QtfontEditorFactory(QtAbstractEditorFactory):
    def __init__(self, parent=None) -> None:
        """
        Creates a factory with the given parent.
        """
        super().__init__(parent)

        self.d_ptr = QtFontEditorFactoryPrivate()
        self.d_ptr.q_ptr = self
        self.editor = None

    def __del__(self):
        """
        Destroys this factory, and all the widgets it has created.
        """
        self.d_ptr.m_editorToProperty.clear()
        del self.d_ptr

    def createEditor(self, manager, prop, parent):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        editor = self.d_ptr.createEditor(prop, parent)
        editor.setValue(manager.value(prop))
        editor.valueChanged.connect(self.slotSetValue)
        editor.destroyed.connect(self.d_ptr.slotEditorDestroyed)

        self.editor = editor

        return

    def connectPropertyManager(self, manager):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        manager.valueChangedSignal.connect(self.slotValueChanged)

    def disconnectPropertyManager(self, manager):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        manager.valueChangedSignal.disconnect(self.slotValueChanged)

    def slotValueChanged(self, prop, value):
        editors = self.d_ptr.m_createdEditors.get(prop)
        if not editors:
            return

        for editor in editors:
            editor.setValue(value)

    def slotSetValue(self, value):
        obj = self.editor
        prop = self.d_ptr.m_editorToProperty.get(obj)
        if prop:
            mgr = self.propertyManager(prop)
            if not mgr:
                return
            
            mgr.setValue(prop, value)

            return


#####################################################################################
#
#   class   QtKeySequenceEditorFactory
#
#   brief   The QtKeySequenceEditorFactory class provides font editing for properties
#           created by QtKeySequencePropertyManager object.
#
#####################################################################################
class QtKeySequenceEditorFactoryPrivate(EditorFactoryPrivate):
    def __init__(self):
        super().__init__()
        self.q_ptr = None


registerEditorFactory(QtKeySequenceEditorFactoryPrivate, QtKeySequenceEdit)


class QtKeySequenceEditorFactory(QtAbstractEditorFactory):
    def __init__(self, parent=None) -> None:
        """
        Creates a factory with the given parent.
        """
        super().__init__(parent)
        self.d_ptr = QtKeySequenceEditorFactoryPrivate()
        self.d_ptr.q_ptr = self
        self.editor = None

    def __del__(self):
        """
        Destroys this factory, and all the widgets it has created.
        """
        self.d_ptr.m_editorToProperty.clear()
        del self.d_ptr

    def createEditor(self, manager, prop, parent):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        editor = self.d_ptr.createEditor(prop, parent)
        editor.setKeySequence(manager.value(prop))

        editor.keySequenceChangedSignal.connect(self.slotSetValue)
        editor.destroyed.connect(self.d_ptr.slotEditorDestroyed)

        self.editor = editor

        return editor

    def connectPropertyManager(self, manager):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        manager.valueChangedSignal.connect(self.slotValueChanged)

    def disconnectPropertyManager(self, manager):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        manager.valueChangedSignal.disconnect(self.slotValueChanged)

    def slotValueChanged(self, prop, value):
        editors = self.d_ptr.m_createdEditors.get(prop)
        if not editors:
            return

        for editor in editors:
            editor.blockSignals(True)
            editor.setKeySequence(value)
            editor.blockSignals(False)

    def slotSetValue(self, value):
        obj = self.editor
        for itEditor in self.d_ptr.m_editorToProperty.keys():
            if itEditor == obj:
                prop = self.d_ptr.m_editorToProperty[itEditor]
                mgr = self.propertyManager(prop)
                if not mgr:
                    return
                
                mgr.setValue(prop, value)

                return


#####################################################################################
#
#   class QtCursorEditorFactory
#
#   brief The QtCursorEditorFactory class provides QComboBox widgets for properties
#         created by QtCursorPropertyManager objects.
#
#####################################################################################
class QtCursorEditorFactoryPrivate(EditorFactoryPrivate):
    def __init__(self):
        super().__init__()
        self.q_ptr = None


class QtCursorEditorFactory(QtAbstractEditorFactory):
    def __init__(self, parent=None) -> None:
        """
        Creates a factory with the given parent.
        """
        super().__init__(parent)
        self.d_ptr = QtCursorEditorFactoryPrivate()
        self.d_ptr.q_ptr = self

        self.updating_enum = False
        self.prop_to_enum = QMap()
        self.enum_to_prop = QMap()
        self.enum_to_editors = QMapList()
        self.editor_to_enum = QMap()

        self.enum_editor_factory = QtEnumEditorFactory(self)
        self.enum_prop_mgr = QtEnumPropertyManager(self)
        self.enum_prop_mgr.valueChangedSignal.connect(self.slotEnumChanged)
        self.enum_editor_factory.addPropertyManager(self.enum_prop_mgr)

        self.editor = None

    def __del__(self):
        """
        Destroys this factory, and all the widgets it has created.
        """
        # self.d_ptr.m_editorToProperty.clear()
        # del self.d_ptr
        pass

    def createEditor(self, manager, prop, parent):
        """
        Reimplemented from the QtAbstractEditorFactory class.
        """
        enum_prop = 0
        if prop in self.prop_to_enum:
            enum_prop = self.prop_to_enum[prop]
        else:
            enum_prop = self.enum_prop_mgr.addProperty(prop.propertyName())
            self.enum_prop_mgr.setEnumNames(enum_prop, cursorDatabase().cursorShapeNames())
            self.enum_prop_mgr.setEnumIcons(enum_prop, cursorDatabase().cursorShapeIcons())
            self.enum_prop_mgr.setValue(enum_prop, cursorDatabase().cursorToValue(manager.value(prop)))
            self.prop_to_enum[prop] = enum_prop
            self.enum_to_prop[enum_prop] = prop

        af = self.enum_editor_factory
        editor = af.findEditor(enum_prop, parent)
        self.enum_to_editors[enum_prop].append(editor)
        self.editor_to_enum[editor] = enum_prop
        editor.destroyed.connect(self.slotEditorDestroyed)

        self.editor = editor

        return editor

    def connectPropertyManager(self, manager):
        manager.valueChangedSignal.connect(self.slotValueChanged)

    def disconnectPropertyManager(self, manager):
        manager.valueChangedSignal.disconnect(self.slotValueChanged)

    def slotValueChanged(self, prop, cursor):
        # Update enum property
        enum_prop = self.prop_to_enum[prop]
        if not enum_prop:
            return

        self.updating_enum = True
        self.enum_prop_mgr.setValue(enum_prop, cursorDatabase().cursorToValue(cursor))
        self.updating_enum = False

    def slotEnumChanged(self, prop, value):
        if self.updating_enum:
            return

        # Update cursor property
        p = self.enum_to_prop[prop]
        if not p:
            return

        cursor_mgr = self.propertyManager(prop)
        if not cursor_mgr:
            return

        cursor_mgr.setValue(prop, QCursor(cursorDatabase().valueToCursor(value)))

    def slotEditorDestroyed(self, obj):
        # Remove from editorto_enum map
        # Remove from enum_to_editors map
        # if enum_to_editors doesn't contains more editors delete enum property
        for editor in self.editor_to_enum.keys():
            if editor == obj:
                enum_prop = self.editor_to_enum[editor]
                self.editor_to_enum.remove(editor)
                self.enum_to_editors[enum_prop].removeAll(editor)

                if len(self.enum_to_editors[enum_prop]) <= 0:
                    self.enum_to_editors.remove(enum_prop)
                    prop = self.enum_to_prop[enum_prop]
                    self.enum_to_prop.remove(enum_prop)
                    self.prop_to_enum.remove(prop)
                    del enum_prop

                return


#####################################################################################
#
#   class QtCharEditorFactory
#
#   brief The QtCharEditorFactory class provides editor widgets for properties
#         created by QtCharPropertyManager objects.
#
#####################################################################################
class QtCharEditorFactoryPrivate(EditorFactoryPrivate):
    def __init__(self):
        super().__init__()
        self.q_ptr = None


registerEditorFactory(QtCharEditorFactoryPrivate, QtCharEdit)


class QtCharEditorFactory(QtAbstractEditorFactory):
    def __init__(self, parent=None) -> None:
        """
        Creates a factory with the given parent.
        """
        super().__init__(parent)
        self.d_ptr = QtCharEditorFactoryPrivate()
        self.d_ptr.q_ptr = self
        self.editor = None

    def __del__(self):
        """
        Destroys this factory, and all the widgets it has created.
        """
        self.d_ptr.m_editorToProperty.clear()
        del self.d_ptr

    def createEditor(self, manager, prop, parent):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        editor = self.d_ptr.createEditor(prop, parent)
        editor.setValue(manager.value(prop))

        editor.valueChangedSignal.connect(self.slotSetValue)
        editor.destroyed.connect(self.d_ptr.slotEditorDestroyed)

        self.editor = editor

        return editor

    def connectPropertyManager(self, manager):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        manager.valueChangedSignal.connect(self.slotValueChanged)

    def disconnectPropertyManager(self, manager):
        """
        Reimplementation of QtAbstractEditorFactory.
        """
        manager.valueChangedSignal.disconnect(self.slotValueChanged)

    def slotValueChanged(self, prop, value):
        editors = self.d_ptr.m_createdEditors.get(prop)
        if not editors:
            return

        for editor in editors:
            editor.blockSignals(True)
            editor.setValue(value)
            editor.blockSignals(False)

    def slotSetValue(self, value):
        obj = self.editor
        for itEditor in self.d_ptr.m_editorToProperty.keys():
            if itEditor == obj:
                prop = self.d_ptr.m_editorToProperty[itEditor]
                mgr = self.propertyManager(prop)
                if not mgr:
                    return

                mgr.setValue(prop, value)

                return
    