# Copyright 2017-2019 TensorHub, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import imp
import json
import logging
import os
import sys

from guild import exit_code
from guild import python_util

FLAGS = {}
MOD_INFO = None

action_types = (
    argparse._StoreAction,
    argparse._StoreTrueAction,
    argparse._StoreFalseAction,
)

def _init_log():
    level = int(os.getenv("LOG_LEVEL", logging.WARN))
    format = os.getenv("LOG_FORMAT", "%(levelname)s: [%(name)s] %(message)s")
    logging.basicConfig(level=level, format=format)
    return logging.getLogger("import_flags_main")

log = _init_log()

def main():
    args = _init_args()
    if not _imports_argparse(args.mod_path):
        _not_supported_error(args.mod_path)
    _patch_argparse(args.output_path)
    # Importing module has the side-effect of writing flag data due to
    # patched argparse
    _exec_module(args.mod_path)

def _init_args():
    p = argparse.ArgumentParser()
    p.add_argument("mod_path")
    p.add_argument("output_path")
    return p.parse_args()

def _imports_argparse(mod_path):
    script = python_util.Script(mod_path)
    return "argparse" in script.imports

def _not_supported_error(mod_path):
    if log.getEffectiveLevel() <= logging.DEBUG:
        log.warning(
            "%s doesn't use argparse - cannot import flags",
            mod_path)
    raise SystemExit(exit_code.NOT_SUPPORTED)

def _patch_argparse(output_path):
    python_util.listen_method(
        argparse.ArgumentParser,
        "add_argument", _handle_add_argument)
    _handle_parse = lambda *args, **kw: _write_flags_and_exit(output_path)
    # parse_known_args is called by parse_args, so this handled both
    # cases.
    python_util.listen_method(
        argparse.ArgumentParser,
        "parse_known_args",
        _handle_parse)

def _handle_add_argument(add_argument, *args, **kw):
    log.debug("handling add_argument: %s %s", args, kw)
    action = add_argument(*args, **kw)
    _maybe_flag(action)
    raise python_util.Result(action)

def _maybe_flag(action):
    flag_name = _flag_name(action)
    if not flag_name:
        log.debug("skipping %s - not a flag option", action)
        return
    if not isinstance(action, action_types):
        log.debug("skipping %s - not an action type", action)
        return
    FLAGS[flag_name] = attrs = {}
    if action.help:
        attrs["description"] = action.help
    if action.default is not None:
        attrs["default"] = action.default
    if action.choices:
        attrs["choices"] = action.choices
    if action.required:
        attrs["required"] = True
    if isinstance(action, argparse._StoreTrueAction):
        attrs["arg-switch"] = True
    elif isinstance(action, argparse._StoreFalseAction):
        attrs["arg-switch"] = False
    log.debug("added flag %s", attrs)

def _flag_name(action):
    for opt in action.option_strings:
        if opt.startswith("--"):
            return opt[2:]
    return None

def _write_flags_and_exit(output_path):
    log.debug("writing flags to %s: %s", output_path, FLAGS)
    with open(output_path, "w") as f:
        json.dump(FLAGS, f)

def _exec_module(mod_path):
    assert mod_path.endswith(".py")
    f = open(mod_path, "r")
    details = (".py", "r", 1)
    sys.argv = [mod_path, "--help"]
    log.debug("loading module from '%s'", mod_path)
    try:
        imp.load_module("__main__", f, mod_path, details)
    except Exception as e:
        raise SystemExit(e)

if __name__ == "__main__":
    main()