#!/usr/bin/python
"""
Reo is a dictionary application made with Python and Gtk+3.

It's a simple script basically. It uses existing tools and as such, easily
works across most Linux distributions without any changes.
"""
# The MIT License (MIT)

# Copyright (c) 2016-2019 Mufeed Ali
# This file is part of Reo

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Author: Mufeed Ali

# Now, beginning with the Imports.

import sys
import logging
import argparse  # for CommandLine-Interface (CLI).
import os
from os.path import expanduser  # for detecting home folder
from shutil import which  # for checks.
import subprocess  # for running dict and others in background
import random  # for Random Words
import lzma
import reo_base
import threading
from html import escape

reo_version = "master"

# Readying ArgParser
parser = argparse.ArgumentParser()  # declare parser as the ArgumentParser used
mgroup = parser.add_mutually_exclusive_group()
mgroup.add_argument("-c", "--check", action="store_true",
                    help="Basic dependancy checks.")
mgroup.add_argument("-d", "--adversion", action="store_true",
                    help="Advanced Version Info")
mgroup.add_argument("-gd", "--dark", action="store_true",
                    help="Use GNOME dark theme")
mgroup.add_argument("-gl", "--light", action="store_true",
                    help="Use GNOME light theme")
parser.add_argument("-l", "--livesearch", action="store_true",
                    help="Enable live search")
parser.add_argument("-v", "--verbose", action="store_true",
                    help="Make it scream louder")
parsed = parser.parse_args()
# logging is the most important. You have to let users know everything.
if(parsed.verbose):
    level = logging.DEBUG
else:
    level = logging.WARNING
logging.basicConfig(level=level, format="%(asctime)s - " +
                    "[%(levelname)s] [%(threadName)s] (%(module)s:" +
                    "%(lineno)d) %(message)s")
try:
    import gi  # this is the GObject stuff needed for GTK+
    gi.require_version('Gtk', '3.0')  # inform the PC that we need GTK+ 3.
    import gi.repository.Gtk as Gtk  # this is the GNOME depends
    import gi.repository.Gdk as Gdk
    if parsed.check:
        print("PyGOject bindings working")
except ImportError as ierr:
    logging.fatal("Importing GObject failed!")
    if not parsed.check:
        print("Confirm all dependencies by running " +
              "Reo with '--check' parameter.\n" +
              ierr)
        sys.exit(1)
    elif parsed.check:
        print("Install GObject bindings.\n" +
              "For Ubuntu, Debian, etc:\n" +
              "'sudo apt install python3-gobject'\n" +
              "From extra repo for Arch Linux:\n" +
              "'pacaur -S python-gobject' or 'sudo pacman -S python-gobject'" +
              "\nThanks for trying this out!")
builder = Gtk.Builder()


def darker():
    """Switch to Dark mode."""
    global dark
    settings = Gtk.Settings.get_default()
    settings.set_property("gtk-application-prefer-dark-theme", True)
    dark = True


def lighter():
    """Switch to Light mode."""
    global dark
    settings = Gtk.Settings.get_default()
    settings.set_property("gtk-application-prefer-dark-theme", False)
    dark = False


def windowcall():
    """Call the window."""
    global sb, viewer
    window = builder.get_object('window')  # main window
    sb = builder.get_object('searchEntry')  # Search box
    viewer = builder.get_object('defView')  # Data Space
    header = builder.get_object('header')  # Headerbar
    header.set_show_close_button(True)
    if((os.environ.get('GTK_CSD') == '0') and
       (os.environ.get('XDG_SESSION_TYPE') != 'wayland')):
        headlabel = builder.get_object('headlabel')
        titles = builder.get_object('titles')
        titles.set_margin_end(0)
        titles.set_margin_start(0)
        headlabel.destroy()
    window.set_role('Reo')
    window.set_title('Reo')
    sb.grab_focus()
    window.show_all()


if not parsed.adversion and not parsed.check:
    if Gtk.Settings.get_default().get_property("gtk-application-prefer" +
                                               "-dark-theme"):
        dark = True
    else:
        dark = False
    if parsed.dark:
        darker()
    elif parsed.light:
        lighter()
    PATH = os.path.dirname(os.path.realpath(__file__))
    GLADEFILE = PATH + "/reo.ui"
    # GLADEFILE = "/usr/share/reo/reo.ui"
    builder.add_from_file(GLADEFILE)
    windowcall()


wnver = '3.1'
wncheckonce = False


