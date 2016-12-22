#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Contains test cases for the DownloadItem object."""

from __future__ import unicode_literals

import sys
import os.path
import unittest

PATH = os.path.realpath(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(PATH)))

try:
    from youtube_dl_gui.downloadmanager import DownloadItem
except ImportError as error:
    print error
    sys.exit(1)


class TestItemInit(unittest.TestCase):

    """Test case for DownloadItem init."""

    def test_init(self):
        url = "url"
        options = ["-f", "flv"]

        ditem = DownloadItem(url, options)

        self.assertEqual(ditem.stage, "Queued")
        self.assertEqual(ditem.url, url)
        self.assertEqual(ditem.options, options)
        self.assertEqual(ditem.object_id, hash(url + unicode(options)))

        self.assertEqual(ditem.path, "")
        self.assertEqual(ditem.filenames, [])
        self.assertEqual(ditem.extensions, [])
        self.assertEqual(ditem.filesizes, [])

        self.assertEqual(
            ditem.progress_stats,
            {"filename": url,
             "extension": "-",
             "filesize": "-",
             "percent": "0%",
             "speed": "-",
             "eta": "-",
             "status": "Queued",
             "playlist_size": "",
             "playlist_index": ""}
        )


class TestGetFiles(unittest.TestCase):

    """Test case for DownloadItem get_files method."""

    def setUp(self):
        self.ditem = DownloadItem("url", ["-f", "flv"])

    def test_get_files(self):
        path = os.path.join("/home", "user", "downloads")

        self.ditem.path = path
        self.ditem.filenames = ["file1", "file2"]
        self.ditem.extensions = [".mp4", ".m4a"]

        self.assertEqual(self.ditem.get_files(), [os.path.join(path, "file1" + ".mp4"), os.path.join(path, "file2" + ".m4a")])

    def test_get_files_no_data(self):
        self.assertEqual(self.ditem.get_files(), [])


class TestItemComparison(unittest.TestCase):

    """Test case for DownloadItem __eq__ method."""

    def test_equal_true(self):
        ditem1 = DownloadItem("url", ["-f", "flv"])
        ditem2 = DownloadItem("url", ["-f", "flv"])

        self.assertTrue(ditem1 == ditem2)

    def test_equal_false(self):
        ditem1 = DownloadItem("url", ["-f", "flv"])
        ditem2 = DownloadItem("url2", ["-f", "flv"])

        self.assertFalse(ditem1 == ditem2)

        ditem1 = DownloadItem("url", ["-f", "flv"])
        ditem2 = DownloadItem("url", ["-f", "mp4"])

        self.assertFalse(ditem1 == ditem2)


class TestSetItemStage(unittest.TestCase):

    """Test case for DownloadItem stage setter."""

    def setUp(self):
        self.ditem = DownloadItem("url", ["-f", "flv"])

    def test_set_stage_valid(self):
        self.ditem.stage = "Queued"
        self.assertEqual(self.ditem.stage, "Queued")
        self.assertEqual(self.ditem.progress_stats["status"], "Queued")

        self.ditem.stage = "Active"
        self.assertEqual(self.ditem.stage, "Active")
        self.assertEqual(self.ditem.progress_stats["status"], "Pre Processing")

        self.ditem.stage = "Completed"
        self.assertEqual(self.ditem.stage, "Completed")
        self.assertEqual(self.ditem.progress_stats["status"], "Finished")

        self.ditem.stage = "Paused"
        self.assertEqual(self.ditem.stage, "Paused")
        self.assertEqual(self.ditem.progress_stats["status"], "Paused")

        self.ditem.stage = "Error"
        self.assertEqual(self.ditem.stage, "Error")
        self.assertEqual(self.ditem.progress_stats["status"], "Error")

    def test_set_stage_invalid(self):
        raised = False

        try:
            self.ditem.stage = "some other status"
        except ValueError:
            raised = True

        self.assertTrue(raised)


