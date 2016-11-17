import wtforms_json
from sqlalchemy import not_, desc
from sqlalchemy.orm.session import make_transient

from flask import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from datetime import datetime

from wateraware import app

import os

DATABASE_NAME = None
DATABASE_USER = None
DATABASE_PASSWORD = None

filename = os.path.join(os.path.dirname(__file__), '..', '..', 'conf')
with open(filename) as conf:
    for line in conf:
        line_array = line.split('=')
        if line_array[0] == "DATABASE_NAME":
            DATABASE_NAME = line_array[1].strip()
        if line_array[0] == "DATABASE_USER":
            DATABASE_USER = line_array[1].strip()
        if line_array[0] == "DATABASE_PASSWORD":
            DATABASE_PASSWORD = line_array[1].strip()

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{}:{}@localhost:5432/{}'.format(DATABASE_USER, DATABASE_PASSWORD, DATABASE_NAME)

db = SQLAlchemy(app)

wtforms_json.init()


class ModelObject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_updated = db.Column(db.TIMESTAMP, server_default=db.func.now(), onupdate=db.func.current_timestamp())

    # Added methods
    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, json):
        self.set_columns(**json)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_code(cls, code):
        return cls.query.filter(cls.code == code).one()

    # Returns the most recent datetime that an object was added to this table or the minimum date if the table is empty
    @classmethod
    def get_latest_date(cls):
        most_recent_instance = cls.query.order_by(desc(cls.date_updated)).first()
        if most_recent_instance:
            return most_recent_instance.date_updated
        else:
            return datetime.min

    @classmethod
    def delete_all_created_on_or_before_date(cls, date):
        cls.query.filter(cls.date_updated <= date).delete()

    @classmethod
    def is_instance_with_code(cls, code):
        return cls.query.filter(cls.code == code).scalar()

    @classmethod
    def count(cls):
        return cls.query.count()

    @classmethod
    def is_instance_with_id(cls, id):
        return cls.query.filter(cls.id == id).scalar()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter(cls.id == id).one()

    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def get_first(cls):
        return cls.query.first()

    @classmethod
    def update_by_id(cls, id, json):
        cls.getById(id).update(json)

    @classmethod
    def delete_by_id(cls, id):
        cls.getById(id).delete()
        db.session.commit()

    @classmethod
    def delete_all(cls):
        db.engine.execute("DELETE from {0} CASCADE".format(cls.__tablename__))

    @classmethod
    def replace_all(cls, jsonArray):
        cls.delete_all()
        for jsonObject in jsonArray:
            cls.add(jsonObject)

    @classmethod
    def add(cls, json):
        obj = cls()
        obj.save()
        obj.update(json)
        return obj

    @classmethod
    def print_float_statistics(cls, name, variable):
        answer = db.session.query(func.max(variable), func.min(variable), func.avg(variable), func.avg(variable)).one()
        print "---\nName: {}\nMax:  {}\nMin:  {}\nAvg:  {}\n---".format(name, *answer)

    @classmethod
    def print_foreign_key_statistics(cls, foreign_class, foreign_key):

        answer = db.session.query(foreign_key,
                                  func.count(foreign_key)).group_by(foreign_key).all()

        def print_row(row):
            print "{1} {0}".format(foreign_class.get_by_id(row[0]).name, row[1])

        print "---"
        map(print_row, answer)
        print "---"

    def copy(self):
        db.session.expunge(self)

        make_transient(self)
        self.id = None
        db.session.add(self)
        db.session.flush()
        return self

    """Base SQLAlchemy Model for automatic serialization and
    deserialization of columns and nested relationships."""

    __abstract__ = True

    # Stores changes made to this model's attributes. Can be retrieved
    # with model.changes
    _changes = {}

    def __init__(self, **kwargs):
        kwargs['_force'] = True
        self._set_columns(**kwargs)

    def _set_columns(self, **kwargs):
        force = kwargs.get('_force')

        readonly = []
        if hasattr(self, 'readonly_fields'):
            readonly = self.readonly_fields
        if hasattr(self, 'hidden_fields'):
            readonly += self.hidden_fields

        readonly += [
            'id',
            'created',
            'updated',
            'modified',
            'created_at',
            'updated_at',
            'modified_at',
        ]

        changes = {}

        columns = self.__table__.columns.keys()
        relationships = self.__mapper__.relationships.keys()

        for key in columns:
            allowed = True if force or key not in readonly else False
            exists = True if key in kwargs else False
            if allowed and exists:
                val = getattr(self, key)
                if val != kwargs[key]:
                    changes[key] = {'old': val, 'new': kwargs[key]}
                    setattr(self, key, kwargs[key])

        for rel in relationships:
            allowed = True if force or rel not in readonly else False
            exists = True if rel in kwargs else False
            if allowed and exists:
                is_list = self.__mapper__.relationships[rel].uselist
                if is_list:
                    valid_ids = []
                    query = getattr(self, rel)
                    cls = self.__mapper__.relationships[rel].argument()
                    for item in kwargs[rel]:
                        if 'id' in item and query.filter_by(id=item['id']).limit(1).count() == 1:
                            obj = cls.query.filter_by(id=item['id']).first()
                            col_changes = obj.set_columns(**item)
                            if col_changes:
                                col_changes['id'] = str(item['id'])
                                if rel in changes:
                                    changes[rel].append(col_changes)
                                else:
                                    changes.update({rel: [col_changes]})
                            valid_ids.append(str(item['id']))
                        else:
                            col = cls()
                            col_changes = col.set_columns(**item)
                            query.append(col)
                            db.session.flush()
                            if col_changes:
                                col_changes['id'] = str(col.id)
                                if rel in changes:
                                    changes[rel].append(col_changes)
                                else:
                                    changes.update({rel: [col_changes]})
                            valid_ids.append(str(col.id))

                    # delete related rows that were not in kwargs[rel]
                    for item in query.filter(not_(cls.id.in_(valid_ids))).all():
                        col_changes = {
                            'id': str(item.id),
                            'deleted': True,
                        }
                        if rel in changes:
                            changes[rel].append(col_changes)
                        else:
                            changes.update({rel: [col_changes]})
                        db.session.delete(item)

                else:
                    val = getattr(self, rel)
                    if self.__mapper__.relationships[rel].query_class is not None:
                        if val is not None:
                            col_changes = val.set_columns(**kwargs[rel])
                            if col_changes:
                                changes.update({rel: col_changes})
                    else:
                        if val != kwargs[rel]:
                            setattr(self, rel, kwargs[rel])
                            changes[rel] = {'old': val, 'new': kwargs[rel]}

        return changes

    def set_columns(self, **kwargs):
        self._changes = self._set_columns(**kwargs)
        if 'modified' in self.__table__.columns:
            self.modified = datetime.utcnow()
        if 'updated' in self.__table__.columns:
            self.updated = datetime.utcnow()
        if 'modified_at' in self.__table__.columns:
            self.modified_at = datetime.utcnow()
        if 'updated_at' in self.__table__.columns:
            self.updated_at = datetime.utcnow()
        return self._changes

    @property
    def changes(self):
        return self._changes

    def reset_changes(self):
        self._changes = {}

    def to_dict(self, show=None, hide=None, path=None, show_all=None):
        """ Return a dictionary representation of this model.
        """

        if not show:
            show = []
        if not hide:
            hide = []
        hidden = []
        if hasattr(self, 'hidden_fields'):
            hidden = self.hidden_fields
        default = []
        if hasattr(self, 'default_fields'):
            default = self.default_fields

        ret_data = {}

        if not path:
            path = self.__tablename__.lower()

            def prepend_path(item):
                item = item.lower()
                if item.split('.', 1)[0] == path:
                    return item
                if len(item) == 0:
                    return item
                if item[0] != '.':
                    item = '.%s' % item
                item = '%s%s' % (path, item)
                return item

            show[:] = [prepend_path(x) for x in show]
            hide[:] = [prepend_path(x) for x in hide]

        columns = self.__table__.columns.keys()
        relationships = self.__mapper__.relationships.keys()
        properties = dir(self)

        for key in columns:
            check = '%s.%s' % (path, key)
            if check in hide or key in hidden:
                continue
            if show_all or key is 'id' or check in show or key in default:
                ret_data[key] = getattr(self, key)

        for key in relationships:
            check = '%s.%s' % (path, key)
            if check in hide or key in hidden:
                continue
            if show_all or check in show or key in default:
                hide.append(check)
                is_list = self.__mapper__.relationships[key].uselist
                if is_list:
                    ret_data[key] = []
                    for item in getattr(self, key):
                        ret_data[key].append(item.to_dict(
                            show=show,
                            hide=hide,
                            path=('%s.%s' % (path, key.lower())),
                            show_all=show_all,
                        ))
                else:
                    if self.__mapper__.relationships[key].query_class is not None:
                        ret_data[key] = getattr(self, key).to_dict(
                            show=show,
                            hide=hide,
                            path=('%s.%s' % (path, key.lower())),
                            show_all=show_all,
                        )
                    else:
                        ret_data[key] = getattr(self, key)

        for key in list(set(properties) - set(columns) - set(relationships)):
            if key.startswith('_'):
                continue
            check = '%s.%s' % (path, key)
            if check in hide or key in hidden:
                continue
            if show_all or check in show or key in default:
                val = getattr(self, key)
                try:
                    ret_data[key] = json.loads(json.dumps(val))
                except:
                    pass

        return ret_data
