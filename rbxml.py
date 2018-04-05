import os
from urllib.parse import unquote
import xml.etree.ElementTree as etree


class RBPlaylistBuilder:
    file_header = '#EXTM3U\n'
    location_leader = 'file://'
    extension = 'm3u'

    # build a playlist from RM xml for writing an m3u
    def __init__(self, xml_node):
        self.xml_node = xml_node
        self._set_name()
        self.fname = '{}.{}'.format(self.name, self.extension)
        self._set_tracks()

    def _set_name(self):
        self.name = self.xml_node.attrib['name']
        print("Found playlist {}".format(self.name))

    def _set_tracks(self):
        print("Scanning tracks....")
        self.tracks = []
        for child in self.xml_node:
            track = child.text.replace(self.location_leader, '')
            self.tracks.append(unquote(track))

    def write_m3u(self, dest_dir):
        print("Converting to m3u...")
        fpath = os.path.join(dest_dir, self.fname)
        with open(fpath, 'w') as m3u_f:
            m3u_f.write(self.file_header)
            m3u_f.write('\n'.join(self.tracks))


class RBPlaylistExporter:

    def __init__(self, playlists_xml_path, m3u_dest_dir):
        print('Building playlists from Rhythmbox xml...')
        # get xml from Settings.RB_asdfasdf
        self.playlists_xml_path = playlists_xml_path
        self.m3u_dest_dir = m3u_dest_dir
        self.xml_root = etree.parse(self.playlists_xml_path).getroot()
        self._set_playlists()

    def _set_playlists(self):
        self.playlists = []
        for child in self.xml_root:
            if child.attrib['type'] == 'static':
                self.playlists.append(RBPlaylistBuilder(child))

    def export_m3us(self):
        for pl in self.playlists:
            pl.write_m3u(self.m3u_dest_dir)
