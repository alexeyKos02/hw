HELM_CHART_VERSION="69.8.2"

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts     
helm repo update

helm install kube-prom-stack prometheus-community/kube-prometheus-stack --version "${HELM_CHART_VERSION}" \
  --namespace monitoring \
  --create-namespace \
  -f "k8s-prom-stack-values.yaml"