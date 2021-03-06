from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
import json

from .models import *
from dj_data.models import *


# Create your views here.
brand = 'DONGJIN VIETNAM J.S.C'


def calc_delta(delta_second, shift_3rd, begin_time, end_time):
    begin_time = datetime.fromtimestamp(begin_time)
    end_time = datetime.fromtimestamp(end_time)
    if shift_3rd == 1:
        shift_1 = datetime(
            end_time.year, end_time.month, end_time.day, 10, 00, 0)
        shift_2 = datetime(
            end_time.year, end_time.month, end_time.day, 18, 00, 0)
        tomorrow = end_time + timedelta(days=1)
        shift_3 = datetime(
            tomorrow.year, tomorrow.month, tomorrow.day, 2, 00, 0
        )

        if begin_time < shift_1:
            if end_time > shift_1:
                delta_second = delta_second - 1800
        if begin_time < shift_2:
            if end_time > shift_2:
                delta_second = delta_second - 1800
        if begin_time < shift_3:
            if end_time > shift_3:
                delta_second = delta_second - 2700

    else:
        shift_1 = datetime(
            end_time.year, end_time.month, end_time.day, 10, 00, 0)
        shift_2 = datetime(
            end_time.year, end_time.month, end_time.day, 14, 00, 0)
        shift_3 = datetime(
            end_time.year, end_time.month, end_time.day, 22, 00, 0)
        tomorrow = end_time + timedelta(days=1)
        shift_4 = datetime(
            tomorrow.year, tomorrow.month, tomorrow.day, 2, 00, 0
        )

        if begin_time < shift_1:
            if end_time > shift_1:
                delta_second = delta_second - 1800
        if begin_time < shift_2:
            if end_time > shift_2:
                delta_second = delta_second - 1800
        if begin_time < shift_3:
            if end_time > shift_3:
                delta_second = delta_second - 1800
        if begin_time < shift_4:
            if end_time > shift_4:
                delta_second = delta_second - 2700

    return delta_second


def get_arr_group_model(today_plan):
    arr = []
    if today_plan:
        # Get today processes in model
        selected_group = DJProcess.objects.filter(model__description=today_plan.model,
                                                department__name=today_plan.department)
        day = datetime.fromtimestamp(today_plan.timestamp).strftime(
            '%Y-%m-%d')
        for process in selected_group:  # Loop through all models in group
            write_obj = WriteData.objects.filter(date=day, department__name=today_plan.department,
                                                 line__name=today_plan.line, process=process)
            if write_obj:
                last_line = write_obj.last()
                first_line = (WriteData.objects.filter(date=last_line.date, department__name=last_line.department,
                                                       line__name=last_line.line, process__name=last_line.process.name,
                                                       version=last_line.version, qty_plan=last_line.qty_plan)).first()
                previous_line = last_line
                if len(write_obj) > 1:  # If found > 1 element in write object
                    # Reverse object, get previous line of last line
                    previous_line = write_obj.order_by('-id')[1]

                if last_line.qty_actual != 0:
                    # Calculator fields
                    start_time = datetime.fromtimestamp(
                        first_line.timestamps).strftime('%H:%M:%S')
                    end_time = datetime.fromtimestamp(
                        last_line.timestamps).strftime('%H:%M:%S')

                    per_finish = last_line.qty_actual / last_line.qty_plan * 100
                    delta_second = last_line.timestamps - first_line.timestamps

                    if last_line.qty_actual == previous_line.qty_actual:  # If qty_actual not change
                        before_actual = (WriteData.objects.filter(qty_actual=last_line.qty_actual, date=last_line.date,
                                                                  department__name=last_line.department, line__name=last_line.line,
                                                                  process__name=last_line.process.name, version=last_line.version,
                                                                  qty_plan=last_line.qty_plan)).first()
                        # End time and delta second just change when qty_actual change
                        end_time = datetime.fromtimestamp(
                            before_actual.timestamps).strftime('%H:%M:%S')
                        delta_second = before_actual.timestamps - first_line.timestamps

                    # Calculate time of shift work
                    delta_second = calc_delta(delta_second, last_line.shift_work,
                                              first_line.timestamps, last_line.timestamps)

                    st_actual = (delta_second + process.st) / \
                        last_line.qty_actual
                    data = {
                        'start': last_line.start,
                        'qty_actual': last_line.qty_actual,
                        'timestamps': last_line.timestamps,
                        'machine': last_line.machine,
                        'material': last_line.material,
                        'quality': last_line.quality,
                        'other': last_line.other,
                        'date': last_line.date,
                        'version': last_line.version,
                        'shift_work': last_line.shift_work,
                        'department': last_line.department.name,
                        'line': last_line.line.name,
                        'model_name': process.model.description,
                        'process_name': process.description,
                        'st_plan': f"{process.st:.2f}",
                        'qty_plan': last_line.qty_plan,

                        'start_time': start_time,
                        'end_time': end_time,
                        'st_actual': f"{st_actual:.2f}",
                        'per_finish': f"{per_finish:.2f}",
                    }
                else:
                    data = {
                        'start': False,
                        'qty_actual': 0,
                        'timestamps': last_line.timestamps,
                        'machine': True,
                        'material': True,
                        'quality': True,
                        'other': True,
                        'date': last_line.date,
                        'version': last_line.version,
                        'shift_work': last_line.shift_work,
                        'department': last_line.department.name,
                        'line': last_line.line.name,
                        'model_name': process.model.description,
                        'process_name': process.description,
                        'st_plan': '0.00',
                        'qty_plan': 0,

                        'start_time': '00:00:00',
                        'end_time': '00:00:00',
                        'st_actual': '0.00',
                        'per_finish': '0.00',
                    }
                arr.append(data)

    return arr


