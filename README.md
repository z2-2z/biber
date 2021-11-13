# Biber
![so cute](./socute.png)

Biber (german for "beaver") is a static website generator.   
It generates a complete blog from a serious of `.post` files,
each describing one blog post.
The `.post` files must follow a custom format but mainly consist
of markdown content that can be extended with custom plugins.

Biber is not a general purpose website generator, it only generates
my blog how I want it.

Features:
- Support for external plugins
- PGP integration (signing of posts and files)

## Installation
```sh
git clone https://github.com/z2-2z/biber
python3 -m virtualenv biber-env
source biber-env/bin/activate
python3 -m pip install -r biber/requirements.txt
```

## Usage
In your `biber-env` run:
```
python3 -m biber <config file>
```
Where `config file` is a configuration file as described below.

## Configuration
The configuration file follows the INI file format.  

### The `Blog` section
```
[Blog]
in: path/to/post/files
out: path/to/webroot
title: My Blog Title
plugins: path/to/folder/with/plugins
```

- `in`: Folder with `.post` files. Subfolders are also scanned. __(mandatory)__
- `out`: This is the folder where the resuling html files will be stored __(mandatory)__
- `title`: The title of your blog as it will be displayed on the index file __(mandatory)__
- `plugins`: Specifies a folder where custom plugins are located. See more about plugins below. __(optional)__

### The `Socials` section
Here you can specify how you can be reached. The entire section is optional.
```
[Socials]
twitter: <twitter handle>
hackerone: <hackerone handle>
github: <github handle>
pubkey: <key id>
```
This should be pretty self explanatory except for:
- `pubkey`: You can put a key id there and biber will export the
 public key and make it downloadable. This will be treated as an
 E-Mail social with a link to a key instead of `mailto:`. __(optional)__
 
### The `PGP` section
Biber supports automatic signing of files and posts. This section is optional.
```
[PGP]
key: <key id>
dir: path/to/gnupg-homedir
binary: /path/to/gpg-executable
sign-posts: <boolean>
```
- `key`: The key id used for signing __(mandatory)__
- `dir`: gnupg's homedir (`--homedir` option) __(optional)__
- `binary`: The pgp program that gets executed __(optional)__
- `sign-posts`: Whether to sign posts (either `true` or `false`) __(optional)__

## Posts
A blog post is described by a single `.post` file that consists
of two sections:
1. Metadata
2. Markdown content

### Metadata
Metadata is specified in the form of `key: value` pairs with one pair
per line like this:
```
author: <author name>
category: <category name>
date: DD.MM.YYYY
sign: <list of filenames>
attachment: <list of filenames>
```
- `author`: The author of the article __(mandatory)__
- `category`: The category of the post (only one category is allowed) __(mandatory)__
- `date`: When the post was created __(mandatory)__
- `sign`: A list of files to sign with PGP. This will create files like `<filename>.sig` where `<filename>` occured in the list of filenames. __(optional)__
- `attachment`: A list of files that shall be copied into the post directory under the webroot. Normally only referenced images are copied. __(optional)__

### Markdown Content
After the metadata lines you can write markdown as you are used to.
But note that the first markdown element must be a h1 heading (`#`). This will denote the title of the blog post, as displayed in the
index. 

## Plugins
Biber enables use of plugins via code blocks like this:
````
```plugin_name opt1=val1,opt2=val2
content that gets sent to plugin
```
````

A plugin is a python file that starts with `biber_` and ends with `.py`. In the example above it would be `biber_plugin_name.py`. It must reside in a directory specified by the `plugins`
directive in the `Blog` section of the configuration file.

A plugin must define one method `generate_content(content, flags)`:
- `content`: The text that is inside the code block
- `flags`: A dictionary with options

In the example above `flags` would have the value:
```
{
    "opt1" : "val1",
    "opt2" : "val2"
}
```
`generate_content` must return HTML that gets embedded into the website.

### Biber API
Biber offers some convenience functions for plugins:
- `class PluginError`: raise this exception instead of builtin exceptions when something goes wrong
- `md_to_html(md)`: Converts markdown content in `md` to HTML
