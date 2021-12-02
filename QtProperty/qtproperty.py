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

import copy
from libqt5.pyqtcore import QList, QMap
from PySide6.QtGui import QColor, QIcon


######################################################################
#
#   class QtProperty
#
#   brief The QtProperty class encapsulates an instance of a property.
#
#   Properties are created by objects of QtAbstractPropertyManager
#   subclasses a manager can create properties of a given type, and
#   is used in conjunction with the QtAbstractPropertyBrowser class.
#   A property is always owned by the manager that creted it, which can
#   be retrieved using the propertyManager() function.
#
#   QtProperty contains the most common property attributes, and
#   provides functions for retrieving as well as setting their values:
#
#   ┌ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐
#   │       Getter              Setter          │
#   ├ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │
#   │   propertyName()      setPropertyName()   │
#   │   statusTip()         setStatusTip()      │
#   │   toopTip()           settoopTip()        │
#   │   whatsThis()         setwhatsThis()      │
#   │   isEnabled()         setEnabled()        │
#   │   isModified()        setModified()       │
#   │   valueText()              -              │
#   │   valueIcon()              -              │
#   └ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┘
#
#   It is also possible to nest properties: QtProperty provides the
#   adSubProperty(), insrtSubProperty() and removeSubProperty() functions
#   to manipulate the set of subproperties. Use the subProperties() function
#   to retrieve a property's current set of subproperties.
#   Note that nested properties are not owned by the parent property,
#   i.e. each subproperty is owned by the manager that created it.
#
######################################################################
class QtProperty:
    def __init__(self, manager=None) -> None:
        """
        Creates a property with the given manager.

        This constructor is only usefule when creating a custom QtProperty
        subclass (e.g. QtVariantProperty). To create a regular QtProperty object,
        use the QtAbstractPropertyManager.addProperty() function instead.
        """
        self.m_enabled = True
        self.m_modified = False
        self.m_manager = manager

        self.m_parentItems = set()
        self.m_subItems = QList()
        self.m_toolTip = ''
        self.m_statusTip = ''
        self.m_whatsThis = ''
        self.m_name = ''
        self.m_nameColor = QColor()
        self.m_valueColor = QColor()

    def __del__(self) -> None:
        """
        Destroys this property.
        Note that subproperties are detached but not destroyed,
        i.e. they can still be used in another context.
        """
        self.destroy()

    def destroy(self) -> None:
        """
        As python cna't force free memory after use del, so we have to destory it manull.
        """
        for prop in self.m_parentItems:
            prop.m_manager.propertyRemoved(self, prop)

        if self.m_manager and self.m_manager != -1:
            self.m_manager.propertyDestroyed(self)

        for prop in self.m_subItems:
            parentItems = prop.m_parentItems
            if parentItems.__contains__(self):
                parentItems.remove(self)

        for prop in self.m_parentItems:
            prop.m_subItems.removeAll(self)

    def subProperties(self) -> QList:
        """
        Returns the set of subproperties.
        Note that subproperties are not owned by this property,
        but by the manager that created them.
        """
        return self.m_subItems

    def propertyManager(self):
        """
        Returns the manager that owns this property.
        """
        return self.m_manager

    def toolTip(self) -> str:
        """
        Returns the property's tool tip.
        """
        return self.m_toolTip

    def statusTip(self) -> str:
        """
        Returns the property's status tip.
        """
        return self.m_statusTip

    def whatsThis(self) -> str:
        """
        Returns the property's "What's this" help text.
        """
        return self.m_whatsThis

    def propertyName(self) -> str:
        """
        Returns the propert's name.
        """
        return self.m_name

    def isEnabled(self) -> bool:
        """
        Returns whether the property is enabled.
        """
        return self.m_enabled

    def isModified(self) -> bool:
        """
        Returns whether the property is modified.
        """
        return self.m_modified

    def hasValue(self) -> bool:
        """
        Returns whether the property has a value

        see also: QtAbstractPropertyManager.hasValue()
        """
        return self.m_manager.hasValue(self)

    def valueIcon(self) -> QIcon:
        """
        Returns an icon representing the current state of this property.

        If the given property type can not generate such an icon,
        this function returns an invalid cicon.

        see also: QtAbstractPropertyManager.valueIcon()
        """
        ico = self.m_manager.valueIcon(self)
        if not ico:
            return QIcon()
        return ico

    def valueText(self) -> str:
        """
        Returns a string representing the current state of this property.

        If the given property type can not generate such a string,
        this function returns an empty string.

        see also: QtAbstractPropertyManager.valueText()
        """
        return self.m_manager.valueText(self)

    def displayText(self) -> str:
        """
        Returns the display text according to the echo-mode set on the editor.
        When the editor is a QLineEdit, this will return a string equal to what
        is displayed.

        see also: QtAbstractPropertyManager.valueText()
        """
        return self.m_manager.displayText(self)

    def setToolTip(self, text) -> None:
        """
        Sets the proeprty's tool tip to the given text.
        """
        if self.m_toolTip == text:
            return

        self.m_toolTip = text
        self.propertyChanged()

    def setStatusTip(self, text) -> None:
        """
        Sets the property's status tip to the given text.
        """
        if self.m_statusTip == text:
            return

        self.m_statusTip = text
        self.propertyChanged()

    def setWhatsThis(self, text) -> None:
        """
        Sets the property's "What's This" help text to the given text.
        """
        if self.m_whatsThis == text:
            return

        self.m_whatsThis = text
        self.propertyChanged()

    def setPropertyName(self, text) -> None:
        """
        Sets the property's name to the given name.
        """
        if self.m_name == text:
            return

        self.m_name = text
        self.propertyChanged()

    def setNameColor(self, color) -> None:
        """
        Sets the property's name color to the givne color.
        """
        if self.m_nameColor == color:
            return

        self.m_nameColor = color
        self.propertyChanged()

    def setValueColor(self, color) -> None:
        """
        Sets the property's value color to the given color.
        """
        if self.m_valueColor == color:
            return

        self.m_valueColor = color
        self.propertyChanged()

    def setEnabled(self, enable) -> None:
        """
        Enables or disables the property according to the passed enable value.
        """
        if self.m_enabled == enable:
            return

        self.m_enabled = enable
        self.propertyChanged()

    def setModified(self, modified) -> None:
        """
        Sets the property's modified state according to the passed modifed value.
        """
        if self.m_modified == modified:
            return

        self.m_modified = modified
        self.propertyChanged()

    def addSubProperty(self, prop) -> None:
        """
        Appends the given property to this property's subproperties.
        If the given property already is added, this function does nothing.
        """
        after = None
        if len(self.m_subItems) > 0:
            after = self.m_subItems[-1]
        self.insertSubProperty(prop, after)

    def insertSubProperty(self, prop, afterProperty) -> None:
        """
        inserts the given property after the specified precedingProperty
        into this property's list of subproperties.

        If precedingProperty is 0, the specified property is inserted at the beginning o the list.

        If the given property already is inserted, this function does nothing.
        """
        if not prop:
            return

        if prop == self:
            return

        # traverse all children of item. if this item is a child of item then cannot add.
        pendingList = copy.copy(prop.subProperties())
        visited = QMap()
        while len(pendingList) > 0:
            i = pendingList[0]
            if i == self:
                return
            pendingList.removeFirst()
            if visited.get(i):
                continue
            visited[i] = True
            pendingList += i.subProperties()

        pendingList = self.subProperties()
        pos = 0
        newPos = 0
        properAfterProperty = None
        while pos < len(pendingList):
            i = pendingList[pos]
            if i == prop:
                return  # if item is already inserted in this item then cannot add.
            if i == afterProperty:
                newPos = pos + 1
                properAfterProperty = afterProperty

            pos += 1

        self.m_subItems.insert(newPos, prop)
        prop.m_parentItems.add(self)

        self.m_manager.propertyInserted(prop, self, properAfterProperty)

    def removeSubProperty(self, prop) -> None:
        """
        Removes the given property from the list of subproperties without deleting it.
        """
        if not prop:
            return

        self.m_manager.propertyRemoved(prop, self)

        pendingList = self.subProperties()
        pos = 0
        while pos < len(pendingList):
            if pendingList[pos] == prop:
                self.m_subItems.removeAt(pos)
                prop.m_parentItems.remove(self)
                return

            pos += 1

    def propertyChanged(self) -> None:
        """
        Internal function.
        """
        self.m_manager.propertyChanged(self)

    def propertyDestroyed(self, prop) -> None:
        if prop in prop.m_manager.m_properties:
            prop.m_manager.propertyDestroyedSignal.emit(prop)
            prop.m_manager.uninitializeProperty(prop)
            prop.m_manager.m_properties.remove(prop)
            # self.propertyDestroyedSignal.emit(prop)
            # self.uninitializeProperty(prop)
            # self.m_properties.remove(prop)
