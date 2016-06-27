#!/usr/bin/env python3

import sys
import os.path
import xml.etree.ElementTree as eTree
from time import gmtime,strftime


class CVParser:
    outfile = sys.stdout    # TODO open actual file
    xmlroot = None
    lang = 'en'
    html_lang = 'en-GB'
    image_path=''
    uid = 100
    name = ''
    update_time = strftime("%Y-%m-%d", gmtime())
    tags = {}

    def __init__(self, infilepath, csspath):
        tree = eTree.parse(infilepath)
        self.xmlroot = tree.getroot()
        if self.xmlroot.tag != 'cv':
            exit_error('Not a valid CV xml!')

        self.start_file(csspath)

    def write_file(self):
        self.name = self.xmlroot.find('name').text

        self.write_header()

        for i in self.xmlroot.findall('desc'):
            self.write_desc(i.find(self.lang).text)

        for contact in ['phone', 'mail', 'linkedin', 'fbook']:
            element = self.xmlroot.find(contact)
            if element:
                icon = 0
                icon_element = element.find('icon')
                if icon_element is not None:
                    icon = icon_element.text
                self.write_contact_info(element.find(self.lang).text, element.find('val').text, icon)

        for tag in self.xmlroot.findall('tag'):
            self.tags[tag.find('name').text] = ({
                'title': tag.find('title').find(self.lang).text,
                'desc': tag.find('desc').find(self.lang).text
            })

        for section in self.xmlroot.findall('section'):
            self.outfile.write('  <h2 class="cvhead">\n')
            if 'icon' in section.attrib:
                self.outfile.write('    <div class="icon">\n'
                                   '      <img src="' + self.image_path + section.attrib['icon'] + '"/>\n'
                                   '    </div>\n')
            self.outfile.write('    ' + section.find('title').find(self.lang).text + '\n'
                               '  </h2>\n')

            for item in section.findall('item') + section.findall('li'):
                title = item.find('title').find(self.lang).text

                if 'years' in item.find('title').attrib:
                    title = item.find('title').attrib['years'] + ' ' + title

                title_tag = 'popuptitle'
                if item.tag == 'li':
                    title_tag += ' li'

                if 'id' in item.attrib:
                    uid = item.attrib['id']
                else:
                    uid = self.uid.__str__()
                    self.uid+=1

                self.outfile.write('  <div class="popupcontainer">\n'
                                   '    <div id="' + uid + '" class="' + title_tag + '">\n'
                                   '      ' + title + '\n'
                                   '    </div>\n')
                content = item.find('content')
                if content is not None:
                    content = content.find(self.lang)
                    if content is not None:
                        self.outfile.write('    <div class="popupcontent">\n'
                                           '      ' + self.content_string_from_element(content) + '\n')
                        if item.find('image') is not None:
                            self.outfile.write('      <div class="images">\n')
                            for image in item.findall('image'):
                                self.outfile.write('        <a href="' + self.image_path + image.find('url').text +
                                           '" class="lightbox" title="' + image.find(self.lang).text +
                                           '"><img src="' + self.image_path + image.find('url').text +
                                           '" style="max-width: 100px; max-height: 100px; margin: 3px;"/></a>')
                            self.outfile.write('      </div>\n')
                        self.outfile.write('    </div>\n')

                self.outfile.write('  </div>\n')

            for content in section.findall('content'):
                self.outfile.write(content.find(self.lang).text)

    def __del__(self):
        self.finish_file()

    def start_file(self, css):
        self.outfile.write('<!DOCTYPE html>\n'
                           '<html lang="' + self.html_lang + '">\n'
                           '<head>\n'
                           '  <meta charset="utf-8">\n'
                           '  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n'
                           '  <title>' + self.name + '</title>\n')
        if css:
            self.outfile.write('  <link href="' + css +'" rel="stylesheet" type="text/css" />\n')
        self.outfile.write('</head>\n'
                           '<body>\n')

    def finish_file(self):
        self.outfile.write('</body>\n'
                           '</html>\n')

    def write_header(self):
        self.outfile.write('  <p align="right">' + self.update_time + '</p>\n')
        self.outfile.write('  <h1>' + self.name + '</h1>\n')

    def write_desc(self, text):
        self.outfile.write('  <span class="profile">' + text + '</span>\n')

    def write_contact_info(self, key, value, image):
        self.outfile.write('  <p class="contact">\n')
        if image:
            self.outfile.write('    <img class="cv-contact" title="' + key + '" src="' + self.image_path + image + '"/>\n')
        self.outfile.write('    ' + key + ': <strong>' + value + '</strong>\n'
                           '  </p>\n')

    def content_string_from_element(self, element):
        s = eTree.tostring(element).decode(encoding='utf-8')
        s = s[s.index('>') + 1 : s.rfind('<')]
        return s

def get_paramsetting(name):
    for arg in sys.argv:
        if arg.startswith('--' + name + '='):
            return arg[name.__len__() + 3:]
    return None

def print_usage():
    sys.stdout.write('Usage:\n'
                     '  cyc.py <input-xml-file> [<output-folder>] [--language=<en|hu|...>]\n'
                     '      [--image-path=<path>] [--css=<path>]')


def exit_error(message, _print_usage):
    if _print_usage:
        print_usage()

    sys.stderr.write(message + '\n')
    exit(-1)


def main():
    if sys.argv.__len__() > 1:
        input_file = sys.argv[1]
        if not os.path.isfile(input_file):
            exit_error('Input file does not exist!', 1)

        css = get_paramsetting('css')

        parser = CVParser(input_file, css)

        lang = get_paramsetting('language')
        if lang:
            parser.lang = lang


        image_path = get_paramsetting('image-path')
        if image_path:
            parser.image_path = image_path

        parser.write_file()
    else:
        exit_error('No input file set!', 1)


main()
