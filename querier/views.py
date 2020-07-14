import json
import random
import re

from django.http import JsonResponse
from django.shortcuts import render


# Create your views here.


def index(request):
    return render(request, 'index.html')


def validate(request):
    code = request.GET.get("code")
    context = {}
    is_valid = False
    column_ls = ['pk', ]
    data = [[i for i in range(1, 11)]]
    err = ""
    loop = 0
    try:
        cls = [''.join(('class', i)) for i in re.split(r"\bclass", code) if i][0]
        get_name = re.compile('class\s(\w+)')
        cls_name = get_name.match(cls).group(1)

        cls_data = [i.lstrip() for i in cls.split('\n') if i.lstrip() != '' if 'class' not in i]
        for dt in cls_data:
            column = re.match(r'(\w+)\s*=\s*models.(\w+)', dt)
            if column:
                field_type = column.group(2)
                if field_type == "CharField":
                    data.append(['{}{}{}'.format(column.group(1), i, loop) for i in range(0, 4)] * 5)
                elif field_type == "IntegerField":
                    data.append(random.sample(range(0, 100), 5) * 5)
                else:
                    data.append(['{}{}{}'.format(column.group(1), i, loop) for i in range(0, 4)] * 5)
                column_ls.append(column.group(1))
                loop += 1
        if len(data) > 1:
            is_valid = True
        context.update(
            {'success': True, 'is_valid': is_valid, 'data': data, 'column': column_ls, 'className': cls_name})
        return JsonResponse(context)
    except Exception as e:
        err = 'Cannot validate the code <a href="#sample">Check sample</a>'
        return JsonResponse({'success': False, 'err': err, 'is_valid': is_valid})


def query(request):
    regex = re.compile(r'(\w+).objects.(\w+)(.+)')
    qr = request.GET.get("query")
    data = request.GET.get("data")
    column = request.GET.get("columns")
    err = ""

    cls_name = request.GET.get("className")

    new_data = []

    success = False
    try:
        if data and column:
            err = ""
            data = json.loads(data)
            column = json.loads(column)
            dt_regex = regex.match(qr)
            if dt_regex.group(1) != cls_name:
                err = "Class name should be {}, you wrote {}".format(cls_name, dt_regex.group(1))

            else:
                if dt_regex and len(dt_regex.groups()) == 3:
                    query_type = dt_regex.group(2)

                    if query_type == "all":
                        new_data = data
                        success = True
                    elif query_type == "none":
                        success = True
                    else:
                        keys = re.split(',', re.sub('[()]', '', dt_regex.group(3).strip('(').strip(')')))

                        for key in keys:
                            key_column = key.split("=")[0].strip()
                            key_query = key.split("=")[1].strip().strip('"').strip("'")

                            if key_column == "pk":
                                key_query = int(key_query)
                            if key_column not in column:
                                err = "Invalid query: {} is not a column".format(key.split("=")[0].strip())
                            else:
                                to_query = list(data[list(column).index(key_column)])
                                result = [to_query.index(x) for x in to_query if x == key_query]
                                for i in range(len(column)):
                                    dt_column = []
                                    for rs in result:
                                        dt_column.append(data[i][rs])
                                    new_data.append(dt_column)
                        if new_data:
                            if query_type == 'get':
                                if len(new_data[0]) > 1:
                                    err = "Get query can only return one query object, This returned {}".format(
                                        len(new_data[0]))
                                    success = False
                                else:
                                    success = True
                            else:
                                success = True
                        else:
                            success = False
        else:
            new_data = []
    except Exception as e:
        success = False
        err = 'An error occurred: {}'.format(e)

    return JsonResponse({'success': success, "err": err, "data": new_data, "column": column})
