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
from itools import vfs

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
        """Return the ratio of the filename (a video)
        Need the "ffmpeg" cli to be on the PATH
        """
        
        # The command to get the video ratio
        command = ['ffmpeg', '-i', filename]

        #output = get_pipe(command, cwd=dirname).read()
        popen = Popen(command, stdout=PIPE, stderr=PIPE, cwd=dirname)
        errno = popen.wait()
        #output2 = popen.stdout
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

    def encode_avi_to_flv(self, tmpfolder, inputfile, name, width):
        # name is unique in this thread
        # inputfile = original file name
        # outputfile = the name variable, unique name
        flv_filename = "%s.flv" % name
        ratio = self.get_ratio(tmpfolder, inputfile)
        height = int(round(float(width)/ratio))
        pprint('===height===')
        pprint('%s' % height)
        pprint('===width===')
        pprint('%s' % width)
        ffmpeg = ['ffmpeg', '-i', '%s' % inputfile, '-acodec', 'mp3', '-ar', '22050',
            '-ab', '32', '-f', 'flv', '-s', '%sx%s' % (width, height), flv_filename]
        get_pipe(ffmpeg, cwd=tmpfolder)
        
        mimetype = 'video/x-flv'
        extension = 'flv'
        tmpdir = vfs.open(tmpfolder)
        file = tmpdir.open(flv_filename)
        try:
            data = file.read()
        finally:
            file.close()
        
        #flvfile(filenname, mimetype, body) = 
        # OK return OK if encoded
        flvfile = [flv_filename, mimetype, data, extension] 
        return flvfile
 
    def make_flv_thumbnail(self, destfolder, filename, width):
        thumb_filename = "%s.png" % inputfile
        ffmpegthumbnailer = ['ffmpegthumbnailer', '-i', '%s.flv' % filename, '-o', '%s.png' % filename, '-s', '%s' % width]
        get_pipe(ffmpegthumbnailer, cwd=destfolder)
        return thumbnail
    
    def add_metadata_to_flv(self, destfolder, filename):
        flvtool2 = ['flvtool2', '-U', '%s' % filename]
        get_pipe(flvtool2, cwd=destfolder)

        
###########################################################################
# Register
register_resource_class(VideoEncodingToFLV)
