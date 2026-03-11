from typing import Callable, Dict, List
from attrs import define, field, Factory
from collections import defaultdict

import ipywidgets as widgets
import ipytree as ipyt
from IPython.display import display, clear_output

def _construct_hierarchical_dict_data(lst, keys) -> Dict:
    """ builds the hierarchical tree from the contexts:
    Usage:
        included_session_context_dict_tree = [ctxt.to_dict() for ctxt in included_session_contexts]
        keys = ['format_name', 'animal', 'exper_name', 'session_name']
        dict_list = included_session_context_dict_tree.copy()
        tree = _construct_hierarchical_dict_data(dict_list, keys)
        tree
    """
    tree = defaultdict(list)
    if len(keys) == 1:
        for d in lst:
            tree[d[keys[0]]].append(d)
        return dict(tree)
    for d in lst:
        tree[d[keys[0]]].append(d)
    for k, v in tree.items():
        tree[k] = _construct_hierarchical_dict_data(v, keys[1:])
    return dict(tree)

@define(slots=False)
class JupyterTreeWidget:
    """ displays a collapsable/expandable tree widget 

    Usage:
        from pyphocorehelpers.gui.Jupyter.TreeWidget import JupyterTreeWidget
        jupyter_tree_widget = JupyterTreeWidget(included_session_contexts=included_session_contexts)

    """
    included_session_contexts: List = field(default=Factory(list)) # IdentifyingContext
    tree: ipyt.Tree = field(default=None, init=False) #field(default=Factory(ipyt.Tree))
    max_depth: int = field(default=20)
    on_selection_changed_callbacks: List[Callable] = field(default=Factory(list))
    display_on_init: bool = field(default=True)
    
    def __attrs_post_init__(self):
        self.construct_and_display_tree()


    def on_node_selected(self, change):
        print(f'.on_node_selected(change: {change})') # change: {'name': 'selected', 'old': False, 'new': True, 'owner': Node(name='fet11-01_12-58-54', selected=True), 'type': 'change'}
        if change['new']:
            clear_output(wait=True)  # Prevent scrolling
            display(self.tree)  # Redisplay the tree to maintain focus
            
            selected_node = change['owner']
            # print(f"Selected node: {selected_node.name}")
            if hasattr(selected_node, 'context'):
                selected_context = selected_node.context
                print(f"Selected context: {selected_context}")
                for a_callback in self.on_selection_changed_callbacks:
                    ## perform the callbacks
                    a_callback(selected_node, selected_context)
        
            self.tree.layout.display = 'none'  # Hide temporarily
            self.tree.layout.display = 'block'  # Show it again to refresh
        

        
        
    def build_tree(self, node, value, depth=0):
        """ constructs the ipytree nodes (GUI objects)"""
        if depth > self.max_depth:
            return

        if isinstance(value, dict):
            for key, child_value in value.items():
                child_node = ipyt.Node(key)
                child_node.selectable = False  # Make non-leaf nodes non-selectable
                node.add_node(child_node)
                self.build_tree(child_node, child_value, depth=depth+1)
        elif isinstance(value, (list, tuple)):
            for context in value:
                a_session_name: str = str(context['session_name'])
                is_parent_node_leaf: bool = False
                if (node.name == a_session_name):
                    is_parent_node_leaf = True
                    leaf_node = node # the parent node is the leaf because they have the same name
                else:                        
                    leaf_node = ipyt.Node(a_session_name)
                
                leaf_node.context = context  # Storing the original context as an attribute
                leaf_node.observe(self.on_node_selected, 'selected')
                if (not is_parent_node_leaf):
                    node.add_node(leaf_node)

        else:
            raise NotImplementedError(f'Unknown type for value: type(value): {type(value)} (expected (dict, list, or tuple), value: {value}')

    def construct_and_display_tree(self):
        """ uses `self.included_session_contexts` to build the tree to display. """
        included_session_context_dict_tree: List[Dict] = [ctxt.to_dict() for ctxt in self.included_session_contexts]
        assert len(included_session_context_dict_tree) > 0, f"tree cannot be empty but self.included_session_contexts: {self.included_session_contexts} "
        keys: List[str] = list(included_session_context_dict_tree[0].keys()) ## get keys from the first item
        
        ## TODO: assert that they're equal for all entries?
        # keys = ['format_name', 'animal', 'exper_name', 'session_name']
        tree_data: Dict = _construct_hierarchical_dict_data(included_session_context_dict_tree, keys) # calls `_construct_hierarchical_dict_data`
        root_node = ipyt.Node('root')
        self.build_tree(root_node, tree_data)
        
        self.tree = ipyt.Tree(nodes=[root_node], multiple_selection=False, animation=0)
        # self.tree.add_node(root_node)
        
        if self.display_on_init:
            display(self.tree)


                
# @function_attributes(short_name=None, tags=[''], input_requires=[], output_provides=[], uses=[], used_by=[], creation_date='2024-09-24 02:46', related_items=[])
def create_log_viewer(logs: dict[str, str]) -> widgets.Tab:
    """ 
    Usage:
        from pyphocorehelpers.gui.Jupyter.TreeWidget import create_log_viewer
        
        # Example usage:
        logs = {
            'log1.txt': 'This is the content of log 1.\nLine 2.\nLine 3.',
            'log2.txt': 'This is the content of log 2.\nLine 2.\nLine 3.',
            'log3.txt': 'This is the content of log 3.\nLine 2.\nLine 3.'
        }

        log_viewer = create_log_viewer(logs=run_logs)
        display(log_viewer)

    """
    tab = widgets.Tab()

    children = []
    for key, value in logs.items():
        text_area = widgets.Textarea(
            value=value,
            disabled=True,  # Make it read-only
            layout=widgets.Layout(width='100%', height='400px')  # Scrollable area
        )
        children.append(text_area)

    tab.children = children
    for i, key in enumerate(logs.keys()):
        tab.set_title(i, key)

    return tab



# ==================================================================================================================== #
# Tree/Hierarchy Renderers and Previewers                                                                              #
# ==================================================================================================================== #


# def on_node_selected(change):
#     if change['new']:  # Node selected
#         print(f"Selected node: {change['owner'].name}")

# def build_tree(node, value, max_depth=20, depth=0):
#     """ 
#         import ipytree as ipyt
#         from IPython.display import display
#         from pyphocorehelpers.gui.Jupyter.TreeWidget import build_tree


#         # Assume curr_computations_results is the root of the data structure you want to explore
#         root_data = a_sess_config.preprocessing_parameters
#         root_node = ipyt.Node('sess.config')
#         build_tree(root_node, root_data)

#         tree = ipyt.Tree()
#         tree.add_node(root_node)
#         display(tree)
#     """
#     if depth > max_depth:
#         return

#     if isinstance(value, dict):
#         for key, child_value in value.items():
#             child_node = ipyt.Node(key)
#             node.add_node(child_node)
#             build_tree(child_node, child_value, max_depth=max_depth, depth=depth+1)
#     else:
#         ## add leaf node:
#         # node.add_node(ipyt.Node(str(value)))
#         leaf_node = ipyt.Node(str(value))
#         leaf_node.observe(on_node_selected, 'selected')
#         node.add_node(leaf_node)

