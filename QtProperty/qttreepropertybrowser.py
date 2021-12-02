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

import ctypes
from PySide6.QtCore import (
    Qt,
    QRect,
    QEvent,
    QSize,
    QCoreApplication,
    Property,
    Signal,
    Slot,
    QModelIndex
)
from PySide6.QtWidgets import (
    QStyleOption,
    QStyle,
    QTreeWidget,
    QStyleOptionViewItem,
    QApplication,
    QItemDelegate,
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QTreeWidgetItem
)
from PySide6.QtGui import QPixmap, QIcon, QPainter, QPalette, QPen, QColor, QFontMetrics

from libqt5.pyqtcore import QMap, QList
from QtProperty.qtbrowseritem import QtBrowserItem
from QtProperty.qtproperty import QtProperty
from QtProperty.qtabstractpropertybrowser import QtAbstractPropertyBrowser


def drawIndicatorIcon(palette, style):
    """
    Draws an icon indicating opened/closing branches
    """
    pix = QPixmap(14, 14)
    pix.fill(Qt.transparent)
    branchOption = QStyleOption()
    #r = QRect(QPoint(0, 0), pix.size())
    branchOption.rect = QRect(2, 2, 9, 9)   # hardcoded in qcommonstyle.cpp
    branchOption.palette = palette
    branchOption.state = QStyle.State_Children

    p = QPainter()

    ## Draw closed state
    p.begin(pix)
    style.drawPrimitive(QStyle.PE_IndicatorBranch, branchOption, p)
    p.end()
    rc = QIcon(pix)
    rc.addPixmap(pix, QIcon.Selected, QIcon.Off)

    ## Draw opened state
    branchOption.state |= QStyle.State_Open
    pix.fill(Qt.transparent)
    p.begin(pix)
    style.drawPrimitive(QStyle.PE_IndicatorBranch, branchOption, p)
    p.end()

    rc.addPixmap(pix, QIcon.Normal, QIcon.On)
    rc.addPixmap(pix, QIcon.Selected, QIcon.On)
    return rc


## ------------ QtPropertyEditorView
class QtPropertyEditorView(QTreeWidget):
    def __init__(self, parent):
        super(QtPropertyEditorView, self).__init__(parent)

        self.m_editorPrivate = None
        self.header().sectionDoubleClicked.connect(self.resizeColumnToContents)

    def setEditorPrivate(self, editorPrivate):
        self.m_editorPrivate = editorPrivate

    def indexToItem(self, index):
        return self.itemFromIndex(index)

    def drawRow(self, painter, option, index):
        opt = QStyleOptionViewItem(option)
        hasValue = True
        if self.m_editorPrivate:
            prop = self.m_editorPrivate.indexToProperty(index)
            if prop:
                hasValue = prop.hasValue()

        if not hasValue and self.m_editorPrivate.markPropertiesWithoutValue():
            c = option.palette.color(QPalette.Dark)
            painter.fillRect(option.rect, c)
            opt.palette.setColor(QPalette.AlternateBase, c)
        else:
            c = self.m_editorPrivate.calculatedBackgroundColor(self.m_editorPrivate.indexToBrowserItem(index))
            if c.isValid():
                painter.fillRect(option.rect, c)
                opt.palette.setColor(QPalette.AlternateBase, c.lighter(112))

        super(QtPropertyEditorView, self).drawRow(painter, opt, index)

        # color = ctypes.c_ulong(QApplication.style().styleHint(QStyle.SH_Table_GridLineColor, opt)).value
        painter.save()
        painter.setPen(QPen(QColor(211, 211, 211)))
        painter.drawLine(opt.rect.x(), opt.rect.bottom(), opt.rect.right(), opt.rect.bottom())
        painter.restore()

    def keyPressEvent(self, event):
        if event.key() in [Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space]:  # Trigger Edit
            if not self.m_editorPrivate.editedItem():
                item = self.currentItem()
                if item:
                    if item.columnCount() >= 2 and ((item.flags() & (Qt.ItemIsEditable | Qt.ItemIsEnabled)) == (Qt.ItemIsEditable | Qt.ItemIsEnabled)):
                        event.accept()
                        ## If the current position is at column 0, move to 1.
                        index = self.currentIndex()
                        if index.column() == 0:
                            index = index.sibling(index.row(), 1)
                            self.setCurrentIndex(index)
                        self.edit(index)
                        return

        super(QtPropertyEditorView, self).keyPressEvent(event)

    def mousePressEvent(self, event):
        super(QtPropertyEditorView, self).mousePressEvent(event)
        item = self.itemAt(event.pos())

        if item:
            if ((item != self.m_editorPrivate.editedItem()) and (event.button() == Qt.LeftButton)
                    and (self.header().logicalIndexAt(event.pos().x()) == 1)
                    and ((item.flags() & (Qt.ItemIsEditable | Qt.ItemIsEnabled)) == (Qt.ItemIsEditable | Qt.ItemIsEnabled))):
                self.editItem(item, 1)
            elif not self.m_editorPrivate.hasValue(item) and self.m_editorPrivate.markPropertiesWithoutValue() and not self.rootIsDecorated():
                if event.pos().x() + self.header().offset() < 20:
                    item.setExpanded(not item.isExpanded())