def get_arr_plan(today_plan):
    arr = []
    if today_plan:
        # Get today processes in model
        selected_group = DJProcess.objects.filter(model__description=today_plan.model,
                                                department__name=today_plan.department)

        for i in range(0, len(selected_group)):
            data = {
                'Start': 0,
                'Q\'ty Actual': 0,
                'Timestamp': today_plan.timestamp,
                'Machine': 1,
                'Material': 1,
                'Quality': 1,
                'Other': 1,
                'Date': today_plan.date,
                'Time': today_plan.time,
                'Department Name': today_plan.department,
                'Department': selected_group[i].department.id,
                'Line Name': today_plan.line,
                'Line': Line.objects.get(name=today_plan.line).id,
                'Process Name': selected_group[i].description,
                'Process ID': selected_group[i].id,
                'Count Model In Group': len(selected_group),
                'Model Name': selected_group[i].model.description,
                'Model ID': selected_group[i].model.id,
                'Version': today_plan.version,
                'Shift Work': 1 if today_plan.shift_work else 0,
                'Q\'ty Plan': today_plan.qty_plan,
                'Finish %': 0,
                'ST Plan': 0,
                'ST Actual': 0,
            }
            arr.append(data)
    return arr


def get_arr_history(selected_plan):
    arr = []
    if selected_plan:
        # Get all plan of selected date
        for plan in selected_plan:
            # Get all model in group model of this plan
            selected_group = DJProcess.objects.filter(model__description=plan.model,
                                                    department__name=plan.department)

            day = datetime.fromtimestamp(plan.timestamp).strftime(
                '%Y-%m-%d')
            # Calculate for all model in selected group
            for process in selected_group:
                write_obj = WriteData.objects.filter(date=day, department__name=plan.department,
                                                     line__name=plan.line, process=process,
                                                     qty_plan=plan.qty_plan, version=plan.version)
                if write_obj:
                    last_line = write_obj.last()
                    first_line = write_obj.first()
                    # Calculate fields
                    start_time = datetime.fromtimestamp(
                        first_line.timestamps).strftime('%H:%M:%S')
                    end_time = datetime.fromtimestamp(
                        last_line.timestamps).strftime('%H:%M:%S')
                    per_finish = last_line.qty_actual / last_line.qty_plan * 100

                    delta_second = last_line.timestamps - first_line.timestamps
                    # Calculate time of shift work
                    delta_second = calc_delta(delta_second, last_line.shift_work,
                                              first_line.timestamps, last_line.timestamps)

                    st_actual = 0
                    if last_line.qty_actual != 0:
                        st_actual = (delta_second + process.st) / \
                            last_line.qty_actual
                        data = {
                            'start': last_line.start,
                            'qty_actual': last_line.qty_actual,
                            'timestamps': last_line.timestamps,
                            'machine': last_line.machine,
                            'material': last_line.material,
                            'quality': last_line.quality,
                            'other': last_line.other,
                            'date': last_line.date,
                            'version': last_line.version,
                            'shift_work': last_line.shift_work,
                            'department': last_line.department.name,
                            'line': last_line.line.name,
                            'model_name': process.model.description,
                            'process_name': process.description,
                            'st_plan': f"{process.st:.2f}",
                            'qty_plan': last_line.qty_plan,

                            'start_time': start_time,
                            'end_time': end_time,
                            'st_actual': f"{st_actual:.2f}",
                            'per_finish': f"{per_finish:.2f}",
                        }
                    else:
                        data = {
                            'start': False,
                            'qty_actual': 0,
                            'timestamps': last_line.timestamps,
                            'machine': True,
                            'material': True,
                            'quality': True,
                            'other': True,
                            'date': last_line.date,
                            'version': last_line.version,
                            'shift_work': last_line.shift_work,
                            'department': last_line.department.name,
                            'line': last_line.line.name,
                            'model_name': process.model.description,
                            'process_name': process.description,
                            'st_plan': '0.00',
                            'qty_plan': 0,

                            'start_time': '00:00:00',
                            'end_time': '00:00:00',
                            'st_actual': '0.00',
                            'per_finish': '0.00',
                        }
                    arr.append(data)
    return arr


