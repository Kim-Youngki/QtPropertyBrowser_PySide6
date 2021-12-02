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
from PySide6.QtCore import QObject


#####################################################################################
#
#   class QtAbstractEditorFactory
#
#   brief The QtAbstractEditorFactory is the base template class for editor factories.
#
#   An editor factory is a class that is able to create an editing widget of
#   specified type (e.g. line edits or comboboxes) for a given QtProperty object,
#   and it is used in conjuction with the QtAbstractPropertyManager and
#   QtAbstractPropertyBrowser classes.
#
#   Note that the QtAbstractEditorFactory functions are using the PropertyManager
#   template argument class which can be any QtAbstractPropertyManager subclass.
#
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   For example:
#   factory = QtSpinBoxFactory()
#   managers = factory.propertyManagers()
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
#   Note that QtSpinBoxFactory by definition creates editing widgets only for
#   properties created by QtIntPropertyManager.
#
#   When using a property browser widget, the properties are created and managed
#   by implementations of the QtAbstractPropertyManager class. To ensure that
#   the properties' values will be displayed  using suitable editing widgets,
#   the managers are associated with objects of QtAbstractEditorFactory subclasses.
#   The property browser will use these associations to determine which factories
#   it should use to create the preferred editing widgets.
#
#   A QtAbstractEditorFactory object is capable of producing editors for several
#   property managers at the same time. To create an association between this factory
#   and a given manager, use the addPropertyManager() function.
#   Use the removePropertyManager() function to make this factory stop producing editors
#   for a given property manager. Use the propertyManagers() function to retrieve
#   the set of managers currently associated with this factory.
#
#   Several ready-made implementations of the QtAbstractEditorFactory class are available:
#
#   Ready-made factories:
#   - QtCheckBoxFactory
#   - QtDateEditFactory
#   - QtDateTimeEidtFactory
#   - QtDoubleSpinBoxFactory
#   - QtEnumEditorFactory
#   - QtLineEditFactory
#   - QtScrollBarFactory
#   - QtSliderFactory
#   - QtSpinBoxFactory
#   - QtTimeEditFactory
#   - QtQvariantEditorFactory       # TODO
#
#   When deriving from the QtAbstractEditorFactory class, several pure abstract method
#   must be implemented;
#   - connectPropertyManager()
#   : is used by the factory to connect to the given manager's signals.
#   - createEditor()
#   : is supposed to create an editor for the given property controlled by the given manager.
#   - disconnectPropertyManager()
#   : is used by the factory to disconnect from the specified manager's signals.
#
#####################################################################################
class QtAbstractEditorFactory(QObject):
    def __init__(self, parent=None) -> None:
        """
        Creates an editor factory with the given parent.
        """
        super(QtAbstractEditorFactory, self).__init__(parent)
        self.m_managers = set()

    def findEditor(self, prop, parent):
        for manager in self.m_managers:
            if manager == prop.propertyManager():
                return self.createEditor(manager, prop, parent)

        return 0

    def addPropertyManager(self, manager) -> None:
        """
        Adds the given manager to this factory's set of managers,
        making this factory produce editing widgets for properties
        created by the given manager.
        """
        if manager in self.m_managers:
            return

        self.m_managers.add(manager)
        self.connectPropertyManager(manager)
        manager.destroyed.connect(self.managerDestroyed)

    def removePropertyManager(self, manager) -> None:
        """
        Removes the given manager form this factory's set of managers.
        The PropertyManager type is a template argument class, and
        may be any QtAbstractPropertyManager subclass.
        """
        if not manager in self.m_managers:
            return

        manager.destroyed.disconnect(self.managerDestroyed)
        self.disconnectPropertyManager(manager)
        self.m_managers.remove(manager)

    def propertyManagers(self) -> set:
        """
        Returns the factory's set of associated managers.
        The PropertyManager type is a template argument class,
        and represents the chosen QtAbstractpropertyManager subclass.
        """
        return self.m_managers

    def propertyManager(self, prop):
        """
        Returns the property manager for the given property, or
        None if the given property doesn't belong to any of this
        factory's registred managers.

        The PropertyManager type is a template argument class,
        and represents the chosen QtAbstractpropertyManager subclass.
        """
        manager = prop.propertyManager()

        for mgr in self.m_managers:
            if mgr == manager:
                return mgr

        return 0

    def managerDestroyed(self, manager) -> None:
        for mgr in self.m_managers:
            if mgr == manager:
                self.m_managers.remove(mgr)
                return

    def breakConnection(self, manager) -> None:
        for mgr in self.m_managers:
            if mgr == manager:
                self.removePropertyManager(mgr)
                return

    """
    Creates an editing widget (with the given parent) for the given property.
    """
    @abstractmethod
    def createEditor(self, manager, prop, parent):
        """
        Abstract method. See the each factory class.
        """
        pass

    """
    Connects this factory to the given manager's signals. The PropertyManager type is
    a template argument class, and represents the chosen QtAbstractPropertyManager subclass.
    
    This function is used internally by the addPropertyManager() function, and makes it
    possible to update an editing widget when the associated property's data changes.
    This is typically done in custom slots responding to the signals emitted by
    the property's manager,
    e.g. QtIntPropertyManager.valueChanged() and QtIntPropertyManager.rangeChanged().
    """
    @abstractmethod
    def connectPropertyManager(self, manager):
        """
        Abstract method. See the each factory class.
        """
        pass

    """
    Disconnects this factory from the given manager's signals. The PropertyManager type is
    a template argument class, and represents the chosen QtAbstractPropertyManager subclass.
    
    This function is used internally by the removePropertyManager() function.
    """
    @abstractmethod
    def disconnectPropertyManager(self, manager):
        """
        Abstract method. See the each factory class.
        """
        pass
