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
###########################################################################


import copy
from PySide6.QtCore import (
    QCoreApplication,
    Qt,
    Signal,
    QSize, QSizeF,
    QLocale,
    QRect, QRectF,
    QPoint, QPointF,
    QDate, QDateTime, QTime,
    qAddPostRoutine
)
from PySide6.QtWidgets import (
    QLineEdit,
    QStyleOptionButton,
    QStyle,
    QApplication,
    QSizePolicy
)
from PySide6.QtGui import QColor, QBrush, QFont, QFontDatabase, QKeySequence
from libqt5.pyqtcore import QMap, INT_MIN, INT_MAX, QList, QMapList
from QtProperty.qtproperty import QtProperty
from QtProperty.qtabstractpropertymanager import QtAbstractPropertyManager
from QtProperty.qtpropertyutils import *


DATA_VAL            = 1
DATA_MINVAL         = 2
DATA_MAXVAL         = 3
DATA_SINGLESTEP     = 4
DATA_READONLY       = 5
DATA_DECIMALS       = 6
DATA_TEXTVISIBLE    = 7
DATA_ENUMNAMES      = 8
DATA_FLAGNAMES      = 9
DATA_REGEXP         = 10
DATA_ECHOMODE       = 11
DATA_CONSTRAINT     = 12
DATA_ENUMICONS      = 13
DATA_GETMINVAL      = 20
DATA_GETMAXVAL      = 21
DATA_SETMINVAL      = 22
DATA_SETMAXVAL      = 23


def getData(propertyMap, data, prop, defaultValue=None):
    it = propertyMap.get(prop)

    if not it:
        return defaultValue
    if data == DATA_MINVAL:
        return it.min_val
    elif data == DATA_MAXVAL:
        return it.max_val
    elif data == DATA_SINGLESTEP:
        return it.single_step
    elif data == DATA_READONLY:
        return it.read_only
    elif data == DATA_DECIMALS:
        return it.decimals
    elif data == DATA_TEXTVISIBLE:
        return it.text_visible
    elif data == DATA_ENUMNAMES:
        return it.enum_names
    elif data == DATA_ENUMICONS:
        return it.enum_icons
    elif data == DATA_FLAGNAMES:
        return it.flag_names
    elif data == DATA_REGEXP:
        return it.regExp
    elif data == DATA_ECHOMODE:
        return it.echo_mode
    else:
        return it.val


def getValue(propertyMap, prop, defaultValue=None):
    return getData(propertyMap, DATA_VAL, prop, defaultValue)


def setSimpleMinData(data, min_val):
    data.min_val = min_val
    if data.max_val < data.min_val:
        data.max_val = data.min_val

    if data.val < data.min_val:
        data.val = data.min_val


def setSimpleMaxData(data, max_val):
    data.max_val = max_val
    if data.min_val > data.max_val:
        data.min_val = data.max_val

    if data.val > data.max_val:
        data.val = data.max_val


def setSimpleValue(prop_map, 
                   prop_changed_signal,
                   value_changed_signal,
                   prop,
                   val):
    if not prop in prop_map.keys():
        return
    
    if prop_map[prop] == val:
        return
    
    prop_map[prop] = val

    prop_changed_signal.emit(prop)
    value_changed_signal.emit(prop, val)


def getMinimum(property_map, prop, default_value=None):
    return getData(property_map, DATA_MINVAL, prop, default_value)


def getMaximum(property_map, prop, default_value=None):
    return getData(property_map, DATA_MAXVAL, prop, default_value)


def setValueInRange(mgr, prop_changed_signal, value_changed_signal, prop, val, set_subprop_value=None):
    if not prop in mgr.values.keys():
        return

    data = mgr.values[prop]

    if data.val == val:
        return

    old_val = data.val
    data.val = qBound(data.min_val, val, data.max_val)

    if data.val == old_val:
        return

    if set_subprop_value:
        set_subprop_value(prop, data.val)

    prop_changed_signal.emit(prop)
    value_changed_signal.emit(prop, data.val)


def qBoundSize(min_val, val, max_val):
    t1 = type(min_val)
    t2 = type(val)
    t3 = type(max_val)
    cropped_val = val
    if t1 == t2 == t3:
        if t1 in [QSize, QSizeF]:
            if min_val.width() > val.width():
                cropped_val.setWidth(min_val.width())
            elif max_val.width() < val.width():
                cropped_val.setWidth(max_val.width())

            if min_val.height() > val.height():
                cropped_val.setHeight(min_val.height())
            elif max_val.height() < val.height():
                cropped_val.setHeight(max_val.height())
        else:
            cropped_val = max(min(max_val, cropped_val), min_val)

    return cropped_val


def qBound(min_val, val, max_val):
    t1 = type(min_val)
    t2 = type(val)
    t3= type(max_val)
    if t1 in [QSize, QSizeF] and t2 in [QSize, QSizeF] and t3 in [QSize, QSizeF]:
        return qBoundSize(min_val, val, max_val)
    else:
        return max(min(max_val, val), min_val)


def setMinimumValue(mgr,
                    prop_changed_signal,
                    value_changed_signal,
                    range_changed_signal,
                    prop,
                    min_val):
    set_sub_prop_range = 0
    setBorderValue(mgr, prop_changed_signal, value_changed_signal, range_changed_signal,
                   prop, DATA_GETMINVAL, DATA_SETMINVAL, min_val, set_sub_prop_range)


def setMaximumValue(mgr,
                    prop_changed_signal,
                    value_changed_signal,
                    range_changed_signal,
                    prop,
                    max_val):
    set_sub_prop_range = 0
    setBorderValue(mgr, prop_changed_signal, value_changed_signal, range_changed_signal,
                   prop, DATA_GETMAXVAL, DATA_SETMAXVAL, max_val, set_sub_prop_range)


def setBorderValue(mgr,
                   prop_changed_signal,
                   value_changed_signal,
                   range_changed_signal,
                   prop,
                   get_range_val,
                   set_range_val,
                   border_val,
                   set_subprop_range):
    if not prop in mgr.values.keys():
        return

    data = mgr.values[prop]

    if get_range_val == DATA_GETMINVAL:
        b_val = data.min_val
    elif get_range_val == DATA_GETMAXVAL:
        b_val = data.max_val
    else:
        b_val = data.val

    if b_val == border_val:
        return

    old_val = data.val
    if set_range_val == DATA_SETMINVAL:
        data.setMinValue(border_val)
    elif set_range_val == DATA_SETMAXVAL:
        data.setMaxValue(border_val)
    else:
        pass

    range_changed_signal.emit(prop, data.min_val, data.max_val)

    # TODO: set_subprop_range는 무슨 데이터인가???
    if set_subprop_range:
        set_subprop_range(prop, data.min_val, data.max_val, data.val)

    if data.val == old_val:
        return

    prop_changed_signal.emit(prop)
    value_changed_signal.emit(prop, data.val)


def setBorderValues(mgr,
                    prop_changed_signal,
                    value_changed_signal,
                    range_changed_signal,
                    prop,
                    min_val,
                    max_val,
                    set_subprop_range):
    if not prop in mgr.values.keys():
        return

    from_val = min_val
    to_val = max_val
    t1 = type(min_val)
    t2 = type(max_val)

    if t1 in [QSize, QSizeF] and t2 in [QSize, QSizeF]:
        t = orderSizeBorders(min_val, max_val)  # TODO: Type check
        from_val, to_val = t[0], t[1]
    else:
        if from_val > to_val:
            from_val, to_val = to_val, from_val

    data = mgr.values[prop]

    if data.min_val == from_val and data.max_val == to_val:
        return

    old_val = data.val

    data.setMinValue(from_val)
    data.setMaxValue(to_val)

    range_changed_signal.emit(prop, data.min_val, data.max_val)

    if set_subprop_range:
        set_subprop_range(prop, data.min_val, data.max_val, data.val)

    if data.val == old_val:
        return

    prop_changed_signal.emit(prop)
    value_changed_signal.emit(prop, data.val)


def orderSizeBorders(min_val, max_val):
    from_size = min_val
    to_size = max_val

    if from_size.width() > to_size.width():
        from_size.setWidth(max_val.width())
        to_size.setWidth(min_val.width())

    if from_size.height() > to_size.height():
        from_size.setHeight(max_val.height())
        to_size.setHeight(min_val.height())

    return (from_size, to_size)


def drawCheckBox(value):
    opt = QStyleOptionButton()
    if value:
        opt.state |= QStyle.State_On
    else:
        opt.state |= QStyle.State_Off

    opt.state |= QStyle.State_Enabled
    style = QApplication.style()

    # Figure out size of an indicator and make sure it is not scaled down in a list view item
    # by making the pixmap as big as a list view icon and centering the indicator in it.
    # (if it is smaller, it can't be helped)

    indicatorWidth = style.pixelMetric(QStyle.PM_IndicatorWidth, opt)
    indicatorHeight = style.pixelMetric(QStyle.PM_IndicatorHeight, opt)
    listViewIconSIze = indicatorWidth
    pixmapWidth = indicatorWidth
    pixmapHeight = max(indicatorHeight, listViewIconSIze)

    opt.rect = QRect(0, 0, indicatorWidth, indicatorHeight)
    pixmap = QPixmap(pixmapWidth, pixmapHeight)
    pixmap.fill(Qt.transparent)

    # Center?
    if pixmapWidth > indicatorWidth:
        xoff = (pixmapWidth - indicatorWidth) / 2
    else:
        xoff = 0

    if pixmapHeight > indicatorHeight:
        yoff = (pixmapHeight - indicatorHeight) / 2
    else:
        yoff = 0

    painter = QPainter(pixmap)
    painter.translate(xoff, yoff)

    style.drawPrimitive(QStyle.PE_IndicatorCheckBox, opt, painter)
    painter.end()

    return QIcon(pixmap)


g_metaEnumProvider = None


def metaEnumProvider():
    global g_metaEnumProvider
    if not g_metaEnumProvider:
        g_metaEnumProvider = QtMetaEnumProvider()
    return g_metaEnumProvider


g_fontDatabaseVar = None


def fontDatabase():
    global g_fontDatabaseVar
    if not g_fontDatabaseVar:
        g_fontDatabaseVar = QFontDatabase()
    
    return g_fontDatabaseVar


#####################################################################################
#
#   class   QtGroupPropertyManager
#
#   brief   The QtGroupPropertyManager provides and managers group properties.
#
#   This class is intended to provide a grouping element without any value.
#
#####################################################################################
class QtGroupPropertyManager(QtAbstractPropertyManager):
    def __init__(self, parent=None):
        super(QtGroupPropertyManager, self).__init__(parent)

    def hasValue(self, prop):
        return False

    def initializeProperty(self, prop):
        pass

    def uninitializeProperty(self, prop):
        pass


#####################################################################################
#
#   class QtStringPropertyManager
#
#   brief The QtStringPropertyManager provides and manages string properties.
#
#   A string property's value can be retrieved using the value() function,
#   and set using the setValue() slot.
#
#   The current value can be checked against a regular expression.
#   To set the regular expression use the setRegExp() slot, use the regExp() function
#   to retrieve the currently set expression.
#
#   In addition, QtStringPropertyManager provides the valueChanged() signal which is
#   emitted whenever a property created by this manager changes, and the regExpChanged()
#   signal which is emitted whenever such a property changes its currently set regular
#   expression.
#
#   = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#   QtStringPropertyManager signal description:
#
#   valueChanged(property, value)
#
#   This signal is emitted whenever a property created by this manager changes its value,
#   passing the property and the new value as parameters.
#
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   regExpChangedSignal(property, regExp)
#
#   This signal is emitted whenever a property created by this manager changes its
#   currently set regular expression, passing the property and the new regExp
#   as parameters.
#####################################################################################
class QtStringPropertyManager(QtAbstractPropertyManager):
    # Defines custom signals
    valueChangedSignal = Signal(QtProperty, str)
    echoModeChangedSignal = Signal(QtProperty, int)
    readOnlyChangedSignal = Signal(QtProperty, bool)
    # regExpChangedSignal = Signal(QtProperty, QRegularExpression)

    class Data:
        val = ""
        echo_mode = QLineEdit.Normal
        read_only = False

    def __init__(self, parent=None):
        """
        Creates a manager with given the parent.
        """
        super(QtStringPropertyManager, self).__init__(parent)
        self.Data = QtStringPropertyManager.Data
        self.values = QMap()

    def __del__(self):
        self.clear()

    def value(self, prop):
        return getValue(self.values, prop, "")

    def echoMode(self, prop):
        return getData(self.values, DATA_ECHOMODE, prop, 0)

    def isReadOnly(self, prop):
        return getData(self.values, DATA_READONLY, prop, False)

    def valueText(self, prop):
        if not prop in self.values.keys():
            return ""

        return self.values[prop].val

    def displayText(self, prop):
        if not prop in self.values.keys():
            return ""

        edit = QLineEdit()
        edit.setEchoMode(self.values[prop].echo_mode)
        edit.setText(self.values[prop].val)
        return edit.displayText()

    def setValue(self, prop, val):
        if not prop in self.values.keys():
            return

        data = self.values[prop]

        if data.val == val:
            return

        # if (data.regExp.isValid() and not data.regExp.exactMatch(val)):
        #     return

        data.val = val

        self.values[prop] = data

        self.propertyChangedSignal.emit(prop)
        self.valueChangedSignal.emit(prop, data.val)

    ###
    #    Sets the regular expression of the given \a property to \a regExp.
    #
    #    \sa regExp(), setValue(), regExpChanged()
    ###
    # def setRegExp(self, property, regExp):
    #
    #     if not property in self.d_ptr.values.keys():
    #         return
    #
    #     data = self.d_ptr.values[property]
    #
    #     if (data.regExp == regExp):
    #         return
    #
    #     data.regExp = regExp
    #
    #     self.d_ptr.values[property] = data
    #
    #     self.regExpChangedSignal.emit(property, data.regExp)

    def setEchoMode(self, prop, echoMode):
        if not prop in self.values.keys():
            return

        data = self.values[prop]

        if data.echoMode == echoMode:
            return

        data.echoMode = echoMode
        self.values[prop] = data

        self.propertyChangedSignal.emit(prop)
        self.echoModeChangedSignal.emit(prop, data.echoMode)

    def setReadOnly(self, prop, readOnly):

        if not prop in self.values.keys():
            return

        data = self.values[prop]

        if data.readOnly == readOnly:
            return

        data.readOnly = readOnly
        self.values[prop] = data

        self.propertyChangedSignal.emit(prop)
        self.echoModeChangedSignal.emit(prop, data.echoMode)

    def initializeProperty(self, prop):
        self.values[prop] = QtStringPropertyManager.Data()

    def uninitializeProperty(self, prop):
        self.values.remove(prop)


#####################################################################################
#
#   class   QtIntPropertyManager
#
#   brief   The QtIntPropertyManager provides and manages int properties.
#
#   An int property has a current value, and a range specifying the valid values.
#   The range is defined by a minimum and a maximum value.
#
#   The property's value and range can be retrieved using the value(), mimimum() and
#   maximum(), setMinimum() and setMaximum() slots.
#   Alternatively, the range can be defined in one go using the setRange() slot.
#
#   In addition, QtintPropertyManager provides the valueChanged() signal which
#   is emitted whenever a property created by this manager changes, and
#   the rangeChanged() signal which is emitted wnheneer such a property changes
#   its range of valid values.
#
#   = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#   QtIntPropertyManager signal description:
#
#   valueChanged(property, value)
#
#    This signal is emitted whenever a property created by this manager
#    changes its value, passing the property and the new
#    value as parameters.
#
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   rangeChanged(property, min, max)
#
#   This signal is emitted whenever a property created by this manager changes
#   its range of valid values, passing the property and the new minimum and maximum values.
#
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   singleStepChanged(property, step)
#
#   This signal is emitted whenever a property created by this manager changes
#   its single step property, passing the property and the new step value.
#
#####################################################################################
class QtIntPropertyManager(QtAbstractPropertyManager):
    # Defines custom signals
    valueChangedSignal = Signal(QtProperty, int)
    rangeChangedSignal = Signal(QtProperty, int, int)
    singleStepChangedSignal = Signal(QtProperty, int)
    readOnlyChangedSignal = Signal(QtProperty, bool)

    class Data:
        val = 0
        min_val = -INT_MAX
        max_val = INT_MAX
        single_step = 1
        read_only = False

        def setMinValue(self, new_min_val):
            setSimpleMinData(self, new_min_val)

        def setMaxValue(self, new_max_val):
            setSimpleMaxData(self, new_max_val)

    def __init__(self, parent=None):
        """
        Creates a manager with the given parent.
        """
        super(QtIntPropertyManager, self).__init__(parent)
        self.values = QMap()
        self.Data = QtIntPropertyManager.Data()

    def __del__(self):
        """
        Destroys this manager, and all the properties it has created.
        """
        self.clear()

    def value(self, prop):
        """
        Returns the given property's value.
        If the given property is not managed by this manager,
        this function returns 0.
        """
        return getValue(self.values, prop, 0)

    def minimum(self, prop):
        """
        Returns the given property's minimum value.
        """
        return getMinimum(self.values, prop, 0)

    def maximum(self, prop):
        """
        Returns the given property's maximum value.
        """
        return getMaximum(self.values, prop, 0)

    def singleStep(self, prop):
        """
        Returns the given property's step value.
        The step is typically used to increment or decrement a property value
        while pressing an arrow key.
        """
        return getData(self.values, DATA_SINGLESTEP, prop, 0)

    def isReadOnly(self, prop):
        """
        Returns read-only status of the property.
        When property is read-only it's value can be selected and copied
        from editor but not modified.
        """
        return getData(self.values, DATA_READONLY, prop, False)

    def valueText(self, prop):
        """
        Reimplementation
        """
        data = self.values.get(prop)
        if not data:
            return ""

        return str(data.val)

    def setValue(self, prop, val):
        """
        Sets the value of the given property to value.
        If the specified value is not valid according to the given
        property's range, the value is adjusted to the nearest valid
        value within the range.
        """
        set_subprop_value = None
        setValueInRange(self, self.propertyChangedSignal, self.valueChangedSignal,
                        prop, val, set_subprop_value)

    def setMinimum(self, prop, min_val):
        """
        Sets the minimum value for the given property to min_val.
        When setting the minimum value, the maximum and current values are
        adjusted if necessary (ensuring that the range remains valid and
        that the current value is within the range).
        """
        setMinimumValue(self,
                        self.propertyChangedSignal,
                        self.valueChangedSignal,
                        self.rangeChangedSignal,
                        prop, min_val)

    def setMaximum(self, prop, max_val):
        """
        Sets the maximum value for the given property to max_val.
        When setting maximum value, the minimum and current values are
        adjusted if necessary (ensuring that the range remains valid and
        that the current value is within the range).
        """
        setMaximumValue(self,
                        self.propertyChangedSignal,
                        self.valueChangedSignal,
                        self.rangeChangedSignal,
                        prop, max_val)

    def setRange(self, prop, min_val, max_val):
        """
        Sets the range of valid values.
        This is a convenience funtion defining the range of vlaid values
        in one go; setting the minimum and maximum values for the given property
        with a single function call.
        When setting a new range, the current value is adjusted if neccessary
        (ensuring that the value remains within range).
        """
        set_subprop_range = 0
        setBorderValues(self,
                        self.propertyChangedSignal,
                        self.valueChangedSignal,
                        self.rangeChangedSignal,
                        prop, min_val, max_val, set_subprop_range)

    def setSingleStep(self, prop, step):
        """
        Sets the step value for the given property to step.
        The step is typically used to increment or decrement a property value
        while pressing an arrow key.
        """
        if not prop in self.values.keys():
            return

        data = self.values[prop]

        if step < 0:
            step = 0

        if data.single_step == step:
            return

        data.single_step = step

        self.values[prop] = data
        self.singleStepChangedSignal.emit(prop, data.single_step)

    def setReadOnly(self, prop, read_only):
        """
        Sets read-only status of the property.
        """
        if not prop in self.values.keys():
            return

        data = self.values[prop]

        if data.read_only == read_only:
            return

        data.read_only = read_only
        self.values[prop] = data

        self.propertyChangedSignal.emit(prop)
        self.readOnlyChangedSignal.emit(prop, data.read_only)

    def initializeProperty(self, prop):
        """
        Reimplementation
        """
        self.values[prop] = QtIntPropertyManager.Data()

    def uninitializeProperty(self, prop):
        """
        Reimplementaion
        """
        self.values.remove(prop)


