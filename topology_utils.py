from pathlib import Path


OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def render_topo(net, out_file="topo.svg"):
    import pydot

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / Path(out_file).name
    graph = pydot.Dot(graph_type="graph")
    for host in net.hosts:
        node = pydot.Node(
            host.name,
            shape="ellipse",
            color="blue",
            style="filled",
            fillcolor="#e8f0fe",
        )
        graph.add_node(node)
    for switch in net.switches:
        node = pydot.Node(
            switch.name,
            shape="box",
            color="red",
            style="filled",
            fillcolor="#ffe8e8",
        )
        graph.add_node(node)
    for link in net.links:
        node1 = link.intf1.node.name
        node2 = link.intf2.node.name
        graph.add_edge(pydot.Edge(node1, node2))
    graph.write_svg(str(output_path))
    print(f"export to {output_path}")


def render_topo_switches_only(net, out_file="topo_switches_only.svg"):
    import pydot

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / Path(out_file).name
    graph = pydot.Dot(graph_type="graph")
    for switch in net.switches:
        node = pydot.Node(
            switch.name,
            shape="box",
            color="red",
            style="filled",
            fillcolor="#ffe8e8",
        )
        graph.add_node(node)
    for link in net.links:
        if link.intf1.node in net.switches and link.intf2.node in net.switches:
            node1 = link.intf1.node.name
            node2 = link.intf2.node.name
            graph.add_edge(pydot.Edge(node1, node2))
    graph.write_svg(str(output_path))
    print(f"export to {output_path}")
