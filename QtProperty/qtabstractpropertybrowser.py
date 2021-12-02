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
from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QWidget

from libqt5.pyqtcore import QMap, QMapList, QMapMapList, QList
from QtProperty.qtbrowseritem import QtBrowserItem
from QtProperty.qtproperty import QtProperty

g_viewToManagerToFactory = None


def m_viewToManagerToFactory():
    global g_viewToManagerToFactory
    if not g_viewToManagerToFactory:
        g_viewToManagerToFactory = QMapMapList()
    return g_viewToManagerToFactory


g_managerToFactoryToViews = None


def m_managerToFactoryToViews():
    global g_managerToFactoryToViews
    if not g_managerToFactoryToViews:
        g_managerToFactoryToViews = QMapMapList()
    return g_managerToFactoryToViews


#####################################################################################
#
#   class QtAbstractPropertyBrowser
#
#   brief QtAbstractPropertyBrowser provides a base class for implementing property browsers.
#
#   A property browser is a widget that enables the user to edit a given set of properties.
#   Each property is represented by a label specifying the property's name,
#   and an editing widget (e.g. a line edit or a combobox) holding its value.
#   A property can have zero or more subproperties.
#
#   The top level properties can be retrieved using the properties() function.
#   To traverse each property's subproperties, use the QtProperty.subProperties() function.
#   in addition, the set of top level properties can be manipulated using
#   the addProperty(), insertPorperty() and removeProperty() function.
#   Note that the QtProperty class provides a corresponding set of functions
#   making it possible to manipulate the set of subproperties as well.
#
#   To remove all the properties from the property browser widget, use
#   the clear() function. This function will clear the editor, but it
#   will not delete the properties since they can still be used in
#   other editors.
#
#   The properties themselves are created and managed by
#   implementations of the QtAbstractPropertyManager class. A manager
#   can handle (i.e. create and manage) properties of a given type. In
#   the property browser the managers are associated with
#   implementations of the QtAbstractEditorFactory: A factory is a
#   class able to create an editing widget of a specified type.
#
#   When using a property browser widget, managers must be created for
#   each of the required property types before the properties
#   themselves can be created. To ensure that the properties' values
#   will be displayed using suitable editing widgets, the managers
#   must be associated with objects of the preferred factory
#   implementations using the setFactoryForManager() function. The
#   property browser will use these associations to determine which
#   factory it should use to create the preferred editing widget.
#
#   Note that a factory can be associated with many managers, but a
#   manager can only be associated with one single factory within the
#   context of a single property browser.  The associations between
#   managers and factories can at any time be removed using the
#   unsetFactoryForManager() function.
#
#   Whenever the property data changes or a property is inserted or
#   removed, the itemChanged(), itemInserted() or
#   itemRemoved() functions are called, respectively. These
#   functions must be reimplemented in derived classes in order to
#   update the property browser widget. Be aware that some property
#   instances can appear several times in an abstract tree
#   structure.
#
#   = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#   For example:
#
#   property1, property2, property3
#   property2.addSubProperty(property1)
#   property3.addSubProperty(property2)
#
#   editor = QtAbstractPropertyBrowser()
#
#   editor.addProperty(property1)
#   editor.addProperty(property2)
#   editor.addProperty(property3)
#
#   = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#
#   The addProperty() function returns a QtBrowserItem that uniquely
#   identifies the created item.
#
#   To make a property editable in the property browser, the
#   createEditor() function must be called to provide the
#   property with a suitable editing widget.
#
#   Note that there are two ready-made property browser implementations:
#   - QtGroupBoxPropertyBrowser     TODO: Not yet
#   - QtTreePropertyBrowser
#
#####################################################################################
class QtAbstractPropertyBrowser(QWidget):
    # Defines signal
    currentItemChangedSignal = Signal(QtBrowserItem)

    def __init__(self, parent=None) -> None:
        """
        Creates an abstract property browser with the given parent.
        """
        super(QtAbstractPropertyBrowser, self).__init__(parent)

        self.m_subItems = QList()
        self.m_managerToProperties = QMapList()
        self.m_propertyToParents = QMapList()
        self.m_topLevelPropertyToIndex = QMap()
        self.m_topLevelIndexes = QList()
        self.m_propertyToIndexes = QMapList()
        self.m_currentItem = None

    """
    The properties that were displayed in
    the editor are not deleted since they still can be used in other editors.
    Neither does the destructor delete the property managers and editor
    factories that were used by this property browser widget unless
    this widget was their parent.
    """
    def __del__(self) -> None:
        """
        Destroys the property browser, and destroys all the items
        that were created by this property browser.
        """
        indexes = self.topLevelItems()
        for itItem in indexes:
            self.clearIndex(itItem)

    def insertSubTree(self, prop, parentProperty):
        if self.m_propertyToParents.get(prop):
            # property was already inserted, so its manager is connected
            # and all its children are inserted and theirs managers are connected
            # we just register new parent (parent has to be new).
            self.m_propertyToParents[prop].append(parentProperty)
            # don't need to update d__ptr.m_managerToProperties map since
            # d__ptr.m_managerToProperties[manager] already contains property.
            return

        manager = prop.propertyManager()
        if not self.m_managerToProperties[manager]:
            # connect manager's signals
            manager.propertyInsertedSignal.connect(self.slotPropertyInserted)
            manager.propertyRemovedSignal.connect(self.slotPropertyRemoved)
            manager.propertyDestroyedSignal.connect(self.slotPropertyDestroyed)
            manager.propertyChangedSignal.connect(self.slotPropertyChanged)

        self.m_managerToProperties[manager].append(prop)
        self.m_propertyToParents[prop].append(parentProperty)

        for subProperty in prop.subProperties():
            self.insertSubTree(subProperty, prop)

    def removeSubTree(self, prop, parentProperty):
        if not self.m_propertyToParents.get(prop):
            # ASSERT
            return

        self.m_propertyToParents[prop].removeAll(parentProperty)
        if len(self.m_propertyToParents[prop]) > 0:
            return

        self.m_propertyToParents.remove(prop)
        manager = prop.propertyManager()
        self.m_managerToProperties[manager].removeAll(prop)
        if not self.m_managerToProperties[manager]:
            # disconnect manager's signals
            manager.propertyInsertedSignal.disconnect(self.slotPropertyInserted)
            manager.propertyRemovedSignal.disconnect(self.slotPropertyRemoved)
            manager.propertyDestroyedSignal.disconnect(self.slotPropertyDestroyed)
            manager.propertyChangedSignal.disconnect(self.slotPropertyChanged)
            self.m_managerToProperties.remove(manager)

        for subProperty in prop.subProperties():
            self.removeSubTree(subProperty, prop)

    def createBrowserIndexes(self, prop, parentProperty, afterProperty):
        parentToAfter = QMap()
        if afterProperty:
            indexes = self.m_propertyToIndexes.get(afterProperty)
            if not indexes:
                return

            for idx in indexes:
                parentIdx = idx.parent()
                if ((parentProperty and parentIdx and parentIdx.property() == parentProperty) or (
                        not parentProperty and not parentIdx)):
                    parentToAfter[idx.parent()] = idx
        elif parentProperty:
            indexes = self.m_propertyToIndexes.get(parentProperty)
            if not indexes:
                return

            for idx in indexes:
                parentToAfter[idx] = 0
        else:
            parentToAfter[0] = 0

        for it in parentToAfter.keys():
            self.createBrowserIndex(prop, it, parentToAfter[it])

    def createBrowserIndex(self, prop, parentIndex, afterIndex):
        newIndex = QtBrowserItem(self, prop, parentIndex)
        if parentIndex:
            parentIndex.addChild(newIndex, afterIndex)
            # parentIndex.d__ptr.addChild(newIndex, afterIndex)
        else:
            self.m_topLevelPropertyToIndex[prop] = newIndex
            self.m_topLevelIndexes.insert(self.m_topLevelIndexes.indexOf(afterIndex) + 1, newIndex)

        if not self.m_propertyToIndexes.get(prop):
            self.m_propertyToIndexes[prop] = QList()

        self.m_propertyToIndexes[prop].append(newIndex)
        self.itemInserted(newIndex, afterIndex)
        subItems = prop.subProperties()
        afterChild = 0
        for child in subItems:
            afterChild = self.createBrowserIndex(child, newIndex, afterChild)

        return newIndex

    def removeBrowserIndexes(self, prop, parentProperty):
        toRemove = QList()
        if not prop in self.m_propertyToIndexes.keys():
            return

        indexes = self.m_propertyToIndexes[prop]
        for idx in indexes:
            parentIdx = idx.parent()
            if ((parentProperty and parentIdx and parentIdx.property() == parentProperty) or (
                    not parentProperty and not parentIdx)):
                toRemove.append(idx)

        for index in toRemove:
            self.removeBrowserIndex(index)

    def removeBrowserIndex(self, index):
        children = index.children()
        for i in range(len(children) - 1, -1, -1):
            self.removeBrowserIndex(children[i])

        self.itemRemoved(index)
        if index.parent():
            index.parent().removeChild(index)
            # index.parent().d__ptr.removeChild(index)
        else:
            self.m_topLevelPropertyToIndex.remove(index.property())
            self.m_topLevelIndexes.removeAll(index)

        prop = index.property()
        self.m_propertyToIndexes[prop].removeAll(index)
        if len(self.m_propertyToIndexes[prop]) <= 0:
            self.m_propertyToIndexes.remove(prop)
        del index

    def clearIndex(self, index):
        children = index.children()
        for c in children:
            self.clearIndex(c)

        del index

    def properties(self) -> QList:
        """
        Returns the property browser's list of top level properties.
        To traverse the subproperties, use the QtProperty.subProperties() function.
        """
        return self.m_subItems

    def items(self, prop) -> QList:
        """
        Returns the property browser's list of all items associated with the given property.
        There is one itme per instance of the property in the browser.
        """
        return self.m_propertyToIndexes[prop]

    def topLevelItem(self, prop) -> QMap:
        """
        Returns the top lovel items associated with the given property.

        Returns the None if property wasn't inserted into this property browser
        or isn't a top level one.
        """
        return self.m_topLevelPropertyToIndex[prop]

    def topLevelItems(self) -> QList:
        """
        Returns list of top level items.
        """
        return self.m_topLevelIndexes

    def clear(self) -> None:
        """
        Removes all the properties from the editor, but does not delete them
        since they can still be used in other editors.
        """
        subList = self.properties()
        for x in range(len(subList) - 1, -1, -1):
            self.removeProperty(subList[-1])

    """
    Returns the item created by property browser which is associated with the property.
    In order to get all children items created by the property browser in this call,
    the returned item should be traversed.
    
    If the specified property is already added, this function does nothing and returns None.
    """
    def addProperty(self, prop) -> QtBrowserItem:
        """
        Appends the given property (and its subproperties)
        to the property browser's list of top level properties.
        """
        afterProperty = 0
        if len(self.m_subItems) > 0:
            afterProperty = self.m_subItems[-1]
        return self.insertProperty(prop, afterProperty)

    """
    Returns item created by property browser which
    is associated with the property. In order to get all children items
    created by the property browser in this call returned item should be traversed.

    If the specified afterProperty is None, the given property is inserted at
    the beginning of the list. If property is already inserted,
    this function does nothing and returns None
    """
    def insertProperty(self, prop, afterProperty) -> QtBrowserItem:
        """
        Inserts the given property (and its subproperties) after
        the specified afterProperty in the browser's list of top level properties.
        """
        if not prop:
            return 0

        # if item is already inserted in this item then cannot add.
        pendingList = self.properties()
        pos = 0
        newPos = 0
        while pos < len(pendingList):
            p = pendingList[pos]
            if p == prop:
                return 0
            if p == afterProperty:
                newPos = pos + 1

            pos += 1

        self.createBrowserIndexes(prop, 0, afterProperty)

        # traverse inserted subtree and connect to manager's signals
        self.insertSubTree(prop, 0)

        self.m_subItems.insert(newPos, prop)

        return self.topLevelItem(prop)

    """
    Note that the properties are not deleted since they can still be used in other editors.
    """
    def removeProperty(self, prop) -> None:
        """
        Removes the specified property (and its subproperties) from
        the property browser's list of top level properties. All items
        that were associated with the given property and its chilredn are deleted.
        """
        if not prop:
            return

        pendingList = self.properties()
        pos = 0
        while pos < len(pendingList):
            if pendingList[pos] == prop:
                self.m_subItems.removeAt(pos)   # perhaps this two lines
                self.removeSubTree(prop, 0)     # should be moved down after propertyRemoved call.

                self.removeBrowserIndexes(prop, 0)

                # when item is deleted, item will call removeItem for top level items,
                # and itemRemoved for nested items.

                return

            pos += 1

    """
    If the property is created by a property manager which was not
    associated with any of the existing factories in this property editor,
    the function returns None
    
    To make a property editable in the property browser,
    the createEditor() function must be called to provide the property
    with a suitable editing widget.
    
    Reimplement this function to provide additional decoration for
    the editing widgets created by the installed factories.
    """
    def createEditor(self, prop, parent):
        """
        Creates an editing widget (with the given parent) for the given
        property according to the previously established associations
        between property managers and editor factories.
        """
        factory = 0
        manager = prop.propertyManager()

        pb = m_viewToManagerToFactory().get(self)
        if pb:
            factory = pb.get(manager)

        if not factory:
            return 0

        return factory.findEditor(prop, parent)

    def addFactory(self, abstractManager, abstractFactory) -> bool:
        connectNeeded = False
        if (not abstractManager in m_managerToFactoryToViews().keys()) or (
        not abstractFactory in m_managerToFactoryToViews()[abstractManager]):
            connectNeeded = True
        elif self in m_managerToFactoryToViews()[abstractManager][abstractFactory]:
            return connectNeeded

        if (self in m_viewToManagerToFactory().keys()) and (abstractManager in m_viewToManagerToFactory()[self]):
            self.unsetFactoryForManager(abstractManager)

        m_managerToFactoryToViews()[abstractManager][abstractFactory].append(self)
        m_viewToManagerToFactory()[self][abstractManager] = abstractFactory

        return connectNeeded

    def unsetFactoryForManager(self, manager) -> None:
        """
        Removes the association between the given manager and the factory bound to it,
        automatically calling the QtAbstractEditorFactory.removePropertyManager() function if necessary.
        """
        if (not self in m_viewToManagerToFactory().keys()) or (not manager in m_viewToManagerToFactory()[self]):
            return

        abstractFactory = m_viewToManagerToFactory()[self][manager]
        m_viewToManagerToFactory()[self].pop(manager)
        if not m_viewToManagerToFactory()[self]:
            m_viewToManagerToFactory().remove(self)

        m_managerToFactoryToViews()[manager][abstractFactory][self].clear()
        if len(m_managerToFactoryToViews()[manager][abstractFactory]) <= 0:
            m_managerToFactoryToViews().remove(manager)[abstractFactory]
            abstractFactory.breakConnection(manager)
            if not m_managerToFactoryToViews()[manager]:
                m_managerToFactoryToViews().remove(manager)

    def setCurrentItem(self, item):
        """
        Sets the current item in the property browser to item.
        """
        oldItem = self.m_currentItem
        self.m_currentItem = item
        if oldItem != item:
            if item == 0 or item is None:
                item = QtBrowserItem()
            self.currentItemChangedSignal.emit(item)

    """
    For example:
    intManager = QtIntManager()
    doubleManager = QtDoubleManager()
    
    myInteger = intManager.addProperty()
    myDouble = doubleManager.addProperty()
    
    spinBoxFactory = QtSpinBoxFactory()
    doubleSpinBoxFactory = QtDoubleSpinBoxFactory()
    
    editor = QtAbstractPropertyBrowser()
    editor.setFactoryForManager(iniManager, spinBoxFactory)
    editor.setFactoryForManager(doubleManager, doubleSpinBoxFactory)
    
    editor.addProperty(myInteger)
    editor.addProperty(myDouble)
    = = = = = = = = = = = = = = = = = = 
    
    In this example the myInteger property's value is displayed
    with a QSpinBox widget, while the myDouble property's value is
    displayed with a QDoubleSpinBox widget.
    
    Note that a factory can be associated with many managers, but a
    manager can only be associated with one single factory. If the
    given manager already is associated with another factory, the
    old association is broken before the new one established.
    
    This function ensures that the given manager and the given
    factory are compatible, and it automatically calls the
    QtAbstractEditorFactory.addPropertyManager() function if necessary.
    """
    def setFactoryForManager(self, manager, factory):
        """
        Connects the given manager to the given factory, ensuring that
        properties of the manager's type will be displayed with an editing
        widget suitable for their value.
        """
        if self.addFactory(manager, factory):
            factory.addPropertyManager(manager)

    @Slot(QtProperty, QtProperty, list)
    def slotPropertyInserted(self, prop, parentProperty, afterProperty):
        if not self.m_propertyToParents.get(parentProperty):
            return
        if type(afterProperty) == list:
            afterProperty = afterProperty[0]
        self.createBrowserIndexes(prop, parentProperty, afterProperty)
        self.insertSubTree(prop, parentProperty)

    @Slot(QtProperty, QtProperty)
    def slotPropertyRemoved(self, prop, parentProperty):
        if not self.m_propertyToParents.get(parentProperty):
            return
        self.removeSubTree(prop, parentProperty)  # this line should be probably moved down after propertyRemoved call
        self.removeBrowserIndexes(prop, parentProperty)

    @Slot(QtProperty)
    def slotPropertyDestroyed(self, prop):
        if not prop in self.m_subItems:
            return
        self.removeProperty(prop)

    @Slot(QtProperty)
    def slotPropertyChanged(self, prop):
        if not prop in self.m_propertyToIndexes.keys():
            return

        indexes = self.m_propertyToIndexes[prop]
        for idx in indexes:
            self.itemChanged(idx)

    """
    This function is called to update the widget whenever a property
    is inserted or added to the property browser, passing the insertedItem 
    of property and the specified precedingItem as parameters.
    
    If precedingItem is None, the insertedItem was put at the beginning of its
    parent item's list of subproperties. If the parent of insrtedItem is None,
    the insertedItem was added as a top level property of this property browser.
    
    This function must be reimplemented in derived classes.
    Note that if the insertedItem's property has subproperties, this method will be
    called for those properties as soon as the current call is finished.
    """
    @abstractmethod
    def itemInserted(self, insertedItem, precedingItem) -> None:
        """
        Abstract method. See the QtTreePropertyBrowser class.

        :param insertedItem: Item to be added.
        :param precedingItem: Parent item.
        """
        pass

    """
    This function is called to update the widget whenever a property is removed
    from the property browser, passing the item of the property as parameters.
    The passed item is deleted just after this call is finished.
    
    If the parent of item is None, the removed item was a top level property
    in this editor.
    
    This function must be reimplemented in derived classes.
    Note that if the isnertedItem's property has subproperties, this method will be
    called for those properties as soon as the current call is started.
    """
    @abstractmethod
    def itemRemoved(self, item) -> None:
        """
        Abstract method. See the QtTreePropertyBrowser class.

        :param item: Item to be removed.
        """
        pass

    """
    This function is called whenever a property's data changes, passing the item of
    property as parameters.
    
    This function must be reimplemented in derived classes, in order to update the
    property browser widget whenever a property's name, tool tip, status tip,
    "what's this" text, value text or value icon changes.
    
    Note that if the property browser contains several occurrences of the same property,
    this method will be called once for each occurrence (with a different item each item.)
    """
    @abstractmethod
    def itemChanged(self, item) -> None:
        """
        Abstract method. See the QtTreePropertyBrowser class.

        :param item: Item containing changes.
        """
