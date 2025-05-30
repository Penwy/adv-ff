# -*- coding: utf-8 -*-
# pylint: disable=C0301, R0902, R0903
"""
    Copyright (C) 2023 by Penwywern <gaspard.larrouturou@protonmail.com>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import sys
import os.path
import platform
import subprocess
import importlib.metadata as meta
import logging

import ctypes as ct
import ctypes.util
import ast
import json
import math, cmath, re, random, time

import obspython as obs

version = {
    "major" : 1,
    "minor" : 3,
    "patch" : 0,
    "variant" : ""
}

obs_required_version = {
    "major" : 30,
    "minor" : 2,
    "patch" : 0,
    "variant" : ""
}

if sys.version_info[0] < 3 or sys.version_info[1] < 9:
    print("Python version < 3.9, correct behaviour is not guaranteed")

print(f"adv-ff starting load of version {('.').join((str(n) for _, n in version.items()))} on python {sys.version}")



try:
    pyp_version = meta.version("pyparsing")
    if int(pyp_version[0]) >= 3:
        import pyparsing as pp
        print(f"Found pyparsing {pyp_version}")
        pyp_satisfied = True
    else:
        print(f"Pyparsing outdated : found {pyp_version}, requires 3.0")
        pyp_satisfied = False
except (meta.PackageNotFoundError, ModuleNotFoundError):
    print("Pyparsing not found")
    pyp_satisfied = False


if not pyp_satisfied:
    print("Pyparsing requirements not satisfied, attempting pip install")
    options = ['--target', sys.path[-1]]

    if platform.system() == "Windows":
        py_executable = [os.path.join(sys.exec_prefix, "python")]
    elif platform.system() == "Darwin":
        py_executable = [os.path.join(sys.exec_prefix, f"bin/python{sys.version_info[0]}.{sys.version_info[1]}")]
    else:
        py_executable = [f"python{sys.version_info[0]}.{sys.version_info[1]}"]    # No, sys.executable is not trustworthy in the slightest

    try:
        if platform.system() == "Linux" and platform.freedesktop_os_release()["ID"] == "org.kde.Platform":
            subprocess.check_call([*py_executable, '-m', 'ensurepip'])          # Flatpak is weirdge

        subprocess.check_call([*py_executable, '-m', 'pip', 'install',  *options, '--upgrade', 'pyparsing'])
        import pyparsing as pp
        print("Pyparsing successfully imported")

    except Exception as exc:
        print("pyparsing import failed :")
        logging.exception(exc)
        pp = None




###################################################################################################
###### OBS Version Check #######################################################################
###################################################################################################

obs_version = obs.obs_get_version()
minimum_required = ((obs_required_version['major']<<24) |
                    (obs_required_version['minor']<<16) |
                    (obs_required_version['patch']<<0))
obs_version_check = obs_version >= minimum_required

###################################################################################################
###### Script customisation #######################################################################
###################################################################################################

remove_zws = True


token_delimiter = "$"


source_fetch_proc = {"game_capture" :                 {"get_hooked":[("string",   "title"),
                                                                     ("string",   "class"),
                                                                     ("string",   "executable"),
                                                                     ("bool",     "hooked"),
                                                                     ],
                                                       },
                     "window_capture":                {"get_hooked":[("string",   "title"),
                                                                     ("string",   "class"),
                                                                     ("string",   "executable"),
                                                                     ("bool",     "hooked"),
                                                                     ],
                                                       },
                     "wasapi_process_output_capture": {"get_hooked":[("string",   "title"),
                                                                     ("string",   "class"),
                                                                     ("string",   "executable"),
                                                                     ("bool",     "hooked"),
                                                                     ],
                                                       },
                     "xcomposite_input":              {"get_hooked":[("string",   "name"),
                                                                     ("string",   "class"),
                                                                     ("bool",     "hooked"),
                                                                     ],
                                                       },
                     }

calldata_fetchers = {"string":  obs.calldata_string,
                     "bool":    obs.calldata_bool,
                     "int":     obs.calldata_int,
                     "float":   obs.calldata_float,
                     }


if_locals       = {"bool": bool, "float": float, "int": int, "str": str,
                   }

if_whitelist    = (ast.Constant,
                   ast.Name, ast.Load,
                   ast.Expression,
                   ast.UnaryOp, ast.UAdd, ast.USub, ast.Not, ast.Invert,
                   ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow, ast.LShift, ast.RShift, ast.BitOr, ast.BitXor, ast.BitAnd, ast.MatMult,
                   ast.BoolOp, ast.And, ast.Or,
                   ast.Compare, ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Is, ast.IsNot, ast.In, ast.NotIn,
                   ast.Call,
                   )

ex_locals       = {"math" : math, "cmath": cmath, "json": json, "re": re, "random": random, "time": time,
                   "abs": abs,
                   "all": all, "any": any,
                   "ascii": ascii,
                   "bin": bin, "hex" : hex, "oct": oct,
                   "bool": bool, "complex": complex, "float": float, "int": int, "str": str,
                   "chr": chr, "ord": ord,
                   "enumerate": enumerate, "reversed": reversed, "sorted": sorted, "zip": zip,
                   "len": len, "range": range,
                   "min": min, "max": max,
                   "pow": pow,
                   "round": round,
                   "sum": sum
                   }

ex_whitelist    = (ast.Constant, ast.JoinedStr, ast.FormattedValue,
                   ast.List, ast.Tuple, ast.Set, ast.Dict,
                   ast.Name, ast.Load, ast.Store, ast.Del, ast.Starred,
                   ast.Expression,
                   ast.UnaryOp, ast.UAdd, ast.USub, ast.Not, ast.Invert,
                   ast.BinOp, ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow, ast.LShift, ast.RShift, ast.BitOr, ast.BitXor, ast.BitAnd, ast.MatMult,
                   ast.BoolOp, ast.And, ast.Or,
                   ast.Compare, ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Is, ast.IsNot, ast.In, ast.NotIn,
                   ast.Call, ast.keyword,
                   ast.Attribute,
                   ast.IfExp,
                   ast.Subscript, ast.Slice,
                   ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp, ast.comprehension
                   )

def source_post_process(source, settings):
    """ Called on every source, allows to add to or modify its tokens (the "settings" dict).
    """

    # Adds the text of the selected file for a freetype2 source
    if obs.obs_source_get_unversioned_id(source) == "text_ft2_source":
        try:
            if settings["from_file"]:
                try:
                    with open(settings["text_file"], 'rt', encoding="utf8") as file:
                        settings["file_text"] = " ".join([line.strip() for line in file.readlines()])

                except FileNotFoundError:
                    print(f"Source \"{obs.obs_source_get_name(source)}\": File {settings['text_file']} not found.")
                    settings["file_text"] = ""

                except KeyError:
                    print(f"Source \"{obs.obs_source_get_name(source)}\": No file specified")
                    settings["file_text"] = ""
            else:
                settings["file_text"] = ""

        except KeyError:
            settings["file_text"] = ""


    # Adds the text of the selected file for a GDI+ source
    if obs.obs_source_get_unversioned_id(source) == "text_gdiplus":
        try:
            if settings["read_from_file"]:
                try:
                    with open(settings["file"], 'rt', encoding="utf8") as file:
                        settings["file_text"] = " ".join([line.strip() for line in file.readlines()])

                except FileNotFoundError:
                    print(f"Source \"{obs.obs_source_get_name(source)}\": File {settings['file']} not found.")
                    settings["file_text"] = ""

                except KeyError:
                    print(f"Source \"{obs.obs_source_get_name(source)}\": No file specified")
                    settings["file_text"] = ""
            else:
                settings["file_text"] = ""

        except KeyError:
            settings["file_text"] = ""



###################################################################################################
###### Function wrapping ##########################################################################
###################################################################################################


if platform.system() == "Linux" or platform.system() == "Darwin":
    libobs = ct.CDLL(ct.util.find_library("obs"))
    libfe = ct.CDLL(ct.util.find_library("obs-frontend-api"))
else:
    libobs = ct.CDLL("obs")
    libfe = ct.CDLL("obs-frontend-api")


def wrap(lib, funcname, restype, argtypes):
    """Wraps a C function from the given lib into python
    """
    func = getattr(lib, funcname)
    func.restype = restype
    func.argtypes = argtypes
    return func


#### Wrapping for hotkey manipulation
###################################################################################################

class ctHotkey(ct.Structure):
    pass

obs_hotkey_enum_func = ct.CFUNCTYPE(ct.c_bool, ct.c_void_p, ct.c_size_t, ct.POINTER(ctHotkey))

obs_hotkey_func = ct.CFUNCTYPE(ct.c_void_p, ct.c_size_t, ct.POINTER(ctHotkey), ct.c_bool)


ctHotkey._fields_ = (
                ("id", ct.c_size_t),
                ("name", ct.c_char_p),
                ("description", ct.c_char_p),
                ("func", obs_hotkey_func),
                ("data", ct.c_void_p),
                )


obs.obs_hotkey_get_name = wrap(libobs,
                               "obs_hotkey_get_name",
                               restype=ct.c_char_p,
                               argtypes=[ct.POINTER(ctHotkey)])

obs.obs_enum_hotkeys    = wrap(libobs,
                               "obs_enum_hotkeys",
                               restype=None,
                               argtypes=[obs_hotkey_enum_func, ct.c_void_p])


class HotkeyOverride():
    def __init__(self):
        self.active = False
        self.hotkey = None
        self.newfunc = None
        self.oldfunc = None

    def assign_override(self, func):
        self.newfunc = func
        if self.hotkey and self.active:
            self.hotkey.func = self.newfunc

    def assign_hk(self, hotkey):
        self.hotkey = hotkey
        self.oldfunc = type(hotkey.func)()
        ct.pointer(self.oldfunc)[0] = hotkey.func

    def activate(self, active):
        if self.hotkey and active and self.newfunc:
            self.hotkey.func = self.newfunc
        if self.hotkey and not active:
            self.hotkey.func = self.oldfunc
        self.active = active


#### Necessary to be able to bfree it to not leak memory
###################################################################################################

_os_generate_formatted_filename = wrap(libobs,
                                       "os_generate_formatted_filename",
                                       restype=ct.c_void_p,
                                       argtypes=[ct.c_char_p, ct.c_bool, ct.c_char_p])

_obs_frontend_get_last_recording = wrap(libfe,
                                       "obs_frontend_get_last_recording",
                                       restype=ct.c_void_p,
                                       argtypes=[])

_bfree                          = wrap(libobs,
                                       "bfree",
                                       restype=None,
                                       argtypes=[ct.c_void_p])


def os_generate_formatted_filename(extension, space, file_format):
    file_format = file_format[:valid_formatted_length(file_format)]
    formatted_p = _os_generate_formatted_filename(extension.encode("utf-8"), space, file_format.encode("utf-8"))
    value       = ct.c_char_p(formatted_p).value
    _bfree(formatted_p)
    if value:
        return value.decode("utf-8")
    return ""


def obs_frontend_get_last_recording():
    filepath_p = _obs_frontend_get_last_recording()
    value       = ct.c_char_p(filepath_p).value
    _bfree(filepath_p)
    if value:
        return value.decode("utf-8")
    return ""

def valid_formatted_length(file_format):    # This is an abomination I really hope the filename formatting crop will be fixed soonish
    available_length = 255 - 10             # We assume no extension will ever be more than 10 bytes, if there exists one that does, fuck that noise

    formatted_p = _os_generate_formatted_filename("".encode("utf-8"), False, file_format.encode("utf-8"))
    value       = ct.c_char_p(formatted_p).value
    _bfree(formatted_p)

    while len(value) > available_length:
        file_format = file_format[:-1]
        formatted_p = _os_generate_formatted_filename("".encode("utf-8"), False, file_format.encode("utf-8"))
        value       = ct.c_char_p(formatted_p).value
        _bfree(formatted_p)
    return len(file_format)




###################################################################################################



###################################################################################################
###### Parser Grammar #############################################################################
###################################################################################################

if pp:
    def if_action(tokens):
        return(("if", *tokens.as_list()))

    def exec_action(tokens):
        return(("exec", *tokens.as_list()))

    def literal_action(tokens):
        return(("value", *tokens.as_list()))

    def string_action(tokens):
        return(("string", *tokens.as_list()))

    def counter_action(tokens):
        return(("counter", *tokens.as_list()))


    grammar     = pp.Forward()

    kw          = {"ex_start"  : pp.Literal(f"{token_delimiter}exec{token_delimiter}").suppress(),
                   "if_start"  : pp.Literal(f"{token_delimiter}if{token_delimiter}").suppress(),
                   "if_then"   : pp.Literal(f"{token_delimiter}then{token_delimiter}").suppress(),
                   "if_else"   : pp.Literal(f"{token_delimiter}else{token_delimiter}").suppress(),
                   "end"       : pp.Literal(f"{token_delimiter}end{token_delimiter}").suppress(),
                   }
    keyword     = pp.Or([_[1] for _ in kw.items()])

    literal     =  (pp.Literal("v").suppress()                              +
                    ~keyword + pp.Literal(f"{token_delimiter}").suppress()  +
                    pp.Group(grammar)                                       +
                    pp.Literal(f"{token_delimiter}").suppress()
                    )

    counter     =  (pp.Literal("c").suppress()                              +
                    ~keyword + pp.Literal(f"{token_delimiter}").suppress()  +
                    pp.Group(grammar)                                       +
                    pp.Literal(f"{token_delimiter}").suppress()
                    )

    str_block   = pp.Combine(pp.OneOrMore(~keyword +~literal +~counter +~pp.Literal(f"{token_delimiter}") + pp.Regex(r'[\s\S]')))

    ex_block    = kw["ex_start"]   + pp.Group(grammar)          + kw["end"]

    if_block    = (kw["if_start"]  + pp.Group(grammar)          +
                   kw["if_then"]   + pp.Group(grammar)          +
                  (kw["if_else"]   + pp.Group(grammar))[..., 1] + kw["end"]
                   )

    if_block.set_parse_action(if_action)
    ex_block.set_parse_action(exec_action)
    str_block.set_parse_action(string_action)
    literal.set_parse_action(literal_action)
    counter.set_parse_action(counter_action)

    grammar.leave_whitespace()
    if_block.leave_whitespace()
    ex_block.leave_whitespace()
    literal.leave_whitespace()
    counter.leave_whitespace()
    str_block.leave_whitespace()

    grammar <<= pp.ZeroOrMore( ex_block
                             | if_block
                             | literal
                             | counter
                             | str_block
                             )



###################################################################################################
###### Interpreter ################################################################################
###################################################################################################

class Counters():
    """Holds the values of the counters and the currently selected one
    """
    data = {}
    selected = None

counters = Counters()

def exec_eval(expr):
    """ Checks for validity and legality of exec token statement then evaluates it
    """
    class Visitor(ast.NodeVisitor):
        def visit(self, node):
            if not isinstance(node, ex_whitelist):
                raise ValueError(type(node))
            return super().visit(node)

    try:
        node = ast.parse(expr.strip(), mode='eval')
    except SyntaxError as ex:
        return ex, 400

    try:
        Visitor().visit(node)
    except ValueError as ex:
        return ex, 405

    try:
        return eval(compile(node, "<string>", "eval"), {'__builtins__': None}, ex_locals), 200
    except Exception as ex:
        return ex, 422


def if_eval(expr):
    """ Checks for validity and legality of if token condition then evaluates it
    """
    class Visitor(ast.NodeVisitor):
        def visit(self, node):
            if not isinstance(node, if_whitelist):
                raise ValueError(node)
            return super().visit(node)

    try:
        node = ast.parse(expr.strip(), mode='eval')
    except SyntaxError as ex:
        return ex, 400

    try:
        Visitor().visit(node)
    except ValueError as ex:
        return ex, 405

    try:
        return eval(compile(node, "<string>", "eval"), {'__builtins__': None}, if_locals), 200
    except Exception as ex:
        return ex, 422


def counter_eval(counter_id, increase=True):
    try:
        value = counters.data[counter_id]
        if increase:
            counters.data[counter_id] += 1

    except KeyError:
        value = 0
        counters.data[counter_id] = int(increase)

    return str(value)


def parser_fetch_data(sources):
    """ Given a list of source names, builds a data object for use in interpretation
    """
    data = {}
    for ind, source_name in enumerate(sources):
        source = obs.obs_get_source_by_name(source_name)
        if source:
            source_data     = obs.obs_source_get_settings(source)
            settings        = json.loads(obs.obs_data_get_json_with_defaults(source_data))
            obs.obs_data_release(source_data)

            settings["width"]       = obs.obs_source_get_width(source)
            settings["height"]      = obs.obs_source_get_height(source)
            settings["muted"]       = obs.obs_source_muted(source)
            settings["active"]      = obs.obs_source_active(source)
            settings["showing"]     = obs.obs_source_showing(source)

            sid = obs.obs_source_get_unversioned_id(source)
            if sid in source_fetch_proc:
                for proc, items in source_fetch_proc[sid].items():
                    cd = obs.calldata_create()
                    obs.proc_handler_call(obs.obs_source_get_proc_handler(source),
                                          proc, cd)
                    for func, key in items:
                        settings[key] = calldata_fetchers[func](cd, key)
                    obs.calldata_destroy(cd)

            source_post_process(source, settings)

            data[ind]           = settings
            data[source_name]   = settings

        obs.obs_source_release(source)

    current_scene       = obs.obs_frontend_get_current_scene()
    current_preview     = obs.obs_frontend_get_current_preview_scene()
    data["user"]        = os.path.expanduser('~')
    data["username"]    = os.path.basename(os.path.expanduser('~'))
    data["scene"]       = obs.obs_source_get_name(current_scene)
    if current_preview:
        data["program"] = obs.obs_source_get_name(current_scene)
        data["preview"] = obs.obs_source_get_name(current_preview)
    else:
        data["program"] = ""
        data["preview"] = ""
    obs.obs_source_release(current_scene)
    obs.obs_source_release(current_preview)

    data["day"] = time.strftime("%a")
    data["Day"] = time.strftime("%A")
    data["month"] = time.strftime("%b")
    data["Month"] = time.strftime("%B")

    try:
        data["executable"] = data[0]["executable"]
    except KeyError:
        data["executable"] = ""
    try:
        data["title"] = data[0]["title"]
    except KeyError:
        data["title"] = ""

    return data


class ErrCounter():
    """ Used to track errors happening while interpreting
    """
    counter = 0

def interpreter(tree, data, err_counter=ErrCounter(), increase_counters=True, sanitize=False):
    """ Builds an interpreted string from a parsed tree and data
        Works recursively on the tree
    """
    return_string = ""
    for node in tree:
        match node[0]:

            case "string":
                return_string += node[1]

            case "exec":
                interpreted = interpreter(node[1], data, err_counter, increase_counters)
                val, code = exec_eval(interpreted)
                match code:
                    case 200:
                        return_string += str(val)
                    case 400:
                        err_counter.counter +=1
                        print(f"Malformed exec : {interpreted} : {val}")
                    case 405:
                        err_counter.counter +=1
                        print(f"Forbidden exec token : {interpreted} : {val}")
                    case 422:
                        err_counter.counter +=1
                        print(f"Failed exec : {interpreted} : {val}")

            case "if":
                interpreted = interpreter(node[1], data, err_counter, increase_counters)
                condition, code = if_eval(interpreted)
                match code:
                    case 200:
                        if condition:
                            return_string += interpreter(node[2], data, err_counter)
                        else:
                            return_string += interpreter(node[3], data, err_counter)
                    case 400:
                        err_counter.counter +=1
                        print(f"Malformed if : {interpreted} : {condition}")
                    case 405:
                        err_counter.counter +=1
                        print(f"Forbidden if token : {interpreted} : {condition}")
                    case 422:
                        err_counter.counter +=1
                        print(f"Failed if : {interpreted} : {condition}")

            case "counter":
                interpreted = interpreter(node[1], data, err_counter, increase_counters)
                return_string += counter_eval(interpreted, increase_counters)

            case "value":
                try:
                    interpreted = interpreter(node[1], data, err_counter, increase_counters)
                    inds = interpreted.split("][")
                    startinds = inds[0].split("[")
                    startinds[0] = "0" if startinds[0] == "" else startinds[0]
                    inds = startinds + inds[1:]
                    inds[-1] = inds[-1][:-1] if inds[-1][-1] == "]" else inds[-1]

                    val = data
                    for ind in inds:
                        try:
                            val = val[int(ind)]
                        except ValueError:
                            val = val[ind]

                except KeyError as ex:
                    err_counter.counter +=1
                    print(f"Missing key : {ex} in {interpreted}")
                    val = ""
                return_string += str(val)

    if sanitize:
        return_string = re.sub(r"[\*\"<>:\|\?]", "_", return_string)

    if remove_zws:
        return_string = re.sub(r"[\u180e\u200B\u200C\u200D\u2060\ufeff]", "", return_string)

    return return_string


###################################################################################################
###### Parsers ####################################################################################
###################################################################################################


class Parser():
    """ Used to hold persistent data for the parsers
    """
    oldformat   = None
    sources     = []
    tree        = []

class Splitfile():
    """ Holds data about filesplitting settings
    """
    old_mode         = None
    size            = float("inf")
    time            = float("inf")
    hotkey          = HotkeyOverride()
    current_file    = None
    split_pending   = False


############################# Recording output parser
rec_parser = Parser()
split_file = Splitfile()

def split_file_done_callback(*args):
    """ Signals that the last requested file split has been done
    """
    split_file.current_file = obs_frontend_get_last_recording()
    split_file.split_pending = False


@obs_hotkey_func
def split_file_hotkey_callback(*args):
    """ Overrides the default callback for the split file hotkey
    """
    if not split_file.split_pending:
        rec = obs.obs_frontend_get_recording_output()
        data = obs.obs_output_get_settings(rec)
        obs.obs_data_set_string(data, 'format', rec_parser_interpret())
        obs.obs_data_release(data)
        obs.obs_output_release(rec)

        split_file.split_pending = True
        split_file.hotkey.oldfunc(*args)


def split_file_auto_callback(*args):
    """ operates the Time and Size auto filesplits
    """
    if not split_file.split_pending:

        try:
            if (split_file.old_mode == "Size"
                and os.path.getsize(split_file.current_file) < split_file.size):
                return
        except FileNotFoundError:
            return

        print("in auto callback")
        rec = obs.obs_frontend_get_recording_output()
        data = obs.obs_output_get_settings(rec)
        obs.obs_data_set_string(data, 'format', rec_parser_interpret())
        obs.obs_data_release(data)
        obs.obs_output_release(rec)

        split_file.split_pending = True
        obs.obs_frontend_recording_split_file()


def rec_parser_interpret():
    """ Fetches data and returns interpreted string
    """
    data = parser_fetch_data(rec_parser.sources)
    file_format = interpreter(rec_parser.tree, data, increase_counters=True, sanitize=(platform.system()=="Windows"))
    return file_format[:valid_formatted_length(file_format)]


def rec_parser_tree_from_string(string):
    """ Creates parsed tree from string
    """
    try:
        rec_parser.tree = grammar.parse_string(string, True)
    except pp.exceptions.ParseException:
        rec_parser.tree = None


def rec_parser_apply_cb(event):
    """ Applies the formatting when recording is starting and reverts it once started
    """
    match event:
        case obs.OBS_FRONTEND_EVENT_RECORDING_STARTING:

            config = obs.obs_frontend_get_profile_config()
            rec_parser.oldformat = obs.config_get_string(config, "Output",
                                                         "FilenameFormatting") or ""
            if flags.record_enabled:
                obs.config_set_string(config, "Output",
                                      "FilenameFormatting", rec_parser_interpret())

                if (obs.config_get_string(config, "Output", "Mode") == "Advanced"
                    and obs.config_get_bool(config, "AdvOut", "RecSplitFile")):
                    # If one of the non-manual filesplitting types was selected, change to manual
                    # and divert the check for filesplitting to our own function
                    split_file.hotkey.activate(True)
                    split_file.old_mode = obs.config_get_string(config, "AdvOut", "RecSplitFileType")
                    obs.config_set_string(config, "AdvOut", "RecSplitFileType", "Manual")

                    rec = obs.obs_frontend_get_recording_output()
                    obs.signal_handler_connect(obs.obs_output_get_signal_handler(rec),
                                               "file_changed", split_file_done_callback)
                    obs.obs_output_release(rec)

                    match split_file.old_mode:
                        case "Time":
                            obs.timer_add(split_file_auto_callback,
                                          obs.config_get_int(config, "AdvOut", "RecSplitFileTime") * 60000)
                        case "Size":
                            obs.timer_add(split_file_auto_callback, 1000)
                            split_file.size = obs.config_get_int(config, "AdvOut", "RecSplitFileSize") * 1000000


        case obs.OBS_FRONTEND_EVENT_RECORDING_STARTED:
            if flags.record_enabled:
                if split_file.old_mode == "Size":
                    split_file.current_file = obs_frontend_get_last_recording()

            config = obs.obs_frontend_get_profile_config()
            obs.config_set_string(config, "Output",
                                  "FilenameFormatting", rec_parser.oldformat)


        case obs.OBS_FRONTEND_EVENT_RECORDING_STOPPED:
            if split_file.old_mode:
                obs.timer_remove(split_file_auto_callback)
                split_file.hotkey.activate(False)

                config = obs.obs_frontend_get_profile_config()
                obs.config_set_string(config, "AdvOut", "RecSplitFileType", split_file.old_mode)
                split_file.old_mode = None





############################# Replay buffer parser
buf_parser = Parser()


def buf_parser_interpret():
    """ Fetches data and returns interpreted string
    """
    data = parser_fetch_data(buf_parser.sources)
    file_format = interpreter(buf_parser.tree, data, increase_counters=True, sanitize=(platform.system()=="Windows"))
    return file_format[:valid_formatted_length(file_format)]


def buf_parser_tree_from_string(string):
    """ Creates parsed tree from string
    """
    try:
        buf_parser.tree = grammar.parse_string(string, True)
    except pp.exceptions.ParseException:
        buf_parser.tree = None


def buf_parser_connect_cb(event):
    """ Connects/disconnects the apply callback when replay buffer is started/stopped
    """
    match event:
        case obs.OBS_FRONTEND_EVENT_REPLAY_BUFFER_STARTED:
            rb = obs.obs_frontend_get_replay_buffer_output()
            obs.signal_handler_connect(obs.obs_output_get_signal_handler(rb),
                                       "saving", buf_parser_apply_cb)
            obs.obs_output_release(rb)

        case obs.OBS_FRONTEND_EVENT_REPLAY_BUFFER_STOPPING:
            rb = obs.obs_frontend_get_replay_buffer_output()
            obs.signal_handler_disconnect(obs.obs_output_get_signal_handler(rb),
                                          "saving", buf_parser_apply_cb)
            obs.obs_output_release(rb)


def buf_parser_apply_cb(calldata):
    """ Applies the formatting when the buffer is set to be saved
    """
    if flags.buffer_enabled:
        rb = obs.obs_frontend_get_replay_buffer_output()

        data = obs.obs_output_get_settings(rb)
        obs.obs_data_set_string(data, 'format', buf_parser_interpret())
        obs.obs_data_release(data)

        obs.obs_output_release(rb)



###################################################################################################
###### UI building ################################################################################
###################################################################################################

class SettingsHolder():
    """ Holds the data settings of the script.
        I really don't like doing that, but it's the only way I found to
        update the settings through a button press.
        (here the counter value display with the refresh counters button.)
    """
    settings = None

settings_holder = SettingsHolder()


def get_space():
    """ Whether filenames should be generated with or without spaces
        (used only in displaying the result of the formatting in the UI)
    """
    config = obs.obs_frontend_get_profile_config()
    mode = obs.config_get_string(config, "Output",
                                 "Mode")  or ""

    if mode == "Simple":
        space = obs.config_get_bool(config, "SimpleOutput",
                                    "FileNameWithoutSpace")
    else:
        rectype = obs.config_get_string(config, "AdvOut",
                                        "RecType") or ""
        if rectype == "Standard":
            space = obs.config_get_bool(config, "AdvOut",
                                        "RecFileNameWithoutSpace")
        else:
            space = obs.config_get_bool(config, "AdvOut",
                                        "FFFileNameWithoutSpace")
    return not space
    # Because consistency is overrated I guess


def rec_tester(props, *args):
    """ Attempts to builds a filename from the specified recording formatting and displays it in the UI
    """
    obs.obs_property_set_long_description(  obs.obs_properties_get(props, "rec_warning"), " ")
    obs.obs_property_set_description(       obs.obs_properties_get(props, "rec_warning"), " ")
    obs.obs_property_set_long_description(  obs.obs_properties_get(props, "rec_result"),  " ")
    obs.obs_property_set_description(       obs.obs_properties_get(props, "rec_result"),  " ")

    if rec_parser.tree is None:
        obs.obs_property_set_long_description(  obs.obs_properties_get(props, "rec_warning"), "parsing error, malformed formatting string")
        obs.obs_property_set_description(       obs.obs_properties_get(props, "rec_warning"), "Error: ")
        obs.obs_property_text_set_info_type(    obs.obs_properties_get(props, "rec_warning"), obs.OBS_TEXT_INFO_ERROR)

    else:
        data = parser_fetch_data(rec_parser.sources)
        error_counter = ErrCounter()
        result = os_generate_formatted_filename("", get_space(), interpreter(rec_parser.tree, data, error_counter, increase_counters=False, sanitize=(platform.system()=="Windows")))

        obs.obs_property_set_long_description(  obs.obs_properties_get(props, "rec_result"), result)
        obs.obs_property_set_description(       obs.obs_properties_get(props, "rec_result"), "")
        obs.obs_property_text_set_info_type(    obs.obs_properties_get(props, "rec_result"), obs.OBS_TEXT_INFO_NORMAL)

        if error_counter.counter:
            obs.obs_property_set_long_description(  obs.obs_properties_get(props, "rec_warning"), "errors while interpreting, check log for more details")
            obs.obs_property_set_description(       obs.obs_properties_get(props, "rec_warning"), "Warning: ")
            obs.obs_property_text_set_info_type(    obs.obs_properties_get(props, "rec_warning"), obs.OBS_TEXT_INFO_WARNING)

    fill_counters_list(props)
    obs.obs_data_set_int(settings_holder.settings, "counter_val", counters.data[counters.selected])
    return True


def buf_tester(props, *args):
    """ Attempts to builds a filename from the specified replay buffer formatting and displays it in the UI
    """
    obs.obs_property_set_long_description(  obs.obs_properties_get(props, "buf_warning"), " ")
    obs.obs_property_set_description(       obs.obs_properties_get(props, "buf_warning"), " ")
    obs.obs_property_set_long_description(  obs.obs_properties_get(props, "buf_result"),  " ")
    obs.obs_property_set_description(       obs.obs_properties_get(props, "buf_result"),  " ")

    if buf_parser.tree is None:
        obs.obs_property_set_long_description(  obs.obs_properties_get(props, "buf_warning"), "parsing error, malformed formatting string")
        obs.obs_property_set_description(       obs.obs_properties_get(props, "buf_warning"), "Error: ")
        obs.obs_property_text_set_info_type(    obs.obs_properties_get(props, "buf_warning"), obs.OBS_TEXT_INFO_ERROR)

    else:
        data = parser_fetch_data(buf_parser.sources)
        error_counter = ErrCounter()
        result = os_generate_formatted_filename("", get_space(), interpreter(buf_parser.tree, data, error_counter, increase_counters=False, sanitize=(platform.system()=="Windows")))

        obs.obs_property_set_long_description(  obs.obs_properties_get(props, "buf_result"), result)
        obs.obs_property_set_description(       obs.obs_properties_get(props, "buf_result"), "")
        obs.obs_property_text_set_info_type(    obs.obs_properties_get(props, "buf_result"), obs.OBS_TEXT_INFO_NORMAL)

        if error_counter.counter:
            obs.obs_property_set_long_description(  obs.obs_properties_get(props, "buf_warning"), "errors while interpreting, check log for more details")
            obs.obs_property_set_description(       obs.obs_properties_get(props, "buf_warning"), "Warning: ")
            obs.obs_property_text_set_info_type(    obs.obs_properties_get(props, "buf_warning"), obs.OBS_TEXT_INFO_WARNING)

    fill_counters_list(props)
    obs.obs_data_set_int(settings_holder.settings, "counter_val", counters.data[counters.selected])
    return True


def fill_counters_list(props):
    counter_list = obs.obs_properties_get(props, "counter_list")
    obs.obs_property_list_clear(counter_list)
    for counter_name in counters.data:
        obs.obs_property_list_add_string(counter_list, "Default Counter" if (counter_name=="counter") else f"Counter : {counter_name}", f"{counter_name}")


def refresh_counters(props, prop):
    data = parser_fetch_data(rec_parser.sources)
    interpreter(rec_parser.tree, data, increase_counters=False)
    data = parser_fetch_data(buf_parser.sources)
    interpreter(buf_parser.tree, data, increase_counters=False)

    fill_counters_list(props)
    obs.obs_data_set_int(settings_holder.settings, "counter_val", counters.data[counters.selected])
    return True


def remove_counter(props, prop):
    if counters.selected and counters.selected != "counter":
        counters.data.pop(counters.selected)
    else:
        print("Cannot remove default counter.")

    fill_counters_list(props)
    return True


def counter_selected_modified(props, prop, settings):
    selected_counter = obs.obs_data_get_string(settings, "counter_list")
    if selected_counter:
        counters.selected = selected_counter
        obs.obs_data_set_int(settings, "counter_val", counters.data[counters.selected])
        return True


def counter_value_modified(props, prop, settings):
    if json.loads(obs.obs_data_get_json_with_defaults(settings)):
        counters.data[counters.selected] = obs.obs_data_get_int(settings, "counter_val")


class PropertiesFlags():
    """ Holds UI flags
    """
    record_enabled      = False
    buffer_enabled      = False
    buffer_available    = False

flags = PropertiesFlags()
# Disables replay buffer formatting if PR#8955 isn't present
flags.buffer_available = hasattr(obs, "OBS_FRONTEND_EVENT_REPLAY_BUFFER_SAVING")


def process_props_flags(props, *args):
    """ Hides or show recording/replay buffer UI depending on whether their formatting is enabled
    """
    if not flags.buffer_available:
        obs.obs_property_set_visible(obs.obs_properties_get(props, "buf_enable"),   False)
        # Hides the option to enable replay buffer formatting if PR#8955 isn't present

    if flags.record_enabled:
        obs.obs_property_set_visible(obs.obs_properties_get(props, "rec_format"),   True)
        obs.obs_property_set_visible(obs.obs_properties_get(props, "rec_source"),   True)
        obs.obs_property_set_visible(obs.obs_properties_get(props, "rec_tester"),   True)
        obs.obs_property_set_visible(obs.obs_properties_get(props, "rec_result"),   True)
        obs.obs_property_set_visible(obs.obs_properties_get(props, "rec_warning"),  True)
    else:
        obs.obs_property_set_visible(obs.obs_properties_get(props, "rec_format"),   False)
        obs.obs_property_set_visible(obs.obs_properties_get(props, "rec_source"),   False)
        obs.obs_property_set_visible(obs.obs_properties_get(props, "rec_tester"),   False)
        obs.obs_property_set_visible(obs.obs_properties_get(props, "rec_result"),   False)
        obs.obs_property_set_visible(obs.obs_properties_get(props, "rec_warning"),  False)

    if flags.buffer_enabled:
        obs.obs_property_set_visible(obs.obs_properties_get(props, "buf_format"),   True)
        obs.obs_property_set_visible(obs.obs_properties_get(props, "buf_source"),   True)
        obs.obs_property_set_visible(obs.obs_properties_get(props, "buf_tester"),   True)
        obs.obs_property_set_visible(obs.obs_properties_get(props, "buf_result"),   True)
        obs.obs_property_set_visible(obs.obs_properties_get(props, "buf_warning"),  True)
    else:
        obs.obs_property_set_visible(obs.obs_properties_get(props, "buf_format"),   False)
        obs.obs_property_set_visible(obs.obs_properties_get(props, "buf_source"),   False)
        obs.obs_property_set_visible(obs.obs_properties_get(props, "buf_tester"),   False)
        obs.obs_property_set_visible(obs.obs_properties_get(props, "buf_result"),   False)
        obs.obs_property_set_visible(obs.obs_properties_get(props, "buf_warning"),  False)

    return True


def script_defaults(settings):
    if not (pp and obs_version_check):
        return
    config = obs.obs_frontend_get_profile_config()
    rec_parser.oldformat = obs.config_get_string(config, "Output",
                                                 "FilenameFormatting") or ""

    buf_parser.oldformat = ((obs.config_get_string(config, "SimpleOutput",
                                                   "RecRBPrefix") or "") +
                            rec_parser.oldformat +
                            (obs.config_get_string(config, "SimpleOutput",
                                                   "RecRBSuffix") or "")
                            )

    obs.obs_data_set_default_string(settings, "rec_format", rec_parser.oldformat)
    obs.obs_data_set_default_string(settings, "buf_format", buf_parser.oldformat)

    obs.obs_data_set_default_bool(settings, "rec_enable", False)
    obs.obs_data_set_default_bool(settings, "buf_enable", False)

    # Somehow, data_get_json segfaults on script reload if the defaults are initialised with data_array_create, don't ask me why.
    # Sept 8 2024 : found out why, thanks Vix, and fuck data arrays, it's too complex to explain in comments if you need to know, ask me in the obs discord.

    obs.obs_data_set_default_array(settings, "rec_source", None)
    obs.obs_data_set_default_array(settings, "buf_source", None)


    default_counter = obs.obs_data_get_default_obj(settings, "counters")
    if not default_counter:
        default_counter = obs.obs_data_create()
        obs.obs_data_set_default_obj(settings, "counters", default_counter)
    obs.obs_data_set_default_int(default_counter, "counter", 0)
    obs.obs_data_release(default_counter)
    obs.obs_data_set_default_int(settings, "counter_val", 0)

    obs.obs_data_set_default_string(settings, "counter_list", "counter")


def script_properties():
    props = obs.obs_properties_create()
    # Padding so that it doesn't jump around (needs refining)
    blank = obs.obs_properties_add_text(props, "tblank",    "<p style='color:#00000000'>Formatting</p>",   obs.OBS_TEXT_INFO)
    obs.obs_property_set_long_description(blank, " ")

    if not (pp and obs_version_check):
        return props

    obs.obs_properties_add_button(              props, "counter_refresh",   "Refresh counters list",    refresh_counters)
    c_list = obs.obs_properties_add_list(       props, "counter_list",      "Counters",                 obs.OBS_COMBO_TYPE_LIST,    obs.OBS_COMBO_FORMAT_STRING)
    c_val = obs.obs_properties_add_int(         props, "counter_val",       "Counter Value",            0, 99999, 1)
    obs.obs_properties_add_button(              props, "counter_remove",    "Remove counter",           remove_counter)
    obs.obs_property_set_modified_callback(c_list,  counter_selected_modified)
    obs.obs_property_set_modified_callback(c_val,   counter_value_modified)
    fill_counters_list(props)

    obs.obs_properties_add_bool(            props, "rec_enable",    "Enable recording formatting")
    obs.obs_properties_add_editable_list(   props, "rec_source",    "Sources",          obs.OBS_EDITABLE_LIST_TYPE_STRINGS, None, None)
    obs.obs_properties_add_text(            props, "rec_format",    "Formatting",       obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_button(          props, "rec_tester",    "Check formatting", rec_tester)
    obs.obs_properties_add_text(            props, "rec_result",    " ",                obs.OBS_TEXT_INFO)
    obs.obs_properties_add_text(            props, "rec_warning",   " ",                obs.OBS_TEXT_INFO)

    obs.obs_properties_add_bool(            props, "buf_enable",    "Enable replay buffer formatting")
    obs.obs_properties_add_editable_list(   props, "buf_source",    "Sources",          obs.OBS_EDITABLE_LIST_TYPE_STRINGS, None, None)
    obs.obs_properties_add_text(            props, "buf_format",    "Formatting",       obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_button(          props, "buf_tester",    "Check formatting", buf_tester)
    obs.obs_properties_add_text(            props, "buf_result",    " ",                obs.OBS_TEXT_INFO)
    obs.obs_properties_add_text(            props, "buf_warning",   " ",                obs.OBS_TEXT_INFO)

    obs.obs_property_set_modified_callback(obs.obs_properties_get(props, "rec_enable"), process_props_flags)
    obs.obs_property_set_modified_callback(obs.obs_properties_get(props, "buf_enable"), process_props_flags)
    process_props_flags(props)
    return props


def script_description():
    """ #RTFM
    """
    desc = ("<h4>Advanced Filename Formatter</h4>"
            "Allows dynamically generating filenames from sources state and more.<br>"
            "Please read <a href='https://github.com/Penwy/adv-ff/blob/main/docs/doc.md'>the docs</a>."
            )
    if not pp:
        desc += ("<br>"
                 "<br>"
                 "<font color=#ff0000>This script requires the <a href='https://pypi.org/project/pyparsing/'>PyParsing</a> module to properly function, but it wasn't found and failed to install.</font><br>"
                 "<font color=#ff0000>Check <a href='https://github.com/Penwy/adv-ff/tree/main/pyparsing-troubleshoot'>this page</a> for possible solutions.</font><br>"
                 )
    if not obs_version_check:
        desc += ("<br>"
                 "<br>"
                 f"<font color=#ff0000>This version of adv-ff requires OBS ≥ {obs_required_version['major']}.{obs_required_version['minor']}.{obs_required_version['patch']}  </font><br>"
                 "<font color=#ff0000>Please update OBS for the script to work</font><br>"
                 )
    return desc


###################################################################################################
###### OBS script functions #######################################################################
###################################################################################################


def script_load(settings):
    if not (pp and obs_version_check):
        return
    settings_holder.settings = settings
    data = json.loads(obs.obs_data_get_json_with_defaults(settings))

    flags.record_enabled =  data["rec_enable"]
    flags.buffer_enabled =  data["buf_enable"] if flags.buffer_available else False

    obs.obs_frontend_add_event_callback(rec_parser_apply_cb)
    if flags.buffer_available:
        obs.obs_frontend_add_event_callback(buf_parser_connect_cb)

    counters.data.update(data["counters"])
    counters.selected = data["counter_list"]

    @obs_hotkey_enum_func
    def get_split_hotkey(dat, hotkey_id, hotkey):
        if obs.obs_hotkey_get_name(hotkey).decode("utf8") == "OBSBasic.SplitFile":
            split_file.hotkey.assign_hk(hotkey.contents)
            return False
        return True

    obs.obs_enum_hotkeys(get_split_hotkey, None)
    split_file.hotkey.assign_override(split_file_hotkey_callback)


def script_unload():
    if split_file.old_mode:
        obs.timer_remove(split_file_auto_callback)
        split_file.hotkey.activate(False)

        config = obs.obs_frontend_get_profile_config()
        obs.config_set_string(config, "AdvOut", "RecSplitFileType", split_file.old_mode)
        split_file.old_mode = None



def script_update(settings):
    if not (pp and obs_version_check):
        return
    data = json.loads(obs.obs_data_get_json_with_defaults(settings))

    flags.record_enabled =  data["rec_enable"]
    flags.buffer_enabled =  data["buf_enable"] if flags.buffer_available else False

    rec_parser_tree_from_string(data["rec_format"])
    rec_parser.sources = []
    for item in (data["rec_source"]):
        rec_parser.sources.append(item["value"])

    buf_parser_tree_from_string(data["buf_format"])
    buf_parser.sources = []
    for item in (data["buf_source"]):
        buf_parser.sources.append(item["value"])



def script_save(settings):
    if not (pp and obs_version_check):
        return
    counters_data = obs.obs_data_create_from_json(json.dumps(counters.data))
    obs.obs_data_set_obj(settings, "counters", counters_data)
    obs.obs_data_release(counters_data)
