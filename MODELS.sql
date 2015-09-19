DROP SCHEMA ea CASCADE;
CREATE SCHEMA ea;

CREATE TABLE item (
        id SERIAL,
        virtual boolean NOT NULL DEFAULT FALSE, -- a virtual relation_id has no relation and is used only to group related items
        PRIMARY KEY(id)
);

CREATE TABLE translation (
        id SERIAL, -- TODO: replace by hash of translation (=> remove duplicate)
        translation TEXT NOT NULL,
        PRIMARY KEY(id)
);

CREATE TABLE relation (
        id SERIAL,
        item_id integer NOT NULL REFERENCES item(id),
        relation_id integer NOT NULL REFERENCES item(id),
        PRIMARY KEY (id)
);

CREATE TABLE link_translation (
        link_id integer NOT NULL REFERENCES link(id),
        translation_id integer NOT NULL REFERENCES translation(id),
        lang char(2) NOT NULL, -- we must always have english since we will search "IN (choosen_lang, 'en')"
        PRIMARY KEY (link_id, translation_id, lang)
);

CREATE TABLE link_relation (
        link_id integer NOT NULL REFERENCES link(id),
        relation_id integer NOT NULL REFERENCES relation(id),
        PRIMARY KEY (link_id, relation_id)
);

CREATE TABLE link (
        id SERIAL, -- TODO: replace by hash of link (=> remove duplicate)
        link TEXT,
        priority integer DEFAULT 0,
        -- format_id intger, -- gotten from python link importer (an hash of a static hash defining the domain) or null if unmanaged link
        item_id integer REFERENCES item(id), -- main item id related to link (there could be unrelated link)
        PRIMARY KEY(id)
);

-- todo: check integer UNSIGNED to see if it is present in postgresql
