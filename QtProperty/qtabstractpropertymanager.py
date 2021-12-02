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

from abc import *
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLineEdit
from QtProperty.qtproperty import QtProperty


#####################################################################################
#
#   class QtAbstractPropertyManager
#
#   brief The QtAbstractPropertyManager provides an interface for property managers.
#
#   A manager can create and manage properties of a given type, and is used
#   in conjunction with the QtAbstractPropertyBrowser class.
#
#   When using a property browser widget, the properties are created and managed
#   by implementations of the QtAbstractPropertyManager class. To ensure that
#   the properties' values will be displayted using suitable editing widgets,
#   the managers are associated with objects of QtAbstractEditorFactory subclasses.
#   The property browser will use these associations to determine which factories
#   it should use to creat the preferred editing widgets.
#
#   The QtAbstractPropertyManager class provides common functionality
#   like creating a property using the addProperty() function, and
#   retriving the properties created by the manager using the
#   properties() function. The clas salso provides signals that
#   are emitted when the manager's properties change;
#   - propertyDestroyed()
#   - propertyChanged()
#   - propertyRemoved()
#   - propertyInserted()
#
#   QtAbstractPropertyManager subclasses are supposed to provide their
#   own type specific API.
#   Note that several ready-made implementations are available:
#   - QtBoolPropertyManager
#   - QtColorPropertyManager
#   - QtDatePropertyManager
#   - QtDateTimePropertyManager
#   - QtDoublePropertyManager
#   - QtEnumPropertyManager
#   - QtFlagPropertyManager
#   - QtFontPropertyManager         TODO 10
#   - QtGroupPropertyManager
#   - QtIntPropertyManager
#   - QtPointPropertyManager
#   - QtRectPropertyManager
#   - QtSizePropertyManager
#   - QtSizePolicyPropertyManager
#   - QtStringPropertyManager
#   - QtTimePropertyManager
#
#   = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#   QtAbstractPropertyManager signal description:
#
#   propertyInsertedSignal(newProperty, parentProperty, precedingProperty)
#   This signal is emitted when a new subproperty is inserted into an
#   existing property, passing the newProperty, parentProperty and precedingProperty as parameters.
#
#   If precedingProperty is None, the newProperty was inserted at the beginning of
#   the parentProperty's subproperties list.
#
#   Note that signal is emitted only if the parentProperty is created by this manager.
#
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   propertyChangedSignal(property)
#   This signal is emitted whenever a property's data changes, passing to the property as parameter.
#
#   Note that signal is only emitted for properties that are created by this manager.
#
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   propertyRemovedSignal(property, parentProperty)
#   This signal is emitted when a subproperty is removed, passing to the removed property
#   and the parentProperty as parameters.
#
#   Note that signal is only emitted for properties that are created by this manager.
#
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   propertyDestroyedSignal(property)
#   This signal is emitted when the specified property is about to be destroyed.
#
#   Note that signal is only emitted for properties that are created by this manager.
#
#####################################################################################
class QtAbstractPropertyManager(QObject):
    propertyInsertedSignal = Signal(QtProperty, QtProperty, list)
    propertyChangedSignal = Signal(QtProperty)
    propertyRemovedSignal = Signal(QtProperty, QtProperty)
    propertyDestroyedSignal = Signal(QtProperty)

    def __init__(self, parent=None) -> None:
        """
        Creates an abstract property manager with the given parent.
        """
        super(QtAbstractPropertyManager, self).__init__(parent)
        self.m_properties = set()

    def __del__(self) -> None:
        """
        Destroys the manager. All properties created by the manager are destroyed.
        """
        self.clear()

    def clear(self) -> None:
        """
        Destroys all the properties that this manager has created.
        """
        properties = list(self.properties())
        for i in range(len(properties)):
            prop = properties[i]
            prop.destroy()

    def properties(self) -> set:
        """
        Returns the set of properties created by this manager.
        """
        return self.m_properties

    def hasValue(self, prop) -> bool:
        """
        Returns whether the given property has a value.
        The default implementation of this function returns True.
        """
        return True

    def valueIcon(self, prop) -> QIcon:
        """
        Returns an icon representing the current state of the given property.
        The default implementation of this function returns an invalid icon.
        """
        return QIcon()

    def valueText(self, prop) -> str:
        """
        Returns a string representing the current state of the given property.
        The default implementation of this function returns an empty string.

        This function is implemented at inherited subclasses.
        """
        return ""

    def displayText(self, prop) -> str:
        """
        Returns a string representing the current state of the given property.
        The default implementation of this function returns an empty string.

        This function is implemented at inherited subclasses.
        """
        return ""

    def echoMode(self, prop):
        """
        Returns the echo mode representing the current state of the given property.
        The default implementing of this function returns QLineEdit.Normal.
        """
        return QLineEdit.Normal

    def addProperty(self, name="") -> QtProperty:
        """
        Creates a property with the given name which then is owned by this manager.
        Internally, this function calls the createProperty() and initializeProperty() functions.
        """
        prop = self.createProperty()
        if prop:
            prop.setPropertyName(name)
            self.m_properties.add(prop)
            self.initializeProperty(prop)

        return prop

    def createProperty(self) -> QtProperty:
        """
        Creates a property.
        The base implementation produces QtProperty instances reimplement
        this function to make this manager produces objects of a QtProperty subclass.
        """
        return QtProperty(self)

    @abstractmethod
    def initializeProperty(self, prop):
        pass

    @abstractmethod
    def uninitializeProperty(self, prop):
        pass

    def propertyDestroyed(self, prop):
        if prop in self.m_properties:
            self.propertyDestroyedSignal.emit(prop)
            self.uninitializeProperty(prop)
            self.m_properties.remove(prop)

    def propertyChanged(self, prop):
        self.propertyChangedSignal.emit(prop)

    def propertyRemoved(self, prop, parentProperty):
        self.propertyRemovedSignal.emit(prop, parentProperty)

    def propertyInserted(self, prop, parentProperty, afterProperty=None):
        self.propertyInsertedSignal.emit(prop, parentProperty, [afterProperty])