def get_arr_last_model(plan):  # Get latest data (calculate st with previous st)
    arr = []
    if plan:
        # Get all model in group model of this plan
        selected_group = DJProcess.objects.filter(model__description=plan.model,
                                                department__name=plan.department)
        day = datetime.fromtimestamp(plan.timestamp).strftime(
            '%Y-%m-%d')
        # Calculate for all model in selected group
        for process in selected_group:
            write_obj = WriteData.objects.filter(date=day, department__name=plan.department,
                                                 line__name=plan.line, process=process,
                                                 qty_plan=plan.qty_plan, version=plan.version)
            if write_obj:
                last_line = write_obj.last()
                latest_obj = LatestData.objects.filter(date=last_line.date, department=last_line.department,
                                                       line=last_line.line, process=last_line.process,
                                                       qty_plan=last_line.qty_plan, version=last_line.version).last()
                data = []
                if latest_obj:
                    st_actual_previous = '0.00'
                    st_actual = '0.00'
                    
                    # Find data
                    previous_line = last_line
                    if len(write_obj) > 1:  # If found > 1 element in write object
                        # Get previous qty_actual
                        current_line = (WriteData.objects.filter(qty_actual=last_line.qty_actual, date=last_line.date,
                                                                 department__name=last_line.department, line__name=last_line.line,
                                                                 process__name=last_line.process.name, version=last_line.version,
                                                                 qty_plan=last_line.qty_plan)).first()
                        _previous_line = (WriteData.objects.filter(qty_actual=current_line.qty_actual - 1, date=current_line.date,
                                                                   department__name=current_line.department, line__name=current_line.line,
                                                                   process__name=current_line.process.name, version=current_line.version,
                                                                   qty_plan=current_line.qty_plan)).first()
                        if _previous_line:
                            previous_line = _previous_line

                    if last_line.qty_actual != 0:
                        # Calculate fields
                        start_time = datetime.fromtimestamp(
                            previous_line.timestamps).strftime('%H:%M:%S')
                        end_time = datetime.fromtimestamp(
                            current_line.timestamps).strftime('%H:%M:%S')

                        per_finish = current_line.qty_actual / current_line.qty_plan * 100

                        delta_second = current_line.timestamps - previous_line.timestamps
                        # Calculate time of shift work
                        delta_second = calc_delta(delta_second, current_line.shift_work,
                                                  previous_line.timestamps, current_line.timestamps)

                        # Get previous st
                        st_actual_previous = f"{delta_second:.2f}"

                        # Check database change(if old data => not save / if new data => save)
                        if latest_obj.qty_actual != last_line.qty_actual or latest_obj.start != last_line.start \
                                or latest_obj.machine != last_line.machine or latest_obj.material != last_line.material \
                                or latest_obj.quality != last_line.quality or latest_obj.other != last_line.other:

                            new_data = LatestData(start=last_line.start, qty_actual=last_line.qty_actual, timestamps=last_line.timestamps,
                                                machine=last_line.machine, material=last_line.material, quality=last_line.quality,
                                                other=last_line.other, date=last_line.date, version=last_line.version,
                                                shift_work=last_line.shift_work, qty_plan=last_line.qty_plan, department=last_line.department,
                                                line=last_line.line, process=last_line.process)
                            new_data.save()

                            # If data change => update st_actual
                            if latest_obj.qty_actual != last_line.qty_actual:
                                st_actual = f"{delta_second:.2f}"

                        data = {
                            'start': last_line.start,
                            'qty_actual': last_line.qty_actual,
                            'timestamps': last_line.timestamps,
                            'machine': last_line.machine,
                            'material': last_line.material,
                            'quality': last_line.quality,
                            'other': last_line.other,
                            'date': last_line.date,
                            'version': last_line.version,
                            'shift_work': last_line.shift_work,
                            'department': last_line.department.name,
                            'line': last_line.line.name,
                            'count_process_in_model': len(selected_group),
                            'model_name': process.model.description,
                            'process_name': process.description,
                            'process_order': process.order,
                            'st_plan': f"{process.st:.2f}",
                            'qty_plan': last_line.qty_plan,

                            'start_time': start_time,
                            'end_time': end_time,
                            'st_actual': st_actual,
                            'st_actual_previous': st_actual_previous,
                            'per_finish': f"{per_finish:.2f}",
                        }
                    else:
                        data = {
                            'start': False,
                            'qty_actual': 0,
                            'timestamps': last_line.timestamps,
                            'machine': True,
                            'material': True,
                            'quality': True,
                            'other': True,
                            'date': last_line.date,
                            'version': last_line.version,
                            'shift_work': last_line.shift_work,
                            'department': last_line.department.name,
                            'line': last_line.line.name,
                            'count_process_in_model': len(selected_group),
                            'model_name': process.model.description,
                            'process_name': process.description,
                            'process_order': process.order,
                            'st_plan': '0.00',
                            'qty_plan': 0,

                            'start_time': '00:00:00',
                            'end_time': '00:00:00',
                            'st_actual': '0.00',
                            'st_actual_previous': st_actual_previous,
                            'per_finish': '0.00',
                        }

                else:
                    new_data = LatestData(start=last_line.start, qty_actual=last_line.qty_actual, timestamps=last_line.timestamps,
                                          machine=last_line.machine, material=last_line.material, quality=last_line.quality,
                                          other=last_line.other, date=last_line.date, version=last_line.version,
                                          shift_work=last_line.shift_work, qty_plan=last_line.qty_plan, department=last_line.department,
                                          line=last_line.line, process=last_line.process)
                    new_data.save()

                arr.append(data)
    return arr


