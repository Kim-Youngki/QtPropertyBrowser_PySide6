import sys
import os
filePath = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(filePath,'QtProperty'))
sys.path.append(os.path.join(filePath,'libqt5'))

from PySide6.QtCore import QLocale
from PySide6.QtWidgets import QApplication, QWidget, QGridLayout, QLineEdit
from PySide6.QtGui import QIcon
from QtProperty.qtpropertymanager import (
    QtGroupPropertyManager,
    QtStringPropertyManager,
    QtIntPropertyManager,
    QtDoublePropertyManager,
    QtBoolPropertyManager,
    QtColorPropertyManager,
    QtRectPropertyManager,
    QtRectFPropertyManager,
    QtSizePropertyManager,
    QtSizeFPropertyManager,
    QtEnumPropertyManager,
    QtSizePolicyPropertyManager,
    QtFlagPropertyManager,
    QtPointPropertyManager,
    QtPointFPropertyManager,
    QtDatePropertyManager,
    QtTimePropertyManager,
    QtDateTimePropertyManager,
    QtFontPropertyManager,
    QtLocalePropertyManager,
    QtKeySequencePropertyManager,
    QtCursorPropertyManager,
    QtCharPropertyManager
)
from QtProperty.qteditorfactory import (
    QtLineEditFactory,
    QtSpinBoxFactory,
    QtDoubleSpinBoxFactory,
    QtCheckBoxFactory,
    QtColorEditorFactory,
    QtEnumEditorFactory,
    QtSliderFactory,
    QtScrollBarFactory,
    QtDateEditFactory,
    QtTimeEditFactory,
    QtDateTimeEditFactory,
    QtfontEditorFactory,
    QtKeySequenceEditorFactory,
    QtCursorEditorFactory,
    QtCharEditorFactory
)
from QtProperty.qttreepropertybrowser import QtTreePropertyBrowser
from QtProperty.qtgroupboxpropertybrowser import QtGroupBoxPropertyBrowser
from QtProperty.qtbuttonpropertybrowser import QtButtonPropertyBrowser
from libqt5.pyqtcore import QList, QMap

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = QWidget()

    group_mgr = QtGroupPropertyManager(w)
    string_mgr = QtStringPropertyManager(w)
    int_mgr = QtIntPropertyManager(w)
    double_mgr = QtDoublePropertyManager(w)
    bool_mgr = QtBoolPropertyManager(w)
    color_mgr = QtColorPropertyManager(w)
    rect_mgr = QtRectPropertyManager(w)
    rectF_mgr = QtRectFPropertyManager(w)
    size_mgr = QtSizePropertyManager(w)
    sizeF_mgr = QtSizeFPropertyManager(w)
    enum_mgr = QtEnumPropertyManager(w)
    size_policy_mgr = QtSizePolicyPropertyManager(w)
    flag_mgr = QtFlagPropertyManager(w)
    pt_mgr = QtPointPropertyManager(w)
    ptF_mgr = QtPointFPropertyManager(w)
    int_mgr_slider = QtIntPropertyManager(w)
    int_mgr_scroll = QtIntPropertyManager(w)
    date_mgr = QtDatePropertyManager(w)
    time_mgr = QtTimePropertyManager(w)
    date_time_mgr = QtDateTimePropertyManager(w)
    font_mgr = QtFontPropertyManager(w)
    locale_mgr = QtLocalePropertyManager(w)
    key_mgr = QtKeySequencePropertyManager(w)
    cursor_mgr = QtCursorPropertyManager(w)
    char_mgr = QtCharPropertyManager(w)

    item0 = group_mgr.addProperty("QObject")

    item1 = string_mgr.addProperty("string")
    item0.addSubProperty(item1)

    item2 = int_mgr.addProperty("intSpin")
    int_mgr.setRange(item2, 1, 10)
    item0.addSubProperty(item2)

    item3 = double_mgr.addProperty("doubleSpin")
    double_mgr.setRange(item3, -10.0, 10.0)
    double_mgr.setDecimals(item3, 4)
    double_mgr.setSingleStep(item3, 0.1)
    item0.addSubProperty(item3)

    item4 = bool_mgr.addProperty("bool")
    item0.addSubProperty(item4)

    item5 = color_mgr.addProperty("color")
    item0.addSubProperty(item5)

    item6 = rect_mgr.addProperty("rect_int_spin")
    item0.addSubProperty(item6)

    item7 = rectF_mgr.addProperty("reect_double_spin")
    rectF_mgr.setSingleStep(item7, 0.5)
    item0.addSubProperty(item7)

    item8 = size_mgr.addProperty("size_int_spin")
    item0.addSubProperty(item8)

    item9 = sizeF_mgr.addProperty("size_double_spin")
    sizeF_mgr.setSingleStep(item9, 0.3)
    item0.addSubProperty(item9)

    item10 = enum_mgr.addProperty("enum")
    names = QList()
    names.append("up")
    names.append("right")
    names.append("down")
    names.append("left")

    enum_mgr.setEnumNames(item10, names)
    icons = QMap()
    icons[0] = QIcon("./res/up.png")
    icons[1] = QIcon("./res/right.png")
    icons[2] = QIcon("./res/down.png")
    icons[3] = QIcon("./res/left.png")
    enum_mgr.setEnumIcons(item10, icons)
    item0.addSubProperty(item10)

    item11 = size_policy_mgr.addProperty("size_policy")
    item0.addSubProperty(item11)

    item12 = flag_mgr.addProperty("flag")
    flag_names = QList()
    flag_names.append("Flag0")
    flag_names.append("Flag1")
    flag_names.append("Flag2")
    flag_mgr.setFlagNames(item12, flag_names)
    item0.addSubProperty(item12)

    item13 = pt_mgr.addProperty("point")
    item0.addSubProperty(item13)

    item14 = ptF_mgr.addProperty("pointF")
    ptF_mgr.setSingleStep(item14, 0.6)
    item0.addSubProperty(item14)

    item15 = int_mgr_slider.addProperty("int_slider")
    int_mgr_slider.setRange(item15, 0, 50)
    int_mgr_slider.setValue(item15, 33)
    item0.addSubProperty(item15)

    item16 = int_mgr_scroll.addProperty("int_scroll")
    int_mgr_scroll.setRange(item16, 100, 300)
    int_mgr_scroll.setValue(item16, 256)
    item0.addSubProperty(item16)

    item17 = date_mgr.addProperty("date")
    item0.addSubProperty(item17)

    item18 = time_mgr.addProperty("time")
    item0.addSubProperty(item18)

    item19  = date_time_mgr.addProperty("date_time")
    date_time_mgr.setFormat(item19, QLocale.LongFormat)
    item0.addSubProperty(item19)

    item20 = font_mgr.addProperty("font")
    item0.addSubProperty(item20)

    item21 = locale_mgr.addProperty("locale")
    item0.addSubProperty(item21)

    item22 = key_mgr.addProperty("key")
    item0.addSubProperty(item22)

    item23 = cursor_mgr.addProperty("cursor")
    item0.addSubProperty(item23)

    item24 = char_mgr.addProperty("char")
    item0.addSubProperty(item24)

    line_edit_factory = QtLineEditFactory(w)
    spin_box_factory = QtSpinBoxFactory(w)
    double_spin_box_factory = QtDoubleSpinBoxFactory(w)
    check_box_factory = QtCheckBoxFactory(w)
    color_factory = QtColorEditorFactory(w)
    enum_factory = QtEnumEditorFactory(w)
    slider_factory = QtSliderFactory(w)
    scroll_factory = QtScrollBarFactory(w)
    date_factory = QtDateEditFactory(w)
    time_factory = QtTimeEditFactory(w)
    date_time_factory = QtDateTimeEditFactory(w)
    font_factory = QtfontEditorFactory(w)
    key_factory = QtKeySequenceEditorFactory(w)
    cursor_factory = QtCursorEditorFactory(w)
    char_factory = QtCharEditorFactory(w)

    editor = QtTreePropertyBrowser()
    # editor = QtGroupBoxPropertyBrowser()
    # editor = QtButtonPropertyBrowser()    # -> some problem
    editor.setResizeMode(QtTreePropertyBrowser.ResizeToContents)
    editor.setFactoryForManager(string_mgr, line_edit_factory)
    editor.setFactoryForManager(int_mgr, spin_box_factory)
    editor.setFactoryForManager(double_mgr, double_spin_box_factory)
    editor.setFactoryForManager(bool_mgr, check_box_factory)
    editor.setFactoryForManager(color_mgr, color_factory)
    editor.setFactoryForManager(rect_mgr.subIntPropertyManager(), spin_box_factory)
    editor.setFactoryForManager(rectF_mgr.subDoublePropertyManager(), double_spin_box_factory)
    editor.setFactoryForManager(size_mgr.subIntPropertyManager(), spin_box_factory)
    editor.setFactoryForManager(sizeF_mgr.subDoublePropertyManager(), double_spin_box_factory)
    editor.setFactoryForManager(enum_mgr, enum_factory)
    editor.setFactoryForManager(size_policy_mgr.subIntPropertyManager(), spin_box_factory)
    editor.setFactoryForManager(size_policy_mgr.subEnumPropertyManager(), enum_factory)
    editor.setFactoryForManager(flag_mgr.subBoolPropertyManager(), check_box_factory)
    editor.setFactoryForManager(pt_mgr.subIntPropertyManager(), spin_box_factory)
    editor.setFactoryForManager(ptF_mgr.subDoublePropertyManager(), double_spin_box_factory)
    editor.setFactoryForManager(int_mgr_slider, slider_factory)
    editor.setFactoryForManager(int_mgr_scroll, scroll_factory)
    editor.setFactoryForManager(date_mgr, date_factory)
    editor.setFactoryForManager(time_mgr, time_factory)
    editor.setFactoryForManager(date_time_mgr, date_time_factory)
    editor.setFactoryForManager(font_mgr.subIntPropertyManager(), spin_box_factory)
    editor.setFactoryForManager(font_mgr.subBoolPropertyManager(), check_box_factory)
    editor.setFactoryForManager(font_mgr.subEnumPropertyManager(), enum_factory)
    editor.setFactoryForManager(locale_mgr.subEnumPropertyManager(), enum_factory)
    editor.setFactoryForManager(key_mgr, key_factory)
    editor.setFactoryForManager(cursor_mgr, cursor_factory)
    editor.setFactoryForManager(char_mgr, char_factory)

    editor.addProperty(item0)

    # collapse property
    editor.setExpandedByProperty(item5, False)
    # editor.setExpandedByProperty(item6, False)
    # editor.setExpandedByProperty(item7, False)
    # editor.setExpandedByProperty(item8, False)
    # editor.setExpandedByProperty(item9, False)
    # editor.setExpandedByProperty(item11, False)
    # editor.setExpandedByProperty(item13, False)
    # editor.setExpandedByProperty(item14, False)
    # editor.setExpandedByProperty(item20, False)
    

    layout = QGridLayout(w)
    layout.addWidget(editor)

    # w.setFixedSize(500, 600)
    w.resize(500, 700)
    w.show()

    sys.exit(app.exec())
