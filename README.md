# Elevator
Elevator control API with elevator simulator

python manage.py elevatorsim to start simulator

# GET requests:
* /control?elevator_id=x | x - elevator id. Returns elevator status
* /control?elevator_id=x&log=1 | x - elevator id. Returns log info for specified elevators

# POST requests:
* /control {'request_from': x, 'request_to': y} | Submits elevator request. x, y - floor number
* /control {'floor_count': x} | Updates building floor count
* /control {'active_elevators': x} | Sets active elevator count