def home(request):
    title = 'View'
    # now_datetime = timezone.now().strftime(
    #     '%Y-%m-%d 00:00:00.000000+00:00')
    my_date = datetime.fromtimestamp(
        datetime.timestamp(timezone.now())).strftime('%Y-%m-%d')

    # Get plan of all line in current date
    today_plan_arm_a = Planning.objects.filter(
        date=my_date, department='ARM', line='A').last()
    today_plan_arm_b = Planning.objects.filter(
        date=my_date, department='ARM', line='B').last()
    today_plan_arm_c = Planning.objects.filter(
        date=my_date, department='ARM', line='C').last()
    today_plan_arm_d = Planning.objects.filter(
        date=my_date, department='ARM', line='D').last()
    today_plan_arm_e = Planning.objects.filter(
        date=my_date, department='ARM', line='E').last()
    today_plan_arm_f = Planning.objects.filter(
        date=my_date, department='ARM', line='F').last()
    today_plan_arm_j = Planning.objects.filter(
        date=my_date, department='ARM', line='J').last()

    today_plan_ass_a = Planning.objects.filter(
        date=my_date, department='ASS', line='A').last()
    today_plan_ass_b = Planning.objects.filter(
        date=my_date, department='ASS', line='B').last()
    today_plan_ass_c = Planning.objects.filter(
        date=my_date, department='ASS', line='C').last()
    today_plan_ass_d = Planning.objects.filter(
        date=my_date, department='ASS', line='D').last()
    today_plan_ass_e = Planning.objects.filter(
        date=my_date, department='ASS', line='E').last()
    today_plan_ass_f = Planning.objects.filter(
        date=my_date, department='ASS', line='F').last()
    today_plan_ass_j = Planning.objects.filter(
        date=my_date, department='ASS', line='J').last()

    # ARM
    arr_arm_a = get_arr_group_model(today_plan_arm_a)
    arr_arm_b = get_arr_group_model(today_plan_arm_b)
    arr_arm_c = get_arr_group_model(today_plan_arm_c)
    arr_arm_d = get_arr_group_model(today_plan_arm_d)
    arr_arm_e = get_arr_group_model(today_plan_arm_e)
    arr_arm_f = get_arr_group_model(today_plan_arm_f)
    arr_arm_j = get_arr_group_model(today_plan_arm_j)

    # ASS
    arr_ass_a = get_arr_group_model(today_plan_ass_a)
    arr_ass_b = get_arr_group_model(today_plan_ass_b)
    arr_ass_c = get_arr_group_model(today_plan_ass_c)
    arr_ass_d = get_arr_group_model(today_plan_ass_d)
    arr_ass_e = get_arr_group_model(today_plan_ass_e)
    arr_ass_f = get_arr_group_model(today_plan_ass_f)
    arr_ass_j = get_arr_group_model(today_plan_ass_j)

    dict_arm_a = dict(zip([z for z in range(0, len(arr_arm_a))], arr_arm_a))
    dict_arm_b = dict(zip([z for z in range(0, len(arr_arm_b))], arr_arm_b))
    dict_arm_c = dict(zip([z for z in range(0, len(arr_arm_c))], arr_arm_c))
    dict_arm_d = dict(zip([z for z in range(0, len(arr_arm_d))], arr_arm_d))
    dict_arm_e = dict(zip([z for z in range(0, len(arr_arm_e))], arr_arm_e))
    dict_arm_f = dict(zip([z for z in range(0, len(arr_arm_f))], arr_arm_f))
    dict_arm_j = dict(zip([z for z in range(0, len(arr_arm_j))], arr_arm_j))

    dict_ass_a = dict(zip([z for z in range(0, len(arr_ass_a))], arr_ass_a))
    dict_ass_b = dict(zip([z for z in range(0, len(arr_ass_b))], arr_ass_b))
    dict_ass_c = dict(zip([z for z in range(0, len(arr_ass_c))], arr_ass_c))
    dict_ass_d = dict(zip([z for z in range(0, len(arr_ass_d))], arr_ass_d))
    dict_ass_e = dict(zip([z for z in range(0, len(arr_ass_e))], arr_ass_e))
    dict_ass_f = dict(zip([z for z in range(0, len(arr_ass_f))], arr_ass_f))
    dict_ass_j = dict(zip([z for z in range(0, len(arr_ass_j))], arr_ass_j))

    context = {
        'brand': brand,
        'title': title,

        'dict_arm_a': dict_arm_a,
        'dict_arm_b': dict_arm_b,
        'dict_arm_c': dict_arm_c,
        'dict_arm_d': dict_arm_d,
        'dict_arm_e': dict_arm_e,
        'dict_arm_f': dict_arm_f,
        'dict_arm_j': dict_arm_j,

        'dict_ass_a': dict_ass_a,
        'dict_ass_b': dict_ass_b,
        'dict_ass_c': dict_ass_c,
        'dict_ass_d': dict_ass_d,
        'dict_ass_e': dict_ass_e,
        'dict_ass_f': dict_ass_f,
        'dict_ass_j': dict_ass_j,
    }

    if request.method == 'GET':
        if request.is_ajax():
            context_data = {
                'dict_arm_a': dict_arm_a,
                'dict_arm_b': dict_arm_b,
                'dict_arm_c': dict_arm_c,
                'dict_arm_d': dict_arm_d,
                'dict_arm_e': dict_arm_e,
                'dict_arm_f': dict_arm_f,
                'dict_arm_j': dict_arm_j,

                'dict_ass_a': dict_ass_a,
                'dict_ass_b': dict_ass_b,
                'dict_ass_c': dict_ass_c,
                'dict_ass_d': dict_ass_d,
                'dict_ass_e': dict_ass_e,
                'dict_ass_f': dict_ass_f,
                'dict_ass_j': dict_ass_j,
            }
            data = {
                'tbl_arm_a': render_to_string('write/ajax_data/table-arm-a.html', context=context_data),
                'tbl_arm_b': render_to_string('write/ajax_data/table-arm-b.html', context=context_data),
                'tbl_arm_c': render_to_string('write/ajax_data/table-arm-c.html', context=context_data),
                'tbl_arm_d': render_to_string('write/ajax_data/table-arm-d.html', context=context_data),
                'tbl_arm_e': render_to_string('write/ajax_data/table-arm-e.html', context=context_data),
                'tbl_arm_f': render_to_string('write/ajax_data/table-arm-f.html', context=context_data),
                'tbl_arm_j': render_to_string('write/ajax_data/table-arm-j.html', context=context_data),

                'tbl_ass_a': render_to_string('write/ajax_data/table-ass-a.html', context=context_data),
                'tbl_ass_b': render_to_string('write/ajax_data/table-ass-b.html', context=context_data),
                'tbl_ass_c': render_to_string('write/ajax_data/table-ass-c.html', context=context_data),
                'tbl_ass_d': render_to_string('write/ajax_data/table-ass-d.html', context=context_data),
                'tbl_ass_e': render_to_string('write/ajax_data/table-ass-e.html', context=context_data),
                'tbl_ass_f': render_to_string('write/ajax_data/table-ass-f.html', context=context_data),
                'tbl_ass_j': render_to_string('write/ajax_data/table-ass-j.html', context=context_data),
            }
            return JsonResponse({'data': data}, status=200)

    return render(request, 'write/home.html', context=context)

