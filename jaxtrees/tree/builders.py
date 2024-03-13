from . import JaxTree, JaxNode

def THeight_legacy(h,degree,new_node=JaxNode,fake_root=None):
    def _builder(h,degree,parent):
        """ generative tree of given height and degree """
        node = new_node(); node.parent = parent; node.children = None
        if h > 1:
            node.children = [_builder(h-1,degree,node) for i in range(degree)]
        return node
    
    if fake_root is None:
        return JaxTree(root=_builder(h,degree,None))
    else:
        fake_root.children = [_builder(h,degree,fake_root)]
        return JaxTree(root=fake_root)



def assymetric_tree(h):
    """ generative tree of given height """
    if h ==1:
        return JaxTree(JaxNode())
    # build asymmetric tree
    root = JaxNode(children=[JaxNode(),JaxNode()])

    root.children[0].parent = root
    root.children[1].parent = root

    node = root.children[1]

    for i in range(h-1):
        node.children = [JaxNode(),JaxNode()]
    
        node.children[0].parent = node
        node.children[1].parent = node

        node = node.children[1]


    tree = JaxTree(root)
    return tree 

### Tree generation and initialization
def tree_from_newick(newick_str):
    """Generate a JaxTree from a Newick string."""
    def parse_newick(newick_str):
        k = -1
        root = current_node = JaxNode(children=[])  # Start with a root node
        for i, char in enumerate(newick_str):
            if i < k:
                #For some reason, the i and char will not be overwritten and contuine from there in the loop 
                # so we make this to skip where i<k, where k is the position of the last letter or number we use  
                continue
            elif char == '(':
                # Create a new node and make it a child of the current node
                new_node = JaxNode(parent=current_node,children =[])
                current_node.children += [new_node]
                current_node = new_node  # Move down to the new node

            elif char == ',':
                # Go up to the parent, and then create a sibling node
                current_node = current_node.parent
                new_node = JaxNode(parent=current_node,children =[])
                current_node.children += [new_node]


                current_node = new_node  # Move to the new sibling node
            elif char == ')':
                # End of a subtree, move up to the parent node
                current_node = current_node.parent
            elif char == ':':
                # Branch length follows
                start = i + 1
                while i + 1 < len(newick_str) and newick_str[i + 1] not in [',', ')', ';', ' ']:
                    i += 1
                current_node.data["edge_length"] = float(newick_str[start:i + 1])
                k = i+1

            elif char not in [';', ' ',":"] and newick_str[i-1] not in [':']: # This does not work
                # Reading a node name, collect all characters till we hit a control character
                start = i

                while i + 1 < len(newick_str) and newick_str[i + 1] not in ['(', ')', ',', ';', ':', ' ']:
                    i += 1

                current_node.name = newick_str[start:i + 1]

                # For some reason this will not overwrite in the loop.... 
                #i  = i;char = newick_str[i+1]  # Adjust because the outer loop will increment `i`
                k = i+1
                
        return JaxTree(root)
    return parse_newick(newick_str)


### Alternative Newick tree generation
def tree_from_newick_recursive(newick_str):
    import re

    iter_tokens = re.finditer(r"([^:;,()\s]*)(?:\s*:\s*([\d.]+)\s*)?([,);])|(\S)", newick_str+";")

    def recursive_parse_newick(parent=None):
        name, length, delim, char = next(iter_tokens).groups(0)

        node = JaxNode(name=name if name else None,             # create a "ghost" subtree root node without data
                       data={"edge_length": float(length)} if length else {},
                       parent=parent,
                       children=[])
        
        if char == "(": # start a subtree

            while char in "(,": # add all children within a parenthesis to the current node
                child, char = recursive_parse_newick(parent=node)
                node.children.append(child)

            name, length, delim, char = next(iter_tokens).groups(0)

            node.name = name                        # assign data to the "ghost" subtree root node
            node.data = {"edge_length": float(length)} if length else {}
            
        return node, delim
    
    return recursive_parse_newick()[0]
