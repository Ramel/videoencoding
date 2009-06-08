# -*- coding: UTF-8 -*-
# Copyright (C) 2009 Armel FORTUN <armel@maar.fr>
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

# Import from the Standard Library
import commands

# Import from ikaaro
from ikaaro.folder import Folder
from ikaaro.registry import register_resource_class

# Debug
from pprint import pprint


class VideoEncodingToFLV(Video):

    class_id = 'video_encoding'
    class_title = MSG(u'Video Encoding')
    class_description = MSG(u'Encode in FLV an AVI video file')
    #class_icon16 = 'tracker/tracker16.png'
    #class_icon48 = 'tracker/tracker48.png'
    #class_views = ['view', 'add_issue', 'search', 'browse_content', 'edit']

    #__fixed_handlers__ = ['product', 'module', 'version', 'type', 'priority',
    #    'state', 'calendar']
    
    def encode(self, filename, ratio):
        # Encode

    def get_ratio(self, filename):
        """Need the "ffmpeg" cli to be on the PATH
        """
        
        output = commands.getoutput('ffmpeg -i %s') % filename
        m = re.search('Video: [^\\n]*\\n', output)
        m = m.replace('Video: ', '')
        m = m.replace('\n', '')
        m = m.split(', ')
        size = m[2].split('z')
        ratio = %d / %d % (size[0], size[1])
        pprint ratio

        return ratio


###########################################################################
# Register
###########################################################################
register_resource_class(VideoEncodingToFLV)