@login_required(login_url='login')
def planning(request):
    title = 'Planning'
    path = f"{settings.BASE_DIR}/static/json/"
    # print(path)

    departments = Department.objects.all()
    lines = Line.objects.all()
    dj_models = DJModel.objects.all()

    submit_data = []

    if request.method == 'POST':
        if 'btn-plan' in request.POST:
            # Get data Plan form
            my_timestamp = datetime.timestamp(timezone.now())
            my_time = datetime.fromtimestamp(my_timestamp).strftime('%H:%M:%S')
            my_date = datetime.fromtimestamp(my_timestamp).strftime('%Y-%m-%d')
            # Custom date
            current_date = datetime.fromtimestamp(my_timestamp)
            if current_date.hour < 6 and current_date.minute < 55:
                yesterday = current_date - timedelta(days=1)
                my_date = datetime(yesterday.year, yesterday.month,
                                   yesterday.day).strftime('%Y-%m-%d')

            department = Department.objects.filter(
                name=request.POST['department'])
            if department:
                department = request.POST['department']

            line = Line.objects.filter(name=request.POST['line'])
            if line:
                line = request.POST['line']

            dj_model = DJModel.objects.filter(
                description=request.POST['dj_model'])
            if dj_model:
                dj_model = request.POST['dj_model']

            plan = ''
            if str(request.POST['plan']).isnumeric():
                plan = int(request.POST['plan'])
                if plan == 0:
                    plan = 1

            version = ''
            if str(request.POST['version']).isnumeric():
                version = int(request.POST['version'])

            shift_work = 0
            if 'check-shift' in request.POST:
                shift_work = 1

            if department and line and dj_model and plan != '' and version != '':
                # Check plan exists in database
                plan_exists = Planning.objects.filter(date=my_date, department=department,
                                                      line=line, model=dj_model,
                                                      version=version, shift_work=shift_work,
                                                      qty_plan=plan)

                if not plan_exists:
                    my_plan = Planning(timestamp=my_timestamp, date=my_date, time=my_time,
                                       department=department, line=line, model=dj_model,
                                       version=version, shift_work=shift_work, qty_plan=plan)
                    my_plan.save()

                    messages.add_message(
                        request, messages.SUCCESS, 'Plan are created.')
                    info = f"<style>table, th, td {{border: 1px solid black;}}\
                    li.safe.info{{margin-left:5px;}}</style><table><thead>\
                    <th>Department</th><th>Line</th><th>Model</th><th>Plan</th>\
                    <th>Version</th><th>3rd Shift</th></thead><tbody><tr>\
                    <td>{department}</td><td>{line}</td><td>{dj_model}</td>\
                    <td>{plan}</td><td>{version}</td><td>{shift_work}</td>\
                    </tr></tbody></table>"
                    messages.add_message(request, messages.INFO,
                                         info, extra_tags='safe')

                    # Get plan of current date
                    today_plan_arm_a = Planning.objects.filter(
                        date=my_date, department='ARM', line='A').last()
                    today_plan_arm_b = Planning.objects.filter(
                        date=my_date, department='ARM', line='B').last()
                    today_plan_arm_c = Planning.objects.filter(
                        date=my_date, department='ARM', line='C').last()
                    today_plan_arm_d = Planning.objects.filter(
                        date=my_date, department='ARM', line='D').last()
                    today_plan_arm_e = Planning.objects.filter(
                        date=my_date, department='ARM', line='E').last()
                    today_plan_arm_f = Planning.objects.filter(
                        date=my_date, department='ARM', line='F').last()
                    today_plan_arm_j = Planning.objects.filter(
                        date=my_date, department='ARM', line='J').last()

                    today_plan_ass_a = Planning.objects.filter(
                        date=my_date, department='ASS', line='A').last()
                    today_plan_ass_b = Planning.objects.filter(
                        date=my_date, department='ASS', line='B').last()
                    today_plan_ass_c = Planning.objects.filter(
                        date=my_date, department='ASS', line='C').last()
                    today_plan_ass_d = Planning.objects.filter(
                        date=my_date, department='ASS', line='D').last()
                    today_plan_ass_e = Planning.objects.filter(
                        date=my_date, department='ASS', line='E').last()
                    today_plan_ass_f = Planning.objects.filter(
                        date=my_date, department='ASS', line='F').last()
                    today_plan_ass_j = Planning.objects.filter(
                        date=my_date, department='ASS', line='J').last()

                    # Get data of plan
                    arr_arm_a = get_arr_plan(today_plan_arm_a)
                    arr_arm_b = get_arr_plan(today_plan_arm_b)
                    arr_arm_c = get_arr_plan(today_plan_arm_c)
                    arr_arm_d = get_arr_plan(today_plan_arm_d)
                    arr_arm_e = get_arr_plan(today_plan_arm_e)
                    arr_arm_f = get_arr_plan(today_plan_arm_f)
                    arr_arm_j = get_arr_plan(today_plan_arm_j)

                    arr_ass_a = get_arr_plan(today_plan_ass_a)
                    arr_ass_b = get_arr_plan(today_plan_ass_b)
                    arr_ass_c = get_arr_plan(today_plan_ass_c)
                    arr_ass_d = get_arr_plan(today_plan_ass_d)
                    arr_ass_e = get_arr_plan(today_plan_ass_e)
                    arr_ass_f = get_arr_plan(today_plan_ass_f)
                    arr_ass_j = get_arr_plan(today_plan_ass_j)

                    submit_data.append(arr_arm_a)
                    submit_data.append(arr_arm_b)
                    submit_data.append(arr_arm_c)
                    submit_data.append(arr_arm_d)
                    submit_data.append(arr_arm_e)
                    submit_data.append(arr_arm_f)
                    submit_data.append(arr_arm_j)

                    submit_data.append(arr_ass_a)
                    submit_data.append(arr_ass_b)
                    submit_data.append(arr_ass_c)
                    submit_data.append(arr_ass_d)
                    submit_data.append(arr_ass_e)
                    submit_data.append(arr_ass_f)
                    submit_data.append(arr_ass_j)
                    # print(submit_data)
                else:
                    messages.add_message(
                        request, messages.WARNING, 'Plan already exists in database. Please check your version.')

            else:
                messages.add_message(
                    request, messages.WARNING, 'Submit invalid data.')
            # Export data to json file
            with open(f"{path}active_lines.json", 'w+', encoding="utf-8") as f:
                json.dump(submit_data, f, indent=4, ensure_ascii=False)

    context = {
        'brand': brand,
        'title': title,
        'departments': departments,
        'lines': lines,
        'dj_models': dj_models,
    }

    return render(request, 'write/planning.html', context=context)


