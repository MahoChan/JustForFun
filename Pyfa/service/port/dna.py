# =============================================================================
# Copyright (C) 2014 Ryan Holmes
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


import re
from collections import OrderedDict

from logbook import Logger

from eos.const import FittingModuleState, FittingSlot
from eos.saveddata.cargo import Cargo
from eos.saveddata.citadel import Citadel
from eos.saveddata.drone import Drone
from eos.saveddata.fighter import Fighter
from eos.saveddata.fit import Fit
from eos.saveddata.module import Module
from eos.saveddata.ship import Ship
from gui.fitCommands.helpers import activeStateLimit
from service.const import PortDnaOptions
from service.fit import Fit as svcFit
from service.market import Market


pyfalog = Logger(__name__)


def importDna(string, fitName=None):
    sMkt = Market.getInstance()
    ids = list(map(int, re.findall(r'\d+', string)))
    for id_ in ids:
        try:
            try:
                Ship(sMkt.getItem(id_))
            except ValueError:
                Citadel(sMkt.getItem(id_))
            string = string[string.index(str(id_)):]
            break
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            pyfalog.warning("Exception caught in importDna")
            pass
    string = string[:string.index("::") + 2]
    info = string.split(":")
    return processImportInfo(info, fitName, ";")

def importDnaAlt(string, fitName=None):
    sMkt = Market.getInstance()
    ids = list(map(int, re.findall(r'\d+', string)))
    for id_ in ids:
        try:
            try:
                Ship(sMkt.getItem(id_))
            except ValueError:
                Citadel(sMkt.getItem(id_))
            string = string[string.index(str(id_)):]
            break
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            pyfalog.warning("Exception caught in importDna")
            pass
    info = string.split(":")
    return processImportInfo(info, fitName, "*")

def processImportInfo(info, fitName, amountSeparator):
    sMkt = Market.getInstance()
    f = Fit()
    try:
        try:
            f.ship = Ship(sMkt.getItem(int(info[0])))
        except ValueError:
            f.ship = Citadel(sMkt.getItem(int(info[0])))
        if fitName is None:
            f.name = "{0} - DNA Imported".format(f.ship.item.name)
        else:
            f.name = fitName
    except UnicodeEncodeError:
        def logtransform(s_):
            if len(s_) > 10:
                return s_[:10] + "..."
            return s_

        pyfalog.exception("Couldn't import ship data {0}", [logtransform(s) for s in info])
        return None

    moduleList = []
    for itemInfo in info[1:]:
        if itemInfo:
            if amountSeparator in itemInfo:
                itemID, amount = itemInfo.split(amountSeparator)
            else:
                itemID = itemInfo
                amount = 1
            item = sMkt.getItem(int(itemID), eager="group.category")

            if item.category.name == "Drone":
                d = Drone(item)
                d.amount = int(amount)
                f.drones.append(d)
            elif item.category.name == "Fighter":
                ft = Fighter(item)
                ft.amount = int(amount) if ft.amount <= ft.fighterSquadronMaxSize else ft.fighterSquadronMaxSize
                if ft.fits(f):
                    f.fighters.append(ft)
            elif item.category.name == "Charge":
                c = Cargo(item)
                c.amount = int(amount)
                f.cargo.append(c)
            else:
                for i in range(int(amount)):
                    try:
                        m = Module(item)
                    except (KeyboardInterrupt, SystemExit):
                        raise
                    except:
                        pyfalog.warning("Exception caught in importDna")
                        continue
                    # Add subsystems before modules to make sure T3 cruisers have subsystems installed
                    if item.category.name == "Subsystem":
                        if m.fits(f):
                            f.modules.append(m)
                    else:
                        m.owner = f
                        if m.isValidState(FittingModuleState.ACTIVE):
                            m.state = activeStateLimit(m.item)
                        moduleList.append(m)

    # Recalc to get slot numbers correct for T3 cruisers
    sFit = svcFit.getInstance()
    sFit.recalc(f)
    sFit.fill(f)

    for module in moduleList:
        if module.fits(f):
            module.owner = f
            if module.isValidState(FittingModuleState.ACTIVE):
                module.state = activeStateLimit(module.item)
            f.modules.append(module)

    return f


def exportDna(fit, options, callback):
    dna = str(fit.shipID)
    subsystems = []  # EVE cares which order you put these in
    mods = OrderedDict()
    charges = OrderedDict()
    for mod in fit.modules:
        if not mod.isEmpty:
            if mod.slot == FittingSlot.SUBSYSTEM:
                subsystems.append(mod)
                continue
            if mod.itemID not in mods:
                mods[mod.itemID] = 0
            mods[mod.itemID] += 1

            if mod.charge:
                if mod.chargeID not in charges:
                    charges[mod.chargeID] = 0
                # `or 1` because some charges (ie scripts) are without qty
                charges[mod.chargeID] += mod.numCharges or 1

    for subsystem in sorted(subsystems, key=lambda mod_: mod_.getModifiedItemAttr("subSystemSlot")):
        dna += ":{0};1".format(subsystem.itemID)

    for mod in mods:
        dna += ":{0};{1}".format(mod, mods[mod])

    for drone in fit.drones:
        dna += ":{0};{1}".format(drone.itemID, drone.amount)

    for fighter in fit.fighters:
        dna += ":{0};{1}".format(fighter.itemID, fighter.amount)

    for cargo in fit.cargo:
        # DNA format is a simple/dumb format. As CCP uses the slot information of the item itself
        # without designating slots in the DNA standard, we need to make sure we only include
        # charges in the DNA export. If modules were included, the EVE Client will interpret these
        # as being "Fitted" to whatever slot they are for, and it causes an corruption error in the
        # client when trying to save the fit
        if cargo.item.category.name == "Charge":
            if cargo.item.ID not in charges:
                charges[cargo.item.ID] = 0
            charges[cargo.item.ID] += cargo.amount

    for charge in charges:
        dna += ":{0};{1}".format(charge, charges[charge])

    text = dna + "::"

    if options[PortDnaOptions.FORMATTING]:
        text = '<url=fitting:{}>{}</url>'.format(text, fit.name)

    if callback:
        callback(text)
    else:
        return text