#####################################################################################
#
#   class   QtDoublePropertyManager
#
#   brief   The QtDoublePropertyManager provides and manages double properties.
#
#    A double property has a current value, and a range specifying the
#    valid values. The range is defined by a minimum and a maximum
#    value.
#
#    The property's value and range can be retrieved using the value(),
#    minimum() and maximum() functions, and can be set using the
#    setValue(), setMinimum() and setMaximum() slots.
#    Alternatively, the range can be defined in one go using the
#    setRange() slot.
#
#    In addition, QtDoublePropertyManager provides the valueChanged() signal
#    which is emitted whenever a property created by this manager
#    changes, and the rangeChanged() signal which is emitted whenever
#    such a property changes its range of valid values.
#
#   = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#   QtDoublePropertyManager signal description:
#
#   valueChanged(property, value)
#
#    This signal is emitted whenever a property created by this manager
#    changes its value, passing the property and the new
#    value as parameters.
#
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   rangeChangedSignal(property, min, max)
#
#   This signal is emitted whenever a property created by this manager changes its
#   range of valid values, passing the property and the new minimum and maximum values.
#
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   singleStepChanged(property, step)
#
#   This signal is emitted whenever a property created by this manager changes
#   its single step property, passing the property and the new step value.
#
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   decimalsChanged(property, precision)
#
#   This signal is emitted wheever a property created by this manager changes its
#   precision of value, passing the property and the new precesion value.
#
#####################################################################################
class QtDoublePropertyManager(QtAbstractPropertyManager):
    # Defines custom signals
    valueChangedSignal      = Signal(QtProperty, float)
    rangeChangedSignal      = Signal(QtProperty, float, float)
    singleStepChangedSignal = Signal(QtProperty, float)
    decimalsChangedSignal   = Signal(QtProperty, int)
    readOnlyChangedSignal   = Signal(QtProperty, bool)

    class Data:
        val = 0.0
        min_val = -INT_MAX
        max_val = INT_MAX
        single_step = 1.0
        decimals = 2
        read_only = False

        def setMinValue(self, new_min_val):
            setSimpleMinData(self, new_min_val)

        def setMaxValue(self, new_max_val):
            setSimpleMaxData(self, new_max_val)

    def __init__(self, parent=None):
        """
        Creates a manager with the given parent.
        """
        super(QtDoublePropertyManager, self).__init__(parent)
        self.values = QMap()
        self.Data = QtDoublePropertyManager.Data()

    def __del__(self):
        """
        Destroys this manager, and all the properties it has created.
        """
        self.clear()

    def value(self, prop):
        """
        Returns the given property's value.
        """
        return getValue(self.values, prop, 0.0)

    def minimum(self, prop):
        """
        Returns the given property's minimum value.
        """
        return getMinimum(self.values, prop, 0.0)

    def maximum(self, prop):
        """
        Returns the given property's maximum value.
        """
        return getMaximum(self.values, prop, 0.0)

    def singleStep(self, prop):
        """
        Returns the given property's step value.
        The step is typically used to increment or decrement a property value
        while pressing an arrow key.
        """
        return getData(self.values, DATA_SINGLESTEP, prop, 0)

    def decimals(self, prop):
        """
        Returns the given property's precision, in decimals.
        """
        return getData(self.values, DATA_DECIMALS, prop, 0)

    def isReadOnly(self, prop):
        """
        Returns read-only status of the property.
        When property is read-only it's value can be selected and copied
        from editor but not modified.
        """
        return getData(self.values, DATA_READONLY, prop, False)

    def valueText(self, prop) -> str:
        """
        Reimplementation
        """
        if not prop in self.values.keys():
            return ""

        return QLocale.system().toString(float(self.values[prop].val), 'f', self.values[prop].decimals)

    def setValue(self, prop, val):
        """
        Sets the value of the given property to value.
        If the specified value is not valid according to the given
        property's range, the value is adjusted to the nearest valid
        value within the range.
        """
        set_subprop_value = None
        setValueInRange(self, self.propertyChangedSignal, self.valueChangedSignal,
                        prop, val, set_subprop_value)

    def setMinimum(self, prop, min_val):
        """
        Sets the minimum value for the given property to min_val.
        When setting the minimum value, the maximum and current values are
        adjusted if necessary (ensuring that the range remains valid and
        that the current value is within the range).
        """
        setMinimumValue(self,
                        self.propertyChangedSignal,
                        self.valueChangedSignal,
                        self.rangeChangedSignal,
                        prop, min_val)

    def setMaximum(self, prop, max_val):
        """
        Sets the maximum value for the given property to max_val.
        When setting maximum value, the minimum and current values are
        adjusted if necessary (ensuring that the range remains valid and
        that the current value is within the range).
        """
        setMaximumValue(self,
                        self.propertyChangedSignal,
                        self.valueChangedSignal,
                        self.rangeChangedSignal,
                        prop, max_val)

    def setRange(self, prop, min_val, max_val):
        """
        Sets the range of valid values.
        This is a convenience funtion defining the range of vlaid values
        in one go; setting the minimum and maximum values for the given property
        with a single function call.
        When setting a new range, the current value is adjusted if neccessary
        (ensuring that the value remains within range).
        """
        set_subprop_range = 0
        setBorderValues(self,
                        self.propertyChangedSignal,
                        self.valueChangedSignal,
                        self.rangeChangedSignal,
                        prop, min_val, max_val, set_subprop_range)

    def setSingleStep(self, prop, step):
        """
        Sets the step value for the given property to step.
        The step is typically used to increment or decrement a property value
        while pressing an arrow key.
        """
        if not prop in self.values.keys():
            return

        data = self.values[prop]

        if step < 0:
            step = 0

        if data.single_step == step:
            return

        data.single_step = step

        self.values[prop] = data
        self.singleStepChangedSignal.emit(prop, data.single_step)

    def setReadOnly(self, prop, read_only):
        """
        Sets read-only status of the property.
        """
        if not prop in self.values.keys():
            return

        data = self.values[prop]

        if data.read_only == read_only:
            return

        data.read_only = read_only
        self.values[prop] = data

        self.propertyChangedSignal.emit(prop)
        self.readOnlyChangedSignal.emit(prop, data.read_only)

    def setDecimals(self, prop, precision):
        """
        Sets the precision of the given property to precision.
        The valid decimal range is 0~13.
        The default is 2.
        """
        if not prop in self.values.keys():
            return

        data = self.values[prop]

        if precision > 13:
            precision = 13
        elif precision < 0:
            precision = 0

        if data.decimals == precision:
            return

        data.decimals = precision

        self.values[prop] = data
        self.decimalsChangedSignal.emit(prop, data.decimals)

    def initializeProperty(self, prop):
        """
        Reimplementation
        """
        self.values[prop] = QtDoublePropertyManager.Data()

    def uninitializeProperty(self, prop):
        """
        Reimplementaion
        """
        self.values.remove(prop)


#####################################################################################
#
#   class   QtBoolPropertyManager
#
#   brief   The QtBoolPropertyManager class provides and manages boolean properties.
#
#   The property's value can be retrieved using the value() function, and
#   set using setValue() slot.
#
#   In addition, QtBoolPropertyManager provides the valueChagned() signal which is
#   emitted whenever a property created by this manager changes.
#
#   = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#   QtBoolPropertyManager signal description:
#
#   valueChanged(property, value)
#
#   This signal is emitted whenever a property created by this manager changes its
#   value, passing the property and the new value as parameters.
#
#####################################################################################
class QtBoolPropertyManager(QtAbstractPropertyManager):
    # Defines custom signals
    valueChangedSignal          = Signal(QtProperty, bool)
    textVisibleChangedSignal    = Signal(QtProperty, bool)

    class Data:
        val = False
        val2 = False
        text_visible = True

    def __init__(self, parent=None):
        """
        Creates a manager with the given parent.
        """
        super(QtBoolPropertyManager, self).__init__(parent)
        self.values = QMap()
        self.Data = QtBoolPropertyManager.Data()
        self.checked_icon = drawCheckBox(True)
        self.unchecked_icon = drawCheckBox(False)

    def __del__(self):
        """
        Destroys this manager, and all the properties it has created.
        """
        self.clear()

    def value(self, prop):
        """
        Returns the given property's value.
        If the given property is not managed by this manager,
        this function returns False.
        """
        return getValue(self.values, prop, False)

    def textVisible(self, prop):
        """
        Returns the given property's text visible value.
        If the given property is not managed by this manager,
        this function returns False.
        :param prop:
        :return:
        """
        return getData(self.values, DATA_TEXTVISIBLE, prop, False)

    def valueText(self, prop) -> str:
        """
        Reimplementation
        """
        if not prop in self.values.keys():
            return ""

        data = self.values[prop]

        if not data.text_visible:
            return ""

        true_text = "True"
        false_text = "False"

        if data.val:
            return true_text
        else:
            return false_text

    def valueIcon(self, prop) -> QIcon:
        """
        Reimplementation
        """
        if not prop in self.values.keys():
            return

        if self.values[prop].val:
            return self.checked_icon
        else:
            return self.unchecked_icon

    def setValue(self, prop, val):
        """
        Sets the value of the given property to value.
        """
        if not prop in self.values.keys():
            return

        data = self.values[prop]
        if data.val == val:
            return

        data.val = val
        self.values[prop] = data

        self.propertyChangedSignal.emit(prop)
        self.valueChangedSignal.emit(prop, data.val)

    def setTextVisible(self, prop, text_visible):
        if not prop in self.values.keys():
            return

        data = self.values[prop]

        if data.text_visible == text_visible:
            return

        data.text_visible = text_visible
        self.values[prop] = data

        self.propertyChangedSignal.emit(prop)
        self.textVisibleChangedSignal.emit(prop, data.text_visible)

    def initializeProperty(self, prop):
        """
        Reimplementation
        """
        self.values[prop] = QtBoolPropertyManager.Data()

    def uninitializeProperty(self, prop):
        """
        Reimplementation
        """
        self.values.remove(prop)


#####################################################################################
#
#   class   QtColorPropertyManager
#
#   brief   The QtColorPropertyManager provides and manages QColor properties.
#
#   A color property has nested red, greed and blue subproperties.
#   The top-level property's value can be retrieved using the vlaue() function, and
#   set using the setValue() slot.
#
#   The subproperties are created by a QtIntPropertyManager object. This manager can
#   be retrieved using the subIntPropertyManager() function. In order to provide editing
#   widgets for the subproperties in a property browser widget, this manager must be
#   associated with an editor factory.
#
#   In addition, QtColorPropertyManager provides the valueChanged() signal which is
#   emitted whenever a property created by this manager changes.
#
#   = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#   QtBoolPropertyManager signal description:
#
#   valueChanged(property, value)
#
#   This signal is emitted whenever a property created by this manager changes its
#   value, passing the property and the new value as parameters.
#
#####################################################################################
class QtColorPropertyManager(QtAbstractPropertyManager):
    # Defines custom signal
    valueChangedSignal = Signal(QtProperty, QColor)

    def __init__(self, parent=None):
        """
        Creates a manager with the given parent.
        """
        super(QtColorPropertyManager, self).__init__(parent)
        self.values = QMap()
        self.prop_to_r = QMap()
        self.prop_to_g = QMap()
        self.prop_to_b = QMap()
        self.prop_to_a = QMap()
        self.r_to_prop = QMap()
        self.g_to_prop = QMap()
        self.b_to_prop = QMap()
        self.a_to_prop = QMap()
        self.int_prop_mgr = None

        self.int_prop_mgr = QtIntPropertyManager(self)
        self.int_prop_mgr.valueChangedSignal.connect(self.slotIntChanged)
        self.int_prop_mgr.propertyDestroyedSignal.connect(self.slotPropertyDestroyed)

    def __del__(self):
        """
        Destroys this manager, and all the properties it has crated.
        """
        self.clear()

    def subIntPropertyManager(self):
        """
        Returns the manager that produces the nested red, green, and blue subproperties.

        In order to provide editing widgets for the subproperties in a property browser widget,
        this manager must be associated with an editor factory.
        """
        return self.int_prop_mgr

    def value(self, prop):
        """
        Returns the given property's value.

        If the given property is not managed by this manager,
        this function returns an invalid color.
        """
        return self.values.get(prop, QColor())

    def valueText(self, prop) -> str:
        """
        Reimplementation
        """
        if not prop in self.values.keys():
            return ""

        color = self.values[prop]
        return "[%d, %d, %d] (%d)" % (color.red(), color.green(), color.blue(), color.alpha())

    def valueIcon(self, prop) -> QIcon:
        """
        Reimplementation
        """
        if not prop in self.values.keys():
            return QIcon()

        return brushValueIcon(QBrush(self.values[prop]))

    def setValue(self, prop, val):
        """
        Sets the value of the given property to value.
        Nested properties are updated automatically.
        """
        if not prop in self.values.keys():
            return

        if self.values[prop] == val:
            return

        self.values[prop] = val

        self.int_prop_mgr.setValue(self.prop_to_r[prop], val.red())
        self.int_prop_mgr.setValue(self.prop_to_g[prop], val.green())
        self.int_prop_mgr.setValue(self.prop_to_b[prop], val.blue())
        self.int_prop_mgr.setValue(self.prop_to_a[prop], val.alpha())

        self.propertyChangedSignal.emit(prop)
        self.valueChangedSignal.emit(prop, val)

    def initializeProperty(self, prop):
        """
        Reimplementation
        """
        val = QColor()
        self.values[prop] = val

        r_prop = self.int_prop_mgr.addProperty()
        r_prop.setPropertyName("Red")
        self.int_prop_mgr.setValue(r_prop, val.red())
        self.int_prop_mgr.setRange(r_prop, 0, 0xFF)
        self.prop_to_r[prop] = r_prop
        self.r_to_prop[r_prop] = prop
        prop.addSubProperty(r_prop)

        g_prop = self.int_prop_mgr.addProperty()
        g_prop.setPropertyName("Green")
        self.int_prop_mgr.setValue(g_prop, val.green())
        self.int_prop_mgr.setRange(g_prop, 0, 0xFF)
        self.prop_to_g[prop] = g_prop
        self.g_to_prop[g_prop] = prop
        prop.addSubProperty(g_prop)

        b_prop = self.int_prop_mgr.addProperty()
        b_prop.setPropertyName("Blue")
        self.int_prop_mgr.setValue(b_prop, val.blue())
        self.int_prop_mgr.setRange(b_prop, 0, 0xFF)
        self.prop_to_b[prop] = b_prop
        self.b_to_prop[b_prop] = prop
        prop.addSubProperty(b_prop)

        a_prop = self.int_prop_mgr.addProperty()
        a_prop.setPropertyName("Alpha")
        self.int_prop_mgr.setValue(a_prop, val.alpha())
        self.int_prop_mgr.setRange(a_prop, 0, 0xFF)
        self.prop_to_a[prop] = a_prop
        self.a_to_prop[a_prop] = prop
        prop.addSubProperty(a_prop)

    def uninitializeProperty(self, prop):
        """
        Reimplementation
        """
        r_prop = self.prop_to_r[prop]
        if r_prop:
            self.r_to_prop.remove(r_prop)
            del r_prop

        self.prop_to_r.remove(prop)

        g_prop = self.prop_to_g[prop]
        if g_prop:
            self.g_to_prop.remove(g_prop)
            del g_prop

        self.prop_to_g.remove(prop)

        b_prop = self.prop_to_b[prop]
        if b_prop:
            self.b_to_prop.remove(b_prop)
            del b_prop

        self.prop_to_b.remove(prop)

        a_prop = self.prop_to_a[prop]
        if a_prop:
            self.a_to_prop.remove(a_prop)
            del a_prop

        self.prop_to_a.remove(prop)

    def slotIntChanged(self, prop, value):
        prop_r = self.r_to_prop.get(prop, 0)
        if prop_r:
            c = copy.copy(self.values[prop_r])
            c.setRed(value)
            self.setValue(prop_r, c)
        else:
            prop_g = self.g_to_prop.get(prop, 0)
            if prop_g:
                c = copy.copy(self.values[prop_g])
                c.setGreen(value)
                self.setValue(prop_g, c)
            else:
                prop_b = self.b_to_prop.get(prop, 0)
                if prop_b:
                    c = copy.copy(self.values[prop_b])
                    c.setBlue(value)
                    self.setValue(prop_b, c)
                else:
                    prop_a = self.a_to_prop.get(prop, 0)
                    if prop_a:
                        c = copy.copy(self.values[prop_a])
                        c.setAlpha(value)
                        self.setValue(prop_a, c)

    def slotPropertyDestroyed(self, prop):
        prop_r = self.r_to_prop.get(prop, 0)
        if prop_r:
            self.prop_to_r[prop_r] = 0
            self.r_to_prop.remove(prop)
        else:
            prop_g = self.g_to_prop.get(prop, 0)
            if prop_g:
                self.prop_to_g[prop_g] = 0
                self.g_to_prop.remove(prop)
            else:
                prop_b = self.b_to_prop.get(prop, 0)
                if prop_b:
                    self.prop_to_b[prop_b] = 0
                    self.b_to_prop.remove(prop)
                else:
                    prop_a = self.a_to_prop.get(prop, 0)
                    if prop_a:
                        self.prop_to_a[prop_a] = 0
                        self.a_to_prop.remove(prop)


