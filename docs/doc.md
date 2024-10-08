# Advanced Filename Formatter Documentation

## Basic usage

This script allows overriding the basic OBS formatting with extended tokens.\
Formatting can be enabled separately for recording or replay buffer.\
Once enabled, it'll spawn the following UI :

![Basic adv-ff formatting UI](https://github.com/Penwy/adv-ff/blob/main/docs/basic_UI.png)

- Sources added to the "Sources" list will have their data available to insert in the formatting.
- The "Formatting" field specifies a custom formatting to override the default one. It accepts both the basic OBS formatting tokens as well as custom tokens added by the script.
- The "Check formatting" button builds a filename from the specified formatting and displays it, to check whether the specified formatting is valid and its output.

Basic formatting tokens are as follow:

`v$day$` : Abbreviated weekday name[^1]\
`v$Day$` : Full weekday name[^1]\
`v$month$` : Abbreviated month name[^1]\
`v$Month$` : Full month name[^1]

`v$user$` : Path to the Home directory of the current user (without trailing slash)\
`v$username$` : Username of the current user

`v$scene$` : Currently selected scene ("Preview" scene when in studio mode)\
`v$preview$` : Current preview scene (empty string if not in studio mode)\
`v$program$` : Current program scene (empty string if not in studio mode)

`v$executable$` : Executable currently hooked by the first source in the list (empty string if the source is not a game/window/application audio capture, or not hooked)\
`v$title$` : Title of the window currently hooked by the first source in the list (empty string if the source is not a game/window/application audio capture, or not hooked)\

[^1]: Currently, those are using python's default locale.

## Advanced Usage

*N.B.: When using complex formatting, I seriously advise unchecking "Overwrite if file exists" in the OBS advanced settings so as to not delete important files if the formatting does something you hadn't planned.*

### Accessing source settings

The settings of a source added to the source list are accessible by specifying the key to access in brackets : `v$[<key>]$`.\
For example, `v$[text]$` inserts the text of a text source.\
In the case of nested data settings, just specify the keys one after the other.\
For example, `v$[playlist][0][value]$` inserts the name of the first item of a VLC source's playlist.

Additionally, the following keys are added for use alongside the source settings :
- `width`, `height`: base width and height of the source (*not the sceneitem's width and height*)
- `muted`: whether the source is muted in the mixer
- `active`: whether the source is active (shown on an active output's mix)
- `showing`: whether the source is showing (shown on an active output's mix, or a preview)
- For game capture, window capture and application audio capture[^2] sources:
    - `hooked`: whether the source is currently hooked to a window
    - `title`: title of the window currently hooked (empty string if the source is not hooked)
    - `class`: class of the window currently hooked (empty string if the source is not hooked)
    - `executable`: executable of the window currently hooked (empty string if the source is not hooked)
- For Xcomposite window capture sources:
    - `hooked`: whether the source is currently hooked to a window
    - `name`: name of the window currently hooked (empty string if the source is not hooked)
    - `class`: class of the window currently hooked (empty string if the source is not hooked)
- For Text sources (both Freetype2 and GDI+):
    - `file_text`: if the source is reading from file, the contents of the file in question, otherwise an empty string

[^2]: Builtin, not win-capture-audio plugin.

### Multiple sources

When multiple sources are added to the list, they can be accessed by specifying either the source's name or its position in the list (*starting at 0*) before the brackets.\
For example, `v$2[height]$` inserts the height of the *third* source in the list.

When no source is specified, it defaults to the first one in the list.\
`v$executable$` and `v$title$` are just proxies for `v$0[executable]$` and `v$0[title]$`.

### Counters

Counter tokens are numbers that get incremented by 1 every time they are used when saving a file.\
The default counter can be inserted with `c$counter$`.
Additional counters can be created by inserting a token following the template `c$<counter_name>$`.

The counters list at the top of the script's properties allows to manually adjust the value of select counters, or delete unused ones.
A newly created counter will not appear in the list until it's been refreshed with the relevant button.\
Due to the limitations of scripting, the counter value displayed in the UI cannot get updated each time the counter is used, so don't forget to refresh the list before manually changing its value or you'll overwrite the increase.

*N.B.:\
- A counter inside the `$then$` block of an `$if$` statement will not get incremented if the statement's condition evaluates to false (and inversely for the `$else$` block).\
- If you want a looping counter, use the exec token with a modulo operator. For example, `$exec$ c$counter$ %10 $end$` will loop the default counter between 0 and 9.*

### If token

The if token inserts one of two possibilities depending on the truth value of a simple condition. The syntax is as follows :\
`$if$ <condition> $then$ <inserted if true> $else$ <inserted if false> $end$`\
The condition is evaluated with python syntax.

For example, `$if$ "v$executable$" == "javaw.exe" $then$ Minecraft $else$ Not Minecraft $end$` will insert "Minecraft" if the executable hooked by the first source in the list is javaw.exe, and "Not Minecraft" if it isn't. Note the quotes around `v$executable$` to have it compared as a string.\
The else token can be omitted, in which case nothing will be inserted if the condition is false.

### Exec token

*N.B.: This uses `eval()`.\
If you don't understand why that's a bad idea, you probably shouldn't be using it.\
The eval is somewhat sanitized with an ast node whitelist and controlled locals, but eval can't be 100% sanitized. If you want to crash the python interpreter with it, you probably can.*

The exec token evaluates a statement as python code and inserts its return value. The syntax is as follows :\
`$exec$ <statement to evaluate> $end$`

For example, `$exec$ random.paretovariate(1) $end$` inserts a random number sampled from a Pareto distribution of parameter 1.\
I don't know why you'd want to do that but hey, you can.

### Customisation

The following can be customised or added to, in the "Script customisation" section, at the start of the script file.

- `remove_zws`: by default and because of Activision being weirdos with the CoD window title, any zero width whitespace (including mongolian vowel separator, zero width space, zero width non-joiner, zero width joiner, word joiner and zero-width non-breaking space) are removed from the filename generation. If for some reason you need any of those in your filename, set this to true.

- `token_delimiter`: the character(s) used to delimit tokens. By nature, the character(s) used as delimiter can't be put directly in the filename, so if you want to put dollar signs in your filenames, change it to something else.

- `source_fetch_proc`: when fetching data from sources, if the source's type id matches one listed in there, the procedures listed under it get called on it, and the specified values are retrieved from the calldata and added to the data available to the parser.\
    To add to it, syntax is as follows :
    ```
    <unversionned_id> : {<proc_1> : [(<type1>, <key1>), (<type2>, <key2>), ...],
                         <proc_2> : [(<type1>, <key1>), (<type2>, <key2>), ...],
                         ...
                         }
    ```
    The "type" defines which function is used to retrieve the data from the calldata, as defined below it in `calldata_fetchers`.

- `if_locals`, `if_whitelist`, `ex_locals` and `ex_whitelist` define the locals and nodes available to the if and exec tokens eval.

- `source_post_process` is applied to each source (after the fetch procs). It allows to add tokens that can't be gotten by a proc.

### Additional notes

- All tokens are fully nestable, in any order. Have fun.

- The replay buffer and "hooked" source info functionality rely on signals and procedures that are not (yet) part of current OBS (29.1.2). You can find a custom build that will enable them [here](https://github.com/Penwy/obs-studio/actions/runs/5301025505).

- OBS's filenames have a limit of 255 characters. In order to leave room for the extension (without which the muxer doesn't work), adv-ff limit its filename to 245 characters.

- On Windows, due to limitations in filename charsets, the characters `* " < > : | ?` will be remplaced by an underscore.