def history(request):
    title = 'History'
    # Default selected date
    current_date = datetime.fromtimestamp(
        datetime.timestamp(timezone.now()))
    current_date_str = current_date.strftime('%Y-%m-%d')
    selected_date = current_date_str

    if request.method == 'POST':
        if 'btn-history' in request.POST:
            try:  # Validate data when user submit
                user_submit_date = request.POST['date-history']
                selected_date_obj = datetime(int(user_submit_date[:4]),
                                             int(user_submit_date[5:7]),
                                             int(user_submit_date[-2:]))
                selected_date = selected_date_obj.strftime('%Y-%m-%d')
            except:
                pass

            if selected_date == current_date.strftime('%Y-%m-%d'):
                if current_date.hour < 6 and current_date.minute < 55:
                    yesterday = current_date - timedelta(days=1)
                    selected_date = datetime(yesterday.year,
                                             yesterday.month,
                                             yesterday.day).strftime('%Y-%m-%d')

    selected_plan_arm_a = Planning.objects.filter(
        date=selected_date, department='ARM', line='A')
    selected_plan_arm_b = Planning.objects.filter(
        date=selected_date, department='ARM', line='B')
    selected_plan_arm_c = Planning.objects.filter(
        date=selected_date, department='ARM', line='C')
    selected_plan_arm_d = Planning.objects.filter(
        date=selected_date, department='ARM', line='D')
    selected_plan_arm_e = Planning.objects.filter(
        date=selected_date, department='ARM', line='E')
    selected_plan_arm_f = Planning.objects.filter(
        date=selected_date, department='ARM', line='F')
    selected_plan_arm_j = Planning.objects.filter(
        date=selected_date, department='ARM', line='J')

    selected_plan_ass_a = Planning.objects.filter(
        date=selected_date, department='ASS', line='A')
    selected_plan_ass_b = Planning.objects.filter(
        date=selected_date, department='ASS', line='B')
    selected_plan_ass_c = Planning.objects.filter(
        date=selected_date, department='ASS', line='C')
    selected_plan_ass_d = Planning.objects.filter(
        date=selected_date, department='ASS', line='D')
    selected_plan_ass_e = Planning.objects.filter(
        date=selected_date, department='ASS', line='E')
    selected_plan_ass_f = Planning.objects.filter(
        date=selected_date, department='ASS', line='F')
    selected_plan_ass_j = Planning.objects.filter(
        date=selected_date, department='ASS', line='J')

    # ARM
    arr_arm_a = get_arr_history(selected_plan_arm_a)
    arr_arm_b = get_arr_history(selected_plan_arm_b)
    arr_arm_c = get_arr_history(selected_plan_arm_c)
    arr_arm_d = get_arr_history(selected_plan_arm_d)
    arr_arm_e = get_arr_history(selected_plan_arm_e)
    arr_arm_f = get_arr_history(selected_plan_arm_f)
    arr_arm_j = get_arr_history(selected_plan_arm_j)

    # ASS
    arr_ass_a = get_arr_history(selected_plan_ass_a)
    arr_ass_b = get_arr_history(selected_plan_ass_b)
    arr_ass_c = get_arr_history(selected_plan_ass_c)
    arr_ass_d = get_arr_history(selected_plan_ass_d)
    arr_ass_e = get_arr_history(selected_plan_ass_e)
    arr_ass_f = get_arr_history(selected_plan_ass_f)
    arr_ass_j = get_arr_history(selected_plan_ass_j)

    dict_arm_a = dict(zip([z for z in range(0, len(arr_arm_a))], arr_arm_a))
    dict_arm_b = dict(zip([z for z in range(0, len(arr_arm_b))], arr_arm_b))
    dict_arm_c = dict(zip([z for z in range(0, len(arr_arm_c))], arr_arm_c))
    dict_arm_d = dict(zip([z for z in range(0, len(arr_arm_d))], arr_arm_d))
    dict_arm_e = dict(zip([z for z in range(0, len(arr_arm_e))], arr_arm_e))
    dict_arm_f = dict(zip([z for z in range(0, len(arr_arm_f))], arr_arm_f))
    dict_arm_j = dict(zip([z for z in range(0, len(arr_arm_j))], arr_arm_j))

    dict_ass_a = dict(zip([z for z in range(0, len(arr_ass_a))], arr_ass_a))
    dict_ass_b = dict(zip([z for z in range(0, len(arr_ass_b))], arr_ass_b))
    dict_ass_c = dict(zip([z for z in range(0, len(arr_ass_c))], arr_ass_c))
    dict_ass_d = dict(zip([z for z in range(0, len(arr_ass_d))], arr_ass_d))
    dict_ass_e = dict(zip([z for z in range(0, len(arr_ass_e))], arr_ass_e))
    dict_ass_f = dict(zip([z for z in range(0, len(arr_ass_f))], arr_ass_f))
    dict_ass_j = dict(zip([z for z in range(0, len(arr_ass_j))], arr_ass_j))

    context = {
        'brand': brand,
        'title': title,
        'selected_date': selected_date,
        'current_date': current_date_str,

        'dict_arm_a': dict_arm_a,
        'dict_arm_b': dict_arm_b,
        'dict_arm_c': dict_arm_c,
        'dict_arm_d': dict_arm_d,
        'dict_arm_e': dict_arm_e,
        'dict_arm_f': dict_arm_f,
        'dict_arm_j': dict_arm_j,

        'dict_ass_a': dict_ass_a,
        'dict_ass_b': dict_ass_b,
        'dict_ass_c': dict_ass_c,
        'dict_ass_d': dict_ass_d,
        'dict_ass_e': dict_ass_e,
        'dict_ass_f': dict_ass_f,
        'dict_ass_j': dict_ass_j,

        'json_arm_a': json.dumps(dict_arm_a),
        'json_arm_b': json.dumps(dict_arm_b),
        'json_arm_c': json.dumps(dict_arm_c),
        'json_arm_d': json.dumps(dict_arm_d),
        'json_arm_e': json.dumps(dict_arm_e),
        'json_arm_f': json.dumps(dict_arm_f),
        'json_arm_j': json.dumps(dict_arm_j),

        'json_ass_a': json.dumps(dict_ass_a),
        'json_ass_b': json.dumps(dict_ass_b),
        'json_ass_c': json.dumps(dict_ass_c),
        'json_ass_d': json.dumps(dict_ass_d),
        'json_ass_e': json.dumps(dict_ass_e),
        'json_ass_f': json.dumps(dict_ass_f),
        'json_ass_j': json.dumps(dict_ass_j),
    }
    return render(request, 'write/history.html', context=context)