#####################################################################################
#
#   class   QtRectPropertyManager
#
#   brief   The QtRectPropertymanager provides and manages QRect properties.
#
#   A rectangle property has nested x, y, width and height subproperties.
#   The top-level property's value can be retrieved using the value() function,
#   and set using the setValue() slot.
#
#   The subproperties are created by a QtIntPropetyManager object. This manager can be
#   retrieved using the subIntPropertyManager() function. In order to provide editing
#   widgets for the subproperties in a property browser widget, this manager must be
#   associated with an editor factory.
#
#   A rectangle property also has a constraint rectangle which can be retrieved
#   using the constraint() function, and st using the setConstraint() slot.
#
#   In addition, QtRectPropertyManager provides the valueChanged() signal which is emitted
#   whenever a property created by this manager changes, and the constraintChange() signal
#   which is emitted whenever such a property changes its constraint rectangle.
#
#   = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#   QtRectPropertyManager signal description:
#
#   valueChanged(property, value)
#
#   This signal is emitted whenever a property created by this manager changes its
#   value, passing the property and the new value as parameters.
#
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   constraintChanged(property, constraint)
#
#   This signal is emitted whenever property changes its constraint rectangle,
#   passing the property and the new constraint rectangle as parameters.
#
#####################################################################################
class QtRectPropertyManager(QtAbstractPropertyManager):
    # Defines custom signals
    valueChangedSignal      = Signal(QtProperty, QRect)
    constraintChangedSignal = Signal(QtProperty, QRect)

    class Data:
        val = QRect(0, 0, 0, 0)
        constraint = QRect(0, 0, 0, 0)

    def __init__(self, parent=None):
        """
        Creates a manager with the given parent.
        """
        super(QtRectPropertyManager, self).__init__(parent)
        self.values = QMap()
        self.prop_to_x = QMap()
        self.prop_to_y = QMap()
        self.prop_to_w = QMap()
        self.prop_to_h = QMap()
        self.x_to_prop = QMap()
        self.y_to_prop = QMap()
        self.w_to_prop = QMap()
        self.h_to_prop = QMap()
        self.Data = QtRectPropertyManager.Data()

        self.int_prop_mgr = QtIntPropertyManager(self)
        self.int_prop_mgr.valueChangedSignal.connect(self.slotIntChanged)
        self.int_prop_mgr.propertyDestroyedSignal.connect(self.slotPropertyDestroyed)

    def __del__(self):
        """
        Destroys this manager, and all the properties it has crated.
        """
        self.clear()

    def subIntPropertyManager(self):
        """
        Returns the manager that creates the nested x, y, width and height subproperties.

        In order to provide editing widgets for the mentioned subproperties
        in a property browswer widget, this manager must be associated with an editor factory.
        """
        return self.int_prop_mgr

    def value(self, prop):
        """
        Returns the given property's value.

        If the given property is not managed by this manager, this function
        returns an invalid rectangle.
        """
        return getValue(self.values, prop, QRect())

    def constraint(self, prop):
        """
        Returns the given property's constraining rectangle.
        If returned value is null QRect it means there is no constraint applied.
        """
        return getData(self.values, DATA_CONSTRAINT, prop, QRect())

    def valueText(self, prop) -> str:
        """
        Reimplementation
        """
        if not prop in self.values.keys():
            return ""

        val = self.values[prop].val

        return "[(%d, %d), %d x %d]" % (val.x(), val.y(), val.width(), val.height())

    def setValue(self, prop, val):
        """
        Sets the value of the given property to value.
        Nested properties are updated automatically.

        If the specified value is not inside the given property's constraining rectangle,
        the value is adjusted accordingly to fit within constraint.
        """
        if not prop in self.values.keys():
            return

        data = self.values[prop]

        new_rect = val.normalized()
        if not data.constraint.isNull() and not data.constraint.contains(new_rect):
            r1 = data.constraint
            r2 = new_rect
            new_rect.setLeft(max(r1.left(), r2.left()))
            new_rect.setRight(min(r1.right(), r2.right()))
            new_rect.setTop(max(r1.top(), r2.top()))
            new_rect.setBottom(min(r1.bottom(), r2.bottom()))

            if new_rect.width() < 0 or new_rect.height() < 0:
                return

        if data.val == new_rect:
            return

        data.val = new_rect
        self.values[prop] = data

        self.int_prop_mgr.setValue(self.prop_to_x[prop], new_rect.x())
        self.int_prop_mgr.setValue(self.prop_to_y[prop], new_rect.y())
        self.int_prop_mgr.setValue(self.prop_to_w[prop], new_rect.width())
        self.int_prop_mgr.setValue(self.prop_to_h[prop], new_rect.height())

        self.propertyChangedSignal.emit(prop)
        self.valueChangedSignal.emit(prop, data.val)

    def setConstraint(self, prop, constraint):
        """
        sets the given property's constraining rectangle to constraint.
        When setting the constraint, the current value is adjusted if necessary
        (ensuring that the current rectangle value is inside the constraint).
        In order to reset the constraint pass a null QRect value.
        """
        if not prop in self.values.keys():
            return

        data = self.values[prop]
        new_constraint = constraint.normalized()

        if data.constraint == new_constraint:
            return

        old_val = data.val
        data.cosntraint = new_constraint

        if not data.constraint.isNull() and not data.constraint.contains(old_val):
            r1 = data.constraint
            r2 = data.val

            if r2.width() > r1.width():
                r2.setWidth(r1.width())

            if r2.height() > r1.height():
                r2.setHeight(r1.height())

            if r2.left() < r1.left():
                r2.moveLeft(r1.left())
            elif r2.right() > r1.right():
                r2.moveRight(r1.right())

            if r2.top() < r1.top():
                r2.moveTop(r1.top())
            elif r2.bottom() > r1.bottom():
                r2.moveBottom(r1.bottom())

            data.val = r2

        self.values[prop] = data
        self.constraintChangedSignal.emit(prop, data.constraint)

        self.setConstraintWithValue(prop, data.constraint, data.val)

        if data.val == old_val:
            return

        self.propertyChangedSignal.emit(prop)
        self.valueChangedSignal.emit(prop, data.val)

    def initializeProperty(self, prop):
        """
        Reimplementation
        """
        self.values[prop] = QtRectPropertyManager.Data()

        prop_x = self.int_prop_mgr.addProperty()
        prop_x.setPropertyName("X")
        self.int_prop_mgr.setValue(prop_x, self.values[prop].val.x())
        self.prop_to_x[prop] = prop_x
        self.x_to_prop[prop_x] = prop
        prop.addSubProperty(prop_x)

        prop_y = self.int_prop_mgr.addProperty()
        prop_y.setPropertyName("Y")
        self.int_prop_mgr.setValue(prop_y, self.values[prop].val.y())
        self.prop_to_y[prop] = prop_y
        self.y_to_prop[prop_y] = prop
        prop.addSubProperty(prop_y)

        prop_width = self.int_prop_mgr.addProperty()
        prop_width.setPropertyName("Width")
        self.int_prop_mgr.setValue(prop_width, self.values[prop].val.width())
        self.int_prop_mgr.setMinimum(prop_width, 0)
        self.prop_to_w[prop] = prop_width
        self.w_to_prop[prop_width] = prop
        prop.addSubProperty(prop_width)

        prop_height = self.int_prop_mgr.addProperty()
        prop_height.setPropertyName("Height")
        self.int_prop_mgr.setValue(prop_height, self.values[prop].val.height())
        self.int_prop_mgr.setMinimum(prop_height, 0)
        self.prop_to_h[prop] = prop_height
        self.h_to_prop[prop_height] = prop
        prop.addSubProperty(prop_height)

    def uninitializeProperty(self, prop):
        """
        Reimplementation
        """
        prop_x = self.prop_to_x[prop]
        if prop_x:
            self.x_to_prop.remove(prop_x)
            del prop_x
        self.prop_to_x.remove(prop)

        prop_y = self.prop_to_y[prop]
        if prop_y:
            self.y_to_prop.remove(prop_y)
            del prop_y
        self.prop_to_y.remove(prop)

        prop_width = self.prop_to_w[prop]
        if prop_width:
            self.w_to_prop.remove(prop_width)
            del prop_width
        self.prop_to_w.remove(prop)

        prop_height = self.prop_to_h[prop]
        if prop_height:
            self.h_to_prop.remove(prop_height)
            del prop_height
        self.prop_to_h.remove(prop)

        self.values.remove(prop)

    def slotIntChanged(self, prop, value):
        prop_x = self.x_to_prop.get(prop, 0)
        if prop_x:
            r = copy.copy(self.values[prop_x].val)
            r.moveLeft(value)
            self.setValue(prop_x, r)
        else:
            prop_y = self.y_to_prop.get(prop, 0)  # 0을 넣냐 마냐
            if prop_y:
                r = copy.copy(self.values[prop_y].val)
                r.moveTop(value)
                self.setValue(prop_y, r)
            else:
                prop_width = self.w_to_prop.get(prop, 0)
                if prop_width:
                    data = copy.copy(self.values[prop_width])
                    r = copy.copy(data.val)
                    r.setWidth(value)
                    if not data.constraint.isNull() and data.constraint.x() + data.constraint.width() < r.x() + r.width():
                        r.moveLeft(data.constraint.left() + data.constraint.width() - r.width())

                    self.setValue(prop_width, r)
                else:
                    prop_height = self.h_to_prop.get(prop, 0)
                    if prop_height:
                        data = copy.copy(self.values[prop_height])
                        r = copy.copy(data.val)
                        r.setHeight(value)
                        if not data.constraint.isNull() and data.constraint.y() + data.constraint.height() < r.y() + r.height():
                            r.moveTop(data.constraint.top() + data.constraint.height() - r.height())

                        self.setValue(prop_height, r)

    def slotPropertyDestroyed(self, prop):
        prop_x = self.x_to_prop.get(prop, 0)
        if prop_x:
            self.prop_to_x[prop_x] = 0
            self.x_to_prop.remove(prop)
        else:
            prop_y = self.y_to_prop.get(prop, 0)
            if prop_y:
                self.prop_to_y[prop_y] = 0
                self.y_to_prop.remove(prop)
            else:
                prop_width = self.w_to_prop.get(prop, 0)
                if prop_width:
                    self.prop_to_w[prop_width] = 0
                    self.w_to_prop.remove(prop)
                else:
                    prop_height = self.h_to_prop.get(prop, 0)
                    if prop_height:
                        self.prop_to_h[prop_height] = 0
                        self.h_to_prop.remove(prop)

    def setConstraintWithValue(self, prop, constraint, val):
        isNull = constraint.isNull()
        if isNull:
            left    = INT_MIN
            right   = INT_MAX
            top     = INT_MIN
            bottom  = INT_MAX
            width   = INT_MAX
            height  = INT_MAX
        else:
            left    = constraint.left()
            right   = constraint.left() + constraint.width()
            top     = constraint.top()
            bottom  = constraint.top() + constraint.height()
            width   = constraint.width()
            height  = constraint.height()

        self.int_prop_mgr.setRange(self.prop_to_x[prop], left, right)
        self.int_prop_mgr.setRange(self.prop_to_y[prop], top, bottom)
        self.int_prop_mgr.setRange(self.prop_to_w[prop], 0, width)
        self.int_prop_mgr.setRange(self.prop_to_h[prop], 0, height)

        self.int_prop_mgr.setValue(self.prop_to_x[prop], val.x())
        self.int_prop_mgr.setValue(self.prop_to_y[prop], val.y())
        self.int_prop_mgr.setValue(self.prop_to_w[prop], val.width())
        self.int_prop_mgr.setValue(self.prop_to_h[prop], val.height())


#####################################################################################
#
#   class   QtRectFPropertyManager
#
#   brief   The QtRectFPropertymanager provides and manages QRectF properties.
#
#   A rectangle property has nested x, y, width and height subproperties.
#   The top-level property's value can be retrieved using the value() function,
#   and set using the setValue() slot.
#
#   The subproperties are created by a QtDoublePropetyManager object. This manager can be
#   retrieved using the subDoublePropertyManager() function. In order to provide editing
#   widgets for the subproperties in a property browser widget, this manager must be
#   associated with an editor factory.
#
#   A rectangle property also has a constraint rectangle which can be retrieved
#   using the constraint() function, and st using the setConstraint() slot.
#
#   In addition, QtRectPropertyManager provides the valueChanged() signal which is emitted
#   whenever a property created by this manager changes, and the constraintChange() signal
#   which is emitted whenever such a property changes its constraint rectangle.
#
#   = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#   QtRectPropertyManager signal description:
#
#   valueChanged(property, value)
#
#   This signal is emitted whenever a property created by this manager changes its
#   value, passing the property and the new value as parameters.
#
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   constraintChanged(property, constraint)
#
#   This signal is emitted whenever property changes its constraint rectangle,
#   passing the property and the new constraint rectangle as parameters.
#
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   decimalsChanged(property, precision)
#
#   This signal is emitted whenever a property created by this manager changes
#   its precision of value, passing the property and the new precision value.
#
#####################################################################################
class QtRectFPropertyManager(QtAbstractPropertyManager):
    # Defines custom signals
    valueChangedSignal      = Signal(QtProperty, QRectF)
    constraintChangedSignal = Signal(QtProperty, QRectF)
    decimalsChangedSignal   = Signal(QtProperty, int)

    class Data:
        val = QRectF(0, 0, 0, 0)
        constraint = QRectF(0, 0, 0, 0)
        decimals = 4
        single_step = 1.0
        
    def __init__(self, parent=None):
        """
        Creates a manager with the given parent.
        """
        super(QtRectFPropertyManager, self).__init__(parent)
        self.values = QMap()
        self.prop_to_x = QMap()
        self.prop_to_y = QMap()
        self.prop_to_w = QMap()
        self.prop_to_h = QMap()
        self.x_to_prop = QMap()
        self.y_to_prop = QMap()
        self.w_to_prop = QMap()
        self.h_to_prop = QMap()
        self.Data = QtRectFPropertyManager.Data()

        self.double_prop_mgr = QtDoublePropertyManager(self)
        self.double_prop_mgr.valueChangedSignal.connect(self.slotDoubleChanged)
        self.double_prop_mgr.propertyDestroyedSignal.connect(self.slotPropertyDestroyed)

    def __del__(self):
        """
        Destroys this manager, and all the properties it has crated.
        """
        self.clear()

    def subDoublePropertyManager(self):
        """
        Returns the manager that creates the nested x, y, width and height subproperties.

        In order to provide editing widgets for the mentioned subproperties
        in a property browswer widget, this manager must be associated with an editor factory.
        """
        return self.double_prop_mgr

    def value(self, prop):
        """
        Returns the given property's value.

        If the given property is not managed by this manager, this function
        returns an invalid rectangle.
        """
        return getValue(self.values, prop, QRectF())

    def constraint(self, prop):
        """
        Returns the given property's constraining rectangle.
        If returned value is null QRect it means there is no constraint applied.
        """
        return getData(self.values, DATA_CONSTRAINT, prop, QRectF())

    def decimals(self, prop):
        """
        Returns the given property's precision, in decimals.
        """
        return getData(self.values, DATA_DECIMALS, prop, 0)

    def valueText(self, prop) -> str:
        """
        Reimplementation
        """
        if not prop in self.values.keys():
            return ""

        val = self.values[prop].val
        dec = self.values[prop].decimals
        string = "[(%%.%df, %%.%df), %%.%df x %%.%df]" % (dec, dec, dec, dec)
        return string % (val.x(), val.y(), val.width(), val.height())

    def setValue(self, prop, val):
        """
        Sets the value of the given property to value.
        Nested properties are updated automatically.

        If the specified value is not inside the given property's constraining rectangle,
        the value is adjusted accordingly to fit within constraint.
        """
        if not prop in self.values.keys():
            return

        data = self.values[prop]

        new_rect = val.normalized()
        if not data.constraint.isNull() and not data.constraint.contains(new_rect):
            r1 = data.constraint
            r2 = new_rect
            new_rect.setLeft(max(r1.left(), r2.left()))
            new_rect.setRight(min(r1.right(), r2.right()))
            new_rect.setTop(max(r1.top(), r2.top()))
            new_rect.setBottom(min(r1.bottom(), r2.bottom()))

            if new_rect.width() < 0 or new_rect.height() < 0:
                return

        if data.val == new_rect:
            return

        data.val = new_rect
        self.values[prop] = data

        self.double_prop_mgr.setValue(self.prop_to_x[prop], new_rect.x())
        self.double_prop_mgr.setValue(self.prop_to_y[prop], new_rect.y())
        self.double_prop_mgr.setValue(self.prop_to_w[prop], new_rect.width())
        self.double_prop_mgr.setValue(self.prop_to_h[prop], new_rect.height())

        self.propertyChangedSignal.emit(prop)
        self.valueChangedSignal.emit(prop, data.val)

    def setConstraint(self, prop, constraint):
        """
        sets the given property's constraining rectangle to constraint.
        When setting the constraint, the current value is adjusted if necessary
        (ensuring that the current rectangle value is inside the constraint).
        In order to reset the constraint pass a null QRect value.
        """
        if not prop in self.values.keys():
            return

        data = self.values[prop]
        new_constraint = constraint.normalized()

        if data.constraint == new_constraint:
            return

        old_val = data.val
        data.cosntraint = new_constraint

        if not data.constraint.isNull() and not data.constraint.contains(old_val):
            r1 = data.constraint
            r2 = data.val

            if r2.width() > r1.width():
                r2.setWidth(r1.width())

            if r2.height() > r1.height():
                r2.setHeight(r1.height())

            if r2.left() < r1.left():
                r2.moveLeft(r1.left())
            elif r2.right() > r1.right():
                r2.moveRight(r1.right())

            if r2.top() < r1.top():
                r2.moveTop(r1.top())
            elif r2.bottom() > r1.bottom():
                r2.moveBottom(r1.bottom())

            data.val = r2

        self.values[prop] = data
        self.constraintChangedSignal.emit(prop, data.constraint)

        self.setConstraintWithValue(prop, data.constraint, data.val)

        if data.val == old_val:
            return

        self.propertyChangedSignal.emit(prop)
        self.valueChangedSignal.emit(prop, data.val)

    def setDecimals(self, prop, precision):
        """
        Sets the precision of the given property to precision.
        The valid decimal range is 0~13.
        The default is 4.
        """
        if not prop in self.values.keys():
            return

        data = self.values[prop]

        if precision > 13:
            precision = 13
        elif precision < 0:
            precision = 0

        if data.decimals == precision:
            return

        data.decimals = precision

        self.double_prop_mgr.setDecimals(self.prop_to_x[property], precision)
        self.double_prop_mgr.setDecimals(self.prop_to_y[property], precision)
        self.double_prop_mgr.setDecimals(self.prop_to_w[property], precision)
        self.double_prop_mgr.setDecimals(self.prop_to_h[property], precision)

        self.values[property] = data

        self.decimalsChangedSignal.emit(property, data.decimals)

    def setSingleStep(self, prop, step):
        """
        Sets the single step of the given property to step.
        """
        if not prop in self.values.keys():
            return

        data = self.values[prop]

        if data.single_step == step:
            return

        data.single_step = step

        self.double_prop_mgr.setSingleStep(self.prop_to_x[prop], step)
        self.double_prop_mgr.setSingleStep(self.prop_to_y[prop], step)
        self.double_prop_mgr.setSingleStep(self.prop_to_w[prop], step)
        self.double_prop_mgr.setSingleStep(self.prop_to_h[prop], step)

    def initializeProperty(self, prop):
        """
        Reimplementation
        """
        self.values[prop] = QtRectFPropertyManager.Data()

        prop_x = self.double_prop_mgr.addProperty()
        prop_x.setPropertyName("X")
        self.double_prop_mgr.setDecimals(prop_x, self.decimals(prop))
        self.double_prop_mgr.setValue(prop_x, self.values[prop].val.x())
        self.prop_to_x[prop] = prop_x
        self.x_to_prop[prop_x] = prop
        prop.addSubProperty(prop_x)

        prop_y = self.double_prop_mgr.addProperty()
        prop_y.setPropertyName("Y")
        self.double_prop_mgr.setDecimals(prop_y, self.decimals(prop))
        self.double_prop_mgr.setValue(prop_y, self.values[prop].val.y())
        self.prop_to_y[prop] = prop_y
        self.y_to_prop[prop_y] = prop
        prop.addSubProperty(prop_y)

        prop_width = self.double_prop_mgr.addProperty()
        prop_width.setPropertyName("Width")
        self.double_prop_mgr.setDecimals(prop_width, self.decimals(prop))
        self.double_prop_mgr.setValue(prop_width, self.values[prop].val.width())
        self.double_prop_mgr.setMinimum(prop_width, 0)
        self.prop_to_w[prop] = prop_width
        self.w_to_prop[prop_width] = prop
        prop.addSubProperty(prop_width)

        prop_height = self.double_prop_mgr.addProperty()
        prop_height.setPropertyName("Height")
        self.double_prop_mgr.setDecimals(prop_height, self.decimals(prop))
        self.double_prop_mgr.setValue(prop_height, self.values[prop].val.height())
        self.double_prop_mgr.setMinimum(prop_height, 0)
        self.prop_to_h[prop] = prop_height
        self.h_to_prop[prop_height] = prop
        prop.addSubProperty(prop_height)

    def uninitializeProperty(self, prop):
        """
        Reimplementation
        """
        prop_x = self.prop_to_x[prop]
        if prop_x:
            self.x_to_prop.remove(prop_x)
            del prop_x
        self.prop_to_x.remove(prop)

        prop_y = self.prop_to_y[prop]
        if prop_y:
            self.y_to_prop.remove(prop_y)
            del prop_y
        self.prop_to_y.remove(prop)

        prop_width = self.prop_to_w[prop]
        if prop_width:
            self.w_to_prop.remove(prop_width)
            del prop_width
        self.prop_to_w.remove(prop)

        prop_height = self.prop_to_h[prop]
        if prop_height:
            self.h_to_prop.remove(prop_height)
            del prop_height
        self.prop_to_h.remove(prop)

        self.values.remove(prop)

    def slotDoubleChanged(self, prop, value):
        prop_x = self.x_to_prop.get(prop, 0)
        if prop_x:
            r = QRectF(self.values[prop_x].val)
            r.moveLeft(value)
            self.setValue(prop_x, r)
        else:
            prop_y = self.y_to_prop.get(prop, 0)  # 0을 넣냐 마냐
            if prop_y:
                r = QRectF(self.values[prop_y].val)
                r.moveTop(value)
                self.setValue(prop_y, r)
            else:
                prop_width = self.w_to_prop.get(prop, 0)
                if prop_width:
                    data = self.values[prop_width]
                    r = QRectF(data.val)
                    r.setWidth(value)
                    if not data.constraint.isNull() and data.constraint.x() + data.constraint.width() < r.x() + r.width():
                        r.moveLeft(data.constraint.left() + data.constraint.width() - r.width())

                    self.setValue(prop_width, r)
                else:
                    prop_height = self.h_to_prop.get(prop, 0)
                    if prop_height:
                        data = self.values[prop_height]
                        r = QRectF(data.val)
                        r.setHeight(value)
                        if not data.constraint.isNull() and data.constraint.y() + data.constraint.height() < r.y() + r.height():
                            r.moveTop(data.constraint.top() + data.constraint.height() - r.height())

                        self.setValue(prop_height, r)

    def slotPropertyDestroyed(self, prop):
        prop_x = self.x_to_prop.get(prop, 0)
        if prop_x:
            self.prop_to_x[prop_x] = 0
            self.x_to_prop.remove(prop)
        else:
            prop_y = self.y_to_prop.get(prop, 0)
            if prop_y:
                self.prop_to_y[prop_y] = 0
                self.y_to_prop.remove(prop)
            else:
                prop_width = self.w_to_prop.get(prop, 0)
                if prop_width:
                    self.prop_to_w[prop_width] = 0
                    self.w_to_prop.remove(prop)
                else:
                    prop_height = self.h_to_prop.get(prop, 0)
                    if prop_height:
                        self.prop_to_h[prop_height] = 0
                        self.h_to_prop.remove(prop)

    def setConstraintWithValue(self, prop, constraint, val):
        isNull = constraint.isNull()
        if isNull:
            left    = INT_MIN
            right   = INT_MAX
            top     = INT_MIN
            bottom  = INT_MAX
            width   = INT_MAX
            height  = INT_MAX
        else:
            left    = constraint.left()
            right   = constraint.left() + constraint.width()
            top     = constraint.top()
            bottom  = constraint.top() + constraint.height()
            width   = constraint.width()
            height  = constraint.height()

        self.double_prop_mgr.setRange(self.prop_to_x[prop], left, right)
        self.double_prop_mgr.setRange(self.prop_to_y[prop], top, bottom)
        self.double_prop_mgr.setRange(self.prop_to_w[prop], 0, width)
        self.double_prop_mgr.setRange(self.prop_to_h[prop], 0, height)

        self.double_prop_mgr.setValue(self.prop_to_x[prop], val.x())
        self.double_prop_mgr.setValue(self.prop_to_y[prop], val.y())
        self.double_prop_mgr.setValue(self.prop_to_w[prop], val.width())
        self.double_prop_mgr.setValue(self.prop_to_h[prop], val.height())


