from flask import request, jsonify
from flask_restful import Resource, reqparse, abort, fields, marshal_with
from app.models import BuildsModel, ItemsModel, UsersModel
from app import db
from flask_jwt_extended import (
    jwt_required, create_access_token,
    jwt_refresh_token_required, create_refresh_token,
    get_jwt_identity, set_refresh_cookies, set_access_cookies, unset_jwt_cookies
)


def getUserIdFromPublicId(pubId):
    user = UsersModel.query.filter_by(publicId=pubId).first()
    return user.id

itemArgs = reqparse.RequestParser()
itemArgs.add_argument("id", type=int)
itemArgs.add_argument("name", type=str)
itemArgs.add_argument("price", type=float)
itemArgs.add_argument("category", type=str)
itemArgs.add_argument("description", type=str)
itemArgs.add_argument("imageUrl", type=str)
itemArgs.add_argument("totalRating", type=int)
itemArgs.add_argument("starRating", type=float)
itemArgs.add_argument("buildId", type=int)

item_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'price': fields.Float,
    'category': fields.String,
    'description': fields.String,
    'imageUrl': fields.String,
    'totalRating': fields.Integer,
    'starRating': fields.Float,
    'buildId': fields.Integer,
    'userId': fields.Integer

}


def validateBuildID(userId, buildId):
    if not buildId:
        abort(404, message="Must Specify a Build ID")
    else:
        build = BuildsModel.query.filter_by(id=buildId, userId=userId).first()

        if not build:
            abort(404, message="Must Specify a Valid Build ID")


def validateUserId(userId):
    if not userId:
        abort(404, message="Must Specify a User ID")
    else:
        user = UsersModel.query.filter_by(id=userId).first()

        if not user:
            abort(404, message="Must Specify a Valid User ID")


def validateArgs(args, buildId, userId, method):
    if method == "get":
        if args['name']:
            item = ItemsModel.query.filter_by(name=args['name'], userId=userId, buildId=id).first()
            return item
        elif args['id']:
            item = ItemsModel.query.filter_by(id=args['id'], userId=userId, buildId=id).all()
            return item
        elif args['category']:
            item = ItemsModel.query.filter_by(category=args['category'], userId=userId, buildId=id).all()
            return item
        elif args['price']:
            item = ItemsModel.query.filter_by(price=args['price'], userId=userId, buildId=id).all()
            return item
        else:
            item = ItemsModel.query.filter_by(buildId=buildId, userId=userId).all()
            return item

    elif method == 'put':
        if not args['name'] or not args['category'] or not args['price']:
            return {"status": "Not all Params Specified"}
        else:
            item = ItemsModel(name=args['name'], category=args['category'], price=args['price'],
                              description=args['description'], imageUrl=args['imageUrl'], userId=userId,
                              buildId=buildId)
            db.session.add(item)
            db.session.commit()
            return {"status": "ok", 'item': item}

    elif method == 'delete':
        if args['id']:
            item = ItemsModel.query.filter_by(id=args['id'], userId=userId, buildId=buildId).first()
            db.session.delete(item)
            db.session.commit()
            return {"status": "ok"}

        elif args['name']:
            item = ItemsModel.query.filter_by(name=args['name'], userId=userId, buildId=buildId).first()
            db.session.delete(item)
            db.session.commit()
            return {"status": "ok"}

        elif args['category']:
            item = ItemsModel.query.filter_by(category=args['category'], userId=userId, buildId=buildId).first()
            db.session.delete(item)
            db.session.commit()
            return {"status": "ok"}

        elif args['price']:
            item = ItemsModel.query.filter_by(price=args['price'], userId=userId, buildId=buildId).first()
            db.session.delete(item)
            db.session.commit()
            return {"status": "ok"}
        else:
            return {"status": "Must Provide A Parameter"}

    elif method == "patch":
        item = ItemsModel.query.filter_by(id=args['id'], userId=userId, buildId=buildId).first()
        if item:
            if args['name'] or args['price'] or args['category'] or args['imageUrl'] or args['description'] and \
                    userId and args['buildId']:
                item.name = args['name']
                item.price = args['price']
                item.category = args['category']
                item.description = args['description']
                item.imageUrl = args['imageUrl']
                item.buildId = args['buildId']
                item.userId = userId
            else:
                return {"status": "Must Provide A Parameter"}
            db.session.commit()
        else:
            return {"status": "Invalid Item Id Specified !"}
        return {"status": "ok", 'item': item}


