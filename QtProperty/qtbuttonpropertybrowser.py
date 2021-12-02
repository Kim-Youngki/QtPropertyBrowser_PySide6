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
#   Modified by Youngki Kim in 2021/11/17 for PySide6 support
#
############################################################################


from PySide6.QtCore import Signal, Qt, QSize, QTimer, QRect
from PySide6.QtWidgets import QGridLayout, QSizePolicy, QSpacerItem, QToolButton, QLabel, QFrame
from libqt5.pyqtcore import QList, QMap
from QtProperty.qtbrowseritem import QtBrowserItem
from QtProperty.qtabstractpropertybrowser import QtAbstractPropertyBrowser


class WidgetItem:
    def __init__(self) -> None:
        self.label = 0
        self.widget_label = 0
        self.button = 0
        self.container = 0
        self.layout = 0
        self.parent = None
        self.children = QList()
        self.expanded = False
        self.widget = 0


######################################################################################
#
#   class   QtButtonProeprtyBrowser
#
#   brief   The QtButtonPropertyBrowser class provides a drop down QToolButton
#           based property browser.
#
#   A property browser is a widget that enables the user to edit a given set
#   of properties. Each property is represented by a label specifying
#   the property's name, and an editing widget (e.g. a line edit or a combobox)
#   holding its value. A property can have zero or moe subproperties.
#
#   QtButtonPropertyBrowser provides drop down button for all nested properties,
#   i.e. subproperties are enclosed by a container associated with the drop down
#   button. The parent property's name is displayed as button text.
#
#   Use the QtAbstractPropertyBrowser API to add, insert and remove properties
#   from an instance of the QtButtonPropertyBrowser class. The properteis
#   themselves are created and managed by implementations of 
#   the QtAbstractpropertyManager class.
#
#   = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#   QtButtonPropertyBrowser signal description:
#
#   collapsed(item)
#
#   This signal is emitted when the item is collapsed.
#
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   expanded(item)
#
#   This signal is emitted when the item is expanded.
#
#   = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#
#   TODO: Currently QtButtonPropertyBrowser has some problems.
#
######################################################################################
class QtButtonPropertyBrowser(QtAbstractPropertyBrowser):
    # Defines custom signals
    collapsedSignal = Signal(QtBrowserItem)
    expandedSignal = Signal(QtBrowserItem)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.widget_item = WidgetItem()
        self.index_to_item = QMap()
        self.item_to_index = QMap()
        self.widget_to_item = QMap()
        self.button_to_item = QMap()

        self.main_layout = None
        self.children = QList()
        self.recreate_queue = QList()

        self.init()

    def __del__(self) -> None:
        """
        Destroyes this property browser.

        Note that the properties that were inserted ito this browser are
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

    def createButton(self, parent=None):
        btn = QToolButton(parent)
        btn.setCheckable(True)
        btn.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed))
        btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        btn.setArrowType(Qt.DownArrow)
        btn.setIconSize(QSize(3, 16))

        return btn

    def gridRow(self, item):
        siblings = QList()
        if item.parent:
            siblings = item.parent.children
        else:
            siblings = self.children
        
        row = 0
        for sibling in siblings:
            if sibling == item:
                return row
            
            row += self.gridSpan(sibling)

        return -1

    def gridSpan(self, item):
        if item.container and item.expanded:
            return 2
        
        return 1

    def itemInserted(self, item, after_item):
        """
        Reimplementation
        """
        self.propertyInserted(item, after_item)

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

    def setExpanded(self, item, expanded):
        """
        Sets the item to either collapse or expanded, depending on the value of expanded.
        """
        # i = self.index_to_item[item]
        # if i is None:
        #     return

        if item.expanded == expanded:
            return

        if not item.container:
            return

        item.expanded = expanded
        row = self.gridRow(item)
        parent = item.parent
        l = 0
        if parent:
            l = parent.layout
        else:
            l = self.main_layout

        if expanded:
            self.insertRow(l, row + 1)
            l.addWidget(item.container, row + 1, 0, 1, 2)
            item.container.show()
        else:
            l.removeWidget(item.container)
            item.container.hide()
            self.removeRow(l, row + 1)

        item.button.setChecked(expanded)
        if expanded:
            item.button.setArrowType(Qt.UpArrow)
        else:
            item.button.setArrowType(Qt.DownArrow)

    def isExpanded(self, item) -> bool:
        """
        Returns True if the item is expanded; otherwise returns False.
        """
        i = self.index_to_item[item]
        if i:
            return i.expanded
        
        return False

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

    def updateLater(self):
        QTimer.singleShot(0, self.slotUpdate)

    def slotEditorDestroyed(self):
        editor = self.sender()
        if not editor:
            return
        
        if not self.widget_to_item.get(editor):
            return

        self.widget_to_item[editor].widget = 0
        self.widget_to_item.remove(editor)

    def slotToggled(self, checked):
        item = self.button_to_item[self.sender()]
        if not item:
            return
        
        self.setExpanded(item, checked)

        if checked:
            self.expandedSignal.emit(self.item_to_index[item])
        else:
            self.collapsedSignal.emit(self.item_to_index[item])

    def slotUpdate(self):
        for item in self.recreate_queue:
            parent = item.parent
            w = 0
            l = 0
            old_row = self.gridRow(item)

            if parent:
                w = parent.container
                l = parent.layout
            else:
                w = self
                l = self.main_layout

            span = 1

            if not item.widget and not item.widget_label:
                span = 2

            item.label = QLabel(w)
            item.label.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
            l.addWidget(item.label, old_row, 0, 1, span)

            self.updateItem(item)

        self.recreate_queue.clear()

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
            row = self.gridRow(after_item) + self.gridSpan(after_item)

            if parent_item:
                parent_item.children.insert(parent_item.children.indexOf(after_item) + 1, new_item)
            else:
                self.children.insert(self.children.indexOf(after_item) + 1, new_item)

        if not parent_item:
            layout = self.main_layout
            parent_widget = self
        else:
            if not parent_item.container:
                self.recreate_queue.removeAll(parent_item)
                grand_parent = parent_item.parent

                l = 0
                old_row = self.gridRow(parent_item)

                if grand_parent:
                    l = grand_parent.layout
                else:
                    l = self.main_layout

                container = QFrame()
                container.setFrameShape(QFrame.Panel)
                container.setFrameShadow(QFrame.Raised)

                parent_item.container = container
                parent_item.button = self.createButton()
                self.button_to_item[parent_item.button] = parent_item
                parent_item.button.toggled.connect(self.slotToggled)
                parent_item.layout = QGridLayout()
                container.setLayout(parent_item.layout)

                if parent_item.label:
                    l.removeWidget(parent_item.label)
                    parent_item.label.close()
                    parent_item.label = 0

                span = 1

                if not parent_item.widget and not parent_item.widget_label:
                    span = 2
                
                l.addWidget(parent_item.button, old_row, 0, 1, span)
                self.updateItem(parent_item)

            layout = parent_item.layout
            parent_widget = parent_item.container

        new_item.label = QLabel(parent_widget)
        new_item.label.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        new_item.widget = self.createEditor(index.property(), parent_widget)
        if new_item.widget:
            new_item.widget.destroyed.connect(self.slotEditorDestroyed)
            self.widget_to_item[new_item.widget] = new_item
        elif index.property().hasValue():
            new_item.widget_label = QLabel(parent_widget)
            new_item.widget_label.setSizePolicy(QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed))
        
        self.insertRow(layout, row)

        span = 1

        if new_item.widget:
            layout.addWidget(new_item.widget, row, 1)
        elif new_item.widget_label:
            layout.addWidget(new_item.widget_label, row, 1)
        else:
            span = 2
        layout.addWidget(new_item.label, row, 0, span, 1)

        self.item_to_index[new_item] = index
        self.index_to_item[index] = new_item

        self.updateItem(new_item)

    def propertyRemoved(self, index):
        item = self.index_to_item[index]

        self.index_to_item.remove(index)
        self.item_to_index.remove(item)

        parent_item = item.parent
        row = self.gridRow(item)

        if parent_item:
            parent_item.children.removeAt(parent_item.children.indexOf(item))
        else:
            self.children.removeAt(self.children.indexOf(item))

        col_span = self.gridSpan(item)

        self.button_to_tiem.remove(item.button)

        if item.widget:
            item.widget.close()
            del item.widget
        
        if item.label:
            item.label.close()
            del item.label

        if item.widget_label:
            item.widget_label.close()
            del item.widget_label

        if item.button:
            item.button.close()
            del item.button

        if item.container:
            item.container.close()
            del item.container

        if not parent_item:
            self.removeRow(self.main_layout, row)
            if col_span > 1:
                self.removeRow(self.main_layout, row)
        elif len(parent_item.children) != 0:
            self.removeRow(parent_item.layout, row)
            if col_span > 1:
                self.removeRow(parent_item.layout, row)
        else:
            grand_parent = parent_item.parent
            l = 0
            if grand_parent:
                l = grand_parent.layout
            else:
                l = self.main_layout

            parent_row = self.gridRow(parent_item)
            parent_span = self.gridSpan(parent_item)

            l.removeWidet(parent_item.button)
            l.removeWidget(parent_item.container)

            parent_item.button.close()
            del parent_item.button

            parent_item.container.close()
            del parent_item.container

            parent_item.button = 0
            parent_item.container = 0
            parent_item.layout = 0

            if not parent_item in self.recreate_queue:
                self.recreate_queue.append(parent_item)

            if parent_span > 1:
                self.removeRow(l, parent_row + 1)

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

        for k in item_to_pos.keys():
            r = item_to_pos[k]
            layout.addItem(k, r.x(), r.y(), r.width(), r.height())

    def removeRow(self, layout, row):
        item_to_pos = QMap()
        idx = 0

        while idx < len(layout):
            r, c, rs, cs = layout.getItemPosition(idx)
            if r > row:
                item_to_pos[layout.takeAt(idx)] = QRect(r-1, c, rs, cs)
            else:
                idx += 1

        for k in item_to_pos.keys():
            r = item_to_pos[k]
            layout.addItem(k, r.x(), r.y(), r.width(), r.height())

    def propertyChanged(self, index):
        item = self.index_to_item[index]
        self.updateItem(item)

    def updateItem(self, item):
        prop = self.item_to_index[item].property()
        if item.button:
            font = item.button.font()
            font.setUnderline(prop.isModified())

            item.button.setFont(font)
            item.button.setText(prop.propertyName())
            item.button.setToolTip(prop.toolTip())
            item.button.setStatusTip(prop.statusTip())
            item.button.setWhatsThis(prop.whatsThis())
            item.button.setEnabled(prop.isEnabled())

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
    