#####################################################################################
#
#   class   QtSizePropertyManager
#
#   brief   The QtSizePropertyManager provides and manages QSize properties.
#
#   A size property has nested width and height subproperties.
#   The top-level property's value can be retrieved using the value() function,
#   and set using the setValue() slot.
#
#   The subproperties are created by a QtIntPropertyManager object. This
#   manager can be retrieved using the subIntPropertyManager() function. In
#   order to provide editing widgets for the subproperties in a
#   property browser widget, this manager must be associated with an
#   editor factory.
#
#   A size property also has a range of valid values defined by a
#   minimum size and a maximum size. These sizes can be retrieved
#   using the minimum() and the maximum() functions, and set using the
#   setMinimum() and setMaximum() slots. Alternatively, the range can
#   be defined in one go using the setRange() slot.
#
#   In addition, QtSizePropertyManager provides the valueChanged() signal
#   which is emitted whenever a property created by this manager
#   changes, and the rangeChanged() signal which is emitted whenever
#   such a property changes its range of valid sizes.
#
#   = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#   QtSizePropertyManager signal description:
#
#   valueChanged(property, value)
#
#   This signal is emitted whenever a property created by this manager
#   changes its value, passing the property and the new value as parameters.
#
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   rangeChanged(property, min, max)
#
#   This signal is emitted whenever a property created by this manager changes its
#   range of valid sizes, passing the property and the new minimum and maximum sizes.
#
#####################################################################################
class QtSizePropertyManager(QtAbstractPropertyManager):
    # Defines custom signals
    valueChangedSignal = Signal(QtProperty, QSize)
    rangeChangedSignal = Signal(QtProperty, QSize, QSize)

    class Data:
        val = QSize(0, 0)
        min_val = QSize(0, 0)
        max_val = QSize(INT_MAX, INT_MAX)

    def __init__(self, parent=None):
        """
        Creates a manager with the given parent.
        """
        super(QtSizePropertyManager, self).__init__(parent)
        self.values = QMap()
        self.prop_to_w = QMap()
        self.prop_to_h = QMap()
        self.w_to_prop = QMap()
        self.h_to_prop = QMap()
        self.Data = QtSizePropertyManager.Data()

        self.int_prop_mgr = QtIntPropertyManager(self)
        self.int_prop_mgr.valueChangedSignal.connect(self.slotIntChanged)
        self.int_prop_mgr.propertyDestroyedSignal.connect(self.slotPropertyDestroyed)

    def __del__(self):
        """
        Destroys this manager, and all the properties it has created.
        """
        self.clear()

    def subIntPropertyManager(self):
        """
        Returns the manager that creates the nested width and height
        subproperties.

        In order to provide editing widgets for the width and height
        properties in a property browser widget, this manager must be
        associated with an editor factory.
        """
        return self.int_prop_mgr

    def value(self, prop):
        """
        Returns the given property's value.

        If the given property is not managed by this manager, this function
        returns an invalid size.
        """
        return getValue(self.values, prop, QSize())

    def minimum(self, prop):
        """
        Returns the given property's minimum size value.
        """
        return getMinimum(self.values, prop, QSize())

    def maximum(self, prop):
        """
        Returns the given property's maximum size value.
        """
        return getMaximum(self.values, prop, QSize())

    def valueText(self, prop):
        """
        Reimplementation
        """
        if not prop in self.values.keys():
            return

        val = self.values[prop].val

        return "%d x %d" % (val.width(), val.height())

    def setValue(self, prop, val):
        """
        Sets the value of the given property to value.

        If the specified value is not valid according to the given
        property's size range, the value is adjusted to the nearest
        valid value within the size range.
        """
        setValueInRange(self,
                        self.propertyChangedSignal,
                        self.valueChangedSignal,
                        prop,
                        val,
                        self.setValueToManager)

    def setMinimum(self, prop, min_val):
        """
        Sets the minimum size value for the given property to min_val.

        When setting the minimum size value, the maximum and current values are
        adjusted if necessary (ensuring that the size range remains valid and
        that the current value is within the range).
        """
        setBorderValue(self,
                       self.propertyChangedSignal,
                       self.valueChangedSignal,
                       self.rangeChangedSignal,
                       prop,
                       DATA_GETMINVAL,
                       DATA_GETMINVAL,
                       min_val,
                       self.setRangeToManager)

    def setMaximum(self, prop, max_val):
        """
        Sets the maximum size value for the given property to max_val.

        When setting the maximum size value, the minimum and current values are
        adjusted if necessary (ensuring that the size range remains valid and
        that the current value is within the range).
        """
        setBorderValue(self,
                       self.propertyChangedSignal,
                       self.valueChangedSignal,
                       self.rangeChangedSignal,
                       prop,
                       DATA_GETMAXVAL,
                       DATA_GETMAXVAL,
                       max_val,
                       self.setRangeToManager)

    def setRange(self, prop, min_val, max_val):
        """
        Sets the range of valid values.

        This is a conveniecne function defining the range of valid values
        in one go; setting the minimum and maximum vlaues for the given
        property with a single function call.

        When setting a new range, the current value is adjusted if
        necessary 9ensuring that the value remains within the range).
        """
        setBorderValues(self,
                        self.propertyChangedSignal,
                        self.valueChangedSignal,
                        self.rangeChangedSignal,
                        prop,
                        min_val,
                        max_val,
                        self.setRangeToManager)

    def initializeProperty(self, prop):
        """
        Reimplementation
        """
        self.values[prop] = QtSizePropertyManager.Data()

        prop_w = self.int_prop_mgr.addProperty()
        prop_w.setPropertyName("Width")
        self.int_prop_mgr.setValue(prop_w, 0)
        self.int_prop_mgr.setMinimum(prop_w, 0)
        self.prop_to_w[prop] = prop_w
        self.w_to_prop[prop_w] = prop
        prop.addSubProperty(prop_w)

        prop_h = self.int_prop_mgr.addProperty()
        prop_h.setPropertyName("Width")
        self.int_prop_mgr.setValue(prop_h, 0)
        self.int_prop_mgr.setMinimum(prop_h, 0)
        self.prop_to_h[prop] = prop_h
        self.h_to_prop[prop_h] = prop
        prop.addSubProperty(prop_h)

    def uninitializeProperty(self, prop):
        """
        Reimplementation
        """
        prop_w = self.prop_to_w[prop]
        if prop_w:
            self.w_to_prop.remove(prop_w)
            del prop_w
        self.prop_to_w.remove(prop)

        prop_h = self.prop_to_h[prop]
        if prop_h:
            self.h_to_prop.remove(prop_h)
            del prop_h
        self.prop_to_h.remove(prop)

        self.values.remove(prop)

    def slotIntChanged(self, prop, value):
        prop_w = self.w_to_prop.get(prop, 0)
        if prop_w:
            s = copy.copy(self.values[prop_w].val)
            s.setWidth(value)
            self.setValue(prop_w, s)
        else:
            prop_h = self.h_to_prop.get(prop, 0)
            if prop_h:
                s = copy.copy(self.values[prop_h].val)
                s.setHeight(value)
                self.setValue(prop_h, s)

    def slotPropertyDestroyed(self, prop):
        prop_w = self.w_to_prop.get(prop, 0)
        if prop_w:
            self.prop_to_w[prop_w] = 0
            self.w_to_prop.remove(prop)
        else:
            prop_h = self.h_to_prop.get(prop, 0)
            if prop_h:
                self.prop_to_h[prop_h] = 0
                self.h_to_prop.remove(prop)

    def setValueToManager(self, prop, val):
        self.int_prop_mgr.setValue(self.prop_to_w[prop], val.width())
        self.int_prop_mgr.setValue(self.prop_to_h[prop], val.height())

    def setRangeToManager(self, prop, min_val, max_val, val):
        prop_w = self.prop_to_w[prop]
        prop_h = self.prop_to_h[prop]

        self.int_prop_mgr.setRange(prop_w, min_val.width(), max_val.width())
        self.int_prop_mgr.setValue(prop_w, val.width())
        self.int_prop_mgr.setRange(prop_h, min_val.height(), max_val.height())
        self.int_prop_mgr.setValue(prop_h, val.height())