class Item(Resource):

    def __init__(self):
        self.args = itemArgs.parse_args()
    @marshal_with(item_fields)
    @jwt_required
    def get(self, buildID):
        user_public_id = get_jwt_identity()
        userId = getUserIdFromPublicId(user_public_id)
        validateBuildID(userId, buildID)
        result = validateArgs(self.args, buildID, userId, 'get')
        return result, 200

    @marshal_with(item_fields)
    @jwt_required
    def put(self, buildID):
        user_public_id = get_jwt_identity()
        userId = getUserIdFromPublicId(user_public_id)
        validateBuildID(userId, buildID)
        result = validateArgs(self.args, buildID, userId, 'put')
        if result['status'] != "ok":
            abort(400, message=result['status'])
        return result['item'], 201

    @marshal_with(item_fields)
    @jwt_required
    def patch(self, buildID):
        user_public_id = get_jwt_identity()
        userId = getUserIdFromPublicId(user_public_id)
        validateBuildID(userId, buildID)
        result = validateArgs(self.args, buildID, userId, 'patch')
        if result['status'] != 'ok':
            abort(400, message=result['status'])
        return result['item'], 201

    @jwt_required
    def delete(self, buildID):
        user_public_id = get_jwt_identity()
        userId = getUserIdFromPublicId(user_public_id)
        validateBuildID(userId, buildID)
        result = validateArgs(self.args, buildID, userId, 'delete')
        if result['status'] != "ok":
            abort(404, message=result['status'])
        return "Successfully Deleted", 200


# ********************************* Builds Section ************************


build_args = reqparse.RequestParser()
build_args.add_argument("id", type=int, required=False)
build_args.add_argument("name",type=str, required=False)
build_args.add_argument("description", type=str, required=False)
build_args.add_argument("totalValue", type=float, required=False)
build_args.add_argument("dateCreated", type=str, required=False)

# Fields for the Marshal to return from the database in dictionary form

build_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'description': fields.String,
    'totalValue': fields.Float,
    'dateCreated': fields.DateTime,
    'userId': fields.Integer,
    'items': fields.List(fields.Nested(item_fields))
}


# Checks if request is for all Builds or for one
def executeRequest(user_id, build_id, reqType):
    if not user_id:
        return {'status': None, 'message': 'User Id not Specified', 'status_code': 404}

    elif reqType == "put":
        return {'status': 'ok', 'status_code': 200}

    elif reqType == "get":
        if not build_id:  # if id is None returns all Builds
            builds = BuildsModel.query.filter_by(userId=user_id).all()
            return {'status': 'ok', 'message': builds, 'status_code': 200}
        else:  # returns the build for the particular id
            build = BuildsModel.query.filter_by(id=build_id, userId=user_id).first()
            return {'status': 'ok', 'message': build, 'status_code': 200}

    elif reqType == "delete":
        if id is None:  # if id is None return None
            return {'status': None, 'message': 'No Build Id was Specified', 'status_code': 404}
        else:
            build = BuildsModel.query.filter_by(userId=user_id, id=build_id).first()
            if not build:
                return {'status': None, 'message': 'Invalid Params Specified', 'status_code': 404}
            elif build:
                ItemsModel.query.filter_by(buildId=build.id, userId=user_id).delete()
                db.session.delete(build)
                db.session.commit()
                return {'status': 'ok', 'message': 'Build Successfully Deleted', 'status_code': 200}

    elif reqType == "patch":
        if build_id is None:  # if id is None return None
            return {'status': None, 'message': 'Build Id not Specified', 'status_code': 404}

        else:
            build = BuildsModel.query.filter_by(userId=user_id, id=build_id).first()
            if not build:
                return {'status': None, 'message': 'Invalid Build Id', 'status_code': 404}
            return {'status': 'ok', 'message': build, 'status_code': 200}


def applyPatch(args, build):
    if not args['name']:
        return {"status": None, 'message': 'The Name of the Build Cannot be Null', 'status_code': 404}
    else:
        if args['name'] or args['totalValue'] or args['dateCreated'] or args['description']:
            build.name = args['name']
            build.description = args['description']
            build.totalValue = args['totalValue']
            build.dateCreated = args['dateCreated']
            db.session.commit()
            return {"status": "ok", 'message': build, 'status_code': 200}
        else:
            return {"status": None, 'message': 'No Params were Specified', 'status_code': 404}





