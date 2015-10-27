# -*- coding: utf-8 -*-
#########################################################################
#                                                                       #
# Copyright (C) 2015  Agile Business Group                              #
#                                                                       #
# This program is free software: you can redistribute it and/or modify  #
# it under the terms of the GNU Affero General Public License as        #
# published by the Free Software Foundation, either version 3 of the    #
# License, or (at your option) any later version.                       #
#                                                                       #
# This program is distributed in the hope that it will be useful,       #
# but WITHOUT ANY WARRANTY; without even the implied warranty of        #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
# GNU Affero General Public Licensefor more details.                    #
#                                                                       #
# You should have received a copy of the                                #
# GNU Affero General Public License                                     #
# along with this program.  If not, see <http://www.gnu.org/licenses/>. #
#                                                                       #
#########################################################################

{
    'name': 'Report Qweb Element Page Visibility',
    'version': '8.0.1.0.0',
    'author': 'Agile Business Group, Odoo Community Association (OCA)',
    'category': 'Tools',
    "website": "https://odoo-community.org/",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    'data': [
        'views/layouts.xml',
    ],
    'depends': [
        'report',
    ],
}
