#!/usr/bin/python
import argparse
import os
import json
import sqlite3


def parse_node(node, cursor, parent_id=None):
    if 'type' in node.keys():
        # entity
        num_children = len(node['children']) if 'children' in node.keys() else 0
        cursor.execute('INSERT INTO entities ' +
                       '(url,name,mention_count,children_count,instance_count,parent_id) VALUES (?,?,?,?,?,?)',
                       (node['url'], node['name'], node['mention_count'], num_children, node['instance_count'],
                        parent_id))

        entity_id = cursor.lastrowid
        if node['instance_count']:
            # It has instances
            for instance in node['instances']:
                parse_node(instance, cursor, entity_id)

        if num_children:
            for child in node['children']:
                parse_node(child, cursor, entity_id)
        return None
    else:
        # instance
        cursor.execute('INSERT INTO instances (url,name,mention_count,entity_id) VALUES (?,?,?,?)',
                       (node['url'], node['name'], node['mention_count'], parent_id))
        return None


def run(input_json, db_name):
    if not os.path.isfile(input_json):
        raise Exception('File not found: ' + input_json)

    if not db_name.endswith('.db'):
        raise Exception('DB name must end with .db')

    conn = sqlite3.connect(db_name)

    c = conn.cursor()

    c.execute("""CREATE TABLE entities (
                   id integer primary key autoincrement,
                   url text not null,
                   name text not null,
                   mention_count integer not null,
                   children_count integer not null,
                   instance_count integer not null,
                   parent_id integer,
                   FOREIGN KEY(parent_id) REFERENCES entities(id))""")

    c.execute("""CREATE TABLE instances (
                   id integer primary key autoincrement,
                   url text not null,
                   name text not null,
                   mention_count integer not null,
                   entity_id integer not null,
                   FOREIGN KEY(entity_id) REFERENCES entities(id))""")

    with open(input_json) as jsonFile:
        data = json.load(jsonFile)
        parse_node(data['children'][0], c)

    c.execute("CREATE INDEX entities_name ON entities (name)")
    c.execute("CREATE INDEX instances_name ON instances (name)")

    conn.commit()

    conn.close()


def argument_parser():
    # define argument menu
    description = "Creates a SQLite DB database file from a StoryTeller JSON file"
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('-i', '--input', default='', help='Input JSON file', type=str, required=True)
    parser.add_argument('-n', '--name', default='', help='DB name (must end with .db)', type=str, required=True)
    return parser


def main():
    try:
        a = argument_parser().parse_args()
        run(a.input, a.name)
    except Exception as e:
        print(e)

if __name__ == "__main__":
    main()
