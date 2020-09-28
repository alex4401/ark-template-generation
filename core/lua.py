import luadata


def format_table(data):
    return luadata.serialize(data,
                             form=True).replace('\\t',
                                                '  ').replace('\\n', '\n')