def chart(request):
    title = 'Chart'
    my_date = datetime.fromtimestamp(
        datetime.timestamp(timezone.now())).strftime('%Y-%m-%d')

    # Get plan of all line in current date
    today_plan_arm_a = Planning.objects.filter(
        date=my_date, department='ARM', line='A').last()
    today_plan_arm_b = Planning.objects.filter(
        date=my_date, department='ARM', line='B').last()
    today_plan_arm_c = Planning.objects.filter(
        date=my_date, department='ARM', line='C').last()
    today_plan_arm_d = Planning.objects.filter(
        date=my_date, department='ARM', line='D').last()
    today_plan_arm_e = Planning.objects.filter(
        date=my_date, department='ARM', line='E').last()
    today_plan_arm_f = Planning.objects.filter(
        date=my_date, department='ARM', line='F').last()
    today_plan_arm_j = Planning.objects.filter(
        date=my_date, department='ARM', line='J').last()

    today_plan_ass_a = Planning.objects.filter(
        date=my_date, department='ASS', line='A').last()
    today_plan_ass_b = Planning.objects.filter(
        date=my_date, department='ASS', line='B').last()
    today_plan_ass_c = Planning.objects.filter(
        date=my_date, department='ASS', line='C').last()
    today_plan_ass_d = Planning.objects.filter(
        date=my_date, department='ASS', line='D').last()
    today_plan_ass_e = Planning.objects.filter(
        date=my_date, department='ASS', line='E').last()
    today_plan_ass_f = Planning.objects.filter(
        date=my_date, department='ASS', line='F').last()
    today_plan_ass_j = Planning.objects.filter(
        date=my_date, department='ASS', line='J').last()

    # ARM
    arr_arm_a = get_arr_last_model(today_plan_arm_a)
    arr_arm_b = get_arr_last_model(today_plan_arm_b)
    arr_arm_c = get_arr_last_model(today_plan_arm_c)
    arr_arm_d = get_arr_last_model(today_plan_arm_d)
    arr_arm_e = get_arr_last_model(today_plan_arm_e)
    arr_arm_f = get_arr_last_model(today_plan_arm_f)
    arr_arm_j = get_arr_last_model(today_plan_arm_j)

    # ASS
    arr_ass_a = get_arr_last_model(today_plan_ass_a)
    arr_ass_b = get_arr_last_model(today_plan_ass_b)
    arr_ass_c = get_arr_last_model(today_plan_ass_c)
    arr_ass_d = get_arr_last_model(today_plan_ass_d)
    arr_ass_e = get_arr_last_model(today_plan_ass_e)
    arr_ass_f = get_arr_last_model(today_plan_ass_f)
    arr_ass_j = get_arr_last_model(today_plan_ass_j)

    dict_arm_a = dict(zip([z for z in range(0, len(arr_arm_a))], arr_arm_a))
    dict_arm_b = dict(zip([z for z in range(0, len(arr_arm_b))], arr_arm_b))
    dict_arm_c = dict(zip([z for z in range(0, len(arr_arm_c))], arr_arm_c))
    dict_arm_d = dict(zip([z for z in range(0, len(arr_arm_d))], arr_arm_d))
    dict_arm_e = dict(zip([z for z in range(0, len(arr_arm_e))], arr_arm_e))
    dict_arm_f = dict(zip([z for z in range(0, len(arr_arm_f))], arr_arm_f))
    dict_arm_j = dict(zip([z for z in range(0, len(arr_arm_j))], arr_arm_j))

    dict_ass_a = dict(zip([z for z in range(0, len(arr_ass_a))], arr_ass_a))
    dict_ass_b = dict(zip([z for z in range(0, len(arr_ass_b))], arr_ass_b))
    dict_ass_c = dict(zip([z for z in range(0, len(arr_ass_c))], arr_ass_c))
    dict_ass_d = dict(zip([z for z in range(0, len(arr_ass_d))], arr_ass_d))
    dict_ass_e = dict(zip([z for z in range(0, len(arr_ass_e))], arr_ass_e))
    dict_ass_f = dict(zip([z for z in range(0, len(arr_ass_f))], arr_ass_f))
    dict_ass_j = dict(zip([z for z in range(0, len(arr_ass_j))], arr_ass_j))

    context = {
        'brand': brand,
        'title': title,

        'dict_arm_a': dict_arm_a,
        'dict_arm_b': dict_arm_b,
        'dict_arm_c': dict_arm_c,
        'dict_arm_d': dict_arm_d,
        'dict_arm_e': dict_arm_e,
        'dict_arm_f': dict_arm_f,
        'dict_arm_j': dict_arm_j,

        'dict_ass_a': dict_ass_a,
        'dict_ass_b': dict_ass_b,
        'dict_ass_c': dict_ass_c,
        'dict_ass_d': dict_ass_d,
        'dict_ass_e': dict_ass_e,
        'dict_ass_f': dict_ass_f,
        'dict_ass_j': dict_ass_j,

        'json_arm_a': json.dumps(dict_arm_a),
        'json_arm_b': json.dumps(dict_arm_b),
        'json_arm_c': json.dumps(dict_arm_c),
        'json_arm_d': json.dumps(dict_arm_d),
        'json_arm_e': json.dumps(dict_arm_e),
        'json_arm_f': json.dumps(dict_arm_f),
        'json_arm_j': json.dumps(dict_arm_j),

        'json_ass_a': json.dumps(dict_ass_a),
        'json_ass_b': json.dumps(dict_ass_b),
        'json_ass_c': json.dumps(dict_ass_c),
        'json_ass_d': json.dumps(dict_ass_d),
        'json_ass_e': json.dumps(dict_ass_e),
        'json_ass_f': json.dumps(dict_ass_f),
        'json_ass_j': json.dumps(dict_ass_j),
    }

    if request.method == 'GET':
        if request.is_ajax():
            context_data = {
                'dict_arm_a': dict_arm_a,
                'dict_arm_b': dict_arm_b,
                'dict_arm_c': dict_arm_c,
                'dict_arm_d': dict_arm_d,
                'dict_arm_e': dict_arm_e,
                'dict_arm_f': dict_arm_f,
                'dict_arm_j': dict_arm_j,

                'dict_ass_a': dict_ass_a,
                'dict_ass_b': dict_ass_b,
                'dict_ass_c': dict_ass_c,
                'dict_ass_d': dict_ass_d,
                'dict_ass_e': dict_ass_e,
                'dict_ass_f': dict_ass_f,
                'dict_ass_j': dict_ass_j,
            }

            data = {
                'canvas_arm_a': render_to_string('write/ajax_data/canvas-arm-a.html', context=context_data),
                'canvas_arm_b': render_to_string('write/ajax_data/canvas-arm-b.html', context=context_data),
                'canvas_arm_c': render_to_string('write/ajax_data/canvas-arm-c.html', context=context_data),
                'canvas_arm_d': render_to_string('write/ajax_data/canvas-arm-d.html', context=context_data),
                'canvas_arm_e': render_to_string('write/ajax_data/canvas-arm-e.html', context=context_data),
                'canvas_arm_f': render_to_string('write/ajax_data/canvas-arm-f.html', context=context_data),
                'canvas_arm_j': render_to_string('write/ajax_data/canvas-arm-j.html', context=context_data),

                'canvas_ass_a': render_to_string('write/ajax_data/canvas-ass-a.html', context=context_data),
                'canvas_ass_b': render_to_string('write/ajax_data/canvas-ass-b.html', context=context_data),
                'canvas_ass_c': render_to_string('write/ajax_data/canvas-ass-c.html', context=context_data),
                'canvas_ass_d': render_to_string('write/ajax_data/canvas-ass-d.html', context=context_data),
                'canvas_ass_e': render_to_string('write/ajax_data/canvas-ass-e.html', context=context_data),
                'canvas_ass_f': render_to_string('write/ajax_data/canvas-ass-f.html', context=context_data),
                'canvas_ass_j': render_to_string('write/ajax_data/canvas-ass-j.html', context=context_data),
            }
            return JsonResponse({'data': data}, status=200)

    return render(request, 'write/chart.html', context=context)


