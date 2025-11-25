"""
Setup file para o pacote backend
"""
from setuptools import setup, find_packages

setup(
    name='cursor-contracts-manager',
    version='0.1.0',
    description='Sistema de gestão de contratos de consultoria',
    author='Portal Coddfy Team',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'pyramid>=2.0.2',
        'pyramid-jinja2>=2.10',
        'waitress>=3.0.0',
        'sqlalchemy>=2.0.23',
        'alembic>=1.13.0',
        'psycopg2-binary>=2.9.9',
        'zope-sqlalchemy>=3.1',
        'marshmallow>=3.20.1',
        'pyjwt>=2.8.0',
        'bcrypt>=4.1.1',
        'python-dotenv>=1.0.0',
        'python-dateutil>=2.8.2',
        'pytz>=2023.3',
    ],
    entry_points={
        'paste.app_factory': [
            'main = backend.app:main',
        ],
    },
)

