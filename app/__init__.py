import os
from flask import Flask
from app.data_ingestor import DataIngestor
from app.task_runner import ThreadPool

if not os.path.exists('results'):
    os.mkdir('results')

webserver = Flask(__name__)

webserver.data_ingestor = DataIngestor("./nutrition_activity_obesity_usa_subset.csv")

webserver.tasks_runner = ThreadPool(webserver.data_ingestor.data, webserver.data_ingestor)

webserver.job_counter = 1

from app import routes
