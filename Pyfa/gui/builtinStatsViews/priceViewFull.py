# =============================================================================
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
# =============================================================================

# noinspection PyPackageRequirements
import wx
from gui.statsView import StatsView
from gui.bitmap_loader import BitmapLoader
from gui.utils.numberFormatter import formatAmount
from service.price import Fit, Price
from service.settings import MarketPriceSettings

_t = wx.GetTranslation


class PriceViewFull(StatsView):
    name = "priceViewFull"

    def __init__(self, parent):
        StatsView.__init__(self)
        self.parent = parent
        self.settings = MarketPriceSettings.getInstance()

    def getHeaderText(self, fit):
        return _t("Price")

    def populatePanel(self, contentPanel, headerPanel):
        contentSizer = contentPanel.GetSizer()
        self.panel = contentPanel
        self.headerPanel = headerPanel

        headerContentSizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer = headerPanel.GetSizer()
        hsizer.Add(headerContentSizer, 0, 0, 0)
        self.labelEMStatus = wx.StaticText(headerPanel, wx.ID_ANY, "")
        headerContentSizer.Add(self.labelEMStatus)
        headerPanel.GetParent().AddToggleItem(self.labelEMStatus)

        gridPrice = wx.GridSizer(2, 3, 0, 0)
        contentSizer.Add(gridPrice, 0, wx.EXPAND | wx.ALL, 0)
        for _type, label in (
                ("ship", _t("Ship")), ("fittings", _t("Fittings")), ("character", _t("Character")),
                ("drones", _t("Drones")), ("cargoBay", _t("Cargo bay")), ("total", _t("Total"))
        ):
            if _type in "ship":
                image = "ship_big"
            elif _type in ("fittings", "total"):
                image = "%sPrice_big" % _type
            else:
                image = "%s_big" % _type

            box = wx.BoxSizer(wx.HORIZONTAL)
            gridPrice.Add(box, 0, wx.ALIGN_TOP)

            box.Add(BitmapLoader.getStaticBitmap(image, contentPanel, "gui"), 0, wx.ALIGN_CENTER)

            vbox = wx.BoxSizer(wx.VERTICAL)
            box.Add(vbox, 1, wx.EXPAND)

            vbox.Add(wx.StaticText(contentPanel, wx.ID_ANY, label.capitalize()), 0, wx.ALIGN_LEFT)

            hbox = wx.BoxSizer(wx.HORIZONTAL)
            vbox.Add(hbox)

            lbl = wx.StaticText(contentPanel, wx.ID_ANY, "0.00 ISK")
            setattr(self, "labelPrice%s" % _type.capitalize(), lbl)
            hbox.Add(lbl, 0, wx.ALIGN_LEFT)

    def refreshPanel(self, fit):
        if fit is not None:
            self.fit = fit
            fit_items = set(Fit.fitItemIter(fit))
            Price.getInstance().getPrices(fit_items, self.processPrices, fetchTimeout=30)
            self.labelEMStatus.SetLabel("Updating prices...")

        self.refreshPanelPrices(fit)
        self.panel.Layout()

    def refreshPanelPrices(self, fit=None):

        ship_price = 0
        module_price = 0
        drone_price = 0
        fighter_price = 0
        cargo_price = 0
        booster_price = 0
        implant_price = 0

        if fit:
            ship_price = fit.ship.item.price.price

            if fit.modules:
                for module in fit.modules:
                    if not module.isEmpty:
                        module_price += module.item.price.price

            if fit.drones:
                for drone in fit.drones:
                    drone_price += drone.item.price.price * drone.amount

            if fit.fighters:
                for fighter in fit.fighters:
                    fighter_price += fighter.item.price.price * fighter.amount

            if fit.cargo:
                for cargo in fit.cargo:
                    cargo_price += cargo.item.price.price * cargo.amount

            if fit.boosters:
                for booster in fit.boosters:
                    booster_price += booster.item.price.price

            if fit.appliedImplants:
                for implant in fit.appliedImplants:
                    implant_price += implant.item.price.price

        total_price = 0
        total_price += ship_price
        total_price += module_price
        if self.settings.get("drones"):
            total_price += drone_price + fighter_price
        if self.settings.get("cargo"):
            total_price += cargo_price
        if self.settings.get("character"):
            total_price += booster_price + implant_price

        self.labelPriceShip.SetLabel("%s ISK" % formatAmount(ship_price, 3, 3, 9, currency=True))
        self.labelPriceShip.SetToolTip(wx.ToolTip('{:,.2f} ISK'.format(ship_price)))

        self.labelPriceFittings.SetLabel("%s ISK" % formatAmount(module_price, 3, 3, 9, currency=True))
        self.labelPriceFittings.SetToolTip(wx.ToolTip('{:,.2f} ISK'.format(module_price)))

        self.labelPriceDrones.SetLabel("%s ISK" % formatAmount(drone_price + fighter_price, 3, 3, 9, currency=True))
        self.labelPriceDrones.SetToolTip(wx.ToolTip('{:,.2f} ISK'.format(drone_price + fighter_price)))

        self.labelPriceCargobay.SetLabel("%s ISK" % formatAmount(cargo_price, 3, 3, 9, currency=True))
        self.labelPriceCargobay.SetToolTip(wx.ToolTip('{:,.2f} ISK'.format(cargo_price)))

        self.labelPriceCharacter.SetLabel("%s ISK" % formatAmount(booster_price + implant_price, 3, 3, 9, currency=True))
        self.labelPriceCharacter.SetToolTip(wx.ToolTip('{:,.2f} ISK'.format(booster_price + implant_price)))

        self.labelPriceTotal.SetLabel("%s ISK" % formatAmount(total_price, 3, 3, 9, currency=True))
        self.labelPriceTotal.SetToolTip(wx.ToolTip('{:,.2f} ISK'.format(total_price)))

    def processPrices(self, prices):
        self.refreshPanelPrices(self.fit)

        self.labelEMStatus.SetLabel("")
        self.panel.Layout()


PriceViewFull.register()