class TestUpdateStats(unittest.TestCase):

    """Test case for DownloadItem update_stats method."""

    def setUp(self):
        self.ditem = DownloadItem("url", ["-f", "flv"])

    def test_update_stats(self):
        path = os.path.join("/home", "user")

        self.ditem.update_stats({"filename": "somefilename",
                                 "extension": ".mp4",
                                 "filesize": "9.45MiB",
                                 "percent": "2.0%",
                                 "speed": "200.00KiB/s",
                                 "eta": "00:38",
                                 "status": "Downloading",
                                 "path": path,
                                 "playlist_size": "10",
                                 "playlist_index": "1"})

        self.assertEqual(self.ditem.path, path)
        self.assertEqual(self.ditem.filenames, ["somefilename"])
        self.assertEqual(self.ditem.extensions, [".mp4"])
        self.assertEqual(self.ditem.filesizes, [9909043.20])
        self.assertEqual(
            self.ditem.progress_stats,
            {"filename": "somefilename",
             "extension": ".mp4",
             "filesize": "9.45MiB",
             "percent": "2.0%",
             "speed": "200.00KiB/s",
             "eta": "00:38",
             "status": "Downloading",
             "playlist_size": "10",
             "playlist_index": "1"}
        )

        self.ditem.update_stats({"filename": "someotherfilename",
                                 "extension": ".m4a",
                                 "percent": "50.0%",
                                 "filesize": "2.00MiB",
                                 "playlist_index": "2"})

        # This update should not affect the filesizes
        self.ditem.update_stats({ "percent": "65.0%",
                                 "filesize": "2.00MiB",
                                 "playlist_index": "2"})

        self.assertEqual(self.ditem.filenames, ["somefilename", "someotherfilename"])
        self.assertEqual(self.ditem.extensions, [".mp4", ".m4a"])
        self.assertEqual(self.ditem.filesizes, [9909043.20, 2097152.00])
        self.assertEqual(
            self.ditem.progress_stats,
            {"filename": "someotherfilename",
             "extension": ".m4a",
             "filesize": "2.00MiB",
             "percent": "65.0%",
             "speed": "200.00KiB/s",
             "eta": "00:38",
             "status": "Downloading",
             "playlist_size": "10",
             "playlist_index": "2"}
        )

    def test_update_stats_invalid_input(self):
        self.assertRaises(AssertionError, self.ditem.update_stats, [])

    def test_update_stats_empty_strings(self):
        self.ditem.update_stats({"filename": "",
                                 "extension": "",
                                 "filesize": "",
                                 "percent": "",
                                 "speed": "",
                                 "eta": "",
                                 "status": "",
                                 "playlist_size": "",
                                 "playlist_index": ""})

        self.assertEqual(
            self.ditem.progress_stats,
            {"filename": "url",
             "extension": "-",
             "filesize": "-",
             "percent": "0%",
             "speed": "-",
             "eta": "-",
             "status": "Queued",
             "playlist_size": "",
             "playlist_index": ""}
        )

    def test_update_stats_not_string(self):
        self.ditem.update_stats({"filename": None, "status": 1234, "eta": False})

        self.assertEqual(self.ditem.progress_stats["filename"], "url")
        self.assertEqual(self.ditem.progress_stats["status"], "Queued")
        self.assertEqual(self.ditem.progress_stats["eta"], "-")


class TestDownloadItemPrivate(unittest.TestCase):

    """Test case for private method of the DownloadItem."""

    def test_set_stage(self):
        ditem = DownloadItem("url", ["-f", "flv"])

        active_status = ["Pre Processing", "Downloading", "Post Processing"]
        complete_status = ["Finished", "Warning", "Already Downloaded"]
        error_status = ["Error", "Stopped", "Filesize Abort"]

        for status in active_status:
            ditem._set_stage(status)
            self.assertEqual(ditem.stage, "Active")

        for status in complete_status:
            ditem._set_stage(status)
            self.assertEqual(ditem.stage, "Completed")

        for status in error_status:
            ditem._set_stage(status)
            self.assertEqual(ditem.stage, "Error")

    def test_calc_post_proc_size(self):
        # REFACTOR Not an actual method
        # should transfer to TestUpdateStats
        ditem = DownloadItem("url", ["-f", "flv"])

        ditem.update_stats({"filename": "file.f123",
                            "extension": ".webm",
                            "filesize": "10.00MiB",
                            "percent": "75.0%",
                            "speed": "123.45KiB/s",
                            "eta": "N/A",
                            "status": "Downloading",
                            "path": "/home/user"})

        ditem.update_stats({"filename": "file.f456",
                            "extension": ".m4a",
                            "filesize": "3.45MiB",
                            "percent": "96.0%",
                            "speed": "222.22KiB/s",
                            "eta": "N/A",
                            "status": "Downloading",
                            "path": "/home/user"})

        # Mimic youtube-dl post process behaviour
        ditem.update_stats({"filename": "file",
                            "extension": ".webm",
                            "percent": "100%",
                            "speed": "",
                            "eta": "",
                            "status": "Post Processing"})

        self.assertEqual(ditem.filesizes, [10485760.00, 3617587.20, 14103347.20])

        self.assertEqual(
            ditem.progress_stats,
            {"filename": "file",
             "extension": ".webm",
             "filesize": "13.45MiB",
             "percent": "100%",
             "speed": "-",
             "eta": "-",
             "status": "Post Processing",
             "playlist_size": "",
             "playlist_index": ""}
        )


