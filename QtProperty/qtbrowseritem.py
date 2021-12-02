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

from libqt5.pyqtcore import QList


#####################################################################################
#
#   class QtBrowserItem
#
#   brief The QtBrowserItem class represents a property in a property browser instance.
#
#   Browser items are created whenever a QtProperty is inserted to the property browser.
#   A QtBrowserItem uniquely identifies a browser's item. Thus, if the same QtProperty
#   is inserted multiple times, each occurrence gets its own unique QtBrowserItem.
#   The items are owned by QtAbstractPropertyBrowser and automatically deleted
#   when they are removed from the browser.
#
#   You can traverse a browser's properties by calling parent() and children().
#   The property and the browser associated with an item are available
#   as property() and browser()
#
#####################################################################################
class QtBrowserItem:
    def __init__(self, browser=None, prop=None, parent=None):
        self.m_browser = browser
        self.m_property = prop
        self.m_parent = parent
        self.m_children = QList()

    def __del__(self):
        pass

    def property(self):
        """
        Returns the property which is accossiated with this item.
        Note that several items can be associated with the same property instance
        in the same property browser.
        """
        return self.m_property

    def parent(self):
        """
        Returns the parent item this item.
        Returns None if this item is associated with top-level property
        in item's property browser.
        """
        return self.m_parent

    """
    The properties reproduced from children items are always the same as
    reproduced from associated property's children.
    
    for example:
    - childrenItems = item.children()
    - childrenProperties = item.property().subProperties()
    
    The childrenItems list represents the same list as childProperties.
    """
    def children(self):
        """
        Returns the children items of this item.
        """
        return self.m_children

    def browser(self):
        """
        Returns the property browser which owns this item.
        """
        return self.m_browser

    def addChild(self, index, after):
        if index in self.m_children:
            return
        idx = self.m_children.indexOf(after) + 1    # we insert after returned idx, if it was -1 then we set idx to 0
        self.m_children.insert(idx, index)

    def removeChild(self, index):
        self.m_children.removeAll(index)
