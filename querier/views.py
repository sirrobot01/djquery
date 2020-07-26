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
    data = []
    err = ""
    loop = 0
    try:
        cls = [''.join(('class', i)) for i in re.split(r"\bclass", code) if i][0]
        get_name = re.compile('class\s(\w+)')
        cls_name = get_name.match(cls).group(1)

        cls_data = [i.lstrip() for i in cls.split('\n') if i.lstrip() != '' if 'class' not in i]
        for i in range(1, 11):
            row = [i]
            for dt in cls_data:
                column = re.match(r'(\w+)\s*=\s*models.(\w+)', dt)
                if column:
                    field_type = column.group(2)
                    if field_type == "CharField":
                        row.append(f'{column.group(1)}{i}{loop}')
                    elif field_type == "IntegerField":
                        row.append(f'{random.randint(0, 30)}')
                    else:
                        row.append(f'{column.group(1)}{i}{loop}')

            loop += 1
            data.append(row)
        for dt in cls_data:
            column = re.match(r'(\w+)\s*=\s*models.(\w+)', dt)
            column_ls.append(column.group(1))
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
    queries = []
    new_data = []

    cls_name = request.GET.get("className")


    success = False
    try:
        if data and column:
            err = ""
            data = json.loads(data)
            column = json.loads(column)

            dt_regex = regex.match(qr)
            if dt_regex.group(1) != cls_name:
                err = f"Class name should be {cls_name}, you wrote {dt_regex.group(1)}"
            else:
                if dt_regex and len(dt_regex.groups()) == 3:
                    query_type = dt_regex.group(2)

                    if query_type == "all":
                        success = True
                    elif query_type == "none":
                        success = True
                    else:
                        keys = re.split(',', re.sub('[()]', '', dt_regex.group(3).strip('(').strip(')')))
                        for key in keys:
                            key_column = key.split("=")[0].strip()
                            key_query = key.split("=")[1].strip().strip('"').strip("'")
                            if key_column not in column:
                                err = f'Invalid query: {key.split("=")[0].strip()} is not a column'
                            elif key_column != 'pk':
                                queries.append(key_query)
                            else:
                                key_query = int(key_query)
                                for d in data:
                                    if d[0] == key_query:
                                        new_data.append(d)
                        if queries:
                            if query_type == 'exclude':
                                for d in data:
                                    if not all(x in d for x in queries):
                                        new_data.append(d)
                            else:
                                for d in data:
                                    if all(x in d for x in queries):
                                        new_data.append(d)
                        if new_data:
                            if query_type == 'get':
                                if len(new_data) > 1:
                                    err = f"Get query can only return one query object, This returned {len(new_data[0])}"
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
        err = f'An error occurred: {e}'

    return JsonResponse({'success': success, "err": err, "data": new_data, "column": column})
