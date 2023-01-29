# noinspection PyPackageRequirements
import wx

from eos.const import FittingSlot
from eos.saveddata.drone import Drone
from eos.saveddata.fit import Fit
from eos.saveddata.implant import Implant
from eos.saveddata.module import Module, Rack
from eos.saveddata.targetProfile import TargetProfile
from graphs.wrapper import BaseWrapper
from gui.viewColumn import ViewColumn


class BaseIcon(ViewColumn):
    name = "Base Icon"

    def __init__(self, fittingView, params):
        ViewColumn.__init__(self, fittingView)
        self.size = 24
        self.maxsize = self.size
        self.mask = wx.LIST_MASK_IMAGE
        self.columnText = ""
        self.shipImage = fittingView.imageList.GetImageIndex("ship_small", "gui")

    def getImageId(self, stuff):
        if isinstance(stuff, BaseWrapper):
            stuff = stuff.item

        if isinstance(stuff, Drone):
            return -1
        elif isinstance(stuff, Fit):
            return self.shipImage
        elif isinstance(stuff, Rack):
            return -1
        elif isinstance(stuff, Implant):
            if stuff.character:  # if it has a character as it's parent
                return self.fittingView.imageList.GetImageIndex("character_small", "gui")
            else:
                return self.shipImage
        elif isinstance(stuff, Module):
            if stuff.isEmpty:
                return self.fittingView.imageList.GetImageIndex("slot_%s_small" % FittingSlot(stuff.slot).name.lower(),
                                                                "gui")
            else:
                return self.loadIconFile(stuff.item.iconID or "")
        elif isinstance(stuff, TargetProfile):
            return self.fittingView.imageList.GetImageIndex("target_small", "gui")

        item = getattr(stuff, "item", stuff)
        return self.loadIconFile(item.iconID)

    def loadIconFile(self, iconFile):
        if iconFile:
            return self.fittingView.imageList.GetImageIndex(iconFile, "icons")
        else:
            return -1


BaseIcon.register()
