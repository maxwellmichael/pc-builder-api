from marshmallow import schema, fields
from marshmallow.validate import Length, Range


class ItemsSchema(schema):
    name = fields.Str(required=True, validate=Length(min=6))
    price = fields.Float(required=True)
    category = fields.Str(required=True)
    imageUrl = fields.URL()
    description = fields.Str()
    totalRating = fields.Int()
    starRating = fields.Float()
    userId = fields.Int(required=True)
    buildId = fields.Int(required=True)


class BuildsSchema(schema):
    name = fields.Str(required=True)
    description = fields.Str()
    totalValue = fields.Int()
    dateCreated = fields.DateTime()
    userId = fields.Int(required=True)
    items = fields.List(fields.Nested(ItemsSchema))


class UsersSchema(schema):
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    isOnline = fields.Bool()
    isAdmin = fields.Bool()
    lastOnline = fields.DateTime()
    createdOn = fields.DateTime()
    modifiedOn = fields.DateTime()
    builds = fields.List(fields.Nested(BuildsSchema))
    privateId = fields.Str()
