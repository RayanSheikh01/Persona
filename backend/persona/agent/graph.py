from .nodes.retrieve import make_retrieve_node
from .nodes.respond import render_memories
from .nodes.extract import make_extract_node
from .nodes.persist import make_persist_node
from .state import ChatState

class StateGraph:
    def __init__(self, state_cls):
        self.state_cls = state_cls
        self.nodes = {}
        self.edges = {}
        self.entry_point = None

    def add_node(self, name, func):
        self.nodes[name] = func

    def add_edge(self, from_node, to_node):
        if from_node not in self.edges:
            self.edges[from_node] = []
        self.edges[from_node].append(to_node)

    def set_entry_point(self, node_name):
        self.entry_point = node_name

    def compile(self):
        # For simplicity, we return a function that executes the graph
        async def execute(initial_input):
            state = self.state_cls()
            current_node = self.entry_point
            input_data = initial_input
            while current_node != END:
                node_func = self.nodes[current_node]
                output_data = await node_func(input_data)
                state.update(output_data)
                next_nodes = self.edges.get(current_node, [])
                if not next_nodes:
                    break
                current_node = next_nodes[0]  # For simplicity, we take the first edge
                input_data = state.get()  # Pass the entire state to the next node
            return state.get()
        return execute

def build_graph(*, conn, store, client, system_prompt, extract_prompt,
                on_token=None, on_retrieved=None):
    g = StateGraph(ChatState)
    g.add_node("retrieve", make_retrieve_node(store=store, client=client, on_retrieved=on_retrieved))
    g.add_node("respond",  render_memories(client=client, system_prompt_template=system_prompt, on_token=on_token))
    g.add_node("extract",  make_extract_node(client=client, extract_prompt=extract_prompt))
    g.add_node("persist",  make_persist_node(conn=conn, store=store, client=client))
    g.set_entry_point("retrieve")
    g.add_edge("retrieve", "respond")
    g.add_edge("respond", "extract")
    g.add_edge("extract", "persist")
    g.add_edge("persist", END)
    return g.compile()