@login_required(login_url='login')
def check_plan(request):
    title = 'Check Plan'

    departments = Department.objects.all()
    lines = Line.objects.all()
    dj_models = DJModel.objects.all()

    my_plan = ''

    if request.method == 'POST':
        if 'btn-check-plan' in request.POST:
            # Get data Plan form
            my_timestamp = datetime.timestamp(timezone.now())
            my_time = datetime.fromtimestamp(my_timestamp).strftime('%H:%M:%S')
            my_date = datetime.fromtimestamp(my_timestamp).strftime('%Y-%m-%d')
            # Custom date
            current_date = datetime.fromtimestamp(my_timestamp)
            if current_date.hour < 6 and current_date.minute < 55:
                yesterday = current_date - timedelta(days=1)
                my_date = datetime(yesterday.year, yesterday.month,
                                   yesterday.day).strftime('%Y-%m-%d')

            department = Department.objects.filter(
                name=request.POST['department'])
            if department:
                department = request.POST['department']

            line = Line.objects.filter(name=request.POST['line'])
            if line:
                line = request.POST['line']

            dj_model = DJModel.objects.filter(
                description=request.POST['dj_model'])
            if dj_model:
                dj_model = request.POST['dj_model']

            plan = ''
            if str(request.POST['plan']).isnumeric():
                plan = int(request.POST['plan'])
                if plan == 0:
                    plan = 1

            version = ''
            if str(request.POST['version']).isnumeric():
                version = int(request.POST['version'])

            shift_work = 0
            if 'check-shift' in request.POST:
                shift_work = 1

            if department and line and dj_model and plan != '' and version != '':
                # Check plan exists in database
                plan_exists = Planning.objects.filter(date=my_date, department=department,
                                                      line=line, model=dj_model,
                                                      version=version, shift_work=shift_work,
                                                      qty_plan=plan)

                if plan_exists:
                    my_plan = plan_exists.last()
                    return redirect('test_input', my_plan.id)

                else:
                    messages.add_message(
                        request, messages.WARNING, 'Your PLAN request: ')
                    info = f"<style>table, th, td {{border: 1px solid black;}}\
                    li.safe.info{{margin-left:5px;}}</style><table><thead>\
                    <th>Department</th><th>Line</th><th>Model</th><th>Plan</th>\
                    <th>Version</th><th>3rd Shift</th></thead><tbody><tr>\
                    <td>{department}</td><td>{line}</td><td>{dj_model}</td>\
                    <td>{plan}</td><td>{version}</td><td>{shift_work}</td>\
                    </tr></tbody></table>"
                    messages.add_message(request, messages.INFO,
                                         info, extra_tags='safe')

                    messages.add_message(
                        request, messages.ERROR, 'Not found this PLAN. Please check your information and try again.')

    context = {
        'brand': brand,
        'title': title,
        'departments': departments,
        'lines': lines,
        'dj_models': dj_models,
        'my_plan': my_plan,
    }

    return render(request, 'write/check-plan.html', context=context)


@login_required(login_url='login')
def test_input(request, pk_plan):
    title = 'Test Input'
    current_timestamp = datetime.timestamp(timezone.now())
    # current_date = datetime.fromtimestamp(current_timestamp)
    # current_date_str = current_date.strftime('%Y-%m-%d')

    departments = Department.objects.all()
    lines = Line.objects.all()
    dj_models = DJModel.objects.all()

    my_plan = Planning.objects.get(id=pk_plan)
    my_processes = DJProcess.objects.filter(
        department__name=my_plan.department, model__description=my_plan.model)

    if request.method == 'POST':
        start = False
        qty_actual = 0
        timestamp = current_timestamp
        machine = True
        material = True
        quality = True
        other = True
        date = my_plan.date
        version = my_plan.version
        shift_work = my_plan.shift_work
        qty_plan = my_plan.qty_plan
        department = Department.objects.get(name=my_plan.department)
        line = Line.objects.get(name=my_plan.line)
        process_id = request.POST['btn-process-id']

        # Check exists
        exists_data = WriteData.objects.filter(date=date, department=department,
                                               line=line, process_id=process_id,
                                               version=version, shift_work=shift_work,
                                               qty_plan=qty_plan).last()
        if exists_data:
            start = exists_data.start
            qty_actual = exists_data.qty_actual
            machine = exists_data.machine
            material = exists_data.material
            quality = exists_data.quality
            other = exists_data.other
        else:
            new_data = WriteData(start=start, qty_actual=qty_actual, timestamps=timestamp,
                                 machine=machine, material=material, quality=quality,
                                 other=other, date=date, version=version,
                                 shift_work=shift_work, qty_plan=qty_plan,
                                 department=department, line=line,
                                 process_id=process_id)
            new_data.save()

            exists_data = WriteData.objects.get(date=date, department=department,
                                                line=line, process_id=process_id,
                                                version=version, shift_work=shift_work,
                                                qty_plan=qty_plan)

        if 'btn-other' in request.POST:
            other = not other
        if 'btn-quality' in request.POST:
            quality = not quality
        if 'btn-material' in request.POST:
            material = not material
        if 'btn-machine' in request.POST:
            machine = not machine
        if 'btn-on-off' in request.POST:
            start = not start

        try:  # Validate qty_actual of user submit
            qty_actual = request.POST['txt-qty-actual']
            qty_actual = int(qty_actual)
        except:
            qty_actual = exists_data.qty_actual

        new_data = WriteData(start=start, qty_actual=qty_actual, timestamps=timestamp,
                             machine=machine, material=material, quality=quality,
                             other=other, date=date, version=version,
                             shift_work=shift_work, qty_plan=qty_plan,
                             department=department, line=line,
                             process_id=process_id)
        # print(qty_actual, timestamp, other, quality, material, machine, start,
        #       date, version, shift_work, qty_plan, department, line, process_id)
        new_data.save()

    context = {
        'brand': brand,
        'title': title,
        'departments': departments,
        'lines': lines,
        'dj_models': dj_models,
        'my_plan': my_plan,
        'my_processes': my_processes,
    }

    return render(request, 'write/test-input.html', context=context)
