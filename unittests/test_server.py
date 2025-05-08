import unittest

from app import webserver, DataIngestor, ThreadPool
from app.task_runner import TaskRunner

class TestServer(unittest.TestCase):
    def setUp(self):
        '''Set up the test case by initializing the server and creating a test client.'''
        dummyIngestor = DataIngestor("./test.csv")

        self.server = webserver
        self.server.data_ingestor = dummyIngestor
        self.server.tasks_runner = ThreadPool(self.server.data_ingestor.data, self.server.data_ingestor)
        self.client = self.server.test_client()

        self.task_queue = None
        self.shutdown_event = None
        self.jobs_dict = {}
        self.res_dict = {}

        # Minimal test data
        self.data = [
            {"LocationDesc": "California", "Question": "Percent of adults aged 18 years and older who have an overweight classification", "Data_Value": 10},
            {"LocationDesc": "California", "Question": "Percent of adults aged 18 years and older who have an overweight classification", "Data_Value": 20},
            {"LocationDesc": "Nevada", "Question": "Percent of adults aged 18 years and older who have an overweight classification", "Data_Value": 30},
        ]

        self.runner = TaskRunner(
            self.task_queue,
            self.shutdown_event,
            self.jobs_dict,
            self.res_dict,
            dummyIngestor.data,
            dummyIngestor
        )

    def test_01_server_is_running(self):
        '''Test if the server is running by checking the root endpoint.'''
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_02_states_mean_route(self):
        '''Test the /api/states_mean endpoint.'''
        data = {
            "question": "Percent of adults aged 18 years and older who have an overweight classification"
        }

        response = self.client.post('/api/states_mean', json=data)
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        self.assertIn('job_id', response_data)

    def test_03_state_mean_route(self):
        '''Test the /api/state_mean endpoint.'''
        data = {
            "question": "Percent of adults aged 18 years and older who have an overweight classification",
            "state": "California"
        }

        response = self.client.post('/api/state_mean', json=data)
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        self.assertIn('job_id', response_data)

    def test_04_global_mean_route(self):
        '''Test the /api/global_mean endpoint.'''
        data = {
            "question": "Percent of adults aged 18 years and older who have an overweight classification"
        }

        response = self.client.post('/api/global_mean', json=data)
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        self.assertIn('job_id', response_data)

    def test_05_diff_from_mean_route(self):
        '''Test the /api/diff_from_mean endpoint.'''
        data = {
            "question": "Percent of adults aged 18 years and older who have an overweight classification"
        }

        response = self.client.post('/api/diff_from_mean', json=data)
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        self.assertIn('job_id', response_data)

    def test_06_best5_route(self):
        '''Test the /api/best5 endpoint.'''
        data = {
            "question": "Percent of adults aged 18 years and older who have an overweight classification"
        }

        response = self.client.post('/api/best5', json=data)
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        self.assertIn('job_id', response_data)

    def test_07_worst5_route(self):
        '''Test the /api/worst5 endpoint.'''
        data = {
            "question": "Percent of adults aged 18 years and older who have an overweight classification"
        }

        response = self.client.post('/api/worst5', json=data)
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        self.assertIn('job_id', response_data)

    def test_08_mean_by_category_route(self):
        '''Test the /api/mean_by_category endpoint.'''
        data = {
            "question": "Percent of adults aged 18 years and older who have an overweight classification"
        }

        response = self.client.post('/api/mean_by_category', json=data)
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        self.assertIn('job_id', response_data)

    def test_09_state_mean_by_category_route(self):
        '''Test the /api/state_mean_by_category endpoint.'''
        data = {
            "question": "Percent of adults aged 18 years and older who have an overweight classification",
            "state": "California"
        }

        response = self.client.post('/api/state_mean_by_category', json=data)
        self.assertEqual(response.status_code, 200)
        response_data = response.json
        self.assertIn('job_id', response_data)

    def test_11_check_state_mean(self):
        '''Test the find_state_mean method.'''
        data = {
            "question": "Percent of adults aged 18 years and older who have an overweight classification",
            "state": "California"
        }

        result = self.runner.find_state_mean(data["state"], data["question"])
        self.assertEqual(result, {"California": 15.0})

    def test_12_find_global_mean(self):
        '''Test the find_global_mean method.'''
        data = {
            "question": "Percent of adults aged 18 years and older who have an overweight classification",
        }
        result = self.runner.find_global_mean(data["question"])
        expected = {"global_mean": 20.0}
        self.assertEqual(result, expected)

    def test_13_find_diff_from_mean(self):
        '''Test the find_diff_from_mean method.'''
        data = {
            "question": "Percent of adults aged 18 years and older who have an overweight classification",
        }

        result = self.runner.find_diff_from_mean(data["question"])
        expected = {
            "California": 5.0,
            "Nevada": -10.0
        }
        self.assertEqual(result, expected)

    def test_14_find_state_diff_from_mean(self):
        '''Test the find_state_diff_from_mean method.'''
        data = {
            "question": "Percent of adults aged 18 years and older who have an overweight classification",
            "state": "California"
        }

        result = self.runner.find_state_diff_from_mean(data["state"], data["question"])
        expected = {"California": 5.0}
        self.assertEqual(result, expected)
    
    def test_15_find_best5(self):
        '''Test the find_best5 method.'''
        data = {
            "question": "Percent of adults aged 18 years and older who have an overweight classification",
        }

        result = self.runner.find_best5(data["question"])
        expected = {
            "California": 15.0,
            "Nevada": 30.0
        }
        self.assertEqual(result, expected)

    def test_16_find_worst5(self):
        '''Test the find_worst5 method.'''
        data = {
            "question": "Percent of adults aged 18 years and older who have an overweight classification",
        }

        result = self.runner.find_worst5(data["question"])
        expected = {
            "California": 15.0,
            "Nevada": 30.0
        }
        self.assertEqual(result, expected)

    def test_99_graceful_shutdown(self):
        '''Test the graceful shutdown endpoint.'''
        response = self.client.get('api/graceful_shutdown')

        self.assertEqual(response.status_code, 200)
        response_data = response.json
        self.assertIn('status', response_data)

        data = {
            "question": "Cool easter egg for whoever is reading this :))"
        }

        response = self.client.post('/api/states_mean', json=data)
        self.assertEqual(response.status_code, 503)