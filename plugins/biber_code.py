from biber import PluginError

def generate_content(content, args):
    if "language" not in args:
        raise PluginError("code block needs language argument")
    
    return f'''\
        <pre><code class="language-{args['language']} line-numbers">{content}</code></pre>
    '''
