#!/usr/bin/python3

from urllib import parse
import locale, gettext, os
from subprocess import check_output

from gi.repository import GObject, Gio, Gtk, Nemo

class DotnetPropertyPage(GObject.GObject, Nemo.PropertyPageProvider, Nemo.NameAndDescProvider):

    def get_property_pages(self, files):
        # files: list of NemoVFSFile
        if len(files) != 1:
            return []

        file = files[0]
        if file.get_uri_scheme() != 'file':
            return []

        if file.is_directory():
            return []

        if not(file.is_mime_type('application/x-msdownload')):
            return []

        filename = parse.unquote(file.get_uri()[7:])

        #GUI
        locale.setlocale(locale.LC_ALL, '')
        gettext.bindtextdomain("nemo-extensions")
        gettext.textdomain("nemo-extensions")
        _ = gettext.gettext

        self.property_label = Gtk.Label(_('.NET'))
        self.property_label.show()

        self.builder = Gtk.Builder()
        self.builder.set_translation_domain('nemo-extensions')
        self.builder.add_from_file("/usr/share/nemo-dotnetinfo-tab/nemo-dotnetinfo-tab.glade")

        #connect gtk objects to python variables
        for obj in self.builder.get_objects():
            if issubclass(type(obj), Gtk.Buildable):
                name = Gtk.Buildable.get_name(obj)
                setattr(self, name, obj)
        
        no_info = _("No Info")
        
        # set defaults to blank to prevent nonetype errors
        file.add_string_attribute('filedesc', '')
        file.add_string_attribute('filever', '')
        file.add_string_attribute('productname', '')
        file.add_string_attribute('productversion', '')
        file.add_string_attribute('language', '')
        file.add_string_attribute('copyright', '')
        file.add_string_attribute('company', '')
        file.add_string_attribute('comments', '')

        dictionary={}
        out = check_output(["exiftool", filename]).decode()
        
        for keyValue in out.split("\n"):
            keyValuePair = keyValue.split(":")
            if(len(keyValuePair) == 2):
                m = keyValuePair[0].strip()
                dictionary[m] = keyValuePair[1].strip()
           

        file.add_string_attribute('filedesc', dictionary.get('File Description',''))
        file.add_string_attribute('filever', dictionary.get('Assembly Version',''))
        file.add_string_attribute('productname', dictionary.get('Product Name',''))
        file.add_string_attribute('productversion', dictionary.get('Product Version',''))
        file.add_string_attribute('language', dictionary.get('Language Code',''))
        file.add_string_attribute('copyright', dictionary.get('Legal Copyright',''))
        file.add_string_attribute('company', dictionary.get('Company Name',''))
        file.add_string_attribute('comments', dictionary.get('Comments',''))
               
        self.builder.get_object("filedesc_text").set_label(file.get_string_attribute('filedesc'))
        self.builder.get_object("filever_text").set_label(file.get_string_attribute('filever'))
        self.builder.get_object("productname_text").set_label(file.get_string_attribute('productname'))
        self.builder.get_object("productversion_text").set_label(file.get_string_attribute('productversion'))
        self.builder.get_object("language_text").set_label(file.get_string_attribute('language'))
        self.builder.get_object("copyright_text").set_label(file.get_string_attribute('copyright'))
        self.builder.get_object("company_text").set_label(file.get_string_attribute('company'))
        self.builder.get_object("comments_text").set_label(file.get_string_attribute('comments'))

        return [
            Nemo.PropertyPage(name="NemoPython::NET",
                              label=self.property_label,
                              page=self.builder_root_widget)
        ]

    def get_name_and_desc(self):
        return [("Nemo NET Tab:::View .NET assembly information from the properties tab")]
