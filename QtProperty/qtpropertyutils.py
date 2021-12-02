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

from PySide6.QtCore import Qt, QLocale, QRectF
from PySide6.QtWidgets import QSizePolicy
from PySide6.QtGui import QImage, QPainter, QPixmap, QIcon, QFont, QTextOption, QCursor
from libqt5.pyqtcore import QList, QMap, QMapMap


# For QtColorEditWidget #########################################################
def colorValueText(color):
    return "[%d, %d, %d] (%d)" % (color.red(), color.green(), color.blue(), color.alpha())


def brushValuePixmap(brush):
    img = QImage(16, 16, QImage.Format_ARGB32_Premultiplied)
    img.fill(0)

    painter = QPainter(img)
    painter.setCompositionMode(QPainter.CompositionMode_Source)
    painter.fillRect(0, 0, img.width(), img.height(), brush)

    color = brush.color()
    if color.alpha() != 255:  # indicate alpha by an inset
        opaque_brush = brush
        color.setAlpha(255)
        opaque_brush.setColor(color)
        painter.fillRect(img.width() / 4, img.height() / 4,
                         img.width() / 2, img.height() / 2, opaque_brush)

    painter.end()

    return QPixmap.fromImage(img)


def brushValueIcon(brush):
    return QIcon(brushValuePixmap(brush))


# For QtLocalePropertyManager and QtSizePolicyPropertyManager ###################
class QtMetaEnumProvider:
    def __init__(self):
        self.language_enum_names = QList()
        self.country_enum_names = QMap()
        self.index_to_language = QMap()
        self.language_to_index = QMap()
        self.index_to_country = QMapMap()
        self.country_to_index = QMapMap()
        # self.policy_enum_names = ['Fixed', 'Minimum', 'MinimumExpanding', 'Maximum', 'Preferred', 'Expanding', 'Ignored']
        self.policy_enum_names = {0: 'Fixed',
                                  1: 'Minimum',
                                  3: 'MinimumExpanding',
                                  4: 'Maximum',
                                  5: 'Preferred',
                                  7: 'Expanding',
                                  13: 'Ignored'}
        self.initLocale()

    def initLocale(self):
        name_to_language = {}
        all_locales = QLocale.matchingLocales(QLocale.AnyLanguage, QLocale.AnyScript, QLocale.AnyCountry)
        for idx, select_locale in enumerate(all_locales):
            language = select_locale.language()

            if not select_locale.languageToString(select_locale.language()) in name_to_language:
                name_to_language[language] = QLocale.languageToString(language)
        # language = QLocale.C
        # while language <= QLocale.LastLanguage:
        #     locale = QLocale(language)
        #
        #     if locale.language() == language:
        #         name_to_language[language] = QLocale.languageToString(language)
        #     language = language + 1

        system = QLocale.system()
        sys_lang = system.language()
        if not QLocale.languageToString(system.language()) in name_to_language.values():
            name_to_language[QLocale.languageToString(sys_lang)] = sys_lang

        languages = name_to_language.keys()
        for language in languages:
            countries = QLocale.matchingLocales(language, QLocale.AnyScript, QLocale.AnyCountry)
            if len(countries) > 0 and language == sys_lang:
                countries.append(QLocale(sys_lang, system.country()))

            if len(countries) > 0 and not self.language_to_index.get(language):
                countries = self.sortCountries(countries)
                lang_idx = len(self.language_enum_names)
                self.index_to_language[lang_idx] = language
                self.language_to_index[language] = lang_idx

                country_names = QList()
                country_idx = 0
                for c in countries:
                    country = c
                    country_names.append(QLocale.countryToString(country))
                    self.index_to_country[lang_idx][country_idx] = country
                    self.country_to_index[language][country] = country_idx
                    country_idx += 1

                self.language_enum_names.append(QLocale.languageToString(language))
                self.country_enum_names[language] = country_names

    def policyEnumValueNames(self):
        return self.policy_enum_names

    def policyEnumNames(self):
        return QList(self.policy_enum_names.values())

    def languageEnumNames(self):
        return self.language_enum_names

    def countryEnumNames(self, language):
        return self.country_enum_names[language]

    def sortCountries(self, countries):
        countries_map = QMap()
        for country in countries:
            c = country.country()
            countries_map[c] = QLocale.countryToString(c)
        sorted(countries_map)

        return countries_map.keys()

    def indexToSizePolicy(self, index):
        """
        Convert combobox index to QSizePolicy.
        """
        keys = list(self.policy_enum_names.keys())
        if index < 0 or index >= len(keys):
            return -1

        if index == 0:
            return QSizePolicy.Fixed
        elif index == 1:
            return QSizePolicy.Minimum
        elif index == 2:
            return QSizePolicy.MinimumExpanding
        elif index == 3:
            return QSizePolicy.Maximum
        elif index == 4:
            return QSizePolicy.Preferred
        elif index == 5:
            return QSizePolicy.Expanding
        elif index == 6:
            return QSizePolicy.Ignored

        # return keys[index]

    def sizePolicyToIndex(self, policy):
        """
        Convert QSizePolicy to combobox index.
        """
        i = 0
        keys = list(self.policy_enum_names.keys())
        for key in keys:
            if policy == key:
                return i

            i += 1

        return -1

    def valueToIndex(self, value):
        """
        Convert combobox index to dict key.
        """
        if value == 0:
            return 0
        elif value == 1:
            return 1
        elif value == 2:
            return 3
        elif value == 3:
            return 4
        elif value == 4:
            return 5
        elif value == 5:
            return 7
        elif value == 6:
            return 13

    def indexToLocale(self, language_index, country_index):
        lang = QLocale.C
        country = QLocale.AnyCountry

        if self.index_to_language.get(language_index):
            lang = self.index_to_language[language_index]

            if self.index_to_country.get(language_index) and self.index_to_country[language_index].get(country_index):
                country = self.index_to_country[language_index][country_index]

        return [lang, country]

    def localeToIndex(self, language, country):
        lang = 0
        coun = 0
        if self.language_to_index.get(language):
            lang = self.language_to_index[language]

            if self.country_to_index.get(language) and self.country_to_index[language].get(country):
                coun = self.country_to_index[language][country]

        return [lang, coun]


