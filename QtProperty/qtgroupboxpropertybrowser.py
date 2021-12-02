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

from PySide6.QtCore import Qt, QTimer, QRect
from PySide6.QtWidgets import QGridLayout, QSizePolicy, QSpacerItem, QLabel, QGroupBox, QFrame
from libqt5.pyqtcore import QList, QMap
from QtProperty.qtabstractpropertybrowser import QtAbstractPropertyBrowser


class WidgetItem:
    def __init__(self) -> None:
        self.widget = None
        self.label = None
        self.widget_label = None
        self.group_box = None
        self.layout = None
        self.line = None
        self.parent = None
        self.children = QList()


class QtGroupBoxPropertyBrowser(QtAbstractPropertyBrowser):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.index_to_item = QMap()
        self.item_to_index = QMap()
        self.widget_to_item = QMap()
        self.main_layout = 0
        self.children = QList()
        self.recreate_queue = QList()

        self.init()

    def __del__(self) -> None:
        """
        Destroys this property browser.

        Note that the properties that were inserted into this browser are
        not destroyed since they may still be used in other browsers.
        The properties are owned by the manager that created them.
        """
        for item in self.item_to_index.keys():
            del item

    def init(self):
        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)
        item = QSpacerItem(0, 0, QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.main_layout.addItem(item, 0, 0)

    def createEditor(self, prop, parent):
        return super().createEditor(prop, parent)

    def itemInserted(self, insertedItem, precedingItem) -> None:
        """
        Reimplementation
        """
        self.propertyInserted(insertedItem, precedingItem)

    def itemRemoved(self, item) -> None:
        """
        Reimplementation
        """
        self.propertyRemoved(item)

    def itemChanged(self, item) -> None:
        """
        Reimplementation
        """
        self.propertyChanged(item)

    def scrollPosition(self):
        """
        Returns the position of scroll bar
        """
        return 0, 0

    def setScrollPosition(self, dx, dy):
        """
        Sets scroll bars position
        """
        pass

    def slotEditorDestroyed(self):
        editor = self.sender()
        if not editor:
            return
        
        if not editor in self.widget_to_item.keys():
            return

        self.widget_to_item[editor] = 0
        self.widget_to_item.remove(editor)

    def slotUpdate(self):
        for item in self.recreate_queue:
            par = item.parent
            w = 0
            l = 0
            old_row = -1
            
            if not par:
                w = self
                l = self.main_layout
                old_row = self.children.indexOf(item)
            else:
                w = par.group_box
                l = par.layout
                old_row = par.children.indexOf(item)

                if self.hasHeader(par):
                    old_row += 2

            if item.widget:
                item.widget.setParent(w)
            elif item.widget_label:
                item.widget_label.setParent(w)
            else:
                item.widget_label = QLabel(w)
                item.widget_label.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed))
                item.widget_label.setTextFormat(Qt.PlanText)

            span = 1
            if item.widget:
                l.addWidget(item.widget, old_row, 1, 1, 1)
            elif item.widget_label:
                l.addWidget(item.widget_label, old_row, 1, 1, 1)
            else:
                span = 2
            
            item.label = QLabel(w)
            item.label.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
            l.addWidget(item.label, old_row, 0, 1, span)

            self.upateItem(item)

        self.recreate_queue.clear()

    def updateLater(self):
        QTimer.singleShot(0, self, self.slotUpdate())

    def propertyInserted(self, index, after_index):
        after_item = self.index_to_item[after_index]
        parent_item = self.index_to_item.value(index.parent())

        new_item = WidgetItem()
        new_item.parent = parent_item

        layout = 0
        parent_widget = 0
        row = -1

        if not after_item:
            row = 0

            if parent_item:
                parent_item.children.insert(0, new_item)
            else:
                self.children.insert(0, new_item)
        else:
            if parent_item:
                row = parent_item.children.indexOf(after_item) + 1
                parent_item.children.insert(row, new_item)
            else:
                row = self.children.indexOf(after_item) + 1
                self.children.insert(row, new_item)

        if parent_item and self.hasHeader(parent_item):
            row += 2

        if not parent_item:
            layout = self.main_layout
            parent_widget = self
        else:
            if not parent_item.group_box:
                self.recreate_queue.removeAll(parent_item)
                par = parent_item.parent

                w = 0
                l = 0
                old_row = -1

                if not par:
                    w = self
                    l = self.main_layout
                    old_row = self.children.indexOf(parent_item)
                else:
                    w = par.group_box
                    l = par.layout
                    old_row = par.children.indexOf(parent_item)

                    if self.hasHeader(par):
                        old_row += 2

                parent_item.group_box = QGroupBox(w)
                parent_item.layout = QGridLayout()
                parent_item.group_box.setLayout(parent_item.layout)

                if parent_item.label:
                    l.removeWidget(parent_item.label)
                    parent_item.label.close()
                    parent_item.label = 0

                if parent_item.widget:
                    l.removeWidget(parent_item.widget)
                    parent_item.widget.setParent(parent_item.group_box)
                    parent_item.layout.addWidget(parent_item.widget, 0, 0, 1, 2)
                    parent_item.line = QFrame(parent_item.group_box)
                elif parent_item.widget_label:
                    l.removeWidget(parent_item.widget_label)
                    parent_item.widget_label.close()
                    parent_item.widget_label = 0

                if parent_item.line:
                    parent_item.line.setFrameShape(QFrame.HLine)
                    parent_item.line.setFrameShadow(QFrame.Sunken)
                    parent_item.layout.addWidget(parent_item.line, 1, 0, 1, 2)
                
                l.addWidget(parent_item.group_box, old_row, 0, 1, 2)
                self.updateItem(parent_item)
            
            layout = parent_item.layout
            parent_widget = parent_item.group_box

        new_item.label = QLabel(parent_widget)
        new_item.label.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        new_item.widget = self.createEditor(index.property(), parent_widget)
        if not new_item.widget:
            new_item.widget_label = QLabel(parent_widget)
            new_item.widget_label.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed))
            new_item.widget_label.setTextFormat(Qt.PlainText)
        else:
            new_item.widget.destroyed.connect(self.slotEditorDestroyed)
            self.widget_to_item[new_item.widget] = new_item

        self.insertRow(layout, row)
        span = 1
        if new_item.widget:
            layout.addWidget(new_item.widget, row, 1)
        elif new_item.widget_label:
            layout.addWidget(new_item.widget_label, row, 1)
        else:
            span = 2
        
        layout.addWidget(new_item.label, row, 0, 1, span)

        self.item_to_index[new_item] = index
        self.index_to_item[index] = new_item

        self.updateItem(new_item)

    def propertyRemoved(self, index):
        item = self.index_to_item[index]

        self.index_to_item.remove(index)
        self.item_to_index.remove(item)

        parent_item = item.parent

        row = -1

        if parent_item:
            row = parent_item.children.indexOf(item)
            parent_item.children.removeAt(row)

            if self.hasHeader(parent_item):
                row += 2
        else:
            row = self.children.indexOf(item)
            self.children.removeAt(row)
        
        if item.widget:
            item.widget.close()
            del item.widget
        
        if item.label:
            item.label.close()
            del item.label

        if item.widget_label:
            item.widget_label.close()
            del item.widget_label

        if item.group_box:
            item.group_box.close()
            del item.group_box

        if not parent_item:
            self.removeRow(self.main_layout, row)
        elif len(parent_item.children) > 0:
            self.removeRow(parent_item.layout, row)
        else:
            par = parent_item.parent
            l = 0
            old_orw = -1

            if not par:
                l = self.main_layout
                old_row = self.children.indexOf(parent_item)
            else:
                l = par.layout
                old_row = par.children.indexOf(parent_item)

                if self.hasHeader(par):
                    old_row += 2

            if parent_item.widget:
                parent_item.widget.hide()
                parent_item.widget.setParent(0)
            elif parent_item.widget_label:
                parent_item.widget_label.hide()
                parent_item.widget_label.setParent(0)
            else:
                pass

            l.removeWidget(parent_item.group_box)
            parent_item.group_box.close()
            parent_item.group_box = 0
            parent_item.line = 0
            parent_item.layout = 0

            if not parent_item in self.recreate_queue:
                self.recreate_queue.append(parent_item)
            
            self.updateLater()

        self.recreate_queue.removeAll(item)

        del item
    
    def insertRow(self, layout, row):
        item_to_pos = QMap()
        idx = 0

        while idx < layout.count():
            r, c, rs, cs = layout.getItemPosition(idx)
            if r >= row:
                item_to_pos[layout.takeAt(idx)] = QRect(r + 1, c, rs, cs)
            else:
                idx += 1

        for it in item_to_pos.keys():
            r = item_to_pos[it]
            layout.addItem(it, r.x(), r.y(), r.width(), r.height())

    def removeRow(self, layout, row):
        item_to_pos = QMap()
        idx = 0

        while idx < layout.count():
            r, c, rs, cs = layout.getItemPosition(idx)
            if r > row:
                item_to_pos[layout.takeAt(idx)] = QRect(r - 1, c, rs, cs)
            else:
                idx += 1

        for it in item_to_pos.keys():
            r = item_to_pos[it]
            layout.addItem(it, r.x(), r.y(), r.width(), r.height())

    def hasHeader(self, item):
        if item.widget:
            return True
        
        return False

    def propertyChanged(self, index):
        item = self.index_to_item[index]

        self.updateItem(item)

    def updateItem(self, item):
        prop = self.item_to_index[item].property()
        if item.group_box:
            font = item.group_box.font()
            font.setUnderline(prop.isModified())

            item.group_box.setFont(font)
            item.group_box.setTitle(prop.propertyName())
            item.group_box.setToolTip(prop.toolTip())
            item.group_box.setStatusTip(prop.statusTip())
            item.group_box.setWhatsThis(prop.whatsThis())
            item.group_box.setEnabled(prop.isEnabled())

        if item.label:
            font = item.label.font()
            font.setUnderline(prop.isModified())
            item.label.setFont(font)
            item.label.setText(prop.propertyName())
            item.label.setToolTip(prop.toolTip())
            item.label.setStatusTip(prop.statusTip())
            item.label.setWhatsThis(prop.whatsThis())
            item.label.setEnabled(prop.isEnabled())

        if item.widget_label:
            font = item.widget_label.font()
            font.setUnderline(False)
            item.widget_label.setFont(font)
            item.widget_label.setText(prop.valueText())
            item.widget_label.setToolTip(prop.valueText())
            item.widget_label.setEnabled(prop.isEnabled())

        if item.widget:
            font = item.widget.font()
            font.setUnderline(False)
            item.widget.setFont(font)
            item.widget.setEnabled(prop.isEnabled())
            item.widget.setToolTip(prop.valueText())