#####################################################################################
#
#   class   QtSizeFPropertyManager
#
#   brief   The QtSizeFPropertyManager provides and manages QSizeF properties.
#
#   A size property has nested width and height subproperties.
#   The top-level property's value can be retrieved using the value() function,
#   and set using the setValue() slot.
#
#   The subproperties are created by a QtDoublePropertyManager object. This
#   manager can be retrieved using the subDoublePropertyManager() function. In
#   order to provide editing widgets for the subproperties in a
#   property browser widget, this manager must be associated with an
#   editor factory.
#
#   A size property also has a range of valid values defined by a
#   minimum size and a maximum size. These sizes can be retrieved
#   using the minimum() and the maximum() functions, and set using the
#   setMinimum() and setMaximum() slots. Alternatively, the range can
#   be defined in one go using the setRange() slot.
#
#   In addition, QtSizeFPropertyManager provides the valueChanged() signal
#   which is emitted whenever a property created by this manager
#   changes, and the rangeChanged() signal which is emitted whenever
#   such a property changes its range of valid sizes.
#
#   = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#   QtSizePropertyManager signal description:
#
#   valueChanged(property, value)
#
#   This signal is emitted whenever a property created by this manager
#   changes its value, passing the property and the new value as parameters.
#
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   rangeChanged(property, min, max)
#
#   This signal is emitted whenever a property created by this manager changes its
#   range of valid sizes, passing the property and the new minimum and maximum sizes.
#
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   decimalsChanged(property, precision)
#
#   This signal is emitted whenever a proeprty created by this manager changes its
#   precision of value, passing the property and the new precision value as pareameters.
#
#####################################################################################
class QtSizeFPropertyManager(QtAbstractPropertyManager):
    # Defines custom signals
    valueChangedSignal      = Signal(QtProperty, QSizeF)
    rangeChangedSignal      = Signal(QtProperty, QSizeF, QSizeF)
    decimalsChangedSignal   = Signal(QtProperty, int)

    class Data:
        val = QSizeF(0, 0)
        min_val = QSizeF(0, 0)
        max_val = QSizeF(INT_MAX, INT_MAX)
        decimals = 4
        single_step = 1.0

    def __init__(self, parent=None):
        """
        Creates a manager with the given parent.
        """
        super(QtSizeFPropertyManager, self).__init__(parent)
        self.values = QMap()
        self.prop_to_w = QMap()
        self.prop_to_h = QMap()
        self.w_to_prop = QMap()
        self.h_to_prop = QMap()
        self.Data = QtSizeFPropertyManager.Data()

        self.double_prop_mgr = QtDoublePropertyManager(self)
        self.double_prop_mgr.valueChangedSignal.connect(self.slotDoubleChanged)
        self.double_prop_mgr.propertyDestroyedSignal.connect(self.slotPropertyDestroyed)

    def __del__(self):
        """
        Destroys this manager, and all the properties it has created.
        """
        self.clear()

    def subDoublePropertyManager(self):
        """
        Returns the manager that creates the nested width and height
        subproperties.

        In order to provide editing widgets for the width and height
        properties in a property browser widget, this manager must be
        associated with an editor factory.
        """
        return self.double_prop_mgr

    def value(self, prop):
        """
        Returns the given property's value.

        If the given property is not managed by this manager, this function
        returns an invalid size.
        """
        return getValue(self.values, prop, QSizeF())

    def minimum(self, prop):
        """
        Returns the given property's minimum size value.
        """
        return getMinimum(self.values, prop, QSizeF())

    def maximum(self, prop):
        """
        Returns the given property's maximum size value.
        """
        return getMaximum(self.values, prop, QSizeF())

    def decimals(self, prop):
        """
        Returns the given property's precision, in decimals.
        """
        return getData(self.values, DATA_DECIMALS, prop, 0)

    def valueText(self, prop):
        """
        Reimplementation
        """
        if not prop in self.values.keys():
            return

        val = self.values[prop].val
        dec = self.values[prop].decimals
        string = "%%.%df x %%.%df" % (dec, dec)

        return string % (val.width(), val.height())

    def setValue(self, prop, val):
        """
        Sets the value of the given property to value.

        If the specified value is not valid according to the given
        property's size range, the value is adjusted to the nearest
        valid value within the size range.
        """
        setValueInRange(self,
                        self.propertyChangedSignal,
                        self.valueChangedSignal,
                        prop,
                        val,
                        self.setValueToManager)

    def setMinimum(self, prop, min_val):
        """
        Sets the minimum size value for the given property to min_val.

        When setting the minimum size value, the maximum and current values are
        adjusted if necessary (ensuring that the size range remains valid and
        that the current value is within the range).
        """
        setBorderValue(self,
                       self.propertyChangedSignal,
                       self.valueChangedSignal,
                       self.rangeChangedSignal,
                       prop,
                       DATA_GETMINVAL,
                       DATA_GETMINVAL,
                       min_val,
                       self.setRangeToManager)

    def setMaximum(self, prop, max_val):
        """
        Sets the maximum size value for the given property to max_val.

        When setting the maximum size value, the minimum and current values are
        adjusted if necessary (ensuring that the size range remains valid and
        that the current value is within the range).
        """
        setBorderValue(self,
                       self.propertyChangedSignal,
                       self.valueChangedSignal,
                       self.rangeChangedSignal,
                       prop,
                       DATA_GETMAXVAL,
                       DATA_GETMAXVAL,
                       max_val,
                       self.setRangeToManager)

    def setDecimals(self, prop, precision):
        """
        Sets the precision of the given property to precision.

        The vlaid decimal range is 0~13. The default is 4.
        """
        if not prop in self.values.keys():
            return

        data = self.values[prop]

        if precision > 13:
            precision = 13
        elif precision < 0:
            precision = 0

        if data.decimals == precision:
            return

        data.decimals = precision

        self.double_prop_mgr.setDecimals(self.prop_to_w[prop], precision)
        self.double_prop_mgr.setDecimals(self.prop_to_h[prop], precision)

        self.values[prop] = data
        self.decimalsChangedSignal.emit(prop, data.decimals)

    def setSingleStep(self, prop, step):
        """
        Sets the isngle step of the given property to step.
        """
        if not prop in self.values.keys():
            return

        data = self.values[prop]

        if data.single_step == step:
            return

        data.single_step = step

        self.double_prop_mgr.setSingleStep(self.prop_to_w[prop], step)
        self.double_prop_mgr.setSingleStep(self.prop_to_h[prop], step)

    def setRange(self, prop, min_val, max_val):
        """
        Sets the range of valid values.

        This is a conveniecne function defining the range of valid values
        in one go; setting the minimum and maximum vlaues for the given
        property with a single function call.

        When setting a new range, the current value is adjusted if
        necessary 9ensuring that the value remains within the range).
        """
        setBorderValues(self,
                        self.propertyChangedSignal,
                        self.valueChangedSignal,
                        self.rangeChangedSignal,
                        prop,
                        min_val,
                        max_val,
                        self.setRangeToManager)

    def initializeProperty(self, prop):
        """
                Reimplementation
                """
        self.values[prop] = QtSizeFPropertyManager.Data()

        prop_w = self.double_prop_mgr.addProperty()
        prop_w.setPropertyName("Width")
        self.double_prop_mgr.setDecimals(prop_w, self.decimals(prop))
        self.double_prop_mgr.setValue(prop_w, 0)
        self.double_prop_mgr.setMinimum(prop_w, 0)
        self.prop_to_w[prop] = prop_w
        self.w_to_prop[prop_w] = prop
        prop.addSubProperty(prop_w)

        prop_h = self.double_prop_mgr.addProperty()
        prop_h.setPropertyName("Width")
        self.double_prop_mgr.setDecimals(prop_h, self.decimals(prop))
        self.double_prop_mgr.setValue(prop_h, 0)
        self.double_prop_mgr.setMinimum(prop_h, 0)
        self.prop_to_h[prop] = prop_h
        self.h_to_prop[prop_h] = prop
        prop.addSubProperty(prop_h)

    def uninitializeProperty(self, prop):
        """
        Reimplementation
        """
        prop_w = self.prop_to_w[prop]
        if prop_w:
            self.w_to_prop.remove(prop_w)
            del prop_w
        self.prop_to_w.remove(prop)

        prop_h = self.prop_to_h[prop]
        if prop_h:
            self.h_to_prop.remove(prop_h)
            del prop_h
        self.prop_to_h.remove(prop)

        self.values.remove(prop)

    def slotDoubleChanged(self, prop, value):
        prop_w = self.w_to_prop.get(prop, 0)
        if prop_w:
            s = copy.copy(self.values[prop_w].val)
            s.setWidth(value)
            self.setValue(prop_w, s)
        else:
            prop_h = self.h_to_prop.get(prop, 0)
            if prop_h:
                s = copy.copy(self.values[prop_h].val)
                s.setHeight(value)
                self.setValue(prop_h, s)

    def slotPropertyDestroyed(self, prop):
        prop_w = self.w_to_prop.get(prop, 0)
        if prop_w:
            self.prop_to_w[prop_w] = 0
            self.w_to_prop.remove(prop)
        else:
            prop_h = self.h_to_prop.get(prop, 0)
            if prop_h:
                self.prop_to_h[prop_h] = 0
                self.h_to_prop.remove(prop)

    def setValueToManager(self, prop, val):
        self.double_prop_mgr.setValue(self.prop_to_w[prop], val.width())
        self.double_prop_mgr.setValue(self.prop_to_h[prop], val.height())

    def setRangeToManager(self, prop, min_val, max_val, val):
        prop_w = self.prop_to_w[prop]
        prop_h = self.prop_to_h[prop]

        self.double_prop_mgr.setRange(prop_w, min_val.width(), max_val.width())
        self.double_prop_mgr.setValue(prop_w, val.width())
        self.double_prop_mgr.setRange(prop_h, min_val.height(), max_val.height())
        self.double_prop_mgr.setValue(prop_h, val.height())


#####################################################################################
#
#   class   QtEnumPropertyManager
#
#   brief   Thie QtEnumPropertyManager provides and manages enum properties.
#
#   Each enum property has an associated list of enum names which can be retrieved
#   using the enumNames() function, and set using the corresponding setEnumnames()
#   function. an enum property's value is represented by an indx in this list, and
#   can be retrieved and set using the value() and setValue() slots respectively.
#
#   each enum value can also have an associated icon. The mapping from values to icons
#   can be set using the setEnumIcons() function and querie with the enumIcons() functions.
#
#   In addition, QtEnumPropertyManager provides the valueChanged(0 signal which is
#   emitted whenever a property created by this manaer changes.
#   The enumNamesChanged() or enumIconsChanged() signal is emitted whenever the list
#   of enum names or icons is altered.
#
#   = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#   QtEnumPropertyManager signal description:
#
#   valueChanged(property, value)
#
#   This signal is emitted whenever a property created by this manager
#   changes its value, passing the property and the new value as parameters.
#
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   enumNamesChanged(property, names)
#
#   This signal is emitted whenever a property created by this manager
#   changes its enum names, passing the property and the new names as parameters.
#
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   enumIconsChanged(proeprty, icons)
#
#   This signal is emitted whenever a property created by this manager changes its
#   enum icons, passing the property and the new mapping of values to icons as parameters.
#
#####################################################################################
class QtEnumPropertyManager(QtAbstractPropertyManager):
    # Defines custom signals
    valueChangedSignal      = Signal(QtProperty, int)
    enumNamesChangedSignal  = Signal(QtProperty, QList)
    enumIconsChangedSignal  = Signal(QtProperty, QMap)

    class Data:
        val = -1
        enum_names = QList()
        enum_icons = QMap()

    def __init__(self, parent=None):
        """
        Creates a manager with the given parent.
        """
        super(QtEnumPropertyManager, self).__init__(parent)
        self.values = QMap()
        self.Data = QtEnumPropertyManager.Data()

    def __del__(self):
        """
        Destroys this manager, and all the properties it has created.
        """
        self.clear()

    def value(self, prop):
        """
        Returns the given property's value which is an index in the list
        returned by enumNames()

        If the given property is not managed by this manager, this function
        returns -1.
        """
        return getValue(self.values, prop, -1)

    def enumNames(self, prop):
        """
        Returns the given property's list of enum names.
        """

        # In case of QtSizePolicyPropertyManager
        data = getData(self.values, DATA_ENUMNAMES, prop, [])
        if type(data) == dict:
            return QList(data.values())
        ###

        return getData(self.values, DATA_ENUMNAMES, prop, [])

    def enumIcons(self, prop):
        """
        Returns the given property's map of enum values to their icons.
        """
        return getData(self.values, DATA_ENUMICONS, prop, {})

    def valueText(self, prop) -> str:
        """
        Reimplementation
        """
        if not prop in self.values.keys():
            return

        data = self.values[prop]
        val = data.val

        # if val >= 0 and val < len(data.enum_names):
        if 0 <= val < len(data.enum_names):
            # In case of QtSizePolicyPropertyManager
            if type(data.enum_names) == dict:
                idx = metaEnumProvider().valueToIndex(val)
                return data.enum_names[idx]
            ###

            return data.enum_names[val]

        return ""

    def valueIcon(self, prop) -> QIcon:
        """
        Reimplementation
        """
        if not prop in self.values.keys():
            return

        data = self.values[prop]
        val = data.val
        return data.enum_icons.value(val)

    def setValue(self, prop, val):
        """
        Sets the value of the given property to value.
        The specified value must be less than the size of the given property's
        enum_names list, and larger than (or equal to) 0.
        """
        if not prop in self.values.keys():
            return

        data = self.values[prop]

        if val >= len(data.enum_names):
            return

        if val < 0 and len(data.enum_names) > 0:
            return

        if val < 0:
            val = -1

        if data.val == val:
            return

        data.val = val
        self.values[prop] = data
        self.propertyChangedSignal.emit(prop)
        self.valueChangedSignal.emit(prop, data.val)

    def setEnumNames(self, prop, names):
        """
        Sets the given property's list of enum names to names.
        The property's current value is reset to 0 indicating the first item of the list.
        If the specified enum_names list is empy, the property's current value is set to -1.
        """
        if not prop in self.values.keys():
            return

        data = self.values[prop]

        if data.enum_names == names:
            return

        data.enum_names = names
        data.val = -1

        if len(names) > 0:
            data.val = 0

        self.values[prop] = data
        self.enumNamesChangedSignal.emit(prop, data.enum_names)
        self.propertyChangedSignal.emit(prop)
        self.valueChangedSignal.emit(prop, data.val)

    def setEnumIcons(self, prop, icons):
        """
        Sets the given property's map of enum values to their icons to icons.
        Each enum value can have associated icon.
        This association is represented with passed enum_icons map.
        """
        if not prop in self.values.keys():
            return

        self.values[prop].enum_icons = icons

        self.enumIconsChangedSignal.emit(prop, self.values[prop].enum_icons)
        self.propertyChangedSignal.emit(prop)

    def initializeProperty(self, prop):
        """
        Reimplementation
        """
        self.values[prop] = QtEnumPropertyManager.Data()

    def uninitializeProperty(self, prop):
        """
        Reimplementation
        """
        self.values.remove(prop)


#####################################################################################
#
#   class   QtSizePolicyPropertyManager
#
#   brief   The QtSizePolicyPropertyManager provides and manages QSizePolicy properties.
#
#   A size policy property has nested horizontalPolicy, verticalPolicy, horizontalStretch
#   and verticalStretch subproperties. The top-level property's value can be retrieved
#   using the value() function, and set using the setValue() slot.
#
#   The subproperties are created by QtIntPropertyManager and QtEnumPropertyManager
#   objects. These managers can be retrieved using the subIntPropertyManager()
#   and subEnumPropertyManager() functions respectively. In order to provide editing
#   widgets for the subproperties in a property browser widget, these managers
#   must be associated with editor factories.
#
#   In addition, QtSizePolicyPropertyManager provides the valueChanged() signal which
#   is emitted whenever a property created by this manager changes.
#
#   = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#   QtSizePolicyPropertyManager signal description:
#
#   valueChanged(property, value)
#
#   This signal is emitted whenever a property created by this manager
#   changes its value, passing a pointer to the \a property and the
#   new \a value as parameters.
#
#####################################################################################
class QtSizePolicyPropertyManager(QtAbstractPropertyManager):
    # Defines custom signal
    valueChangedSignal = Signal(QtProperty, QSizePolicy)

    def __init__(self, parent=None):
        """
        Creates a manager with the given parent.
        """
        super(QtSizePolicyPropertyManager, self).__init__(parent)
        self.values = QMap()
        self.prop_to_hpolicy = QMap()
        self.prop_to_hstretch = QMap()
        self.prop_to_vpolicy = QMap()
        self.prop_to_vstretch = QMap()
        self.hpolicy_to_prop = QMap()
        self.hstretch_to_prop = QMap()
        self.vpolicy_to_prop = QMap()
        self.vstretch_to_prop = QMap()

        self.int_prop_mgr = QtIntPropertyManager(self)
        self.int_prop_mgr.valueChangedSignal.connect(self.slotIntChanged)
        self.int_prop_mgr.propertyDestroyedSignal.connect(self.slotPropertyDestroyed)
        self.enum_prop_mgr = QtEnumPropertyManager(self)
        self.enum_prop_mgr.valueChangedSignal.connect(self.slotEnumChanged)
        self.enum_prop_mgr.propertyDestroyedSignal.connect(self.slotPropertyDestroyed)

    def __del__(self):
        """
        Destroys this manager, and all the properties it has created.
        """
        self.clear()

    def subIntPropertyManager(self):
        """
        Returns the manager that creates the nested horizontalStretch and
        verticalStretch subproperties.

        In order to provide editing widgets for the mentioned subproperties
        in an property browser widget, this manager must be associated with
        an editor factory.
        """
        return self.int_prop_mgr

    def subEnumPropertyManager(self):
        """
        Returns the manager that created the nested horizontalPolicy and
        verticalPolicy subproperties.

        In order to provide editing widgets for the mentioned subproperties
        in an property browser widget, this manager must be associated with
        an editor factory.
        """
        return self.enum_prop_mgr

    def value(self, prop):
        """
        Returns the given property's value.

        If the given property is not managed by this manager, this
        """
        return self.values.get(prop, QSizePolicy())

    def valueText(self, prop) -> str:
        """
        Reimplementation
        """
        if not prop in self.values.keys():
            return ""

        sp = self.values[prop]
        mep = metaEnumProvider()
        h_index = mep.sizePolicyToIndex(sp.horizontalPolicy())
        v_index = mep.sizePolicyToIndex(sp.verticalPolicy())

        if h_index != -1:
            h_policy = mep.policyEnumValueNames()[sp.horizontalPolicy()]
        else:
            h_policy = "Invalid"

        if v_index != -1:
            v_policy = mep.policyEnumValueNames()[sp.verticalPolicy()]
        else:
            v_policy = "Invalid"

        pl_names = mep.policyEnumValueNames()
        h_policy = pl_names.get(sp.horizontalPolicy(), 0)
        v_policy = pl_names.get(sp.verticalPolicy(), 0)

        string = "[%s, %s, %d, %d]" % (h_policy, v_policy, sp.horizontalStretch(), sp.verticalStretch())
        return string

    def setValue(self, prop, val):
        """
        Sets the value of the given property to value.
        Nested properties are updated automatically.
        """
        if not prop in self.values.keys():
            return

        # if self.values[prop] == val:
        #     return

        self.values[prop] = val
        self.enum_prop_mgr.setValue(self.prop_to_hpolicy[prop],
                                      metaEnumProvider().sizePolicyToIndex(val.horizontalPolicy()))
        self.enum_prop_mgr.setValue(self.prop_to_vpolicy[prop],
                                      metaEnumProvider().sizePolicyToIndex(val.verticalPolicy()))
        self.int_prop_mgr.setValue(self.prop_to_hstretch[prop], val.horizontalStretch())
        self.int_prop_mgr.setValue(self.prop_to_vstretch[prop], val.verticalStretch())

        self.propertyChangedSignal.emit(prop)
        self.valueChangedSignal.emit(prop, val)

    def initializeProperty(self, prop):
        """
        Reimplementation
        """
        val = QSizePolicy()
        self.values[prop] = val

        prop_hpolicy = self.enum_prop_mgr.addProperty()
        prop_hpolicy.setPropertyName("Horizontal Policy")
        self.enum_prop_mgr.setEnumNames(prop_hpolicy, metaEnumProvider().policyEnumValueNames())
        self.enum_prop_mgr.setValue(prop_hpolicy, metaEnumProvider().sizePolicyToIndex(val.horizontalPolicy()))
        self.prop_to_hpolicy[prop] = prop_hpolicy
        self.hpolicy_to_prop[prop_hpolicy] = prop
        prop.addSubProperty(prop_hpolicy)

        prop_vpolicy = self.enum_prop_mgr.addProperty()
        prop_vpolicy.setPropertyName("Vertical Policy")
        self.enum_prop_mgr.setEnumNames(prop_vpolicy, metaEnumProvider().policyEnumValueNames())
        self.enum_prop_mgr.setValue(prop_vpolicy, metaEnumProvider().sizePolicyToIndex(val.verticalPolicy()))
        self.prop_to_vpolicy[prop] = prop_vpolicy
        self.vpolicy_to_prop[prop_vpolicy] = prop
        prop.addSubProperty(prop_vpolicy)

        prop_hstretch = self.int_prop_mgr.addProperty()
        prop_hstretch.setPropertyName("Horizontal Stretch")
        self.int_prop_mgr.setValue(prop_hstretch, val.horizontalStretch())
        self.int_prop_mgr.setRange(prop_hstretch, 0, 0xff)
        self.prop_to_hstretch[prop] = prop_hstretch
        self.hstretch_to_prop[prop_hstretch] = prop
        prop.addSubProperty(prop_hstretch)

        prop_vstretch = self.int_prop_mgr.addProperty()
        prop_vstretch.setPropertyName("Vertical Stretch")
        self.int_prop_mgr.setValue(prop_vstretch, val.verticalStretch())
        self.int_prop_mgr.setRange(prop_vstretch, 0, 0xff)
        self.prop_to_vstretch[prop] = prop_vstretch
        self.vstretch_to_prop[prop_vstretch] = prop
        prop.addSubProperty(prop_vstretch)

    def uninitializeProperty(self, prop):
        """
        Reimplementation
        """
        prop_hpolicy = self.prop_to_hpolicy[prop]
        if prop_hpolicy:
            self.hpolicy_to_prop.remove(prop_hpolicy)
            del prop_hpolicy

        self.prop_to_hpolicy.remove(prop)

        prop_vpolicy = self.prop_to_vpolicy[prop]
        if prop_vpolicy:
            self.vpolicy_to_prop.remove(prop_vpolicy)
            del prop_vpolicy

        self.prop_to_vpolicy.remove(prop)

        prop_hstretch = self.prop_to_hstretch[prop]
        if prop_hstretch:
            self.hstretch_to_prop.remove(prop_hstretch)
            del prop_hstretch

        self.prop_to_hstretch.remove(prop)

        prop_vstretch = self.prop_to_vstretch[prop]
        if prop_vstretch:
            self.vstretch_to_prop.remove(prop_vstretch)
            del prop_vstretch

        self.prop_to_vstretch.remove(prop)

        self.values.remove(prop)

    def slotIntChanged(self, prop, value):
        prop_hstretch = self.hstretch_to_prop.get(prop, 0)
        if prop_hstretch:
            sp = self.values[prop_hstretch]
            # sp = QSizePolicy(self.values[prop_hstretch])
            sp.setHorizontalStretch(value)
            self.setValue(prop_hstretch, sp)
        else:
            prop_vstretch = self.vstretch_to_prop.get(prop, 0)
            if prop_vstretch:
                sp = self.values[prop_vstretch]
                # sp = QSizePolicy(self.values[prop_vstretch])
                sp.setVerticalStretch(value)
                self.setValue(prop_vstretch, sp)

    def slotEnumChanged(self, prop, value):
        prop_hpolicy = self.hpolicy_to_prop.get(prop, 0)
        if prop_hpolicy:
            sp = self.values[prop_hpolicy]
            sp.setHorizontalPolicy(metaEnumProvider().indexToSizePolicy(value))
            self.setValue(prop_hpolicy, sp)
        else:
            prop_vpolicy = self.vpolicy_to_prop.get(prop, 0)
            if prop_vpolicy:
                sp = self.values[prop_vpolicy]
                sp.setVerticalPolicy(metaEnumProvider().indexToSizePolicy(value))
                self.setValue(prop_vpolicy, sp)

    def slotPropertyDestroyed(self, prop):
        prop_hstretch = self.hstretch_to_prop.get(prop, 0)
        if prop_hstretch:
            self.prop_to_hstretch[prop_hstretch] = 0
            self.hstretch_to_prop.remove(prop)
        else:
            prop_vstretch = self.vstretch_to_prop.get(prop, 0)
            if prop_vstretch:
                self.prop_to_vstretch[prop_vstretch] = 0
                self.vstretch_to_prop.remove(prop)
            else:
                prop_hpolicy = self.hpolicy_to_prop.get(prop, 0)
                if prop_hpolicy:
                    self.prop_to_hpolicy[prop_hpolicy] = 0
                    self.hpolicy_to_prop.remove(prop)
                else:
                    prop_vpolicy = self.vpolicy_to_prop.get(prop, 0)
                    if prop_vpolicy:
                        self.prop_to_vpolicy[prop_vpolicy] = 0
                        self.vpolicy_to_prop.remove(prop)