class Build(Resource):
    def __init__(self):
        super(Resource)
        self.args = build_args.parse_args()

    @marshal_with(build_fields)
    @jwt_required
    def get(self):
        user_public_id = get_jwt_identity()
        userId = getUserIdFromPublicId(user_public_id)
        result = executeRequest(userId, self.args['id'], 'get')
        return result['message'], result['status_code']

    @marshal_with(build_fields)
    @jwt_required
    def put(self):
        user_public_id = get_jwt_identity()
        userId = getUserIdFromPublicId(user_public_id)
        result = executeRequest(userId, "", 'put')
        if not result['status']:
            return result['message'], result['status_code']
        build = BuildsModel(name=self.args['name'], totalValue=self.args['totalValue'],
                            dateCreated=self.args['dateCreated'], userId=userId)
        db.session.add(build)
        db.session.commit()
        return build, 201

    @marshal_with(build_fields)
    @jwt_required
    def patch(self):
        user_public_id = get_jwt_identity()
        userId = getUserIdFromPublicId(user_public_id)
        result = executeRequest(userId, self.args['id'], 'patch')
        if not result['status']:
            abort(result['status_code'], message=result['message'])
        patchresult = applyPatch(self.args, result['message'])
        if not patchresult['status']:
            abort(patchresult['status_code'], message=patchresult['message'])
        else:
            return patchresult['message'], 200

    @jwt_required
    def delete(self):
        user_public_id = get_jwt_identity()
        userId = getUserIdFromPublicId(user_public_id)
        result = executeRequest(userId, self.args['id'], 'delete')

        if not result['status']:
            abort(result['status_code'], message=result['message'])

        elif result['status'] == 'ok':
            return result['message'], result['status_code']


# ********************************* Login Section ************************


UserLogin_args = reqparse.RequestParser()
UserLogin_args.add_argument('email', type=str, location='form', help="Must contain an Email", required=True)
UserLogin_args.add_argument('password', type=str, location='form', help="Must contain a Password", required=True)

# Fields for the Marshal to return from the database in dictionary form
user_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'email': fields.String,
    'createdOn': fields.DateTime,
    'modifiedOn': fields.DateTime,
    'builds': fields.List(fields.Nested(build_fields)),
    'isAdmin': fields.Boolean,
    'lastOnline': fields.DateTime,
}


class UserLogin(Resource):

    def __init__(self):
        super(Resource)
        self.args = UserLogin_args.parse_args()
        print(self.args)

    def post(self):
        result = UsersModel.userLogin(self.args['email'], self.args['password'])
        if not result['status']:
            abort(result['status_code'], message=result['message'])

        resp = jsonify({'login': True})
        set_refresh_cookies(resp, result['tokens']['refresh_token'])
        set_access_cookies(resp, result['tokens']['access_token'])
        return resp
        #return jsonify({"token": token.decode("UTF-8")})

class UserLogout(Resource):

    def delete(self):
        resp = jsonify({'logout': True})
        unset_jwt_cookies(resp)
        return resp



UserRegister_args = reqparse.RequestParser()
UserRegister_args.add_argument('name', type=str, location='form', help="Must contain an UserName", required=True)
UserRegister_args.add_argument('email', type=str, location='form', help="Must contain an Email", required=True)
UserRegister_args.add_argument('password', type=str, location='form', help="Must contain a Password", required=True)


class UserRegister(Resource):
    def __init__(self):
        super(Resource)
        self.args = UserRegister_args.parse_args()

    def post(self):
        result = UsersModel.userRegister(self.args['name'], self.args['email'], self.args['password'])
        if not result['status']:
            return result['message'], 404
        return "Account Created Successfully!", 200


class RefreshAccessToken(Resource):

    @jwt_refresh_token_required
    def get(self):
        current_user = get_jwt_identity()
        print(current_user)
        if not current_user:
            return abort(401, message="Invalid Refresh Token")

        resp = jsonify({'Refreshed': True})
        new_access_token = create_access_token(identity=current_user)
        set_access_cookies(resp, new_access_token)
        print(current_user)
        return resp
