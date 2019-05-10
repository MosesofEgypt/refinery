import argparse

from refinery import tag_path_tokens
from refinery.repl_help_strs import command_help_strings,\
     command_arg_strings

__all__ = ("repl_parser", "repl_subparser",)


repl_parser = argparse.ArgumentParser(
    description="This is Refinery!"
    )
# make an argument to specify whether commands are to be queued or executed
repl_subparser = repl_parser.add_subparsers(dest="operation")

_ops = {}
# define the arg parsers for each operation
for name in sorted((
        "extract_tags", "extract_data", "extract_tag", "extract_cheape",
        "deprotect_map", "load_map", "unload_map", "save_map", "rename_map",
        "spoof_crc", "rename_tag_by_id", "rename_tag", "rename_dir",
        "set_vars", "get_vars", "map_info", "tag_id_tokens", "tag_id_macros",
        "switch_map", "switch_map_by_filepath", "switch_engine",
        "dir", "files", "dir_ct", "file_ct", "dir_names", "file_names",
        "quit", "maps", "engines", "verbose", "prompt", "cls")):
    _ops[name] = repl_subparser.add_parser(
        name.replace("_", "-"), help=command_help_strings[name])


#########################################################################
# add the positional arguments
#########################################################################
_ops["rename_tag"].add_argument(
    'tag-path', help=command_arg_strings["rename_tag"]['tag-path'])

_ops["rename_dir"].add_argument(
    'dir-path', help=command_arg_strings["rename_dir"]['dir-path'])

_ops["prompt"].add_argument(
    'level', default=None, choices=(0, 1, 2), type=int, nargs="?",
    help=command_arg_strings["prompt"]['level'])

_ops["verbose"].add_argument(
    'level', default=None, type=int, nargs="?",
    help=command_arg_strings["verbose"]['level'])
    
_ops["maps"].add_argument(
    'engine', default=None, nargs="?",
    help=command_arg_strings["maps"]['engine'])

_ops["rename_map"].add_argument(
    'new-name', help=command_arg_strings["rename_map"]['new-name'])

_ops["switch_map"].add_argument(
    'map-name', help=command_arg_strings["switch_map"]['map-name'])

_ops["switch_engine"].add_argument(
    'engine', help=command_arg_strings["switch_engine"]['engine'])

_ops["spoof_crc"].add_argument(
    'new-crc', type=int, help=command_arg_strings["spoof_crc"]['new-crc'])

_ops["tag_id_tokens"].add_argument(
    'token-prefix', default="", nargs="?",
    help=command_arg_strings["tag_id_tokens"]['token-prefix'])

_ops["tag_id_macros"].add_argument(
    'macro-prefix', default="", nargs="?",
    help=command_arg_strings["tag_id_macros"]['macro-prefix'])

for name in ("load_map", "extract_cheape", "switch_map_by_filepath"):
    _ops[name].add_argument(
        'filepath', help=command_arg_strings[name]['filepath'])

for name in ("deprotect_map", "save_map"):
    _ops[name].add_argument(
        'filepath', default=None, nargs="?",
        help=command_arg_strings[name]['filepath'])

for name in ("dir", "files", "dir_ct", "file_ct",
             "dir_names", "file_names"):
    _ops[name].add_argument(
        'dir', default=None, nargs="?",
        help=command_arg_strings[name]['dir'])

for name in ("rename_tag_by_id", "extract_tag"):
    _ops[name].add_argument(
        'tag-id', help=command_arg_strings[name]['tag-id'])

for name in ("rename_tag_by_id", "rename_tag", "rename_dir"):
    _ops[name].add_argument(
        'new-path', help=command_arg_strings[name]['new-path'])


# most args accept map-name and engine as their last optional positional args
for name in (
        "extract_tags", "extract_data", "extract_tag", "extract_cheape",
        "unload_map", "save_map", "deprotect_map", "rename_map",
        "spoof_crc", "rename_tag_by_id", "rename_tag", "rename_dir",
        "dir", "files", "map_info", "dir_ct", "file_ct",
        "dir_names", "file_names"):
    _ops[name].add_argument(
        'map-name', default=None, nargs="?",
        help=command_arg_strings[name]['map-name'])
    _ops[name].add_argument(
        'engine', default=None, nargs="?",
        help=command_arg_strings[name]['engine'])


#########################################################################
# add the optional arguments
#########################################################################
for name in ("deprotect_map", "load_map"):
    _ops[name].add_argument(
        '--do-printout', default=None, type=int,
        help=command_arg_strings[name]['do-printout'])