#####################################################################################
#
#   class QtFlagPropertyManager
#
#   brief The QtFlagPropertyManager provides and manages flag properties.
#
#   Each flag property has an associated list of flag names which can be retrieved
#   using the flagNames() function, and set using the corresponding 
#   setFlagNames() function.
#
#   The flag manager provides properties with nested boolean subproperties 
#   representing each flag, i.e. a flag property's value is the binary combination of 
#   the subproperties' value. A property's value can be retrieved and set using
#   the value() and setValue() slots respectively. The combination of flags is 
#   represented by single int value - that's why it's possible to store up to 
#   32 independent flags in one flag property.
#
#   The subproperties are created by a QtBoolPropertyManager object. This manager 
#   can be retrieved using the subBoolPropertyManager() function. In order to 
#   provide editing widgets for the subproperties in a property browser widget, 
#   this manager must be associated with an editor factory.
#
#   In addition, QtFlagPropertyManager provides the valueChanged() signal which is 
#   emitted whenever a property created by this manager chagnes, and 
#   he flagNamesChanged() signal which emitted whenever the list of flag names 
#   is altered.
#
#   = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#   QtFlagPropertyManager signal description:
#
#   valueChanged(property, value)
#   
#   This signal is emitted whenever a property created by this manager changes tis value,
#   passing the property and the new value as parameters.
#
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   flagNamesChanged(property, names)
#
#   This signal is emitted whenever a property created by this manager changes its
#   flag names, passing the property and the new names as pareameters.
#
#####################################################################################
class QtFlagPropertyManager(QtAbstractPropertyManager):
    # Defines custom signals
    valueChangedSignal      = Signal(QtProperty, int)
    flagNamesChangedSignal  = Signal(QtProperty, QList)

    class Data:
        val = -1
        flag_names = QList()

    def __init__(self, parent=None) -> None:
        """
        Creates a manager with the given parent.
        """
        super().__init__(parent=parent)
        self.values = QMap()
        self.prop_to_flags = QMapList()
        self.flags_to_prop = QMap()
        self.data = QtFlagPropertyManager.Data()

        self.bool_prop_mgr = QtBoolPropertyManager(self)
        self.bool_prop_mgr.valueChangedSignal.connect(self.slotBoolChanged)
        self.bool_prop_mgr.propertyDestroyedSignal.connect(self.slotPropertyDestroyed)

    def __del__(self):
        """
        Destroys this manager, and all the properties it has created.
        """
        self.clear()

    def subBoolPropertyManager(self):
        """
        Returns the manager that produces the nested boolean subproperties
        representing each flag.

        In order to provide editing widgets for the subproperties in a
        property browser widget, this manager must be associated with an editor factory.
        """
        return self.bool_prop_mgr

    def value(self, prop):
        """
        Returns this given property's value.

        If the given property is not managed by this manager, this function returns 0.
        """
        return getValue(self.values, prop, 0)

    def flagNames(self, prop):
        """
        Returns the given property's list of flag names.
        """
        return getData(self.values, DATA_FLAGNAMES, prop, [])

    def valueText(self, prop) -> str:
        """
        Reimplementation
        """
        if not prop in self.values.keys():
            return ""

        data = self.values[prop]

        s = ""
        level = 0
        bar = " | "
        for it in data.flag_names:
            if data.val & (1 << level):
                if s != "":
                    s += bar
                
                s += it

            level += 1
            
        return s

    def setValue(self, prop, val):
        """
        Sets the value of the given property to value.
        Nestd properties are updated automatically.

        The specified value must be less than the binary combination of
        the property's flagNames() list size (i.e. less than 2^n, where n 
        is the size of the list) and larger than (or equal to) 0.
        """
        if not prop in self.values.keys():
            return

        data = self.values[prop]
        if data.val == val:
            return

        if val > (1 << len(data.flag_names)) - 1:
            return
        
        if val < 0:
            return

        data.val = val
        self.values[prop] = data

        level = 0
        for p in self.prop_to_flags[prop]:
            if p:
                self.bool_prop_mgr.setValue(p, val & (1 << level))
            level += 1

        self.propertyChangedSignal.emit(prop)
        self.valueChangedSignal.emit(prop, data.val)

    def slotBoolChanged(self, prop, value):
        p = self.flags_to_prop.get(prop, 0)
        if p == 0:
            return
        
        level = 0
        for a in self.prop_to_flags[p]:
            if a == prop:
                v = copy.copy(self.values[p].val)

                if value:
                    v |= (1 << level)
                else:
                    v &= ~(1 << level)

                self.setValue(p, v)
                return

            level += 1

    def setFlagNames(self, prop, flag_names):
        if not prop in self.values.keys():
            return

        data = self.values[prop]
        if data.flag_names == flag_names:
            return

        data.flag_names = flag_names
        data.val = 0

        self.values[prop] = data

        for p in self.prop_to_flags[prop]:
            if p:
                del p

        self.prop_to_flags[prop].clear()

        for flag_name in flag_names:
            p = self.bool_prop_mgr.addProperty()
            p.setPropertyName(flag_name)
            prop.addSubProperty(p)

            self.prop_to_flags[prop].append(p)
            self.flags_to_prop[p] = prop

        self.flagNamesChangedSignal.emit(prop, data.flag_names)
        self.propertyChangedSignal.emit(prop)
        self.valueChangedSignal.emit(prop, data.val)

    def initializeProperty(self, prop):
        """
        Reimplementation
        """
        self.values[prop] = QtFlagPropertyManager.Data()
        self.prop_to_flags[prop] = QList()

    def uninitializeProperty(self, prop):
        """
        Reimplementation
        """
        for p in self.prop_to_flags[prop]:
            if p:
                del p

        self.prop_to_flags.remove(prop)
        self.values.remove(prop)

    def slotPropertyDestroyed(self, prop):
        flag_prop = self.flags_to_prop.get(prop, 0)
        if flag_prop == 0:
            return

        self.prop_to_flags[flag_prop].replace(self.prop_to_flags[flag_prop].indexOf(prop), 0)
        self.flags_to_prop.remove(prop)


#####################################################################################
#
#   class   QtPointPropertyManager
#
#   brief   The QtPointPropertyManager provides and manages properties.
#
#   a point property has nested x and y subproperties. The top-level property's value
#   cna be retrieved using the value() function, and set using the setValue() function.
#
#   The subproperties are created by a QtIntPropertyManager object. This manager can be
#   retrieved using the subIntPropertyManager() function. In order to provide editing
#   widgets for teh subproperties in a property browser widget, this manager must be
#   associated with an editor factory.
#
#   In addition, QtPointPropertyManager provides the valueChanged() signal which
#   is emitted whenever a property created by this manager changes.
#
#   = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#   QtPointPropertyManager signal description:
#
#   valueChanged(property, value)
#   
#   This signal is emitted whenever a property created by this manager changes tis value,
#   passing the property and the new value as parameters.
#####################################################################################
class QtPointPropertyManager(QtAbstractPropertyManager):
    # Defines custom signals
    valueChangedSignal = Signal(QtProperty, QPoint)

    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        self.values = QMap()
        self.prop_to_x = QMap()
        self.prop_to_y = QMap()
        self.x_to_prop = QMap()
        self.y_to_prop = QMap()

        self.int_prop_mgr = QtIntPropertyManager(self)
        self.int_prop_mgr.valueChangedSignal.connect(self.slotIntChanged)
        self.int_prop_mgr.propertyDestroyedSignal.connect(self.slotPropertyDestroyed)

    def __del__(self):
        """
        Destroys this manager, and all the properties it has created.
        """
        self.clear()

    def subIntPropertyManager(self):
        """
        Returns the manager that produces the nested x and y subproperties.

        In order to provide editing widgets for the subproperties in a
        property browser widget, this manager must be associated with an editor factory.
        """
        return self.int_prop_mgr

    def value(self, prop):
        """
        Returns this given property's value.

        If the given property is not managed by this manager, this function returns 0.
        """
        return self.values.get(prop, QPoint())

    def valueText(self, prop) -> str:
        """
        Reimplementation
        """
        if not prop in self.values.keys():
            return ""

        val = self.values[prop]
        return "(%d, %d)" %(val.x(), val.y())

    def setValue(self, prop, val):
        """
        Sets the value of the given property to value.
        Nested properties are updated automatically.
        """
        if not prop in self.values.keys():
            return

        if self.values[prop] == val:
            return

        self.values[prop] = val
        self.int_prop_mgr.setValue(self.prop_to_x[prop], val.x())
        self.int_prop_mgr.setValue(self.prop_to_y[prop], val.y())

        self.propertyChangedSignal.emit(prop)
        self.valueChangedSignal.emit(prop, val)

    def initializeProperty(self, prop):
        """
        Reimplementation
        """
        self.values[prop] = QPoint(0, 0)

        prop_x = self.int_prop_mgr.addProperty()
        prop_x.setPropertyName("X")
        self.int_prop_mgr.setValue(prop_x, 0)
        self.prop_to_x[prop] = prop_x
        self.x_to_prop[prop_x] = prop
        prop.addSubProperty(prop_x)

        prop_y = self.int_prop_mgr.addProperty()
        prop_y.setPropertyName("Y")
        self.int_prop_mgr.setValue(prop_y, 0)
        self.prop_to_y[prop] = prop_y
        self.y_to_prop[prop_y] = prop
        prop.addSubProperty(prop_y)

    def uninitializeProperty(self, prop):
        """
        Reimplementation
        """
        prop_x = self.prop_to_x[prop]
        if prop_x:
            self.x_to_prop.remove(prop_x)
            del prop_x
        self.prop_to_x.remove(prop)

        prop_y = self.prop_to_y[prop]
        if prop_y:
            self.y_to_prop.remove(prop_y)
            del prop_y
        self.prop_to_y.remove(prop)

        self.values.remove(prop)    
        

    def slotIntChanged(self, prop, value):
        prop_x = self.x_to_prop.get(prop, 0)
        if prop_x:
            p = copy.copy(self.values[prop_x])
            p.setX(value)
            self.setValue(prop_x, p)
        else:
            prop_y = self.y_to_prop.get(prop, 0)
            if prop_y:
                p = copy.copy(self.values[prop_y])
                p.setY(value)
                self.setValue(prop_y, p)

    def slotPropertyDestroyed(self, prop):
        prop_x = self.x_to_prop.get(prop, 0)
        if prop_x:
            self.prop_to_x[prop_x] = 0
            self.x_to_prop.remove(prop)
        else:
            prop_y = self.y_to_prop.get(prop, 0)
            if prop_y:
                self.prop_to_y[prop_y] = 0
                self.y_to_prop.remove(prop)


#####################################################################################
#
#   class   QtPointFPropertyManager
#
#   brief   The QtPointFPropertyManager provides and manages properties.
#
#   a point property has nested x and y subproperties. The top-level property's value
#   cna be retrieved using the value() function, and set using the setValue() function.
#
#   The subproperties are created by a QtDoublePropertyManager object. This manager 
#   can be retrieved using the subIntPropertyManager() function. In order to provide 
#   editing widgets for teh subproperties in a property browser widget, this manager 
#   must be associated with an editor factory.
#
#   In addition, QtPointPropertyManager provides the valueChanged() signal which
#   is emitted whenever a property created by this manager changes.
#
#   = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#   QtPointPropertyManager signal description:
#
#   valueChanged(property, value)
#   
#   This signal is emitted whenever a property created by this manager changes tis value,
#   passing the property and the new value as parameters.
#
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   decimalsChanged(property, precision)
#
#   This signal is emitted whenever a proeprty created by this manager changes its
#   precision of value, passing the property and the new precision value as pareameters.
#
#####################################################################################
class QtPointFPropertyManager(QtAbstractPropertyManager):
    # Defines custom signals
    valueChangedSignal      = Signal(QtProperty, QPointF)
    decimalsChangedSignal   = Signal(QtProperty, int)

    class Data:
        val = QPointF()
        decimals = 4
        single_step = 1.0

    def __init__(self, parent=None) -> None:
        """
        Creates a manager with the given parent.
        """
        super().__init__(parent=parent)
        self.values = QMap()
        self.prop_to_x = QMap()
        self.prop_to_y = QMap()
        self.x_to_prop = QMap()
        self.y_to_prop = QMap()
        self.Data = QtPointFPropertyManager.Data()

        self.double_prop_mgr = QtDoublePropertyManager(self)
        self.double_prop_mgr.valueChangedSignal.connect(self.slotDoubleChanged)
        self.double_prop_mgr.propertyDestroyedSignal.connect(self.slotPropertyDestroyed)

    def __del__(self):
        """
        Destroys this manager, and all the properties it has created.
        """
        self.clear()
    
    def subDoublePropertyManager(self):
        """
        Returns the manager that produces the nested x and y subproperties.

        In order to provide editing widgets for the subproperties in a
        property browser widget, this manager must be associated with an editor factory.
        """
        return self.double_prop_mgr

    def value(self, prop):
        """
        Returns this given property's value.

        If the given property is not managed by this manager, this function returns with coordinates (0, 0).
        """
        return getValue(self.values, prop, QPointF())

    def decimals(self, prop):
        """
        Returns the given property's precision, in dcimals.
        """
        return getData(self.values, DATA_DECIMALS, prop, 0)

    def valueText(self, prop) -> str:
        """
        Reimplementation
        """
        if not prop in self.values.keys():
            return ""
        
        val = self.values[prop].val
        dec = self.values[prop].decimals
        string = "%%.%df, %%.%df" % (dec, dec)
        return string % (val.x(), val.y())

    def setValue(self, prop, val):
        """
        Sets the value of the given property to value.
        Nested properties are updated automatically.
        """
        if not prop in self.values.keys():
            return

        if self.values[prop].val == val:
            return
        
        self.values[prop].val = val
        self.double_prop_mgr.setValue(self.prop_to_x[prop], val.x())
        self.double_prop_mgr.setValue(self.prop_to_y[prop], val.y())

        self.propertyChangedSignal.emit(prop)
        self.valueChangedSignal.emit(prop, val)

    def setDecimals(self, prop, precision):
        """
        Sets the precision of the given property to precision.
        The valid decimal range is 0~13.
        The default is 4.
        """
        if not prop in self.values.keys():
            return
        
        data = self.values[prop]

        if precision > 13:
            precision = 13
        elif precision < 0:
            precision = 0

        if data.decimals == precision:
            return
        
        data.decimals = precision
        self.double_prop_mgr.setDecimals(self.prop_to_x[prop], precision)
        self.double_prop_mgr.setDecimals(self.prop_to_y[prop], precision)

        self.values[prop] = data
        self.decimalsChangedSignal.emit(prop, data.decimals)

    def setSingleStep(self, prop, step):
        """
        Sets the single step of the given property to step.
        """
        if not prop in self.values.keys():
            return
        
        data = self.values[prop]

        if data.single_step == step:
            return

        data.single_step = step

        self.double_prop_mgr.setSingleStep(self.prop_to_x[prop], step)
        self.double_prop_mgr.setSingleStep(self.prop_to_y[prop], step)
        

    def initializeProperty(self, prop):
        """
        Reimplementation
        """
        self.values[prop] = QtPointFPropertyManager.Data()

        prop_x = self.double_prop_mgr.addProperty()
        prop_x.setPropertyName("X")
        self.double_prop_mgr.setDecimals(prop_x, self.decimals(prop))
        self.double_prop_mgr.setValue(prop_x, 0)
        self.prop_to_x[prop] = prop_x
        self.x_to_prop[prop_x] = prop
        prop.addSubProperty(prop_x)

        prop_y = self.double_prop_mgr.addProperty()
        prop_y.setPropertyName("X")
        self.double_prop_mgr.setDecimals(prop_y, self.decimals(prop))
        self.double_prop_mgr.setValue(prop_y, 0)
        self.prop_to_y[prop] = prop_y
        self.y_to_prop[prop_y] = prop
        prop.addSubProperty(prop_y)

    def uninitializeProperty(self, prop):
        """
        Reimplementation
        """
        prop_x = self.prop_to_x[prop]
        if prop_x:
            self.x_to_prop.remove(prop_x)
            del prop_x
        self.prop_to_x.remove(prop)

        prop_y = self.prop_to_y[prop]
        if prop_y:
            self.y_to_prop.remove(prop_y)
            del prop_y
        self.prop_to_y.remove(prop)

        self.values.remove(prop)   


    def slotDoubleChanged(self, prop, value):
        prop_x = self.x_to_prop.get(prop, 0)
        if prop_x:
            p = copy.copy(self.values[prop_x].val)
            p.setX(value)
            self.setValue(prop_x, p)
        else:
            prop_y = self.y_to_prop.get(prop, 0)
            if prop_y:
                p = copy.copy(self.values[prop_y].val)
                p.setY(value)
                self.setValue(prop_y, p)

    def slotPropertyDestroyed(self, prop):
        prop_x = self.x_to_prop.get(prop, 0)
        if prop_x:
            self.prop_to_x[prop_x] = 0
            self.x_to_prop.remove(prop)
        else:
            prop_y = self.y_to_prop.get(prop, 0)
            if prop_y:
                self.prop_to_y[prop_y] = 0
                self.y_to_prop.remove(prop)


