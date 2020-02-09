def return_group_exception(e):
    print("contains ? ", str(e).__contains__('Resource Not Found: groupKey'))
    if str(e).__contains__('Resource Not Found: groupKey'):
        return {
            "message": "group don't exist",
            "error_code" : 404
        }, 404


def return_create_group_exception(e):
    return {
               "message": "group already exist",
               "error_code": 409
           }, 409
