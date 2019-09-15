###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Security 
#    (see https://mukit.at).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

#----------------------------------------------------------
# Helper
#----------------------------------------------------------

def convert_security_uid(id):
    if isinstance(id, NoSecurityUid):
        return super(NoSecurityUid, id).__int__()
    return id

#----------------------------------------------------------
# Model
#----------------------------------------------------------
    
class NoSecurityUid(int):
    
    def __int__(self):
        return self

    def __eq__(self, other):
        if isinstance(other, int):
            return False
        return super(NoSecurityUid, self).__int__() == other
       
    def __hash__(self):
        return super(NoSecurityUid, self).__hash__()