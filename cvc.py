#!/usr/bin/env python3

import sys
import os.path
import xml.etree.ElementTree as eTree
from time import gmtime,strftime

class CVParser:
    outfile = None
    xmlroot = None
    lang = 'en'
    html_lang = 'en-GB'
    headless = False
    image_path=''
    uid = 100
    name = ''
    update_time = strftime("%Y-%m-%d", gmtime())
    tags = {}
    images = []

    def __init__(self, infilepath, outfile, is_headless=False, css_array=[], js_array=[]):
        tree = eTree.parse(infilepath)
        self.xmlroot = tree.getroot()
        if self.xmlroot.tag != 'cv':
            exit_error('Not a valid CV xml!')
        if outfile is not None:
            self.outfile = open(outfile, 'w')
        else:
            self.outfile = sys.stdout # use default output otherwise

        self.headless = is_headless
        self.start_file(css_array, js_array)

    def write_file(self):
        self.name = self.xmlroot.find('name').text

        for i in self.xmlroot.findall('profile-img'):
            self.images.append(self.image_path + i.find('url').text)
        self.write_header()

        for i in self.xmlroot.findall('desc'):
            self.write_desc(i.find(self.lang).text)

        for contact in self.xmlroot.findall('contact'):
            if contact:
                icon = 0
                icon_element = contact.find('icon')
                if icon_element is not None:
                    icon = icon_element.text

                href = None
                type_element = contact.find('type')
                if type_element is not None:
                    if type_element.text == 'email':
                        href = 'mailto:' + contact.find('val').text
                    elif type_element.text == 'url':
                        href = contact.find('val').text
                self.write_contact_info(contact.find(self.lang).text, contact.find('val').text, icon, href)

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
                    title = item.find('title').attrib['years'].replace('\\nbsp', '&nbsp;') + ' ' + title

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

    def start_file(self, css_array=[], js_array=[]):
        if not self.headless:
            self.outfile.write('<!DOCTYPE html>\n'
                               '<html lang="' + self.html_lang + '">\n'
                               '<head>\n'
                               '  <meta charset="utf-8">\n'
                               '  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />\n'
                               '  <title>' + self.name + '</title>\n')
            for css in css_array:
                self.outfile.write('  <link href="' + css + '" rel="stylesheet" type="text/css" />\n')
            for js in js_array:
                self.outfile.write('  <script type="text/javascript" src="' + js + '"></script>')
            self.outfile.write('</head>\n'
                               '<body>\n')

    def finish_file(self):
        if not self.headless:
            self.outfile.write('</body>\n'
                               '</html>\n')

    def write_header(self):
        self.outfile.write('  <p align="right">' + self.update_time + '</p>\n')
        if self.images.__len__() > 0:
            self.outfile.write('<a href="' + self.images[0] + '" class="lightbox"><img src="' + self.images[0] + '" class="profimg"/></a>\n')
        self.outfile.write('  <h1>' + self.name + '</h1>\n')

    def write_desc(self, text):
        self.outfile.write('  <span class="profile">' + text + '</span><br/>\n')

    def write_contact_info(self, key, value, image, href = None):
        self.outfile.write('  <p class="contact">\n')
        if image:
            self.outfile.write('    <img class="cv-contact" title="' + key + '" src="' + self.image_path + image + '"/>\n')
        if href:
            value = '<a href="' + href + '">' + value + '</a>'
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
                     '  cyc.py <input-xml-file> <output-file> [--format=<html|html-headless>] [--language=<en|hu|...>]\n'
                     '      [--image-path=<path>] [--css=<path>] [--js=<path>]\n'
                     '\n'
                     '  Image path, css & js are used in html to link to files, relative to\n'
                     '  the webservers root folder.\n'
                     '\n'
                     '  You may use --css1, --css2 etc. and --js1 etc. to include multiple files\n'
                     '  in the <head> of the document. There is no option to write inline css or\n'
                     '  js in the command line.\n\n')


def exit_error(message, _print_usage):
    sys.stderr.write('Error: ' + message + '\n\n')

    if _print_usage:
        print_usage()
    exit(-1)


def main():
    if sys.argv.__len__() > 1:
        output_file = None
        input_file = sys.argv[1]
        if not os.path.isfile(input_file):
            exit_error('Input file does not exist!', 1)

        if sys.argv.__len__() > 2:
            if not sys.argv[2].startswith('-'):
                output_file = sys.argv[2]

        headless = False
        outformat = get_paramsetting('format')
        if outformat:
            if outformat == 'html-headless':
                headless = True
            elif outformat != 'html':
                exit_error('Invalid format \'%s\'' % outformat)

        css_array = []
        css = get_paramsetting('css')
        if css: css_array.append(css)
        i = 1
        while True:
            css = get_paramsetting('css%d' % i)
            if not css: break
            css_array.append(css)
            i += 1

        js_array = []
        js = get_paramsetting('js')
        if js: css_array.append(js)
        i = 1
        while True:
            js = get_paramsetting('js%d' % i)
            if not js: break
            js_array.append(js)
            i += 1

        parser = CVParser(input_file, output_file, headless, css_array, js_array)

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