# For QtFontEditWidget #########################################################
def fontValuePixmap(font):
    f = QFont(font)
    img = QImage(16, 16, QImage.Format_ARGB32_Premultiplied)
    img.fill(0)

    p = QPainter(img)
    p.setRenderHint(QPainter.TextAntialiasing, True)
    p.setRenderHint(QPainter.Antialiasing, True)

    f.setPointSize(13)
    p.setFont(f)

    t = QTextOption()
    t.setAlignment(Qt.AlignCenter)
    p.drawText(QRectF(0, 0, 16, 16), "A", t)
    p.end()

    return QPixmap.fromImage(img)


def fontValueText(font):
    return "[%s, %d]" % (font.family(), font.pointSize())


def fontValueIcon(font):
    return QIcon(fontValuePixmap(font))


# For QtCursorPropertyManager #########################################################
class QtCursorDatabase():
    def __init__(self):
        self.cursor_names = QList()
        self.cursor_icons = QMap()
        self.value_to_cursor_shape = QMap()
        self.cursor_shape_to_value = QMap()

        self.appendCursor(Qt.ArrowCursor, "Arrow",                  QIcon(":/qt-project.org/qtpropertybrowser/images/cursor-arrow.png"))
        self.appendCursor(Qt.UpArrowCursor, "Up Arrow",             QIcon(":/qt-project.org/qtpropertybrowser/images/cursor-uparrow.png"))
        self.appendCursor(Qt.CrossCursor, "Cross",                  QIcon(":/qt-project.org/qtpropertybrowser/images/cursor-cross.png"))
        self.appendCursor(Qt.WaitCursor, "Wait",                    QIcon(":/qt-project.org/qtpropertybrowser/images/cursor-wait.png"))
        self.appendCursor(Qt.IBeamCursor, "IBeam",                  QIcon(":/qt-project.org/qtpropertybrowser/images/cursor-ibeam.png"))
        self.appendCursor(Qt.SizeVerCursor, "Size Vertical",        QIcon(":/qt-project.org/qtpropertybrowser/images/cursor-sizev.png"))
        self.appendCursor(Qt.SizeHorCursor, "Size Horizontal",      QIcon(":/qt-project.org/qtpropertybrowser/images/cursor-sizeh.png"))
        self.appendCursor(Qt.SizeFDiagCursor, "Size Backslash",     QIcon(":/qt-project.org/qtpropertybrowser/images/cursor-sizef.png"))
        self.appendCursor(Qt.SizeBDiagCursor, "Size Slash",         QIcon(":/qt-project.org/qtpropertybrowser/images/cursor-sizeb.png"))
        self.appendCursor(Qt.SizeAllCursor, "Size All",             QIcon(":/qt-project.org/qtpropertybrowser/images/cursor-sizeall.png"))
        self.appendCursor(Qt.BlankCursor, "Blank",                  QIcon())
        self.appendCursor(Qt.SplitVCursor, "Split Vertical",        QIcon(":/qt-project.org/qtpropertybrowser/images/cursor-vsplit.png"))
        self.appendCursor(Qt.SplitHCursor, "Split Horizontal",      QIcon(":/qt-project.org/qtpropertybrowser/images/cursor-hsplit.png"))
        self.appendCursor(Qt.PointingHandCursor, "Pointing Hand",   QIcon(":/qt-project.org/qtpropertybrowser/images/cursor-hand.png"))
        self.appendCursor(Qt.ForbiddenCursor, "Forbidden",          QIcon(":/qt-project.org/qtpropertybrowser/images/cursor-forbidden.png"))
        self.appendCursor(Qt.OpenHandCursor, "Open Hand",           QIcon(":/qt-project.org/qtpropertybrowser/images/cursor-openhand.png"))
        self.appendCursor(Qt.ClosedHandCursor, "Closed Hand",       QIcon(":/qt-project.org/qtpropertybrowser/images/cursor-closedhand.png"))
        self.appendCursor(Qt.WhatsThisCursor, "What's This",        QIcon(":/qt-project.org/qtpropertybrowser/images/cursor-whatsthis.png"))
        self.appendCursor(Qt.BusyCursor, "Busy",                    QIcon(":/qt-project.org/qtpropertybrowser/images/cursor-busy.png"))

    def clear(self):
        self.cursor_names.clear()
        self.cursor_icons.clear()
        self.value_to_cursor_shape.clear()
        self.cursor_shape_to_value.clear()

    def appendCursor(self,shape, name, icon):
        if self.cursor_shape_to_value.get(shape):
            return
        value = len(self.cursor_names)
        self.cursor_names.append(name)
        self.cursor_icons[value] = icon
        self.value_to_cursor_shape[value] = shape
        self.cursor_shape_to_value[shape] = value

    def cursorShapeNames(self):
        return self.cursor_names

    def cursorShapeIcons(self):
        return self.cursor_icons

    def cursorToShapeName(self,cursor):
        val = self.cursorToValue(cursor)
        if val >= 0:
            return self.cursor_names[val]
        return ''

    def cursorToShapeIcon(self,cursor):
        val = self.cursorToValue(cursor)
        return self.cursor_icons[val]

    def cursorToValue(self,cursor):
        shape = cursor.shape()
        return self.cursor_shape_to_value.get(shape, -1)

    def valueToCursor(self,value):
        if value in self.value_to_cursor_shape:
            return QCursor(self.value_to_cursor_shape[value])
        return QCursor()