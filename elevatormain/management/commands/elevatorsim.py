from django.core.management.base import BaseCommand, CommandError
import time
from elevatormain.models import Elevator, Building, Log
from datetime import datetime
import ast

# Disables specific elevators based on building active elevator number while it's not equal to number of active elevators
# Only disables elevators which are stationary and have no pending requests
def elevators_status(elevators_in_use, building_active_elevators, elevators):
    if len(elevators_in_use) > building_active_elevators:
        disable_elevators_n = len(elevators_in_use) - building_active_elevators
        if elevators.filter(action=0).count() >= disable_elevators_n:
            for elevator in elevators.order_by('-id'):
                if disable_elevators_n != 0:
                    if elevator.action == 0 and elevator.id in elevators_in_use and len(ast.literal_eval(elevator.request)) == 0:
                        elevator.active = 0
                        elevator.save()
                        disable_elevators_n -= 1

    if len(elevators_in_use) < building_active_elevators:
        enable_elevators_n = building_active_elevators - len(elevators_in_use)
        for elevator in elevators.order_by('-id'):
            if enable_elevators_n != 0:
                if elevator.id not in elevators_in_use:
                    elevator.active = 1
                    elevator.save()
                    enable_elevators_n -= 1

    return elevators_in_use


# Handles building and elevator requests
def handle_requests(elevators, building):
    building_requests = ast.literal_eval(building.requests)
    for building_request in building_requests:
        closest_elevator = [0, 1000]  # [1] is a place keeper. Any integer bigger than building floor count
        for elevator in elevators.filter(action=0, active=1):
            if len(ast.literal_eval(elevator.request)) == 0:

                # Finds closest available elevator
                if abs(elevator.current_floor - building_request[0]) < closest_elevator[1]:
                    closest_elevator = [elevator.id, abs(elevator.current_floor - building_request[0])]

        # If elevators available assigns closest one to request
        if closest_elevator[1] != 1000:
            elevator = elevators.filter(id=closest_elevator[0]).first()
            elevator.request = building_request
            building_requests.remove(building_request)
            building.requests = building_requests
            building.save()
            elevator.save()

    # Assigns elevator's next action from elevator.requests list
    for elevator in elevators.filter(action=0, active=1):
        elevator_request_n = len(ast.literal_eval(elevator.request))
        if elevator_request_n != 0:
            elevator.action = ast.literal_eval(elevator.request)[0]
            elevator_request = ast.literal_eval(elevator.request)
            del elevator_request[0]
            elevator.request = elevator_request
            elevator.save()


def move_elevators(elevators, elevators_movement):
    for elevator in elevators:
        if elevator.action != 0 and elevator.action not in (-1, -2):
            if elevator.id not in elevators_movement.keys():
                log = Log(elevator_id=elevator.id, action='called', position=elevator.current_floor,
                          destination=elevator.action, time=datetime.now().replace(microsecond=0))
                log.save()
                elevators_movement[elevator.id] = {'last_floor': int(time.time())}

                if elevator.current_floor < elevator.action:
                    elevators_movement[elevator.id]['direction'] = 'up'
                elif elevator.current_floor > elevator.action:
                    elevators_movement[elevator.id]['direction'] = 'down'

            if abs(elevator.current_floor - elevator.action) != 0 and elevator.action not in (-1, -2):
                if int(time.time()) - elevators_movement[elevator.id]['last_floor'] >= elevator.movement_speed:
                    if elevators_movement[elevator.id]['direction'] == 'down':
                        elevator.current_floor -= 1
                    else:
                        elevator.current_floor += 1

                    log = Log(elevator_id=elevator.id, action=elevators_movement[elevator.id]['direction'],
                              position=elevator.current_floor,
                              destination=elevator.action, time=datetime.now().replace(microsecond=0))
                    log.save()
                    elevators_movement[elevator.id]['last_floor'] = int(time.time())
                    elevator.save()
            else:
                log = Log(elevator_id=elevator.id, action='arrived',
                          position=elevator.current_floor,
                          destination=elevator.action, time=datetime.now().replace(microsecond=0))
                log.save()
                elevator.action = 0
                elevator.save()

            # Elevator arrived, open doors
            if elevator.action == 0:
                elevator.action = -1
                elevator.save()
                del elevators_movement[elevator.id]

        # Handles opening and closing of doors
        elif elevator.action in (-1, -2):
            if elevator.id not in elevators_movement.keys():
                elevators_movement[elevator.id] = {'door_time': int(time.time())}
                log = Log(elevator_id=elevator.id, action='doors open',
                          position=elevator.current_floor,
                          destination=elevator.action, time=datetime.now().replace(microsecond=0))
                log.save()
            # Open doors
            if elevator.action == -1:
                if int(time.time()) - elevators_movement[elevator.id]['door_time'] >= elevator.door_speed:
                    elevator.action = -2
                    elevator.save()
                    elevators_movement[elevator.id]['door_time'] = int(time.time())

            # Close doors
            elif elevator.action == -2:
                if int(time.time()) - elevators_movement[elevator.id]['door_time'] >= elevator.door_speed:
                    log = Log(elevator_id=elevator.id, action='doors close',
                              position=elevator.current_floor,
                              destination=elevator.action, time=datetime.now().replace(microsecond=0))
                    log.save()
                    elevator.action = 0
                    elevator.save()
                    elevators_movement[elevator.id]['door_time'] = 0
                    del elevators_movement[elevator.id]

    return elevators_movement


class Command(BaseCommand):

    def handle(self, *args, **options):
        elevators_movement = {}

        while True:
            elevators = Elevator.objects.all()
            building = Building.objects.first()
            building_active_elevators = building.active_elevators
            elevators_in_use = [x.id for x in elevators if x.active == 1]

            elevators_in_use = elevators_status(elevators_in_use, building_active_elevators, elevators)
            elevators_movement = move_elevators(elevators, elevators_movement)
            handle_requests(elevators, building)

            time.sleep(0.01)