for name in ("deprotect_map", "save_map"):
    _ops[name].add_argument(
        '--fix-tag-index-offset', default=None, type=int,
        help=command_arg_strings[name]['fix-tag-index-offset'])
    _ops[name].add_argument(
        '--meta-data-expansion', default=None, type=int,
        help=command_arg_strings[name]['meta-data-expansion'])
    _ops[name].add_argument(
        '--raw-data-expansion', default=None, type=int,
        help=command_arg_strings[name]['raw-data-expansion'])
    _ops[name].add_argument(
        '--triangle-data-expansion', default=None, type=int,
        help=command_arg_strings[name]['triangle-data-expansion'])
    _ops[name].add_argument(
        '--vertex-data-expansion', default=None, type=int,
        help=command_arg_strings[name]['vertex-data-expansion'])

for name in ("dir_ct", "file_ct"):
    _ops[name].add_argument(
        '-t', '--total', default=False, action="store_const", const=True,
        dest="total", help=command_arg_strings[name]['total'])

for name in ("extract_tags", "extract_data", "deprotect_map"):
    _ops[name].add_argument(
        '--print-errors', default=None, type=int,
        help=command_arg_strings[name]['print-errors'])

for name in ("dir", "files"):
    _ops[name].add_argument(
        '--depth', default=None, type=int,
        help=command_arg_strings[name]['depth'])
    _ops[name].add_argument(
        '--guides', default=None, type=int,
        help=command_arg_strings[name]['guides'])
    _ops[name].add_argument(
        '--header', default=None, type=int,
        help=command_arg_strings[name]['header'])
    _ops[name].add_argument(
        '--indexed', default=None, type=int,
        help=command_arg_strings[name]['indexed'])
    _ops[name].add_argument(
        '--tag-ids', default=None, type=int,
        help=command_arg_strings[name]['tag-ids'])

for name in ("extract_tag", "extract_tags", "extract_data"):
    _ops[name].add_argument(
        '--force-lower-case-paths', default=None, type=int,
        help=command_arg_strings[name]['force-lower-case-paths'])
    _ops[name].add_argument(
        '--generate-comp-verts', default=None, type=int,
        help=command_arg_strings[name]['generate-comp-verts'])
    _ops[name].add_argument(
        '--generate-uncomp-verts', default=None, type=int,
        help=command_arg_strings[name]['generate-uncomp-verts'])
    _ops[name].add_argument(
        '--out-dir', default=None,
        help=command_arg_strings[name]['out-dir'])
    _ops[name].add_argument(
        '--overwrite', default=None, type=int,
        help=command_arg_strings[name]['overwrite'])
    _ops[name].add_argument(
        '--recursive', default=None, type=int,
        help=command_arg_strings[name]['recursive'])
    _ops[name].add_argument(
        '--rename-scnr-dups', default=None, type=int,
        help=command_arg_strings[name]['rename-scnr-dups'])
    _ops[name].add_argument(
        '--tagslist-path', default=None,
        help=command_arg_strings[name]['tagslist-path'])

for name in ("extract_tags", "extract_data"):
    _ops[name].add_argument(
        '--tokens', default=True, type=int,
        help=command_arg_strings[name]['tokens'])
    _ops[name].add_argument(
        '--macros', default=True, type=int,
        help=command_arg_strings[name]['macros'])

for name in (
        "autoload-resources", "do-printout", "print-errors",
        "force-lower-case-paths", "rename-scnr-dups", "overwrite",
        "recursive", "decode-adpcm", "generate-uncomp-verts",
        "generate-comp-verts", "use-tag-index-for-script-names",
        "use-scenario-names-for-script-names", "bitmap-extract-keep-alpha",
        "fix-tag-classes", "fix-tag-index-offset", "use-minimum-priorities",
        "valid-tag-paths-are-accurate", "scrape-tag-paths-from-scripts",
        "limit-tag-path-lengths", "print-heuristic-name-changes",
        "use-heuristics", "shallow-ui-widget-nesting", "rename-cached-tags"):
    _ops["set_vars"].add_argument(
        '--%s' % name, default=None, type=int,
        help=command_arg_strings["set_vars"][name])

for name in ("tags-dir", "data-dir", "tagslist-path", "bitmap-extract-format"):
    _ops["set_vars"].add_argument(
        '--%s' % name, default=None,
        help=command_arg_strings["set_vars"][name])
    
