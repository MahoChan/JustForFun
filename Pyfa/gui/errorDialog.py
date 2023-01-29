# ===============================================================================
# Copyright (C) 2010 Diego Duclos
#
# This file is part of pyfa.
#
# pyfa is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyfa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyfa.  If not, see <http://www.gnu.org/licenses/>.
# ===============================================================================

import datetime
import sys
import traceback

# noinspection PyPackageRequirements
import wx
from logbook import Logger

import config
from gui.auxWindow import AuxiliaryFrame
from service.prereqsCheck import version_block


_t = wx.GetTranslation
pyfalog = Logger(__name__)


class ErrorHandler:
    __parent = None
    __frame = None

    @classmethod
    def HandleException(cls, exc_type, exc_value, exc_traceback):
        with config.logging_setup.threadbound():
            # Print the base level traceback
            t = traceback.format_exception(exc_type, exc_value, exc_traceback)
            pyfalog.critical("\n\n" + "".join(t))

            if cls.__parent is None:
                app = wx.App(False)
                cls.__frame = ErrorFrame(None)
                cls.__frame.addException("".join(t))
                cls.__frame.Show()
                app.MainLoop()
                sys.exit()
            else:
                if not cls.__frame:
                    cls.__frame = ErrorFrame(cls.__parent)
                cls.__frame.Show()
                cls.__frame.addException("".join(t))

    @classmethod
    def SetParent(cls, parent):
        cls.__parent = parent


class ErrorFrame(AuxiliaryFrame):

    def __init__(self, parent=None, error_title=_t('Error!')):
        super().__init__(parent, id=wx.ID_ANY, title=_t("pyfa error"), pos=wx.DefaultPosition, size=wx.Size(500, 600))

        from eos.config import gamedata_version, gamedata_date

        if gamedata_date:
            try:
                time = datetime.datetime.fromtimestamp(int(gamedata_date)).strftime('%Y-%m-%d %H:%M:%S')
            except TypeError:
                time = None
        else:
            time = None
        version = "pyfa " + config.getVersion() + '\nEVE Data Version: {} ({})\n\n'.format(gamedata_version, time)  # gui.aboutData.versionString

        desc = _t("pyfa has experienced an unexpected issue. Below is a message that contains crucial \n"
               "information about how this was triggered. Please contact the developers with the \n"
               "information provided through the EVE Online forums or file a GitHub issue.")

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        headSizer = wx.BoxSizer(wx.HORIZONTAL)

        headingText = wx.StaticText(self, wx.ID_ANY, error_title, wx.DefaultPosition, wx.DefaultSize, wx.ALIGN_CENTRE)
        headingText.SetFont(wx.Font(14, 74, 90, 92, False))

        headSizer.Add(headingText, 1, wx.ALL, 5)
        mainSizer.Add(headSizer, 0, wx.EXPAND, 5)

        mainSizer.Add(wx.StaticLine(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL), 0, wx.EXPAND | wx.ALL, 5)

        box = wx.BoxSizer(wx.VERTICAL)
        mainSizer.Add(box, 0, wx.EXPAND | wx.ALIGN_TOP)

        descText = wx.StaticText(self, wx.ID_ANY, desc)
        box.Add(descText, 1, wx.ALL, 5)

        # github = wx.lib.agw.hyperlink.HyperLinkCtrl(self, wx.ID_ANY, label="Github", URL="https://github.com/pyfa-org/Pyfa/issues")
        # box.Add(github, 0, wx.ALL, 5)
        #
        # eveForums = wx.lib.agw.hyperlink.HyperLinkCtrl(self, wx.ID_ANY, label="EVE Forums", URL="https://forums.eveonline.com/t/27156")
        # box.Add(eveForums, 0, wx.ALL, 5)

        # mainSizer.AddSpacer((0, 5), 0, wx.EXPAND, 5)

        self.errorTextCtrl = wx.TextCtrl(self, wx.ID_ANY, version + version_block.strip(), wx.DefaultPosition,
                                         (-1, 400), wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.TE_DONTWRAP)
        self.errorTextCtrl.SetFont(wx.Font(8, wx.FONTFAMILY_TELETYPE, wx.NORMAL, wx.NORMAL))
        mainSizer.Add(self.errorTextCtrl, 0, wx.EXPAND | wx.ALL, 5)
        self.errorTextCtrl.AppendText("\n")
        self.errorTextCtrl.Layout()

        self.SetSizer(mainSizer)
        mainSizer.Layout()
        self.Layout()
        self.SetMinSize(self.GetSize())

        self.Centre(wx.BOTH)

    def addException(self, text):
        self.errorTextCtrl.AppendText("\n{}\n\n{}".format("#" * 20, text))