class TestReset(unittest.TestCase):

    """Test case for the DownloadItem reset method."""

    def setUp(self):
        self.ditem = DownloadItem("url", ["-f", "flv"])

    def test_reset_completed_stage(self):
        self.ditem._stage = "Completed"
        self.ditem.path = os.path.join("/home", "user")
        self.ditem.filenames = ["file"]
        self.ditem.extensions = [".mp4"]
        self.ditem.filesizes = [123456.00]
        self.ditem.progress_stats = {
            "filename": "file",
            "extension": ".mp4",
            "filsize": "6.66MiB",
            "percent": "100%",
            "speed": "-",
            "eta": "00:00",
            "status": "Finished",
            "playlist_size": "",
            "playlist_index": ""
        }

        self.ditem.reset()

        self.assertEqual(self.ditem._stage, "Queued")
        self.assertEqual(self.ditem.path, "")
        self.assertEqual(self.ditem.filenames, [])
        self.assertEqual(self.ditem.extensions, [])
        self.assertEqual(self.ditem.filesizes, [])
        self.assertEqual(
            self.ditem.progress_stats,
            {"filename": "url",
             "extension": "-",
             "filesize": "-",
             "percent": "0%",
             "speed": "-",
             "eta": "-",
             "status": "Queued",
             "playlist_size": "",
             "playlist_index": ""}
        )

    def test_reset_error_stage(self):
        self.ditem._stage = "Error"
        self.ditem.path = os.path.join("/home", "user")
        self.ditem.filenames = ["file1", "file2", "file"]
        self.ditem.extensions = [".mp4", ".m4a", ".mp4"]
        self.ditem.filesizes = [1234.00, 3421.00, 4655.00]
        self.ditem.progress_stats = {
            "filename": "file",
            "extension": ".mp4",
            "filsize": "9.45MiB",
            "percent": "100%",
            "speed": "-",
            "eta": "00:00",
            "status": "Error",
            "playlist_size": "10",
            "playlist_index": "8"
        }

        self.ditem.reset()

        self.assertEqual(self.ditem._stage, "Queued")
        self.assertEqual(self.ditem.path, "")
        self.assertEqual(self.ditem.filenames, [])
        self.assertEqual(self.ditem.extensions, [])
        self.assertEqual(self.ditem.filesizes, [])
        self.assertEqual(
            self.ditem.progress_stats,
            {"filename": "url",
             "extension": "-",
             "filesize": "-",
             "percent": "0%",
             "speed": "-",
             "eta": "-",
             "status": "Queued",
             "playlist_size": "",
             "playlist_index": ""}
        )

    def test_reset_paused_stage(self):
        self.ditem._stage = "Paused"
        # No need to change filanames, extension, etc
        # since everything in pause state has the default value

        self.ditem.reset()
        self.assertEqual(self.ditem._stage, "Queued")

    def test_reset_active_stage(self):
        self.ditem._stage = "Active"
        self.ditem.path = os.path.join("/home", "user")
        self.ditem.filenames = ["file1"]
        self.ditem.extensions = [".mp4"]
        self.ditem.filesizes = [1234.00]
        self.ditem.progress_stats = {
            "filename": "file1",
            "extension": ".mp4",
            "filsize": "9.45MiB",
            "percent": "75.5%",
            "speed": "200.00KiB/s",
            "eta": "00:10",
            "status": "Downloading"
        }

        self.assertRaises(RuntimeError, self.ditem.reset)


def main():
    unittest.main()


if __name__ == '__main__':
    main()
