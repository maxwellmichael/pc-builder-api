from flask import jsonify
from flask_restful import Resource, reqparse, abort, fields, marshal_with
from app.models import BuildsModel, ItemsModel
from app import db
from flask_cors import cross_origin


builds = [
    {
        "build_name": "Budget Build",
        "items": [
            {
                "name": "ASRock B450M Steel Legend",
                "price": 9390.00,
                "category": "Motherboard",
                "image_url": "https://images-na.ssl-images-amazon.com/images/I/71LIALdCw%2BL._SX355_.jpg",
                "description": ""
            },
            {
                "name": "AMD Ryzen 3 3100",
                "price": 9396.00,
                "category": "CPU",
                "description": "",
                "image_url": "https://www.amd.com/system/files/2020-04/450000-ryzen3-3rd-gen-pib-1260x709_0.png"
            },
            {
                "name": "Zotac Gaming GeForce GTX 1650 Super Twin Fan",
                "price": 15999.00,
                "category": "Graphics Card",
                "description": "",
                "image_url": "https://www.zotac.com/download/files/styles/w1024/public/product_gallery/graphics_cards/zt-t16510f-10l-image1.jpg?itok=PlQL7iZk"
            },
            {
                "name": "Corsair Vengeance LPX 8GB (1x8GB) DDR4 3200MHZ C16",
                "price": 3250.00,
                "category": "Ram Module",
                "description": "",
                "image_url": "https://www.pcstudio.in/wp-content/uploads/2019/11/CORSAIR-VENGEANCE-LPX-8GB-1x8GB-DDR4-3200MHZ-C16-DESKTOP-RAM-BLACK-4.jpg"
            },
            {
                "name": "Cooler Master MWE 550W,80+",
                "price": 4397.00,
                "category": "Power Supply",
                "description": "",
                "image_url": "https://s3-eu-west-1.amazonaws.com/cdn.coolermaster.com/assets/1064/04111_27-image.png"
            }
        ]

    },

    {
        "build_name": "Premium Build",
        "items": [
            {
                "name": "ASRock B450M Steel Legend",
                "price": 9390.00,
                "category": "Motherboard",
                "image_url": "https://images-na.ssl-images-amazon.com/images/I/71LIALdCw%2BL._SX355_.jpg",
                "description": ""
            },
            {
                "name": "AMD Ryzen 3 3100",
                "price": 9396.00,
                "category": "CPU",
                "description": "",
                "image_url": "https://www.amd.com/system/files/2020-04/450000-ryzen3-3rd-gen-pib-1260x709_0.png"
            },
            {
                "name": "Zotac Gaming GeForce GTX 1650 Super Twin Fan",
                "price": 15999.00,
                "category": "Graphics Card",
                "description": "",
                "image_url": "https://www.zotac.com/download/files/styles/w1024/public/product_gallery/graphics_cards/zt-t16510f-10l-image1.jpg?itok=PlQL7iZk"
            },
            {
                "name": "Corsair Vengeance LPX 8GB (1x8GB) DDR4 3200MHZ C16",
                "price": 3250.00,
                "category": "Ram Module",
                "description": "",
                "image_url": "https://www.pcstudio.in/wp-content/uploads/2019/11/CORSAIR-VENGEANCE-LPX-8GB-1x8GB-DDR4-3200MHZ-C16-DESKTOP-RAM-BLACK-4.jpg"
            },
            {
                "name": "Cooler Master MWE 550W,80+",
                "price": 4397.00,
                "category": "Power Supply",
                "description": "",
                "image_url": "https://s3-eu-west-1.amazonaws.com/cdn.coolermaster.com/assets/1064/04111_27-image.png"
            }
        ]

    }
]

build_args = reqparse.RequestParser()
build_args.add_argument("id", type=int, help="ID of Build Required", required=False)
build_args.add_argument("name", type=str, required=False)
build_args.add_argument("totalValue", type=float, required=False)
build_args.add_argument("dateCreated", type=str, required=False)

item_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'price': fields.Float,
    'category': fields.String,
    'description': fields.String,
    'imageUrl': fields.String,
    'buildId': fields.Integer
}

build_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'totalValue': fields.Float,
    'dateCreated': fields.DateTime,
    'items': fields.List(fields.Nested(item_fields))
}


# Checks if request is for all Builds or for one
def validateId(id, reqType):
    if reqType == "get":
        if id is None:  # if id is None returns all Builds
            return BuildsModel.query.all()
        else:  # returns the build for the particular id
            return BuildsModel.query.filter_by(id=id).first()

    elif reqType == "delete":
        if id is None:  # if id is None return None
            return {'status': None}
        else:
            build = BuildsModel.query.filter_by(id=id).first()
            if not build:
                return {'status': 'invalid'}
            elif build:
                ItemsModel.query.filter_by(buildId=build.id).delete()
                db.session.delete(build)
                db.session.commit()
                return {'status': 'ok'}

    elif reqType == "patch":
        if id is None:  # if id is None return None
            abort(400, message="No Id was Provided")
        else:
            build = BuildsModel.query.filter_by(id=id).first()
            if not build:
                abort(400, message="The Provided Id is Invalid")