## ------------ QtPropertyEditorDelegate
class QtPropertyEditorDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(QtPropertyEditorDelegate, self).__init__(parent)

        self.m_editorPrivate = None
        self.m_editedItem = None
        self.m_editedWidget = None
        self.m_disablePainting = False
        self.m_propertyToEditor = QMap()
        self.m_editorToProperty = QMap()

    def setEditorPrivate(self, editorPrivate):
        self.m_editorPrivate = editorPrivate

    def setModelData(self, pt_widget, pt_QAbstractItemModel, modelIndex):
        pass

    def setEditorData(self, pt_widget, modelIndex):
        pass

    def editedItem(self):
        return self.m_editedItem

    def indentation(self, index):
        if not self.m_editorPrivate:
            return 0

        item = self.m_editorPrivate.indexToItem(index)
        indent = 0
        while item.parent():
            item = item.parent()
            indent += 1
        if self.m_editorPrivate.treeWidget().rootIsDecorated():
            indent += 1
        return indent * self.m_editorPrivate.treeWidget().indentation()

    def slotEditorDestroyed(self, obj):
        return
        # if object:
        #     hv = object.property('hash_value')
        #     for x in self.m_editorToProperty:
        #         if x[0].hash_value==hv:
        #             self.m_propertyToEditor.remove(x)
        #             self.m_editorToProperty.erase(x)
        #             break
        #     if (self.m_editedWidget.hash_value == hv):
        #         self.m_editedWidget = 0
        #         self.m_editedItem = 0

    def destroyEditor(self, editor, index):
        if editor:
            hv = editor.property('hash_value')

            for x in self.m_editorToProperty:
                if x[0].hash_value == hv:
                    self.m_propertyToEditor.remove(x)
                    self.m_editorToProperty.erase(x)
                    break
            if self.m_editedWidget.hash_value == hv:
                self.m_editedWidget = 0
                self.m_editedItem = 0
            #editor.deleteLater()

    def closeEditor(self, prop):
        pass

    def createEditor(self, parent, pt_QStyleOptionViewItem, index):
        if index.column() == 1 and self.m_editorPrivate:
            prop = self.m_editorPrivate.indexToProperty(index)
            item = self.m_editorPrivate.indexToItem(index)

            if prop and item and (item.flags() & Qt.ItemIsEnabled):
                editor = self.m_editorPrivate.createEditor(prop, parent)

                if editor:
                    h = editor.__hash__()
                    editor.setProperty('hash_value', h)
                    editor.hash_value = h
                    editor.setAutoFillBackground(True)
                    editor.installEventFilter(self)
                    editor.destroyed.connect(self.slotEditorDestroyed)
                    self.m_propertyToEditor[prop] = editor
                    self.m_editorToProperty[editor] = prop
                    self.m_editedItem = item
                    self.m_editedWidget = editor

                    return editor
        return

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect.adjusted(0, 0, 0, -1))

    def paint(self, painter, option, index):
        hasValue = True
        if self.m_editorPrivate:
            prop = self.m_editorPrivate.indexToProperty(index)
            if prop:
                hasValue = prop.hasValue()

        opt = QStyleOptionViewItem(option)
        if (self.m_editorPrivate and index.column() == 0) or not hasValue:
            prop = self.m_editorPrivate.indexToProperty(index)
            if prop and prop.isModified():
                opt.font.setBold(True)
                opt.fontMetrics = QFontMetrics(opt.font)

        c = QColor()
        if not hasValue and self.m_editorPrivate.markPropertiesWithoutValue():
            c = opt.palette.color(QPalette.Dark)
            opt.palette.setColor(QPalette.Text, opt.palette.color(QPalette.BrightText))
        else:
            c = self.m_editorPrivate.calculatedBackgroundColor(self.m_editorPrivate.indexToBrowserItem(index))
            if c.isValid() and (opt.features & QStyleOptionViewItem.Alternate):
                c = c.lighter(112)

        if c.isValid():
            painter.fillRect(option.rect, c)
        opt.state &= ~QStyle.State_HasFocus

        if index.column() == 1:
            item = self.m_editorPrivate.indexToItem(index)
            if self.m_editedItem and (self.m_editedItem == item):
                self.m_disablePainting = True

        super(QtPropertyEditorDelegate, self).paint(painter, opt, index)
        if option.type:
            self.m_disablePainting = False

        opt.palette.setCurrentColorGroup(QPalette.Active)
        color = ctypes.c_ulong(QApplication.style().styleHint(QStyle.SH_Table_GridLineColor, opt)).value
        painter.save()
        painter.setPen(QPen(QColor(color)))
        if not self.m_editorPrivate or (not self.m_editorPrivate.lastColumn(index.column()) and hasValue):
            if option.direction == Qt.LeftToRight:
                right = option.rect.right()
            else:
                right = option.rect.left()
            painter.drawLine(right, option.rect.y(), right, option.rect.bottom())

        painter.restore()

    def drawDecoration(self, painter, option,rect, pixmap):
        if self.m_disablePainting:
            return

        super(QtPropertyEditorDelegate, self).drawDecoration(painter, option, rect, pixmap)

    def drawDisplay(self,painter, option, rect, text):
        if self.m_disablePainting:
            return

        super(QtPropertyEditorDelegate, self).drawDisplay(painter, option, rect, text)

    def sizeHint(self, option, index):
        return super(QtPropertyEditorDelegate, self).sizeHint(option, index) + QSize(3, 4)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.FocusOut:
            fe = event
            if fe.reason() == Qt.ActiveWindowFocusReason:
                return False

        if event.type() == QEvent.KeyPress:
            return super(QtPropertyEditorDelegate, self).eventFilter(obj, event)

        return super(QtPropertyEditorDelegate, self).eventFilter(obj, event)