def wncheck():
    """Check if WordNet is properly installed."""
    global wnver, wncheckonce, wn
    if not wncheckonce:
        try:
            check = subprocess.Popen(["dict", "-d", "wn", "test"],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT)
            checkt = check.stdout.read().decode()
        except Exception as ex:
            print("Error with dict. Error")
            print(ex)
        if not checkt.find('1 definition found\n\nFrom WordNet (r)' +
                           ' 3.1 (2011) [wn]:\n') == -1:
            wnver = '3.1'
            logging.info("Using WordNet 3.1")
        elif not checkt.find('1 definition found\n\nFrom WordNet (r)' +
                             ' 3.0 (2006) [wn]:\n') == -1:
            wnver = '3.0'
            logging.info("Using WordNet 3.0")
        wncheckonce = True
    wn = str(lzma.open('wn' + wnver + '.lzma', 'r').read()).split('\\n')


def adv():
    """Check all requirements thoroughly."""
    print('Reo - ' + reo_version)
    print('Copyright 2016-2019 Mufeed Ali')
    print()
    wncheck()
    if wnver == '3.1':
        print("WordNet Version 3.1 (2011) (Installed)")
    elif wnver == '3.0':
        print("WordNet Version 3.0 (2006) (Installed)")
    try:
        check2 = subprocess.Popen(["dict", "-V"],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT)
        check2t = check2.stdout.read().decode()
        print("Dict Version Info:\n" + check2t.strip())
    except Exception as ex:
        print("Looks like missing components. (dict)\n" + str(ex))
    print()
    try:
        check3 = subprocess.Popen(["espeak-ng", "--version"],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT)
        check3t = check3.stdout.read().decode()
        print("eSpeak-ng Version Info:\n" + check3t.strip())
    except Exception as ex:
        print("You're missing a few components. (espeak-ng)\n" + str(ex))
    sys.exit()


def CheckBin(bintocheck):
    """Check presence of required binaries."""
    try:
        which(bintocheck)
        print(bintocheck + " seems to be installed. OK.")
        bincheck = True
    except Exception as ex:
        logging.fatal(bintocheck + " is not installed! Dependancy missing!" +
                      str(ex))
        bincheck = False
    return bincheck


def PrintChecks(espeakng, dictc, dictd, wndict):
    """Print result of all checks."""
    if (espeakng and dictc and dictd and wndict):
        print("Everything Looks Perfect!\n" +
              "You should be able to run it without any issues!")
    elif (espeakng and dictc and dictd and not wndict):
        print("WordNet's data file is missing. Re-install 'dict-wn'.\n" +
              "For Ubuntu, Debian, etc:\n" +
              "'sudo apt install dict-wn'\n" +
              "From AUR for Arch Linux:\n" +
              "'pacaur -S dict-wn'\n" +
              "Everything else (NOT everything) looks fine...\n" +
              "... BUT you can't run it.")
    elif (espeakng and not dictc and not dictd and not wndict):
        print("dict and dictd (client and server) are missing.. install it." +
              "\nFor Ubuntu, Debian, etc:\n" +
              "'sudo apt install dictd dict-wn'\n" +
              "From community repo for Arch Linux (but WordNet from AUR):\n" +
              "'pacaur -S dictd dict-wn'\n" +
              "That should point you in the right direction to getting \n" +
              "it to work.")
    elif (not espeakng and not dictc and not dictd and not wndict):
        print("ALL bits and pieces are Missing...\n" +
              "For Ubuntu, Debian, etc:\n" +
              "'sudo apt install espeak-ng dictd dict-wn'\n" +
              "From community repo for Arch Linux (but WordNet from AUR):\n" +
              "'pacaur -S espeak-ng dictd dict-wn'\n" +
              "Go on, get it working now!")
    elif (not espeakng and dictc and dictd and wndict):
        print("Everything except eSpeak-ng is working...\n" +
              "For Ubuntu, Debian, etc:\n" +
              "'sudo apt install espeak-ng'\n" +
              "From community repo for Arch Linux:\n" +
              "'pacaur -S espeak-ng' or 'sudo pacman -S espeak-ng'\n" +
              "It should be alright then.")
    elif (not espeakng and dictc and dictd and wndict):
        print("eSpeak-ng is missing and WordNet might not work as intended.\n"
              + "Install 'espeak-ng' and re-install the 'dict-wn' package.\n" +
              "For Ubuntu, Debian, etc:\n" +
              "'sudo apt install espeak-ng dict-wn'\n" +
              "From AUR for Arch Linux:\n" +
              "'pacaur -S espeak-ng dict-wn'\n" +
              "Everything else (NOT everything) looks fine.\n" +
              "Go on, try and run it!")
    elif (not espeakng and dictc and dictd and not wndict):
        print("eSpeak-ng is missing and WordNet's data file is missing." +
              "Re-install 'dict-wn'.\n" +
              "For Ubuntu, Debian, etc:\n" +
              "'sudo apt install espeak-ng dict-wn'\n" +
              "From AUR for Arch Linux:\n" +
              "'pacaur -S espeak-ng dict-wn'\n" +
              "Everything else (NOT everything) looks" +
              " fine BUT you can't run it.")


