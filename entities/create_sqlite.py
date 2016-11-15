#!/usr/bin/python
import argparse
import os
import json
import sqlite3


def parse_node(node, cursor, parent_id=None):
    """
        this function recursively calls itself on its instances or children, if there are any.
    """

    def isexpandable():
        if 'instance_count' in node.keys() and node['instance_count'] > 0:
            return True
        elif 'children' in node.keys() and len(node['children']) > 0:
            return True
        else:
            return False

    if 'type' in node.keys():
        # node is an entity

        child_of = parent_id
        is_entity = True
        is_instance = False
        is_expandable = isexpandable()
        if 'mention_count' in node.keys():
            mention_count = node['mention_count']
        else:
            mention_count = 0
        name = node['name']
        url = node['url']

        cursor.execute('INSERT INTO nodes ' +
                       '(child_of,is_entity,is_expandable,is_instance,mention_count,name,url) VALUES (?,?,?,?,?,?,?)',
                       (child_of, is_entity, is_expandable, is_instance, mention_count, name, url))

        if 'children' in node.keys():
            num_children = len(node['children'])
        else:
            num_children = 0

        entity_id = cursor.lastrowid
        if node['instance_count'] > 0:
            # It has instances
            for instance in node['instances']:
                parse_node(instance, cursor, entity_id)

        if num_children > 0:
            for child in node['children']:
                parse_node(child, cursor, entity_id)
        return None
    else:
        # node is an instance

        child_of = parent_id
        is_entity = False
        is_instance = True
        is_expandable = isexpandable()
        if 'mention_count' in node.keys():
            mention_count = node['mention_count']
        else:
            mention_count = 0
        name = node['name']
        url = node['url']

        cursor.execute('INSERT INTO nodes ' +
                       '(child_of,is_entity,is_expandable,is_instance,mention_count,name,url) VALUES (?,?,?,?,?,?,?)',
                       (child_of, is_entity, is_expandable, is_instance, mention_count, name, url))

        return None


def run(input_json, db_name):
    if not os.path.isfile(input_json):
        raise Exception('File not found: ' + input_json)

    if not db_name.endswith('.db'):
        raise Exception('DB name must end with .db')

    conn = sqlite3.connect(db_name)

    c = conn.cursor()

    c.execute("""
        CREATE TABLE nodes (
            child_of integer,
            id integer primary key autoincrement,
            is_entity integer not null,
            is_expandable integer not null,
            is_instance integer not null,
            mention_count integer not null,
            name text not null,
            url text not null)
            """)

    with open(input_json) as jsonFile:
        data = json.load(jsonFile)
        parse_node(data['children'][0], c)

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
