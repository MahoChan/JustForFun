# noinspection PyPackageRequirements
import wx

import gui.fitCommands as cmd
import gui.mainFrame
from gui.contextMenu import ContextMenuUnconditional
from service.fit import Fit
from service.market import Market

_t = wx.GetTranslation


class AddCommandFit(ContextMenuUnconditional):
    # Get list of items that define a command fit
    sMkt = Market.getInstance()
    grp = sMkt.getGroup(1770)  # Command burst group
    commandTypeIDs = {item.ID for item in grp.items}
    commandFits = []
    menu = None

    @classmethod
    def fitChanged(cls, evt):
        # This fires on a FitChanged event and updates the command fits whenever a command burst module is added or
        # removed from a fit. evt.typeID can be either a int or a set (in the case of multiple module deletions)
        if evt is None or (getattr(evt, 'action', None) in ("modadd", "moddel") and getattr(evt, 'typeID', None)):
            if evt is not None:
                ids = getattr(evt, 'typeID')
                if not isinstance(ids, set):
                    ids = {ids}

            if evt is None or not ids.isdisjoint(cls.commandTypeIDs):
                # we are adding or removing an item that defines a command fit. Need to refresh fit list
                cls.populateFits(evt)
        evt.Skip()

    @classmethod
    def populateFits(cls, evt):
        sFit = Fit.getInstance()
        cls.commandFits = sFit.getFitsWithModules(cls.commandTypeIDs)

    def __init__(self):
        self.mainFrame = gui.mainFrame.MainFrame.getInstance()

    def display(self, callingWindow, srcContext):
        if self.mainFrame.getActiveFit() is None or len(self.__class__.commandFits) == 0 or srcContext != "commandView":
            return False
        return True

    def getText(self, callingWindow, itmContext):
        return _t("Command Fits")

    def addFit(self, menu, fit, includeShip=False):
        label = fit.name if not includeShip else "({}) {}".format(fit.ship.item.name, fit.name)
        if not label:
            label = ' '
        id = ContextMenuUnconditional.nextID()
        self.fitMenuItemIds[id] = fit
        menuItem = wx.MenuItem(menu, id, label)
        menu.Bind(wx.EVT_MENU, self.handleSelection, menuItem)
        return menuItem

    def getSubMenu(self, callingWindow, context, rootMenu, i, pitem):
        msw = True if "wxMSW" in wx.PlatformInfo else False
        self.context = context
        self.fitMenuItemIds = {}

        sub = wx.Menu()

        if len(self.__class__.commandFits) < 15:
            for fit in sorted(self.__class__.commandFits, key=lambda x: x.name):
                menuItem = self.addFit(rootMenu if msw else sub, fit, True)
                sub.Append(menuItem)
        else:
            typeDict = {}

            for fit in self.__class__.commandFits:
                shipName = fit.ship.item.name
                if shipName not in typeDict:
                    typeDict[shipName] = []
                typeDict[shipName].append(fit)

            for ship in sorted(typeDict.keys()):
                shipItem = wx.MenuItem(sub, ContextMenuUnconditional.nextID(), ship)
                grandSub = wx.Menu()
                shipItem.SetSubMenu(grandSub)

                for fit in sorted(typeDict[ship], key=lambda x: x.name):
                    fitItem = self.addFit(rootMenu if msw else grandSub, fit, False)
                    grandSub.Append(fitItem)

                sub.Append(shipItem)

        return sub

    def handleSelection(self, event):
        fit = self.fitMenuItemIds[event.Id]
        if fit is False or fit not in self.__class__.commandFits:
            event.Skip()
            return

        fitID = self.mainFrame.getActiveFit()
        self.mainFrame.command.Submit(cmd.GuiAddCommandFitsCommand(fitID=fitID, commandFitIDs=[fit.ID]))


AddCommandFit.populateFits(None)
AddCommandFit.register()
