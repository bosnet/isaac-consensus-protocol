
def log_current_state(now, design, log_state):
    assert isinstance(now, set)
    for node_name, consensus in sorted(now):
        node_design = getattr(design.nodes_by_name, node_name)
        faulties = getattr(design.faulties, node_design.node.name, list())
        log_state.metric(
            node=node_name,
            messages=consensus.messages,
            faulties=faulties,
            quorum=dict(
                threshold=node_design.quorum.threshold,
                validators=list(map(lambda x: x.name, node_design.quorum.validators)),
            ),
        )

    return
