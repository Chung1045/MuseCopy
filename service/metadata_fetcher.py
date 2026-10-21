from tinytag import TinyTag

def fetch_metadata(filePath):
    tag: TinyTag = TinyTag.get(filePath)
    return tag
