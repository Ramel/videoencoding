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
from subprocess import call, Popen, PIPE
import re
import sys

# Import from itools
from itools.gettext import MSG
from itools.web import ERROR
from itools.core.utils import get_pipe

# Import from ikaaro
from ikaaro.folder import Folder
from ikaaro.registry import register_resource_class
from ikaaro.file import Video

# Debug
from pprint import pprint


class VideoEncodingToFLV(Video):

    class_id = 'video_encoding'
    class_title = MSG(u'Video Encoding')
    class_description = MSG(u'Encode in FLV an AVI video file')
    
    """
    def encode(self, filename, ratio):
        # Encode
    """

    def get_ratio(self, dirname, filename):
        """
        Need the "ffmpeg" cli to be on the PATH
        """
        
        # The command to get the video ratio
        command = ['ffmpeg', '-i', filename]

        #output = get_pipe(command, cwd=dirname).read()
        popen = Popen(command, stdout=PIPE, stderr=PIPE, cwd=dirname)
        errno = popen.wait()
        output2 = popen.stdout
        # Working with the std error as output
        # because we use the -i in the cli 
        output = popen.stderr.read()
        pprint('===output==')
        pprint(output)
        pprint('===isinstance==')
        pprint('%s' % isinstance(output, basestring)) 
        
        if output is not None:
            
            m = re.search('Video: [^\\n]*\\n', output)
            pprint('%s' % m.group(0))
            m = m.group(0).replace('Video: ', '').replace('\n', '').split(', ')
            pprint('===m===')
            pprint('%s' % m)
            size = m[2].split('x')
            ratio = float(size[0])/float(size[1])
        else:
            ratio = "Nothing at all"
        return ratio

###########################################################################
# Register
register_resource_class(VideoEncodingToFLV)
