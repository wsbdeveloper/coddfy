"""
View para servir Swagger UI
Integração com OpenAPI/Swagger para documentação interativa
"""
from pyramid.view import view_config
from pyramid.response import Response
import os


@view_config(route_name='swagger_ui', request_method='GET')
def swagger_ui(request):
    """
    GET /api/docs/swagger
    Serve a interface Swagger UI
    """
    html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Coddfy Contracts Manager CCM API - Swagger UI</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
    <style>
        body {
            margin: 0;
            padding: 0;
        }
        .topbar {
            background-color: #2c3e50 !important;
        }
        .swagger-ui .topbar .download-url-wrapper {
            display: none;
        }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {
            const ui = SwaggerUIBundle({
                url: "/api/openapi.yaml",
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                plugins: [
                    SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout",
                docExpansion: "list",
                defaultModelsExpandDepth: 1,
                defaultModelExpandDepth: 1,
                persistAuthorization: true,
                filter: true,
                tryItOutEnabled: true
            });
            window.ui = ui;
        };
    </script>
</body>
</html>
    """
    return Response(html, content_type='text/html')


@view_config(route_name='openapi_spec', request_method='GET')
def openapi_spec(request):
    """
    GET /api/openapi.yaml
    Serve o arquivo de especificação OpenAPI
    """
    # Lê o arquivo openapi.yaml
    spec_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 
        'openapi.yaml'
    )
    
    try:
        with open(spec_path, 'r', encoding='utf-8') as f:
            spec_content = f.read()
        return Response(spec_content, content_type='application/x-yaml')
    except FileNotFoundError:
        return Response(
            'OpenAPI specification not found',
            status=404
        )

