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

    def get_size_and_ratio(self, filename):
        """Return the width, height and ratio of the filename (a video)
        Need the "ffmpeg" cli to be on the PATH
        """
        #dirname = "." 
        # The command to get the video ratio
        command = ['ffmpeg', '-i', filename]

        #output = get_pipe(command, cwd=dirname).read()
        #popen = Popen(command, stdout=PIPE, stderr=PIPE, cwd=dirname)
        popen = Popen(command, stdout=PIPE, stderr=PIPE)
        errno = popen.wait()
        output = popen.stderr.read()

        if output is not None:    
            m = re.search('Video: [^\\n]*\\n', output)
            m = m.group(0).replace('Video: ', '').replace('\n', '').split(', ')
            
            size = m[2].split('x')
            ratio = float(size[0])/float(size[1])
            #ratio =  { 'width': size[0], 'height': size[1], 'ratio': ratio }
            ratio =  [size[0], size[1], ratio]
        else:
            ratio = "Cannot calculate the Video size and ratio"
        return ratio
    
    def get_ratio(self, dirname, filename):
        """Return the ratio of the filename (a video)
        Need the "ffmpeg" cli to be on the PATH
        """
        
        # The command to get the video ratio
        command = ['ffmpeg', '-i', filename]

        #output = get_pipe(command, cwd=dirname).read()
        popen = Popen(command, stdout=PIPE, stderr=PIPE, cwd=dirname)
        errno = popen.wait()
        output = popen.stderr.read()
        """
        pprint('===output==')
        pprint(output)
        pprint('===isinstance==')
        pprint('%s' % isinstance(output, basestring)) 
        """
        if output is not None:    
            m = re.search('Video: [^\\n]*\\n', output)
            #pprint('%s' % m.group(0))
            m = m.group(0).replace('Video: ', '').replace('\n', '').split(', ')
            """
            pprint('===m===')
            pprint('%s' % m)
            """
            size = m[2].split('x')
            ratio = float(size[0])/float(size[1])
            width = str(size[0])
            height = str(size[1])
            
        else:
            ratio = "Cannot calculate the Video ratio"
        return ratio

    def encode_avi_to_flv(self, tmpfolder, inputfile, name, width):
        # name is unique in this thread
        # inputfile = original file name
        # outputfile = the name variable, unique name
        flv_filename = "%s.flv" % name
        ratio = self.get_ratio(tmpfolder, inputfile)
        height = int(round(float(width)/ratio))
        """
        pprint('===height===')
        pprint('%s' % height)
        pprint('===width===')
        pprint('%s' % width)
        """
        # Use -sameq to keep input video quality
        """
        ffmpeg = ['ffmpeg', '-i', '%s' % inputfile, '-acodec', 'mp3', '-ar', '22050',
            '-ab', '32', '-f', 'flv', '-s', '%sx%s' % (width, height),
            '-b', '576000', flv_filename]
        """
        ffmpeg = ['ffmpeg', '-i', '%s' % inputfile, '-acodec', 'mp3', '-ar', '22050',
            '-ab', '32', '-f', 'flv', '-s', '%sx%s' % (width, height),
            '-sameq', flv_filename]
        get_pipe(ffmpeg, cwd=tmpfolder)

        self.add_metadata_to_flv(tmpfolder, flv_filename)

        self.make_flv_thumbnail(tmpfolder, name, width)

        tmpdir = vfs.open(tmpfolder)
        # Copy the flv content to a data variable
        flv_file = tmpdir.open(flv_filename)
        try:
            flv_data = flv_file.read()
        finally:
            flv_file.close()
        # Copy the thumb content
        thumb_file = tmpdir.open('%s.png' % name)
        try:
            thumb_data = thumb_file.read()
        finally:
            thumb_file.close()

        # Return a FLV file and a PNG thumbnail
        flvfile = [flv_filename, 'video/x-flv', flv_data, 'flv']
        flvthumb = ['thumb_%s' % name, 'image/png', thumb_data, 'png']
        
        if((len(flv_data) == 0) or (len(thumb_data) == 0)):
             #exit
            encoded = None
        else:
            encoded = {'flvfile':flvfile, 'flvthumb':flvthumb}

        return encoded
 
    def make_flv_thumbnail(self, destfolder, filename, width):
        ffmpegthumbnailer = ['ffmpegthumbnailer', '-i', '%s.flv' % filename, '-o', '%s.png' % filename, '-s', '%s' % width]
        get_pipe(ffmpegthumbnailer, cwd=destfolder)
    
    def add_metadata_to_flv(self, destfolder, filename):
        flvtool2 = ['flvtool2', '-U', '%s' % filename]
        get_pipe(flvtool2, cwd=destfolder)

        
###########################################################################
# Register
register_resource_class(VideoEncodingToFLV)