def applyPatch(args):
    build = BuildsModel.query.filter_by(id=args['id']).first()
    if args['name'] or args['totalValue'] or args['dateCreated']:
        build.name = args['name']
        build.totalValue = args['totalValue']
        build.dateCreated = args['dateCreated']
    else:
        return {"status": "No Params were Specified"}
    db.session.commit()
    return {"status": "ok", 'build': build}


class Build(Resource):
    def __init__(self):
        super(Resource)
        self.args = build_args.parse_args()

    @marshal_with(build_fields)
    def get(self):
        result = validateId(self.args['id'], 'get')
        return result, 200

    @marshal_with(build_fields)
    def put(self):
        build = BuildsModel(name=self.args['name'], totalValue=self.args['totalValue'],
                            dateCreated=self.args['dateCreated'])
        db.session.add(build)
        db.session.commit()
        return build, 201

    @marshal_with(build_fields)
    def patch(self):
        validateId(self.args['id'], 'patch')
        result = applyPatch(self.args)
        if result['status'] != 'ok':
            abort(400, message=result['status'])
        return result['build'], 201

    def delete(self):
        result = validateId(self.args['id'], 'delete')

        if result['status'] is None:
            abort(400, message="No ID was Specified")

        elif result['status'] == 'invalid':
            abort(404, message="The id Specified Doesn't Exist")

        elif result['status'] == 'ok':
            return 'Sucessfully Deleted', 200


itemArgs = reqparse.RequestParser()
itemArgs.add_argument("id", type=int)
itemArgs.add_argument("name", type=str)
itemArgs.add_argument("price", type=float)
itemArgs.add_argument("category", type=str)
itemArgs.add_argument("description", type=str)
itemArgs.add_argument("imageUrl", type=str)
itemArgs.add_argument("buildId", type=str)


def validateBuildID(id):
    if not id:
        abort(404, message="Must Specify a Build ID")
    else:
        build = BuildsModel.query.filter_by(id=id).first()

        if not build:
            abort(301, message="Must Specify a Valid ID")


def validateArgs(args, id, method):
    if method == "get":
        if args['name']:
            item = ItemsModel.query.filter_by(name=args['name'], buildId=id).first()
            return item
        elif args['id']:
            item = ItemsModel.query.filter_by(id=args['id'], buildId=id).all()
            return item
        elif args['category']:
            item = ItemsModel.query.filter_by(category=args['category'], buildId=id).all()
            return item
        elif args['price']:
            item = ItemsModel.query.filter_by(price=args['price'], buildId=id).all()
            return item
        else:
            item = ItemsModel.query.filter_by(buildId=id).all()
            return item

    elif method == 'put':
        if not args['name'] or not args['category'] or not args['price']:
            return {"status": "Not all Params Specified"}
        else:
            item = ItemsModel(name=args['name'], category=args['category'], price=args['price'],
                              description=args['description'], imageUrl=args['imageUrl'], buildId=id)
            db.session.add(item)
            db.session.commit()
            return {"status": "ok", 'item': item}

    elif method == 'delete':
        if args['id']:
            item = ItemsModel.query.filter_by(id=args['id'], buildId=id).first()
            db.session.delete(item)
            db.session.commit()
            return {"status": "ok"}

        elif args['name']:
            item = ItemsModel.query.filter_by(name=args['name'], buildId=id).first()
            db.session.delete(item)
            db.session.commit()
            return {"status": "ok"}

        elif args['category']:
            item = ItemsModel.query.filter_by(category=args['category'], buildId=id).first()
            db.session.delete(item)
            db.session.commit()
            return {"status": "ok"}

        elif args['price']:
            item = ItemsModel.query.filter_by(price=args['price'], buildId=id).first()
            db.session.delete(item)
            db.session.commit()
            return {"status": "ok"}
        else:
            return {"status": "Must Provide A Parameter"}

    elif method == "patch":
        item = ItemsModel.query.filter_by(id=args['id'], buildId=id).first()
        if item:
            if args['name'] or args['price'] or args['category'] or args['imageUrl'] or args['description'] and args['buildId']:
                item.name = args['name']
                item.price = args['price']
                item.category = args['category']
                item.description = args['description']
                item.imageUrl = args['imageUrl']
                item.buildId = args['buildId']
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
    def get(self, buildID):
        validateBuildID(buildID)
        result = validateArgs(self.args, buildID, 'get')
        return result, 200

    @marshal_with(item_fields)
    def put(self, buildID):
        validateBuildID(buildID)
        result = validateArgs(self.args, buildID, 'put')
        if result['status'] != "ok":
            abort(400, message=result['status'])
        return result['item'], 201

    @marshal_with(item_fields)
    def patch(self, buildID):
        validateBuildID(buildID)
        result = validateArgs(self.args, buildID, 'patch')
        if result['status'] != 'ok':
            abort(400, message=result['status'])
        return result['item'], 201


    def delete(self, buildID):
        validateBuildID(buildID)
        result = validateArgs(self.args, buildID, 'delete')
        if result['status'] != "ok":
            abort(404, message=result['status'])
        return "Succesfully Deleted", 200