def syscheck():
    """Check requirements but not thoroughly."""
    espeakng = CheckBin('espeak-ng')
    dictc = CheckBin('dict')
    dictd = CheckBin('dictd')
    if os.path.exists('/usr/share/dictd/wn.dict.dz'):
        print('WordNet databse seems to be installed. OK.')
        wndict = True
    else:
        logging.warning("WordNet database is not found! Probably won't work.")
        wndict = False
    PrintChecks(espeakng, dictc, dictd, wndict)
    sys.exit()


if parsed.adversion:
    adv()
if parsed.check:
    syscheck()
homefold = expanduser('~')  # Find the location of the home folder of the user
reofold = homefold + "/.config/reo"
# ^ This is where stuff like settings, Custom Definitions, etc will go.
cdefold = reofold + "/cdef"
# ^ The Folder within reofold where Custom Definitions are to be kept.
if not os.path.exists(reofold):  # check for Reo folder
    os.makedirs(reofold)  # create Reo folder
if not os.path.exists(cdefold):  # check for Custom Definitions folder.
    os.makedirs(cdefold)  # create Custom Definitions folder.
if (os.path.exists(reofold + "/dark") and
   not os.path.exists(reofold + "/light")):  # check for Dark mode file
    darker()
elif (not os.path.exists(reofold + "/dark") and
      os.path.exists(reofold + "/light")):
    lighter()
if os.path.exists(reofold + "/maxhide"):
    maxhide = True
if os.path.exists(reofold + "/wnver31"):
    logging.info("Using WordNet 3.1 as per local config")
    wnver = '3.1'
    wncheckonce = True
if os.path.exists(reofold + "/livesearch") or parsed.livesearch:
    livesearch = True
else:
    livesearch = False
term = None  # Last searched item.
threading.Thread(target=wncheck).start()


class GUI:
    """Define all UI actions and sub-actions."""

    def on_window_destroy(self, window):
        """Clear all windows."""
        Gtk.main_quit()

    def state_changed(self, window, state):
        """Detect changes to the window state and adapt."""
        header = builder.get_object('header')
        if maxhide:
            if ("MAXIMIZED" in str(state.new_window_state) and
                    "FOCUSED" in str(state.new_window_state)):
                header.set_show_close_button(False)
            else:
                header.set_show_close_button(True)

    def icon_press(self, imagemenuitem4):
        """Open About Window."""
        about = builder.get_object('aboutReo')
        about.set_version(reo_version)
        response = about.run()
        if (response == Gtk.ResponseType.DELETE_EVENT or
                response == Gtk.ResponseType.CANCEL):
            about.hide()

    def sst(self, imagemenuitem1):
        """Search selected text."""
        text = Gtk.Clipboard.get(Gdk.SELECTION_PRIMARY).wait_for_text()
        text = text.replace('-\n         ', '-').replace('\n', ' ')
        text = text.replace('         ', '')
        sb.set_text(text)
        if not text == '' and not text.isspace():
            self.searchClick()
            sb.grab_focus()

    def paste_search(self, pastensearch):
        """Search text in clipboard."""
        text = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD).wait_for_text()
        sb.set_text(text)
        if not text == '' and not text.isspace():
            self.searchClick()
            sb.grab_focus()

    def newced(self, title, primary, secondary):
        """Show error dialog."""
        cept = builder.get_object('cept')
        cest = builder.get_object('cest')
        ced = builder.get_object('ced')
        ced.set_title(title)
        cept.set_label(primary)
        cest.set_label(secondary)
        response = ced.run()
        if (response == Gtk.ResponseType.DELETE_EVENT or
                response == Gtk.ResponseType.OK):
            ced.hide()

    def fortune(self):
        """Present fortune easter egg."""
        try:
            fortune = subprocess.Popen(["fortune", "-a"],
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)
            fortune.wait()
            ft = fortune.stdout.read().decode()
            ft = escape(ft, False)
            return "<tt>" + ft + "</tt>"
        except Exception as ex:
            ft = "Easter Egg Fail!!! Install 'fortune' or 'fortunemod'."
            print(ft + "\n" + str(ex))
            return "<tt>" + ft + "</tt>"

    def cowfortune(self):
        """Present cowsay version of fortune easter egg."""
        try:
            cowsay = subprocess.Popen(["cowsay", self.fortune()],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT)
            cowsay.wait()
            if cowsay:
                cst = cowsay.stdout.read().decode()
            return "<tt>" + cst + "</tt>"
        except Exception as ex:
            ft = ("Easter Egg Fail!!! Install 'fortune' or 'fortunemod'" +
                  " and also 'cowsay'.")
            print(ft + "\n" + str(ex))
            return "<tt>" + ft + "</tt>"

    def searchClick(self, searchButton=None):
        """Pass data to search function and set TextView data."""
        global term
        text = sb.get_text().strip()
        if not text == term:
            viewer.get_buffer().set_text("")
            lastiter = viewer.get_buffer().get_end_iter()
            out = self.search(text)
            term = text
            viewer.get_buffer().insert_markup(lastiter, out, -1)

    def search(self, sb):
        """Clean input text, give errors and pass data to reactor."""
        if (not sb.strip('<>"?`![]()/\\:;,') == '' and
                not sb.isspace() and not sb == ''):
            text = sb.strip().strip('<>"?`![]()/\\:;,')
            return self.reactor(text)
        elif (sb.strip('<>"?`![]()/\\:;,') == '' and
              not sb.isspace() and
              not sb == ''):
            logging.error("Invalid Characters.")
            self.newced('Error: Invalid Input!', 'Invalid Characters!',
                        "Reo thinks that your input was actually \nju" +
                        "st a bunch of useless characters. \nSo, 'Inva" +
                        "lid Characters' error!")

    def reactor(self, text):
        """Check easter eggs and set variables."""
        global searched
        if dark:
            sencol = "cyan"  # Color of sentences in Dark mode
            wordcol = "lightgreen"  # Color of: Similar Words,
