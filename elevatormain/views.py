from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Elevator, Building, Log
from django.views.decorators.csrf import csrf_exempt
import time
import ast


@csrf_exempt
def control(request):
    if request.method == 'GET':
        response = {}
        if request.GET.get('elevator_id'):
            elevator_info = []
            elevator_ids = request.GET.get('elevator_id').split(',')

            # Check if requested ids are integers. Returns a list of ids that are not integers
            elevator_ids_not_integer = [x for x in elevator_ids if not x.isdigit()]
            if len(elevator_ids_not_integer) > 0:
                return JsonResponse({'id not an integer': elevator_ids_not_integer}, status=400)

            elevator_ids = [int(x) for x in elevator_ids]
            elevators = Elevator.objects.all()

            elevator_db_ids = [x.id for x in elevators]
            # Check if requested ids exist. Returns a list of ids not in database
            elevator_ids_not_exist = [x for x in elevator_ids if x not in elevator_db_ids]
            if len(elevator_ids_not_exist) > 0:
                return JsonResponse({'id does not exist': elevator_ids_not_exist}, status=400)

            else:
                if request.GET.get('log'):
                    send_logs = []
                    for elevator_id in elevator_ids:
                        send_log = []
                        logs = Log.objects.filter(elevator_id=elevator_id)
                        for log in logs:
                            send_log.append({'id': log.id, 'elevator_id': elevator_id, 'action': log.action,
                                             'destination': log.destination,
                                             'position': log.position, 'time': log.time})
                        send_logs.append(send_log)
                    return JsonResponse({'logs': send_logs}, status=200)

                for elevator_id in elevator_ids:
                    elevator = Elevator.objects.filter(id=elevator_id).first()
                    if elevator.action not in (0, -1, -2):
                        if elevator.current_floor < elevator.action:
                            direction = 'up'
                        else:
                            direction = 'down'
                    else:
                        direction = 'still'

                    elevator_info.append({'elevator_id': elevator.id, 'current_floor': elevator.current_floor,
                                          'elevator_active': elevator.active, 'elevator_action': elevator.action,
                                          'direciton': direction})

            response = {
                'elevator_info': elevator_info
            }

        return JsonResponse(response)

    if request.method == 'POST':
        print(request)
        if request.POST.get('request_from') and request.POST.get('request_to'):
            building = Building.objects.first()
            request_from = request.POST.get('request_from')
            request_to = request.POST.get('request_to')

            try:
                request_from = int(request_from)
            except ValueError:
                return JsonResponse({'not an integer': request_from}, status=400)

            try:
                request_to = int(request_to)
            except ValueError:
                return JsonResponse({'not an integer': request_to}, status=400)

            if request_from > building.floor_count or request_to > building.floor_count:
                return JsonResponse({'invalid floor': [request_from, request_to], 'floor count': building.floor_count}, status=400)

            elevator_requests = ast.literal_eval(building.requests)
            if [request_from, request_to] not in elevator_requests:
                elevator_requests.append([request_from, request_to])
            print(elevator_requests)
            building.requests = elevator_requests
            building.save()

        if request.POST.get('active_elevators'):
            active_elevators = request.POST.get('active_elevators')
            if active_elevators.isdigit():
                active_elevators = int(active_elevators)
                building = Building.objects.first()
                if active_elevators <= Elevator.objects.all().count() and active_elevators > -1:
                    building.active_elevators = active_elevators
                    building.save()
                else:
                    return JsonResponse({'invalid elevator amount': active_elevators,
                                           'elevators in building:': Elevator.objects.all().count()}, status=400)
            else:
                return JsonResponse({'invalid elevator amount': active_elevators}, status=400)

        if request.POST.get('floor_count'):
            floor_count = request.POST.get('floor_count')

            if floor_count.isdigit():
                floor_count = int(floor_count)
                if not floor_count < 2:
                    building = Building.objects.first()
                    building.floor_count = floor_count
                    building.save()
                else:
                    return JsonResponse({'invalid number of floors': floor_count, 'min floors': 2}, status=400)
            else:
                return JsonResponse({'not an integer': floor_count}, status=400)

        return HttpResponse(status=200)