#####################################################################################
#
#   class   QtDatePropertyManager
#
#   brief   The QtDatePropertyManager provides and manages QDate properties.
#
#   A date property has a current value, and a range specifying the valid dates. 
#   The range is defined by a minimum and a maximum value.
#
#   The property's values can be retrieved using the minimum(), maximum() and 
#   value() functions, and can be set using the setMinimum(), setMaximum() and 
#   setValue() slots. Alternatively, the range can be defined in one go using 
#   the setRange() slot.
#
#   In addition, QtDatePropertyManager provides the valueChanged() signal
#   which is emitted whenever a property created by this manager
#   changes, and the rangeChanged() signal which is emitted whenever
#   such a property changes its range of valid dates.
#
#   = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#   QtPointPropertyManager signal description:
#
#   valueChanged(property, value)
#   
#   This signal is emitted whenever a property created by this manager changes tis value,
#   passing the property and the new value as parameters.
#
#   - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#   rangeChanged(property, minimum, maximum)
#
#   This signal is emitted whenever a property created by this manager changes its
#   range of valid dates, passing the property and the new minimum and maximum dates.
#
#####################################################################################
class QtDatePropertyManager(QtAbstractPropertyManager):
    # Defines custom signals
    valueChangedSignal = Signal(QtProperty , QDate)
    rangeChangedSignal = Signal(QtProperty , QDate, QDate)

    class Data:
        val = QDate.currentDate()
        min_val = QDate(1752, 9, 14)
        max_val = QDate(7999, 12, 31)

    def __init__(self, parent=None) -> None:
        """
        Creates a manager with the given parent.
        """
        super().__init__(parent)
        self.values = QMap()
        self.Data = QtDatePropertyManager.Data()
        self.format = QLocale().dateFormat(QLocale.ShortFormat)

    def __del__(self):
        """
        Destroys this manager, and all the properties it has created.
        """
        self.clear()
    
    def value(self, prop):
        """
        Returns the given property's value.
        If the given property is not managed by this manager,
        this function returns an invalid date.
        """
        return getValue(self.values, prop, QDate())

    def minimum(self, prop):
        """
        Returns the given property's minimum date.
        """
        return getMinimum(self.values, prop, QDate())
    
    def maximum(self, prop):
        """
        Returns the given property's maximum date.
        """
        return getMaximum(self.values, prop, QDate())

    def valueText(self, prop):
        """
        Reimplementation
        """
        if not prop in self.values.keys():
            return ""

        return self.values[prop].val.toString(self.format)

    def setValue(self, prop, val):
        """
        Sets the value of the given property to value.
        
        If the specified value is not a valid date according to 
        the given property's range, the value is adjusted to 
        the nearest valid value within the range.
        """
        set_subprop_value = 0
        setValueInRange(self, 
                        self.propertyChangedSignal,
                        self.valueChangedSignal, 
                        prop, 
                        val,
                        set_subprop_value)

    def setMinimum(self, prop, min_val):
        """
        Sets the minimum value for the given property to min_val.

        When setting the minimum vaue, the maximum and current values are
        adjusted if necessary (ensuring that the range remains valid and
        that the current value is within in the range).
        """
        setMinimumValue(self,
                        self.propertyChangedSignal,
                        self.valueChangedSignal,
                        self.rangeChangedSignal,
                        prop,
                        min_val)

    def setMaximum(self, prop, max_val):
        """
        Sets the maximum value for the given property to min_val.

        When setting the minimum vaue, the maximum and current values are
        adjusted if necessary (ensuring that the range remains valid and
        that the current value is within in the range).
        """
        setMaximumValue(self,
                        self.propertyChangedSignal,
                        self.valueChangedSignal,
                        self.rangeChangedSignal,
                        prop,
                        max_val)

    def setRange(self, prop, min_val, max_val):
        set_subprop_range = 0
        setBorderValues(self,
                        self.propertyChangedSignal,
                        self.valueChangedSignal,
                        self.rangeChangedSignal,
                        prop,
                        min_val,
                        max_val,
                        set_subprop_range)

    def initializeProperty(self, prop):
        """
        Reimplementation
        """
        self.values[prop] = QtDatePropertyManager.Data()

    def uninitializeProperty(self, prop):
        """
        Reimplementation
        """
        self.values.remove(prop)


#####################################################################################
#
#   class   QtTimePropertyManager
#
#   brief   The QtTimePropertyManager provides and manages QTime properties.
#
#   A time property's value can be retrieved using the value() function, and set
#   using the setValue() slot.
#
#   In addition, QtTimePropertyManager provides the valueChanged() signal which
#   is emitted whenever a property created by this manager changes.
#
#   = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#   QtTimePropertyManager signal description:
#
#   valueChanged(property, value)
#
#   This signal is emitted whenever a property created by this manager changes its value,
#   passing the property and the new value as parameters.
#
#####################################################################################
class QtTimePropertyManager(QtAbstractPropertyManager):
    # Defines custom signal
    valueChangedSignal = Signal(QtProperty, QTime)

    def __init__(self, parent=None) -> None:
        """
        Creates a manager with the given parent.
        """
        super().__init__(parent)
        self.values = QMap()
        self.format = QLocale().timeFormat(QLocale.ShortFormat)

    def __del__(self):
        """
        Destroys this manager, and all the properties it has created.
        """
        self.clear()

    def value(self, prop):
        """
        Returns the given property's value.
        
        If the given property is not managed by this manager,
        this function returns an invalid time object.
        """
        return self.values.get(prop, QTime())

    def valueText(self, prop) -> str:
        """
        Reimplementation
        """
        if not prop in self.values.keys():
            return ""

        return self.values[prop].toString(self.format)

    def setValue(self, prop, val):
        """
        Sets the value of the given property to value.
        """
        setSimpleValue(self.values,
                       self.propertyChangedSignal,
                       self.valueChangedSignal,
                       prop,
                       val)

    def setFormat(self, prop, format):
        """
        Sets the value of the given property to format.
        """
        if not prop in self.values.keys():
            return

        self.format = QLocale().timeFormat(format)

    def initializeProperty(self, prop):
        """
        Reimplementation
        """
        self.values[prop] = QTime.currentTime()

    def uninitializeProperty(self, prop):
        """
        Reimplementation
        """
        self.values.remove(prop)


#####################################################################################
#
#   class   QtDateTimePropertyManager
#
#   brief   The QtDateTimePropertyManager provides and manages QDateTime properties.
#
#   A date and time property has a current value which can be retrieved using
#   the value() function, and set using the setValue() slot. 
#   In addition, QtDateTimePropertyManager provides the valueChanged() signal which 
#   is emitted whenever a property created by this manager changes.
#
#   = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#   QtPointPropertyManager signal description:
#
#   valueChanged(property, value)
#   
#   This signal is emitted whenever a property created by this manager changes tis value,
#   passing the property and the new value as parameters.
#
#####################################################################################
class QtDateTimePropertyManager(QtAbstractPropertyManager):
    # Defines custom signal
    valueChangedSignal = Signal(QtProperty, QDateTime)

    def __init__(self, parent=None) -> None:
        """
        Creates a manager with the given parent.
        """
        super().__init__(parent)
        self.values = QMap()

        # ShortFormat: yyyy-mm-dd
        # LongFormat: yyyy년 mm월 dd일 요일
        self.format = QLocale().dateFormat(QLocale.ShortFormat)
        self.format += ", "
        # ShortFormat: hh:mm
        # LongFormat: hh:mm:ss
        self.format += QLocale().timeFormat(QLocale.ShortFormat)

    def __del__(self):
        """
        Destroys this manager, and all the properties it has created.
        """
        self.clear()

    def value(self, prop):
        """
        Returns the given property's value.
        
        If the given property is not managed by this manager,
        this function returns an invalid QDateTime object.
        """
        return self.values.get(prop, QDateTime())

    def valueText(self, prop) -> str:
        """
        Reimplementation
        """
        return self.values[prop].toString(self.format)

    def setValue(self, prop, val):
        """
        Sets the value of the given property to value.
        """
        setSimpleValue(self.values,
                      self.propertyChangedSignal,
                      self.valueChangedSignal,
                      prop,
                      val)

    def setFormat(self, prop, format):
        """
        Sets the value of the given property to format.
        Date and time are changed.
        """
        if not prop in self.values.keys():
            return
        
        self.format = QLocale().dateFormat(format)
        self.format += ", "
        self.format += QLocale().timeFormat(format)

    def initializeProperty(self, prop):
        """
        Reimplementation
        """
        self.values[prop] = QDateTime.currentDateTime()
        
    def uninitializeProperty(self, prop):
        """
        Reimplementation
        """
        self.values.remove(prop)


#####################################################################################
#
#   class   QtFontPropertyManager
#
#   brief   The QtFontPropertyManager provides and manages QFont properties.
#
#   A font property has nested family, point size, bold, italic, underline, strike out
#   and kerning subproperties. The top-level property's value can be retireved using
#   the value() function, and set using the setValue() slot.
#   
#   The subproperties are created by QtIntPropertyManager, QtEnumPropertyManager and
#   QtBoolPropertyManager object. These managers can be retrieved using the
#   corresponding subIntPropertyManager(), subEnumPropertyManager() and 
#   subBoolPropertyManager() functions. In order to provide editing widgets 
#   for the subproperties in a property browser widget, these managers must be 
#   associated with editor factories.
#
#   In addition, QtFontPropertyManager provides the valueChanged() signal which
#   is emitted whenever a property created by this manager changes.
#
#   = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#   QtIntPropertyManager signal description:
#
#   valueChanged(property, value)
#
#    This signal is emitted whenever a property created by this manager
#    changes its value, passing the property and the new
#    value as parameters.
#
#####################################################################################
class QtFontPropertyManager(QtAbstractPropertyManager):
    # Defines custom signal
    valueChangedSignal = Signal(QtProperty, QFont)

    def __init__(self, parent=None) -> None:
        """
        Creates a manager with the given parent.
        """
        super().__init__(parent)
        self.values = QMap()
        self.family_names = QList()
        self.prop_to_family = QMap()
        self.prop_to_font_size = QMap()
        self.prop_to_bold = QMap()
        self.prop_to_italic = QMap()
        self.prop_to_underline = QMap()
        self.prop_to_strike_out = QMap()
        self.prop_to_kerning = QMap()
        
        self.family_to_prop = QMap()
        self.font_size_to_prop = QMap()
        self.bold_to_prop = QMap()
        self.italic_to_prop = QMap()
        self.underline_to_prop = QMap()
        self.strike_out_to_prop = QMap()
        self.kerning_to_prop = QMap()

        self.setting_value = False
        self.font_database_change_timer = None

        QCoreApplication.instance().fontDatabaseChanged.connect(self.slotFontDatabaseChanged)

        self.int_prop_mgr = QtIntPropertyManager(self)
        self.int_prop_mgr.valueChangedSignal.connect(self.slotIntChanged)
        self.int_prop_mgr.propertyDestroyedSignal.connect(self.slotPropertyDestroyed)

        self.enum_prop_mgr = QtEnumPropertyManager(self)
        self.enum_prop_mgr.valueChangedSignal.connect(self.slotEnumChanged)
        self.enum_prop_mgr.propertyDestroyedSignal.connect(self.slotPropertyDestroyed)
        
        self.bool_prop_mgr = QtBoolPropertyManager(self)
        self.bool_prop_mgr.valueChangedSignal.connect(self.slotBoolChanged)
        self.bool_prop_mgr.propertyDestroyedSignal.connect(self.slotPropertyDestroyed)

    def __del__(self):
        """
        Destroys this manager, and all the properties it has created.
        """
        self.clear()

    def subIntPropertyManager(self):
        """
        Returns the manager that creates the pointSize subproperty.
        
        In order to provide editing widgets for the pointSize property
        in a property browser widget, this manager must be associated 
        with an editor factory.
        """
        return self.int_prop_mgr

    def subEnumPropertyManager(self):
        """
        Returns the manager that creates the family subproperty.
        
        In order to provide editing widgets for the family property
        in a property browser widget, this manager must be associated 
        with an editor factory.
        """
        return self.enum_prop_mgr

    def subBoolPropertyManager(self):
        """
        Returns the manager that creates the bold, italic, underline,
        strikeOut and kerning subproperties.
        
        In order to provide editing widgets for the family property
        in a property browser widget, this manager must be associated 
        with an editor factory.
        """
        return self.bool_prop_mgr

    def value(self, prop):
        """
        Returns the given property's value.
        
        If the given property is not managed by this manager, this function
        returns a font objeect that uses the application's default font.
        """
        return self.values.get(prop, QFont())

    def valueText(self, prop) -> str:
        """
        Reimplementation
        """
        if not prop in self.values.keys():
            return ""

        return fontValueText(self.values[prop])

    def valueIcon(self, prop) -> QIcon:
        """
        Reimplementation
        """
        if not prop in self.values.keys():
            return QIcon()

        return fontValueIcon(self.values[prop])

    def setValue(self, prop, val):
        """
        Sets the value of the given property to value.
        Nested properties are updated automatically.
        """
        if not prop in self.values.keys():
            return

        old_val = self.values[prop]
        if old_val == val:
            return

        self.values[prop] = val

        idx = self.family_names.indexOf(val.family())
        if idx == -1:
            idx = 0

        setting_value = self.setting_value
        self.setting_value = True

        self.enum_prop_mgr.setValue(self.prop_to_family[prop], idx)
        self.enum_prop_mgr.setValue(self.prop_to_font_size[prop], idx)
        self.enum_prop_mgr.setValue(self.prop_to_bold[prop], idx)
        self.enum_prop_mgr.setValue(self.prop_to_italic[prop], idx)
        self.enum_prop_mgr.setValue(self.prop_to_underline[prop], idx)
        self.enum_prop_mgr.setValue(self.prop_to_strike_out[prop], idx)
        self.enum_prop_mgr.setValue(self.prop_to_kerning[prop], idx)

        self.setting_value = setting_value

        self.propertyChangedSignal.emit(prop)
        self.valueChangedSignal.emit(prop, val)

    def initializeProperty(self, prop):
        """
        Reimplementation
        """
        val = QFont()
        self.values[prop] = val

        prop_family = self.enum_prop_mgr.addProperty()
        prop_family.setPropertyName("Family")
        if len(self.family_names) <= 0:
            self.family_names += fontDatabase().families()
        
        self.enum_prop_mgr.setEnumNames(prop_family, self.family_names)
        idx = self.family_names.indexOf(val.family())
        if idx == -1:
            idx = 0
        
        self.enum_prop_mgr.setValue(prop_family, idx)
        self.prop_to_family[prop] = prop_family
        self.family_to_prop[prop_family] = prop
        prop.addSubProperty(prop_family)

        prop_point_size = self.int_prop_mgr.addProperty()
        prop_point_size.setPropertyName("Font size")
        self.int_prop_mgr.setValue(prop_point_size, val.pointSize())
        self.int_prop_mgr.setMinimum(prop_point_size, 1)
        self.prop_to_font_size[prop] = prop_point_size
        self.font_size_to_prop[prop_point_size] = prop
        prop.addSubProperty(prop_point_size)

        prop_bold = self.bool_prop_mgr.addProperty()
        prop_bold.setPropertyName("Bold")
        self.bool_prop_mgr.setValue(prop_bold, val.bold())
        self.prop_to_bold[prop] = prop_bold
        self.bold_to_prop[prop_bold] = prop
        prop.addSubProperty(prop_bold)

        prop_italic = self.bool_prop_mgr.addProperty()
        prop_italic.setPropertyName("Italic")
        self.bool_prop_mgr.setValue(prop_italic, val.italic())
        self.prop_to_italic[prop] = prop_italic
        self.italic_to_prop[prop_italic] = prop
        prop.addSubProperty(prop_italic)

        prop_underline = self.bool_prop_mgr.addProperty()
        prop_underline.setPropertyName("Underline")
        self.bool_prop_mgr.setValue(prop_underline, val.underline())
        self.prop_to_underline[prop] = prop_underline
        self.underline_to_prop[prop_underline] = prop
        prop.addSubProperty(prop_underline)

        prop_strike_out = self.bool_prop_mgr.addProperty()
        prop_strike_out.setPropertyName("Strike_out")
        self.bool_prop_mgr.setValue(prop_strike_out, val.strikeOut())
        self.prop_to_strike_out[prop] = prop_strike_out
        self.strike_out_to_prop[prop_strike_out] = prop
        prop.addSubProperty(prop_strike_out)

        prop_kerning = self.bool_prop_mgr.addProperty()
        prop_kerning.setPropertyName("Kerning")
        self.bool_prop_mgr.setValue(prop_kerning, val.kerning())
        self.prop_to_kerning[prop] = prop_kerning
        self.kerning_to_prop[prop_kerning] = prop
        prop.addSubProperty(prop_kerning)

    def uninitializeProperty(self, prop):
        """
        Reimplementation
        """
        prop_family = self.prop_to_family[prop]
        if prop_family:
            self.family_to_prop.remove(prop_family)
            del prop_family
        self.prop_to_family.remove(prop)

        prop_point_size = self.prop_to_font_size[prop]
        if prop_point_size:
            self.font_size_to_prop.remove(prop_point_size)
            del prop_point_size
        self.prop_to_font_size.remove(prop)

        prop_bold = self.prop_to_bold[prop]
        if prop_bold:
            self.bold_to_prop.remove(prop_bold)
            del prop_bold
        self.prop_to_bold.remove(prop)

        prop_italic = self.prop_to_italic[prop]
        if prop_italic:
            self.italic_to_prop.remove(prop_italic)
            del prop_italic
        self.prop_to_italic.remove(prop)

        prop_underline = self.prop_to_underline[prop]
        if prop_underline:
            self.underline_to_prop.remove(prop_underline)
            del prop_underline
        self.prop_to_underline.remove(prop)

        prop_strike_out = self.prop_to_strike_out[prop]
        if prop_strike_out:
            self.strike_out_to_prop.remove(prop_strike_out)
            del prop_strike_out
        self.prop_to_strike_out.remove(prop)

        prop_kerning = self.prop_to_kerning[prop]
        if prop_kerning:
            self.kerning_to_prop.remove(prop_kerning)
            del prop_kerning
        self.prop_to_kerning.remove(prop)
            

    def slotIntChanged(self, prop, value):
        if self.setting_value:
            return
        
        prop_point_size = self.font_size_to_prop.get(prop, 0)
        if prop_point_size:
            f = QFont(self.values[prop_point_size])
            f.setPointSize(value)
            self.setValue(prop_point_size, f)

    def slotEnumChanged(self, prop, value):
        if self.setting_value:
            return

        prop_family = self.family_to_prop.get(prop, 0)
        if prop_family:
            f = QFont(self.values[prop_family])
            f.setFamily(self.family_names[value])
            self.setValue(prop_family, f)

    def slotBoolChanged(self, prop, value):
        if self.setting_value:
            return

        p = self.bold_to_prop.get(prop, 0)
        if p:
            f = QFont(self.values[p])
            f.setBold(value)
            self.setValue(p, f)
        else:
            p = self.italic_to_prop.get(prop, 0)
            if p:
                f = QFont(self.values[p])
                f.setItalic(value)
                self.setValue(p, f)
            else:
                p = self.underline_to_prop.get(prop, 0)
                if p:
                    f = QFont(self.values[p])
                    f.setUnderline(value)
                    self.setValue(p, f)
                else:
                    p = self.strike_out_to_prop.get(prop, 0)
                    if p:
                        f = QFont(self.values[p])
                        f.setStrikeOut(value)
                        self.setValue(p, f)
                    else:
                        p = self.kerning_to_prop.get(prop, 0)
                        if p:
                            f = QFont(self.values[p])
                            f.setKerning(value)
                            self.setValue(p, f)

    def slotPropertyDestroyed(self, prop):
        p = self.font_size_to_prop.get(prop, 0)
        if p:
            self.prop_to_font_size[p] = 0
            self.font_size_to_prop.remove(prop)
        else:
            p = self.family_to_prop.get(prop, 0)
            if p:
                self.prop_to_family[p] = 0
                self.family_to_prop.remove(prop)
            else:
                p = self.bold_to_prop.get(prop, 0)
                if p:
                    self.prop_to_bold[p] = 0
                    self.bold_to_prop.remove(prop)
                else:
                    p = self.italic_to_prop.get(prop, 0)
                    if p:
                        self.prop_to_italic[p] = 0
                        self.italic_to_prop.remove(prop)
                    else:
                        p = self.underline_to_prop.get(prop, 0)
                        if p:
                            self.prop_to_underline[p] = 0
                            self.underline_to_prop.remove(prop)
                        else:
                            p = self.strike_out_to_prop.get(prop, 0)
                            if p:
                                self.prop_to_strike_out[p] = 0
                                self.strike_out_to_prop.remove(prop)
                            else:
                                p = self.kerning_to_prop.get(prop, 0)
                                if p:
                                    self.prop_to_kerning[p] = 0
                                    self.kerning_to_prop.remove(prop)

    def slotFontDatabaseChanged(self):
        if not self.font_database_change_timer:
            self.font_database_change_timer = QTime(self)
            self.font_database_change_timer.setInterval(0)
            self.font_database_change_timer.setSingleShot(True)
            self.font_database_change_timer.timeout.connect(self.slotFontDatabaseDelayedChange)

        if not self.font_database_change_timer.isActive():
            self.font_database_change_timer.start()

    def slotFontDatabaseDelayedChange(self):
        # Rescan available font names
        old_families = self.family_names
        self.family_names = fontDatabase().families()

        # Adapt all existing properties
        if len(self.prop_to_family) > 0:
            for prop_family in self.prop_to_family:
                old_idx = self.enum_prop_mgr[prop_family]
                new_idx = self.family_names.indexOf(old_families[old_idx])

                if new_idx < 0:
                    new_idx = 0
                
                self.enum_prop_mgr.setEnumNames(prop_family, self.family_names)
                self.enum_prop_mgr.setValue(prop_family, new_idx)


