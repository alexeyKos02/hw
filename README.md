


### 1. Запуск Minikube
Для начала запустите Minikube, который будет использоваться для локального развертывания Kubernetes:

```bash
minikube start
```
### 2. Перейдите в каталог `kubernetes`
Перейдите в каталог, содержащий все Kubernetes-ресурсы для развертывания:

```bash
cd kubernetes
```

### 3. Установка Prometheus и Grafana
Используйте скрипт для установки Prometheus и Grafana в Kubernetes:

```bash
sh install-prom-stack.sh
```

Этот скрипт установит весь необходимый стек мониторинга (Prometheus, Grafana и другие необходимые компоненты).

### 4. Применение Kubernetes-манифестов
Теперь примените Kubernetes-манифесты для развертывания приложений и ресурсов в кластере:

```bash
kubectl apply -f kubernetes/
```


### 5. Открытие портов для доступа к инструментам
Для того чтобы работать с графиками и мониторингом, откройте порты для доступа к сервисам Grafana, Prometheus и Flask-приложению:

- Откройте порт для доступа к Grafana:
    ```bash
    kubectl port-forward -n monitoring svc/kube-prom-stack-grafana 3000:80 &
    ```
    Теперь вы можете получить доступ к Grafana на [http://localhost:3000](http://localhost:3000).
<img width="1724" alt="Screenshot 2025-03-23 at 21 31 38" src="https://github.com/user-attachments/assets/d5bac2e9-60c6-4554-81f3-a5fddeec2236" />

- Откройте порт для доступа к Prometheus:
    ```bash
    kubectl port-forward -n monitoring svc/kube-prom-stack-kube-prome-prometheus 9090:9090 &
    ```
    Теперь вы можете получить доступ к Prometheus на [http://localhost:9090](http://localhost:9090).
<img width="1727" alt="Screenshot 2025-03-23 at 21 33 54" src="https://github.com/user-attachments/assets/26f55600-2221-4965-8d6d-c1535c66a9a7" />

- Откройте порт для доступа к Flask-приложению:
    ```bash
    kubectl port-forward svc/flask-app-service 5000:80 &
    ```
    Теперь вы можете получить доступ к Flask-приложению на [http://localhost:5000](http://localhost:5000).

### 6. Тестирование с использованием `pytest`
Теперь, когда все сервисы запущены, вы можете протестировать ваш проект, используя `pytest` для выполнения тестов.

Для этого выполните команду:

```bash
pytest
```

`pytest` выполнит все тесты, которые были настроены для вашего проекта, и вы получите отчет о прохождении тестов.

<img width="1442" alt="Screenshot 2025-03-23 at 17 52 17" src="https://github.com/user-attachments/assets/cd2e88a8-bab5-44b5-8cf9-ea0ce33e3134" />

### 7. Документация API (Swagger)
Flask-приложение интегрировано с Swagger для автоматической генерации документации API. Вы можете получить доступ к ней через веб-интерфейс, перейдя по следующему адресу:

http://localhost:5000/apidocs
<img width="1208" alt="Screenshot 2025-03-23 at 21 21 49" src="https://github.com/user-attachments/assets/55513e89-c89e-4862-aabc-0773ae2c7748" />


### 7. Логирование

<img width="1104" alt="Screenshot 2025-03-23 at 21 35 42" src="https://github.com/user-attachments/assets/50f7e4f8-3fa3-484e-b783-c72d1a7811dc" />
