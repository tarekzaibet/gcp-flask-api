from marshmallow import Schema, fields


class ProjectSchema(Schema):
    name = fields.Str(required=True)
    folder_id = fields.Str(required=True)
    owner_email = fields.Str(required=True)
    application_code = fields.Str(required=False)
    budget_code = fields.Str(required=False)
    environment = fields.Str(required=False)


class FolderSchema(Schema):
    name = fields.Str(required=True)
    folder_id = fields.Str(required=True)
    owner_email = fields.Str(required=True)
    application_code = fields.Str(required=False)
    budget_code = fields.Str(required=False)
    environments = fields.List(fields.Str(required=True))