#####################################################################################
#
#   class   QtLocalePropertyManager
#
#   brief   The QtLocalePropertyManager provides and manages properties.
#
#   A locale property has nested language and country subproperties. The top-level
#   property's value can be retrieved using the value() function, and set using
#   setValue() slot.
#
#   The subproperties are created by QtEnumPropertyManager object. These submanager
#   can be retrieved using the subEnumPropertyManager() function. In order to provide
#   editing widgets for the subproperties in a property browser widget, this manager
#   must be associated with editor factory.
#
#   In addition, QtLocalePropertyManager provides the valueChanged() signal which 
#   is emitted whenever a property created by this manager changes.
#
#   = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#   QtLocalePropertyManager signal description:
#
#   This signal is emitted whenever a property created by this manager changes its value,
#   passing the property and the new value as parameters.
#
#####################################################################################
class QtLocalePropertyManager(QtAbstractPropertyManager):
    # Defines custom signal
    valueChangedSignal = Signal(QtProperty, QLocale)

    def __init__(self, parent=None) -> None:
        """
        Creates a manager with given the parent.
        """
        super().__init__(parent)
        self.values = QMap()
        self.prop_to_lang = QMap()
        self.prop_to_country = QMap()
        self.lang_to_prop = QMap()
        self.country_to_prop = QMap()
        
        self.enum_prop_mgr = QtEnumPropertyManager(self)
        self.enum_prop_mgr.valueChangedSignal.connect(self.slotEnumChanged)
        self.enum_prop_mgr.propertyDestroyedSignal.connect(self.slotPropertyDestroyed)

    def __del__(self):
        """
        Destroys this manager, and all the properties it has created.
        """
        self.clear()

    def subEnumPropertyManager(self):
        """
        Returns the manager that creates the ensted language and country subproperties.
        
        In order to provide editing widgets for the mentioned subproperites
        in a property browser widget, this manager must be associated with an editor factory.
        """
        return self.enum_prop_mgr

    def value(self, prop):
        """
        Returns the given property's value.
        
        If the given property is not managed by this manager,
        this function returns the default locale.
        """
        return self.values.get(prop, QLocale())

    def valueText(self, prop):
        """
        Reimplementation
        """
        if not prop in self.values.keys():
            return ""

        loc = self.values[prop]
        lang_idx = 0
        country_idx = 0
        lang_idx, country_idx = metaEnumProvider().localeToIndex(loc.language(), loc.country())
        s = self.tr("%s, %s"%(metaEnumProvider().languageEnumNames()[lang_idx],
                metaEnumProvider().countryEnumNames(loc.language()).at(country_idx)))

        return s

    def setValue(self, prop, val):
        """
        Sets the value of the given property to value. Nested properties are updated automatically.
        """
        if not prop in self.values.keys():
            return

        loc = self.values[prop]
        if (loc == val):
            return

        self.values[prop] = val

        lang_idx = 0
        country_idx = 0
        lang_idx, country_idx = metaEnumProvider().localeToIndex(val.language(), val.country())
        if loc.language() != val.language():
            self.enum_prop_mgr.setValue(self.prop_to_lang[prop], lang_idx)
            self.enum_prop_mgr.setEnumNames(self.prop_to_country[prop], metaEnumProvider().countryEnumNames(val.language()))

        self.enum_prop_mgr.setValue(self.prop_to_country[prop], country_idx)

        self.propertyChangedSignal.emit(prop)
        self.valueChangedSignal.emit(prop, val)

    def initializeProperty(self, prop):
        """
        Reimplementation
        """
        val = QLocale()
        self.values[prop] = val

        lang_idx = 0
        country_idx = 0
        lang_idx, country_idx = metaEnumProvider().localeToIndex(val.language(), val.country())

        prop_lang = self.enum_prop_mgr.addProperty()
        prop_lang.setPropertyName(self.tr("Language"))
        self.enum_prop_mgr.setEnumNames(prop_lang, metaEnumProvider().languageEnumNames())
        self.enum_prop_mgr.setValue(prop_lang, lang_idx)
        self.prop_to_lang[prop] = prop_lang
        self.lang_to_prop[prop_lang] = prop
        prop.addSubProperty(prop_lang)

        prop_country = self.enum_prop_mgr.addProperty()
        prop_country.setPropertyName(self.tr("Country"))
        self.enum_prop_mgr.setEnumNames(prop_country, metaEnumProvider().countryEnumNames(val.language()))
        self.enum_prop_mgr.setValue(prop_country, country_idx)
        self.prop_to_country[prop] = prop_country
        self.country_to_prop[prop_country] = prop
        prop.addSubProperty(prop_country)

    def uninitializeProperty(self, prop):
        """
        Reimplementation
        """
        prop_lang = self.prop_to_lang[prop]
        if prop_lang:
            self.lang_to_prop.remove(prop_lang)
            del prop_lang

        self.prop_to_lang.remove(prop)

        prop_country = self.prop_to_country[prop]
        if prop_country:
            self.country_to_prop.remove(prop_country)
            del prop_country

        self.prop_to_country.remove(prop)

        self.values.remove(prop)

    def slotEnumChanged(self, prop, value):
        prop_lang = self.lang_to_prop.get(prop, 0)
        if prop_lang:
            loc = self.values[prop_lang]
            new_lang = loc.language()
            new_country = loc.country()
            new_lang, c = metaEnumProvider().indexToLocale(value, 0)
            newLoc = QLocale(new_lang, new_country)
            self.setValue(prop_lang, newLoc)
        else:
            prop_country = self.country_to_prop.get(prop, 0)
            if prop_country:
                loc = self.values[prop_country]
                new_lang = loc.language()
                new_country = loc.country()
                new_lang, new_country = metaEnumProvider().indexToLocale(self.enum_prop_mgr.value(self.prop_to_lang[prop_country]), value)
                newLoc = QLocale(new_lang, new_country)
                self.setValue(prop_country, newLoc)

    def slotPropertyDestroyed(self, prop):
        subProp = self.lang_to_prop.get(prop, 0)
        if subProp:
            self.prop_to_lang[subProp] = 0
            self.lang_to_prop.remove(prop)
        else:
            subProp = self.country_to_prop.get(prop, 0)
            if subProp:
                self.prop_to_country[subProp] = 0
                self.country_to_prop.remove(prop)

        self.enum_prop_mgr = QtEnumPropertyManager(self)
        self.enum_prop_mgr.valueChangedSignal.connect(self.slotEnumChanged)
        self.enum_prop_mgr.propertyDestroyedSignal.connect(self.slotPropertyDestroyed)


#####################################################################################
#
#   class   QtKeySequencePropertyManager
#
#   brief   The QtKeySequencePropertyManager
#
#   A key sequence's value can be retrieved using the value() function, and set
#   the using the setValue() slot.
#
#   In addition, QtKeySequencePropertyManager provides the valueChanged() signal
#   which is emitted whenever a property created by this manager changes.
#
#   = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#   QtKeySequencePropertyManager signal description:
#
#   valueChanged(property, value)
#
#   This signal is emitted whenever a property created by this manager changes
#   its value, passing the property and the new value as parameters.
#
#####################################################################################
class QtKeySequencePropertyManager(QtAbstractPropertyManager):
    # Defines custom signal
    valueChangedSignal = Signal(QtProperty, QKeySequence)

    def __init__(self, parent=None) -> None:
        """
        Creates a manager with the given parent.
        """
        super().__init__(parent)
        self.values = QMap()
        self.format = ""

    def __del__(self) -> None:
        """
        Destroys this manager, and all the properties it has created.
        """
        self.clear()

    def value(self, prop):
        """
        Returns the given property's value.
        
        If the given property is not managed by this manager, 
        this function returns an empty QKeySequence object.
        """
        return self.values.get(prop, QKeySequence())

    def valueText(self, prop) -> str:
        """
        Reimplementation
        """
        if not prop in self.values.keys():
            return ""

        return self.values[prop].toString(QKeySequence.NativeText)

    def setValue(self, prop, val):
        """
        Sets the value of the given property to value.
        """
        setSimpleValue(self.values,
                       self.propertyChangedSignal,
                       self.valueChangedSignal,
                       prop,
                       val)

    def initializeProperty(self, prop):
        """
        Reimplementation
        """
        self.values[prop] = QKeySequence()

    def uninitializeProperty(self, prop):
        """
        Reimplementation
        """
        self.values.remove(prop)


#####################################################################################
#
#   class   QtCharPropertyManager
#
#   brief   The QtCharPropertyManager provides and manages QChar properties.
#
#   A char's value can be retrieved using the value() function, and set using 
#   the setValue() slot.
#
#   In addition, QtCharPropertyManager provides the valueChanged() signal
#   which is emitted whenever a property created by this manager
#   changes.
#
#   = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#   QtCharEditorFactory signal description:
#
#   This signal is emitted whenever a property created by this manager chagnes its
#   value, passing the property and the new value as parameters.
#
#####################################################################################
class QtCharPropertyManager(QtAbstractPropertyManager):
    # Defines custom signal
    valueChangedSignal = Signal(QtProperty, str)
    
    def __init__(self, parent):
        """
        Creates a manager with the given parent.
        """
        super(QtCharPropertyManager, self).__init__(parent)
        self.values = QMap()

    def __del__(self) -> None:
        """
        Destroys this manager, and all the properties it has created.
        """
        self.clear()

    def value(self, prop):
        """
        Returns the given property's value.

        If the given property is not managed by this manager,
        this function returns an null QChar object.
        """
        return self.values.get(prop, "")

    def valueText(self, prop):
        """
        Reimplementation
        """
        if not prop in self.values.keys():
            return ""

        char = self.values[prop]
        if char == "":
            return ""
        else:
            return str(char)

    def setValue(self, prop, val):
        """
        Sets the value of the given property to value.
        """
        setSimpleValue(self.values,
                       self.propertyChangedSignal,
                       self.valueChangedSignal,
                       prop,
                       val)

    def initializeProperty(self, prop):
        """
        Reimplementation
        """
        self.values[prop] = ""

    def uninitializeProperty(self, prop):
        """
        Reimplementation
        """
        self.values.remove(prop)


#####################################################################################
#
#   class   QtCursorPropertyManager
#
#   brief   The QtCursorPropertyManager provides and manages QCursor properties.
#
#   A cursor property has a current value which can be retrieved using the value()
#   function, and set using the setValue() slot.
#   In addition, QtCursorPropertyManager provides the valueChanged() signal which
#   is emitted whenever a property created by this manager changes.
#
#   = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = = =
#   QtCursorPropertyManager signal description:
#
#   valueChanged(property, value)
#
#   This signal is emitted whenever a property created by this manager
#   changes its value, passing the property and the new value as parameters.
#
#####################################################################################
g_cursorDatabase = None


def cursorDatabase():
    global g_cursorDatabase
    if not g_cursorDatabase:
        g_cursorDatabase = QtCursorDatabase()

    return g_cursorDatabase


def clearCursorDatabase():
    cursorDatabase().clear()


# Make sure icons are removed as soon as QApplication is destroyed, otherwise,
# handles are leaked on X11.
class CuusorDatabase(QtCursorDatabase):
    def __init__(self):
        super().__init__()
        qAddPostRoutine(clearCursorDatabase)



class QtCursorPropertyManager(QtAbstractPropertyManager):
    # Defines custom signal
    valueChangedSignal = Signal(QtProperty, QCursor)

    def __init__(self, parent=None):
        """
        Creates a manager with the given parent.
        """
        super(QtCursorPropertyManager, self).__init__(parent)
        self.values = QMap()

    def __del__(self):
        """
        Destroys this manager, and all the properties it has created.
        """
        self.clear()

    def value(self, prop):
        """
        Returns the givne property's value.
        
        If the givne property is not managed by this manager,
        this function returns a default QCursor object.
        """
        return self.values.get(prop, QCursor())

    def valueText(self, prop) -> str:
        """
        Reimplementation
        """
        if not prop in self.values.keys():
            return

        return cursorDatabase().cursorToShapeName(self.values[prop])

    def valueIcon(self, prop) -> QIcon:
        """
        Reimplementation
        """
        if not prop in self.values.keys():
            return

        return cursorDatabase().cursorToShapeIcon(self.values[prop])

    def setValue(self, prop, value):
        """
        Sets the value of the given property to value.
        """
        if not prop in self.values.keys():
            return

        if self.values[prop].shape() == value.shape() and value.shaep() != Qt.BitmapCursor:
            return

        self.values[prop] = value

        self.propertyChangedSignal.emit(prop)
        self.valueChangedSignal.emit(prop, value)

    def initializeProperty(self, prop):
        """
        Reimplementation
        """
        self.values[prop] = QCursor()

    def uninitializeProperty(self, prop):
        """
        Reimplementation
        """
        self.values.remove(prop)


#####################################################################################
#
#   class   QtCharPropertyManager
#
#   brief   The QtCharPropertyManager provides and manages QChar properties.
#
#   A char's value can be retrieved using the value()
#   function, and set using the setValue() slot.
#
#   In addition, QtCharPropertyManager provides the valueChanged() signal
#   which is emitted whenever a property created by this manager
#   changes.
#
#####################################################################################
class QtCharPropertyManager(QtAbstractPropertyManager):
    # Defines custom signal
    valueChangedSignal = Signal(QtProperty, str)

    def __init__(self, parent=None) -> None:
        """
        Creates a manager with the given parent.
        """
        super().__init__(parent)
        self.values = QMap()

    def __del__(self) -> None:
        """
        Destroys this manager, and all the properties it has created.
        """
        self.clear()

    def value(self, prop):
        """
        Returns the given property's value.
        
        If the given property is not managed by this manager,
        this function returns an null QChar object.
        """
        return self.values.get(prop, "")

    def valueText(self, prop) -> str:
        """
        Reimplementation
        """
        if not prop in self.values.keys():
            return ""

        char = self.values[prop]
        if char == "":
            return ""
        else:
            return str(char)

    def setValue(self, prop, val):
        """
        Sets the value of the given property to value.
        """
        setSimpleValue(self.values,
                       self.propertyChangedSignal,
                       self.valueChangedSignal,
                       prop,
                       val)

    def initializeProperty(self, prop):
        """
        Reimplementation
        """
        self.values[prop] = ""

    def uninitializeProperty(self, prop):
        """
        Reimplementation
        """
        self.values.remove(prop)
        