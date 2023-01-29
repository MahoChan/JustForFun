# ===============================================================================
# Copyright (C) 2010 Diego Duclos
#
# This file is part of eos.
#
# eos is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# eos is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with eos.  If not, see <http://www.gnu.org/licenses/>.
# ===============================================================================

from sqlalchemy import Column, String, Integer, Table
from sqlalchemy.orm import mapper, synonym

from eos.db import gamedata_meta
from eos.gamedata import ImplantSet

implant_set_table = Table("implantsets", gamedata_meta,
                          Column("setID", Integer, primary_key=True),
                          Column("setName", String),
                          Column("gradeName", String),
                          Column("implants", String))

mapper(ImplantSet, implant_set_table,
       properties={"ID": synonym("setID")})
