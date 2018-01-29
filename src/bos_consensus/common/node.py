class Node:
    name = None
    endpoint = None

    def __init__(self, name, endpoint):
        assert isinstance(name, str)

        self.name = name
        self.endpoint = endpoint

    def __eq__(self, rhs):
        assert isinstance(rhs, Node)
        rhs_endpoint = rhs.endpoint
        lhs_endpoint = self.endpoint

        t_str = '//localhost:'  # target_string
        r_str = '//127.0.0.1:'  # replace_string
        if t_str in rhs_endpoint:
            rhs_endpoint.replace(t_str, r_str)

        if t_str in lhs_endpoint:
            lhs_endpoint.replace(t_str, r_str)

        return lhs_endpoint == rhs_endpoint

    def __repr__(self):
        return '<Node: %s(%s)>' % (self.name, self.endpoint)

    def to_dict(self):
        return dict(
            name=self.name,
            endpoint=self.endpoint
        )

    def check_faulty(self):
        return False

