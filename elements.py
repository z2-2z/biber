#TODO: tables

class Element:
    pass

class Heading(list, Element):
    def __init__(self, level):
        self.level = level
        super().__init__()
        
    def __repr__(self):
        return f"Heading(level={self.level}, {super().__repr__()})"

class Paragraph(list, Element):
    def __repr__(self):
        return f"Paragraph({super().__repr__()})"

class Text(str, Element):
    def __repr__(self):
        return f"Text({super().__repr__()})"

class Strong(list, Element):
    def __repr__(self):
        return f"Strong({super().__repr__()})"

class Block(str, Element):
    """
    A code block opened by multiple back-ticks
    but without any info => doesn't contain source
    code.
    """
    def __repr__(self):
        return f"Block({super().__repr__()})"

class ListItem(list, Element):
    def __repr__(self):
        return f"ListItem({super().__repr__()})"

class UnorderedList(Element):
    def __init__(self):
        self.items = []
        
    def __repr__(self):
        return f"UnorderedList({self.items})"
        
class Quote(list, Element):
    def __repr__(self):
        return f"Quote({super().__repr__()})"
    
class LineBreak(Element):
    def __repr__(self):
        return f"LineBreak()"
    
class Emphasis(list, Element):
    def __init__(self, strength):
        self.strength = strength
        super().__init__()
        
    def __repr__(self):
        return f"Emphasis(strength={self.strength}, {super().__repr__()})"
        
class Tag(str, Element):
    def __repr__(self):
        return f"Tag({super().__repr__()})"
    
class Link(list, Element):
    def __init__(self, href):
        self.href = href
        super().__init__()
        
    def __repr__(self):
        return f"Link(href={self.href}, {super().__repr__()})"
        
class PluginInvocation(Element):
    def __init__(self, name, args, content):
        self.name = name
        self.args = args
        self.content = content
        
    def __repr__(self):
        return f"CodeBlock(name={self.name}, args={self.args}, content={self.content})"
        
class OrderedList(Element):
    def __init__(self):
        self.items = []
        
    def __repr__(self):
        return f"OrderedList({self.items})"
        
class Image(Element):
    def __init__(self, src, alt):
        self.src = src
        self.alt = alt
        
    def __repr__(self):
        return f"Image(src={self.src}, alt={self.alt})"
