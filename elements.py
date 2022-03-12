
class Heading(list):
    def __init__(self, level):
        self.level = level
        super().__init__()
        
    def __repr__(self):
        return f"Heading(level={self.level}, {super().__repr__()})"

class Paragraph(list):
    def __repr__(self):
        return f"Paragraph({super().__repr__()})"

class Text(str):
    def __repr__(self):
        return f"Text({super().__repr__()})"

class Strong(list):
    def __repr__(self):
        return f"Strong({super().__repr__()})"

class Block(str):
    """
    A code block opened by multiple back-ticks
    but without any info => doesn't contain source
    code.
    """
    def __repr__(self):
        return f"Block({super().__repr__()})"

class ListItem(list):
    def __repr__(self):
        return f"ListItem({super().__repr__()})"

class UnorderedList:
    def __init__(self):
        self.items = []
        
    def __repr__(self):
        return f"UnorderedList({self.items})"
        
class Quote(list):
    def __repr__(self):
        return f"Quote({super().__repr__()})"
    
class LineBreak:
    def __repr__(self):
        return f"LineBreak({super().__repr__()})"
    
class Emphasis(list):
    def __init__(self, strength):
        self.strength = strength
        super().__init__()
        
    def __repr__(self):
        return f"Emphasis(strength={self.strength}, {super().__repr__()})"
        
class Tag(str):
    def __repr__(self):
        return f"Tag({super().__repr__()})"
    
class Link(list):
    def __init__(self, href):
        self.href = href
        super().__init__()
        
    def __repr__(self):
        return f"Link(href={self.href}, {super().__repr__()})"
        
class PluginInvocation:
    def __init__(self, name, args, content):
        self.name = name
        self.args = args
        self.content = content
        
    def __repr__(self):
        return f"CodeBlock(name={self.name}, args={self.args}, content={self.content})"
        
class OrderedList:
    def __init__(self):
        self.items = []
        
    def __repr__(self):
        return f"OrderedList({self.items})"
        
class Image:
    def __init__(self, src, alt):
        self.src = src
        self.alt = alt
        
    def __repr__(self):
        return f"Image(src={self.src}, alt={self.alt})"
