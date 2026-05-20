from langgraph.graph import END, StateGraph

from .nodes.extract import make_extract_node
from .nodes.summarize import make_summarize_node
from .nodes.persist import make_persist_node
from .nodes.respond import make_respond_node
from .nodes.retrieve import make_retrieve_node
from .state import ChatState


def build_graph(
    *,
    conn,
    store,
    client,
    system_prompt: str,
    extract_prompt: str,
    on_token=None,
    on_retrieved=None,
    summary_store=None
):
    g = StateGraph(ChatState)
    g.add_node(
        "retrieve",
        make_retrieve_node(store=store, client=client, on_retrieved=on_retrieved),
    )
    g.add_node(
        "respond",
        make_respond_node(
            client=client, system_prompt_template=system_prompt, on_token=on_token
        ),
    )
    g.add_node(
        "extract", make_extract_node(client=client, extract_prompt=extract_prompt)
    )
    if summary_store is not None:
        g.add_node(
            "summarize",
            make_summarize_node(
                summary_store=summary_store, buffer_turns=20, stride=10, summarizer=None
            ),
        )
    g.add_node("persist", make_persist_node(conn=conn, store=store, client=client))
    g.set_entry_point("retrieve")
    g.add_edge("retrieve", "respond")
    g.add_edge("respond", "extract")
    g.add_edge("extract", "persist")
    if summary_store is not None:
        g.add_edge("persist", "summarize")
        g.add_edge("summarize", END)
    else:
        g.add_edge("persist", END)

    return g.compile()
