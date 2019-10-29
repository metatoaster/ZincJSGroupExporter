import unittest
import json
from os import listdir
from os.path import exists, join
from tempfile import TemporaryDirectory
from pkg_resources import resource_filename

from zincjs_group_exporter.api import export_threejs_cli


class CliTestCase(unittest.TestCase):

    def setUp(self):
        root = TemporaryDirectory()
        self.addCleanup(root.cleanup)
        self.root = root.name

    def test_create_model(self):
        target = resource_filename('zincjs_group_exporter', 'static/test.exf')
        with open(target, 'r') as fd:
            export_threejs_cli(self.root, [fd])

        outdir = join(self.root, 'output')
        self.assertTrue(exists(outdir))
        self.assertEqual(19, len(listdir(outdir)))

        with open(join(outdir, '0')) as fd:
            root_node = json.load(fd)

        self.assertEqual(root_node[0]['URL'], './output/1')