for name in (
        "autoload-resources", "do-printout", "print-errors",
        "force-lower-case-paths", "rename-scnr-dups", "overwrite",
        "recursive", "decode-adpcm", "generate-uncomp-verts",
        "generate-comp-verts", "use-tag-index-for-script-names",
        "use-scenario-names-for-script-names", "bitmap-extract-keep-alpha",
        "fix-tag-classes", "fix-tag-index-offset", "use-minimum-priorities",
        "valid-tag-paths-are-accurate", "scrape-tag-paths-from-scripts",
        "limit-tag-path-lengths", "print-heuristic-name-changes",
        "use-heuristics", "shallow-ui-widget-nesting", "rename-cached-tags",
        "tags-dir", "data-dir", "tagslist-path", "bitmap-extract-format"):
    _ops["get_vars"].add_argument(
        '--%s' % name, const=True, default=False, action="store_const",
        help=command_arg_strings["get_vars"][name])

for name in ("extract_tags", "extract_data"):
    _ops[name].add_argument(
        '--tag-ids', nargs="*", default=(tag_path_tokens.TOKEN_ALL, ),
        help=command_arg_strings[name]['tag-ids'])

_ops["extract_tag"].add_argument(
    '--filepath', default=None,
    help=command_arg_strings["extract_tag"]['filepath'])

_ops["extract_data"].add_argument(
    '--decode-adpcm', default=None, type=int,
    help=command_arg_strings["extract_data"]['decode-adpcm'])
_ops["extract_data"].add_argument(
    '--bitmap-extract-format', default=None, choices=["dds", "tga", "png"],
    help=command_arg_strings["extract_data"]['bitmap-extract-format'])
_ops["extract_data"].add_argument(
    '--bitmap-extract-keep-alpha', default=None, type=int,
    help=command_arg_strings["extract_data"]['bitmap-extract-keep-alpha'])

_ops["load_map"].add_argument(
    '--autoload-resources', default=None, type=int,
    help=command_arg_strings["load_map"]['autoload-resources'])
_ops["load_map"].add_argument(
    '--make-active', default=None, type=int,
    help=command_arg_strings["load_map"]['make-active'])
_ops["load_map"].add_argument(
    '--replace-if-same-name', default=None, type=int,
    help=command_arg_strings["load_map"]['replace-if-same-name'])

_ops["dir"].add_argument(
    '--dirs-first', default=None, type=int,
    help=command_arg_strings["dir"]['dirs-first'])
_ops["dir"].add_argument(
    '--extra-dir-spacing', default=None, type=int,
    help=command_arg_strings["dir"]['extra-dir-spacing'])
_ops["dir"].add_argument(
    '--files', default=None, type=int,
    help=command_arg_strings["dir"]['files'])
_ops["dir"].add_argument(
    '--indent', default=None, type=int,
    help=command_arg_strings["dir"]['indent'])

_ops["deprotect_map"].add_argument(
    '--fix-tag-classes', default=None, type=int,
    help=command_arg_strings["deprotect_map"]['fix-tag-classes'])
_ops["deprotect_map"].add_argument(
    '--limit-tag-path-lengths', default=None, type=int,
    help=command_arg_strings["deprotect_map"]['limit-tag-path-lengths'])
_ops["deprotect_map"].add_argument(
    '--print-heuristic-name-changes', default=None, type=int,
    help=command_arg_strings["deprotect_map"]['print-heuristic-name-changes'])
_ops["deprotect_map"].add_argument(
    '--rename-cached-tags', default=None, type=int,
    help=command_arg_strings["deprotect_map"]['rename-cached-tags'])
_ops["deprotect_map"].add_argument(
    '--scrape-tag-paths-from-scripts', default=None, type=int,
    help=command_arg_strings["deprotect_map"]['scrape-tag-paths-from-scripts'])
_ops["deprotect_map"].add_argument(
    '--shallow-ui-widget-nesting', default=None, type=int,
    help=command_arg_strings["deprotect_map"]['shallow-ui-widget-nesting'])
_ops["deprotect_map"].add_argument(
    '--use-heuristics', default=None, type=int,
    help=command_arg_strings["deprotect_map"]['use-heuristics'])
_ops["deprotect_map"].add_argument(
    '--use-minimum-priorities', default=None, type=int,
    help=command_arg_strings["deprotect_map"]['use-minimum-priorities'])
_ops["deprotect_map"].add_argument(
    '--use-scenario-names-for-script-names', default=None, type=int,
    help=command_arg_strings["deprotect_map"]['use-scenario-names-for-script-names'])
_ops["deprotect_map"].add_argument(
    '--use-tag-index-for-script-names', default=None, type=int,
    help=command_arg_strings["deprotect_map"]['use-tag-index-for-script-names'])
_ops["deprotect_map"].add_argument(
    '--valid-tag-paths-are-accurate', default=None, type=int,
    help=command_arg_strings["deprotect_map"]['valid-tag-paths-are-accurate'])