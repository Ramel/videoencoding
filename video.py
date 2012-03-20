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
import sys, os

# Import from itools
from itools.gettext import MSG
from itools.web import ERROR
from itools.core.utils import get_pipe
from itools import fs
from itools.fs import vfs

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

    def get_video_codec(self, filename, vcodec="h264"):
        """Return a boolean value of the asked codec video encoding
        """
        command = ['ffmpeg', '-i', filename]
        popen = Popen(command, stdout=PIPE, stderr=PIPE)
        errno = popen.wait()
        output = popen.stderr.read()

        if output is not None:
            print("output = %s" % output)
            m = re.search('Video: [^\\n]*\\n', output)
            print('%s' % m.group(0))
            m = m.group(0).replace('Video: ','').replace('\n','').split(', ')
            print('%s' % m)
        else:
            vcodec = "Cannot retrieve the video codec, sorry!"

        return vcodec


    def get_size_and_ratio(self, filename):
        """Return the width, height and ratio of the filename (a video)
        Need the "ffmpeg" cli to be on the PATH
        """
        # The command to get the video ratio
        command = ['ffmpeg', '-i', filename]

        popen = Popen(command, stdout=PIPE, stderr=PIPE)
        errno = popen.wait()
        output = popen.stderr.read()

        if output is not None:
            size = self.get_size(output)
            ratio = float(size[0])/float(size[1])
            ratio = [size[0], size[1], ratio]
        else:
            ratio = "Cannot calculate the Video size and ratio"

        return ratio


    def isodd(self, x):
        return x & 1


    def iseven(self, x):
        #not x & 1
        return float(x) % 2 == 0


    def check_resize_height_is_even(self, outwidth, width, height):
        resize = float(outwidth) * float(height) / float(width)
        if self.iseven(resize):
            return True
        else:
            return False


    def get_next_even_height(self, outwidth, width, height):
        count = 0
        while (count < 10):
            count = count + 1
            height = int(height) + 1
            outputsize = float(outwidth) * height / float(width)
            print("outputsize = %s (%s * %s / %s)" % (
                                    outputsize, outwidth, height, width))
            print("iseven(%s) = %s" % (outputsize, self.iseven(outputsize)))
            if self.iseven(outputsize):
                return int(outputsize)
            else:
                continue
        return False


    def get_size(self, output):
        m = re.search('Video: [^\\n]*\\n', output)
        #pprint('%s' % m.group(0))
        m = m.group(0).replace('Video: ','').replace('\n','').split(', ')
        #pprint("m = %s" % m)
        # Sometime it returns a '[blabla]', remove it
        size = m[2].split('[')
        size = size[0].split('x')
        #ratio = float(size[0])/float(size[1])

        size = [size[0], size[1].replace(' ','')]
        return size


    def get_size_frompath(self, dirname, filename):
        """Return the size of the filename (a video)
        Need the "ffmpeg" cli to be on the PATH
        """
        # The command to get the video ratio
        command = ['ffmpeg', '-i', filename]
        popen = Popen(command, stdout=PIPE, stderr=PIPE, cwd=dirname)
        errno = popen.wait()
        output = popen.stderr.read()
        if output is not None:
            size = self.get_size(output)
        else:
            size = [ None, "Cannot calculate the Video size!" ]
        return size


    def get_ratio(self, dirname, filename):
        """Return the ratio of the filename (a video)
        Need the "ffmpeg" cli to be on the PATH
        """

        # The command to get the video ratio
        command = ['ffmpeg', '-i', filename]
        popen = Popen(command, stdout=PIPE, stderr=PIPE, cwd=dirname)
        errno = popen.wait()
        output = popen.stderr.read()
        if output is not None:
            size = self.get_size(output)
            ratio = float(size[0])/float(size[1])
        else:
            ratio = "Cannot calculate the Video ratio"
        return ratio


    def encode_video_to_flv(self, tmpfolder, inputfile,
                                    name, width, encode=False):
        """ Take a *inputfile* video, taking is *name*, encode it in flv inside
        the *tmpfolder*, at given *width*. Return *video_low* and a
        *video_low_thumb* files of the original file
        """
        flv_filename = "%s.flv" % name
        ratio = self.get_ratio(tmpfolder, inputfile)
        height = int(round(float(width)/ratio))

        original_W, original_H = self.get_size_frompath(tmpfolder, inputfile)
        print("original_W = %s, original_H = %s" % (original_W, original_H))
        if original_W is not None:
            if self.check_resize_height_is_even(width, original_W, original_H):
                even = True
                crop = False
            else:
                even = self.get_next_even_height(
                                        width, original_W, original_H)
                crop = even * float(original_W) / float(width)
                crop = crop - int(original_H)
                height = even

        if not even:
            msg = u"The ratio width/height is not even, so the video cannot be encoded!"
            raise NotImplementedError, "%s" % msg

        else:
            if not encode:
                #TWO PASS
                # Pass one
                ffmpeg = ['ffmpeg', '-i', '%s' % inputfile, '-sameq', '-s',
                          '%sx%s' % (width, height), '-pass', '1', '-vcodec', 'libx264',
                          '-fpre', '/usr/share/ffmpeg/libx264-normal.ffpreset',
                          '-b', '512k',
                          '-bt', '512k',
                          '-threads', '0', '-f', 'rawvideo', '-f', 'mp4', '-an', '-y',
                          '/dev/null']
                print("Pass 1 : ffmpeg = %s" % ffmpeg)
                get_pipe(ffmpeg, cwd=tmpfolder)
                # Pass two
                ffmpeg = ['ffmpeg', '-i', '%s' % inputfile, '-sameq', '-s',
                          '%sx%s' % (width, height), '-f', 'mp4', '-pass', '2',
                          '-acodec', 'libfaac', '-ab', '128k', '-ac', '2',
                          '-vcodec', 'libx264',
                          '-fpre', '/usr/share/ffmpeg/libx264-normal.ffpreset',
                          '-b', '512k', '-bt', '512k',
                          '-threads',  '0', '-metadata', 'author="Tchack"', '-metadata',
                          'copyright="Tous droits réservés - Tchack/ALUMA Productions"',
                          flv_filename]
                print("Pass 2 : ffmpeg = %s" % ffmpeg)
                get_pipe(ffmpeg, cwd=tmpfolder)
            
            elif encode == 'one':
                #ONE PASS
                ffmpeg = ['ffmpeg', '-i', '%s' % inputfile, '-acodec', 'libfaac', '-ar', '22050',
                    '-ab', '32k', '-f', 'flv', '-s', '%sx%s' % (width, height),
                    '-sameq', flv_filename]
                get_pipe(ffmpeg, cwd=tmpfolder)

            elif encode == 'one_chroma_faststart':
                tmp_flv_filename = "tmp_%s.flv" % name
                ffmpeg= ['ffmpeg', '-y', '-i', '%s' % inputfile,
                            #'-fpre', '/usr/share/ffmpeg/libx264-hq.ffpreset',
                            '-preset', 'fast',
                            '-s', '%sx%s' % (width, height),
                            '-vcodec', 'libx264',
                            '-b', '512k',
                            '-acodec', 'libfaac',
                            '-ar', '44100',
                            '-ab', '128k',
                            '-coder', 'ac',
                            '-me_method', 'full',
                            '-me_range', '16',
                            '-subq', '5',
                            '-sc_threshold', '40',
                            '-cmp', '+chroma',
                            '-partitions', '+parti4x4+partp8x8+partb8x8',
                            '-i_qfactor', '0.71',
                            '-keyint_min', '25',
                            '-b_strategy', '1',
                            '-g', '250',
                            '-r', '20',
                            '-metadata', 'author="Tchack"',
                            '-metadata', 'copyright="Tous droits réservés - Tchack/ALUMA Productions"',
                            #'-vf', 'crop=in_w:in_h+%s' % int(crop),
                            #tmp_flv_filename]
                            flv_filename]
                if crop:
                    ffmpeg.insert(-1, '-vf')
                    ffmpeg.insert(-1, 'crop=in_w:in_h+%s' % int(crop))

                print("Pass : ffmpeg = %s" % ffmpeg)
                get_pipe(ffmpeg, cwd=tmpfolder)
                #ffmpeg = ['qt-faststart', "\"./%s\"" % tmp_flv_filename, "\"./%s\"" % flv_filename]
                #print("Pass : faststart = %s" % ffmpeg)
                #get_pipe(ffmpeg, cwd=tmpfolder)

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
            # Need to add the PNG to ikaaro

            # Return a FLV file and a PNG thumbnail
            flvfile = ["%s" % name, 'video/x-flv',
                        flv_data, 'flv', width, height]
            flvthumb = ['%s_thumb' % name, 'image/png', thumb_data, 'png']

            if((len(flv_data) == 0) or (len(thumb_data) == 0)):
                 #exit
                encoded = None
            else:
                encoded = {'flvfile':flvfile, 'flvthumb':flvthumb}

            return encoded


    def encode_avi_to_flv(self, tmpfolder, inputfile, name, width):
        """ Take a *inputfile* video, tafking is *name*, encode it in flv inside
        the *tmpfolder*, at given *width*.
        """
        flv_filename = "%s.flv" % name
        ratio = self.get_ratio(tmpfolder, inputfile)
        height = int(round(float(width)/ratio))

        ffmpeg = ['ffmpeg', '-i', '%s' % inputfile, '-acodec', 'libfaac', '-ar', '22050',
            '-ab', '32k', '-f', 'flv', '-s', '%sx%s' % (width, height),
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
        # Need to add the PNG to ikaaro

        # Return a FLV file and a PNG thumbnail
        flvfile = [flv_filename, 'video/x-flv', flv_data, 'flv']
        flvthumb = ['thumb_%s' % name, 'image/png', thumb_data, 'png']

        if((len(flv_data) == 0) or (len(thumb_data) == 0)):
             #exit
            encoded = None
        else:
            encoded = {'flvfile':flvfile, 'flvthumb':flvthumb}

        return encoded


    def make_thumbnail_only(self, tmpfolder, inputfile, name, width):
        """ Take a *inputfile* video, using is *name*, create a thumbnail as a
        PNG file in the *tmpfolder*, at given *width*.
        """
        flv_filename = "%s" % name
        ratio = self.get_ratio(tmpfolder, inputfile)
        height = int(round(float(width)/ratio))

        self.add_metadata_to_flv(tmpfolder, flv_filename)
        self.make_thumbnail(tmpfolder, name, width)

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
        # Need to add the PNG to ikaaro

        # Return a PNG thumbnail
        flvthumb = ['%s_thumb' % name, 'image/png', thumb_data, 'png']

        if(len(thumb_data) == 0):
             #exit
            thumbnail = None
        else:
            thumbnail = {'flvthumb':flvthumb}

        return thumbnail


    def make_flv_thumbnail(self, destfolder, filename, width):
        """ Create a Thumb at t(ime)=0 (percent or time)
        """
        ffmpegthumbnailer = ['ffmpegthumbnailer', '-i', '%s.flv' % filename,
    '-o', '%s.png' % filename, '-t', '0', '-s', '%s' % width]
        get_pipe(ffmpegthumbnailer, cwd=destfolder)

    def make_thumbnail(self, destfolder, filename, width):
        """ Create a Thumb at t(ime)=0 (percent or time)
        """
        ffmpegthumbnailer = ['ffmpegthumbnailer', '-i', '%s' % filename,
    '-o', '%s.png' % filename, '-t', '0', '-s', '%s' % width]
        get_pipe(ffmpegthumbnailer, cwd=destfolder)

    def add_metadata_to_flv(self, destfolder, filename):
        """ Add some Metadata to the FLV file, as ffmpeg is not doing that well.
        """
        flvtool2 = ['flvtool2', '-U', '%s' % filename]
        get_pipe(flvtool2, cwd=destfolder)


###########################################################################
# Register
register_resource_class(VideoEncodingToFLV)
