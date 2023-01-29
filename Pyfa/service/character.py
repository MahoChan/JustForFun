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
import sys
import copy
import itertools
import json

from logbook import Logger
import threading
from codecs import open
from xml.etree import ElementTree
from xml.dom import minidom
import gzip

# noinspection PyPackageRequirements
import wx

import config
import eos.db
from service.esi import Esi

from eos.saveddata.implant import Implant as es_Implant
from eos.saveddata.character import Character as es_Character, Skill
from eos.saveddata.module import Module as es_Module
from eos.const import FittingSlot as es_Slot
from eos.saveddata.fighter import Fighter as es_Fighter

pyfalog = Logger(__name__)
_t = wx.GetTranslation

class CharacterImportThread(threading.Thread):

    def __init__(self, paths, callback):
        threading.Thread.__init__(self)
        self.name = "CharacterImport"
        self.paths = paths
        self.callback = callback
        self.running = True

    def run(self):
        paths = self.paths
        sCharacter = Character.getInstance()
        all5_character = es_Character("All 5", 5)
        all_skill_ids = []
        for skill in all5_character.skills:
            # Parse out the skill item IDs to make searching it easier later on
            all_skill_ids.append(skill.itemID)

        for path in paths:
            if not self.running:
                break
            try:
                charFile = open(path, mode='r').read()
                doc = minidom.parseString(charFile)
                if doc.documentElement.tagName not in ("SerializableCCPCharacter", "SerializableUriCharacter"):
                    pyfalog.error("Incorrect EVEMon XML sheet")
                    raise RuntimeError("Incorrect EVEMon XML sheet")
                name = doc.getElementsByTagName("name")[0].firstChild.nodeValue
                securitystatus = doc.getElementsByTagName("securityStatus")[0].firstChild.nodeValue or 0
                skill_els = doc.getElementsByTagName("skill")
                skills = []
                for skill in skill_els:
                    if int(skill.getAttribute("typeID")) in all_skill_ids and (0 <= int(skill.getAttribute("level")) <= 5):
                        skills.append({
                            "typeID": int(skill.getAttribute("typeID")),
                            "level": int(skill.getAttribute("level")),
                        })
                    else:
                        pyfalog.error(
                                "Attempted to import unknown skill {0} (ID: {1}) (Level: {2})",
                                skill.getAttribute("name"),
                                skill.getAttribute("typeID"),
                                skill.getAttribute("level"),
                        )
                char = sCharacter.new(name + " (EVEMon)")
                sCharacter.apiUpdateCharSheet(char.ID, skills, securitystatus)
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception as e:
                pyfalog.error("Exception on character import:")
                pyfalog.error(e)
                continue

        wx.CallAfter(self.callback)

    def stop(self):
        self.running = False


class SkillBackupThread(threading.Thread):
    def __init__(self, path, saveFmt, activeFit, callback):
        threading.Thread.__init__(self)
        self.name = "SkillBackup"
        self.path = path
        self.saveFmt = saveFmt
        self.activeFit = activeFit
        self.callback = callback
        self.running = True

    def run(self):
        path = self.path
        sCharacter = Character.getInstance()

        backupData = None
        if self.running:
            if self.saveFmt == "xml" or self.saveFmt == "emp":
                backupData = sCharacter.exportXml()
            else:
                backupData = sCharacter.exportText()

        if self.running and backupData is not None:
            if self.saveFmt == "emp":
                with gzip.open(path, mode='wb') as backupFile:
                    backupFile.write(backupData.encode())
            else:
                with open(path, mode='w', encoding='utf-8') as backupFile:
                    backupFile.write(backupData)

        wx.CallAfter(self.callback)

    def stop(self):
        self.running = False