######################################################################
#
#   class QtTreePropertyBrowser
#
#   brief The QtTreePropertyBrowser class provides QTreeWidget based
#   property browser.
#
#   A property browser is a widget that enables the user to edit a
#   given set of properties. Each property is represented by a label
#   specifying the property's name, and an editing widget (e.g. a line
#   edit or a combobox) holding its value. A property can have zero or
#   more subproperties.
#
#   QtTreePropertyBrowser provides a tree based view for all nested
#   properties, i.e. properties that have subproperties can be in an
#   expanded (subproperties are visible) or collapsed (subproperties
#   are hidden) state. For example:
#
#   Use the QtAbstractPropertyBrowser API to add, insert and remove
#   properties from an instance of the QtTreePropertyBrowser class.
#   The properties themselves are created and managed by
#   implementations of the QtAbstractPropertyManager class.
#
######################################################################
class QtTreePropertyBrowser(QtAbstractPropertyBrowser):
    Interactive, Stretch, Fixed, ResizeToContents = range(4)

    # Defines signals
    collapsedSignal = Signal(QtBrowserItem)
    expandedSignal = Signal(QtBrowserItem)

    def __init__(self, parent=None) -> None:
        super(QtTreePropertyBrowser, self).__init__(parent)

        self.m_indexToItem = QMap()
        self.m_itemToIndex = QMap()
        self.m_indexToBackgroundColor = QMap()

        self.m_treeWidget = None
        self.m_headerVisible = True
        self.m_resizeMode = QtTreePropertyBrowser.Stretch
        self.m_delegate = None
        self.m_markPropertiesWithoutValue = False
        self.m_browserChangedBlocked = False
        self.m_expandIcon = QIcon()

        self.init(self)
        self.currentItemChangedSignal.connect(self.slotCurrentBrowserItemChanged)

    """
    Note that the properties that were inserted into this browser are not destroyed
    since they may still be used in other browsers.
    The properties are owned by the manager that created them.
    """
    def __del__(self) -> None:
        """
        Destroys this property browser.
        """
        pass

    def init(self, parent):
        layout = QHBoxLayout(parent)
        layout.setContentsMargins(0, 0, 0, 0)
        self.m_treeWidget = QtPropertyEditorView(parent)
        self.m_treeWidget.setEditorPrivate(self)
        self.m_treeWidget.setIconSize(QSize(18, 18))
        layout.addWidget(self.m_treeWidget)
        parent.setFocusProxy(self.m_treeWidget)

        self.m_treeWidget.setColumnCount(2)
        labels = QList()
        labels.append(QCoreApplication.translate("QtTreePropertyBrowser", "Property"))
        labels.append(QCoreApplication.translate("QtTreePropertyBrowser", "Value"))
        self.m_treeWidget.setHeaderLabels(labels)
        self.m_treeWidget.setAlternatingRowColors(True)
        self.m_treeWidget.setEditTriggers(QAbstractItemView.EditKeyPressed)
        self.m_delegate = QtPropertyEditorDelegate(parent)
        self.m_delegate.setEditorPrivate(self)
        self.m_treeWidget.setItemDelegate(self.m_delegate)
        self.m_treeWidget.header().setSectionsMovable(False)
        self.m_treeWidget.header().setSectionResizeMode(QHeaderView.Stretch)

        self.m_expandIcon = drawIndicatorIcon(self.palette(), self.style())

        self.m_treeWidget.collapsed.connect(self.slotCollapsed)
        self.m_treeWidget.expanded.connect(self.slotExpanded)
        self.m_treeWidget.currentItemChanged.connect(self.slotCurrentTreeItemChanged)

    def createEditor(self, prop, parent):
        return super().createEditor(prop, parent)

    def currentItem(self):
        treeItem = self.m_treeWidget.currentItem()
        if treeItem:
            return self.m_itemToIndex.get(treeItem)

        return 0

    def setCurrItem(self, browserItem, block):
        blocked = False
        if block:
            blocked = self.m_treeWidget.blockSignals(True)
        if browserItem is None:
            self.m_treeWidget.setCurrentItem(None)
        else:
            self.m_treeWidget.setCurrentItem(self.m_indexToItem.get(browserItem))
        if block:
            self.m_treeWidget.blockSignals(blocked)

    def indexToProperty(self, index):
        item = self.m_treeWidget.indexToItem(index)
        idx = self.m_itemToIndex.get(item)
        if idx:
            return idx.property()
        return 0

    def propertyToIndex(self, prop: QtProperty):
        indices = self.m_propertyToIndexes.get(prop)
        if not indices:
            return

        for idx in indices:
            p = idx.property()
            if p == prop:
                return idx

    def indexToBrowserItem(self, index):
        item = self.m_treeWidget.indexToItem(index)
        return self.m_itemToIndex.get(item)

    def indexToItem(self, index):
        return self.m_treeWidget.indexToItem(index)

    def lastColumn(self, column):
        return self.m_treeWidget.header().visualIndex(column) == self.m_treeWidget.columnCount() - 1

    def disableItem(self, item):
        flags = item.flags()
        if flags & Qt.ItemIsEnabled:
            flags &= ~Qt.ItemIsEnabled
            item.setFlags(flags)
            self.m_delegate.closeEditor(self.m_itemToIndex[item].property())
            childCount = item.childCount()
            for i in range(childCount):
                child = item.child(i)
                self.disableItem(child)

    def enableItem(self, item):
        flags = item.flags()
        flags |= Qt.ItemIsEnabled
        item.setFlags(flags)
        childCount = item.childCount()
        for i in range(childCount):
            child = item.child(i)
            prop = self.m_itemToIndex[child].property()
            if prop.isEnabled():
                self.enableItem(child)

    def hasValue(self, item):
        browserItem = self.m_itemToIndex.get(item)
        if browserItem:
            return browserItem.property().hasValue()

        return False

    def propertyInserted(self, index, afterIndex):
        afterItem = self.m_indexToItem.get(afterIndex)
        parentItem = self.m_indexToItem.get(index.parent())

        newItem = 0
        if parentItem:
            newItem = QTreeWidgetItem(parentItem, afterItem)
        else:
            newItem = QTreeWidgetItem(self.m_treeWidget, afterItem)

        self.m_itemToIndex[newItem] = index
        self.m_indexToItem[index] = newItem

        newItem.setFlags(newItem.flags() | Qt.ItemIsEditable)
        newItem.setExpanded(True)

        self.updateItem(newItem)

    def propertyRemoved(self, index):
        item = self.m_indexToItem.get(index)

        if self.m_treeWidget.currentItem() == item:
            self.m_treeWidget.setCurrentItem(None)

        parent = item.parent()
        if parent:
            parent.removeChild(item)
        else:
            treeWidget = item.treeWidget()
            treeWidget.takeTopLevelItem(treeWidget.indexOfTopLevelItem(item))

        self.m_indexToItem.remove(index)
        self.m_itemToIndex.remove(item)
        self.m_indexToBackgroundColor.remove(index)

    def propertyChanged(self, index):
        item = self.m_indexToItem.get(index)
        self.updateItem(item)

    def treeWidget(self):
        return self.m_treeWidget

    def markPropertiesWithoutValue(self):
        return self.m_markPropertiesWithoutValue

    def updateItem(self, item):
        prop = self.m_itemToIndex[item].property()
        expandIcon = QIcon()

        if prop.hasValue():
            toolTip = prop.toolTip()

            if len(toolTip) <= 0:
                toolTip = prop.displayText()
            item.setToolTip(1, toolTip)
            item.setIcon(1, prop.valueIcon())

            if len(prop.displayText()) <= 0:
                item.setText(1, prop.valueText())
            else:
                item.setText(1, prop.displayText())

        elif self.markPropertiesWithoutValue() and not self.m_treeWidget.rootIsDecorated():
            expandIcon = self.m_expandIcon

        item.setIcon(0, expandIcon)
        item.setFirstColumnSpanned(not prop.hasValue())
        item.setToolTip(0, prop.propertyName())
        item.setStatusTip(0, prop.statusTip())
        item.setWhatsThis(0, prop.whatsThis())
        item.setText(0, prop.propertyName())
        wasEnabled = item.flags() & Qt.ItemIsEnabled
        isEnabled = wasEnabled

        if prop.isEnabled():
            parent = item.parent()
            if not parent or (parent.flags() & Qt.ItemIsEnabled):
                isEnabled = True
            else:
                isEnabled = False
        else:
            isEnabled = False

        if wasEnabled != isEnabled:
            if isEnabled:
                self.enableItem(item)
            else:
                self.disableItem(item)

        self.m_treeWidget.viewport().update()

    def editedItem(self):
        return self.m_delegate.editedItem()

    def editItem(self, browserItem):
        treeItem = self.m_indexToItem.get(browserItem, 0)
        if treeItem:
            self.m_treeWidget.setCurrentItem(treeItem, 1)
            self.m_treeWidget.editItem(treeItem, 1)

    def indentation(self):
        return self.m_treeWidget.indentation()

    def setIndentation(self, i):
        self.m_treeWidget.setIndentation(i)

    def rootIsDecorated(self):
        return self.m_treeWidget.rootIsDecorated()

    def setRootIsDecorated(self, show):
        self.m_treeWidget.setRootIsDecorated(show)
        for it in self.m_itemToIndex.keys():
            prop = self.m_itemToIndex[it].property()
            if not prop.hasValue():
                self.updateItem(it)

    def alternatingRowColors(self):
        return self.m_treeWidget.alternatingRowColors()

    def setAlternatingRowColors(self, enable):
        self.m_treeWidget.setAlternatingRowColors(enable)

    def isHeaderVisible(self):
        return self.m_headerVisible

    def setHeaderVisible(self, visible):
        if self.m_headerVisible == visible:
            return

        self.m_headerVisible = visible
        self.m_treeWidget.header().setVisible(visible)

    def resizeMode(self):
        return self.m_resizeMode

    def setResizeMode(self, mode):
        if self.m_resizeMode == mode:
            return

        self.m_resizeMode = mode
        m = QHeaderView.Stretch
        if mode == QtTreePropertyBrowser.Interactive:
            m = QHeaderView.Interactive
        elif mode == QtTreePropertyBrowser.Fixed:
            m = QHeaderView.Fixed
        elif mode == QtTreePropertyBrowser.ResizeToContents:
            m = QHeaderView.ResizeToContents

        self.m_treeWidget.header().setSectionResizeMode(m)

    def scrollPosition(self):
        return self.m_treeWidget.horizontalScrollBar().value(), self.m_treeWidget.verticalScrollBar().value()

    def setScrollPosition(self, dx, dy):
        self.m_treeWidget.horizontalScrollBar().setValue(dx)
        self.m_treeWidget.verticalScrollBar().setValue(dy)

    def splitterPosition(self):
        return self.m_treeWidget.header().sectionSize(0)

    def setSplitterPosition(self, position):
        self.m_treeWidget.header().resizeSection(0, position)

    def setExpanded(self, item: QtBrowserItem, expanded: bool) -> None:
        treeItem = self.m_indexToItem.get(item)
        if treeItem:
            treeItem.setExpanded(expanded)

    def setExpandedByProperty(self, prop: QtProperty, expanded: bool) -> None:
        idx = self.propertyToIndex(prop)    # idx is QtBrowserItem
        tree_item = self.m_indexToItem.get(idx)
        if tree_item:
            tree_item.setExpanded(expanded)

    def isExpanded(self, item: QtBrowserItem) -> bool:
        treeItem = self.m_indexToItem.get(item)
        if treeItem:
            return treeItem.isExpanded()

        return False

    def isItemVisible(self, item: QtBrowserItem) -> bool:
        treeItem = self.m_indexToItem.get(item)
        if treeItem:
            return not treeItem.isHidden()
        return False

    def setItemVisible(self, item: QtBrowserItem, visible: bool) -> None:
        treeItem = self.m_indexToItem.get(item)
        if treeItem:
            treeItem.setHidden(not visible)

    def setBackgroundColor(self, item, color):
        if not item in self.m_indexToItem:
            return
        if color.isValid():
            self.m_indexToBackgroundColor[item] = color
        else:
            self.m_indexToBackgroundColor.remove(item)
        self.m_treeWidget.viewport().update()

    def backgroundColor(self, item):
        return self.m_indexToBackgroundColor.get(item)

    def calculatedBackgroundColor(self, item):
        i = item
        while i:
            it = self.m_indexToBackgroundColor.get(i)
            if it:
                return it
            i = i.parent()

        return QColor()

    def setPropertiesWithoutValueMarked(self, mark):
        if self.m_markPropertiesWithoutValue == mark:
            return

        self.m_markPropertiesWithoutValue = mark
        for it in self.m_itemToIndex.keys():
            prop = self.m_itemToIndex[it].property()
            if not prop.hasValue():
                self.updateItem(it)

        self.m_treeWidget.viewport().update()

    def propertiesWithoutValueMarked(self):
        return self.m_markPropertiesWithoutValue

    def itemInserted(self, item, afterItem):
        """
        Reimplementation
        """
        self.propertyInserted(item, afterItem)

    def itemRemoved(self, item):
        """
        Reimplementation
        """
        self.propertyRemoved(item)

    def itemChanged(self, item):
        """
        Reimplementation
        """
        self.propertyChanged(item)

    @Slot(QModelIndex)
    def slotCollapsed(self, index):
        item = self.indexToItem(index)
        idx = self.m_itemToIndex.get(item)
        if item:
            if idx is None:
                idx = QtBrowserItem()
            self.collapsedSignal.emit(idx)

    @Slot(QModelIndex)
    def slotExpanded(self, index):
        item = self.indexToItem(index)
        idx = self.m_itemToIndex.get(item)
        if item:
            self.expandedSignal.emit(idx)

    @Slot(QtBrowserItem)
    def slotCurrentBrowserItemChanged(self, item):
        if not self.m_browserChangedBlocked and item != self.currentItem():
            self.setCurrItem(item, True)

    @Slot(QTreeWidgetItem, QTreeWidgetItem)
    def slotCurrentTreeItemChanged(self, newItem, pt_QTreeWidgetItem):
        browserItem = 0
        if newItem:
            browserItem = self.m_itemToIndex.get(newItem)

        self.m_browserChangedBlocked = True
        self.setCurrentItem(browserItem)
        self.m_browserChangedBlocked = False

    ###
    #   Sets the current item to \a item and opens the relevant editor for it.
    ###
    indentation = Property(int, indentation, setIndentation)
    rootIsDecorated = Property(bool, rootIsDecorated, setRootIsDecorated)
    alternatingRowColors = Property(bool, alternatingRowColors, setAlternatingRowColors)
    headerVisible = Property(bool, isHeaderVisible, setHeaderVisible)
    resizeMode = Property(int, resizeMode, setResizeMode)
    splitterPosition = Property(int, splitterPosition, setSplitterPosition)
    propertiesWithoutValueMarked = Property(bool, propertiesWithoutValueMarked, setPropertiesWithoutValueMarked)
