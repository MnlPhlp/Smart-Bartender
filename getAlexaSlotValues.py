import drinks

for drink in drinks.drink_list:
    value = str({"id": drink["key"], "name": {"value": drink["name"]}})
    value = value.replace("'", '"')
    print(value+",")
