def get_text(nodelist):
    """Helper function to pull text out of XML nodes."""
    retval = ''.join([node.data for node in nodelist
                      if node.nodeType == node.TEXT_NODE]) 
    return retval