#                                     Synonyms and Antonyms.
        else:
            sencol = "blue"  # Color of sentences in regular
            wordcol = "green"  # Color of: Similar Words, Synonyms, Antonyms.
        skip = ['00-database-allchars', '00-database-info', '00-database-long',
                '00-database-short', '00-database-url']
        if text in skip:
            return "<tt> Running Reo with WordNet " + wnver + "</tt>"
        elif text == 'fortune -a':
            return self.fortune()
        elif text == 'cowfortune':
            return self.cowfortune()
        elif text == 'crash now' or text == 'close now':
            Gtk.main_quit()
        elif text == 'reo':
            reodef = str("<tt>Pronunciation: <b>/ɹˈiːəʊ/</b>\n  <b>Reo</b>" +
                         " ~ <i>Japanese Word</i>\n  <b>1:</b> Name " +
                         "of this application, chosen kind of at random." +
                         "\n  <b>2:</b> Japanese word meaning 'Wise" +
                         " Center'\n <b>Similar Words:</b>\n <i><" +
                         "span foreground=\"" + wordcol + "\">  ro, " +
                         "re, roe, redo, reno, oreo, ceo, leo, neo, " +
                         "rho, rio, reb, red, ref, rem, rep, res," +
                         " ret, rev, rex</span></i></tt>")
            return reodef
        if text and not text.isspace():
            searched = True
            return self.generator(text, wordcol, sencol)

    def cdef(self, text, wordcol, sencol):
        """Present custom definition when available."""
        with open(cdefold + '/' + text, 'r') as cdfile:
            cdefread = cdfile.read()
            relist = {"<i>($WORDCOL)</i>": wordcol, "<i>($SENCOL)</i>": sencol,
                      "($WORDCOL)": wordcol, "($SENCOL)": sencol,
                      "$WORDCOL": wordcol, "$SENCOL": sencol}
            for i, j in relist.items():
                cdefread = cdefread.replace(i, j)
            if "\n[warninghide]" in cdefread:
                cdefread = cdefread.replace("\n[warninghide]", "")
                return cdefread
            else:
                return(cdefread + '\n<span foreground="#e6292f">' +
                       'NOTE: This is a Custom definition. No one' +
                       ' is to be held responsible for errors in' +
                       ' this.</span>')

    def dictdef(self, text, wordcol, sencol):
        """Obtain all outputs from dict and espeak and return final result."""
        strat = "lev"
        try:
            prc = subprocess.Popen(["dict", "-d", "wn", text],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
            pro = subprocess.Popen(["espeak-ng", "-ven-uk-rp",
                                    "--ipa", "-q", text],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
            clos = subprocess.Popen(["dict", "-m", "-d", "wn",
                                     "-s", strat, text],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        except Exception as ex:
            logging.error("Didnt Work! ERROR INFO: " + str(ex))
        prc.wait()
        proc = prc.stdout.read().decode()
        if not proc == '':
            soc = reo_base.defProcessor(proc, text, sencol, wordcol, "pango")
            crip = 0
        else:
            soc = "Coundn't find definition for '" + text + "'."
            crip = 1
        pro.wait()
        pron = pro.stdout.read().decode()
        pron = " /" + pron.strip().replace('\n ', ' ') + "/"
        clos.wait()
        clp = clos.stdout.read().decode()
        clp = reo_base.clsfmt(clp, text)
        fail = 0
        if text.lower() == 'recursion':
            clp = 'recursion'
        if clp == '':
            fail = 1
        if pro and not crip == 1:
            pron = "<b>Pronunciation</b>: <b>" + pron + '</b>'
        elif pro and crip == 1:
            pron = "<b>Probable Pronunciation</b>: <b>" + pron + '</b>'
        if fail == 0:
            if crip == 1:
                clp = ('<b>Did you mean</b>:\n<i><span foreground="' +
                       wordcol + '">  ' + clp + '</span></i>')
            else:
                clp = ('<b>Similar Words</b>:\n' +
                       '<i><span foreground="' + wordcol + '">  ' +
                       clp + '</span></i>')
        return pron.strip() + '\n' + soc + '\n' + clp.strip()

    def generator(self, text, wordcol, sencol):
        """Check if custom definition exists."""
        if os.path.exists(cdefold + '/' + text.lower()):
            return self.cdef(text, wordcol, sencol)
        else:
            return self.dictdef(text, wordcol, sencol)

    def cedok(self, cedok):
        """Generate OK response from error dialog."""
        ced = builder.get_object('ced')
        ced.response(Gtk.ResponseType.OK)

    def randword(self, mnurand):
        """Choose a random word and pass it to the search box."""
        rw = random.choice(wn)
        sb.set_text(rw.strip())
        self.searchClick()
        sb.grab_focus()

    def clear(self, clearButton):
        """Clear text in the Search box and the Data space."""
        sb.set_text("")
        viewer.get_buffer().set_text("")

    def audio(self, audioButton):
        """Say the search entry out loud with espeak speech synthesis."""
        speed = '120'  # To change eSpeak-ng audio speed.
        text = sb.get_text().strip()
        if searched and not text == '':
            reo_base.readTerm(speed, sb.get_text().strip())
        elif text == '' or text.isspace():
            self.newced("Umm..?", "Umm..?", "Reo can't find any text" +
                        " there! You sure \nyou typed something?")
        elif not searched:
            self.newced("Sorry!!", "Sorry!!",
                        "I'm sorry but you have to do a search" +
                        " first \nbefore trying to  listen to it." +
                        " I mean, Reo \nis <b>NOT</b> a Text-To" +
                        "-Speech Software!")

    def changed(self, searchEntry):
        """Detect changes to Search box and clean or do live searching."""
        global searched
        searched = False
        sb.set_text(sb.get_text().replace('\n', ' '))
        sb.set_text(sb.get_text().replace('         ', ''))
        if livesearch:
            self.searchClick()

    def quitb(self, imagemenuitem10):
        """Quit using menu."""
        Gtk.main_quit()

    def savedef(self, imagemenuitem2):
        """Save definition using FileChooser dialog."""
        defdiag = Gtk.FileChooserDialog("Save Definition as...",
                                        builder.get_object('window'),
                                        Gtk.FileChooserAction.SAVE,
                                        ("Save", Gtk.ResponseType.OK,
                                         "Cancel", Gtk.ResponseType.CANCEL))
        response = defdiag.run()
        if (response == Gtk.ResponseType.DELETE_EVENT or
                response == Gtk.ResponseType.CANCEL):
            defdiag.hide()
        elif response == Gtk.ResponseType.OK:
            sf = open(defdiag.get_filename(), 'w')
            startiter = viewer.get_buffer().get_start_iter()
            lastiter = viewer.get_buffer().get_end_iter()
            sf.write(viewer.get_buffer().get_text(startiter, lastiter,
                                                  'false'))
            sf.close()
            defdiag.hide()


builder.connect_signals(GUI())
Gtk.main()
