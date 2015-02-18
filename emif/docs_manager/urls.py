# -*- coding: utf-8 -*-
# Copyright (C) 2014 Universidade de Aveiro, DETI/IEETA, Bioinformatics Group - http://bioinformatics.ua.pt/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
from django.conf.urls.defaults import *
from views import *
from documents import *

urlpatterns = patterns('',

    # Upload Documents
    url(r'^uploadfile/(?P<fingerprint_id>[^/]+)/$', 'docs_manager.views.upload_file'),

    # List Files
    url(r'^docfiles/(?P<fingerprint>[^/]+)/$', 'docs_manager.views.list_fingerprint_files'),


)