class Character:
    instance = None
    skillReqsDict = {}

    @classmethod
    def getInstance(cls):
        if cls.instance is None:
            cls.instance = Character()

        return cls.instance

    def __init__(self):
        # Simply initializes default characters in case they aren't in the database yet
        self.all0()
        self.all5()

    def exportText(self):
        data = "Pyfa exported plan for \"" + self.skillReqsDict['charname'] + "\"\n"
        data += "=" * 79 + "\n"
        data += "\n"
        item = ""
        try:
            for s in self.skillReqsDict['skills']:
                if item == "" or not item == s["item"]:
                    item = s["item"]
                    data += "-" * 79 + "\n"
                    data += "Skills required for {}:\n".format(item)
                data += "{}{}: {}\n".format("    " * s["indent"], s["skill"], int(s["level"]))
            data += "-" * 79 + "\n"
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception:
            pass

        return data

    def exportXml(self):
        root = ElementTree.Element("plan")
        root.attrib["name"] = "Pyfa exported plan for " + self.skillReqsDict['charname']
        root.attrib["revision"] = config.evemonMinVersion

        sorts = ElementTree.SubElement(root, "sorting")
        sorts.attrib["criteria"] = "None"
        sorts.attrib["order"] = "None"
        sorts.attrib["groupByPriority"] = "false"

        skillsSeen = set()

        for s in self.skillReqsDict['skills']:
            skillKey = str(s["skillID"]) + "::" + s["skill"] + "::" + str(int(s["level"]))
            if skillKey in skillsSeen:
                pass  # Duplicate skills confuse EVEMon
            else:
                skillsSeen.add(skillKey)
                entry = ElementTree.SubElement(root, "entry")
                entry.attrib["skillID"] = str(s["skillID"])
                entry.attrib["skill"] = s["skill"]
                entry.attrib["level"] = str(int(s["level"]))
                entry.attrib["priority"] = "3"
                entry.attrib["type"] = "Prerequisite"
                notes = ElementTree.SubElement(entry, "notes")
                notes.text = entry.attrib["skill"]

        # tree = ElementTree.ElementTree(root)
        data = ElementTree.tostring(root, 'utf-8')
        prettydata = minidom.parseString(data).toprettyxml(indent="  ")

        return prettydata

    @staticmethod
    def backupSkills(path, saveFmt, activeFit, callback):
        thread = SkillBackupThread(path, saveFmt, activeFit, callback)
        pyfalog.debug("Starting backup skills thread.")
        thread.start()

    @staticmethod
    def importCharacter(path, callback):
        thread = CharacterImportThread(path, callback)
        pyfalog.debug("Starting import character thread.")
        thread.start()

    @staticmethod
    def all0():
        return es_Character.getAll0()

    def all0ID(self):
        return self.all0().ID

    @staticmethod
    def all5():
        return es_Character.getAll5()

    def all5ID(self):
        return self.all5().ID

    @staticmethod
    def getAlphaCloneList():
        return eos.db.getAlphaCloneList()

    @staticmethod
    def getCharacterList():
        return eos.db.getCharacterList()

    @staticmethod
    def getCharacter(identity):
        char = eos.db.getCharacter(identity)
        return char

    def saveCharacter(self, charID):
        """Save edited skills"""
        if charID == self.all5ID() or charID == self.all0ID():
            return
        char = eos.db.getCharacter(charID)
        char.saveLevels()

    @staticmethod
    def saveCharacterAs(charID, newName):
        """Save edited skills as a new character"""
        char = eos.db.getCharacter(charID)
        newChar = copy.deepcopy(char)
        newChar.name = newName
        eos.db.save(newChar)

        # revert old char
        char.revertLevels()
        return newChar.ID

    @staticmethod
    def revertCharacter(charID):
        """Rollback edited skills"""
        char = eos.db.getCharacter(charID)
        char.revertLevels()

    @staticmethod
    def getSkillGroups():
        cat = eos.db.getCategory(16)
        groups = []
        for grp in cat.groups:
            if grp.published:
                groups.append((grp.ID, grp.name))
        return sorted(groups, key=lambda x: x[1])

    @staticmethod
    def getSkills(groupID):
        group = eos.db.getGroup(groupID)
        skills = []
        for skill in group.items:
            if skill.published is True:
                skills.append((skill.ID, skill.name))
        return sorted(skills, key=lambda x: x[1])

    @staticmethod
    def getSkillsByName(text):
        items = eos.db.searchSkills(text)
        skills = []
        for skill in items:
            if skill.published is True:
                skills.append((skill.ID, skill.name))
        return sorted(skills, key=lambda x: x[1])

    @staticmethod
    def setAlphaClone(char, cloneID):
        char.alphaCloneID = cloneID
        eos.db.commit()

    @staticmethod
    def setSecStatus(char, secStatus):
        char.secStatus = secStatus
        eos.db.commit()

    @staticmethod
    def getSkillDescription(itemID):
        return eos.db.getItem(itemID).description

    @staticmethod
    def getGroupDescription(groupID):
        return eos.db.getMarketGroup(groupID).description

    @staticmethod
    def getSkillLevel(charID, skillID):
        skill = eos.db.getCharacter(charID).getSkill(skillID)
        return float(skill.level) if skill.learned else _t("Not learned"), skill.isDirty

    @staticmethod
    def getDirtySkills(charID):
        return eos.db.getCharacter(charID).dirtySkills

    @staticmethod
    def getCharName(charID):
        return eos.db.getCharacter(charID).name

    @staticmethod
    def new(name="New Character"):
        char = es_Character(name)
        eos.db.save(char)
        return char

    @staticmethod
    def rename(char, newName):
        if char.name in ("All 0", "All 5"):
            pyfalog.info("Cannot rename built in characters.")
        else:
            char.name = newName
            eos.db.commit()

    @staticmethod
    def copy(char):
        newChar = copy.deepcopy(char)
        eos.db.save(newChar)
        return newChar

    @staticmethod
    def delete(char):
        eos.db.remove(char)

    @staticmethod
    def getApiDetails(charID):
        # todo: fix this (or get rid of?)
        return "", "", "", []
        char = eos.db.getCharacter(charID)
        if char.chars is not None:
            chars = json.loads(char.chars)
        else:
            chars = None
        return char.apiID or "", char.apiKey or "", char.defaultChar or "", chars or []

    @staticmethod
    def getSsoCharacter(charID):
        char = eos.db.getCharacter(charID)
        sso = char.getSsoCharacter(config.getClientSecret())
        return sso

    @staticmethod
    def setSsoCharacter(charID, ssoCharID):
        char = eos.db.getCharacter(charID)
        if ssoCharID is not None:
            sso = eos.db.getSsoCharacter(ssoCharID, config.getClientSecret())
            char.setSsoCharacter(sso, config.getClientSecret())
        else:
            char.setSsoCharacter(None, config.getClientSecret())
        eos.db.commit()

    def apiFetch(self, charID, callback):
        thread = UpdateAPIThread(charID, (self.apiFetchCallback, callback))
        thread.start()

    def apiFetchCallback(self, guiCallback, e=None):
        eos.db.commit()
        wx.CallAfter(guiCallback, e)

    @staticmethod
    def apiUpdateCharSheet(charID, skills, securitystatus):
        char = eos.db.getCharacter(charID)
        char.apiUpdateCharSheet(skills, securitystatus)
        eos.db.commit()

    @classmethod
    def changeLevel(cls, charID, skillID, level, persist=False, ifHigher=False):
        char = eos.db.getCharacter(charID)
        skill = char.getSkill(skillID)

        if ifHigher and level < skill.level:
            return

        if isinstance(level, str) or level > 5 or level < 0:
            skill.setLevel(None, persist)
            eos.db.commit()
        elif skill.level != level:
            cls._trainSkillReqs(char, skill, persist)
            skill.setLevel(level, persist)
            eos.db.commit()

    @classmethod
    def _trainSkillReqs(cls, char, skill, persist):
        for childSkillItem, neededSkillLevel in skill.item.requiredSkills.items():
            childSkill = char.getSkill(childSkillItem.ID)
            if childSkill.level < neededSkillLevel:
                childSkill.setLevel(neededSkillLevel, persist)
                cls._trainSkillReqs(char, childSkill, persist)

    @staticmethod
    def revertLevel(charID, skillID):
        char = eos.db.getCharacter(charID)
        skill = char.getSkill(skillID)
        skill.revert()

    @staticmethod
    def saveSkill(charID, skillID):
        char = eos.db.getCharacter(charID)
        skill = char.getSkill(skillID)
        skill.saveLevel()

    @staticmethod
    def addImplant(charID, itemID):
        char = eos.db.getCharacter(charID)
        if char.ro:
            pyfalog.error("Trying to add implant to read-only character")
            return

        implant = es_Implant(eos.db.getItem(itemID))
        char.implants.makeRoom(implant)
        char.implants.append(implant)
        eos.db.commit()

    @staticmethod
    def removeImplant(charID, implant):
        char = eos.db.getCharacter(charID)
        char.implants.remove(implant)
        eos.db.commit()

    @staticmethod
    def getImplants(charID):
        char = eos.db.getCharacter(charID)
        return char.implants

    def checkRequirements(self, fit):
        # toCheck = []
        reqs = {}
        for thing in itertools.chain(fit.modules, fit.drones, fit.fighters, (fit.ship,), fit.appliedImplants, fit.boosters):
            if isinstance(thing, es_Module) and thing.slot == es_Slot.RIG:
                continue
            for attr in ("item", "charge"):
                if attr == "charge" and isinstance(thing, es_Fighter):
                    # Fighter Bombers are automatically charged with micro bombs.
                    # These have skill requirements attached, but aren't used in EVE.
                    continue
                subThing = getattr(thing, attr, None)
                subReqs = {}
                if subThing is not None:
                    if isinstance(thing, es_Fighter) and attr == "charge":
                        continue
                    self._checkRequirements(fit.character, subThing, subReqs)
                    if subReqs:
                        reqs[subThing] = subReqs

        return reqs

    def _checkRequirements(self, char, subThing, reqs):
        for req, level in subThing.requiredSkills.items():
            name = req.name
            ID = req.ID
            info = reqs.get(name)
            currLevel, subs = info if info is not None else 0, {}
            if level > currLevel and (char is None or char.getSkill(req).level < level):
                reqs[name] = (level, ID, subs)
                self._checkRequirements(char, req, subs)
        return reqs


class UpdateAPIThread(threading.Thread):

    def __init__(self, charID, callback):
        threading.Thread.__init__(self)

        self.name = "CheckUpdate"
        self.callback = callback
        self.charID = charID
        self.running = True

    def run(self):
        try:
            char = eos.db.getCharacter(self.charID)

            sEsi = Esi.getInstance()
            sChar = Character.getInstance()
            ssoChar = sChar.getSsoCharacter(char.ID)

            if not self.running:
                self.callback[0](self.callback[1])
                return
            resp = sEsi.getSkills(ssoChar.ID)

            if not self.running:
                self.callback[0](self.callback[1])
                return
            # todo: check if alpha. if so, pop up a question if they want to apply it as alpha. Use threading events to set the answer?
            char.clearSkills()
            for skillRow in resp["skills"]:
                char.addSkill(Skill(char, skillRow["skill_id"], skillRow["trained_skill_level"]))

            if not self.running:
                self.callback[0](self.callback[1])
                return
            resp = sEsi.getSecStatus(ssoChar.ID)
            char.secStatus = resp['security_status']
            self.callback[0](self.callback[1])
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as ex:
            pyfalog.warn(ex)
            self.callback[0](self.callback[1], sys.exc_info())

    def stop(self):
        self.running = False
