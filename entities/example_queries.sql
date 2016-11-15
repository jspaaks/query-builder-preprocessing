# Get all the instances of a given entity <ID>
SELECT name,url,mention_count FROM instance WHERE entity_id = <ID>;

# Get all the decendant entities (children, grandchildren, etc.) of the entity <ID>
WITH tblChild AS
(
    SELECT * FROM entities WHERE parent_id = <ID>
    UNION ALL
    SELECT entities.* FROM entities  JOIN tblChild  ON entities.parent_id = tblChild.id
)
SELECT name FROM tblChild;

# Get all the name of the instances from descendant entities of the entity <ID> (including also its own instances)
SELECT i.name FROM instances i,
(WITH tblChild AS
(
    SELECT * FROM entities WHERE parent_id = <ID>
    UNION ALL
    SELECT entities.* FROM entities  JOIN tblChild  ON entities.parent_id = tblChild.id
)
SELECT id FROM tblChild
UNION ALL
SELECT <ID>) t
WHERE i.entity_id = t.id;

# Get all the ancestors of an entity <ID>
WITH tblParent AS
(
    SELECT * FROM entities WHERE id = <ID>
    UNION ALL
    SELECT entities.* FROM entities JOIN tblParent  ON entities.id = tblParent.parent_id
)
SELECT name FROM tblParent WHERE id <> <ID>;

# Get all the ancestor entities of the entity of a instance (including the entity)
WITH tblParent AS
(
    SELECT * FROM entities WHERE id = (SELECT entity_id FROM instances WHERE id = <ID>)
    UNION ALL
    SELECT entities.* FROM entities JOIN tblParent  ON entities.id = tblParent.parent_id
)
SELECT * FROM tblParent;
