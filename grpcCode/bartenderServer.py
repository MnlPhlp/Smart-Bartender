from google.protobuf.message import Message
from grpcCode.bartender_pb2 import DrinkRequest, DrinkResponse
from bartender import Bartender
from grpcCode.bartender_pb2_grpc import BartenderServicer, add_BartenderServicer_to_server
from drinks import drink_list
import grpc


class BartenderServer(BartenderServicer):
    bartender: Bartender
    validDrinks: "dict[str,list[str]]"

    def __init__(self, bartender: Bartender):
        self.bartender = bartender
        self.loadValidDrinks()

    def start(self):
        server = grpc.server(grpc.Future.ThreadPoolExecutor(max_workers=10))
        add_BartenderServicer_to_server(BartenderServicer(), server)
        server.add_insecure_port('[::]:50051')
        server.start()
        server.wait_for_termination()

    def loadValidDrinks(self):
        for drink in drink_list:
            ingredients = drink["ingredients"]
            presentIng = 0
            # check if all ingredients are configured in the pump config
            for ing in ingredients.keys():
                for p in self.bartender.pump_configuration.keys():
                    if (ing == self.bartender.pump_configuration[p]["value"]):
                        presentIng += 1
            if (presentIng == len(ingredients.keys())):
                self.validDrinks[drink["name"]] = ingredients.keys()

    def MakeDrink(self, request, context):
        """make a drink
        """
        # check if drink is valid
        if self.validDrinks[request.drink] == None:
            return DrinkResponse(
                success=False,
                message="invalid drink"
            )
        # get ingredients
        ingredients = self.validDrinks[request.drink]
        # make the drink
        self.bartender.makeDrink(request.drink, ingredients)
        return DrinkRequest(
            succes=True,
            message="started making a "+request.drink
        )
