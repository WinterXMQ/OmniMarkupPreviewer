from .base_renderer import *
import re
import markdown


@renderer
class MarkdownRenderer(MarkupRenderer):
    FILENAME_PATTERN_RE = re.compile(r'\.(md|mmd|mkdn?|mdwn|mdown|markdown|litcoffee)$')
    YAML_FRONTMATTER_RE = re.compile(r'\A---\s*\n.*?\n?^---\s*$\n?', re.DOTALL | re.MULTILINE)
    MARKDOWN_SYNTAX_RE = re.compile(r'^text\.html\.markdown\S*')

    def load_settings(self, renderer_options, global_setting):
        super(MarkdownRenderer, self).load_settings(renderer_options, global_setting)
        if 'extensions' in renderer_options:
            extensions = renderer_options['extensions']
        else:
            # Fallback to the default GFM style
            extensions = ['tables', 'strikeout', 'fenced_code', 'codehilite']
        extensions = set(extensions)
        for ext in extensions:
            if ext in ['abbr', 'admonition', 'attr_list', 'codehilite', 'def_list', 'extra', 'fenced_code', 'footnotes', 'headerid', 'meta', 'nl2br', 'sane_lists', 'smart_strong', 'smarty', 'tables', 'toc', 'wikilinks']:
                extensions.remove(ext)
                extensions.add('markdown.extensions.%s' % ext)
        if global_setting.mathjax_enabled:
            if 'mathjax' not in extensions:
                extensions.add('mdx_mathjax')
        if 'smartypants' in extensions:
            extensions.remove('smartypants')
            extensions.add('smarty')
        if 'codehilite' in extensions:
            extensions.remove('codehilite')
            extensions.add('codehilite(linenums=False,guess_lang=False)')
        self.extensions = list(extensions)

    @classmethod
    def is_enabled(cls, filename, syntax):
        """Looks for any syntax that begins with 'text.html.markdown'.

        Common options are:

        * text.html.markdown  # normal
        * text.html.markdown.gfm  # github-flavored
        * text.html.markdown.multimarkdown  # fletcherpenney.net/multimarkdown
        """
        if cls.MARKDOWN_SYNTAX_RE.match(syntax):
            return True
        return cls.FILENAME_PATTERN_RE.search(filename) is not None

    def render(self, text, **kwargs):
        text = self.YAML_FRONTMATTER_RE.sub('', text)
        return markdown.markdown(text, output_format='html5',
                                 extensions=self.extensions)
