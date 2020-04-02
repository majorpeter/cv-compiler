#!/usr/bin/env python3

import sys
import os.path
import xml.etree.ElementTree as eTree
from argparse import ArgumentParser
from time import gmtime,strftime
import html


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
            self.outfile = sys.stdout  # use default output otherwise

        self.headless = is_headless
        self.start_file(css_array, js_array)

    def write_file(self):
        self.name = self.xmlroot.find('name').text

        for i in self.xmlroot.findall('profile-img'):
            self.images.append(self.image_path + i.find('url').text)
        self.write_header()

        for i in self.xmlroot.findall('desc'):
            self.write_desc(i.find(self.lang).text)

        self.outfile.write('  <div id="contact-info">\n')
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
        self.outfile.write('  </div>\n')

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
                title_element = item.find('title')
                title = title_element.find(self.lang).text
                title_prefix = ''
                title_postfix = ''
                list_item = False

                if 'years' in title_element.attrib:
                    title = title_element.attrib['years'].replace('\\nbsp', '&nbsp;') + ' ' + title

                title_class = 'popuptitle'
                if item.tag == 'li':
                    title_class += ' li'
                    list_item = True

                if 'id' in item.attrib:
                    uid = item.attrib['id']
                    has_real_uid = True
                else:
                    uid = self.uid.__str__()
                    self.uid+=1
                    has_real_uid = False

                content = item.find('content')
                if content is not None:
                    title_class += ' toggle'
                    if list_item:
                        title_prefix += '<span class="toggle"></span>'
                    else:
                        title_prefix += '<span class="toggle hide"></span>'
                elif list_item:
                    title_prefix += '&bull;&nbsp;'

                if 'image' in title_element.attrib:
                    image = title_element.attrib['image']
                    if 'image-full' in title_element.attrib:
                        image_full = title_element.attrib['image-full']
                    else:
                        image_full = title_element.attrib['image']
                    title_postfix += '<a class="lightbox" title="'+ html.escape(title) + '" href="' + \
                                self.image_path + image_full + '">' \
                               '<img class="section" src="' + self.image_path + image + '"></a>'

                for tag in item.findall('tag'):
                    title_postfix += '<span class="tag ' + html.escape(tag.text) + '" title="' +\
                             html.escape(self.tags[tag.text]['desc']) + '">' + self.tags[tag.text]['title'] + '</span>'

                if has_real_uid:
                    title_postfix += '<a class="anchor" href="#' + html.escape(uid) + '">&para;</a>'

                self.outfile.write('  <div class="popupcontainer" data-id="' + uid + '">\n'
                                   '    <div id="' + uid + '" class="' + title_class + '">\n'
                                   '      ' + title_prefix + title + title_postfix + '\n'
                                   '    </div>\n')
                if content is not None:
                    content = content.find(self.lang)
                    if content is not None:
                        self.outfile.write('    <div class="popupcontent" id="pd' + uid + '" style="display: none;">\n'
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
        self.outfile.write('    <p class="contact">\n')
        if image:
            self.outfile.write('      <img class="cv-contact" title="' + key + '" src="' + self.image_path + image + '"/>\n')
        if href:
            value = '<a href="' + href + '">' + value + '</a>'
        self.outfile.write('      ' + key + ': <strong>' + value + '</strong>\n'
                           '    </p>\n')

    def content_string_from_element(self, element):
        s = eTree.tostring(element).decode(encoding='utf-8')
        s = s[s.index('>') + 1 : s.rfind('<')]
        return s


def exit_error(message):
    sys.stderr.write('Error: ' + message + '\n\n')
    exit(-1)


def main():
    parser = ArgumentParser()
    parser.add_argument('input', help='Input XML for compilation')
    parser.add_argument('output', nargs='?', default=None, help='Destination file path')
    parser.add_argument('--format', choices=['html', 'html-headless'], help='Output file format')
    parser.add_argument('--language', choices=['en', 'hu'], default='en', help='Language of exported data')
    parser.add_argument('--image-path', default='', help='Relative path of images in exported HTML')
    parser.add_argument('--css', nargs='*', help='Link this CSS in <head>')
    parser.add_argument('--js', nargs='*', help='Link this CSS in <head>')
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        exit_error('Input file does not exist!')

    headless = (args.format == 'html-headless')
    parser = CVParser(args.input, args.output, headless, args.css, args.js)
    parser.lang = args.language
    parser.image_path = args.image_path

    parser.write_file()


if __name__ == '__main__':
    main()
