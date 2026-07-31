import Model
from random import random

car_types = [Model.BasicCar, Model.TwoPassengersCar]

model_parameters = [
    {"nb_cars": 1, "nb_passengers": 10, "width": 30, "max_speed": 5, "seed": 0, "file_name": "city",
     "time_recompute_path": 3, "time_before_accept": 3, "time_passenger_spawn": -1, "custom_entities": None},
    {"nb_cars": 3, "nb_passengers": 20, "width": 30, "max_speed": 5, "seed": 0, "file_name": "city",
     "time_recompute_path": 3, "time_before_accept": 3, "time_passenger_spawn": -1, "custom_entities": None},
]


max_steps = 20_000
def compute_nb_steps_to_end(model):
    i = 0
    while Model.number_passengers(model) > 0 and i < max_steps:
        model.step()
        i += 1
    return i


results = [[[] for _ in range(len(model_parameters))] for _ in range(len(car_types))]
nb_errors = [[0 for _ in range(len(model_parameters))] for _ in range(len(car_types))]
for j in range(len(model_parameters)):
    model_params = model_parameters[j]
    for k in range(20):
        model_params["seed"] = random()
        for i in range(len(car_types)):
            Model.Car = car_types[i]
            model = Model.Model(**model_params)

            result = compute_nb_steps_to_end(model)
            results[i][j].append(result)
            if result >= max_steps:
                nb_errors[i][j] += 1

        print(k)


for i in range(len(results)):
    print(f"Les scores de la voiture {car_types[i]} : \n")
    for j in range(len(results[i])):
        results_filtered = [result for result in results[i][j] if result < max_steps]
        print(f"avec les paramètres suivants : {model_parameters[j]} \nla moyenne des scores est : {sum(results_filtered) / len(results_filtered)}\nle nombre d'erreurs est : {nb_errors[i][j]}")
    print("\n")
