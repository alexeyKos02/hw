# grpc_server.py
from concurrent import futures
import grpc
from business_pb2 import BusinessResponse
from business_pb2_grpc import BusinessServiceServicer, add_BusinessServiceServicer_to_server
from app import db, create_app
from app.models import BusinessData

app = create_app()
app.app_context().push()  # Создаем контекст приложения

class BusinessService(BusinessServiceServicer):
    def Create(self, request, context):
        # Создание данных
        new_data = BusinessData(data=request.data)
        db.session.add(new_data)
        db.session.commit()
        return BusinessResponse(message="Data created successfully")

    def Get(self, request, context):
        # Получение данных
        data = BusinessData.query.get(request.id)
        if data:
            return BusinessResponse(message=data.data)
        return BusinessResponse(message="Data not found")

    def Update(self, request, context):
        # Обновление данных
        data = BusinessData.query.get(request.id)
        if data:
            data.data = request.data
            db.session.commit()
            return BusinessResponse(message="Data updated successfully")
        return BusinessResponse(message="Data not found")

    def Delete(self, request, context):
        # Удаление данных
        data = BusinessData.query.get(request.id)
        if data:
            db.session.delete(data)
            db.session.commit()
            return BusinessResponse(message="Data deleted successfully")
        return BusinessResponse(message="Data not found")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_BusinessServiceServicer_to_server(BusinessService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC Server started. Listening on port 50051.")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
