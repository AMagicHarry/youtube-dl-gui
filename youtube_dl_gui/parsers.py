#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""Youtubedlg module responsible for parsing the options. """

from __future__ import unicode_literals

import os.path

from .utils import (
    remove_shortcuts,
    to_string
)


class OptionHolder(object):

    """Simple data structure that holds informations for the given option.

    Args:
        name (string): Option name. Must be a valid option name
            from the optionsmanager.OptionsManager class.
            See optionsmanager.OptionsManager load_default() method.

        flag (string): The option command line switch.
            See https://github.com/rg3/youtube-dl/#options

        default_value (any): The option default value. Must be the same type
            with the corresponding option from the optionsmanager.OptionsManager
            class.

        requirements (list): The requirements for the given option. This
            argument is a list of strings with the name of all the options
            that this specific option needs. For example 'subs_lang' needs the
            'write_subs' option to be enabled.

    """

    def __init__(self, name, flag, default_value, requirements=None):
        self.name = name
        self.flag = flag
        self.requirements = requirements
        self.default_value = default_value

    def is_boolean(self):
        """Returns True if the option is a boolean switch else False. """
        return type(self.default_value) is bool

    def check_requirements(self, options_dict):
        """Check if the required options are enabled.

        Args:
            options_dict (dictionary): Dictionary with all the options.

        Returns:
            True if any of the required options is enabled else False.

        """
        if self.requirements is None:
            return True

        return any([options_dict[req] for req in self.requirements])


class OptionsParser(object):

    """Parse optionsmanager.OptionsManager options.

    This class is responsible for turning some of the youtube-dlg options
    to youtube-dl command line options.

    """

    def __init__(self):
        self._ydl_options = [
            OptionHolder('playlist_start', '--playlist-start', 1),
            OptionHolder('playlist_end', '--playlist-end', 0),
            OptionHolder('max_downloads', '--max-downloads', 0),
            OptionHolder('username', '-u', ''),
            OptionHolder('password', '-p', ''),
            OptionHolder('video_password', '--video-password', ''),
            OptionHolder('retries', '-R', 10),
            OptionHolder('proxy', '--proxy', ''),
            OptionHolder('user_agent', '--user-agent', ''),
            OptionHolder('referer', '--referer', ''),
            OptionHolder('ignore_errors', '-i', False),
            OptionHolder('write_description', '--write-description', False),
            OptionHolder('write_info', '--write-info-json', False),
            OptionHolder('write_thumbnail', '--write-thumbnail', False),
            OptionHolder('min_filesize', '--min-filesize', 0),
            OptionHolder('max_filesize', '--max-filesize', 0),
            OptionHolder('write_all_subs', '--all-subs', False),
            OptionHolder('write_auto_subs', '--write-auto-sub', False),
            OptionHolder('write_subs', '--write-sub', False),
            OptionHolder('keep_video', '-k', False),
            OptionHolder('restrict_filenames', '--restrict-filenames', False),
            OptionHolder('save_path', '-o', ''),
            OptionHolder('embed_subs', '--embed-subs', False, ['write_auto_subs', 'write_subs']),
            OptionHolder('to_audio', '-x', False),
            OptionHolder('audio_format', '--audio-format', '', ['to_audio']),
            OptionHolder('video_format', '-f', '0'),
            OptionHolder('subs_lang', '--sub-lang', '', ['write_subs']),
            OptionHolder('audio_quality', '--audio-quality', '5', ['to_audio'])
        ]

    def parse(self, options_dictionary):
        """Parse optionsmanager.OptionsManager options.

        Parses the given options to youtube-dl command line arguments.

        Args:
            options_dictionary (dictionary): Dictionary with all the options.

        Returns:
            List of strings with all the youtube-dl command line options.

        """
        options_list = ['--newline']

        # Create a copy of options_dictionary
        # We don't want to edit the original options dictionary
        # and change some of the options values like 'save_path' etc..
        options_dict = options_dictionary.copy()

        self._build_savepath(options_dict)
        self._build_videoformat(options_dict)
        self._build_filesizes(options_dict)

        # Parse basic youtube-dl command line options
        for option in self._ydl_options:
            if option.check_requirements(options_dict):
                value = options_dict[option.name]

                if value != option.default_value:
                    options_list.append(option.flag)

                    if not option.is_boolean():
                        options_list.append(to_string(value))

        # Parse cmd_args
        for option in options_dict['cmd_args'].split():
            options_list.append(option)

        return options_list

    def _build_savepath(self, options_dict):
        """Build the save path.

        We use this method to build the value of the 'save_path' option and
        store it back to the options dictionary.

        Args:
            options_dict (dictionary): Copy of the original options dictionary.

        """
        save_path = remove_shortcuts(options_dict['save_path'])

        if options_dict['output_format'] == 'id':
            save_path = os.path.join(save_path, '%(id)s.%(ext)s')
        elif options_dict['output_format'] == 'title':
            save_path = os.path.join(save_path, '%(title)s.%(ext)s')
        else:
            save_path = os.path.join(save_path, options_dict['output_template'])

        options_dict['save_path'] = save_path

    def _build_videoformat(self, options_dict):
        """Build the video format.

        We use this method to build the value of the 'video_format' option and
        store it back to the options dictionary.

        Args:
            options_dict (dictionary): Copy of the original options dictionary.

        """
        if options_dict['video_format'] != '0' and options_dict['second_video_format'] != '0':
            options_dict['video_format'] = options_dict['video_format'] + '+' + options_dict['second_video_format']

    def _build_filesizes(self, options_dict):
        """Build the filesize options values.

        We use this method to build the values of 'min_filesize' and
        'max_filesize' options and store them back to options dictionary.

        Args:
            options_dict (dictionary): Copy of the original options dictionary.

        """
        if options_dict['min_filesize']:
            options_dict['min_filesize'] = to_string(options_dict['min_filesize']) + options_dict['min_filesize_unit']

        if options_dict['max_filesize']:
            options_dict['max_filesize'] = to_string(options_dict['max_filesize']) + options_dict['max_filesize_unit']
